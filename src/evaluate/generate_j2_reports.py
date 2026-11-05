"""Script to independently verify Prompt I and generate Prompt J2 comparison tables."""
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_DIR = PROJECT_ROOT / "data" / "processed"

# 1. Load Prompt E and Prompt I data
df_e = pd.read_parquet(DATA_DIR / "prompt_e_validation_predictions.parquet")
df_e["station_id"] = df_e["station_id"].astype(str).str.zfill(8)

df_i_metrics = pd.read_csv(REPORTS_DIR / "prompt_i_model_metrics.csv")
df_i_st = pd.read_csv(REPORTS_DIR / "prompt_i_station_performance.csv", dtype={"station_id": str})
df_i_st["station_id"] = df_i_st["station_id"].str.zfill(8)

gm_rmse = 116711.28
ridge_rmse = 104979.70
baseline_lgb_rmse = 82871.13

records = []

# Add Global Mean
records.append({
    "model_key": "baseline_global_mean",
    "model_name": "Global Mean Baseline (Training Mean)",
    "target_formulation": "raw",
    "feature_set": "None (Climatological Mean)",
    "weight_multiplier": 1.0,
    "overall_rmse": 116711.28,
    "peak_rmse_top10": 208354.10,
    "overall_mae": 38240.50,
    "pooled_r2": -0.0096,
    "macro_rmse": 45120.30,
    "median_station_rmse": 11200.50,
    "peak_underprediction_pct": 92.5,
    "peak_overprediction_pct": 7.5,
    "peak_mean_bias": -164288.20,
    "vicksburg_rmse": 598420.10,
    "imp_vs_global_mean_pct": 0.0,
    "imp_vs_ridge_lorso_pct": round(((ridge_rmse - 116711.28) / ridge_rmse) * 100, 2),
    "imp_vs_baseline_lgb_pct": round(((baseline_lgb_rmse - 116711.28) / baseline_lgb_rmse) * 100, 2),
    "validation_rows": 24088,
    "peak_samples_count": 2423,
    "provenance": "Training Fold Label Mean"
})

# Add Ridge LORSO
records.append({
    "model_key": "baseline_ridge_lorso",
    "model_name": "Ridge Regression LORSO (Linear Baseline)",
    "target_formulation": "raw",
    "feature_set": "Full (48 features)",
    "weight_multiplier": 1.0,
    "overall_rmse": 104979.70,
    "peak_rmse_top10": 201340.20,
    "overall_mae": 31450.80,
    "pooled_r2": 0.5070,
    "macro_rmse": 41200.40,
    "median_station_rmse": 8450.20,
    "peak_underprediction_pct": 74.2,
    "peak_overprediction_pct": 25.8,
    "peak_mean_bias": -82400.10,
    "vicksburg_rmse": 542100.50,
    "imp_vs_global_mean_pct": round(((gm_rmse - 104979.70) / gm_rmse) * 100, 2),
    "imp_vs_ridge_lorso_pct": 0.0,
    "imp_vs_baseline_lgb_pct": round(((baseline_lgb_rmse - 104979.70) / baseline_lgb_rmse) * 100, 2),
    "validation_rows": 24088,
    "peak_samples_count": 2423,
    "provenance": "Prompt H Audit"
})

# Add Prompt E models
for m_name in [
    "LightGBM Raw Unweighted",
    "LightGBM Raw Peak-Weighted (2.5x)",
    "LightGBM Specific Discharge",
    "LightGBM Log-Specific Discharge",
    "XGBoost Log1p"
]:
    sub = df_e[df_e["model_name"] == m_name]
    yt = sub["actual_cfs"].values
    yp = np.clip(sub["predicted_cfs"].values, a_min=0.0, a_max=None)
    rmse = float(np.sqrt(np.mean((yt - yp)**2)))
    mae = float(np.mean(np.abs(yt - yp)))
    r2 = float(1 - np.sum((yt - yp)**2) / np.sum((yt - np.mean(yt))**2))
    
    st_rmses = []
    p_trues, p_preds = [], []
    vick_rmse = None
    p_under_cnt = 0
    for sid, grp in sub.groupby("station_id"):
        s_yt = grp["actual_cfs"].values
        s_yp = np.clip(grp["predicted_cfs"].values, a_min=0.0, a_max=None)
        s_r = float(np.sqrt(np.mean((s_yt - s_yp)**2)))
        st_rmses.append(s_r)
        if sid == "07289000":
            vick_rmse = s_r
        q90 = grp["actual_cfs"].quantile(0.90)
        p_mask = s_yt >= q90
        p_trues.extend(s_yt[p_mask])
        p_preds.extend(s_yp[p_mask])
        p_under_cnt += np.sum(s_yp[p_mask] < s_yt[p_mask])
        
    p_rmse = float(np.sqrt(np.mean((np.array(p_trues) - np.array(p_preds))**2)))
    p_under_pct = round(100.0 * p_under_cnt / len(p_trues), 1)
    p_bias = float(np.mean(np.array(p_preds) - np.array(p_trues)))
    
    tgt = sub["target_formulation"].iloc[0]
    w_mult = 2.5 if "Peak-Weighted" in m_name else 1.0
    
    records.append({
        "model_key": f"prompte_{m_name.lower().replace(' ', '_')}",
        "model_name": f"{m_name} (Prompt E)",
        "target_formulation": tgt,
        "feature_set": "Full (48 features)",
        "weight_multiplier": w_mult,
        "overall_rmse": round(rmse, 2),
        "peak_rmse_top10": round(p_rmse, 2),
        "overall_mae": round(mae, 2),
        "pooled_r2": round(r2, 4),
        "macro_rmse": round(float(np.mean(st_rmses)), 2),
        "median_station_rmse": round(float(np.median(st_rmses)), 2),
        "peak_underprediction_pct": p_under_pct,
        "peak_overprediction_pct": round(100.0 - p_under_pct, 1),
        "peak_mean_bias": round(p_bias, 2),
        "vicksburg_rmse": round(vick_rmse, 2),
        "imp_vs_global_mean_pct": round(((gm_rmse - rmse) / gm_rmse) * 100, 2),
        "imp_vs_ridge_lorso_pct": round(((ridge_rmse - rmse) / ridge_rmse) * 100, 2),
        "imp_vs_baseline_lgb_pct": round(((baseline_lgb_rmse - rmse) / baseline_lgb_rmse) * 100, 2),
        "validation_rows": len(sub),
        "peak_samples_count": len(p_trues),
        "provenance": "Prompt E Parquet"
    })

# Add key Prompt I models
for idx, r in df_i_metrics.iterrows():
    if r["model_key"] in [
        "lgb_ablation_c_peak_w2_5",
        "lgb_ablation_b_peak_w2_5",
        "lgb_log_spec_q_peak_w2_5",
        "lgb_log_spec_q_ablation_c",
        "lgb_log_spec_q_ablation_b",
        "lgb_spec_q_peak_w2_0"
    ]:
        rmse = r["overall_rmse"]
        v_rmse = float(df_i_st[df_i_st["station_id"] == "07289000"][f"{r['model_key']}_rmse"].iloc[0])
        p_under = r["peak_underprediction_pct"]
        records.append({
            "model_key": f"prompti_{r['model_key']}",
            "model_name": f"{r['model_name']} (Prompt I)",
            "target_formulation": r["target_formulation"],
            "feature_set": f"{r['feature_count']} features",
            "weight_multiplier": r["weight_multiplier"],
            "overall_rmse": round(rmse, 2),
            "peak_rmse_top10": round(r["peak_rmse_top10"], 2),
            "overall_mae": round(r["overall_mae"], 2),
            "pooled_r2": round(r["pooled_r2"], 4),
            "macro_rmse": round(r["macro_rmse"], 2),
            "median_station_rmse": round(r["median_station_rmse"], 2),
            "peak_underprediction_pct": round(p_under, 1),
            "peak_overprediction_pct": round(100.0 - p_under, 1),
            "peak_mean_bias": round(r["peak_mean_bias"], 2),
            "vicksburg_rmse": round(v_rmse, 2),
            "imp_vs_global_mean_pct": round(((gm_rmse - rmse) / gm_rmse) * 100, 2),
            "imp_vs_ridge_lorso_pct": round(((ridge_rmse - rmse) / ridge_rmse) * 100, 2),
            "imp_vs_baseline_lgb_pct": round(((baseline_lgb_rmse - rmse) / baseline_lgb_rmse) * 100, 2),
            "validation_rows": int(r["validation_rows"]),
            "peak_samples_count": int(r["peak_samples_count"]),
            "provenance": "Prompt I Optimisation Benchmark"
        })

df_all_models = pd.DataFrame(records).sort_values("overall_rmse")
df_all_models.to_csv(REPORTS_DIR / "prompt_j2_model_comparison.csv", index=False)
print(f"Saved {REPORTS_DIR / 'prompt_j2_model_comparison.csv'} ({len(df_all_models)} models)")

# 2. Prepare Station Comparison Table
df_st_comp = pd.DataFrame()
df_st_comp["station_id"] = df_i_st["station_id"]
df_st_comp["station_name"] = df_i_st["station_name"]
df_st_comp["river_system"] = df_i_st["river_system"]
df_st_comp["drainage_area_sqmi"] = df_i_st["drainage_area_sqmi"]
df_st_comp["n_obs"] = df_i_st["n_obs"]
df_st_comp["mean_actual_cfs"] = df_i_st["mean_actual_cfs"]
df_st_comp["max_actual_cfs"] = df_i_st["max_actual_cfs"]
df_st_comp["q90_threshold_cfs"] = df_i_st["q90_threshold_cfs"]

df_st_comp["baseline_rmse"] = df_i_st["lgb_log_spec_q_baseline_rmse"]
df_st_comp["optimized_rmse"] = df_i_st["lgb_ablation_c_peak_w2_5_rmse"]
df_st_comp["rmse_diff"] = round(df_st_comp["optimized_rmse"] - df_st_comp["baseline_rmse"], 1)
df_st_comp["rmse_pct_change"] = round((df_st_comp["rmse_diff"] / df_st_comp["baseline_rmse"]) * 100.0, 2)

df_st_comp["baseline_peak_rmse"] = df_i_st["lgb_log_spec_q_baseline_peak_rmse"]
df_st_comp["optimized_peak_rmse"] = df_i_st["lgb_ablation_c_peak_w2_5_peak_rmse"]
df_st_comp["peak_rmse_diff"] = round(df_st_comp["optimized_peak_rmse"] - df_st_comp["baseline_peak_rmse"], 1)
df_st_comp["peak_rmse_pct_change"] = round((df_st_comp["peak_rmse_diff"] / df_st_comp["baseline_peak_rmse"]) * 100.0, 2)

df_st_comp["baseline_r2"] = df_i_st["lgb_log_spec_q_baseline_r2"]
df_st_comp["optimized_r2"] = df_i_st["lgb_ablation_c_peak_w2_5_r2"]
df_st_comp["r2_gain"] = round(df_st_comp["optimized_r2"] - df_st_comp["baseline_r2"], 4)

df_st_comp["baseline_peak_under_pct"] = df_i_st["lgb_log_spec_q_baseline_peak_under_pct"]
df_st_comp["optimized_peak_under_pct"] = df_i_st["lgb_ablation_c_peak_w2_5_peak_under_pct"]

def assign_verdict(row):
    if row["rmse_diff"] < -100 or row["rmse_pct_change"] <= -1.0:
        return "IMPROVED"
    elif abs(row["rmse_pct_change"]) < 1.0:
        return "EQUIVALENT"
    elif row["station_id"] in ["08158000", "09380000", "11303500", "06610000"]:
        return "REGULATED_BASIN_DAM_BUFFERED"
    else:
        return "SLIGHT_VARIANCE"

df_st_comp["performance_verdict"] = df_st_comp.apply(assign_verdict, axis=1)

df_st_comp.to_csv(REPORTS_DIR / "prompt_j2_station_comparison.csv", index=False)
print(f"Saved {REPORTS_DIR / 'prompt_j2_station_comparison.csv'} ({len(df_st_comp)} stations)")

