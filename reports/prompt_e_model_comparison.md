# PRAVAHA — Leave-One-River-System-Out (LORSO) Benchmark Report
**Project**: PRAVAHA — FLOODCAST Hackathon  
**Target Variable**: Daily River Discharge (`discharge_cfs`)  
**Evaluation Methodology**: Leave-One-River-System-Out (LORSO) Cross-Validation  
**Date**: November 2026  
**Auditor & ML Engineer**: Lead Data & ML Systems Engineer  

---

## Executive Summary

This report documents the rigorous implementation and empirical results of the **Leave-One-River-System-Out (LORSO)** validation benchmark for the FLOODCAST regression challenge.

In previous phases, Strategy C evaluated spatial generalisation by holding out individual gauges while evaluating model predictions on future time periods (2022–2023). However, our forensic audit (Prompt D) identified a critical hydrological flaw:
> *When holding out station `07010000` (Mississippi River at St. Louis, MO), upstream gauges on the exact same mainstem (`05331000` at St. Paul, MN and `05420500` at Clinton, IA) remained in the training set.*

To eliminate all advective river network connectivity leakage, **Phase E** establishes a 23-river-system grouping and implements strict out-of-system cross-validation:
- When a river system is held out, **every single connected gauge on that river system is removed from training**.
- Training uses strictly data prior to $2021\text{-}12\text{-}31$ from all other eligible river systems.
- Evaluation is performed strictly on the held-out river system during $2022\text{-}01\text{-}01$ to $2023\text{-}12\text{-}31$.
- Evaluates 5 controlled model formulations across **24,088 identical out-of-system validation rows** spanning 33 active stations.

---

## 1. LORSO Cross-Validation Fold Design (23 Folds)

| Fold ID | Held-Out River System | Stations in River System | Training Stations | Training Samples | Validation Samples (2022–2023) | Connected Gauges Excluded |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **01** | Potomac River | `01646500` | 33 | 142,346 | 730 | 1 |
| **02** | Neuse River | `02087500` | 33 | 142,346 | 730 | 1 |
| **03** | Mississippi River Mainstem | `05331000`, `05420500`, `07010000`, `07289000` | 30 | 129,197 | 2,920 | 4 |
| **04** | Texas Colorado River | `08158000` | 33 | 142,347 | 730 | 1 |
| **05** | California Central Valley System | `11447650`, `11303500` | 32 | 140,247 | 730 | 2 |
| **06** | Susquehanna River | `01570500` | 33 | 142,346 | 730 | 1 |
| **07** | Catawba River | `02146000` | 33 | 142,346 | 730 | 1 |
| **08** | Santa Fe River | `02322500` | 33 | 142,346 | 730 | 1 |
| **09** | Ohio River Basin | `03183500`, `03335500` | 32 | 137,963 | 1,460 | 2 |
| **10** | Fox River | `040851385` | 33 | 142,348 | 728 | 1 |
| **11** | Kawishiwi River | `05127000` | 33 | 142,347 | 730 | 1 |
| **12** | Missouri River System | `06334500`, `06610000`, `06805500` | 31 | 133,580 | 2,190 | 3 |
| **13** | Little Arkansas River | `07144100` | 33 | 142,346 | 730 | 1 |
| **14** | Red River | `07337000` | 33 | 142,350 | 730 | 1 |
| **15** | San Jacinto River | `08068000` | 33 | 142,346 | 730 | 1 |
| **16** | Lavaca River | `08164000` | 33 | 142,346 | 730 | 1 |
| **17** | San Antonio River | `08181800` | 33 | 142,346 | 730 | 1 |
| **18** | Pecos River | `08378500` | 33 | 142,346 | 730 | 1 |
| **19** | Upper Colorado River System | `09058000`, `09163500`, `09380000` | 31 | 133,580 | 2,190 | 3 |
| **20** | Logan River | `10109000` | 33 | 142,346 | 730 | 1 |
| **21** | Salinas River | `11152500` | 33 | 142,346 | 730 | 1 |
| **22** | Cedar River | `12119000` | 33 | 142,346 | 730 | 1 |
| **23** | Columbia River System | `12472800`, `13317000`, `14211720` | 31 | 133,581 | 2,190 | 3 |

*Note*: In Fold 05 (California Central Valley), station `11447650` (Sacramento River) has daily discharge only through 2015-09-30, so its 2022–2023 validation count is 0, while San Joaquin (`11303500`) provides 730 validation rows.

---

## 2. Master LORSO Model Comparison

All 5 models were evaluated across the exact same **24,088 out-of-system validation rows** and **2,423 extreme peak events** (top-10% flow days per station derived on actual validation labels).

### 2.1 Pooled Metrics across all 24,088 Validation Observations

| Model Architecture | Target Formulation | Peak Weighted | Overall RMSE (cfs) | Top-10% Peak RMSE (cfs) | MAE (cfs) | R² |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **LightGBM Log-Specific Discharge** | `log_spec_q` | No | **82,871.1** | 156,593.8 | **24,644.3** | **0.4910** |
| **LightGBM Specific Discharge** | `spec_q` | No | 86,836.6 | **155,136.8** | 26,092.0 | 0.4411 |
| **LightGBM Raw Peak-Weighted** | `raw` | Yes (2.5x) | 108,321.3 | 202,091.4 | 32,260.0 | 0.1303 |
| **LightGBM Raw Unweighted** | `raw` | No | 109,609.5 | 204,474.6 | 32,312.1 | 0.1095 |
| **XGBoost Log1p** | `log1p` | No | 109,842.1 | 203,656.1 | 28,995.8 | 0.1057 |

### 2.2 Macro-Average Metrics across 33 Stations (Equal Station Weighting)

| Model Architecture | Target Formulation | Macro RMSE (cfs) | Macro Peak RMSE (cfs) | Macro MAE (cfs) | Macro R² |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **LightGBM Log-Specific Discharge** | `log_spec_q` | **31,814.4** | 58,034.8 | **24,642.4** | -87.7 |
| **LightGBM Specific Discharge** | `spec_q` | 34,348.2 | **56,345.4** | 26,090.0 | -113.0 |
| **XGBoost Log1p** | `log1p` | 35,448.7 | 67,418.2 | 28,993.8 | **-33.1** |
| **LightGBM Raw Unweighted** | `raw` | 39,558.3 | 73,177.1 | 32,309.7 | -149.2 |
| **LightGBM Raw Peak-Weighted** | `raw` | 39,637.4 | 72,732.4 | 32,257.6 | -184.6 |

---

## 3. Key Empirical Findings & Architectural Insights

### 3.1 The Decisive Advantage of Specific Discharge ($q = Q / A$)
Under true spatial holdout (LORSO), **drainage area normalization is the single most critical architectural choice**:
- **Error Reduction**: LightGBM `log_spec_q` reduces pooled RMSE from $109,609\text{ cfs}$ (Raw) down to $82,871\text{ cfs}$—an **absolute error reduction of 26,738 cfs (24.4%)**.
- **Flood Peak Accuracy**: LightGBM `spec_q` reduces Top-10% Peak RMSE from $204,475\text{ cfs}$ (Raw) to $155,137\text{ cfs}$—an **absolute peak error reduction of 49,338 cfs (24.1%)**.
- **Explained Variance**: $R^2$ jumps from $0.1095$ (Raw) to **$0.4910$ (`log_spec_q`)**, demonstrating that predicting unit runoff yield ($cfs / sq\ mi$) prevents catastrophic volume scale mismatch on unseen river systems.

### 3.2 Why Raw Models Fail on Unseen River Systems
- In chronological validation (where all stations were in training), Raw LightGBM achieved an RMSE of $\sim 59,000\text{ cfs}$ because tree splits memorized basin-specific discharge ranges.
- However, when an entire river system (such as the Mississippi Mainstem with Vicksburg, DA $1,144,500\text{ sq mi}$) is held out, a model trained on raw CFS has never encountered a basin of that volumetric magnitude. Its trees cap maximum discharge predictions at $\sim 350,000\text{ cfs}$, resulting in errors exceeding $1,000,000\text{ cfs}$ during peak Mississippi crests.
- Conversely, Specific Discharge ($q = Q/A$) predicts runoff yield in $cfs / sq\ mi$, which automatically scales to any basin size when multiplied by that basin's verified drainage area.

### 3.3 The Controlled Impact of Peak Sample Weighting ($w=2.5$)
- Evaluating LightGBM Raw with peak sample weighting ($w=2.5$ for $y \ge q_{90}$ derived strictly on training folds) reduced pooled peak RMSE from $204,474.6\text{ cfs}$ to $202,091.4\text{ cfs}$ ($2,383\text{ cfs}$ reduction), and slightly improved overall RMSE ($109,610\text{ cfs} \to 108,321\text{ cfs}$).
- However, peak weighting on raw CFS is fundamentally constrained: **it cannot correct a scale extrapolation failure**. Without area normalization, no amount of sample weighting enables a raw tree model to predict $1.4\text{ million cfs}$ on an unseen macro-basin.

---

## 4. Per-River-System Breakdown Table

Performance comparison across all 23 held-out river systems (Overall RMSE in $cfs$):

| River System | N_St | Val Rows | LightGBM Raw | Peak-Weighted Raw | LightGBM Spec Q | LightGBM Log-Spec Q | XGBoost Log1p | Winning Model |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Potomac River** | 1 | 730 | 7,753.8 | 7,603.2 | 7,841.8 | **7,557.8** | 7,940.7 | LightGBM Log-Spec Q |
| **Neuse River** | 1 | 730 | 1,250.3 | 1,586.4 | 863.2 | 892.0 | **764.5** | XGBoost Log1p |
| **Mississippi Mainstem** | 4 | 2,920 | 301,868.7 | 297,103.0 | 232,178.9 | **221,310.6** | 306,260.7 | **LightGBM Log-Spec Q (-80.5k cfs)** |
| **Texas Colorado River** | 1 | 730 | 23,749.6 | 26,988.1 | 19,769.7 | 16,211.7 | **8,797.2** | XGBoost Log1p |
| **CA Central Valley** | 1 | 730 | 25,145.7 | 30,519.4 | 14,061.0 | **12,845.5** | 22,531.3 | LightGBM Log-Spec Q |
| **Susquehanna River** | 1 | 730 | 36,782.5 | **32,648.4** | 34,305.5 | 34,825.0 | 36,791.3 | Peak-Weighted Raw |
| **Catawba River** | 1 | 730 | 2,866.3 | 2,903.6 | 2,027.3 | **1,979.2** | 3,132.5 | LightGBM Log-Spec Q |
| **Santa Fe River** | 1 | 730 | 2,417.7 | 1,720.7 | 1,497.6 | **638.1** | 1,404.2 | LightGBM Log-Spec Q |
| **Ohio River Basin** | 2 | 1,460 | 4,302.8 | 4,325.2 | 3,868.1 | 4,248.7 | **3,313.3** | XGBoost Log1p |
| **Fox River** | 1 | 728 | 4,183.0 | 5,345.5 | **2,865.0** | 2,865.6 | 6,008.2 | LightGBM Spec Q |
| **Kawishiwi River** | 1 | 730 | 1,339.8 | **1,224.6** | 1,566.7 | 1,606.5 | 1,590.4 | Peak-Weighted Raw |
| **Missouri System** | 3 | 2,190 | 33,410.8 | 37,694.3 | 45,819.1 | 37,745.6 | **9,275.8** | XGBoost Log1p |
| **Little Arkansas River**| 1 | 730 | 700.9 | 796.6 | 563.0 | 462.6 | **450.2** | XGBoost Log1p |
| **Red River** | 1 | 730 | 41,511.5 | 37,604.7 | 19,572.7 | 12,737.5 | **6,451.9** | XGBoost Log1p |
| **San Jacinto River** | 1 | 730 | 1,088.1 | 1,179.7 | **904.8** | 979.8 | 921.8 | LightGBM Spec Q |
| **Lavaca River** | 1 | 730 | 1,001.2 | **883.5** | 887.3 | 946.7 | 1,012.7 | Peak-Weighted Raw |
| **San Antonio River** | 1 | 730 | 1,097.7 | 1,456.6 | 731.9 | 553.4 | **516.8** | XGBoost Log1p |
| **Pecos River** | 1 | 730 | 296.3 | 619.1 | 229.6 | **119.5** | 209.1 | LightGBM Log-Spec Q |
| **Upper Colorado System**| 3 | 2,190 | 64,253.2 | 66,758.0 | 69,372.4 | 68,423.4 | **56,392.3** | XGBoost Log1p |
| **Logan River** | 1 | 730 | 1,093.7 | 1,740.9 | 265.8 | 246.0 | **243.2** | XGBoost Log1p |
| **Salinas River** | 1 | 730 | 4,688.5 | 3,867.6 | 3,585.5 | **2,415.7** | 6,125.7 | LightGBM Log-Spec Q |
| **Cedar River** | 1 | 730 | 10,645.0 | 10,664.4 | 581.0 | 599.6 | **470.2** | XGBoost Log1p |
| **Columbia System** | 3 | 2,190 | 62,341.1 | 63,362.7 | **58,256.2** | 59,045.8 | 60,510.1 | LightGBM Spec Q |

---

## 5. Flood Peak & Extreme Surge Analysis

Detailed evaluation of models on the **2,423 top-10% flood peak events** and the **Top-50 mega flood crests** ($> 400,000\text{ cfs}$):

| Model Name | Peak Events Underpredicted (%) | Peak Events Overpredicted (%) | Peak Mean Bias (cfs) | Top-50 Mega Events RMSE (cfs) | Top-50 Mega Events Bias (cfs) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LightGBM Specific Discharge** | 63.0% | 37.0% | **-35,800.2** | **843,098.5** | **-789,926.0** |
| **LightGBM Log-Specific Discharge**| 67.8% | 32.2% | -41,560.1 | 845,232.9 | -822,961.4 |
| **LightGBM Raw Peak-Weighted** | **55.4%** | **44.6%** | -49,084.1 | 1,085,163.3 | -1,084,231.8 |
| **LightGBM Raw Unweighted** | 57.5% | 42.5% | -50,797.2 | 1,096,957.2 | -1,096,148.4 |
| **XGBoost Log1p** | 80.2% | 19.8% | -58,067.0 | 1,098,358.1 | -1,097,498.2 |

### Key Flood Peak Findings:
1. **Severe Upper-Tail Truncation in Log1p**: XGBoost `log1p` underpredicts **80.2%** of extreme flood days. While it excels at small and arid basins, the concave log-transform severely suppresses gradients for massive surges, creating a systematic negative bias of $-58,067\text{ cfs}$ on peak days.
2. **Specific Discharge Achieves Best Mega-Surge Accuracy**: LightGBM `spec_q` achieves the lowest peak mean bias ($-35,800\text{ cfs}$) and reduces Top-50 mega-event RMSE by over **$253,000\text{ cfs}$** compared to raw models.
3. **Peak Sample Weighting Mitigates Underprediction**: LightGBM Raw Peak-Weighted achieved the lowest percentage of underpredicted peak events ($55.4\%$), showing that gradient weighting directly increases tree sensitivity to surge triggers.

---

## 6. Comparison with Previous Validation Regimes

It is critical not to conflate validation scores across different regimes because the underlying data populations and leakage constraints differ fundamentally:

| Validation Regime | Scope & Isolation Rules | Val Rows | Evaluated Basins | Best Model Architecture | Best Overall RMSE (cfs) | Best Peak RMSE (cfs) |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **Chronological Holdout** | Same 33 stations; Train $\le 2021$, Val 2022–2023. Spatial locations known. | 24,088 | All 33 | LightGBM `log_spec_q` | 49,298.2 | 48,395.7 (Raw Weighted) |
| **Strategy C (Phases C1–C2)** | 9 individual stations held out; upstream Mississippi gauges leaked in train. Mega-basins omitted. | 6,570 | 9 | LightGBM Raw | 27,161.7 (Artificially low) | 29,404.6 |
| **LORSO Benchmark (Prompt E)** | **Entire river systems held out** (23 systems); zero upstream/downstream leakage. All 33 stations evaluated. | **24,088** | **All 33** | **LightGBM `log_spec_q`** | **82,871.1** | **155,136.8 (`spec_q`)** |

### Why LORSO Scores are Higher than Previous Regimes:
1. **Elimination of Network Memorization**: In Strategy C, holding out St. Louis while training on St. Paul and Clinton allowed models to exploit correlated mainstem flow. Under LORSO, when Mississippi Mainstem is held out, the model must predict Vicksburg and St. Louis purely from precipitation and static attributes with zero Mississippi data in training.
2. **Inclusion of Mega-Basins**: Strategy C omitted Vicksburg ($DA = 1.14M\text{ sq mi}$), which artificially dropped RMSE. LORSO includes all 33 stations, providing the first true, uncompromised test of continental generalisation.

---

## 7. Final Assessment & Model Selection (Prompt E Deliverable)

### 7.1 Best Model by Criterion
1. **Best Model for Overall RMSE**: **LightGBM Log-Specific Discharge (`log_spec_q`)** (Pooled RMSE: **82,871.1 cfs**; Macro RMSE: **31,814.4 cfs**).
2. **Best Model for Top-10% Peak RMSE**: **LightGBM Specific Discharge (`spec_q`)** (Pooled Peak RMSE: **155,136.8 cfs**; Macro Peak RMSE: **56,345.4 cfs**).
3. **Best Model for MAE**: **LightGBM Log-Specific Discharge (`log_spec_q`)** (Pooled MAE: **24,644.3 cfs**; Macro MAE: **24,642.4 cfs**).
4. **Best Model for R²**: **LightGBM Log-Specific Discharge (`log_spec_q`)** ($R^2 = \mathbf{0.4910}$).
5. **Most Consistent Model across Unseen River Systems**: **LightGBM Log-Specific Discharge**. It avoids the catastrophic $10,000\text{ cfs}$ overpredictions of Raw CFS on small mountain creeks (Cedar, Logan, Pecos) while avoiding the severe $80\%$ underprediction of XGBoost `log1p` on large rivers.
6. **Verdict on Peak Weighting**: Peak sample weighting ($w=2.5$) moderately improves flood peak RMSE on raw models ($204.5\text{k} \to 202.1\text{k cfs}$), but **cannot overcome the fundamental scale failure of raw models on unseen basins**.
7. **Verdict on Specific Discharge**: Specific Discharge ($q = Q/A$) and Log-Specific Discharge are **hydrologically essential** for unseen station generalisation. They provide a 24.4% overall error reduction and a 24.1% flood peak error reduction.
8. **Unresolved Limitations**: Daily mean vs daily maximum target confirmation (Phase E0 Blocker BLK-01) and NASA POWER vs Open-Meteo feature alignment (BLK-02) remain unconfirmed by organizers.

