# PRAVAHA — Model Performance Percentage & Relative Accuracy Analysis

**Audit Protocol**: PROMPT J1  
**Task Type**: Continuous Numerical Streamflow Regression (Discharge in CFS)  
**Evaluation Methodology**: Leave-One-River-System-Out (LORSO) Spatial Holdout Cross-Validation  
**Data Source**: `data/processed/prompt_e_validation_predictions.parquet`  
**Validation Population**: Exactly 24,088 station-days across 33 hydrologically diverse USGS stations (2022–2023)  
**Evaluated Models**: 5 Existing PRAVAHA Machine Learning Architectures  

---

## 1. Executive Summary & Foundational Machine Learning Context

Predicting river discharge in cubic feet per second (CFS) across unseen river systems is a **continuous regression problem**, not a binary or multi-class classification problem. 

### Why Conventional "Accuracy Percentages" (e.g., "95% Accuracy") Are Scientifically Invalid:
In classification tasks, an observation is either discrete True or False, enabling a simple accuracy percentage:
$$\text{Accuracy} = \frac{\text{Correct Predictions}}{\text{Total Predictions}} \times 100\%$$
In continuous hydrologic streamflow regression:
1. **Infinitesimal Probability of Exact Match**: The mathematical probability that a model predicts the exact floating-point discharge of a river down to $0.0000\text{ cfs}$ is effectively zero ($P(\hat{y} = y) = 0$).
2. **Skewness Across Five Orders of Magnitude**: Streamflows range from $0.0\text{ cfs}$ on dry Southwestern arroyos to over $1,230,000\text{ cfs}$ on the Lower Mississippi River. A relative error of $10\text{ cfs}$ represents an infinitesimal $0.0008\%$ error at Vicksburg, but a catastrophic $1000\%$ error on a headwater stream flowing at $1\text{ cfs}$.
3. **Misleading Industry Clichés**: Claiming "95% accuracy" in streamflow prediction without defining a tolerance threshold is either mathematically meaningless or indicative of confusing the $R^2$ coefficient of determination with predictive precision.

To provide hydrologically and statistically sound percentage indicators, this audit computes five standardized relative indicators:
- **Variance Explained ($R^2 \times 100\%$)**
- **Relative RMSE Improvement over Baselines (%)**
- **Normalised Root Mean Square Error (NRMSE %)**
- **Prediction Tolerance Rates ($\pm 10\%, \pm 20\%, \pm 30\%$)**
- **Peak Flood Performance Percentages (%)**

---

## 2. Mathematical Formulations & Data Provenance

All metrics were computed strictly across the identical **24,088 validation rows** from `data/processed/prompt_e_validation_predictions.parquet`:

### A. Variance Explained (%)
$$\text{Variance Explained (\%)} = \text{Pooled } R^2 \times 100\% = \left(1 - \frac{\sum_{i=1}^N (y_i - \hat{y}_i)^2}{\sum_{i=1}^N (y_i - \bar{y})^2}\right) \times 100\%$$
- **Verification**: For the leading `LightGBM log_spec_q` model, $R^2 = 0.4910$, yielding exactly **$49.10\%$ Variance Explained**.
- **Important Note**: Variance explained quantifies the fraction of total temporal and spatial variance accounted for by the model. It is **not** the percentage of time the model is correct.

### B. Relative RMSE Improvement (%)
$$\text{RMSE Improvement (\%)} = \left(\frac{\text{Baseline RMSE} - \text{Model RMSE}}{\text{Baseline RMSE}}\right) \times 100\%$$
Evaluated against two established baselines:
1. **Global Mean Baseline**: Predicting the constant historical training mean ($\bar{y}_{\text{train}} = 43,685.08\text{ cfs}$) across all validation rows. Validation RMSE = **$116,711.28\text{ cfs}$**.
2. **Ridge Regression Baseline**: Out-of-system LORSO Ridge regression using identical features. Validation RMSE = **$104,979.70\text{ cfs}$** (from `reports/prompt_h_model_accuracy_audit.md` and `reports/baseline_validation_report.md`).

### C. Normalised RMSE (NRMSE %)
$$\text{NRMSE (\%)} = \left(\frac{\text{RMSE}}{\bar{y}_{\text{actual}}}\right) \times 100\%$$
- **Validation Actual Mean Discharge**: $\bar{y}_{\text{actual}} = \mathbf{32,288.44\text{ cfs}}$.
- **Limitations for River Discharge**: Because the distribution of river discharge is extreme positive-skewed (median discharge is only $2,230.00\text{ cfs}$), the mean is heavily pulled upward by the Mississippi River ($562,273\text{ cfs}$ mean). Consequently, NRMSE numbers exceed $100\%$ across all models because squared errors on mega-basins dominate the unweighted numerator.

### D. Prediction Tolerance Rate (%)
$$\text{Tolerance Rate}_{\pm K\%} = \frac{\sum_{i \in \text{Eligible}} \mathbb{I}\left(\frac{|\hat{y}_i - y_i|}{y_i} \le \frac{K}{100}\right)}{N_{\text{Eligible}}} \times 100\%$$
- **Low-Flow Exclusion Threshold ($y \ge 50.0\text{ cfs}$)**:
  - When $y \approx 0\text{ cfs}$, dividing by $y$ causes extreme mathematical instability (e.g. actual = $0.2\text{ cfs}$, pred = $5.0\text{ cfs} \implies 2,400\%$ error).
  - Out of 24,088 total validation rows, **2,892 low-flow observations ($< 50\text{ cfs}$)** were excluded from tolerance calculations.
  - **Eligible Sample Size**: **$21,196$ observations** ($88.0\%$ of the validation dataset).
  - *(For full transparency, results at $y \ge 10.0\text{ cfs}$ with $N = 22,884$ eligible are also reported).*

### E. Peak Performance Percentages (%)
Evaluated on the **top 10% highest daily mean flow observations per station** ($y \ge q_{90}(\text{station})$) across the validation period ($N_{\text{peak}} = \mathbf{2,423\text{ samples}}$):
- **Peak Underprediction %**: Percentage where $\hat{y} < y$.
- **Peak Overprediction %**: Percentage where $\hat{y} > y$.
- **Peak Tolerance Rates**: Percentage of peak samples with relative error $\le 20\%$ and $\le 30\%$.
- *Hydrological Clarification*: These observations represent extreme **daily-mean discharge** ($00060\_00003$), which integrates 24-hour volume, distinct from instantaneous 15-minute peak stage crests ($00060\_00001$).

---

## 3. Comprehensive Five-Model Comparison Table

All calculations executed across the identical 24,088 validation rows:

| Performance Metric | LightGBM log_spec_q | LightGBM spec_q | LightGBM raw peak-weighted (2.5x) | LightGBM raw unweighted | XGBoost log1p |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Target Formulation** | $\log(q + 1)$ | $q = Q / A$ | Raw $Q$ (cfs) | Raw $Q$ (cfs) | $\log(Q + 1)$ |
| **Overall RMSE (cfs)** | **82,871.13** | 86,836.57 | 108,321.35 | 109,609.53 | 109,842.15 |
| **Top-10% Peak RMSE (cfs)** | 156,593.84 | **155,136.83** | 202,091.42 | 204,474.57 | 203,656.14 |
| **Overall MAE (cfs)** | **24,644.29** | 26,091.96 | 32,259.99 | 32,312.13 | 28,995.81 |
| **Pooled $R^2$** | **0.4910** | 0.4411 | 0.1303 | 0.1095 | 0.1057 |
| **Variance Explained (%)** | **49.10%** | 44.11% | 13.03% | 10.95% | 10.57% |
| **RMSE Imp. vs Global Mean (%)** | **+28.99%** | +25.60% | +7.19% | +6.08% | +5.89% |
| **RMSE Imp. vs Ridge LORSO (%)** | **+21.06%** | +17.28% | -3.18% | -4.41% | -4.63% |
| **NRMSE (%)** | **256.66%** | 268.94% | 335.48% | 339.47% | 340.19% |
| **% within $\pm 10\%$ ($y \ge 50\text{ cfs}$)** | 6.78% | **7.05%** | 3.87% | 3.74% | 5.68% |
| **% within $\pm 20\%$ ($y \ge 50\text{ cfs}$)** | 14.48% | **14.62%** | 7.67% | 7.55% | 11.86% |
| **% within $\pm 30\%$ ($y \ge 50\text{ cfs}$)** | **22.06%** | 21.99% | 11.90% | 11.51% | 18.30% |
| **% within $\pm 20\%$ ($y \ge 10\text{ cfs}$)** | 13.49% | **13.69%** | 7.12% | 7.05% | 11.40% |
| **Peak Underprediction %** | 67.81% | 62.98% | **55.43%** | 57.49% | 80.19% |
| **Peak Overprediction %** | 32.19% | 37.02% | **44.57%** | 42.51% | 19.81% |
| **Peak within $\pm 20\%$ Error** | 10.11% | **14.11%** | 6.48% | 5.98% | 8.75% |
| **Peak within $\pm 30\%$ Error** | 15.72% | **21.38%** | 10.40% | 8.96% | 13.62% |
| **Eligible Observations ($y \ge 50$)**| 21,196 | 21,196 | 21,196 | 21,196 | 21,196 |
| **Excluded Low-Flow ($y < 50$)** | 2,892 | 2,892 | 2,892 | 2,892 | 2,892 |
| **Peak Samples Count ($q_{90}$)** | 2,423 | 2,423 | 2,423 | 2,423 | 2,423 |

---

## 4. Answers to Final Evaluation Questions

### 1. What percentage of variance does the leading model explain?
**Answer**: **49.10%** ($R^2 = 0.4910$).  
The model accounts for approximately half of the total spatiotemporal variance in daily discharge across completely unseen river systems. *(Under Prompt I optimization, this rises to 59.64%)*.

### 2. What percentage does it improve RMSE over the global mean baseline?
**Answer**: **28.99% improvement**.  
Baseline RMSE drops from $116,711.28\text{ cfs}$ (predicting the continental mean flow) to $82,871.13\text{ cfs}$.

### 3. What percentage does it improve RMSE over Ridge regression?
**Answer**: **21.06% improvement**.  
Baseline LORSO Ridge regression RMSE drops from $104,979.70\text{ cfs}$ to $82,871.13\text{ cfs}$, proving that non-linear tree models provide substantial value over linear hydrologic baselines.

### 4. What percentage of predictions fall within $\pm 10\%$, $\pm 20\%$, and $\pm 30\%$ error?
**Answer** (evaluated on non-zero flows $y \ge 50\text{ cfs}$):
- Within $\pm 10\%$: **6.78%** (1,438 / 21,196)
- Within $\pm 20\%$: **14.48%** (3,070 / 21,196)
- Within $\pm 30\%$: **22.06%** (4,675 / 21,196)  
*(When evaluated at $y \ge 10\text{ cfs}$, $\pm 20\%$ tolerance is $13.49\%$).*

### 5. What percentage of extreme peak observations are underestimated?
**Answer**: **67.81%** (1,643 of 2,423 top-10% peak flow events).  
Due to logarithmic compression, `log_spec_q` underpredicts upper-tail flood surges. By contrast, the linear specific discharge model (`LightGBM spec_q`) reduces underprediction to **62.98%**, and peak-weighted raw models reduce it to **55.43%**.

### 6. Which model has the best percentage-based performance?
**Answer**: 
- **Overall Winner**: **`LightGBM log_spec_q`** dominates Variance Explained (**49.10%**), Relative Improvement vs Mean (**+28.99%**), Relative Improvement vs Ridge (**+21.06%**), and lowest overall NRMSE (**256.66%**).
- **Peak Flood Specialist**: **`LightGBM spec_q`** wins on Peak RMSE ($155,136.83\text{ cfs}$), Peak Tolerance within $\pm 20\%$ (**14.11%**), Peak Tolerance within $\pm 30\%$ (**21.38%**), and lower peak underprediction (**62.98%**).

### 7. Which percentage metrics are most suitable for the hackathon presentation?
**Answer**: See detailed slide wording in `reports/prompt_j1_presentation_recommendation.md`.
1. **"49.1% of Streamflow Variance Explained ($R^2 = 0.491$)"** on completely unseen river basins.
2. **"29.0% Error Reduction over Climatological Baselines"** and **"21.1% Gain over Ridge Regression"**.
3. **"Peak Flood Underprediction Audited at 67.8%"** — presenting honest, scientifically credible evaluation that highlights the necessity of flood warning safety buffers.

