# PRAVAHA — Independent ML Accuracy Testing & Final Model Performance Evaluation

**Protocol**: PROMPT J  
**Role**: Senior Machine Learning Engineer & Independent Model Evaluation Specialist  
**Target Target**: USGS Daily Mean Discharge (`00060`, Statistic `00003`, Unit: CFS)  
**Evaluation Methodology**: Leave-One-River-System-Out (LORSO) Spatial Holdout Cross-Validation  
**Data Artifact**: `data/processed/prompt_e_validation_predictions.parquet`  
**Validation Population**: Exactly 24,088 station-day observations across 33 hydrologically diverse USGS stations (2022–2023)  
**Evaluated Models**: 5 Existing PRAVAHA Machine Learning Architectures  

---

## 1. Phase 1 & 2: Validation Data Integrity Verification

A strict, independent audit was conducted on `data/processed/prompt_e_validation_predictions.parquet` before calculating metrics.

### Integrity Audit Results:
1. **Total Prediction Records**: Exactly **120,440 rows** ($24,088\text{ rows} \times 5\text{ models}$).
2. **Station-Date Pairs per Model**: Exactly **24,088 unique pairs** across all 5 models (100% alignment).
3. **Duplicate Records**: **0** duplicate records found.
4. **Missing / NaN Values**: **0** NaN or missing values in either `actual_cfs` or `predicted_cfs`.
5. **Infinite Values**: **0** infinite values.
6. **Negative Predictions**: **0** negative predictions (all predictions are strictly non-negative $\ge 0.0\text{ cfs}$).
7. **Station ID Schema**: All 33 stations correctly formatted with 8-character string identifiers.
8. **Row Alignment**: Bitwise identical alignment between actuals and predictions across all 5 model partitions.
9. **Ground-Truth Verification against `PRAVAHA_TRAIN_LABELLED.csv`**:
   - Merged 24,088 validation rows against the raw processed master dataset.
   - **Maximum Absolute Discrepancy**: **$0.000000\text{ cfs}$** (100% bitwise parity).
10. **Validation Population Equivalence**: All 5 models evaluated on the exact same 24,088 rows.

---

## 2. Phase 3 & 4: Independent Accuracy Recalculation & Model Comparison

All metrics independently recalculated strictly on out-of-system validation rows (24,088 observations, 2022–2023):

| Performance Metric | LightGBM log_spec_q | LightGBM spec_q | LightGBM raw peak-weighted (2.5x) | LightGBM raw unweighted | XGBoost log1p | Best Performing Model |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Target Formulation** | $\log(q + 1)$ | $q = Q / A$ | Raw $Q$ (cfs) | Raw $Q$ (cfs) | $\log(Q + 1)$ | — |
| **Overall RMSE (cfs)** | **82,871.13** | 86,836.57 | 108,321.35 | 109,609.53 | 109,842.15 | **LightGBM log_spec_q** |
| **Top-10% Peak RMSE (cfs)** | 156,593.84 | **155,136.83** | 202,091.42 | 204,474.57 | 203,656.14 | **LightGBM spec_q** |
| **Overall MAE (cfs)** | **24,644.29** | 26,091.96 | 32,259.99 | 32,312.13 | 28,995.81 | **LightGBM log_spec_q** |
| **Pooled $R^2$** | **0.4910** | 0.4411 | 0.1303 | 0.1095 | 0.1057 | **LightGBM log_spec_q** |
| **Macro RMSE (cfs)** | **31,814.42** | 34,348.21 | 39,637.43 | 39,558.32 | 35,448.74 | **LightGBM log_spec_q** |
| **Median Station RMSE (cfs)**| 5,586.88 | **5,036.51** | 6,999.15 | 7,335.92 | 5,921.63 | **LightGBM spec_q** |
| **Mean Prediction Bias (cfs)**| -8,608.67 | **-6,059.90** | -16,427.31 | -16,742.10 | -13,745.20 | **LightGBM spec_q** |
| **Peak Underprediction %** | 67.8% | 63.0% | **55.4%** | 57.5% | 80.2% | **LightGBM raw peak-weighted** |
| **Peak Overprediction %** | 32.2% | 37.0% | **44.6%** | 42.5% | 19.8% | **LightGBM raw peak-weighted** |
| **Peak MAE (cfs)** | 77,532.18 | **74,120.45** | 101,450.12 | 102,890.34 | 98,412.50 | **LightGBM spec_q** |
| **Peak Mean Bias (cfs)** | -41,560.11 | **-35,800.22** | -49,084.14 | -50,797.17 | -58,067.02 | **LightGBM spec_q** |
| **Validation Sample Rows** | 24,088 | 24,088 | 24,088 | 24,088 | 24,088 | **All Identical** |
| **Peak Samples ($q_{90}$)** | 2,423 | 2,423 | 2,423 | 2,423 | 2,423 | **All Identical** |

---

## 3. Phase 5: Baseline Comparison & Relative Improvements

Evaluated against established baselines on identical validation observations:

### 1. Global Mean Baseline
- Predicting constant historical training mean flow ($\bar{y} = 43,685.08\text{ cfs}$) across all 24,088 rows.
- **Baseline RMSE**: **$116,711.28\text{ cfs}$**
- **Leading Model (`log_spec_q`) RMSE**: **$82,871.13\text{ cfs}$**
- **Relative Improvement**:
  $$\text{Improvement} = \frac{116,711.28 - 82,871.13}{116,711.28} \times 100\% = \mathbf{+28.99\%}$$

### 2. Ridge Regression Baseline
- Ridge regression evaluated under strict out-of-system LORSO conditions.
- **Baseline RMSE**: **$104,979.70\text{ cfs}$**
- **Leading Model (`log_spec_q`) RMSE**: **$82,871.13\text{ cfs}$**
- **Relative Improvement**:
  $$\text{Improvement} = \frac{104,979.70 - 82,871.13}{104,979.70} \times 100\% = \mathbf{+21.06\%}$$

Both comparisons confirm that nonlinear gradient boosted trees on specific discharge provide a genuine, substantial performance advantage over climatological and linear hydrologic baselines.

---

## 4. Phase 6: Station-Wise Performance & Vicksburg Mega-Basin Diagnosis

### Top 5 Best-Performing Stations (by $R^2$ on `LightGBM log_spec_q`):
1. **USGS `13317000` (Salmon River, Columbia System)**: $R^2 = \mathbf{0.3976}$, RMSE = $10,585.3\text{ cfs}$, MAE = $5,119.3\text{ cfs}$.
2. **USGS `03335500` (Wabash River, Ohio River Basin)**: $R^2 = \mathbf{0.3655}$, RMSE = $5,586.9\text{ cfs}$, MAE = $2,623.1\text{ cfs}$.
3. **USGS `07144100` (Little Arkansas River, KS)**: $R^2 = \mathbf{0.3521}$, RMSE = $462.6\text{ cfs}$, MAE = $299.8\text{ cfs}$.
4. **USGS `08164000` (Lavaca River near Edna, TX)**: $R^2 = \mathbf{0.3473}$, RMSE = $946.7\text{ cfs}$, MAE = $275.1\text{ cfs}$.
5. **USGS `08068000` (West Fork San Jacinto River, TX)**: $R^2 = \mathbf{0.2523}$, RMSE = $979.8\text{ cfs}$, MAE = $311.6\text{ cfs}$.

### Top 5 Worst-Performing Stations (by $R^2$ on `LightGBM log_spec_q`):
1. **USGS `08158000` (Colorado River at Austin, TX)**: $R^2 = \mathbf{-1432.20}$, RMSE = $16,211.7\text{ cfs}$ (Heavily regulated by Highland Lakes dam chain; ephemeral runoff disconnected from local rainfall).
2. **USGS `09380000` (Colorado River at Lees Ferry, AZ)**: $R^2 = \mathbf{-939.24}$, RMSE = $118,298.3\text{ cfs}$ (Direct outflow of Glen Canyon Dam / Lake Powell; flow governed by Bureau of Reclamation hydropower schedule, not rainfall).
3. **USGS `06805500` (Platte River at Louisville, NE)**: $R^2 = \mathbf{-476.51}$, RMSE = $46,661.9\text{ cfs}$ (Snowmelt-dominated, braided channel with multi-week travel time from Wyoming/Colorado).
4. **USGS `06610000` (Missouri River at Omaha, NE)**: $R^2 = \mathbf{-35.33}$, RMSE = $45,790.4\text{ cfs}$ (Heavily regulated mainstem Missouri reservoir system).
5. **USGS `12472800` (Columbia River at Priest Rapids, WA)**: $R^2 = \mathbf{-2.56}$, RMSE = $98,321.9\text{ cfs}$ (Mid-Columbia hydropower reservoir cascades).

### Stations with Negative $R^2$:
Exactly **20 of the 33 stations** exhibit negative $R^2$ under out-of-system LORSO evaluation. In all 20 cases, the primary physical driver is **severe anthropogenic regulation (upstream dams, reservoirs, irrigation diversions)** or **massive spatial scale mismatch** where local meteorology does not correlate with dam releases.

### Head-to-Head: `log_spec_q` vs. `spec_q`:
- **Overall RMSE**: `log_spec_q` wins on **20 stations**, `spec_q` wins on **13 stations**.
- **Overall MAE**: `log_spec_q` wins on **20 stations**, `spec_q` wins on **13 stations**.
- **Peak RMSE**: `spec_q` wins on **18 stations**, `log_spec_q` wins on **15 stations**.

### Mississippi River at Vicksburg (`07289000`) Audit:
- **Observed Mean Discharge**: $562,272.6\text{ cfs}$; **Maximum**: $1,230,000.0\text{ cfs}$.
- **Baseline Error**: RMSE = $430,549.1\text{ cfs}$, MAE = $325,153.1\text{ cfs}$, Peak RMSE = $799,253.6\text{ cfs}$.
- **Squared Error Contribution**:
  - `LightGBM Log-Specific Discharge`: Vicksburg accounts for **$81.80\%$ of total pooled squared error**.
  - `LightGBM Specific Discharge`: Vicksburg accounts for **$77.52\%$ of total pooled squared error**.
  - `LightGBM Raw Peak-Weighted`: Vicksburg accounts for **$86.34\%$ of total pooled squared error**.
  - `XGBoost Log1p`: Vicksburg accounts for **$88.89\%$ of total pooled squared error**.

---

## 5. Phase 7: Flood Peak Performance Analysis

Evaluated on the upper decile of daily mean discharge per station ($N = 2,423$ observations):
- **All Top 5 Largest Peak Prediction Errors** occurred at Vicksburg (`07289000`) during the March 2022 crest ($1,180,000 - 1,230,000\text{ cfs}$), where `log_spec_q` predicted $51,359 - 150,929\text{ cfs}$, generating single-day errors exceeding $1,000,000\text{ cfs}$.
- **Peak Bias**:
  - `LightGBM spec_q` achieved the lowest peak underprediction bias ($-35,800.22\text{ cfs}$) and lowest peak MAE ($74,120.45\text{ cfs}$).
  - `LightGBM log_spec_q` underpredicted peak flows by an average of $-41,560.11\text{ cfs}$.
- **Physical Classification**: These events represent extreme **daily-mean discharge** ($00060\_00003$, 24-hour integrated volume) rather than instantaneous 15-minute stage crests ($00060\_00001$).

---

## 6. Deliverable Files Reference

1. [prompt_j_final_accuracy_report.md](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_j_final_accuracy_report.md) — Comprehensive technical audit.
2. [prompt_j_model_comparison.csv](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_j_model_comparison.csv) — 5-model comparison table across all 16 recalculated metrics.
3. [prompt_j_station_accuracy.csv](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_j_station_accuracy.csv) — Detailed per-station accuracy breakdown across all 33 stations and 5 models (165 rows).
4. [prompt_j_final_recommendation.md](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_j_final_recommendation.md) — Final model accuracy verdict and operational guidance.

