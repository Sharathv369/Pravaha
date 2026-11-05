"""
FLOODCAST Competition Evaluation Metrics for PRAVAHA
Computes:
1. Overall RMSE (40% weight)
2. RMSE on top-10% discharge days per station (30% weight) - flood peak penalty
3. Overall MAE (20% weight)
4. Overall R2 (10% weight)
"""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def compute_competition_metrics(
    df_eval: pd.DataFrame,
    y_true_col: str = "discharge_cfs",
    y_pred_col: str = "pred_discharge_cfs",
    station_col: str = "station_id"
) -> Dict[str, float]:
    """
    Computes all FLOODCAST competition evaluation metrics.
    Only rows where y_true is valid and not NaN are evaluated.
    """
    valid_mask = df_eval[y_true_col].notna() & df_eval[y_pred_col].notna()
    df_valid = df_eval[valid_mask].copy()

    if len(df_valid) == 0:
        return {
            "rmse": np.nan,
            "rmse_top10": np.nan,
            "mae": np.nan,
            "r2": np.nan,
            "composite_loss": np.nan,
            "n_samples": 0
        }

    y_true = df_valid[y_true_col].values
    y_pred = np.clip(df_valid[y_pred_col].values, a_min=0, a_max=None) # Non-negative enforcement

    # 1. Overall RMSE
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))

    # 2. Top-10% discharge days per station RMSE
    top10_true_list = []
    top10_pred_list = []

    for _, group in df_valid.groupby(station_col):
        q90 = group[y_true_col].quantile(0.90)
        peak_mask = group[y_true_col] >= q90
        top10_true_list.extend(group.loc[peak_mask, y_true_col].values)
        top10_pred_list.extend(np.clip(group.loc[peak_mask, y_pred_col].values, a_min=0, a_max=None))

    if len(top10_true_list) > 0:
        rmse_top10 = float(np.sqrt(mean_squared_error(top10_true_list, top10_pred_list)))
    else:
        rmse_top10 = rmse

    # 3. Overall MAE
    mae = float(mean_absolute_error(y_true, y_pred))

    # 4. Overall R2
    r2 = float(r2_score(y_true, y_pred))

    # Composite loss representation (weighted sum of RMSE and peak RMSE)
    # The hackathon scores: RMSE 40%, Peak RMSE 30%, MAE 20%, R2 10%
    # Leaderboard during the event is raw RMSE.
    composite_loss = 0.40 * rmse + 0.30 * rmse_top10 + 0.20 * mae

    return {
        "rmse": rmse,
        "rmse_top10": rmse_top10,
        "mae": mae,
        "r2": r2,
        "composite_loss": composite_loss,
        "n_samples": len(df_valid),
        "n_peak_samples": len(top10_true_list)
    }

