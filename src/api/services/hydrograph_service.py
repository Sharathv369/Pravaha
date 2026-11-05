"""Service layer for historical hydrograph time-series and LORSO validation predictions."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from fastapi import HTTPException

from src.api import config
from src.api.schemas import HydrographPoint, HydrographResponse


def sanitize_float(val: Any) -> Optional[float]:
    """Ensure floating-point numbers are strictly valid JSON numbers (no NaN or Inf)."""
    if val is None or pd.isna(val) or np.isneginf(val) or np.isposinf(val):
        return None
    return float(val)


def validate_iso_date(date_str: str, param_name: str) -> None:
    """Validate that date_str is a valid ISO 8601 YYYY-MM-DD date."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format for '{param_name}': '{date_str}'. Expected format is YYYY-MM-DD."
        )


class HydrographService:
    """Singleton service managing hydrograph queries with in-memory station indexing."""

    def __init__(self):
        self._train_df: Optional[pd.DataFrame] = None
        self._val_df: Optional[pd.DataFrame] = None
        self._station_catalog_df: Optional[pd.DataFrame] = None
        self._initialized: bool = False
        self._load_data()

    def _load_data(self) -> None:
        """Load labelled discharge observations and validation predictions into memory."""
        # 1. Load Station Names for response metadata
        if config.VERIFIED_STATION_CATALOG_CSV.exists():
            cat = pd.read_csv(
                config.VERIFIED_STATION_CATALOG_CSV,
                dtype={"station_id": str},
                usecols=["station_id", "station_name"],
            )
            cat["station_id"] = cat["station_id"].astype(str).str.zfill(8)
            self._station_catalog_df = cat.set_index("station_id")

        # 2. Load Labelled Daily Mean Discharge Observations
        if config.TRAIN_LABELLED_CSV.exists():
            df_t = pd.read_csv(
                config.TRAIN_LABELLED_CSV,
                dtype={"station_id": str},
                usecols=["station_id", "date", "discharge_cfs"],
            )
            df_t["station_id"] = df_t["station_id"].astype(str).str.zfill(8)
            self._train_df = df_t

        # 3. Load Out-of-System LORSO Validation Predictions (2022-2023)
        if config.LORSO_PREDICTIONS_PARQUET.exists():
            df_v = pd.read_parquet(config.LORSO_PREDICTIONS_PARQUET)
            df_v["station_id"] = df_v["station_id"].astype(str).str.zfill(8)
            df_v["date_str"] = df_v["date"].dt.strftime("%Y-%m-%d")
            self._val_df = df_v

        self._initialized = True

    def is_ready(self) -> bool:
        """Check if essential hydrograph datasets are loaded."""
        return self._initialized and self._train_df is not None and not self._train_df.empty

    def resolve_model_name(self, requested_model: Optional[str]) -> Tuple[str, str]:
        """Resolve model name and target formulation code from alias or full name."""
        if not requested_model:
            return config.DEFAULT_MODEL_NAME, config.DEFAULT_TARGET_FORMULATION

        cleaned = requested_model.strip().lower()
        if cleaned in config.MODEL_ALIASES:
            canonical_name = config.MODEL_ALIASES[cleaned]
        else:
            # Check if canonical name matches directly
            canonical_name = None
            for alias, target in config.MODEL_ALIASES.items():
                if target.lower() == cleaned:
                    canonical_name = target
                    break

        if not canonical_name:
            supported = list(set(config.MODEL_ALIASES.values()))
            raise HTTPException(
                status_code=400,
                detail=f"Unknown model identifier '{requested_model}'. Supported models are: {supported}"
            )

        # Map canonical name to target formulation
        formulation_map = {
            "LightGBM Log-Specific Discharge": "log_spec_q",
            "LightGBM Specific Discharge": "spec_q",
            "LightGBM Raw Unweighted": "raw",
            "LightGBM Raw Peak-Weighted (2.5x)": "raw",
            "XGBoost Log1p": "log1p",
        }
        return canonical_name, formulation_map.get(canonical_name, "log_spec_q")

    def get_hydrograph(
        self,
        station_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> HydrographResponse:
        """Return historical discharge time-series merged with held-out LORSO predictions."""
        if not self.is_ready():
            raise HTTPException(status_code=503, detail="Historical discharge dataset is currently unavailable.")

        clean_id = station_id.strip()
        if len(clean_id) == 7 and clean_id.isdigit():
            clean_id = f"0{clean_id}"

        # 1. Verify Station Exists
        st_rows = self._train_df[self._train_df["station_id"] == clean_id]
        if st_rows.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Station '{station_id}' was not found in the historical discharge records."
            )

        # 2. Date Validation
        if start_date:
            validate_iso_date(start_date, "start_date")
        if end_date:
            validate_iso_date(end_date, "end_date")
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail=f"start_date ('{start_date}') must be earlier than or equal to end_date ('{end_date}')."
            )

        # 3. Resolve Model
        canonical_model, target_formulation = self.resolve_model_name(model_name)

        # 4. Filter Historical Observations
        obs = st_rows.copy()
        if start_date:
            obs = obs[obs["date"] >= start_date]
        if end_date:
            obs = obs[obs["date"] <= end_date]

        obs = obs.sort_values("date")

        # 5. Filter and Join Validation Predictions
        predictions_map: Dict[str, float] = {}
        if self._val_df is not None:
            val_match = self._val_df[
                (self._val_df["station_id"] == clean_id)
                & (self._val_df["model_name"] == canonical_model)
            ]
            if start_date:
                val_match = val_match[val_match["date_str"] >= start_date]
            if end_date:
                val_match = val_match[val_match["date_str"] <= end_date]

            for _, r in val_match.iterrows():
                predictions_map[str(r["date_str"])] = sanitize_float(r["predicted_cfs"])

        # 6. Build Chronological Hydrograph Points
        points: List[HydrographPoint] = []
        for _, r in obs.iterrows():
            d_str = str(r["date"])
            act_cfs = sanitize_float(r["discharge_cfs"])
            pred_cfs = predictions_map.get(d_str)

            has_pred = pred_cfs is not None
            points.append(
                HydrographPoint(
                    date=d_str,
                    station_id=clean_id,
                    actual_discharge_cfs=act_cfs,
                    predicted_discharge_cfs=pred_cfs,
                    prediction_model=canonical_model if has_pred else None,
                    validation_type="LORSO_HOLDOUT" if has_pred else None,
                    data_source="USGS_NWIS_DAILY_MEAN_00060_00003",
                    data_status="OBSERVED_AND_VALIDATED" if has_pred else "OBSERVED_HISTORICAL",
                )
            )

        station_name = clean_id
        if self._station_catalog_df is not None and clean_id in self._station_catalog_df.index:
            station_name = str(self._station_catalog_df.loc[clean_id, "station_name"])

        res_start = points[0].date if points else (start_date or "")
        res_end = points[-1].date if points else (end_date or "")

        return HydrographResponse(
            station_id=clean_id,
            station_name=station_name,
            model_name=canonical_model,
            target_formulation=target_formulation,
            total_points=len(points),
            start_date=res_start,
            end_date=res_end,
            data=points,
        )


# Global singleton instance
hydrograph_service = HydrographService()
