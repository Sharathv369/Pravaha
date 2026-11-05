"""
PRAVAHA — Prompt J1: Model Performance Percentage & Relative Accuracy Analysis
Calculates percentage-based metrics across all 5 existing LORSO models on identical 24,088 rows.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

val_parquet = DATA_DIR / "prompt_e_validation_predictions.parquet"
if not val_parquet.exists():
    raise FileNotFoundError(f"Missing {val_parquet}")

df = pd.read_parquet(val_parquet)

models = [
    ("LightGBM Log-Specific Discharge", "log_spec_q"),
    ("LightGBM Specific Discharge", "spec_q"),
    ("LightGBM Raw Peak-Weighted (2.5x)", "raw"),
    ("LightGBM Raw Unweighted", "raw"),
    ("XGBoost Log1p", "log1p")
]

# Baseline RMSE benchmarks
GLOBAL_MEAN_RMSE = 116711.28  # Constant global training mean (43,685.08 cfs) on validation set
RIDGE_LORSO_RMSE = 104979.70  # Out-of-system LORSO Ridge regression baseline

records = []

for m_name, form in models:
    sub = df[df["model_name"] == m_name].copy()
    y_true = sub["actual_cfs"].values
    y_pred = np.clip(sub["predicted_cfs"].values, 0.0, None)
    
    n_total = len(y_true)
    mean_actual = float(np.mean(y_true))
    
    # 1. Standard Regression Metrics
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    
    # 2. Percentage Metrics
    variance_explained_pct = r2 * 100.0
    rel_imp_global_mean_pct = ((GLOBAL_MEAN_RMSE - rmse) / GLOBAL_MEAN_RMSE) * 100.0
    rel_imp_ridge_pct = ((RIDGE_LORSO_RMSE - rmse) / RIDGE_LORSO_RMSE) * 100.0
    nrmse_pct = (rmse / mean_actual) * 100.0
    
    # 3. Prediction Tolerances (Evaluated at y >= 50 cfs to avoid division by zero/low-flow noise)
    # Also calculate at y >= 10 cfs for comparison
    mask_50 = y_true >= 50.0
    n_eligible_50 = int(np.sum(mask_50))
    n_excluded_50 = n_total - n_eligible_50
    re_50 = np.abs(y_pred[mask_50] - y_true[mask_50]) / y_true[mask_50]
    
    pct_within_10_50 = float(100.0 * np.sum(re_50 <= 0.10) / n_eligible_50)
    pct_within_20_50 = float(100.0 * np.sum(re_50 <= 0.20) / n_eligible_50)
    pct_within_30_50 = float(100.0 * np.sum(re_50 <= 0.30) / n_eligible_50)
    
    # Threshold at y >= 10 cfs
    mask_10 = y_true >= 10.0
    n_eligible_10 = int(np.sum(mask_10))
    re_10 = np.abs(y_pred[mask_10] - y_true[mask_10]) / y_true[mask_10]
    pct_within_10_10 = float(100.0 * np.sum(re_10 <= 0.10) / n_eligible_10)
    pct_within_20_10 = float(100.0 * np.sum(re_10 <= 0.20) / n_eligible_10)
    pct_within_30_10 = float(100.0 * np.sum(re_10 <= 0.30) / n_eligible_10)
    
    # 4. Peak Performance Percentages (Top 10% per station)
    peak_trues = []
    peak_preds = []
    for sid, grp in sub.groupby("station_id"):
        yt = grp["actual_cfs"].values
        yp = np.clip(grp["predicted_cfs"].values, 0.0, None)
        q90 = float(np.quantile(yt, 0.90))
        p_mask = yt >= q90
        peak_trues.extend(yt[p_mask])
        peak_preds.extend(yp[p_mask])
        
    peak_trues = np.array(peak_trues)
    peak_preds = np.array(peak_preds)
    n_peak = len(peak_trues)
    peak_rmse = float(np.sqrt(mean_squared_error(peak_trues, peak_preds)))
    
    peak_under_pct = float(100.0 * np.sum(peak_preds < peak_trues) / n_peak)
    peak_over_pct = float(100.0 * np.sum(peak_preds > peak_trues) / n_peak)
    
    peak_re = np.abs(peak_preds - peak_trues) / peak_trues
    peak_within_20_pct = float(100.0 * np.sum(peak_re <= 0.20) / n_peak)
    peak_within_30_pct = float(100.0 * np.sum(peak_re <= 0.30) / n_peak)
    
    records.append({
        "model_name": m_name,
        "target_formulation": form,
        "overall_rmse": round(rmse, 2),
        "peak_rmse_top10": round(peak_rmse, 2),
        "overall_mae": round(mae, 2),
        "pooled_r2": round(r2, 4),
        "variance_explained_pct": round(variance_explained_pct, 2),
        "rmse_imp_vs_global_mean_pct": round(rel_imp_global_mean_pct, 2),
        "rmse_imp_vs_ridge_lorso_pct": round(rel_imp_ridge_pct, 2),
        "nrmse_pct": round(nrmse_pct, 2),
        "pct_within_10_error_thresh50": round(pct_within_10_50, 2),
        "pct_within_20_error_thresh50": round(pct_within_20_50, 2),
        "pct_within_30_error_thresh50": round(pct_within_30_50, 2),
        "pct_within_20_error_thresh10": round(pct_within_20_10, 2),
        "peak_underprediction_pct": round(peak_under_pct, 2),
        "peak_overprediction_pct": round(peak_over_pct, 2),
        "peak_within_20_pct": round(peak_within_20_pct, 2),
        "peak_within_30_pct": round(peak_within_30_pct, 2),
        "n_validation_rows": n_total,
        "n_eligible_thresh50": n_eligible_50,
        "n_excluded_thresh50": n_excluded_50,
        "n_peak_samples": n_peak
    })

df_res = pd.DataFrame(records)
out_csv = REPORTS_DIR / "prompt_j1_percentage_comparison.csv"
df_res.to_csv(out_csv, index=False)
print(f"Saved Prompt J1 percentage comparison to {out_csv}")

