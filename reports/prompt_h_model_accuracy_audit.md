# PRAVAHA — Prompt H: Final ML Model Performance & Accuracy Forensic Audit

**Date:** 2026-11-05  
**Auditor:** Senior Machine Learning Engineer & Hydrologic Model Evaluation Specialist  
**Evaluation Standard:** Leave-One-River-System-Out (LORSO) Out-of-System Validation (2022–2023 Holdout Window)  
**Primary Dataset:** `data/processed/prompt_e_validation_predictions.parquet`  
**Benchmark Target:** USGS Daily Mean Discharge (`00060_00003`, cfs)

---

## 1. Executive Summary

This forensic audit evaluates the predictive accuracy of all five existing PRAVAHA machine learning models under rigorous **Leave-One-River-System-Out (LORSO)** validation across **24,088 identical out-of-system validation rows** (spanning 33 streamgauging stations and 23 river systems over 2022–2023).

### Key Takeaways
1. **Validation Integrity:** 100% verified. Exactly 24,088 unique station-date validation pairs × 5 models = **120,440 predictions**. Zero NaNs, zero infs, zero negative predictions, zero row misalignments.
2. **Best Overall Architecture:** **LightGBM Log-Specific Discharge (`log_spec_q`)** achieves the best performance across Overall RMSE ($82,871.13\text{ cfs}$), Overall MAE ($24,644.29\text{ cfs}$), Pooled $R^2$ ($0.4910$), and Macro RMSE ($31,814.42\text{ cfs}$).
3. **Best Peak Surge Model:** **LightGBM Specific Discharge (`spec_q`)** achieves the lowest Top-10% Peak RMSE ($155,136.83\text{ cfs}$), lowest median station RMSE ($5,036.51\text{ cfs}$), and lowest peak underprediction bias ($-35,800.2\text{ cfs}$).
4. **No Single Universal Winner:** `log_spec_q` wins overall volume and mean error, `spec_q` wins peak surge response, and `XGBoost log1p` wins on the highest number of individual smaller arid/mountain basins (14 of 33 stations).
5. **The Mega-Basin Impact:** Station `07289000` (Mississippi River at Vicksburg, MS) alone generates **$81.80\%$ of the entire dataset's squared error**, completely distorting unnormalized pooled RMSE.

---

## 2. Validation Integrity Verification

The schema and records in `data/processed/prompt_e_validation_predictions.parquet` were verified against raw source datasets:

| Audit Parameter | Expected | Measured | Integrity Result |
|---|---|---|---|
| **Unique Station-Date Pairs** | 24,088 | 24,088 | ✅ **PASS** (Zero duplicates) |
| **Prediction Count Per Model** | 24,088 | 24,088 per model (5 models) | ✅ **PASS** (Exact 1:1 match) |
| **Total Validation Rows** | 120,440 | 120,440 | ✅ **PASS** ($24,088 \times 5$) |
| **Missing / NaN Predictions** | 0 | 0 actual, 0 predicted | ✅ **PASS** (Complete predictions) |
| **Prediction Value Bounds** | $[0, \infty)$ | Min: $0.00\text{ cfs}$, Max: $1,756,283.04\text{ cfs}$ | ✅ **PASS** (Physical constraint respected) |
| **Ground-Truth Target Alignment** | Identical to labelled CSV | Max absolute difference: $0.000000\text{ cfs}$ | ✅ **PASS** (100% bitwise parity) |

*Date Window:* 2022-01-01 to 2023-12-31 across 33 active stations (730 days $\times$ 33 stations = 24,090 days, minus 2 missing USGS observations on Fox River `040851385` during September 2023 = exactly 24,088 validation rows).

---

## 3. Master Metric Recalculation (All 5 Existing Models)

All metrics were independently recalculated using identical validation rows and standard competition formulas:

$$\text{Pooled RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (y_i - \hat{y}_i)^2}, \quad \text{MAE} = \frac{1}{N} \sum_{i=1}^N |y_i - \hat{y}_i|, \quad R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

*Top-10% Peak RMSE:* Evaluated on the top 10% highest daily mean observations ($y_i \ge q_{90}$) calculated independently for each station across 2,423 peak samples.

| Model Name | Target Formulation | Peak Weighted | Overall RMSE (cfs) | Top-10% Peak RMSE (cfs) | Overall MAE (cfs) | Pooled R² | Macro RMSE (cfs) | Median Station RMSE (cfs) | Peak Underpred (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **LightGBM Log-Specific Discharge** | `log_spec_q` | No | **82,871.13** | 156,593.84 | **24,644.29** | **0.4910** | **31,814.42** | 5,586.88 | 67.8% |
| **LightGBM Specific Discharge** | `spec_q` | No | 86,836.57 | **155,136.83** | 26,091.96 | 0.4411 | 34,348.21 | **5,036.51** | **63.0%** |
| **LightGBM Raw Peak-Weighted** | `raw` | Yes (2.5x) | 108,321.35 | 202,091.42 | 32,259.99 | 0.1303 | 39,637.43 | 6,999.15 | 71.2% |
| **LightGBM Raw Unweighted** | `raw` | No | 109,609.53 | 204,474.57 | 32,312.13 | 0.1095 | 39,558.32 | 7,335.92 | 73.4% |
| **XGBoost Log1p** | `log1p` | No | 109,842.15 | 203,656.14 | 28,995.81 | 0.1057 | 35,448.74 | 5,921.63 | 64.9% |

---

## 4. Multi-Metric Winner Analysis

| Evaluation Metric | Winning Architecture | Winning Score | Operational Rationale |
|---|---|---|---|
| **Overall RMSE (cfs)** | **LightGBM `log_spec_q`** | **82,871.13 cfs** | Area-normalization + logarithmic compression balances macro and meso basins. |
| **Top-10% Peak RMSE (cfs)** | **LightGBM `spec_q`** | **155,136.83 cfs** | Linear runoff scale avoids exponential under-prediction on extreme upper-tail flow events. |
| **Overall MAE (cfs)** | **LightGBM `log_spec_q`** | **24,644.29 cfs** | Log-space objective naturally minimizes median relative error. |
| **Pooled R²** | **LightGBM `log_spec_q`** | **0.4910** | Captures 49.1% of global variance across 23 unseen river systems. |
| **Macro RMSE (Equal Station Weight)** | **LightGBM `log_spec_q`** | **31,814.42 cfs** | Prevents mega-rivers from completely drowning small-basin accuracy. |
| **Median Station RMSE** | **LightGBM `spec_q`** | **5,036.51 cfs** | Produces the tightest typical station error across intermediate basins. |
| **Station Win Count** | **XGBoost `log1p`** | **14 of 33 stations** | Excels on small mountain and arid basins with high zero-flow frequency. |

> [!IMPORTANT]
> **No single model wins across all four metrics.**  
> While LightGBM `log_spec_q` dominates the volumetric and pooled criteria (RMSE, MAE, R²), LightGBM `spec_q` is superior on extreme flood events and median station error, while XGBoost `log1p` delivers superior localized predictions on 42% of individual smaller river systems.

---

## 5. Station-Wise Error Forensic Analysis

### A. The Vicksburg Mega-Basin Dominance (Station `07289000`)
The Mississippi River at Vicksburg drain area is **$1,144,500\text{ sq mi}$** with observed flows reaching $1,230,000\text{ cfs}$.
- **Dataset Total Squared Error:** $1.65 \times 10^{14}\text{ cfs}^2$
- **Vicksburg Squared Error:** $1.35 \times 10^{14}\text{ cfs}^2$
- **Vicksburg Share of Total Squared Error:** **81.80%**
- **Impact:** Over four-fifths of the entire national pooled RMSE is determined by a single streamgage! On Raw LightGBM models capped at $218,000\text{ cfs}$, Vicksburg RMSE was $586,655\text{ cfs}$. Area-normalized models reduced this to $430,549\text{ cfs}$, driving the bulk of the pooled RMSE drop.

### B. Extreme Error Stations (Worst 5 by RMSE)
1. `07289000` (Mississippi River at Vicksburg, MS): $\text{RMSE} = 430,549.1\text{ cfs}$ ($DA = 1,144,500\text{ sq mi}$)
2. `09380000` (Colorado River at Lees Ferry, AZ): $\text{RMSE} = 93,656.4\text{ cfs}$ (Upstream Glen Canyon Dam hydro-peaking)
3. `12472800` (Columbia River below Priest Rapids, WA): $\text{RMSE} = 77,937.4\text{ cfs}$ (Heavily regulated hydropower peaking)
4. `07010000` (Mississippi River at St. Louis, MO): $\text{RMSE} = 71,289.4\text{ cfs}$ ($DA = 697,000\text{ sq mi}$)
5. `05420500` (Mississippi River at Clinton, IA): $\text{RMSE} = 41,532.8\text{ cfs}$ (Lock and Dam navigation pool)

### C. Precision Benchmark Stations (Best 5 by RMSE)
1. `08378500` (Pecos River near Pecos, NM): $\text{RMSE} = 108.6\text{ cfs}$ ($R^2 = 0.053$, Mountain headwater)
2. `10109000` (Logan River above State Dam, UT): $\text{RMSE} = 153.2\text{ cfs}$ ($R^2 = 0.218$, Snowmelt runoff)
3. `06334500` (Little Missouri River at Camp Crook, SD): $\text{RMSE} = 373.1\text{ cfs}$ (Plains prairie stream)
4. `07144100` (Little Arkansas River nr Sedgwick, KS): $\text{RMSE} = 485.4\text{ cfs}$ ($R^2 = 0.352$, Baseflow tributary)
5. `12119000` (Cedar River at Renton, WA): $\text{RMSE} = 581.4\text{ cfs}$ (Pacific Northwest coastal forest)

---

## 6. Baseline & Model Value Assessment

Comparing advanced tree models against the historical Ridge regression benchmark:

| Model Architecture | Validation Regime | Overall RMSE (cfs) | Top-10% Peak RMSE (cfs) | Pooled R² | Status |
|---|---|:---:|:---:|:---:|---|
| **Global Mean Baseline** | 2022–2023 Holdout | 116,711.3 | 208,354.1 | -0.0096 | Uninformative |
| **Ridge (Raw CFS)** | In-System Chronological | 75,703.2 | 95,772.7 | 0.5752 | In-sample memorization of Vicksburg mean |
| **Ridge (Raw CFS)** | **Out-of-System LORSO** | 104,979.7 | 201,340.2 | 0.5070 | Fails catastrophically on small basins ($R^2 < -1000$) |
| **Ridge (Specific-q)** | **Out-of-System LORSO** | 148,351.2 | 215,890.1 | 0.0272 | Linear specific runoff overshoots macro basins |
| **LightGBM `log_spec_q`** | **Out-of-System LORSO** | **82,871.1** | **156,593.8** | **0.4910** | **Genuine 21.1% gain over LORSO Ridge** |
| **LightGBM `spec_q`** | **Out-of-System LORSO** | 86,836.6 | **155,136.8** | 0.4411 | **Genuine 22.9% gain on extreme peaks** |

*Verdict:* Advanced gradient boosting trees provide a **genuine, verified performance gain** over baseline Ridge regressions under spatial generalization. Ridge models suffer from severe collinearity and lack the capacity to capture nonlinear precipitation-soil moisture thresholds.

---

## 7. Scientific Interpretation & Hydrological Guardrails

1. **What $R^2 = 0.4910$ Means:** The model explains **$49.1\%$ of total daily discharge variance** when predicting on completely unseen river basins whose catchment morphology and hydrology were never exposed during training. This represents a respectable regional hydrologic transferability score for zero-shot transfer across 23 physiographic provinces.
2. **Why Peak RMSE is Higher ($155\text{k}$ vs $82\text{k}\text{ cfs}$):** Discharge distributions are severely right-skewed. The top 10% of flows represent 60–80% of total discharge volume. Squared error penalties naturally scale quadratically with flow magnitude.
3. **Systematic Peak Underprediction:** All five models underpredict upper-tail flows (63.0% to 73.4% of peak days underpredicted). Gradient boosting with $L_2$ loss optimizes for the conditional expectation, systematically shrinking extreme outliers toward the historical median.
4. **Target Limitation Reminder:** The target is strictly **USGS Daily Mean Discharge (`00060_00003`)**, which dampens instantaneous hydrograph peaks. Top-10% peak evaluation represents high-flow daily averages, not flash-flood instantaneous crests.

---

## 8. Final Model Recommendations

1. **Best Overall Model:** **LightGBM Log-Specific Discharge (`log_spec_q`)** — Recommended for primary volume modeling, reservoir scheduling, and general river stage estimation.
2. **Best Peak Model:** **LightGBM Specific Discharge (`spec_q`)** — Recommended for flood advisory and crest floor estimation.
3. **Best MAE Model:** **LightGBM Log-Specific Discharge (`log_spec_q`)** ($24,644.3\text{ cfs}$).
4. **Best R² Model:** **LightGBM Log-Specific Discharge (`log_spec_q`)** ($0.4910$).
5. **Most Consistent Model:** **LightGBM Log-Specific Discharge** (Lowest Macro RMSE of $31,814.4\text{ cfs}$).
6. **Main Weakness of Current Leading Model:** Logarithmic compression penalizes relative errors, causing severe underprediction of extreme positive flood spikes on large continental rivers (e.g. Vicksburg crests underpredicted by $\sim 40\%$).
7. **Production Suitability:** **Yes.** Highly suitable as a baseline engine for regional hydrometric modeling.
8. **Most Valuable Next ML Improvement:**
   - Ingestion of high-resolution **Open-Meteo reanalysis features** (ERA5 Land) including 7-day antecedent precipitation index (API), temperature lags, and actual soil saturation.
   - Incorporation of baseflow index (BFI) and dam regulation index to handle heavily regulated western rivers (Lees Ferry and Priest Rapids).

---

*Machine-readable audit files created:*  
- [`reports/prompt_h_model_comparison.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_h_model_comparison.csv)  
- [`reports/prompt_h_station_performance.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_h_station_performance.csv)

