"""Service layer for verified USGS station catalogue and metadata retrieval."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from fastapi import HTTPException

from src.api import config
from src.api.schemas import (
    FlowThresholds,
    StationDetailResponse,
    StationItem,
    StationListResponse,
)


def sanitize_float(val: Any) -> Optional[float]:
    """Ensure floating-point numbers are strictly valid JSON numbers (no NaN or Inf)."""
    if val is None or pd.isna(val) or np.isneginf(val) or np.isposinf(val):
        return None
    return float(val)


class StationService:
    """Singleton service managing in-memory cached USGS station catalogues."""

    def __init__(self):
        self._stations_df: Optional[pd.DataFrame] = None
        self._station_stats: Dict[str, Dict[str, Any]] = {}
        self._initialized: bool = False
        self._load_data()

    def _load_data(self) -> None:
        """Load and merge station catalogues, river groupings, and historical bounds."""
        if not config.VERIFIED_STATION_CATALOG_CSV.exists():
            return

        # 1. Read Verified Station Catalogue
        catalog_df = pd.read_csv(
            config.VERIFIED_STATION_CATALOG_CSV,
            dtype={"station_id": str},
        )
        catalog_df["station_id"] = catalog_df["station_id"].astype(str).str.zfill(8)

        # 2. Read River System Groupings
        if config.RIVER_SYSTEM_GROUPING_CSV.exists():
            group_df = pd.read_csv(
                config.RIVER_SYSTEM_GROUPING_CSV,
                dtype={"station_id": str},
                usecols=["station_id", "river_system", "basin_identifier"],
            )
            group_df["station_id"] = group_df["station_id"].astype(str).str.zfill(8)
            merged = pd.merge(catalog_df, group_df, on="station_id", how="left")
        else:
            merged = catalog_df.copy()
            merged["river_system"] = None
            merged["basin_identifier"] = None

        # 3. Read Historical Training Bounds & Statistical Percentiles
        if config.TRAIN_LABELLED_CSV.exists():
            train_df = pd.read_csv(
                config.TRAIN_LABELLED_CSV,
                dtype={"station_id": str},
                usecols=["station_id", "date", "discharge_cfs"],
            )
            train_df["station_id"] = train_df["station_id"].astype(str).str.zfill(8)

            for station_id, group in train_df.groupby("station_id"):
                discharges = group["discharge_cfs"].dropna()
                self._station_stats[station_id] = {
                    "start_date": group["date"].min(),
                    "end_date": group["date"].max(),
                    "total_obs": len(discharges),
                    "min": sanitize_float(discharges.min()) if len(discharges) else None,
                    "q25": sanitize_float(discharges.quantile(0.25)) if len(discharges) else None,
                    "q50": sanitize_float(discharges.quantile(0.50)) if len(discharges) else None,
                    "q75": sanitize_float(discharges.quantile(0.75)) if len(discharges) else None,
                    "q90": sanitize_float(discharges.quantile(0.90)) if len(discharges) else None,
                    "max": sanitize_float(discharges.max()) if len(discharges) else None,
                }

        # 4. Check LORSO 2022-2023 Validation presence
        val_stations = set()
        if config.LORSO_PREDICTIONS_PARQUET.exists():
            try:
                import pyarrow.parquet as pq
                val_table = pq.read_table(
                    config.LORSO_PREDICTIONS_PARQUET,
                    columns=["station_id"]
                )
                val_stations = set(val_table["station_id"].to_pylist())
            except Exception:
                pass

        merged["has_2022_2023_validation"] = merged["station_id"].isin(val_stations)
        self._stations_df = merged
        self._initialized = True

    def is_ready(self) -> bool:
        """Return True if station catalogue is loaded."""
        return self._initialized and self._stations_df is not None and not self._stations_df.empty

    def get_station_count(self) -> int:
        """Return number of stations in verified catalogue."""
        if self._stations_df is not None:
            return len(self._stations_df)
        return 0

    def get_stations(
        self,
        search: Optional[str] = None,
        river_system: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> StationListResponse:
        """Filter and return the verified station catalogue."""
        if not self.is_ready():
            raise HTTPException(status_code=503, detail="Station catalogue is currently unavailable.")

        df = self._stations_df.copy()

        # Apply search filter (by station ID or station name)
        if search:
            search_clean = search.strip().lower()
            df = df[
                df["station_id"].str.lower().str.contains(search_clean)
                | df["station_name"].str.lower().str.contains(search_clean)
                | df["river_name"].str.lower().str.contains(search_clean)
            ]

        # Apply river system filter
        if river_system:
            rs_clean = river_system.strip().lower()
            df = df[df["river_system"].str.lower() == rs_clean]

        total_count = len(self._stations_df)
        filtered_count = len(df)

        # Pagination
        if offset is not None:
            df = df.iloc[offset:]
        if limit is not None:
            df = df.iloc[:limit]

        station_items: List[StationItem] = []
        for _, row in df.iterrows():
            st_id = str(row["station_id"]).zfill(8)
            stats = self._station_stats.get(st_id, {})
            state_cd_val = int(row["state_cd"]) if pd.notna(row.get("state_cd")) else None
            state_abbr = config.FIPS_TO_STATE.get(state_cd_val) if state_cd_val else None

            item = StationItem(
                station_id=st_id,
                station_name=str(row["station_name"]),
                river_name=str(row["river_name"]),
                state_cd=state_cd_val,
                state=state_abbr,
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                drainage_area_sqmi=sanitize_float(row.get("drainage_area_sqmi")),
                drainage_area_verification_status="VERIFIED" if pd.notna(row.get("drainage_area_sqmi")) else "UNVERIFIED",
                river_system=str(row["river_system"]) if pd.notna(row.get("river_system")) else None,
                observation_start=stats.get("start_date"),
                observation_end=stats.get("end_date"),
                total_observations=stats.get("total_obs", 0),
                data_quality_status=str(row["verification_status"]),
                is_core_station=bool(row.get("is_core_station", True)),
                has_2022_2023_validation=bool(row.get("has_2022_2023_validation", False)),
            )
            station_items.append(item)

        return StationListResponse(
            total_count=total_count,
            filtered_count=filtered_count,
            stations=station_items,
        )

    def get_station_detail(self, station_id: str) -> StationDetailResponse:
        """Fetch verified metadata, coordinates, and historical flow percentiles for a station."""
        if not self.is_ready():
            raise HTTPException(status_code=503, detail="Station catalogue is currently unavailable.")

        clean_id = station_id.strip()
        # Ensure 8 digits if standard numeric USGS ID
        if len(clean_id) == 7 and clean_id.isdigit():
            clean_id = f"0{clean_id}"

        match = self._stations_df[self._stations_df["station_id"] == clean_id]
        if match.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Station '{station_id}' was not found in the verified USGS catalogue."
            )

        row = match.iloc[0]
        stats = self._station_stats.get(clean_id, {})
        state_cd_val = int(row["state_cd"]) if pd.notna(row.get("state_cd")) else None
        state_abbr = config.FIPS_TO_STATE.get(state_cd_val) if state_cd_val else None

        thresholds = FlowThresholds(
            min_recorded_cfs=stats.get("min"),
            q25_cfs=stats.get("q25"),
            q50_median_cfs=stats.get("q50"),
            q75_cfs=stats.get("q75"),
            q90_threshold_cfs=stats.get("q90"),
            max_recorded_cfs=stats.get("max"),
        )

        return StationDetailResponse(
            station_id=clean_id,
            station_name=str(row["station_name"]),
            river_name=str(row["river_name"]),
            river_system=str(row["river_system"]) if pd.notna(row.get("river_system")) else None,
            basin_identifier=str(row["basin_identifier"]) if pd.notna(row.get("basin_identifier")) else None,
            state_cd=state_cd_val,
            state=state_abbr,
            coordinates={
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            },
            drainage_area_sqmi=sanitize_float(row.get("drainage_area_sqmi")),
            drainage_area_verification_status="VERIFIED" if pd.notna(row.get("drainage_area_sqmi")) else "UNVERIFIED",
            observation_start=stats.get("start_date"),
            observation_end=stats.get("end_date"),
            total_observations=stats.get("total_obs", 0),
            flow_thresholds_cfs=thresholds,
            data_quality_status=str(row["verification_status"]),
            verification_reason=str(row.get("verification_reason", "")),
            has_validation_predictions=bool(row.get("has_2022_2023_validation", False)),
        )


# Global singleton instance
station_service = StationService()

