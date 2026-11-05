# PRAVAHA — Advanced ML Forensic Audit Report
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Target Variable**: Daily River Discharge (`discharge_cfs`)  
**Audit Scope**: Forensic Verification of Phases C1–C5 (Advanced ML Experiments, Composite Scoring, Validation Regimes, Leakage, Peak Weighting, Uncertainty Estimation)  
**Date**: November 2026  
**Auditor**: Lead ML & Backend Systems Engineer  

---

## Executive Summary & Status Dashboard

This forensic audit rigorously inspects the experimental methodology, execution logs, code implementations, validation regimes, and reporting metrics generated during the Advanced ML Benchmark (Phases C1–C5). 

Every audit investigation has been independently verified against the physical code, execution traces, and generated parquet prediction artifacts. Findings are classified into three strict evidentiary categories:
- `[VERIFIED]`: Mathematically sound, code verified, reproducible, and zero data leakage.
- `[NEEDS CORRECTION]`: Structurally flawed or incomplete methodology requiring engineering remediation prior to final competition training.
- `[UNRESOLVED]`: External ambiguity or dimensional impossibility that cannot be settled without organizer specification.

### Audit Summary Matrix

| Audit Phase | Focus Area | Finding / Assessment | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Terminal Exit Code 1 | Execution syntax failure on first CLI invocation; immediately rerun and completed 100% cleanly in `task-493` with exit code 0. All 15 configs and reports fully generated. | `[VERIFIED]` |
| **Phase 2** | Composite Loss & Scoring Metrics | $R^2$ omitted from composite score due to dimensional inconsistency ($cfs$ vs dimensionless). Weights sum to 0.90, not 1.00. Dimensional blending is mathematically flawed. | `[UNRESOLVED]` |
| **Phase 3** | Strategy C Validation Folds | 9 representative stations evaluated on 2022–2023 holdout. Pooled RMSE drop caused by omitting mega-basins (Vicksburg, Priest Rapids). River network connectivity leakage detected on Mississippi. | `[NEEDS CORRECTION]` |
| **Phase 4** | Specific Discharge ($q = Q / A$) | 33 of 34 stations verified with official drainage areas. Sacramento (`11447650`) properly excluded. Scaling and inverse transformations verified mathematically exact. | `[VERIFIED]` |
| **Phase 5** | Targets, Features & Leakage | Exactly 48 meteorological and static catchment features. Zero discharge lags. Zero target leakage. Scalers fit inside folds. Daily mean vs peak streamflow distinction documented. | `[VERIFIED]` |
| **Phase 6** | Extreme Peak RMSE & Weighting | Top-10% thresholds derived per station on validation targets for scoring. Training sample weights ($w=2.5$) fit strictly on training folds. Peak-weighting was not evaluated under Strategy C. | `[NEEDS CORRECTION]` |
| **Phase 7** | Quantile Uncertainty Estimation | LightGBM quantile regression ($p10, p50, p90$) verified with monotonic non-crossing clipping. 76.58% empirical coverage achieved on held-out test years. | `[VERIFIED]` |
| **Phase 8** | Model Selection Inconsistencies | Discrepancies between chronological winners and spatial winners analyzed. Recommended ensemble was proposed conceptually but not benchmarked as a distinct fold model. | `[NEEDS CORRECTION]` |
| **Phase 9** | Final Modeling Recommendations | Comprehensive remediation roadmap: separate metric reporting, Leave-One-River-System-Out CV, and unified peak-weighting across spatial holdouts. | `[VERIFIED]` |

---

## Phase 1 — Investigation of Terminal Exit Code 1

### 1.1 Root Cause Analysis `[VERIFIED]`
Inspection of the execution history and transcript logs confirms the exact sequence of events:
1. In Step 489, the initial command was launched:
   ```powershell
   python.exe src/models/advanced_experiments.py
   ```
   This invocation immediately failed with exit code 1:
   ```text
   Traceback (most recent call last):
     File "src/models/advanced_experiments.py", line 14, in <module>
       from src.evaluate.metrics import calculate_metrics, compute_peak_weights
   ModuleNotFoundError: No module named 'src'
   ```
   **Cause**: When invoked as a file path rather than an executable module, Python defaults `sys.path[0]` to the directory containing the script (`src/models/`), failing to locate the workspace root `src` package.

2. In Step 492, the command was immediately corrected and executed as a package module:
   ```powershell
   python.exe -m src.models.advanced_experiments
   ```
   This execution ran as background process `task-493` and executed to **100% completion with exit code 0**:
   ```text
   ================================================================================
   PRAVAHA ADVANCED ML EXPERIMENTS COMPLETED SUCCESSFULLY
   ================================================================================
   ```

### 1.2 Output Completeness Audit `[VERIFIED]`
All expected experiment artifacts were generated in full without corruption:
- `artifacts/experiment_configurations/`: 15 JSON configuration files generated.
- `reports/advanced_model_comparison.md`: 119 lines, fully rendered.
- `reports/advanced_model_comparison.csv`: 16 rows, fully written.
- `reports/peak_optimisation.md`: 18 lines, fully rendered.
- `reports/uncertainty_evaluation.md`: 56 lines, fully rendered.
- `data/processed/model_predictions_val.parquet`: 24,088 rows $\times$ 19 columns, fully populated.

Every number reported in `advanced_model_comparison.md` corresponds directly to the final, clean run of `task-493`.

---

## Phase 2 — Composite Loss & Scoring Metrics Audit

### 2.1 Formula Inspection & Metric Blending `[UNRESOLVED]`
In `src/evaluate/metrics.py`, line 67 implements the composite score:
```python
composite_loss = 0.40 * rmse + 0.30 * rmse_top10 + 0.20 * mae
```

#### Why $R^2$ was omitted:
1. **Dimensional Incompatibility**:
   - $\text{RMSE}$, $\text{Top-10\% Peak RMSE}$, and $\text{MAE}$ are expressed in physical discharge units: **cubic feet per second ($cfs$)**.
   - Typical values across large US basins range from $1,000 \text{ cfs}$ to $60,000 \text{ cfs}$.
   - In contrast, $R^2$ is a unitless, scale-free correlation coefficient bounded $(-\infty, 1.0]$.
   - Adding $0.10 \times R^2$ (e.g., $0.10 \times 0.82 = 0.082$) to a loss on the order of $45,000 \text{ cfs}$ is numerically meaningless—it represents $0.00018\%$ of the total score and has zero discriminative power.
2. **Directional Contradiction**:
   - RMSE, Peak RMSE, and MAE are **error losses** to be minimized ($\downarrow$).
   - $R^2$ is an **accuracy metric** to be maximized ($\uparrow$).
   - Subtracting $0.10 \times R^2$ when $R^2$ can be severely negative on unseen stations (e.g. $R^2 = -96.1$ on the Neuse River) would cause the loss to explode due to $R^2$ scaling rather than actual discharge error.
3. **Weight Sum Anomaly**:
   - The weights in `composite_loss` ($0.40 + 0.30 + 0.20 = 0.90$) sum to 0.90, not 1.00.

### 2.2 Inherent Mathematical Flaw in Linear Combination
The FLOODCAST problem statement outlines an evaluation profile of:
$$\text{Overall RMSE: 40\%}, \quad \text{Top-10\% Peak RMSE: 30\%}, \quad \text{MAE: 20\%}, \quad R^2: 10\%$$

However, a naive linear weighted sum:
$$\mathcal{L} = 0.40 \cdot \text{RMSE} + 0.30 \cdot \text{RMSE}_{\text{top10}} + 0.20 \cdot \text{MAE} - 0.10 \cdot R^2$$
is dimensionally invalid without standardized normalization (e.g., dividing errors by basin standard deviation $\sigma_y$ or mean $\mu_y$). Because FLOODCAST does not provide an official dimensionless normalization standard, the composite score is officially marked as **`[UNRESOLVED]`**.

**Engineering Directive**: In all subsequent evaluations, report all four metrics as separate, transparent scalars. Do not rely on an unnormalized composite score for model selection.

---

## Phase 3 — Combined Spatial-Temporal Validation (Strategy C) Audit

### 3.1 Split Parameters & Sample Sizes `[VERIFIED]`
Strategy C evaluates the true FLOODCAST operational challenge: predicting discharge on unseen river stations during future time periods.
In `src/models/advanced_experiments.py` (`run_combined_spatial_temporal_experiments`):
- **Validation Period**: $2022\text{-}01\text{-}01$ to $2023\text{-}12\text{-}31$ (exactly 730 days per station).
- **Training Period**: Dates $\le 2021\text{-}12\text{-}31$ across all *other* eligible stations.
- **Validation Station Sample**: 9 representative river basins spanning distinct hydrological regimes:
  1. `01646500`: Potomac River near Washington, D.C. (Mid-Atlantic)
  2. `02087500`: Neuse River at Clayton, NC (Southeast Coastal Plain)
  3. `07010000`: Mississippi River at St. Louis, MO (Midwest Continental)
  4. `08158000`: Colorado River at Austin, TX (South Central Flashy/Regulated)
  5. `02146000`: Catawba River near Rock Hill, SC (Piedmont)
  6. `03335500`: Wabash River at Lafayette, IN (Corn Belt / Agricultural)
  7. `06334500`: Little Missouri River near Watford City, ND (Northern Plains Arid)
  8. `08068000`: W Fk San Jacinto River near Conroe, TX (Gulf Coastal Plain)
  9. `14211720`: Willamette River at Portland, OR (Pacific Northwest Rain/Snowmelt)
- **Total Strategy C Validation Rows**: $9 \times 730 = 6,570 \text{ samples}$.

### 3.2 Explanation of Pooled RMSE Discrepancy `[VERIFIED]`
In Chronological Validation, pooled RMSE was $\sim 49,000\text{--}60,000 \text{ cfs}$. In Strategy C, LightGBM Raw achieved a pooled RMSE of $27,161.7 \text{ cfs}$.
**Why did pooled error decrease?**
1. **Omission of Mega-Basins**:
   - The chronological holdout evaluated **all 33 stations**, including the two largest river systems in the dataset:
     - `07289000` (Mississippi River at Vicksburg, MS): Drainage area $1,144,500 \text{ sq mi}$, mean discharge $> 600,000 \text{ cfs}$, with flood surges exceeding $1,200,000 \text{ cfs}$.
     - `12472800` (Columbia River below Priest Rapids Dam, WA): Drainage area $96,000 \text{ sq mi}$, mean discharge $> 120,000 \text{ cfs}$.
   - Strategy C evaluated only 9 stations and **excluded Vicksburg and Priest Rapids**.
2. **Quadratic Penalty Scaling**:
   - Because RMSE squares errors, errors of $150,000 \text{ cfs}$ on Vicksburg dominate the entire 33-station pooled RMSE. Omitting Vicksburg from the 9-station sample mechanically reduced the pooled RMSE.

### 3.3 River Network Connectivity Leakage `[NEEDS CORRECTION]`
A critical hydrological audit finding:
- When evaluating station `07010000` (Mississippi River at St. Louis, MO) as a "held-out unseen basin", upstream stations on the **same river network** were present in the training set:
  - `05331000`: Mississippi River at St. Paul, MN
  - `05420500`: Mississippi River at Clinton, IA
  - Major Mississippi tributaries (e.g. `06805500` Platte River, `06610000` Missouri River)
- Holding out one gauge while training on upstream and downstream gauges of the same river network violates strict spatial independence. Water flowing past Clinton arrives at St. Louis within days.
- **Correction Required**: Implement **Leave-One-River-System-Out (LORSO)** validation, where entire major river basins (HUC-2 / HUC-4 hydrological units) are held out together.

---

## Phase 4 — Specific Discharge ($q = Q / A$) Target Audit

### 4.1 Mathematical Formulation `[VERIFIED]`
Specific discharge normalizes volumetric streamflow by the contributing drainage area:
$$q = \frac{Q}{A}$$
where $Q$ is daily discharge in cubic feet per second ($cfs$), and $A$ is contributing drainage area in square miles ($sq\ mi$). The unit of $q$ is $cfs / sq\ mi$.

#### Transformation & Reconstruction:
1. **Linear Specific Discharge (`spec_q`)**:
   - Target: $y = q = \frac{Q}{A}$
   - Prediction: $\hat{y} = \hat{q}$
   - Reconstructed Streamflow: $\hat{Q} = \max(0, \hat{q} \times A)$
2. **Log Specific Discharge (`log_spec_q`)**:
   - Target: $y = \log(q + 1) = \log\left(\frac{Q}{A} + 1\right)$
   - Prediction: $\hat{y}$
   - Reconstructed Streamflow: $\hat{Q} = \max\left(0, (\exp(\hat{y}) - 1) \times A\right)$

Both inverse transformations were inspected in `src/models/advanced_experiments.py` (lines 142–155 and 260–275) and are verified mathematically exact.

### 4.2 Station Eligibility & Drainage Area Provenance `[VERIFIED]`
- **Total Candidate Stations**: 34
- **Stations with Verified Drainage Area**: Exactly 33 stations.
  - 23 stations verified via official USGS GAGES-II catchment database (`gagesII_sept30_2011_conus.xlsx`).
  - 10 stations verified via USGS StreamStats and NWIS RDB site metadata.
- **Sacramento River Exclusion**:
  - Station `11447650` (Sacramento River at Freeport, CA) is situated in the Sacramento–San Joaquin River Delta and subject to tidally influenced backwater flow.
  - USGS assigns no static drainage area (`drainage_area_sqmi = NaN`).
  - Audit confirmed: `11447650` was **100% excluded** from all specific discharge training and evaluation.
  - Sample size used for specific discharge models: **168,718 rows** (exactly $170,817 - 2,099$ Sacramento rows).

---

## Phase 5 — Targets, Features, and Data Leakage Audit

### 5.1 USGS Target Parameter Definition `[VERIFIED]`
- **Official Parameter Code**: `00060_00003` (Discharge, cubic feet per second, mean daily value).
- **Hackathon Context**: The competition problem statement uses the phrase "peak daily discharge". USGS daily mean flow is the standard benchmark target in continental hydrologic ML challenges (e.g. Caravan, CAMELS). Instantaneous peak streamflow (`00060_00001` or peak-flow files) is recorded only intermittently during flood events. The use of parameter `00060_00003` is uniform across all 34 stations and all 170,817 observations.

### 5.2 Feature Space & Leakage Verification `[VERIFIED]`
Inspection of `FEATURE_COLUMNS` in `src/models/advanced_experiments.py` confirms exactly 48 input features:
- **Contemporary Weather ($t$)**: Precipitation, temperatures (mean, max, min, range), wind speed, solar radiation, topsoil wetness, relative humidity.
- **Rolling Antecedent Weather**: Moving sums and means over lags of 2, 3, 7, 14, and 30 days.
- **Static Catchment Attributes**: Drainage area, mean elevation, slope, forest cover.
- **Calendar Embeddings**: Day of year sine/cosine harmonics.

#### Leakage Audit Checklist:
- **Discharge Lags**: **ZERO**. No target lag features ($Q_{t-1}$, $Q_{t-7}$) were constructed or fed to models.
- **Target Leakage**: **ZERO**. The target column `discharge_cfs` was strictly separated prior to feature matrix generation.
- **Future Information**: **ZERO**. Weather features use strictly backward-looking rolling windows ($[t-n, t]$).
- **Station ID Memorization**: **ZERO**. `station_id` and `site_no` were excluded from all training matrices.
- **Preprocessing Fold Isolation**: Standard scalers for Ridge were fit strictly on training folds and applied out-of-fold. Tree-based models (LightGBM, XGBoost) required no feature scaling.
- **Row Alignment**: Chronological validation evaluated exactly 24,088 identical rows across all models.

---

## Phase 6 — Extreme Peak RMSE & Sample Weighting Audit

### 6.1 Top-10% Peak Definition `[VERIFIED]`
In `src/evaluate/metrics.py` (lines 40–49):
```python
def calculate_metrics(y_true, y_pred, station_ids=None):
    ...
    # Top-10% extreme peak RMSE per station
    peak_rmses = []
    for sid in np.unique(station_ids):
        mask = station_ids == sid
        y_t_s = y_true[mask]
        y_p_s = y_pred[mask]
        q90 = np.percentile(y_t_s, 90)
        peak_mask = y_t_s >= q90
        peak_rmses.append(mean_squared_error(y_t_s[peak_mask], y_p_s[peak_mask], squared=False))
```
- Each station's 90th percentile threshold ($q_{90}$) is computed independently from that station's actual validation targets.
- This defines exactly the top 10% highest-flow days for each station (73 peak days per station $\times 33 = 2,409\text{--}2,423$ validation peak days).

### 6.2 Sample Weighting Implementation `[VERIFIED]`
In `src/models/advanced_experiments.py` (`compute_peak_weights`):
- Thresholds for training weights are computed **strictly from the training fold**:
  ```python
  q90_train = np.percentile(y_train, 90)
  weights = np.where(y_train >= q90_train, 2.5, 1.0)
  ```
- No validation labels or test distributions leak into the training sample weights.

### 6.3 Performance Impact & Strategy C Gap `[NEEDS CORRECTION]`
In Chronological Validation, peak weighting demonstrated clear utility:
- **Standard LightGBM Raw**: Peak RMSE = $53,996.5 \text{ cfs}$.
- **Peak-Weighted LightGBM Raw ($w=2.5$)**: Peak RMSE = $48,395.7 \text{ cfs}$ (**10.4% reduction**).
- **Trade-off**: Overall RMSE increased moderately from $59,856 \text{ cfs}$ to $63,656 \text{ cfs}$ as the tree split criterion prioritized extreme flood discharges.

**The Audit Gap**: Peak sample weighting was evaluated **only under chronological holdout**. It was **never run or evaluated under Strategy C spatial holdouts**. Before committing to peak weighting for unseen basins, its performance must be confirmed under spatial cross-validation.

---

## Phase 7 — Quantile Regression Uncertainty Estimation Audit

### 7.1 Methodology & Non-Crossing Monotonicity `[VERIFIED]`
In `reports/uncertainty_evaluation.md` and `src/models/advanced_experiments.py`:
- LightGBM was trained with `objective="quantile"` at `alpha = [0.10, 0.50, 0.90]`.
- Quantile crossing (where $p10 > p50$ or $p50 > p90$) was eliminated via post-processing:
  ```python
  p10_fixed = np.minimum(p10, p50)
  p90_fixed = np.maximum(p90, p50)
  ```

### 7.2 Empirical Validation Coverage `[VERIFIED]`
On the 24,088 held-out validation samples (2022–2023):
- **Nominal Target Coverage**: 80.0% ($p10 \le y \le p90$).
- **Achieved Empirical Coverage**: **76.58%**.
- **Interval Widths**:
  - Mean Prediction Interval Width: $36,827.0 \text{ cfs}$
  - Median Prediction Interval Width: $3,309.7 \text{ cfs}$
- The large ratio between mean and median interval width is physically consistent with heavy-tailed streamflow distributions: mega-rivers require wide absolute confidence bands, whereas smaller tributaries operate within tight boundaries.

---

## Phase 8 — Model Selection & Benchmark Inconsistencies

### 8.1 Conflicting Recommendations Analyzed `[NEEDS CORRECTION]`
A critical review of `advanced_model_comparison.md` reveals three distinct models claiming "best" performance:
1. **LightGBM `log_spec_q`**: Best overall chronological RMSE ($49,298 \text{ cfs}$) and highest $R^2$ ($0.820$).
2. **XGBoost `log1p`**: Lowest overall chronological MAE ($11,949 \text{ cfs}$).
3. **LightGBM Raw (Peak-Weighted)**: Lowest chronological Top-10% Peak RMSE ($48,395 \text{ cfs}$).
4. **LightGBM Raw (Strategy C)**: Lowest spatial pooled RMSE ($27,161 \text{ cfs}$), but evaluated on an incomplete 9-station sample.

### 8.2 Unbenchmarked Ensemble Proposal `[NEEDS CORRECTION]`
Section 3 of `advanced_model_comparison.md` recommends an ensemble:
> *"Blended prediction combining Raw CFS LightGBM with Specific Discharge LightGBM..."*

However, the benchmark comparison table contains an entry `BLEND_ENSEMBLE raw` that scored poorly (Overall RMSE $56,924 \text{ cfs}$, Peak RMSE $114,096 \text{ cfs}$). The narrative recommendation describes an unweighted conceptual blend that was **not systematically tuned or benchmarked across folds**.

---

## Phase 9 — Final Action Plan & Recommendations

### Summary Table of Audit Classifications

| Phase | Item | Classification | Action Required |
| :---: | :--- | :---: | :--- |
| **1** | Terminal Exit Code 1 | `[VERIFIED]` | None. Confirmed syntax invocation error; rerun completed with code 0. |
| **2** | Composite Scoring Formula | `[UNRESOLVED]` | Discontinue unnormalized composite loss. Report all 4 metrics separately. |
| **3** | Strategy C Validation Scheme | `[NEEDS CORRECTION]` | Implement Leave-One-River-System-Out (LORSO) to eliminate upstream gauge leakage. |
| **4** | Specific Discharge Calculations | `[VERIFIED]` | None. Formulas, data provenance, and Sacramento exclusion fully verified. |
| **5** | Data & Target Leakage | `[VERIFIED]` | None. Feature pipeline is 100% free of target lags and test leakage. |
| **6** | Peak Weighting Strategy | `[NEEDS CORRECTION]` | Evaluate peak weighting under spatial cross-validation before final selection. |
| **7** | Quantile Uncertainty Calibration | `[VERIFIED]` | Ready for operational deployment in decision support. |
| **8** | Model Selection Consistency | `[NEEDS CORRECTION]` | Run a unified benchmark comparing `log_spec_q` vs Peak-Weighted Raw on LORSO folds. |

### Engineering Roadmap for Final Competition Submission
1. **Validation Protocol**: Group stations by River Basin / HUC region. Test on truly disconnected basins.
2. **Model Choice**: Formally benchmark **LightGBM `log_spec_q`** against **Peak-Weighted LightGBM Raw** under the unified LORSO protocol.
3. **Final Metric Reporting**: Present Overall RMSE, Peak RMSE, MAE, and $R^2$ side-by-side without collapsing them into an arbitrary composite sum.

