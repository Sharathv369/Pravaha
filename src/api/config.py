"""Configuration settings and path resolution for the PRAVAHA API."""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Core Artifact Paths
TRAIN_LABELLED_CSV = PROCESSED_DATA_DIR / "PRAVAHA_TRAIN_LABELLED.csv"
VERIFIED_STATION_CATALOG_CSV = REPORTS_DIR / "verified_station_catalog.csv"
RIVER_SYSTEM_GROUPING_CSV = REPORTS_DIR / "river_system_grouping.csv"
CATCHMENT_PROVENANCE_CSV = REPORTS_DIR / "catchment_provenance.csv"
LORSO_PREDICTIONS_PARQUET = PROCESSED_DATA_DIR / "prompt_e_validation_predictions.parquet"
LORSO_VALIDATION_RESULTS_CSV = REPORTS_DIR / "lors_validation_results.csv"
LORSO_PER_STATION_METRICS_CSV = REPORTS_DIR / "lors_per_station_metrics.csv"
LORSO_PER_RIVER_SYSTEM_METRICS_CSV = REPORTS_DIR / "lors_per_river_system_metrics.csv"

# API Metadata
API_TITLE = "PRAVAHA API"
API_VERSION = "1.0.0"
API_DESCRIPTION = (
    "PRAVAHA Hydrologic Intelligence Platform API — FLOODCAST 24-Hour Hackathon. "
    "Serves verified USGS streamgauging stations, historical daily mean discharge records, "
    "and out-of-system Leave-One-River-System-Out (LORSO) validation benchmark predictions."
)

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Supported LORSO Models Mapping
MODEL_ALIASES = {
    "log_spec_q": "LightGBM Log-Specific Discharge",
    "lightgbm log-specific discharge": "LightGBM Log-Specific Discharge",
    "spec_q": "LightGBM Specific Discharge",
    "lightgbm specific discharge": "LightGBM Specific Discharge",
    "raw": "LightGBM Raw Unweighted",
    "lightgbm raw unweighted": "LightGBM Raw Unweighted",
    "peak_weighted": "LightGBM Raw Peak-Weighted (2.5x)",
    "lightgbm raw peak-weighted (2.5x)": "LightGBM Raw Peak-Weighted (2.5x)",
    "log1p": "XGBoost Log1p",
    "xgboost log1p": "XGBoost Log1p",
}

DEFAULT_MODEL_NAME = "LightGBM Log-Specific Discharge"
DEFAULT_TARGET_FORMULATION = "log_spec_q"

# US FIPS Code to 2-Letter State Mapping
FIPS_TO_STATE = {
    4: "AZ",
    5: "AR",
    6: "CA",
    8: "CO",
    12: "FL",
    16: "ID",
    17: "IL",
    18: "IN",
    19: "IA",
    20: "KS",
    24: "MD",
    27: "MN",
    28: "MS",
    29: "MO",
    31: "NE",
    35: "NM",
    36: "NY",
    37: "NC",
    41: "OR",
    42: "PA",
    45: "SC",
    46: "SD",
    48: "TX",
    49: "UT",
    53: "WA",
    54: "WV",
    55: "WI",
}
