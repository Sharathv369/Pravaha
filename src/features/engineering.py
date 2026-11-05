"""
Feature Engineering Module for PRAVAHA
Computes meteorological, antecedent, calendar, and catchment interaction features.
Strictly zero discharge features (No target leakage).
"""
from typing import List, Tuple
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    # Direct meteorological
    "precipitation_mm",
    "temp_max_c",
    "temp_min_c",
    "temp_mean_c",
    "temp_diurnal_range",
    "soil_moisture",
    
    # Rainfall rolling & antecedent
    "prcp_sum_1d",
    "prcp_sum_2d",
    "prcp_sum_3d",
    "prcp_sum_5d",
    "prcp_sum_7d",
    "prcp_sum_14d",
    "prcp_sum_30d",
    "prcp_sum_60d",
    "prcp_max_3d",
    "prcp_max_7d",
    "prcp_max_14d",
    "days_since_rain_5mm",
    "days_since_rain_10mm",
    "api_k85",
    "api_k90",
    
    # Temperature rolling & snowmelt proxies
    "temp_mean_3d",
    "temp_mean_7d",
    "temp_mean_14d",
    "temp_mean_30d",
    "degree_days_pos",
    "degree_days_7d",
    "snowmelt_proxy",
    
    # Soil moisture rolling & dynamics
    "sm_mean_3d",
    "sm_mean_7d",
    "sm_mean_14d",
    "sm_change_1d",
    "sm_change_3d",
    
    # Calendar & seasonality
    "doy_sin",
    "doy_cos",
    "month",
    
    # Static catchment attributes
    "drainage_area_sqmi",
    "log_drainage_area",
    "mean_elevation_ft",
    "log_mean_elevation",
    "slope_pct",
    "forest_cover_pct",
    
    # Catchment-meteorology interactions
    "rain_x_soil",
    "rain_7d_x_soil",
    "rain_per_log_da",
    "rain_7d_per_log_da",
    "slope_x_forest",
    "elevation_slope_ratio"
]

def compute_antecedent_precipitation_index(p: np.ndarray, k: float = 0.85) -> np.ndarray:
    """Calculates exponential decay Antecedent Precipitation Index (API)."""
    api = np.zeros(len(p), dtype=np.float32)
    current = 0.0
    for i in range(len(p)):
        val = p[i] if not np.isnan(p[i]) else 0.0
        current = current * k + val
        api[i] = current
    return api

def compute_days_since_rain(p: np.ndarray, threshold: float = 5.0) -> np.ndarray:
    """Calculates days since daily rainfall exceeded threshold."""
    days = np.zeros(len(p), dtype=np.float32)
    last_idx = -999.0
    for i in range(len(p)):
        val = p[i] if not np.isnan(p[i]) else 0.0
        if val >= threshold:
            last_idx = i
        days[i] = (i - last_idx) if last_idx >= 0 else 99.0
    return days

def engineer_features_station(df_s: pd.DataFrame) -> pd.DataFrame:
    """
    Computes all features for a single continuous station time series.
    """
    df = df_s.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # 1. Temperature derived
    df["temp_mean_c"] = (df["temp_max_c"] + df["temp_min_c"]) / 2.0
    df["temp_diurnal_range"] = df["temp_max_c"] - df["temp_min_c"]
    df["degree_days_pos"] = np.maximum(0.0, df["temp_mean_c"])
    
    # 2. Rainfall rolling sums and max
    p = df["precipitation_mm"].fillna(0.0)
    df["prcp_sum_1d"] = p.rolling(1, min_periods=1).sum()
    df["prcp_sum_2d"] = p.rolling(2, min_periods=1).sum()
    df["prcp_sum_3d"] = p.rolling(3, min_periods=1).sum()
    df["prcp_sum_5d"] = p.rolling(5, min_periods=1).sum()
    df["prcp_sum_7d"] = p.rolling(7, min_periods=1).sum()
    df["prcp_sum_14d"] = p.rolling(14, min_periods=1).sum()
    df["prcp_sum_30d"] = p.rolling(30, min_periods=1).sum()
    df["prcp_sum_60d"] = p.rolling(60, min_periods=1).sum()
    
    df["prcp_max_3d"] = p.rolling(3, min_periods=1).max()
    df["prcp_max_7d"] = p.rolling(7, min_periods=1).max()
    df["prcp_max_14d"] = p.rolling(14, min_periods=1).max()
    
    # Antecedent indices
    p_arr = p.values
    df["days_since_rain_5mm"] = compute_days_since_rain(p_arr, threshold=5.0)
    df["days_since_rain_10mm"] = compute_days_since_rain(p_arr, threshold=10.0)
    df["api_k85"] = compute_antecedent_precipitation_index(p_arr, k=0.85)
    df["api_k90"] = compute_antecedent_precipitation_index(p_arr, k=0.90)

    # 3. Temperature rolling & snowmelt
    t_mean = df["temp_mean_c"].ffill().bfill()
    df["temp_mean_3d"] = t_mean.rolling(3, min_periods=1).mean()
    df["temp_mean_7d"] = t_mean.rolling(7, min_periods=1).mean()
    df["temp_mean_14d"] = t_mean.rolling(14, min_periods=1).mean()
    df["temp_mean_30d"] = t_mean.rolling(30, min_periods=1).mean()
    
    dd_pos = df["degree_days_pos"].fillna(0.0)
    df["degree_days_7d"] = dd_pos.rolling(7, min_periods=1).sum()
    # Snowmelt proxy: positive degree days after below-freezing periods (elevation-weighted)
    df["snowmelt_proxy"] = df["degree_days_7d"] * (df["mean_elevation_ft"] / 1000.0)

    # 4. Soil moisture dynamics
    sm = df["soil_moisture"].ffill().bfill()
    df["sm_mean_3d"] = sm.rolling(3, min_periods=1).mean()
    df["sm_mean_7d"] = sm.rolling(7, min_periods=1).mean()
    df["sm_mean_14d"] = sm.rolling(14, min_periods=1).mean()
    df["sm_change_1d"] = sm.diff(1).fillna(0.0)
    df["sm_change_3d"] = sm.diff(3).fillna(0.0)

    # 5. Calendar
    doy = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2.0 * np.pi * doy / 365.25)
    df["doy_cos"] = np.cos(2.0 * np.pi * doy / 365.25)
    df["month"] = df["date"].dt.month

    # 6. Static catchment & interactions
    da = df["drainage_area_sqmi"].fillna(100.0)
    elev = df["mean_elevation_ft"].fillna(500.0)
    slope = df["slope_pct"].fillna(5.0)
    forest = df["forest_cover_pct"].fillna(30.0)
    
    df["log_drainage_area"] = np.log1p(da)
    df["log_mean_elevation"] = np.log1p(elev)
    
    df["rain_x_soil"] = df["precipitation_mm"] * sm
    df["rain_7d_x_soil"] = df["prcp_sum_7d"] * sm
    df["rain_per_log_da"] = df["precipitation_mm"] / (df["log_drainage_area"] + 1e-4)
    df["rain_7d_per_log_da"] = df["prcp_sum_7d"] / (df["log_drainage_area"] + 1e-4)
    df["slope_x_forest"] = slope * forest
    df["elevation_slope_ratio"] = elev / (slope + 1.0)

    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df

def generate_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies feature engineering across all stations independently to avoid cross-station leakage.
    """
    station_dfs = []
    for st_id, g in df.groupby("station_id"):
        df_feats = engineer_features_station(g)
        station_dfs.append(df_feats)
        
    df_out = pd.concat(station_dfs, ignore_index=True)
    df_out = df_out.sort_values(["station_id", "date"]).reset_index(drop=True)
    return df_out

