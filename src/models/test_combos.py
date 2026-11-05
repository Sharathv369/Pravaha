import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.features.engineering import generate_features
from src.models.prompt_i_targeted_optimization import (
    FEATURE_SET_B_3D_7D, FEATURE_SET_C_14D, compute_training_peak_weights, calculate_full_metrics
)

df_raw = pd.read_csv("data/processed/PRAVAHA_TRAIN_LABELLED.csv", dtype={"station_id": str})
df_features = generate_features(df_raw)
df_features["date"] = pd.to_datetime(df_features["date"])

df_groups = pd.read_csv("reports/river_system_grouping.csv", dtype={"station_id": str})
station_to_system = dict(zip(df_groups["station_id"], df_groups["river_system"]))
df_features["river_system"] = df_features["station_id"].map(station_to_system)
river_systems = df_groups["river_system"].unique().tolist()

test_combos = {
    "lgb_b_peak_w2_0": (FEATURE_SET_B_3D_7D, 2.0, "Ablation B + Peak 2.0x"),
    "lgb_b_peak_w2_5": (FEATURE_SET_B_3D_7D, 2.5, "Ablation B + Peak 2.5x"),
    "lgb_c_peak_w2_0": (FEATURE_SET_C_14D, 2.0, "Ablation C + Peak 2.0x"),
    "lgb_c_peak_w2_5": (FEATURE_SET_C_14D, 2.5, "Ablation C + Peak 2.5x"),
}

fold_preds = []
for fold_idx, held_out in enumerate(river_systems, 1):
    tr_mask = (~df_features["river_system"].isin([held_out])) & (df_features["date"] <= "2021-12-31")
    va_mask = (df_features["river_system"] == held_out) & (df_features["date"] >= "2022-01-01") & (df_features["date"] <= "2023-12-31")
    
    df_tr = df_features[tr_mask].copy()
    df_va = df_features[va_mask].copy()
    if len(df_va) == 0:
        continue
    
    tr_da_mask = df_tr["drainage_area_sqmi"].notna() & (df_tr["drainage_area_sqmi"] > 0)
    df_tr_da = df_tr[tr_da_mask].copy()
    da_tr = df_tr_da["drainage_area_sqmi"].values
    da_va = df_va["drainage_area_sqmi"].values
    
    y_tr_logq = np.log1p(np.maximum(0.0, df_tr_da["discharge_cfs"].values / da_tr))
    w_2_0 = compute_training_peak_weights(df_tr_da, peak_mult=2.0)
    w_2_5 = compute_training_peak_weights(df_tr_da, peak_mult=2.5)
    
    f_res = df_va[["station_id", "date", "discharge_cfs"]].copy()
    
    for k, (f_cols, w_mult, name) in test_combos.items():
        X_tr = df_tr_da[f_cols].fillna(0.0).values
        X_va = df_va[f_cols].fillna(0.0).values
        w = w_2_0 if w_mult == 2.0 else w_2_5
        
        m = lgb.LGBMRegressor(
            objective="regression", n_estimators=250, learning_rate=0.05,
            num_leaves=31, max_depth=6, subsample=0.8, colsample_bytree=0.8,
            random_state=42, n_jobs=-1, verbose=-1
        )
        m.fit(X_tr, y_tr_logq, sample_weight=w)
        pred_logq = m.predict(X_va)
        f_res[k] = np.clip(np.expm1(pred_logq), 0.0, None) * da_va
        
    fold_preds.append(f_res)

val_all = pd.concat(fold_preds, ignore_index=True)
for k, (_, _, name) in test_combos.items():
    metrics = calculate_full_metrics(val_all, k)
    print(f"{name:25s} | RMSE: {metrics['overall_rmse']:10.2f} | Peak RMSE: {metrics['peak_rmse_top10']:10.2f} | MAE: {metrics['overall_mae']:9.2f} | R2: {metrics['pooled_r2']:6.4f} | Peak Under: {metrics['peak_underprediction_pct']:5.1f}% | Bias: {metrics['mean_prediction_bias']:9.2f}")

