# PRAVAHA — API Data Provenance & Lineage Report
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt API-1 Data Provenance Document  
**Date**: November 2026  
**Auditor**: Lead Hydrological Data Engineer & ML Scientist  
**Scope**: All source datasets, Parquet files, CSV artifacts, and schemas powering the PRAVAHA API  

---

## 1. Authoritative Data Artifacts Directory

The PRAVAHA backend is strictly connected to authentic, immutable local datasets generated during previous verification phases. No synthetic records, artificial interpolations, or unverified external sources are utilized.

| Artifact Path | Format | Size | Total Rows | Canonical Purpose in API |
| :--- | :---: | :---: | :---: | :--- |
| `data/processed/PRAVAHA_TRAIN_LABELLED.csv` | CSV | 11.85 MB | 170,817 | Historical continuous daily discharge observations (2010–2023) across 34 stations; powers `/api/stations/{id}/hydrograph`. |
| `reports/verified_station_catalog.csv` | CSV | 9.13 KB | 38 | Master station registry with geographic coordinates, state FIPS, and NWIS verification tiers; powers `/api/stations`. |
| `reports/river_system_grouping.csv` | CSV | 9.88 KB | 34 | Independent river-system basin assignments and connectivity audit notes; powers `/api/validation/river-systems`. |
| `reports/catchment_provenance.csv` | CSV | 41.39 KB | 152 | GAGES-II and StreamStats audit records for area, elevation, slope, and forest canopy; powers `/api/stations/{id}/catchment-profile`. |
| `data/processed/prompt_e_validation_predictions.parquet` | Parquet | 1.27 MB | 120,440 | Held-out LORSO validation predictions across 5 models for 2022–2023 (24,088 rows per model); powers hydrograph dual-curves. |
| `reports/lors_validation_results.csv` | CSV | 1.16 KB | 5 | Official benchmark leaderboard metrics (Pooled $R^2$, RMSE, MAE); powers `/api/validation/leaderboard`. |
| `reports/lors_per_station_metrics.csv` | CSV | 32.06 KB | 165 | Station-level cross-validation error metrics; informs model limitation profiling. |
| `reports/lors_per_river_system_metrics.csv` | CSV | 15.68 KB | 115 | River-system level cross-validation error metrics; powers `/api/validation/river-systems`. |

---

## 2. Target Variable & Meteorological Provenance

### 2.1 Target Variable Definition
- **Parameter**: `00060_00003` (USGS NWIS Daily Mean Discharge).
- **Physical Unit**: **`cfs` (cubic feet per second)**.
- **Conversion Policy**: Never converted to cubic meters per second ($m^3/s$) or arbitrary non-standard units.
- **Target Imputation**: **0 rows imputed**. All 170,817 rows represent genuine, recorded USGS observations. 3,025 missing target rows were strictly isolated in `PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv` and never used for training or validation.

### 2.2 Meteorological Input Features
- **Reanalysis Source**: **NASA POWER MERRA-2**.
- **Variables Utilized**:
  - `precipitation_mm`: Total precipitation corrected (`PRECTOTCORR`, mm/day).
  - `temp_max_c`: Maximum daily 2-meter air temperature (`T2M_MAX`, °C).
  - `temp_min_c`: Minimum daily 2-meter air temperature (`T2M_MIN`, °C).
  - `soil_moisture`: Surface soil wetness fraction (`GWETTOP`, dimensionless 0–1).
- **Temporal Consistency**: 100% complete daily meteorological records from 2010-01-01 through 2023-12-31 without gaps across all 34 active stations.

---

## 3. Station Catalogue & Basin Mapping Lineage

### 3.1 Candidate Breakdown
- **Total Candidate Stations**: **38** (documented in `reports/verified_station_catalog.csv`).
- **Benchmark-Ready Stations**: **21** (100% verified USGS NWIS discharge + 100% verified GAGES-II catchment physiography).
- **StreamStats Dependent Stations**: **13** (100% verified USGS NWIS discharge; macro-basins exceeding GAGES-II coverage where elevation, slope, and forest cover are unverified).
- **Rejected Stations**: **4** (`01438000`, `03611500`, `06454500`, `06752000` were excluded due to missing daily mean series or truncated historical records ending prior to 2016).

### 3.2 Station ID Integrity
Every station ID is stored and transmitted as a string with leading zeros preserved (e.g. `01646500`, `02087500`, `07010000`, `08158000`, `11447650`). Pydantic models strictly enforce string typing to prevent numerical truncation.

---

## 4. LORSO Benchmark Prediction Provenance

### 4.1 Methodology
The validation dataset (`prompt_e_validation_predictions.parquet`) represents **Leave-One-River-System-Out (LORSO)** 23-fold spatial cross-validation evaluated over the 2-year holdout window (2022-01-01 to 2023-12-31):
- **Models Evaluated**: 5 distinct mathematical formulations:
  1. `LightGBM Raw Unweighted` (`raw`)
  2. `LightGBM Raw Peak-Weighted (2.5x)` (`raw`)
  3. `LightGBM Specific Discharge` (`spec_q`)
  4. `LightGBM Log-Specific Discharge` (`log_spec_q`)
  5. `XGBoost Log1p` (`log1p`)
- **Holdout Rows**: $24,088\text{ rows} \times 5\text{ models} = 120,440\text{ total predictions}$.
- **Zero In-Sample Leakage**: When predicting a station, all stations belonging to that station's river system were strictly excluded from model training, preprocessing scalers, and hyperparameter selection.

### 4.2 Handling of Station 11447650 (Sacramento River at Freeport)
Station `11447650` historical discharge observations in the labeled training dataset ended on `2015-09-30` (2,099 observations). Consequently, this station has **0 validation rows** in the 2022–2023 holdout period.
- In `GET /api/stations/11447650/hydrograph`, observations are returned through 2015-09-30, and `predicted_discharge_cfs` returns `null`.
- In `GET /api/stations/11447650/catchment-profile`, the model limitation indicator explicitly informs callers that the station possesses zero modern validation samples.
- In `GET /api/validation/river-systems`, the `California Central Valley System` reports 2 assigned stations, but 730 evaluated samples (contributed exclusively by station `11303500`).

---

## 5. Verification Against Synthetic Data Fabrication

1. **No Mock Fallbacks in Services**: All services raise explicit HTTP 503 errors if an underlying dataset file is absent, rather than silently substituting random numbers or mock templates.
2. **Deterministic Parity**: Values served by the API match the underlying CSV and Parquet files bit-for-bit, verified by automated assertion tests comparing API payloads against raw file reads.
3. **No Fake Telemetry**: The API never manufactures simulated real-time streamflow or claims live sensor connectivity.

