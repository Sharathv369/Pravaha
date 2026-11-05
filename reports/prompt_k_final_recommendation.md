# PRAVAHA — PROMPT K: FINAL MODEL RECOMMENDATION MEMO

**To:** PRAVAHA Lead Engineering & Hydrological Modeling Team  
**From:** Senior Hydrological Machine Learning Researcher & Model Evaluation Specialist  
**Subject:** Advanced ML Accuracy Optimization — Final Architecture Recommendation  
**Date:** November 2026  
**Status:** DEFINITIVE RECOMMENDATION BASED ON EMPIRICAL EVIDENCE  

---

## 1. EXISTING CHAMPION PERFORMANCE (PROMPT I BASELINE)

The incumbent champion model established in Prompt I was independently re-evaluated on raw data across the full 23-fold Leave-One-River-System-Out (LORSO) canonical 2022–2023 benchmark (24,088 station-days across 33 stations):

- **Algorithm:** LightGBM Regressor (`LGBMRegressor`)
- **Target Formulation:** `log_spec_q` ($\log(\text{discharge} / \text{drainage\_area} + 1.0)$)
- **Feature Set:** `FEATURE_SET_C_14D` (27 meteorological, calendar, static catchment, and 3d/7d/14d antecedent rainfall features)
- **Peak Sample Weighting:** $2.5\times$ applied to observations where $y_{\text{train}} \ge q_{90}$
- **Audited Metrics:**
  - **Pooled $R^2$:** `0.5964` (59.64% variance explained)
  - **Overall RMSE:** `73,793.15 CFS`
  - **Top-10% Peak RMSE:** `128,552.56 CFS`
  - **Macro Station RMSE:** `29,764.24 CFS`
  - **Mean Absolute Error (MAE):** `22,887.18 CFS`
  - **Peak Underprediction Frequency:** `68.8%` (1,667 of 2,423 flood days)
  - **Peak Bias:** `-32,349.15 CFS`

---

## 2. BEST NEWLY TESTED MODEL

The strongest performing newly evaluated architecture across both internal development cross-validation and the canonical benchmark is:

- **Model ID:** `CANDIDATE_B_3.5X`
- **Algorithm:** LightGBM Regressor (`LGBMRegressor`)
- **Target Formulation:** `log_spec_q`
- **Feature Set:** `FEATURE_SET_C_14D` (27 features)
- **Peak Sample Weighting:** **$3.5\times$** (increased from $2.5\times$, applied strictly where $y_{\text{train}} \ge q_{90}$)
- **Canonical Benchmark Results:**
  - **Pooled $R^2$:** **`0.6090`** (60.90% variance explained)
  - **Overall RMSE:** **`72,626.35 CFS`**
  - **Top-10% Peak RMSE:** **`127,638.27 CFS`**
  - **Macro Station RMSE:** **`29,455.65 CFS`**
  - **Peak Underprediction Frequency:** **`66.9%`**
  - **Peak Bias:** **`-30,665.96 CFS`**

---

## 3. DID $R^2$ IMPROVE?

**YES.**  
- Incumbent $R^2$: `0.5964`
- Candidate $3.5\times$ $R^2$: `0.6090`
- **Absolute Gain:** **$+0.0126$** ($+1.26$ percentage points of variance explained).
- **Relative Gain:** **$+2.11\%$**.

*Note on the $R^2 \ge 0.65$ Target:*  
On the internal development holdout (2020–2021), this architecture achieved $R^2 = 0.7778$, comfortably exceeding 0.65. However, on the canonical 2022–2023 unseen river systems, $R^2$ reached `0.6090`. In accordance with scientific integrity guidelines, this is reported honestly: $R^2 \ge 0.65$ is not yet achieved on the canonical out-of-system benchmark without direct dam-release telemetry.

---

## 4. DID OVERALL RMSE IMPROVE?

**YES.**  
- Incumbent Overall RMSE: `73,793.15 CFS`
- Candidate $3.5\times$ Overall RMSE: `72,626.35 CFS`
- **Net Improvement:** **$-1,166.80\text{ CFS}$** ($1.58\%$ error reduction across the entire 24,088-day population).

---

## 5. DID PEAK RMSE IMPROVE?

**YES.**  
- Incumbent Peak RMSE: `128,552.56 CFS`
- Candidate $3.5\times$ Peak RMSE: `127,638.27 CFS`
- **Net Improvement:** **$-914.29\text{ CFS}$** ($0.71\%$ peak error reduction).
- Concurrently, the peak underprediction frequency dropped from `68.8%` to `66.9%` (a net reduction of 46 underpredicted flood days), and peak underprediction bias improved by **$+1,683.19\text{ CFS}$**.

---

## 6. DID SPATIAL GENERALIZATION IMPROVE?

**YES.**  
- **Macro Station RMSE:** Improved from `29,764.24 CFS` to `29,455.65 CFS` (**$-308.59\text{ CFS}$**).
- **Station-Level Win Rate:** Out of 33 unseen gauging stations, the $3.5\times$ model reduced RMSE on **21 stations** ($63.6\%$ of all stations).
- **Major Regional Wins:**
  - Missouri River System (Platte River at Louisville): $-14,004.2\text{ CFS}$ RMSE reduction.
  - Mississippi River Mainstem (St. Paul): $-2,619.7\text{ CFS}$ RMSE reduction ($R^2$ turned from $-0.01$ to $+0.24$).
  - Red River (Index, AR): $-1,624.7\text{ CFS}$ RMSE reduction.
  - Susquehanna River: $-723.1\text{ CFS}$ RMSE reduction.

---

## 7. DID THE IMPROVEMENT SURVIVE THE CANONICAL 2022–2023 BENCHMARK?

**YES.**  
The $3.5\times$ loss weight was identified as the winning configuration exclusively on the pre-2022 internal development split (2020–2021 holdout). When deployed strictly once to the canonical 2022–2023 test set, the improvement transferred consistently:

```
Metric                 Incumbent (2.5x)    Candidate (3.5x)      Delta / Change
Pooled R²                   0.5964              0.6090           +0.0126 (+2.11%)
Overall RMSE (CFS)       73,793.15           72,626.35           -1,166.80 CFS
Peak RMSE (CFS)         128,552.56          127,638.27             -914.29 CFS
Macro Station RMSE       29,764.24           29,455.65             -308.59 CFS
Peak Underprediction         68.8%               66.9%           -1.9% absolute
Peak Bias (CFS)         -32,349.15          -30,665.96           +1,683.19 CFS
```

---

## 8. SHOULD THE NEW MODEL REPLACE PROMPT I?

**YES, RECOMMEND REPLACEMENT.**

### Justification:
1. **Pareto Dominance:** The $3.5\times$ peak-weighted model strictly dominates the Prompt I $2.5\times$ model across every primary metric: higher $R^2$, lower overall RMSE, lower peak RMSE, lower macro station RMSE, and reduced underprediction frequency.
2. **Zero Deployment Risk:** It utilizes the exact same feature engineering pipeline (`FEATURE_SET_C_14D`, 27 features), same API schema, and same LightGBM inference latency (sub-millisecond per station). No new third-party dependencies or external API calls are introduced.
3. **No Retuning Penalty:** It requires changing only one scalar configuration parameter in the training pipeline: `peak_weight = 3.5`.

---

## 9. REMAINING LIMITATIONS & RECOMMENDED NEXT STEPS

While the $3.5\times$ model establishes a new accuracy frontier for pure meteorology-driven discharge prediction ($R^2 = 0.6090$), clear physical ceilings remain:

1. **Dam Regulation & Reservoir Decoupling:**
   - Basins like the Texas Colorado at Austin (`08158000`) and the Colorado at Lees Ferry (`09380000`) exhibit negative station $R^2$ because discharge is governed by reservoir gate operations rather than rainfall-runoff dynamics.
   - *Recommendation:* Incorporate USACE / Bureau of Reclamation reservoir storage anomalies or a binary dam-regulation flag as conditioning inputs.
2. **Continental Wave Attenuation & Travel Times:**
   - At Vicksburg, MS (`07289000`), flow represents the cumulative lag of a million-square-mile catchment spanning multiple weeks. 14-day rainfall sums capture only a fraction of the upstream transit time.
   - *Recommendation:* Introduce a simplified Muskingum hydrologic routing proxy or upstream gauged tributary lagged stages into the model graph.
3. **High-Resolution Forcing (ERA5-Land / HRRR / Open-Meteo):**
   - NASA POWER provides 0.5-degree gridded daily meteorology, which smooths convective storm peaks in mountainous or small catchments.
   - *Recommendation:* When high-resolution Open-Meteo or NWM reanalysis becomes fully ingested, benchmark the $3.5\times$ architecture on finer spatial forcings.

---

**Signed,**  
*Senior Hydrological Machine Learning Researcher & Evaluation Specialist*  
*PRAVAHA Core ML Systems Team*

