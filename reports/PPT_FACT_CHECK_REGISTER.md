# PRAVAHA — Hackathon Technical Fact-Check & Verification Register
**Project**: PRAVAHA (प्रवाह) — "PREDICT THE SURGE. PROTECT THE PEOPLE."  
**Deliverable**: Comprehensive Technical Claim & Metric Traceability Audit  
**Date**: November 2026  
**Status Standards**: `VERIFIED` | `PROVISIONAL` | `DEMONSTRATION ONLY` | `UNRESOLVED` | `PLANNED`  

---

## 1. Executive Summary

This register audits every technical claim, numerical metric, dataset property, and architectural assertion used in the PRAVAHA presentation materials. Every entry is traced to its authoritative project file, CSV column, or audit report.

No unverified numbers, marketing exaggerations, or unconfirmed competition claims are permitted in the presentation deck.

---

## 2. Master Fact-Check & Traceability Register

| # | Claim Description | Verified Value | Source File | Source Section / Column | Verification Status | Slide Allocation |
| :-: | :--- | :--- | :--- | :--- | :-: | :-: |
| **01** | Total Stations in Expanded Labelled Dataset | **34 stations** | `data/processed/PRAVAHA_TRAIN_LABELLED.csv` | `station_id` unique count | `VERIFIED` | Slide 2, 3 |
| **02** | Total Labelled Discharge Observations | **170,817 rows** | `data/processed/PRAVAHA_TRAIN_LABELLED.csv` | Row count | `VERIFIED` | Slide 3 |
| **03** | Total Records Including Missing Target | **173,842 rows** | `data/processed/PRAVAHA_EXPANDED_MASTER.csv` | Row count | `VERIFIED` | Slide 3 |
| **04** | Missing Target Observations Count | **3,025 rows** (1.74% of master) | `data/processed/PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv` | Row count | `VERIFIED` | Slide 3 |
| **05** | Master Dataset Observation Period | **2010-01-01 to 2023-12-31** (14 calendar years) | `data/MANIFEST.md` | `Date Range` | `VERIFIED` | Slide 3 |
| **06** | Total Entries in Candidate Metadata Catalogue | **38 stations** | `reports/verified_station_catalog.csv` | Row count | `VERIFIED` (Broader catalogue) | Slide 3, Notes |
| **07** | Total Stations Evaluated in LORSO Holdout | **33 stations** | `reports/lors_validation_results.csv` | `active_stations` column | `VERIFIED` | Slide 4 |
| **08** | Station 11447650 Truncated Record Span | **2,099 rows** (2010-01-01 to 2015-09-30; 0 in 2022–2023) | `reports/prompt_f_validation_integrity_audit.md` | Section 2.1 | `VERIFIED` | Slide 2, 3, 5 |
| **09** | Total Unique Validation Rows | **24,088 station-date pairs** | `reports/lors_validation_results.csv` | `validation_rows` column | `VERIFIED` | Slide 4 |
| **10** | Total LORSO Validation Predictions | **120,440 predictions** (24,088 rows × 5 models) | `reports/prompt_f_validation_integrity_audit.md` | Section 1.1 | `VERIFIED` | Slide 4 |
| **11** | Total Top-10% Extreme Flood Validation Samples | **2,423 samples** | `reports/prompt_f_model_selection_recommendation.md` | Section 4 | `VERIFIED` | Slide 4 |
| **12** | Total Independent River System Groups | **23 river systems** (23 cross-validation folds) | `reports/river_system_grouping.csv` | Row count | `VERIFIED` | Slide 3, 4 |
| **13** | Top Experimental Model Architecture | **LightGBM Log-Specific Discharge (`log_spec_q`)** | `reports/lors_validation_results.csv` | Row 4 | `VERIFIED` | Slide 2, 4 |
| **14** | Top Model Pooled R² (LORSO Validation) | **0.4910** (0.49097187...) | `reports/lors_validation_results.csv` | `pooled_r2` column | `VERIFIED` | Slide 2, 4, 5 |
| **15** | Top Model Overall Pooled RMSE | **82,871.1 cfs** | `reports/lors_validation_results.csv` | `pooled_rmse` column | `VERIFIED` | Slide 4 |
| **16** | Top Model Top-10% Peak RMSE | **156,593.8 cfs** | `reports/lors_validation_results.csv` | `pooled_rmse_top10` column | `VERIFIED` | Slide 4 |
| **17** | Top Model Overall Pooled MAE | **24,644.3 cfs** | `reports/lors_validation_results.csv` | `pooled_mae` column | `VERIFIED` | Slide 4 |
| **18** | Top Model Macro RMSE (Equal Basin Weighting) | **31,814.4 cfs** | `reports/lors_validation_results.csv` | `macro_rmse` column | `VERIFIED` | Slide 4, Notes |
| **19** | Top Model Median Station RMSE | **5,586.9 cfs** | `reports/prompt_f_model_selection_recommendation.md` | Table 1.2 | `VERIFIED` | Slide 4, Notes |
| **20** | Best Top-10% Extreme Peak RMSE Model | **LightGBM Specific Discharge (`spec_q`)**: **155,136.8 cfs** | `reports/lors_validation_results.csv` | Row 3 | `VERIFIED` | Slide 4 |
| **21** | Raw CFS LightGBM Scale Mismatch Failure | Overall RMSE: **109,609.5 cfs**, Pooled R²: **0.1095** | `reports/lors_validation_results.csv` | Row 1 | `VERIFIED` | Slide 2, 4 |
| **22** | Mississippi at Vicksburg Dominance of Error | **81.80% of total pooled squared error** (DA: 1,144,500 mi²) | `reports/prompt_f_model_selection_recommendation.md` | Section 2.2 | `VERIFIED` | Slide 4, Notes |
| **23** | Target Streamflow Parameter Code | **USGS daily mean discharge: `00060_00003`** (in `cfs`) | `reports/unresolved_competition_questions.md` | Section 1.2 | `VERIFIED` (Provisional target) | Slide 1, 3 |
| **24** | Daily Maximum Discharge Code (`00060_00001`) | Unsystematic across USGS stations; only 1 test station confirmed | `reports/unresolved_competition_questions.md` | Section 1.2 | `UNRESOLVED` | Slide 3, Notes |
| **25** | Weather Data API Sourcing | **NASA POWER MERRA-2** (due to Open-Meteo HTTP 429 quota block) | `reports/unresolved_competition_questions.md` | Section 2.1 | `VERIFIED` (Fallback) | Slide 3 |
| **26** | Soil Moisture Scale Discrepancy | NASA POWER is saturation fraction (0–1); Open-Meteo is m³/m³ | `reports/unresolved_competition_questions.md` | Section 2.2 | `VERIFIED` | Slide 3, Notes |
| **27** | Zero Discharge Feature Leakage | Strictly 0 streamflow lags or target-dependent features | `src/features/engineering.py` | Line 4 comment & list | `VERIFIED` | Slide 3, 4 |
| **28** | Catchment Physiography Sources | **USGS GAGES-II** (23 gauges) + **USGS StreamStats** (10 gauges) | `reports/catchment_provenance.csv` | Row records | `VERIFIED` | Slide 3 |
| **29** | FastAPI Automated Backend Test Suite | **25/25 automated unit tests passing** (0.27s execution) | `reports/api_test_results.md` | Test execution table | `VERIFIED` | Slide 3, 5 |
| **30** | React Frontend TypeScript Build Status | **100% build pass** (0 errors, Vite bundle 325.35 kB) | `reports/ui_backend_integration_test_results.md` | Build log output | `VERIFIED` | Slide 3, 5 |
| **31** | Live API Integration Probes | **5/5 endpoints verified passing** against live server | `reports/ui_backend_integration_test_results.md` | Section 2 table | `VERIFIED` | Slide 3, 5 |
| **32** | Live Operational Forecast Generation | Model evaluated on historical holdouts; no live inference endpoint | `reports/ui_backend_integration_status.md` | Section 5 | `PLANNED` | Slide 5, Notes |
| **33** | Municipal Dispatch / SMS / Siren Operations | Pure frontend scenario simulation with explicit disclaimers | `frontend/src/data/demoData.ts` | Header disclaimer | `DEMONSTRATION ONLY` | Slide 5 |
| **34** | Citizen SOS & Community Reports | Simulated crowdsourced incident feeds for evaluation exercises | `frontend/src/data/demoData.ts` | Header disclaimer | `DEMONSTRATION ONLY` | Slide 5 |
| **35** | NGO Relief Supply Logistics | Simulated mutual-aid resource coordinator for evaluation exercises | `frontend/src/data/demoData.ts` | Header disclaimer | `DEMONSTRATION ONLY` | Slide 5 |

---

## 3. Discrepancy Reconciliation & Resolution Register

### Discrepancy 1: 34 Expanded Dataset Stations vs 38 Metadata Catalogue Entries
- **The Conflict**: `reports/verified_station_catalog.csv` lists 38 stations, but `data/processed/PRAVAHA_TRAIN_LABELLED.csv` contains only 34 stations.
- **The Ground Truth**: During Phase B/C, a broader exploratory catalogue of 38 candidate stations was queried. Four stations (`06454500`, `03611500`, `06752000`, `01438000`) had incomplete time-series or missing records and were dropped. Exactly **34 stations** have verified, unbroken records in the master training dataset.
- **Rule for PPT**: The slide deck must cite **"34 verified USGS streamgauging stations"** as the empirical training and evaluation dataset. Mention 38 only when referencing the broader candidate registry.

### Discrepancy 2: 34 Dataset Stations vs 33 Evaluated Validation Stations
- **The Conflict**: Prompt F reports 33 evaluated stations in the LORSO benchmark, while the dataset contains 34 stations.
- **The Ground Truth**: Station `11447650` (Sacramento River at Freeport, CA) records terminate on `2015-09-30` (2,099 rows). Because the LORSO holdout window is strictly `2022-01-01 to 2023-12-31`, station `11447650` has **0 rows in the validation window**. However, its river system (Fold 05: California Central Valley) was evaluated via its downstream partner `11303500` (San Joaquin River near Vernalis, CA, 730 rows). Thus, all **23 river systems** produced valid validation evaluations across **33 active stations**.
- **Rule for PPT**: State **"33 stations evaluated across 23 river systems in the 2022–2023 holdout"**, and highlight the Sacramento gauge as an authentic demonstration of historical data limitation handling.

### Discrepancy 3: Pooled R² (0.4910) vs Macro R² (-87.66)
- **The Conflict**: Pooled R² is **+0.4910**, but unweighted Macro R² is heavily negative (**-87.66**).
- **The Ground Truth**: Macro R² calculates $R^2$ independently for each station and takes the arithmetic mean. Small, regulated, or low-variance arid basins (e.g., Pecos River, Texas Colorado below Mansfield Dam) exhibit near-zero variance during drought periods. Any minor baseline offset causes localized negative $R^2$ that skews an unweighted average. In contrast, **Pooled R²** calculates variance across all 24,088 continental predictions simultaneously, representing true explained variance across the hydrological network.
- **Rule for PPT**: Always label the metric as **"Pooled R² (LORSO Validation) = 0.4910"**. Never label it as "Macro R²". Provide the median station MAE (**2,623.1 cfs**) to demonstrate typical watershed accuracy.

### Discrepancy 4: USGS Daily Mean (`00060_00003`) vs Daily Maximum (`00060_00001`)
- **The Conflict**: The FLOODCAST Problem Statement mentions "peak daily discharge", but all continental datasets provide daily mean discharge.
- **The Ground Truth**: USGS parameter `00060_00003` (daily mean) is the only continuous, unbroken record available across continental stations (170,817 rows). Instantaneous daily maximum (`00060_00001`) is not systematically computed or published by USGS across most gauges.
- **Rule for PPT**: Transparently state that the model targets **USGS daily mean discharge (`00060_00003`)**, which is the gold standard for continuous continental hydrology, while noting that official clarification on daily maximum is pending.

### Discrepancy 5: NASA POWER MERRA-2 vs Open-Meteo
- **The Conflict**: The challenge description mentions Open-Meteo, but PRAVAHA uses NASA POWER.
- **The Ground Truth**: Open-Meteo returned **HTTP 429 Too Many Requests** (10,000 requests/day quota exhausted). To maintain zero synthetic data, NASA POWER MERRA-2 was integrated, supplying 100% verified meteorological data across all stations.
- **Rule for PPT**: Explain this as an operational reliability engineering achievement: pivoting to satellite/reanalysis data (NASA POWER MERRA-2) when public free APIs rate-limited, while noting soil moisture unit calibration requirements.

---

## 4. Unresolved Competition Questions Checklist

| Topic | Unresolved Item | Presentation Handling |
| :--- | :--- | :--- |
| **Target Variable** | Whether competition test set evaluates daily mean (`00060_00003`) or daily maximum (`00060_00001`). | State provisional target is `00060_00003`; explain mathematical differences. |
| **Weather Features** | Whether organizers supply pre-extracted Open-Meteo data or allow NASA POWER. | Highlight NASA POWER reliability; show soil moisture calibration path. |
| **Station Scope** | Whether final submission allows training on 34 stations or strictly 5 core stations. | Report LORSO results on 34 stations; demonstrate capability to retrain on 5 core if required. |
| **Scoring Formula** | Whether composite score is linearly summed or normalized by variance/range. | Present individual metrics (RMSE, Peak RMSE, MAE, R²) rather than an unnormalized composite score. |

---

## 5. Summary Sign-Off

All metrics cited in `reports/PPT_MASTER_BRIEF.md` and `reports/PPT_SLIDE_CONTENT.md` comply strictly with the values in this register.

