"""
PRAVAHA — Prompt J: Independent ML Accuracy Testing & Final Model Evaluation
Independent calculation and verification engine for all 5 existing LORSO ML models.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

# 1. Load Parquet
val_parquet = DATA_DIR / "prompt_e_validation_predictions.parquet"
if not val_parquet.exists():
    raise FileNotFoundError(f"Missing {val_parquet}")

df = pd.read_parquet(val_parquet)

# 2. Phase 2: Integrity Verification
print("=== PHASE 2: VALIDATION DATA INTEGRITY VERIFICATION ===")
print(f"Total rows in parquet: {len(df):,}")
print(f"Schema columns: {df.columns.tolist()}")

unique_models = df["model_name"].unique().tolist()
print(f"Unique models ({len(unique_models)}): {unique_models}")

model_row_counts = df.groupby("model_name").size().to_dict()
print(f"Row counts per model: {model_row_counts}")

# Check unique station-date pairs
st_dates_per_model = df.groupby("model_name").apply(lambda g: len(g[["station_id", "date"]].drop_duplicates())).to_dict()
print(f"Unique station-date pairs per model: {st_dates_per_model}")

# Duplicates
dup_count = df.duplicated(subset=["model_name", "station_id", "date"]).sum()
print(f"Duplicate records: {dup_count}")

# Missing / NaN / Inf
nan_count = df[["actual_cfs", "predicted_cfs"]].isna().sum().to_dict()
inf_count = np.isinf(df["predicted_cfs"]).sum()
print(f"NaN counts: {nan_count}, Inf counts: {inf_count}")

# Negative predictions
neg_preds = (df["predicted_cfs"] < 0).sum()
print(f"Negative predictions count: {neg_preds}")

# Verification against PRAVAHA_TRAIN_LABELLED.csv
train_labelled = pd.read_csv(DATA_DIR / "PRAVAHA_TRAIN_LABELLED.csv", dtype={"station_id": str})
train_labelled["date"] = pd.to_datetime(train_labelled["date"])
val_truth = train_labelled[(train_labelled["date"] >= "2022-01-01") & (train_labelled["date"] <= "2023-12-31")].copy()

# Merge check with one model
sub_check = df[df["model_name"] == "LightGBM Log-Specific Discharge"].copy()
sub_check["date"] = pd.to_datetime(sub_check["date"])
sub_check["station_id"] = sub_check["station_id"].astype(str)

merged_truth = pd.merge(
    sub_check, val_truth[["station_id", "date", "discharge_cfs"]],
    on=["station_id", "date"], how="inner"
)
max_truth_diff = np.max(np.abs(merged_truth["actual_cfs"] - merged_truth["discharge_cfs"]))
print(f"Ground truth match against PRAVAHA_TRAIN_LABELLED: {len(merged_truth):,}/{len(sub_check):,} rows, Max Diff = {max_truth_diff:.6f} cfs")

# 3. Phase 3 & 4: Independent Accuracy Calculations
models_to_test = [
    ("LightGBM Log-Specific Discharge", "log_spec_q"),
    ("LightGBM Specific Discharge", "spec_q"),
    ("LightGBM Raw Peak-Weighted (2.5x)", "raw"),
    ("LightGBM Raw Unweighted", "raw"),
    ("XGBoost Log1p", "log1p")
]

GLOBAL_MEAN_RMSE = 116711.28
RIDGE_LORSO_RMSE = 104979.70

summary_records = []
all_station_records = []

# Pre-determine station peaks on actuals
station_q90 = {}
for sid, grp in sub_check.groupby("station_id"):
    station_q90[sid] = float(np.quantile(grp["actual_cfs"].values, 0.90))

for m_name, target_form in models_to_test:
    sub = df[df["model_name"] == m_name].copy()
    y_true = sub["actual_cfs"].values
    y_pred = np.clip(sub["predicted_cfs"].values, 0.0, None)
    
    # Global metrics
    overall_rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    overall_mae = float(mean_absolute_error(y_true, y_pred))
    pooled_r2 = float(r2_score(y_true, y_pred))
    mean_bias = float(np.mean(y_pred - y_true))
    
    # Baseline improvements
    imp_global_mean = ((GLOBAL_MEAN_RMSE - overall_rmse) / GLOBAL_MEAN_RMSE) * 100.0
    imp_ridge_lorso = ((RIDGE_LORSO_RMSE - overall_rmse) / RIDGE_LORSO_RMSE) * 100.0
    
    # Station-wise metrics
    st_rmses = []
    st_maes = []
    st_r2s = []
    st_peak_rmses = []
    st_peak_maes = []
    
    peak_trues_all = []
    peak_preds_all = []
    peak_under_count = 0
    total_peak_count = 0
    
    for sid, grp in sub.groupby("station_id"):
        yt = grp["actual_cfs"].values
        yp = np.clip(grp["predicted_cfs"].values, 0.0, None)
        
        st_rmse = float(np.sqrt(mean_squared_error(yt, yp)))
        st_mae = float(mean_absolute_error(yt, yp))
        st_r2 = float(r2_score(yt, yp)) if np.var(yt) > 1e-6 else 0.0
        
        st_rmses.append(st_rmse)
        st_maes.append(st_mae)
        st_r2s.append(st_r2)
        
        q90 = station_q90[sid]
        p_mask = yt >= q90
        yt_p = yt[p_mask]
        yp_p = yp[p_mask]
        
        st_p_rmse = float(np.sqrt(mean_squared_error(yt_p, yp_p)))
        st_p_mae = float(mean_absolute_error(yt_p, yp_p))
        st_peak_rmses.append(st_p_rmse)
        st_peak_maes.append(st_p_mae)
        
        peak_trues_all.extend(yt_p)
        peak_preds_all.extend(yp_p)
        peak_under_count += np.sum(yp_p < yt_p)
        total_peak_count += len(yt_p)
        
        # Save station record
        all_station_records.append({
            "model_name": m_name,
            "target_formulation": target_form,
            "station_id": sid,
            "river_system": grp["river_system"].iloc[0],
            "n_obs": len(yt),
            "mean_actual_cfs": round(float(np.mean(yt)), 1),
            "max_actual_cfs": round(float(np.max(yt)), 1),
            "q90_threshold_cfs": round(q90, 1),
            "rmse_cfs": round(st_rmse, 2),
            "mae_cfs": round(st_mae, 2),
            "r2": round(st_r2, 4),
            "peak_rmse_cfs": round(st_p_rmse, 2),
            "peak_mae_cfs": round(st_p_mae, 2),
            "peak_underprediction_pct": round(100.0 * np.sum(yp_p < yt_p) / len(yt_p), 1) if len(yt_p) > 0 else 0.0,
            "squared_error_sum": float(np.sum((yt - yp)**2))
        })
        
    peak_trues_all = np.array(peak_trues_all)
    peak_preds_all = np.array(peak_preds_all)
    peak_rmse_top10 = float(np.sqrt(mean_squared_error(peak_trues_all, peak_preds_all)))
    peak_mae_top10 = float(mean_absolute_error(peak_trues_all, peak_preds_all))
    peak_under_pct = float(100.0 * peak_under_count / total_peak_count)
    peak_over_pct = float(100.0 * (total_peak_count - peak_under_count) / total_peak_count)
    peak_mean_bias = float(np.mean(peak_preds_all - peak_trues_all))
    
    macro_rmse = float(np.mean(st_rmses))
    median_st_rmse = float(np.median(st_rmses))
    
    summary_records.append({
        "model_name": m_name,
        "target_formulation": target_form,
        "overall_rmse": round(overall_rmse, 2),
        "peak_rmse_top10": round(peak_rmse_top10, 2),
        "overall_mae": round(overall_mae, 2),
        "pooled_r2": round(pooled_r2, 4),
        "macro_rmse": round(macro_rmse, 2),
        "median_station_rmse": round(median_st_rmse, 2),
        "mean_prediction_bias": round(mean_bias, 2),
        "peak_underprediction_pct": round(peak_under_pct, 1),
        "peak_overprediction_pct": round(peak_over_pct, 1),
        "peak_mae": round(peak_mae_top10, 2),
        "peak_mean_bias": round(peak_mean_bias, 2),
        "imp_vs_global_mean_pct": round(imp_global_mean, 2),
        "imp_vs_ridge_lorso_pct": round(imp_ridge_lorso, 2),
        "validation_rows": len(y_true),
        "peak_samples_count": total_peak_count
    })

df_summary = pd.DataFrame(summary_records)
df_summary.to_csv(REPORTS_DIR / "prompt_j_model_comparison.csv", index=False)
print("\n=== SAVED reports/prompt_j_model_comparison.csv ===")
print(df_summary[["model_name", "overall_rmse", "peak_rmse_top10", "overall_mae", "pooled_r2", "macro_rmse", "median_station_rmse", "peak_underprediction_pct"]])

df_st = pd.DataFrame(all_station_records)
df_st.to_csv(REPORTS_DIR / "prompt_j_station_accuracy.csv", index=False)
print(f"\n=== SAVED reports/prompt_j_station_accuracy.csv ({len(df_st)} rows) ===")

# Vicksburg contribution check
sub_vick = df_st[df_st["station_id"] == "07289000"]
for idx, r in sub_vick.iterrows():
    m = r["model_name"]
    st_se = r["squared_error_sum"]
    total_se = np.sum(df_st[df_st["model_name"] == m]["squared_error_sum"])
    pct_se = 100.0 * st_se / total_se
    print(f"[{m}] Vicksburg SE: {st_se:.2e} / Total SE: {total_se:.2e} -> {pct_se:.2f}% of pooled error")

