# PRAVAHA — Prompt J3: Forecast Readiness & Final System Integrity Audit

**Audit Standard**: Senior Machine Learning Evaluation & Hydrologic Operational Audit  
**Audit Date**: 2026-11-05  
**Evaluation Scope**: Feature point-in-time availability, prediction provenance, backend integrity, and prototype capability  
**Target Architecture**: LightGBM Specific Discharge (`log_spec_q`) with 14-day rainfall memory and 2.5x peak weighting  

---

## 1. Executive Summary & Verification Findings

This audit establishes the boundary between **retrospective hydrologic simulation / same-day nowcasting** and **genuine operational flood forecasting**, while verifying the integrity of the PRAVAHA system after disk cleanup.

| Audit Item | Core Question | Finding | Evidence & Status |
| :--- | :--- | :---: | :--- |
| **1. Prompt I Raw Predictions** | Do per-observation predictions exist on disk? | **PASS** | Reconstructed fold-level predictions saved to [`data/processed/prompt_i_champion_predictions.parquet`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/data/processed/prompt_i_champion_predictions.parquet) (24,088 rows). |
| **2. Metric Reproducibility** | Are 73,793.15 RMSE and 128,552.56 Peak RMSE reproducible from raw data? | **PASS** | Recalculated directly from out-of-fold parquet predictions with 0.00% variance. |
| **3. Target Leakage** | Is there any target or future data leakage? | **PASS** | Zero discharge leakage. All rolling windows are strictly right-aligned on trailing past dates. |
| **4. Feature Point-in-Time Availability** | Are input features available at forecast issue time ($t-1$)? | **FAIL** | Model requires same-day precipitation ($p_t$) and same-day temperatures ($T_t$), which are unobserved at $t-1$. |
| **5. Operational Horizon** | Does the model support genuine next-day forecasting? | **FAIL** | Model functions as a **same-day nowcaster / retrospective simulator**, not a $+24\text{h}$ operational forecaster. |
| **6. Backend Health Post-Cleanup** | Are all dependencies and services functional? | **PASS** | All 8 data files intact, 25/25 unit tests pass, all 15 API routes return 200/400/404. |
| **7. Displayed Prototype Model** | Which model does the UI display? | **PASS** | Dashboard displays **Prompt E baseline** (`LightGBM Log-Specific Discharge`), accurately labeled as historical LORSO validation. |

---

## 2. Prompt I Evidence & Reproducibility Audit

### 1. Per-Observation Validation Predictions
- **Finding**: **PASS**
- **Evidence**: The raw out-of-fold validation predictions exist in [`data/processed/prompt_i_champion_predictions.parquet`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/data/processed/prompt_i_champion_predictions.parquet) (302 KB, 24,088 rows across 33 stations for 2022–2023).
- **Exact Provenance**:
  - In Prompt J2, initial comparisons referenced [`reports/prompt_i_model_metrics.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_i_model_metrics.csv) and [`reports/prompt_i_station_performance.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_i_station_performance.csv).
  - To eliminate reliance on aggregate CSVs, the exact 23-fold LORSO training pipeline was re-executed via [`src/evaluate/reconstruct_prompt_i_predictions.py`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/src/evaluate/reconstruct_prompt_i_predictions.py) in 23.70 seconds.
  - Raw prediction columns: `station_id`, `station_name`, `date`, `actual_cfs`, `river_system`, `drainage_area_sqmi`, `fold_id`, `predicted_cfs`.

### 2. Independent Metric Recalculation from Raw Predictions
- **Finding**: **PASS**
- Calculating metrics directly from `prompt_i_champion_predictions.parquet`:
  - **Overall RMSE**: **$73,793.15\text{ cfs}$** (Exact match)
  - **Top-10% Peak RMSE**: **$128,552.56\text{ cfs}$** (Exact match)
  - **Overall MAE**: **$22,887.18\text{ cfs}$** (Exact match)
  - **Pooled $R^2$**: **$0.5964$** (Exact match)
  - **Peak Underprediction Rate**: **$68.8\%$** (Exact match)
  - **Peak Mean Prediction Bias**: **$-32,349.15\text{ cfs}$** (Exact match)

The reported performance gains are authentic and derived strictly from observation-level data.

---

## 3. Critical Point-in-Time Feature Audit

A forensic examination of all 27 features in `FEATURE_SET_C_14D` was conducted to determine point-in-time feasibility. Full feature-by-feature parameters are archived in [`reports/prompt_j3_feature_availability.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_j3_feature_availability.csv).

### Summary Breakdown by Temporal Class:

| Feature Category | Count | Features Included | Uses Current Day $t$? | Available at Forecast Issue Time ($t-1$)? | Operational Role |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Static Basin Physiography** | 7 | `drainage_area_sqmi`, `log_drainage_area`, `mean_elevation_ft`, `log_mean_elevation`, `slope_pct`, `forest_cover_pct`, `slope_x_forest`, `elevation_slope_ratio` | **NO** | **YES** | Time-invariant catchment constants. Fully forecasting-ready. |
| **Calendar Harmonics** | 3 | `doy_sin`, `doy_cos`, `month` | **NO** (Deterministic) | **YES** | Known infinitely in advance. Fully forecasting-ready. |
| **Same-Day Direct Meteorology**| 6 | `precipitation_mm`, `temp_max_c`, `temp_min_c`, `temp_mean_c`, `temp_diurnal_range`, `soil_moisture` | **YES** | **NO** | Observed over full 24h of day $t$. Unobserved at $t-1$. |
| **Trailing Multi-Day Rain Sums**| 6 | `prcp_sum_3d`, `prcp_sum_7d`, `prcp_sum_14d`, `prcp_max_3d`, `prcp_max_7d`, `prcp_max_14d` | **YES** | **NO** | Right-aligned trailing windows include day $t$ rainfall. |
| **Physical Interaction Terms** | 4 | `rain_x_soil`, `rain_per_log_da`, `rain_7d_x_soil`, `rain_7d_per_log_da` | **YES** | **NO** | Compound terms incorporating day $t$ precipitation. |

### Technical Analysis of Timing & Latency:

1. **Same-Day Precipitation ($p_t$)**:
   - `precipitation_mm` represents the total accumulated rainfall from 00:00 to 23:59 UTC on calendar day $t$.
   - In real-world reanalysis products (NASA POWER MERRA-2), the observation for day $t$ is published with a **1 to 3 day latency**.
   - Even with real-time radar (NEXRAD MRMS), the full 24-hour accumulation for day $t$ is only known after day $t$ concludes (at 23:59 UTC).
   - Therefore, at 06:00 on day $t$ (or 18:00 on day $t-1$, when next-day flood advisories are issued), $p_t$ is **physically unknown**.
2. **Rolling Window Alignment**:
   - In [`src/features/engineering.py`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/src/features/engineering.py#L110-122):
     ```python
     df["prcp_sum_3d"] = p.rolling(3, min_periods=1).sum()
     df["prcp_sum_7d"] = p.rolling(7, min_periods=1).sum()
     df["prcp_sum_14d"] = p.rolling(14, min_periods=1).sum()
     ```
   - In pandas, default `rolling()` on sorted dates is right-aligned. Day $t$ computes $p_t + p_{t-1} + p_{t-2}$.
   - **No Target Leakage**: The window never peeks into $t+1$ or future dates.
   - **Point-in-Time Constraint**: Because it includes $p_t$, it cannot be evaluated before day $t$ completes.
3. **Soil Moisture & Temperatures**:
   - `soil_moisture`, `temp_max_c`, and `temp_min_c` represent daily integrated variables over day $t$, requiring retrospective assimilation.

---

## 4. Distinct Operational Classifications

To ensure complete scientific integrity, PRAVAHA models must be clearly categorized across three operational regimes:

```
+--------------------------------------------------------------------------------------------------+
|                                  OPERATIONAL REGIME TAXONOMY                                    |
+--------------------------------------------------------------------------------------------------+
| A. Same-Day Discharge Nowcasting / Retrospective Simulation  | CURRENT PRAVAHA CAPABILITY        |
|    - Target: Q_t (Mean discharge on day t)                   | - Uses observed p_t, T_t, SM_t    |
|    - Inputs: Observed weather on day t                       | - Status: VERIFIED & OPERATIONAL  |
|    - Use Cases: Rapid damage assessment, post-flood forensics| - R² = 0.5964, RMSE = 73,793 cfs  |
+--------------------------------------------------------------------------------------------------+
| B. Next-Day Flood Forecasting (Lead Time: +24h)              | REQUIRES METEOROLOGICAL FORECAST  |
|    - Target: Q_{t+1} (Mean discharge tomorrow)               | - Must replace p_{t+1} with NWP   |
|    - Inputs: Trailing weather (<= t) + NWP Forecast (t+1)    | - NOAA HRRR / GFS precipitation   |
|    - Use Cases: Evacuation planning, early flood warnings    | - Status: PLANNED ARCHITECTURE    |
+--------------------------------------------------------------------------------------------------+
| C. Multi-Day Flood Forecasting (Lead Time: 48h to 7 days)    | REQUIRES ENSEMBLE METEOROLOGY     |
|    - Target: Q_{t+2} ... Q_{t+7}                             | - ECMWF / GEFS ensemble forecasts |
|    - Inputs: Trailing soil memory + 7-day weather ensembles  | - Status: ADVANCED EXPANSION      |
+--------------------------------------------------------------------------------------------------+
```

> [!WARNING]
> **Strict Operational Rule**:  
> In all pitch slides, documentation, and hackathon communications, PRAVAHA must **never** be described as an operational "future flood forecasting" model without the explicit caveat that it currently operates in **same-day nowcasting / retrospective simulation mode**. To achieve genuine $+24\text{h}$ forecasting, the day $t$ features must be supplied by 24-hour Numerical Weather Prediction (NWP) precipitation forecasts.

---

## 5. Prototype Capability Audit

We audited what data and models are currently displayed by the active prototype UI (`http://localhost:5173`):

### 1. Active Model in Dashboard
- **Finding**: **PASS**
- **Inspected Configuration**:
  - `src/api/config.py#L16`: `LORSO_PREDICTIONS_PARQUET = PROCESSED_DATA_DIR / "prompt_e_validation_predictions.parquet"`
  - `src/api/config.py#L52`: `DEFAULT_MODEL_NAME = "LightGBM Log-Specific Discharge"`
  - `frontend/src/pages/DashboardPage.tsx#L118`: `useHydrograph(..., 'log_spec_q')`
- **Result**: The dashboard actively renders the **Prompt E baseline** model (`LightGBM Log-Specific Discharge`), which achieved:
  - Pooled $R^2 = 0.4910$ (49.10% variance explained)
  - Overall RMSE = $82,871.13\text{ cfs}$
  - Peak RMSE = $156,593.84\text{ cfs}$

### 2. Labeling & Provenance Disclaimers
- **Finding**: **PASS**
- **API Hydrograph Disclaimer** ([`src/api/schemas.py#L119-122`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/src/api/schemas.py#L119-L122)):
  > *"Historical USGS daily mean discharge (00060_00003). Model predictions represent historical 2022–2023 out-of-system Leave-One-River-System-Out (LORSO) validation holdouts, NOT live or future operational forecasts."*
- **UI Catchment Profile Card** ([`frontend/src/pages/DashboardPage.tsx#L927`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/frontend/src/pages/DashboardPage.tsx#L927)):
  > *"Documented Model Limitation Profile (LORSO Evidence)"*
- **UI KPI Badge** ([`frontend/src/pages/DashboardPage.tsx#L467`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/frontend/src/pages/DashboardPage.tsx#L467)):
  > *"Historical LORSO Validation"*
- **Result**: The prototype does **not** misrepresent its predictions. It clearly labels them as historical out-of-system validation holdouts and does not claim live real-time telemetry.

---

## 6. Comprehensive Findings Matrix

| Audit Check | Component | Status | Detailed Explanation |
| :--- | :--- | :---: | :--- |
| **Observation Predictions** | `data/processed/prompt_i_champion_predictions.parquet` | **PASS** | 24,088 row-level predictions present on disk. |
| **Metric Exactness** | RMSE 73,793.15 / Peak 128,552.56 | **PASS** | Recalculated from raw data with 0.00% discrepancy. |
| **Target Leakage** | Feature Engineering Pipeline | **PASS** | Zero discharge leakage; right-aligned rolling windows. |
| **Forecast Availability** | Point-in-Time Weather Cutoff | **FAIL** | Requires same-day weather ($p_t$); not available at $t-1$. |
| **Operational Horizon** | Next-Day Forecasting ($t+1$) | **FAIL** | Operates as same-day nowcaster; forecasting requires NWP. |
| **Backend Data Dependencies** | 8 Canonical Files | **PASS** | All 8 required files present, non-empty, and verified. |
| **Unit Test Suite** | 25 Tests in `test_api.py` | **PASS** | 25 ran, 25 passed, 0 failures, 0 errors (0.266s). |
| **API Endpoints** | 15 Live Route Queries | **PASS** | 100% correct HTTP 200, 400, 404 responses. |
| **Frontend Production Build** | Vite Bundler / TypeScript | **PASS** | 1,589 modules transformed in 5.96s with 0 errors. |
| **UI Model Transparency** | Dashboard Hydrograph & Metrics | **PASS** | Accurately renders Prompt E baseline with honest disclaimers. |

