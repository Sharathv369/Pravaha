"""Service layer for Leave-One-River-System-Out (LORSO) validation leaderboard and river-system analytics."""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from fastapi import HTTPException

from src.api import config
from src.api.schemas import (
    LeaderboardItem,
    LeaderboardResponse,
    RiverSystemItem,
    RiverSystemsResponse,
)


def sanitize_float(val: Any) -> Optional[float]:
    """Ensure floating-point numbers are strictly valid JSON numbers (no NaN or Inf)."""
    if val is None or pd.isna(val) or np.isneginf(val) or np.isposinf(val):
        return None
    return float(val)


class ValidationService:
    """Singleton service managing LORSO benchmark results and river system analytics."""

    def __init__(self):
        self._results_df: Optional[pd.DataFrame] = None
        self._river_metrics_df: Optional[pd.DataFrame] = None
        self._river_grouping_df: Optional[pd.DataFrame] = None
        self._initialized: bool = False
        self._load_data()

    def _load_data(self) -> None:
        """Load validation metrics from reports."""
        if config.LORSO_VALIDATION_RESULTS_CSV.exists():
            self._results_df = pd.read_csv(config.LORSO_VALIDATION_RESULTS_CSV)

        if config.LORSO_PER_RIVER_SYSTEM_METRICS_CSV.exists():
            self._river_metrics_df = pd.read_csv(config.LORSO_PER_RIVER_SYSTEM_METRICS_CSV)

        if config.RIVER_SYSTEM_GROUPING_CSV.exists():
            group = pd.read_csv(config.RIVER_SYSTEM_GROUPING_CSV, dtype={"station_id": str})
            group["station_id"] = group["station_id"].astype(str).str.zfill(8)
            self._river_grouping_df = group

        self._initialized = True

    def is_ready(self) -> bool:
        """Check if validation result datasets are available."""
        return self._initialized and self._results_df is not None and not self._results_df.empty

    def get_leaderboard(self) -> LeaderboardResponse:
        """Return the official LORSO validation model leaderboard ranked by Pooled R²."""
        if not self.is_ready():
            raise HTTPException(status_code=503, detail="Validation leaderboard results are currently unavailable.")

        # Sort by pooled_r2 descending
        sorted_df = self._results_df.sort_values("pooled_r2", ascending=False).reset_index(drop=True)

        items: List[LeaderboardItem] = []
        for idx, row in sorted_df.iterrows():
            item = LeaderboardItem(
                model_name=str(row["model_name"]),
                target_formulation=str(row["target_formulation"]),
                overall_rmse_cfs=float(row["pooled_rmse"]),
                peak_rmse_cfs=float(row["pooled_rmse_top10"]),
                overall_mae_cfs=float(row["pooled_mae"]),
                pooled_r2=float(row["pooled_r2"]),
                validation_sample_count=int(row["validation_rows"]),
                peak_sample_count=2423,  # Top-10% empirical peak validation count
                rank_by_pooled_r2=idx + 1,
            )
            items.append(item)

        total_rows = int(sorted_df["validation_rows"].iloc[0]) if len(sorted_df) else 24088

        return LeaderboardResponse(
            total_models=len(items),
            total_validation_rows=total_rows,
            models=items,
        )

    def get_river_systems(self, model_name: Optional[str] = None) -> RiverSystemsResponse:
        """Return held-out river-system validation metrics across all 23 river basin clusters."""
        if not self.is_ready() or self._river_metrics_df is None:
            raise HTTPException(status_code=503, detail="River-system validation metrics are currently unavailable.")

        # Map requested model name or alias
        formulation = "log_spec_q"
        canonical_model = config.DEFAULT_MODEL_NAME
        if model_name:
            cleaned = model_name.strip().lower()
            if cleaned in config.MODEL_ALIASES:
                canonical_model = config.MODEL_ALIASES[cleaned]
            else:
                for alias, target in config.MODEL_ALIASES.items():
                    if target.lower() == cleaned:
                        canonical_model = target
                        break

            formulation_map = {
                "LightGBM Log-Specific Discharge": "log_spec_q",
                "LightGBM Specific Discharge": "spec_q",
                "LightGBM Raw Unweighted": "raw",
                "LightGBM Raw Peak-Weighted (2.5x)": "raw",
                "XGBoost Log1p": "log1p",
            }
            formulation = formulation_map.get(canonical_model, "log_spec_q")

        # Filter river metrics for this model formulation
        filtered_metrics = self._river_metrics_df[self._river_metrics_df["target_formulation"] == formulation]
        metrics_by_system = {
            str(r["river_system"]): r for _, r in filtered_metrics.iterrows()
        }

        # Build map of river systems to all assigned station IDs from grouping
        system_to_stations: Dict[str, List[str]] = {}
        if self._river_grouping_df is not None:
            for _, r in self._river_grouping_df.iterrows():
                rs = str(r["river_system"])
                st_id = str(r["station_id"])
                system_to_stations.setdefault(rs, []).append(st_id)

        items: List[RiverSystemItem] = []
        all_systems = sorted(system_to_stations.keys()) if system_to_stations else sorted(metrics_by_system.keys())

        for rs in all_systems:
            st_ids = system_to_stations.get(rs, [])
            metric_row = metrics_by_system.get(rs)

            if metric_row is not None:
                n_samples = int(metric_row["n_samples"])
                n_peak = int(metric_row["n_peak_samples"])
                rmse_val = sanitize_float(metric_row["rmse"])
                peak_rmse_val = sanitize_float(metric_row["rmse_top10"])
                mae_val = sanitize_float(metric_row["mae"])
                r2_val = sanitize_float(metric_row["r2"])
                val_status = "EVALUATED_HOLDOUT" if n_samples > 0 else "ZERO_VALIDATION_SAMPLES"
            else:
                n_samples = 0
                n_peak = 0
                rmse_val = None
                peak_rmse_val = None
                mae_val = None
                r2_val = None
                val_status = "ZERO_VALIDATION_SAMPLES"

            items.append(
                RiverSystemItem(
                    river_system=rs,
                    held_out_station_ids=st_ids,
                    station_count=len(st_ids),
                    validation_sample_count=n_samples,
                    peak_sample_count=n_peak,
                    model_name=canonical_model,
                    rmse_cfs=rmse_val,
                    peak_rmse_cfs=peak_rmse_val,
                    mae_cfs=mae_val,
                    r2=r2_val,
                    validation_status=val_status,
                )
            )

        return RiverSystemsResponse(
            total_river_systems=len(items),
            model_name=canonical_model,
            river_systems=items,
        )


# Global singleton instance
validation_service = ValidationService()

