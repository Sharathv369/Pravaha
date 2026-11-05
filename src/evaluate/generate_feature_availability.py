"""Script to generate prompt_j3_feature_availability.csv."""
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

features_data = [
    {
        "feature_name": "precipitation_mm",
        "feature_group": "Direct Meteorology",
        "data_source": "NASA POWER (MERRA-2 / GEOS-5 FP-IT)",
        "observation_window": "Calendar Day t (00:00 - 23:59 UTC)",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "Published with 1-3 day reanalysis lag",
        "target_leakage_risk": "NONE (Physical driving variable, no discharge used)",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "temp_max_c",
        "feature_group": "Direct Meteorology",
        "data_source": "NASA POWER (MERRA-2)",
        "observation_window": "Calendar Day t (Daily Maximum)",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "Published with 1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "temp_min_c",
        "feature_group": "Direct Meteorology",
        "data_source": "NASA POWER (MERRA-2)",
        "observation_window": "Calendar Day t (Daily Minimum)",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "Published with 1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "temp_mean_c",
        "feature_group": "Direct Meteorology",
        "data_source": "Derived: (temp_max_c + temp_min_c) / 2",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "Published with 1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "temp_diurnal_range",
        "feature_group": "Direct Meteorology",
        "data_source": "Derived: temp_max_c - temp_min_c",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "Published with 1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "soil_moisture",
        "feature_group": "Direct Meteorology",
        "data_source": "NASA POWER (0-100cm Root Zone)",
        "observation_window": "Calendar Day t Mean",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "Published with 1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "doy_sin",
        "feature_group": "Calendar & Seasonality",
        "data_source": "Astronomical Calendar: sin(2*pi*DOY/365.25)",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Deterministic Time Function",
        "uses_current_day_t": "YES (Deterministic calendar)",
        "available_at_t_minus_1_issue_time": "YES (Known infinitely in advance)",
        "latency_availability": "Zero latency (Mathematical formula)",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "doy_cos",
        "feature_group": "Calendar & Seasonality",
        "data_source": "Astronomical Calendar: cos(2*pi*DOY/365.25)",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Deterministic Time Function",
        "uses_current_day_t": "YES (Deterministic calendar)",
        "available_at_t_minus_1_issue_time": "YES (Known infinitely in advance)",
        "latency_availability": "Zero latency (Mathematical formula)",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "month",
        "feature_group": "Calendar & Seasonality",
        "data_source": "Calendar Month (1 - 12)",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Deterministic Time Function",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "YES (Known infinitely in advance)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "drainage_area_sqmi",
        "feature_group": "Catchment Static",
        "data_source": "USGS NWIS / GAGES-II",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES (Static metadata)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "log_drainage_area",
        "feature_group": "Catchment Static",
        "data_source": "Derived: log1p(drainage_area_sqmi)",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES (Static metadata)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "mean_elevation_ft",
        "feature_group": "Catchment Static",
        "data_source": "GAGES-II / StreamStats DEM",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES (Static metadata)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "log_mean_elevation",
        "feature_group": "Catchment Static",
        "data_source": "Derived: log1p(mean_elevation_ft)",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES (Static metadata)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "slope_pct",
        "feature_group": "Catchment Static",
        "data_source": "GAGES-II / StreamStats DEM",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES (Static metadata)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "forest_cover_pct",
        "feature_group": "Catchment Static",
        "data_source": "GAGES-II / NLCD Land Cover",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES (Static metadata)",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "rain_x_soil",
        "feature_group": "Physical Interaction",
        "data_source": "Derived: precipitation_mm * soil_moisture",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "rain_per_log_da",
        "feature_group": "Physical Interaction",
        "data_source": "Derived: precipitation_mm / log_drainage_area",
        "observation_window": "Calendar Day t",
        "temporal_alignment": "Same-Day Concurrent",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "slope_x_forest",
        "feature_group": "Physical Interaction",
        "data_source": "Derived: slope_pct * forest_cover_pct",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "elevation_slope_ratio",
        "feature_group": "Physical Interaction",
        "data_source": "Derived: mean_elevation_ft / (slope_pct + 1.0)",
        "observation_window": "Static Basin Physiography",
        "temporal_alignment": "Time-Invariant Static",
        "uses_current_day_t": "NO",
        "available_at_t_minus_1_issue_time": "YES",
        "latency_availability": "Zero latency",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Directly Usable for Forecasting"
    },
    {
        "feature_name": "prcp_sum_3d",
        "feature_group": "Trailing Rainfall Memory",
        "data_source": "Derived: rolling 3-day sum (p_t + p_{t-1} + p_{t-2})",
        "observation_window": "Days t-2 through t (Right-aligned)",
        "temporal_alignment": "Trailing Window (Includes Day t)",
        "uses_current_day_t": "YES (Includes Day t)",
        "available_at_t_minus_1_issue_time": "NO (Requires Day t rainfall)",
        "latency_availability": "1-3 day reanalysis lag for Day t component",
        "target_leakage_risk": "NONE (Strictly right-aligned, no future peeking)",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "prcp_sum_7d",
        "feature_group": "Trailing Rainfall Memory",
        "data_source": "Derived: rolling 7-day sum (p_t + ... + p_{t-6})",
        "observation_window": "Days t-6 through t (Right-aligned)",
        "temporal_alignment": "Trailing Window (Includes Day t)",
        "uses_current_day_t": "YES (Includes Day t)",
        "available_at_t_minus_1_issue_time": "NO (Requires Day t rainfall)",
        "latency_availability": "1-3 day reanalysis lag for Day t component",
        "target_leakage_risk": "NONE (Strictly right-aligned, no future peeking)",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "prcp_sum_14d",
        "feature_group": "Trailing Rainfall Memory",
        "data_source": "Derived: rolling 14-day sum (p_t + ... + p_{t-13})",
        "observation_window": "Days t-13 through t (Right-aligned)",
        "temporal_alignment": "Trailing Window (Includes Day t)",
        "uses_current_day_t": "YES (Includes Day t)",
        "available_at_t_minus_1_issue_time": "NO (Requires Day t rainfall)",
        "latency_availability": "1-3 day reanalysis lag for Day t component",
        "target_leakage_risk": "NONE (Strictly right-aligned, no future peeking)",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "prcp_max_3d",
        "feature_group": "Trailing Rainfall Memory",
        "data_source": "Derived: rolling 3-day max of precipitation",
        "observation_window": "Days t-2 through t (Right-aligned)",
        "temporal_alignment": "Trailing Window (Includes Day t)",
        "uses_current_day_t": "YES (Includes Day t)",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "prcp_max_7d",
        "feature_group": "Trailing Rainfall Memory",
        "data_source": "Derived: rolling 7-day max of precipitation",
        "observation_window": "Days t-6 through t (Right-aligned)",
        "temporal_alignment": "Trailing Window (Includes Day t)",
        "uses_current_day_t": "YES (Includes Day t)",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "prcp_max_14d",
        "feature_group": "Trailing Rainfall Memory",
        "data_source": "Derived: rolling 14-day max of precipitation",
        "observation_window": "Days t-13 through t (Right-aligned)",
        "temporal_alignment": "Trailing Window (Includes Day t)",
        "uses_current_day_t": "YES (Includes Day t)",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "rain_7d_x_soil",
        "feature_group": "Physical Interaction",
        "data_source": "Derived: prcp_sum_7d * soil_moisture",
        "observation_window": "Days t-6 through t",
        "temporal_alignment": "Trailing Interaction (Includes Day t)",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    },
    {
        "feature_name": "rain_7d_per_log_da",
        "feature_group": "Physical Interaction",
        "data_source": "Derived: prcp_sum_7d / log_drainage_area",
        "observation_window": "Days t-6 through t",
        "temporal_alignment": "Trailing Interaction (Includes Day t)",
        "uses_current_day_t": "YES",
        "available_at_t_minus_1_issue_time": "NO",
        "latency_availability": "1-3 day reanalysis lag",
        "target_leakage_risk": "NONE",
        "operational_readiness_class": "Nowcasting / Retrospective Simulation Only"
    }
]

df = pd.DataFrame(features_data)
out_csv = REPORTS_DIR / "prompt_j3_feature_availability.csv"
df.to_csv(out_csv, index=False)
print(f"Saved {out_csv} with {len(df)} features.")

