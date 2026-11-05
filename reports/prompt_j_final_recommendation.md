# PRAVAHA — Final Model Accuracy Verdict & Operational Recommendation

**Protocol Reference**: PROMPT J  
**Evaluation Role**: Senior Machine Learning Engineer & Independent Evaluation Specialist  
**Target Target**: USGS Daily Mean Discharge (`00060`, Statistic `00003`, Unit: CFS)  
**Evaluation Methodology**: Leave-One-River-System-Out (LORSO) Spatial Holdout Cross-Validation  
**Holdout Set**: 33 Stations, 24,088 Station-Days (2022–2023)  

---

## 1. Phase 8: Answers to Core Evaluation Questions

### 1. Which existing model is best overall?
**Answer**: **`LightGBM log_spec_q` (Log-Specific Discharge)**.  
It achieves the lowest Overall RMSE (**$82,871.13\text{ cfs}$**), lowest Overall MAE (**$24,644.29\text{ cfs}$**), highest Pooled $R^2$ (**$0.4910$**), and lowest Macro RMSE across stations (**$31,814.42\text{ cfs}$**).

### 2. Which is best for extreme events?
**Answer**: **`LightGBM spec_q` (Linear Specific Discharge)**.  
It achieves the lowest Top-10% Peak RMSE (**$155,136.83\text{ cfs}$** vs $156,593.84\text{ cfs}$), lowest Peak MAE (**$74,120.45\text{ cfs}$**), lowest Peak Underprediction Bias (**$-35,800.22\text{ cfs}$**), and wins on 18 of 33 individual stations during peak flows.

### 3. Which produces the lowest MAE?
**Answer**: **`LightGBM log_spec_q`** with an Overall MAE of **$24,644.29\text{ cfs}$**, outperforming `spec_q` ($26,091.96\text{ cfs}$) and XGBoost ($28,995.81\text{ cfs}$).

### 4. Which has the highest pooled $R^2$?
**Answer**: **`LightGBM log_spec_q`** with a Pooled $R^2$ of **$0.4910$** ($49.10\%$ variance explained), followed by `spec_q` ($0.4411$).

### 5. Which is most consistent across unseen stations?
**Answer**: **`LightGBM log_spec_q`**.  
In station-by-station head-to-head testing, `log_spec_q` wins **20 of the 33 individual stations** on RMSE and MAE, and achieves the lowest Macro RMSE ($31,814.42\text{ cfs}$).

### 6. How much does it improve over the baseline?
**Answer**:
- **$+28.99\%$ RMSE Improvement** over the Global Mean baseline ($116,711.28\text{ cfs} \to 82,871.13\text{ cfs}$).
- **$+21.06\%$ RMSE Improvement** over out-of-system LORSO Ridge regression ($104,979.70\text{ cfs} \to 82,871.13\text{ cfs}$).

### 7. What are its biggest weaknesses?
**Answer**:
1. **Upper-Tail Peak Underprediction**: Compressing flow into logarithmic space ($\log(q + 1)$) penalizes relative errors, causing the model to underestimate **$67.8\%$ of extreme flood peaks** by an average of $-41,560\text{ cfs}$.
2. **Arid Basin Sensitivity**: On dry Southwestern rivers with massive transmission losses (e.g. Pecos River `08378500`, Texas Colorado at Austin `08158000`), the model overestimates flow because local rainfall does not produce overland runoff.
3. **Mega-Basin Scaling**: At Vicksburg (`07289000`), local meteorological inputs cannot capture flood crests originating 1,000 miles upstream weeks earlier.

### 8. Is it ready for further final model development?
**Answer**: **Yes.**  
`LightGBM log_spec_q` is a thoroughly verified, mathematically stable, and leakage-free architecture. Furthermore, the Prompt I experiments demonstrated that combining **14-day antecedent rainfall memory** with **controlled 2.5x peak sample weighting** directly overcomes its upper-tail weakness, reducing Overall RMSE to **$73,793.15\text{ cfs}$** and Top-10% Peak RMSE to **$128,552.56\text{ cfs}$**.

---

## 2. Operational Distinctions: Validation vs. Future Forecasting

> [!IMPORTANT]
> **Historical Validation $\ne$ Future Operational Forecasting:**
> 1. **Historical Validation (Reported Here)**: Measures model skill when provided actual historical reanalysis weather observations over held-out river systems (2022–2023).
> 2. **Operational Future Forecasting**: When deploying the model for a 7-day forward flood forecast, the model is driven by **numerical weather prediction (NWP) forecasts** (e.g., NOAA GFS, HRRR). Forward accuracy will naturally reflect weather forecast uncertainty.
> 3. **Unlabelled Competition Test Set**: If the official competition test set has no ground-truth discharge labels, actual test accuracy **cannot yet be empirically measured** until official test labels are released or evaluated on the competition scoring server.

---

## 3. Recommended Production Hierarchy

1. **Primary Operational Engine**: `LightGBM log_spec_q` (with 14-day antecedent rainfall memory and 2.5x peak weighting from Prompt I).
2. **Flood Alarm / Surge Branch**: `LightGBM spec_q` (retained for upper-tail flood peak verification).
3. **Safety Protocol**: All operational forecasts must include an uncertainty band ($\pm 30\%$) and regional flood warning disclaimers on regulated dams and mega-basins.

