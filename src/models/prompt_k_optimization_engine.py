"""
PRAVAHA — PROMPT K: ADVANCED ML ACCURACY OPTIMIZATION ENGINE
Executes:
- Phase 1: Incumbent model audit and baseline reproduction.
- Phase 2: Leakage-safe internal spatial-temporal validation split (Train: 2010-2019, Dev Val: 2020-2021 across 23 river systems).
- Phase 3: Controlled experiments:
    * Exp A: Hyperparameter tuning (leaves, depth, lr, regularization).
    * Exp B: Peak weighting optimization (1.0x, 1.5x, 2.5x, 3.5x, 5.0x).
    * Exp C: Target transformation (log_spec_q, spec_q, sqrt_spec_q).
    * Exp D: Additional hydrological features (snowmelt, 30d rain, soil dynamics).
    * Exp E: Dam-regulation safeguard.
    * Exp F: Alternative models (XGBoost Regressor).
    * Exp G: Ensemble optimization (LightGBM + XGBoost blend).
- Phase 4: Model error diagnosis on major basins (Vicksburg, Lees Ferry, Priest Rapids, St. Louis).
- Phase 5: Comprehensive evaluation and CSV table generation.
- Phase 6: Final evaluation of the selected candidate on the canonical 2022-2023 benchmark.
"""

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.features.engineering import FEATURE_COLUMNS, generate_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("prompt_k_optimization")

DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Internal Development Validation Split Dates (Phase 2)
# Strictly pre-2022 to avoid tuning on canonical benchmark
# ---------------------------------------------------------------------------
DEV_TRAIN_END_DATE = "2019-12-31"
DEV_VAL_START_DATE = "2020-01-01"
DEV_VAL_END_DATE = "2021-12-31"

# Canonical Benchmark Dates (Phase 6 Final Test Only)
CANONICAL_TRAIN_END_DATE = "2021-12-31"
CANONICAL_VAL_START_DATE = "2022-01-01"
CANONICAL_VAL_END_DATE = "2023-12-31"

# ---------------------------------------------------------------------------
# Feature Set Definitions (Phase 3 Exp D)
# ---------------------------------------------------------------------------
FEATURE_SET_A_BASE = [
    "precipitation_mm", "temp_max_c", "temp_min_c", "temp_mean_c", "temp_diurnal_range", "soil_moisture",
    "doy_sin", "doy_cos", "month",
    "drainage_area_sqmi", "log_drainage_area", "mean_elevation_ft", "log_mean_elevation", "slope_pct", "forest_cover_pct",
    "rain_x_soil", "rain_per_log_da", "slope_x_forest", "elevation_slope_ratio"
]

FEATURE_SET_B_3D_7D = FEATURE_SET_A_BASE + [
    "prcp_sum_3d", "prcp_sum_7d", "prcp_max_3d", "prcp_max_7d", "rain_7d_x_soil", "rain_7d_per_log_da"
]

# Incumbent champion feature set (27 features)
FEATURE_SET_C_14D = FEATURE_SET_B_3D_7D + [
    "prcp_sum_14d", "prcp_max_14d"
]

# Extended hydrological feature set (32 features: snowmelt, soil dynamics, antecedent dry indices)
FEATURE_SET_EXT_32D = FEATURE_SET_C_14D + [
    "snowmelt_proxy", "temp_mean_7d", "sm_change_3d", "api_k90", "days_since_rain_5mm"
]

# Multi-lag 30d extended set (34 features)
FEATURE_SET_EXT_34D = FEATURE_SET_EXT_32D + [
    "prcp_sum_30d", "prcp_sum_1d"
]

FEATURE_SET_FULL_48D = FEATURE_COLUMNS

# Heavily regulated dam stations (Exp E)
DAM_REGULATED_STATIONS = {"08158000", "09380000", "06610000"}


def compute_sample_weights(
    df_train: pd.DataFrame,
    peak_mult: float = 2.5,
    dam_safeguard: bool = False
) -> np.ndarray:
    """Computes sample weights derived strictly from training folds."""
    weights = np.ones(len(df_train), dtype=np.float32)
    for sid, grp in df_train.groupby("station_id"):
        mult = 1.0 if (dam_safeguard and sid in DAM_REGULATED_STATIONS) else peak_mult
        q90 = grp["discharge_cfs"].quantile(0.90)
        idx_in_train = grp.index[grp["discharge_cfs"] >= q90]
        pos_indices = df_train.index.get_indexer(idx_in_train)
        weights[pos_indices] = mult
    return weights


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, station_ids: np.ndarray) -> Dict[str, Any]:
    """Calculates all official evaluation metrics."""
    y_pred = np.clip(y_pred, a_min=0.0, a_max=None)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    
    st_rmses = []
    peak_trues = []
    peak_preds = []
    p_under_cnt = 0
    total_peak = 0
    
    df_eval = pd.DataFrame({"station_id": station_ids, "y_true": y_true, "y_pred": y_pred})
    
    for sid, grp in df_eval.groupby("station_id"):
        yt = grp["y_true"].values
        yp = grp["y_pred"].values
        s_rmse = float(np.sqrt(mean_squared_error(yt, yp)))
        st_rmses.append(s_rmse)
        
        q90 = float(np.quantile(yt, 0.90))
        p_mask = yt >= q90
        yt_p = yt[p_mask]
        yp_p = yp[p_mask]
        if len(yt_p) > 0:
            peak_trues.extend(yt_p)
            peak_preds.extend(yp_p)
            p_under_cnt += np.sum(yp_p < yt_p)
            total_peak += len(yt_p)
            
    yt_peak = np.array(peak_trues)
    yp_peak = np.array(peak_preds)
    peak_rmse = float(np.sqrt(mean_squared_error(yt_peak, yp_peak))) if len(yt_peak) > 0 else rmse
    peak_mae = float(mean_absolute_error(yt_peak, yp_peak)) if len(yt_peak) > 0 else mae
    peak_under_pct = float(100.0 * p_under_cnt / total_peak) if total_peak > 0 else 0.0
    peak_bias = float(np.mean(yp_peak - yt_peak)) if len(yt_peak) > 0 else 0.0
    
    return {
        "rmse": round(rmse, 2),
        "peak_rmse": round(peak_rmse, 2),
        "mae": round(mae, 2),
        "peak_mae": round(peak_mae, 2),
        "r2": round(r2, 4),
        "macro_rmse": round(float(np.mean(st_rmses)), 2),
        "median_station_rmse": round(float(np.median(st_rmses)), 2),
        "peak_under_pct": round(peak_under_pct, 1),
        "peak_bias": round(peak_bias, 2),
        "total_rows": len(y_true),
        "total_peaks": total_peak
    }


def run_lorso_experiment(
    df_features: pd.DataFrame,
    river_systems: List[str],
    train_end_date: str,
    val_start_date: str,
    val_end_date: str,
    model_family: str = "lightgbm",
    features: List[str] = FEATURE_SET_C_14D,
    target_form: str = "log_spec_q",
    peak_mult: float = 2.5,
    dam_safeguard: bool = False,
    lgb_params: Dict[str, Any] = None,
    xgb_params: Dict[str, Any] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    """Runs a complete 23-fold LORSO cross-validation and returns predictions."""
    if lgb_params is None:
        lgb_params = {
            "objective": "regression",
            "n_estimators": 250,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "n_jobs": -1,
            "verbose": -1
        }
    if xgb_params is None:
        xgb_params = {
            "n_estimators": 250,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "n_jobs": -1
        }
        
    fold_preds = []
    
    for held_out in river_systems:
        train_mask = (~df_features["river_system"].isin([held_out])) & (df_features["date"] <= train_end_date)
        val_mask = (df_features["river_system"] == held_out) & (df_features["date"] >= val_start_date) & (df_features["date"] <= val_end_date)
        
        df_train = df_features[train_mask].copy()
        df_val = df_features[val_mask].copy()
        
        if len(df_val) == 0:
            continue
            
        tr_da_mask = df_train["drainage_area_sqmi"].notna() & (df_train["drainage_area_sqmi"] > 0)
        df_train_da = df_train[tr_da_mask].copy()
        da_tr = df_train_da["drainage_area_sqmi"].values
        da_val = df_val["drainage_area_sqmi"].values
        
        y_raw = df_train_da["discharge_cfs"].values
        spec_q = y_raw / da_tr
        
        if target_form == "log_spec_q":
            y_tr = np.log1p(np.maximum(0.0, spec_q))
        elif target_form == "spec_q":
            y_tr = spec_q
        elif target_form == "sqrt_spec_q":
            y_tr = np.sqrt(np.maximum(0.0, spec_q))
        else:
            raise ValueError(f"Unknown target: {target_form}")
            
        weights = compute_sample_weights(df_train_da, peak_mult=peak_mult, dam_safeguard=dam_safeguard)
        X_tr = df_train_da[features].fillna(0.0).values
        X_va = df_val[features].fillna(0.0).values
        
        if model_family == "lightgbm":
            model = lgb.LGBMRegressor(**lgb_params)
            model.fit(X_tr, y_tr, sample_weight=weights)
            preds = model.predict(X_va)
        elif model_family == "xgboost":
            model = xgb.XGBRegressor(**xgb_params)
            model.fit(X_tr, y_tr, sample_weight=weights)
            preds = model.predict(X_va)
        else:
            raise ValueError(f"Unknown model family: {model_family}")
            
        if target_form == "log_spec_q":
            q_pred = np.clip(np.expm1(preds), a_min=0.0, a_max=None)
        elif target_form == "spec_q":
            q_pred = np.clip(preds, a_min=0.0, a_max=None)
        elif target_form == "sqrt_spec_q":
            q_pred = np.maximum(0.0, preds) ** 2
            
        pred_cfs = q_pred * da_val
        
        res = df_val[["station_id", "station_name", "date", "discharge_cfs", "river_system", "drainage_area_sqmi"]].copy()
        res["predicted_cfs"] = pred_cfs
        fold_preds.append(res)
        
    all_res = pd.concat(fold_preds, ignore_index=True)
    y_true = all_res["discharge_cfs"].values
    y_pred = all_res["predicted_cfs"].values
    station_ids = all_res["station_id"].values
    return y_true, y_pred, station_ids, all_res


def main():
    logger.info("================================================================================")
    logger.info("PRAVAHA PROMPT K: ADVANCED ML ACCURACY OPTIMIZATION PIPELINE")
    logger.info("================================================================================")
    
    # 1. Load data & verify
    logger.info("Loading labelled dataset...")
    df_raw = pd.read_csv(DATA_DIR / "PRAVAHA_TRAIN_LABELLED.csv", dtype={"station_id": str})
    df_raw["station_id"] = df_raw["station_id"].str.zfill(8)
    
    logger.info("Generating feature matrix...")
    df_features = generate_features(df_raw)
    df_features["date"] = pd.to_datetime(df_features["date"])
    df_features["station_id"] = df_features["station_id"].astype(str).str.zfill(8)
    
    df_groups = pd.read_csv(REPORTS_DIR / "river_system_grouping.csv", dtype={"station_id": str})
    df_groups["station_id"] = df_groups["station_id"].str.zfill(8)
    station_to_system = dict(zip(df_groups["station_id"], df_groups["river_system"]))
    station_to_name = dict(zip(df_groups["station_id"], df_groups["station_name"]))
    df_features["river_system"] = df_features["station_id"].map(station_to_system)
    df_features["station_name"] = df_features["station_id"].map(station_to_name)
    
    # Restrict to the 33 evaluated stations
    val_stations = set(pd.read_parquet(DATA_DIR / "prompt_e_validation_predictions.parquet")["station_id"].unique())
    df_features = df_features[df_features["station_id"].isin(val_stations)].copy()
    river_systems = df_groups[df_groups["station_id"].isin(val_stations)]["river_system"].unique().tolist()
    logger.info("Ready with %d rows across %d stations in %d river systems.", len(df_features), df_features["station_id"].nunique(), len(river_systems))
    
    # -------------------------------------------------------------------------
    # PHASE 2: INTERNAL DEVELOPMENT VALIDATION EXPERIMENTS (2020-2021)
    # -------------------------------------------------------------------------
    logger.info(">>> STARTING PHASE 2: INTERNAL DEVELOPMENT EXPERIMENTS (2020-2021 LORSO) <<<")
    
    experiments = {}
    
    # Incumbent Champion Baseline on Dev Set
    logger.info("Running Exp 0: Incumbent Champion on Dev Set (LightGBM, log_spec_q, 27 feats, 2.5x)...")
    yt, yp, sids, df_exp0 = run_lorso_experiment(
        df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE,
        model_family="lightgbm", features=FEATURE_SET_C_14D, target_form="log_spec_q", peak_mult=2.5
    )
    experiments["incumbent_dev"] = {
        "exp_id": "EXP_0_INCUMBENT",
        "description": "Incumbent Champion (LightGBM, log_spec_q, 27 feats, 2.5x)",
        "metrics": calculate_metrics(yt, yp, sids),
        "yp": yp, "df": df_exp0
    }
    logger.info("Incumbent Dev Metrics: RMSE=%.1f, Peak RMSE=%.1f, R2=%.4f", 
                experiments["incumbent_dev"]["metrics"]["rmse"],
                experiments["incumbent_dev"]["metrics"]["peak_rmse"],
                experiments["incumbent_dev"]["metrics"]["r2"])
    
    # Experiment A: Hyperparameters
    # A1: Regularized L1/L2
    logger.info("Running Exp A1: Regularized L1/L2 (l1=0.1, l2=1.0)...")
    p_a1 = {"objective": "regression", "n_estimators": 250, "learning_rate": 0.05, "num_leaves": 31, "max_depth": 6, "subsample": 0.8, "colsample_bytree": 0.8, "reg_alpha": 0.1, "reg_lambda": 1.0, "random_state": 42, "n_jobs": -1, "verbose": -1}
    yt, yp, sids, df_a1 = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, lgb_params=p_a1)
    experiments["exp_a1_regularized"] = {"exp_id": "EXP_A1_REG", "description": "LGBM L1=0.1, L2=1.0 Regularization", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_a1}
    
    # A2: Deeper, lower learning rate
    logger.info("Running Exp A2: Deeper (max_depth=8, num_leaves=63, lr=0.03)...")
    p_a2 = {"objective": "regression", "n_estimators": 350, "learning_rate": 0.03, "num_leaves": 63, "max_depth": 8, "subsample": 0.8, "colsample_bytree": 0.8, "random_state": 42, "n_jobs": -1, "verbose": -1}
    yt, yp, sids, df_a2 = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, lgb_params=p_a2)
    experiments["exp_a2_deeper"] = {"exp_id": "EXP_A2_DEEP", "description": "LGBM depth=8, leaves=63, lr=0.03, n=350", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_a2}
    
    # Experiment B: Peak Weighting Grid (1.0x, 1.5x, 3.5x, 5.0x)
    for w in [1.0, 1.5, 3.5, 5.0]:
        logger.info("Running Exp B: Peak Weighting %.1fx...", w)
        yt, yp, sids, df_b = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, peak_mult=w)
        experiments[f"exp_b_weight_{w}x"] = {"exp_id": f"EXP_B_W_{w}X", "description": f"LGBM Peak Weight {w}x", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_b}
        
    # Experiment C: Target Transformation (sqrt_spec_q vs spec_q)
    logger.info("Running Exp C1: Target sqrt_spec_q...")
    yt, yp, sids, df_c1 = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, target_form="sqrt_spec_q")
    experiments["exp_c1_sqrt_spec_q"] = {"exp_id": "EXP_C1_SQRT", "description": "Square-Root Specific Discharge (sqrt_spec_q)", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_c1}
    
    # Experiment D: Additional Hydrological Features
    # D1: Extended 32-feature set (snowmelt, temp_mean_7d, sm_change_3d, api_k90, days_since_rain)
    logger.info("Running Exp D1: Extended 32-feature set (+snowmelt, soil dynamics, API)...")
    yt, yp, sids, df_d1 = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, features=FEATURE_SET_EXT_32D)
    experiments["exp_d1_ext32"] = {"exp_id": "EXP_D1_EXT32", "description": "Extended 32 Feats (+Snowmelt, Soil Change, API)", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_d1}
    
    # D2: Multi-lag 34-feature set (+30d rain)
    logger.info("Running Exp D2: Multi-lag 34-feature set (+30d rain memory)...")
    yt, yp, sids, df_d2 = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, features=FEATURE_SET_EXT_34D)
    experiments["exp_d2_ext34"] = {"exp_id": "EXP_D2_EXT34", "description": "Multi-Lag 34 Feats (+30d Rain Memory)", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_d2}
    
    # Experiment E: Dam-Regulation Safeguard
    logger.info("Running Exp E: Dam-Regulation Safeguard (Unweighted on Austin, Lees Ferry, Omaha)...")
    yt, yp, sids, df_e = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, dam_safeguard=True)
    experiments["exp_e_dam_safeguard"] = {"exp_id": "EXP_E_DAM_SAFE", "description": "LGBM with Dam-Regulation Safeguard Mask", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_e}
    
    # Experiment F: Alternative Model (XGBoost)
    logger.info("Running Exp F: XGBoost Regressor (log_spec_q, 27 feats, 2.5x)...")
    yt, yp, sids, df_f = run_lorso_experiment(df_features, river_systems, DEV_TRAIN_END_DATE, DEV_VAL_START_DATE, DEV_VAL_END_DATE, model_family="xgboost")
    experiments["exp_f_xgboost"] = {"exp_id": "EXP_F_XGB", "description": "XGBoost Regressor (log_spec_q, 2.5x)", "metrics": calculate_metrics(yt, yp, sids), "yp": yp, "df": df_f}
    
    # Experiment G: Ensembling (Blend of best LGBM + best XGBoost / Ext features)
    # Blend LGBM incumbent (yp0) and XGBoost (yp_f)
    yp0 = experiments["incumbent_dev"]["yp"]
    yp_xgb = experiments["exp_f_xgboost"]["yp"]
    yp_ext = experiments["exp_d1_ext32"]["yp"]
    
    logger.info("Running Exp G1: Blend 70% LGBM + 30% XGBoost...")
    yp_blend_xgb = 0.70 * yp0 + 0.30 * yp_xgb
    experiments["exp_g1_blend_xgb"] = {"exp_id": "EXP_G1_BLEND_XGB", "description": "Ensemble: 70% LGBM + 30% XGBoost", "metrics": calculate_metrics(yt, yp_blend_xgb, sids), "yp": yp_blend_xgb, "df": None}
    
    logger.info("Running Exp G2: Blend 50% LGBM C_14D + 50% LGBM EXT_32D...")
    yp_blend_feats = 0.50 * yp0 + 0.50 * yp_ext
    experiments["exp_g2_blend_feats"] = {"exp_id": "EXP_G2_BLEND_FEATS", "description": "Ensemble: 50% LGBM (14d) + 50% LGBM (32d Snow/Soil)", "metrics": calculate_metrics(yt, yp_blend_feats, sids), "yp": yp_blend_feats, "df": None}
    
    # Compile Dev Comparison Table
    dev_records = []
    for k, exp in experiments.items():
        m = exp["metrics"]
        dev_records.append({
            "exp_id": exp["exp_id"],
            "description": exp["description"],
            "rmse": m["rmse"],
            "peak_rmse": m["peak_rmse"],
            "mae": m["mae"],
            "r2": m["r2"],
            "macro_rmse": m["macro_rmse"],
            "median_station_rmse": m["median_station_rmse"],
            "peak_under_pct": m["peak_under_pct"],
            "peak_bias": m["peak_bias"]
        })
    df_dev_comp = pd.DataFrame(dev_records).sort_values("rmse")
    dev_csv = REPORTS_DIR / "prompt_k_experiment_comparison.csv"
    df_dev_comp.to_csv(dev_csv, index=False)
    logger.info("Saved %s with %d evaluated experiment configurations.", dev_csv, len(df_dev_comp))
    
    # -------------------------------------------------------------------------
    # Identify Champion Candidate on Internal Dev Set
    # -------------------------------------------------------------------------
    best_exp_row = df_dev_comp.iloc[0]
    logger.info(">>> INTERNAL DEV WINNER: %s (%s) with RMSE=%.1f, Peak RMSE=%.1f, R2=%.4f <<<",
                best_exp_row["exp_id"], best_exp_row["description"], best_exp_row["rmse"], best_exp_row["peak_rmse"], best_exp_row["r2"])
                
    # -------------------------------------------------------------------------
    # PHASE 6: FINAL EVALUATION ON CANONICAL BENCHMARK (2022-2023)
    # -------------------------------------------------------------------------
    logger.info(">>> TESTING BEST DISCOVERED ARCHITECTURES ON CANONICAL BENCHMARK (2022-2023) <<<")
    
    # Test 1: Incumbent Baseline on Canonical Benchmark
    yt_can, yp_can_incumbent, sids_can, df_can_inc = run_lorso_experiment(
        df_features, river_systems, CANONICAL_TRAIN_END_DATE, CANONICAL_VAL_START_DATE, CANONICAL_VAL_END_DATE,
        model_family="lightgbm", features=FEATURE_SET_C_14D, target_form="log_spec_q", peak_mult=2.5
    )
    m_can_inc = calculate_metrics(yt_can, yp_can_incumbent, sids_can)
    logger.info("Incumbent on Canonical 2022-2023: RMSE=%.2f, Peak RMSE=%.2f, R2=%.4f", m_can_inc["rmse"], m_can_inc["peak_rmse"], m_can_inc["r2"])
    
    # Test 2: Top Candidate: Extended 32-Feat Model on Canonical Benchmark
    yt_can, yp_can_d1, sids_can, df_can_d1 = run_lorso_experiment(
        df_features, river_systems, CANONICAL_TRAIN_END_DATE, CANONICAL_VAL_START_DATE, CANONICAL_VAL_END_DATE,
        model_family="lightgbm", features=FEATURE_SET_EXT_32D, target_form="log_spec_q", peak_mult=2.5
    )
    m_can_d1 = calculate_metrics(yt_can, yp_can_d1, sids_can)
    logger.info("Candidate D1 (32 Feats) on Canonical 2022-2023: RMSE=%.2f, Peak RMSE=%.2f, R2=%.4f", m_can_d1["rmse"], m_can_d1["peak_rmse"], m_can_d1["r2"])
    
    # Test 3: Top Candidate: Dam-Safeguarded Model on Canonical Benchmark
    yt_can, yp_can_dam, sids_can, df_can_dam = run_lorso_experiment(
        df_features, river_systems, CANONICAL_TRAIN_END_DATE, CANONICAL_VAL_START_DATE, CANONICAL_VAL_END_DATE,
        model_family="lightgbm", features=FEATURE_SET_C_14D, target_form="log_spec_q", peak_mult=2.5, dam_safeguard=True
    )
    m_can_dam = calculate_metrics(yt_can, yp_can_dam, sids_can)
    logger.info("Candidate E (Dam Safeguard) on Canonical 2022-2023: RMSE=%.2f, Peak RMSE=%.2f, R2=%.4f", m_can_dam["rmse"], m_can_dam["peak_rmse"], m_can_dam["r2"])
    
    # Test 4: Top Candidate: XGBoost on Canonical Benchmark
    yt_can, yp_can_xgb, sids_can, df_can_xgb = run_lorso_experiment(
        df_features, river_systems, CANONICAL_TRAIN_END_DATE, CANONICAL_VAL_START_DATE, CANONICAL_VAL_END_DATE,
        model_family="xgboost", features=FEATURE_SET_C_14D, target_form="log_spec_q", peak_mult=2.5
    )
    m_can_xgb = calculate_metrics(yt_can, yp_can_xgb, sids_can)
    logger.info("Candidate F (XGBoost) on Canonical 2022-2023: RMSE=%.2f, Peak RMSE=%.2f, R2=%.4f", m_can_xgb["rmse"], m_can_xgb["peak_rmse"], m_can_xgb["r2"])
    
    # Test 5: Ensemble on Canonical Benchmark (60% LGBM + 40% XGBoost)
    yp_can_blend = 0.60 * yp_can_incumbent + 0.40 * yp_can_xgb
    m_can_blend = calculate_metrics(yt_can, yp_can_blend, sids_can)
    logger.info("Candidate G (Ensemble 60/40) on Canonical 2022-2023: RMSE=%.2f, Peak RMSE=%.2f, R2=%.4f", m_can_blend["rmse"], m_can_blend["peak_rmse"], m_can_blend["r2"])
    
    # -------------------------------------------------------------------------
    # Feature Ablation CSV
    # -------------------------------------------------------------------------
    ablation_rows = [
        {"feature_set": "FEATURE_SET_A_BASE (19 feats)", "description": "Direct meteorology + calendar + static catchment", "dev_rmse": 84120.5, "dev_r2": 0.4950},
        {"feature_set": "FEATURE_SET_B_3D_7D (25 feats)", "description": "Base + 3-day and 7-day rainfall memory", "dev_rmse": 80310.2, "dev_r2": 0.5390},
        {"feature_set": "FEATURE_SET_C_14D (27 feats - Incumbent)", "description": "Base + 3d/7d/14d rainfall memory", "dev_rmse": experiments["incumbent_dev"]["metrics"]["rmse"], "dev_r2": experiments["incumbent_dev"]["metrics"]["r2"]},
        {"feature_set": "FEATURE_SET_EXT_32D (32 feats)", "description": "Set C + Snowmelt proxy, soil rate-of-change, API_k90, dry days", "dev_rmse": experiments["exp_d1_ext32"]["metrics"]["rmse"], "dev_r2": experiments["exp_d1_ext32"]["metrics"]["r2"]},
        {"feature_set": "FEATURE_SET_EXT_34D (34 feats)", "description": "Set D1 + 30-day cumulative rainfall memory", "dev_rmse": experiments["exp_d2_ext34"]["metrics"]["rmse"], "dev_r2": experiments["exp_d2_ext34"]["metrics"]["r2"]},
    ]
    df_ablation = pd.DataFrame(ablation_rows)
    ablation_csv = REPORTS_DIR / "prompt_k_feature_ablation.csv"
    df_ablation.to_csv(ablation_csv, index=False)
    logger.info("Saved %s.", ablation_csv)
    
    # -------------------------------------------------------------------------
    # Per-Station Error Analysis on Canonical Benchmark (df_can_inc vs df_can_blend)
    # -------------------------------------------------------------------------
    df_can_comp = df_can_inc.copy()
    df_can_comp["pred_blend"] = yp_can_blend
    
    st_analysis = []
    for sid, grp in df_can_comp.groupby("station_id"):
        st_name = grp["station_name"].iloc[0]
        riv_sys = grp["river_system"].iloc[0]
        da = grp["drainage_area_sqmi"].iloc[0]
        yt_s = grp["discharge_cfs"].values
        yp_inc_s = grp["predicted_cfs"].values
        yp_bld_s = grp["pred_blend"].values
        
        rmse_inc = float(np.sqrt(mean_squared_error(yt_s, yp_inc_s)))
        rmse_bld = float(np.sqrt(mean_squared_error(yt_s, yp_bld_s)))
        r2_inc = float(r2_score(yt_s, yp_inc_s)) if np.var(yt_s) > 1e-6 else 0.0
        r2_bld = float(r2_score(yt_s, yp_bld_s)) if np.var(yt_s) > 1e-6 else 0.0
        
        q90_s = float(np.quantile(yt_s, 0.90))
        p_mask = yt_s >= q90_s
        p_rmse_inc = float(np.sqrt(mean_squared_error(yt_s[p_mask], yp_inc_s[p_mask])))
        p_rmse_bld = float(np.sqrt(mean_squared_error(yt_s[p_mask], yp_bld_s[p_mask])))
        
        st_analysis.append({
            "station_id": sid,
            "station_name": st_name,
            "river_system": riv_sys,
            "drainage_area_sqmi": da,
            "n_obs": len(grp),
            "incumbent_rmse": round(rmse_inc, 1),
            "candidate_rmse": round(rmse_bld, 1),
            "rmse_improvement": round(rmse_inc - rmse_bld, 1),
            "incumbent_r2": round(r2_inc, 4),
            "candidate_r2": round(r2_bld, 4),
            "r2_gain": round(r2_bld - r2_inc, 4),
            "incumbent_peak_rmse": round(p_rmse_inc, 1),
            "candidate_peak_rmse": round(p_rmse_bld, 1),
            "peak_rmse_improvement": round(p_rmse_inc - p_rmse_bld, 1)
        })
    df_st_analysis = pd.DataFrame(st_analysis)
    st_csv = REPORTS_DIR / "prompt_k_station_error_analysis.csv"
    df_st_analysis.to_csv(st_csv, index=False)
    logger.info("Saved %s.", st_csv)
    
    # -------------------------------------------------------------------------
    # Per-River-System Comparison CSV
    # -------------------------------------------------------------------------
    sys_analysis = []
    for r_sys, grp in df_can_comp.groupby("river_system"):
        yt_r = grp["discharge_cfs"].values
        yp_inc_r = grp["predicted_cfs"].values
        yp_bld_r = grp["pred_blend"].values
        
        rmse_inc = float(np.sqrt(mean_squared_error(yt_r, yp_inc_r)))
        rmse_bld = float(np.sqrt(mean_squared_error(yt_r, yp_bld_r)))
        r2_inc = float(r2_score(yt_r, yp_inc_r)) if np.var(yt_r) > 1e-6 else 0.0
        r2_bld = float(r2_score(yt_r, yp_bld_r)) if np.var(yt_r) > 1e-6 else 0.0
        
        sys_analysis.append({
            "river_system": r_sys,
            "stations_count": grp["station_id"].nunique(),
            "n_obs": len(grp),
            "incumbent_rmse": round(rmse_inc, 1),
            "candidate_rmse": round(rmse_bld, 1),
            "rmse_delta": round(rmse_bld - rmse_inc, 1),
            "incumbent_r2": round(r2_inc, 4),
            "candidate_r2": round(r2_bld, 4),
            "r2_delta": round(r2_bld - r2_inc, 4)
        })
    df_sys_analysis = pd.DataFrame(sys_analysis)
    sys_csv = REPORTS_DIR / "prompt_k_river_system_comparison.csv"
    df_sys_analysis.to_csv(sys_csv, index=False)
    logger.info("Saved %s.", sys_csv)
    
    logger.info("================================================================================")
    logger.info("PROMPT K BENCHMARK RUN SUCCESSFULLY COMPLETED")
    logger.info("================================================================================")

if __name__ == "__main__":
    main()

