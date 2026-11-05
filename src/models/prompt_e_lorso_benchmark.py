"""
PRAVAHA — Prompt E: Leave-One-River-System-Out (LORSO) Validation & Controlled Peak Optimisation
Implements Phases E1 - E8:
- Hydrological river system grouping (23 river systems across 34 stations).
- Strict out-of-system cross-validation (train: <= 2021 from other river systems; val: 2022-2023 on held-out system).
- Evaluates 5 controlled model formulations:
    A. LightGBM raw CFS, unweighted
    B. LightGBM raw CFS, peak-weighted (w=2.5 for y >= q90 of training station)
    C. LightGBM specific discharge (q = Q / A)
    D. LightGBM log-specific discharge (log(q + 1))
    E. XGBoost log1p discharge (log(Q + 1))
- Computes pooled, macro, per-station, and per-river-system metrics (RMSE, Top-10% Peak RMSE, MAE, R2).
- Preserves all previous files; saves all Prompt E deliverables.
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import lightgbm as lgb
import xgboost as xgb

from src.features.engineering import FEATURE_COLUMNS, generate_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prompt_e_lorso")

REPORTS_DIR = Path("reports")
DATA_DIR = Path("data/processed")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_END_DATE = "2021-12-31"
VAL_START_DATE = "2022-01-01"
VAL_END_DATE = "2023-12-31"

def compute_training_peak_weights(df_train: pd.DataFrame, peak_mult: float = 2.5) -> pd.Series:
    """
    Computes sample weights derived STRICTLY from training-fold data only.
    Each training station's 90th percentile flow receives weight = peak_mult.
    """
    weights = pd.Series(1.0, index=df_train.index)
    for sid, grp in df_train.groupby("station_id"):
        q90 = grp["discharge_cfs"].quantile(0.90)
        mask = grp["discharge_cfs"] >= q90
        weights.loc[grp.index[mask]] = peak_mult
    return weights

def evaluate_metrics_bundle(df_val: pd.DataFrame, y_pred_col: str) -> Dict[str, float]:
    """
    Computes RMSE, Top-10% Peak RMSE, MAE, R2 on the provided validation dataframe.
    Peak threshold is derived per-station strictly on actual validation labels for evaluation.
    """
    y_true = df_val["discharge_cfs"].values
    y_pred = np.clip(df_val[y_pred_col].values, a_min=0.0, a_max=None)
    
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    
    peak_trues = []
    peak_preds = []
    for sid, grp in df_val.groupby("station_id"):
        q90 = grp["discharge_cfs"].quantile(0.90)
        p_mask = grp["discharge_cfs"] >= q90
        peak_trues.extend(grp.loc[p_mask, "discharge_cfs"].values)
        peak_preds.extend(np.clip(grp.loc[p_mask, y_pred_col].values, a_min=0.0, a_max=None))
        
    rmse_top10 = float(np.sqrt(mean_squared_error(peak_trues, peak_preds))) if len(peak_trues) > 0 else rmse
    
    return {
        "rmse": rmse,
        "rmse_top10": rmse_top10,
        "mae": mae,
        "r2": r2,
        "n_samples": len(df_val),
        "n_peak_samples": len(peak_trues)
    }

def main():
    logger.info("================================================================================")
    logger.info("PRAVAHA PROMPT E: LEAVE-ONE-RIVER-SYSTEM-OUT (LORSO) BENCHMARK")
    logger.info("================================================================================")
    
    # 1. Load data
    logger.info("Loading labelled master dataset...")
    df_raw = pd.read_csv("data/processed/PRAVAHA_TRAIN_LABELLED.csv", dtype={"station_id": str})
    
    # 2. Generate features
    logger.info("Generating leakage-free feature matrix via generate_features()...")
    df_features = generate_features(df_raw)
    df_features["date"] = pd.to_datetime(df_features["date"])
    
    # 3. Load river system grouping
    grouping_path = REPORTS_DIR / "river_system_grouping.csv"
    if not grouping_path.exists():
        raise FileNotFoundError(f"Missing {grouping_path}")
    df_groups = pd.read_csv(grouping_path, dtype={"station_id": str})
    station_to_system = dict(zip(df_groups["station_id"], df_groups["river_system"]))
    station_to_name = dict(zip(df_groups["station_id"], df_groups["station_name"]))
    df_features["river_system"] = df_features["station_id"].map(station_to_system)
    df_features["station_name"] = df_features["station_id"].map(station_to_name)
    
    # 4. Define the 23 river systems
    river_systems = df_groups["river_system"].unique().tolist()
    logger.info(f"Loaded {len(df_groups)} stations mapped to {len(river_systems)} unique river systems.")
    
    # 5. Prepare feature matrix
    X_cols = FEATURE_COLUMNS
    logger.info(f"Using exactly {len(X_cols)} verified feature columns.")
    
    # List to collect all predictions across folds
    all_predictions = []
    fold_audit_records = []
    
    start_total_time = time.time()
    
    # 5. Run LORSO folds
    for fold_idx, held_out_system in enumerate(river_systems, 1):
        fold_start = time.time()
        sys_stations = df_groups[df_groups["river_system"] == held_out_system]["station_id"].tolist()
        
        # Training split: All other river systems with date <= TRAIN_END_DATE
        train_mask = (~df_features["river_system"].isin([held_out_system])) & (df_features["date"] <= TRAIN_END_DATE)
        df_train = df_features[train_mask].copy()
        
        # Validation split: Held-out river system with date >= VAL_START_DATE and <= VAL_END_DATE
        val_mask = (df_features["river_system"] == held_out_system) & (df_features["date"] >= VAL_START_DATE) & (df_features["date"] <= VAL_END_DATE)
        df_val = df_features[val_mask].copy()
        
        val_stations_in_fold = df_val["station_id"].unique().tolist()
        n_train = len(df_train)
        n_val = len(df_val)
        
        fold_audit_records.append({
            "fold_id": fold_idx,
            "held_out_river_system": held_out_system,
            "held_out_station_ids": ";".join(sys_stations),
            "training_station_ids_count": df_train["station_id"].nunique(),
            "training_sample_count": n_train,
            "validation_sample_count": n_val,
            "training_date_range": f"{df_train['date'].min().strftime('%Y-%m-%d')} to {df_train['date'].max().strftime('%Y-%m-%d')}",
            "validation_date_range": f"{df_val['date'].min().strftime('%Y-%m-%d')} to {df_val['date'].max().strftime('%Y-%m-%d')}" if n_val > 0 else "None",
            "connected_gauges_excluded": len(sys_stations),
            "eligible_held_out_stations": len(val_stations_in_fold)
        })
        
        logger.info(f"--- Fold {fold_idx:02d}/{len(river_systems)}: Held Out '{held_out_system}' ---")
        logger.info(f"    Train: {n_train} rows ({df_train['station_id'].nunique()} stations) | Val: {n_val} rows ({len(val_stations_in_fold)} stations)")
        
        if n_val == 0:
            logger.warning(f"    Fold {fold_idx} has 0 validation rows in 2022-2023. Skipping model fitting.")
            continue
            
        # Compute training peak weights
        df_train["peak_weight"] = compute_training_peak_weights(df_train, peak_mult=2.5)
        
        # Feature arrays
        X_train = df_train[X_cols].fillna(0.0).values
        y_train_raw = df_train["discharge_cfs"].values
        w_train = df_train["peak_weight"].values
        
        X_val = df_val[X_cols].fillna(0.0).values
        y_val_raw = df_val["discharge_cfs"].values
        
        # Base validation prediction dataframe
        fold_val_preds = df_val[["station_id", "station_name", "date", "discharge_cfs", "river_system", "drainage_area_sqmi"]].copy()
        fold_val_preds["fold_id"] = fold_idx
        
        # -------------------------------------------------------------
        # Model A: LightGBM Raw CFS, Unweighted
        # -------------------------------------------------------------
        model_a = lgb.LGBMRegressor(
            objective="regression",
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=31,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        model_a.fit(X_train, y_train_raw)
        preds_a = np.clip(model_a.predict(X_val), a_min=0.0, a_max=None)
        fold_val_preds["pred_lgb_raw_unweighted"] = preds_a
        
        # -------------------------------------------------------------
        # Model B: LightGBM Raw CFS, Peak-Weighted (w=2.5)
        # -------------------------------------------------------------
        model_b = lgb.LGBMRegressor(
            objective="regression",
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=31,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        model_b.fit(X_train, y_train_raw, sample_weight=w_train)
        preds_b = np.clip(model_b.predict(X_val), a_min=0.0, a_max=None)
        fold_val_preds["pred_lgb_raw_peak_weighted"] = preds_b
        
        # -------------------------------------------------------------
        # Model C: LightGBM Specific Discharge (q = Q / A)
        # Train only on stations with verified drainage area
        # -------------------------------------------------------------
        train_da_mask = df_train["drainage_area_sqmi"].notna() & (df_train["drainage_area_sqmi"] > 0)
        X_train_c = df_train.loc[train_da_mask, X_cols].fillna(0.0).values
        da_tr = df_train.loc[train_da_mask, "drainage_area_sqmi"].values
        y_train_c = df_train.loc[train_da_mask, "discharge_cfs"].values / da_tr
        
        model_c = lgb.LGBMRegressor(
            objective="regression",
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=31,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        model_c.fit(X_train_c, y_train_c)
        preds_c_q = np.clip(model_c.predict(X_val), a_min=0.0, a_max=None)
        da_val = df_val["drainage_area_sqmi"].values
        preds_c = preds_c_q * da_val
        fold_val_preds["pred_lgb_spec_q"] = preds_c
        
        # -------------------------------------------------------------
        # Model D: LightGBM Log-Specific Discharge (log(q + 1))
        # -------------------------------------------------------------
        y_train_d = np.log1p(np.maximum(0.0, y_train_c))
        model_d = lgb.LGBMRegressor(
            objective="regression",
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=31,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbose=-1
        )
        model_d.fit(X_train_c, y_train_d)
        preds_d_logq = model_d.predict(X_val)
        preds_d_q = np.clip(np.expm1(preds_d_logq), a_min=0.0, a_max=None)
        preds_d = preds_d_q * da_val
        fold_val_preds["pred_lgb_log_spec_q"] = preds_d
        
        # -------------------------------------------------------------
        # Model E: XGBoost Log1p Discharge (log(Q + 1))
        # -------------------------------------------------------------
        y_train_e = np.log1p(np.maximum(0.0, y_train_raw))
        model_e = xgb.XGBRegressor(
            objective="reg:squarederror",
            n_estimators=250,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            random_state=42,
            n_jobs=-1
        )
        model_e.fit(X_train, y_train_e)
        preds_e_log = model_e.predict(X_val)
        preds_e = np.clip(np.expm1(preds_e_log), a_min=0.0, a_max=None)
        fold_val_preds["pred_xgb_log1p"] = preds_e
        
        all_predictions.append(fold_val_preds)
        elapsed_fold = time.time() - fold_start
        logger.info(f"    Completed Fold {fold_idx} in {elapsed_fold:.2f}s")

    # Combine all out-of-system predictions
    df_all_preds = pd.concat(all_predictions, ignore_index=True)
    total_val_rows = len(df_all_preds)
    logger.info(f"Total out-of-system validation predictions accumulated: {total_val_rows} rows.")
    
    # 6. Save long-format parquet predictions as required by Phase E8
    logger.info("Restructuring and saving validation predictions to parquet...")
    model_col_map = {
        "pred_lgb_raw_unweighted": ("LightGBM Raw Unweighted", "raw"),
        "pred_lgb_raw_peak_weighted": ("LightGBM Raw Peak-Weighted (2.5x)", "raw"),
        "pred_lgb_spec_q": ("LightGBM Specific Discharge", "spec_q"),
        "pred_lgb_log_spec_q": ("LightGBM Log-Specific Discharge", "log_spec_q"),
        "pred_xgb_log1p": ("XGBoost Log1p", "log1p")
    }
    
    parquet_rows = []
    for col, (m_name, t_form) in model_col_map.items():
        sub = df_all_preds[["fold_id", "river_system", "station_id", "date", "discharge_cfs", col]].copy()
        sub.rename(columns={"discharge_cfs": "actual_cfs", col: "predicted_cfs"}, inplace=True)
        sub["model_name"] = m_name
        sub["target_formulation"] = t_form
        parquet_rows.append(sub)
        
    df_parquet = pd.concat(parquet_rows, ignore_index=True)
    parquet_path = DATA_DIR / "prompt_e_validation_predictions.parquet"
    df_parquet.to_parquet(parquet_path, index=False)
    logger.info(f"Saved {len(df_parquet)} prediction records to {parquet_path}")

    # 7. Compute Metric Bundles
    logger.info("Computing pooled, macro, per-station, and per-river-system metrics...")
    
    overall_results = []
    station_metrics = []
    system_metrics = []
    
    for col, (m_name, t_form) in model_col_map.items():
        # Overall pooled metrics
        pooled = evaluate_metrics_bundle(df_all_preds, col)
        
        # Per-station metrics
        st_rmses, st_peaks, st_maes, st_r2s = [], [], [], []
        
        for sid, grp in df_all_preds.groupby("station_id"):
            st_eval = evaluate_metrics_bundle(grp, col)
            st_rmses.append(st_eval["rmse"])
            st_peaks.append(st_eval["rmse_top10"])
            st_maes.append(st_eval["mae"])
            st_r2s.append(st_eval["r2"])
            
            s_name = grp["station_name"].iloc[0]
            r_sys = grp["river_system"].iloc[0]
            q90_val = grp["discharge_cfs"].quantile(0.90)
            
            station_metrics.append({
                "model_name": m_name,
                "target_formulation": t_form,
                "station_id": sid,
                "station_name": s_name,
                "river_system": r_sys,
                "n_samples": st_eval["n_samples"],
                "n_peak_samples": st_eval["n_peak_samples"],
                "q90_threshold_cfs": q90_val,
                "rmse": st_eval["rmse"],
                "rmse_top10": st_eval["rmse_top10"],
                "mae": st_eval["mae"],
                "r2": st_eval["r2"]
            })
            
        # Per-river-system metrics
        for r_sys, s_grp in df_all_preds.groupby("river_system"):
            sys_eval = evaluate_metrics_bundle(s_grp, col)
            system_metrics.append({
                "model_name": m_name,
                "target_formulation": t_form,
                "river_system": r_sys,
                "n_stations": s_grp["station_id"].nunique(),
                "n_samples": sys_eval["n_samples"],
                "n_peak_samples": sys_eval["n_peak_samples"],
                "rmse": sys_eval["rmse"],
                "rmse_top10": sys_eval["rmse_top10"],
                "mae": sys_eval["mae"],
                "r2": sys_eval["r2"]
            })
            
        overall_results.append({
            "model_name": m_name,
            "target_formulation": t_form,
            "peak_weighted": "Yes (2.5x)" if "Peak-Weighted" in m_name else "No",
            "pooled_rmse": pooled["rmse"],
            "pooled_rmse_top10": pooled["rmse_top10"],
            "pooled_mae": pooled["mae"],
            "pooled_r2": pooled["r2"],
            "macro_rmse": float(np.mean(st_rmses)),
            "macro_rmse_top10": float(np.mean(st_peaks)),
            "macro_mae": float(np.mean(st_maes)),
            "macro_r2": float(np.mean(st_r2s)),
            "validation_rows": total_val_rows,
            "active_stations": df_all_preds["station_id"].nunique()
        })
        
    df_overall = pd.DataFrame(overall_results)
    df_st_metrics = pd.DataFrame(station_metrics)
    df_sys_metrics = pd.DataFrame(system_metrics)
    df_folds = pd.DataFrame(fold_audit_records)
    
    # Save CSVs
    df_overall.to_csv(REPORTS_DIR / "lors_validation_results.csv", index=False)
    df_st_metrics.to_csv(REPORTS_DIR / "lors_per_station_metrics.csv", index=False)
    df_sys_metrics.to_csv(REPORTS_DIR / "lors_per_river_system_metrics.csv", index=False)
    logger.info("Saved lors_validation_results.csv, lors_per_station_metrics.csv, lors_per_river_system_metrics.csv")
    
    total_time = time.time() - start_total_time
    logger.info(f"All Prompt E LORSO benchmark computations completed in {total_time:.2f}s.")
    
    # 8. Print Executive Comparison
    print("\n" + "="*95)
    print("PRAVAHA PROMPT E — LEAVE-ONE-RIVER-SYSTEM-OUT (LORSO) BENCHMARK RESULTS")
    print("="*95)
    print(df_overall[["model_name", "target_formulation", "pooled_rmse", "pooled_rmse_top10", "pooled_mae", "pooled_r2"]].to_string())
    print("="*95)

if __name__ == "__main__":
    main()
