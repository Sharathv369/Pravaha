"""
Model Training and Tuning Module for PRAVAHA
Trains LightGBM and XGBoost models with:
- Peak-weighted regression to prevent flood peak under-prediction
- Raw vs log-target comparison
- Quantile regressors (p10, p50, p90) for uncertainty bands
- Saving trained models to artifacts/
"""
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb
import xgboost as xgb

from src.features.engineering import FEATURE_COLUMNS
from src.evaluate.metrics import compute_competition_metrics

logger = logging.getLogger(__name__)

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def compute_peak_sample_weights(df: pd.DataFrame, target_col: str = "discharge_cfs", weight_multiplier: float = 3.0) -> np.ndarray:
    """
    Computes sample weights prioritizing top-10% flood peak days.
    Addresses severe RMSE penalty on extreme discharge days.
    """
    weights = np.ones(len(df), dtype=np.float32)
    for _, group in df.groupby("station_id"):
        q90 = group[target_col].quantile(0.90)
        idx = group.index
        is_peak = group[target_col] >= q90
        # Quadratic emphasis above P90
        weights[idx] = np.where(is_peak, 1.0 + weight_multiplier * (group[target_col] / (q90 + 1e-3)), 1.0)
    return weights

class PravahaEnsemble:
    """
    Ensemble model combining LightGBM Peak-Weighted Regressor,
    XGBoost Regressor, and Quantile Regressors for uncertainty bands.
    """
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.lgb_raw = None
        self.lgb_log = None
        self.xgb_model = None
        self.lgb_q10 = None
        self.lgb_q90 = None
        self.feature_names = FEATURE_COLUMNS
        self.station_stats = {}

    def fit(self, df_train: pd.DataFrame, target_col: str = "discharge_cfs"):
        valid_df = df_train[df_train[target_col].notna()].copy()
        X = valid_df[self.feature_names].fillna(0.0)
        y = valid_df[target_col].values
        y_log = np.log1p(y)
        
        # Calculate per-station risk thresholds and statistics
        for st_id, g in valid_df.groupby("station_id"):
            q_vals = g[target_col].values
            self.station_stats[st_id] = {
                "p25": float(np.percentile(q_vals, 25)),
                "p50": float(np.percentile(q_vals, 50)),
                "p75": float(np.percentile(q_vals, 75)),
                "p90": float(np.percentile(q_vals, 90)),
                "p98": float(np.percentile(q_vals, 98)),
                "max": float(np.max(q_vals)),
                "mean": float(np.mean(q_vals))
            }

        weights = compute_peak_sample_weights(valid_df, target_col=target_col)

        # 1. LightGBM Peak-Weighted Regressor (Raw target)
        logger.info("Training LightGBM Peak-Weighted Regressor...")
        self.lgb_raw = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.04,
            num_leaves=45,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.lgb_raw.fit(X, y, sample_weight=weights)

        # 2. LightGBM Log-Target Regressor
        logger.info("Training LightGBM Log-Target Regressor...")
        self.lgb_log = lgb.LGBMRegressor(
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.lgb_log.fit(X, y_log)

        # 3. XGBoost Regressor
        logger.info("Training XGBoost Regressor...")
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=250,
            learning_rate=0.04,
            max_depth=6,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.xgb_model.fit(X, y, sample_weight=weights)

        # 4. Quantile Regressors (p10 and p90 for confidence intervals)
        logger.info("Training LightGBM Quantile Regressors (p10, p90)...")
        self.lgb_q10 = lgb.LGBMRegressor(
            objective="quantile",
            alpha=0.10,
            n_estimators=150,
            learning_rate=0.05,
            num_leaves=31,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.lgb_q10.fit(X, y)

        self.lgb_q90 = lgb.LGBMRegressor(
            objective="quantile",
            alpha=0.90,
            n_estimators=150,
            learning_rate=0.05,
            num_leaves=31,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.lgb_q90.fit(X, y, sample_weight=weights)

        return self

    def predict(self, df_test: pd.DataFrame) -> np.ndarray:
        """
        Returns blended prediction in raw CFS. Enforces non-negative values.
        """
        X = df_test[self.feature_names].fillna(0.0)
        
        pred_raw = self.lgb_raw.predict(X)
        pred_log = np.expm1(self.lgb_log.predict(X))
        pred_xgb = self.xgb_model.predict(X)
        
        # 60% Raw Peak-Weighted LGBM + 25% XGBoost + 15% Log-LGBM
        # Balances overall MSE and top 10% peak surge capture
        blend = 0.60 * pred_raw + 0.25 * pred_xgb + 0.15 * pred_log
        return np.clip(blend, a_min=0.0, a_max=None)

    def predict_with_quantiles(self, df_test: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Returns point prediction plus p10 and p90 uncertainty bands.
        """
        point_pred = self.predict(df_test)
        X = df_test[self.feature_names].fillna(0.0)
        
        q10 = np.clip(self.lgb_q10.predict(X), a_min=0.0, a_max=None)
        q90 = np.clip(self.lgb_q90.predict(X), a_min=0.0, a_max=None)
        
        # Guarantee monotonicity: q10 <= point_pred <= q90
        q10 = np.minimum(q10, point_pred)
        q90 = np.maximum(q90, point_pred)
        
        return {
            "prediction": point_pred,
            "q10": q10,
            "q90": q90
        }

    def save(self, filepath: Path = ARTIFACTS_DIR / "pravaha_ensemble.joblib"):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        logger.info(f"Saved PRAVAHA model bundle to {filepath}")

    @classmethod
    def load(cls, filepath: Path = ARTIFACTS_DIR / "pravaha_ensemble.joblib") -> "PravahaEnsemble":
        return joblib.load(filepath)

