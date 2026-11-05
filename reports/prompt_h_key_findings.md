# PRAVAHA — Prompt H: Key ML Audit Findings & Executive Summary

**Date:** 2026-11-05  
**Auditor:** PRAVAHA Lead ML Systems Engineer  
**Scope:** Performance & Accuracy Evaluation across 5 Existing LORSO Models  
**Reference Files:**  
- Full Technical Report: [`reports/prompt_h_model_accuracy_audit.md`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_h_model_accuracy_audit.md)  
- Model Comparison Data: [`reports/prompt_h_model_comparison.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_h_model_comparison.csv)  
- Station Performance Data: [`reports/prompt_h_station_performance.csv`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/reports/prompt_h_station_performance.csv)

---

## 1. Validation Integrity Result

* **Validation Row Count:** **24,088 unique station-date records** (2022-01-01 to 2023-12-31 across 33 active USGS stations).
* **Total Predictions:** **120,440 predictions** ($24,088 \times 5\text{ models}$).
* **Data Cleanness:** **Zero duplicates, zero NaNs, zero infinite values, zero negative predictions.**
* **Bitwise Target Integrity:** Validation ground-truth labels match `PRAVAHA_TRAIN_LABELLED.csv` with a maximum absolute discrepancy of **$0.000000\text{ cfs}$**.
* **Zero Target Leakage:** No training-fit predictions or future time slices were utilized.

---

## 2. Definitive Model Comparison Table

All four required FLOODCAST metrics independently recalculated across all 24,088 identical out-of-system validation rows:

| Rank | Model Name | Target Formulation | Overall RMSE (cfs) | Top-10% Peak RMSE (cfs) | Overall MAE (cfs) | Pooled R² | Macro RMSE (cfs) | Peak Underpred (%) |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 | **LightGBM Log-Specific Discharge** | `log_spec_q` | **82,871.13** | 156,593.84 | **24,644.29** | **0.4910** | **31,814.42** | 67.8% |
| 🥈 | **LightGBM Specific Discharge** | `spec_q` | 86,836.57 | **155,136.83** | 26,091.96 | 0.4411 | 34,348.21 | **63.0%** |
| 🥉 | **LightGBM Raw Peak-Weighted (2.5x)** | `raw` | 108,321.35 | 202,091.42 | 32,259.99 | 0.1303 | 39,637.43 | 71.2% |
| 4 | **LightGBM Raw Unweighted** | `raw` | 109,609.53 | 204,474.57 | 32,312.13 | 0.1095 | 39,558.32 | 73.4% |
| 5 | **XGBoost Log1p** | `log1p` | 109,842.15 | 203,656.14 | 28,995.81 | 0.1057 | 35,448.74 | 64.9% |

---

## 3. Best Model by Each Metric

* **Best Overall RMSE:** **LightGBM Log-Specific Discharge** ($82,871.13\text{ cfs}$)
* **Best Top-10% Peak RMSE:** **LightGBM Specific Discharge** ($155,136.83\text{ cfs}$)
* **Best Overall MAE:** **LightGBM Log-Specific Discharge** ($24,644.29\text{ cfs}$)
* **Best Pooled R²:** **LightGBM Log-Specific Discharge** ($0.4910$)
* **Best Macro RMSE (Station-Balanced):** **LightGBM Log-Specific Discharge** ($31,814.42\text{ cfs}$)
* **Best Median Station RMSE:** **LightGBM Specific Discharge** ($5,036.51\text{ cfs}$)
* **Most Individual Station Wins:** **XGBoost Log1p** (Lowest RMSE on **14 of 33 stations**)

> [!NOTE]
> **No single model dominates all metrics.** LightGBM `log_spec_q` is the undisputed leader for volumetric prediction, average error, and explained variance ($R^2$), while LightGBM `spec_q` is the strongest on extreme flood peaks, and XGBoost `log1p` is the best localized predictor for small headwater basins.

---

## 4. Current Leading Model Limitations

The leading architecture (**LightGBM Log-Specific Discharge**):
1. **Underpredicts Extreme Flood Crests:** 67.8% of top-10% flow days are underpredicted because log-compression compresses the loss gradient on upper outliers.
2. **Vulnerability to Regulated Flow:** Fails on hydro-peaking dams (e.g. Colorado at Lees Ferry `09380000`, $R^2 = -939.2$, and Priest Rapids `12472800`, $R^2 = -2.56$) where streamflow is dictated by power generation turbines rather than local meteorology.
3. **No Dynamic River Routing:** Lacks multi-day lag convolutions for continental basins where rainfall takes 10–20 days to traverse upstream tributaries.

---

## 5. Station-Wise Error Analysis & The Vicksburg Effect

1. **Verification of the Vicksburg Claim:**  
   - Total squared error across all 33 stations: $1.65 \times 10^{14}\text{ cfs}^2$  
   - Station `07289000` (Mississippi River at Vicksburg) squared error: $1.35 \times 10^{14}\text{ cfs}^2$  
   - **Vicksburg Share of Total Squared Error: 81.80%** (Claim **CONFIRMED**).
2. **Why This Happens:** Vicksburg drains $1,144,500\text{ sq mi}$ and carries flows over $1.2\text{ million cfs}$. An 8% relative error at Vicksburg generates $100,000\text{ cfs}$ of error, whose square ($10^{10}$) dwarfs the entire annual discharge of smaller mountain rivers.
3. **Worst Stations:** Vicksburg `07289000` ($430\text{k cfs}$), Lees Ferry `09380000` ($93.6\text{k cfs}$), Priest Rapids `12472800` ($77.9\text{k cfs}$), St. Louis `07010000` ($71.3\text{k cfs}$).
4. **Best Stations:** Pecos `08378500` ($108.6\text{ cfs}$), Logan `10109000` ($153.2\text{ cfs}$), Little Missouri `06334500` ($373.1\text{ cfs}$), Little Arkansas `07144100` ($485.4\text{ cfs}$), Cedar River `12119000` ($581.4\text{ cfs}$).

---

## 6. Baseline Value Assessment

* Against the **Global Mean baseline** ($\text{RMSE} = 116,711\text{ cfs}, R^2 = -0.0096$), LightGBM `log_spec_q` reduces RMSE by **29.0%** and increases $R^2$ to $+0.4910$.
* Against the **Out-of-System LORSO Ridge baseline** ($\text{RMSE} = 104,980\text{ cfs}, \text{Peak RMSE} = 201,340\text{ cfs}$), LightGBM `log_spec_q` reduces RMSE by **21.1%** and Peak RMSE by **22.2%**.
* **Verdict:** Advanced gradient boosted decision trees provide a **genuine, verified predictive improvement** over baseline linear and mean models for spatial generalization.

---

## 7. Recommended Next ML Experiment

1. **Integrate Open-Meteo High-Resolution Features:** Ingest ERA5-Land variables (`precipitation_sum`, `soil_moisture_0_to_7cm_mean`, `et0_fao_evapotranspiration`) alongside MERRA-2.
2. **Engineer Flow-Lag Routing Features:** Add 3-day, 7-day, and 14-day rolling antecedent precipitation indices (API) to capture travel time on macro-basins.
3. **Hydrological Dam Regulation Feature:** Add a binary or continuous degree-of-regulation flag to separate natural runoff from reservoir releases.
4. **Dual-Branch Loss Formulation:** Train an asymmetric Huber loss with a sample penalty weight on $y \ge q_{90}$ specifically within the `log_spec_q` space to eliminate the 67.8% peak underprediction bias.

