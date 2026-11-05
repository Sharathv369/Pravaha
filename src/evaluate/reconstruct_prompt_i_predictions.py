"""Reconstruct fold-level validation predictions for Prompt I optimized champion.

Model: LightGBM log_spec_q (Optimized: +14d Rain + 2.5x Peak Weighting)
Folds: 23-fold Leave-One-River-System-Out (LORSO)
Validation Period: 2022-01-01 to 2023-12-31 (33 stations, 24,088 rows)
"""
import sys
import time
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import lightgbm as lgb

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.features.engineering import FEATURE_COLUMNS, generate_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("reconstruct_prompt_i")

DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

TRAIN_END_DATE = "2021-12-31"
VAL_START_DATE = "2022-01-01"
VAL_END_DATE = "2023-12-31"

# Feature set C (14-day antecedent memory)
FEATURE_SET_A_BASE = [
    "precipitation_mm", "temp_max_c", "temp_min_c", "temp_mean_c", "temp_diurnal_range", "soil_moisture",
    "doy_sin", "doy_cos", "month",
    "drainage_area_sqmi", "log_drainage_area", "mean_elevation_ft", "log_mean_elevation", "slope_pct", "forest_cover_pct",
    "rain_x_soil", "rain_per_log_da", "slope_x_forest", "elevation_slope_ratio"
]

FEATURE_SET_B_3D_7D = FEATURE_SET_A_BASE + [
    "prcp_sum_3d", "prcp_sum_7d", "prcp_max_3d", "prcp_max_7d", "rain_7d_x_soil", "rain_7d_per_log_da"
]

FEATURE_SET_C_14D = FEATURE_SET_B_3D_7D + [
    "prcp_sum_14d", "prcp_max_14d"
]

def compute_training_peak_weights(df_train: pd.DataFrame, peak_mult: float = 2.5) -> np.ndarray:
    """Computes sample weights derived strictly from training-fold data only."""
    weights = np.ones(len(df_train), dtype=np.float32)
    for sid, grp in df_train.groupby("station_id"):
        q90 = grp["discharge_cfs"].quantile(0.90)
        idx_in_train = grp.index[grp["discharge_cfs"] >= q90]
        pos_indices = df_train.index.get_indexer(idx_in_train)
        weights[pos_indices] = peak_mult
    return weights

def run_reconstruction():
    logger.info("Loading labelled data from %s...", DATA_DIR / "PRAVAHA_TRAIN_LABELLED.csv")
    df_raw = pd.read_csv(DATA_DIR / "PRAVAHA_TRAIN_LABELLED.csv", dtype={"station_id": str})
    df_raw["station_id"] = df_raw["station_id"].str.zfill(8)
    logger.info("Loaded %d rows across %d stations.", len(df_raw), df_raw["station_id"].nunique())
    
    logger.info("Generating features...")
    t0 = time.time()
    df_features = generate_features(df_raw)
    df_features["date"] = pd.to_datetime(df_features["date"])
    df_features["station_id"] = df_features["station_id"].astype(str).str.zfill(8)
    logger.info("Features generated in %.2fs. Shape: %s", time.time() - t0, df_features.shape)
    
    df_groups = pd.read_csv(REPORTS_DIR / "river_system_grouping.csv", dtype={"station_id": str})
    df_groups["station_id"] = df_groups["station_id"].str.zfill(8)
    station_to_system = dict(zip(df_groups["station_id"], df_groups["river_system"]))
    station_to_name = dict(zip(df_groups["station_id"], df_groups["station_name"]))
    
    df_features["river_system"] = df_features["station_id"].map(station_to_system)
    df_features["station_name"] = df_features["station_id"].map(station_to_name)
    
    river_systems = df_groups["river_system"].unique().tolist()
    logger.info("Total river systems for LORSO: %d", len(river_systems))
    
    fold_preds = []
    t_start = time.time()
    
    for fold_idx, held_out in enumerate(river_systems, 1):
        train_mask = (~df_features["river_system"].isin([held_out])) & (df_features["date"] <= TRAIN_END_DATE)
        val_mask = (df_features["river_system"] == held_out) & (df_features["date"] >= VAL_START_DATE) & (df_features["date"] <= VAL_END_DATE)
        
        df_train = df_features[train_mask].copy()
        df_val = df_features[val_mask].copy()
        
        if len(df_val) == 0:
            logger.warning("Fold %d (%s) has 0 val rows. Skipping.", fold_idx, held_out)
            continue
            
        # Specific discharge requires valid drainage area
        tr_da_mask = df_train["drainage_area_sqmi"].notna() & (df_train["drainage_area_sqmi"] > 0)
        df_train_da = df_train[tr_da_mask].copy()
        da_tr = df_train_da["drainage_area_sqmi"].values
        da_val = df_val["drainage_area_sqmi"].values
        
        y_train_raw = df_train_da["discharge_cfs"].values
        y_train_spec_q = y_train_raw / da_tr
        y_train_log_spec_q = np.log1p(np.maximum(0.0, y_train_spec_q))
        
        weights_2_5 = compute_training_peak_weights(df_train_da, peak_mult=2.5)
        
        X_tr = df_train_da[FEATURE_SET_C_14D].fillna(0.0).values
        X_va = df_val[FEATURE_SET_C_14D].fillna(0.0).values
        
        model = lgb.LGBMRegressor(
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
        
        model.fit(X_tr, y_train_log_spec_q, sample_weight=weights_2_5)
        pred_logq = model.predict(X_va)
        pred_q = np.clip(np.expm1(pred_logq), a_min=0.0, a_max=None)
        pred_cfs = pred_q * da_val
        
        fold_res = df_val[["station_id", "station_name", "date", "discharge_cfs", "river_system", "drainage_area_sqmi"]].copy()
        fold_res["fold_id"] = fold_idx
        fold_res["predicted_cfs"] = pred_cfs
        fold_preds.append(fold_res)
        logger.info("Fold %02d/%d: %s | Train: %d rows | Val: %d rows", fold_idx, len(river_systems), held_out, len(df_train), len(df_val))
        
    all_val = pd.concat(fold_preds, ignore_index=True)
    all_val.rename(columns={"discharge_cfs": "actual_cfs"}, inplace=True)
    out_parquet = DATA_DIR / "prompt_i_champion_predictions.parquet"
    all_val.to_parquet(out_parquet, index=False)
    logger.info("Reconstructed fold predictions saved to %s in %.2fs. Total rows: %d", out_parquet, time.time() - t_start, len(all_val))
    return all_val

if __name__ == "__main__":
    run_reconstruction()

