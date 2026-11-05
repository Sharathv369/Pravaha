"""Service layer for verified catchment attributes and model limitation profiles."""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from fastapi import HTTPException

from src.api import config
from src.api.schemas import CatchmentAttribute, CatchmentProfileResponse


def sanitize_float(val: Any) -> Optional[float]:
    """Ensure floating-point numbers are strictly valid JSON numbers (no NaN or Inf)."""
    if val is None or pd.isna(val) or np.isneginf(val) or np.isposinf(val):
        return None
    return float(val)


class CatchmentService:
    """Singleton service managing verified physiographic catchment attributes."""

    def __init__(self):
        self._provenance_df: Optional[pd.DataFrame] = None
        self._catalog_df: Optional[pd.DataFrame] = None
        self._station_metrics_df: Optional[pd.DataFrame] = None
        self._initialized: bool = False
        self._load_data()

    def _load_data(self) -> None:
        """Load catchment provenance and per-station validation metrics."""
        if config.CATCHMENT_PROVENANCE_CSV.exists():
            df_cp = pd.read_csv(config.CATCHMENT_PROVENANCE_CSV, dtype={"station_id": str})
            df_cp["station_id"] = df_cp["station_id"].astype(str).str.zfill(8)
            self._provenance_df = df_cp

        if config.VERIFIED_STATION_CATALOG_CSV.exists():
            cat = pd.read_csv(config.VERIFIED_STATION_CATALOG_CSV, dtype={"station_id": str})
            cat["station_id"] = cat["station_id"].astype(str).str.zfill(8)
            self._catalog_df = cat.set_index("station_id")

        if config.LORSO_PER_STATION_METRICS_CSV.exists():
            sm = pd.read_csv(config.LORSO_PER_STATION_METRICS_CSV, dtype={"station_id": str})
            sm["station_id"] = sm["station_id"].astype(str).str.zfill(8)
            # Filter for best-performing log_spec_q model
            self._station_metrics_df = sm[sm["target_formulation"] == "log_spec_q"].set_index("station_id")

        self._initialized = True

    def is_ready(self) -> bool:
        """Check if catchment provenance dataset is available."""
        return self._initialized and self._provenance_df is not None and not self._provenance_df.empty

    def _determine_limitation_indicator(
        self,
        station_id: str,
        unverified_count: int,
        verification_status: str,
    ) -> str:
        """Derive an evidence-based model limitation explanation from actual validation records."""
        # 1. Zero validation samples due to truncated historical record
        if station_id == "11447650":
            return (
                "Historical USGS discharge observations ended on 2015-09-30; station possesses zero validation "
                "samples in the 2022–2023 LORSO holdout period. Predictions cannot be verified against modern events."
            )

        # 2. Known heavily regulated river basins
        regulated_basins = {
            "08158000": "Colorado River at Austin, TX is controlled by upstream reservoir releases (Lake Travis / Mansfield Dam). Without upstream dam release telemetry, meteorological ML models cannot predict regulated discharge.",
            "09380000": "Colorado River at Lees Ferry, AZ is directly downstream of Glen Canyon Dam. Flow hydrographs are governed by hydropower releases rather than local rainfall.",
            "06805500": "Platte River at Louisville, NE experiences substantial agricultural diversions and upstream reservoir regulation causing severe negative holdout R².",
            "06610000": "Missouri River near Omaha, NE is heavily channelized and regulated by upper Missouri River dams.",
        }
        if station_id in regulated_basins:
            return regulated_basins[station_id]

        # 3. Validation metrics performance
        if self._station_metrics_df is not None and station_id in self._station_metrics_df.index:
            row = self._station_metrics_df.loc[station_id]
            r2 = float(row["r2"]) if pd.notna(row["r2"]) else None
            rmse = float(row["rmse"]) if pd.notna(row["rmse"]) else None

            if r2 is not None and r2 < -1.0:
                return (
                    f"Out-of-system spatial generalization is poor (holdout R² = {r2:.2f}, RMSE = {rmse:,.0f} cfs). "
                    "Flow dynamics reflect complex upstream hydro-morphology not captured by zero-lag weather reanalysis."
                )
            elif r2 is not None and r2 < 0.1:
                return (
                    f"Modest spatial transferability (holdout R² = {r2:.2f}, RMSE = {rmse:,.0f} cfs). "
                    "Flashiness and ephemeral baseflow fluctuations cause non-linear peak prediction errors."
                )
            elif r2 is not None and r2 >= 0.1:
                return (
                    f"Demonstrated spatial holdout skill (holdout R² = {r2:.2f}, RMSE = {rmse:,.0f} cfs). "
                    "Consistent natural runoff catchment responding predictably to antecedent precipitation."
                )

        # 4. Fallback based on unverified attributes
        if unverified_count >= 3:
            return (
                "Catchment static attributes (elevation, slope, forest cover) are unverified; model relies exclusively "
                "on precipitation and drainage area, increasing uncertainty during extreme convective weather."
            )

        return "Standard spatial holdout validation: predictions carry higher uncertainty during unobserved non-linear peak crest events."

    def get_catchment_profile(self, station_id: str) -> CatchmentProfileResponse:
        """Return verified physiographic attributes and honest model limitation indicators."""
        if not self.is_ready():
            raise HTTPException(status_code=503, detail="Catchment provenance dataset is currently unavailable.")

        clean_id = station_id.strip()
        if len(clean_id) == 7 and clean_id.isdigit():
            clean_id = f"0{clean_id}"

        st_rows = self._provenance_df[self._provenance_df["station_id"] == clean_id]
        if st_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Station '{station_id}' was not found in the verified catchment provenance catalogue."
            )

        # Map attributes
        attr_map: Dict[str, pd.Series] = {}
        for _, row in st_rows.iterrows():
            attr_map[str(row["attribute"])] = row

        def build_attr(name: str, default_unit: str) -> CatchmentAttribute:
            if name in attr_map:
                r = attr_map[name]
                is_ver = str(r["verification_status"]) == "VERIFIED"
                val = sanitize_float(r["final_value"]) if is_ver else None
                unit = str(r["final_unit"]) if pd.notna(r["final_unit"]) else default_unit
                source = str(r["source_dataset"]) if pd.notna(r["source_dataset"]) else None
                reason = str(r["failure_reason"]) if pd.notna(r["failure_reason"]) else None
                return CatchmentAttribute(
                    value=val,
                    unit=unit,
                    source_dataset=source,
                    verification_status="VERIFIED" if is_ver else "MISSING_OR_UNVERIFIED",
                    explanation=reason,
                )
            return CatchmentAttribute(
                value=None,
                unit=default_unit,
                source_dataset=None,
                verification_status="MISSING_OR_UNVERIFIED",
                explanation=f"{name} attribute was not present in station provenance records.",
            )

        drainage_attr = build_attr("drainage_area_sqmi", "sq mi")
        elevation_attr = build_attr("mean_elevation_ft", "ft")
        slope_attr = build_attr("slope_pct", "%")
        forest_attr = build_attr("forest_cover_pct", "%")

        unverified_count = sum(
            1 for a in [drainage_attr, elevation_attr, slope_attr, forest_attr]
            if a.verification_status != "VERIFIED"
        )

        station_name = clean_id
        river_name = "Unknown River"
        cat_status = "VERIFIED_BENCHMARK_READY" if unverified_count == 0 else "VERIFIED_REQUIRES_STREAMSTATS"

        if self._catalog_df is not None and clean_id in self._catalog_df.index:
            station_name = str(self._catalog_df.loc[clean_id, "station_name"])
            river_name = str(self._catalog_df.loc[clean_id, "river_name"])
            cat_status = str(self._catalog_df.loc[clean_id, "verification_status"])

        limitation_text = self._determine_limitation_indicator(
            clean_id,
            unverified_count,
            cat_status,
        )

        return CatchmentProfileResponse(
            station_id=clean_id,
            station_name=station_name,
            river_name=river_name,
            drainage_area_sqmi=drainage_attr,
            mean_elevation_ft=elevation_attr,
            slope_pct=slope_attr,
            forest_cover_pct=forest_attr,
            overall_catchment_verification=cat_status,
            model_limitation_indicator=limitation_text,
        )


# Global singleton instance
catchment_service = CatchmentService()

