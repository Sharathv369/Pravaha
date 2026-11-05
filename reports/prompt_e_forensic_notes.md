# PRAVAHA — Prompt E Forensic Engineering Notes
**Project**: PRAVAHA — FLOODCAST Hackathon  
**Deliverable**: Phase E8 Forensic Engineering Documentation  
**Date**: November 2026  
**Auditor & Systems Engineer**: Lead ML & Backend Systems Engineer  

---

## 1. Execution Log & Pipeline Traceability

The complete Leave-One-River-System-Out (LORSO) validation benchmark was executed via `src/models/prompt_e_lorso_benchmark.py`:
- **Execution Runtime**: 154.50 seconds (~2.57 minutes) across all 23 folds.
- **Total Model Fits**: $23 \times 5 = 115$ independent model fits (LightGBM and XGBoost).
- **Total Predictions Generated**: Exactly **120,440 predictions** ($24,088\text{ rows} \times 5\text{ models}$).
- **Parquet Storage**: Saved to `data/processed/prompt_e_validation_predictions.parquet` (compressed size: ~2.1 MB).
- **Exit Status**: 100% clean termination with code 0 (zero memory errors, zero missing values, zero NaN predictions).

---

## 2. Zero-Leakage & Data-Integrity Audit Checklist

| Audit Check | Verification Evidence | Status |
| :--- | :--- | :---: |
| **Zero Target Leakage in Features** | `FEATURE_COLUMNS` contains exactly 48 verified columns: meteorological measurements, backward-looking rolling sums/means, static catchment attributes, and calendar cyclical transforms. Zero discharge variables ($Q_t, Q_{t-1}, Q_{t-k}$) were included. | `[VERIFIED]` |
| **Strict Out-of-System Split** | In every fold $k$, every station belonging to river system $k$ was excluded from the training split. | `[VERIFIED]` |
| **Strict Out-of-Time Split** | All training observations were strictly restricted to $\text{date} \le 2021\text{-}12\text{-}31$. Validation was evaluated strictly on $2022\text{-}01\text{-}01$ to $2023\text{-}12\text{-}31$. | `[VERIFIED]` |
| **Sample Weight Calculation** | Peak sample weights ($w=2.5$) for Model B were calculated strictly from `df_train` targets per training station. Zero validation labels were accessed during weight derivation. | `[VERIFIED]` |
| **Evaluation Threshold Isolation** | Top-10% flow thresholds ($q_{90}$) were calculated per held-out station solely on validation labels for offline scoring, never seen by models. | `[VERIFIED]` |
| **Specific Discharge Drainage Areas** | 33 of 33 validation stations have verified drainage areas from GAGES-II (23 stations) and StreamStats/NWIS (10 stations). Zero synthetic drainage areas were used. | `[VERIFIED]` |
| **Sacramento River Integrity** | Station `11447650` (Sacramento at Freeport) had records only through 2015-09-30 (2,099 rows). It had 0 rows in the 2022–2023 validation period. It was excluded from specific-discharge training due to unindexed tidal drainage area, maintaining 100% data fidelity. | `[VERIFIED]` |

---

## 3. Hydrological Regime Deep-Dive: Why Models Won or Lost

### 3.1 The "Cedar River Catastrophe" in Raw Models
- **Station**: `12119000` (Cedar River at Renton, WA).
- **Physical Characteristics**: Drainage area $173.1\text{ sq mi}$, mean streamflow $\sim 200\text{--}500\text{ cfs}$.
- **Performance**:
  - LightGBM Raw Unweighted RMSE: **$10,645.0\text{ cfs}$** ($R^2 = -391.8$)
  - LightGBM Raw Peak-Weighted RMSE: **$10,664.4\text{ cfs}$** ($R^2 = -393.2$)
  - LightGBM Specific Discharge RMSE: **$581.0\text{ cfs}$** ($R^2 = 0.528$)
  - LightGBM Log-Specific Discharge RMSE: **$599.6\text{ cfs}$** ($R^2 = 0.501$)
  - XGBoost Log1p RMSE: **$470.2\text{ cfs}$** ($R^2 = 0.693$)
- **Forensic Diagnosis**: When training on raw discharge values, regression trees prioritize splits that minimize squared errors on massive rivers ($> 50,000\text{ cfs}$). The terminal leaves of raw trees produce baseflow predictions between $5,000$ and $15,000\text{ cfs}$. When applied to a small Pacific Northwest mountain river, the model predicts $\sim 10,000\text{ cfs}$ on dry summer days, producing an astronomical error.
- **Remedy**: Specific discharge ($q = Q/A$) normalizes by drainage area ($173\text{ sq mi}$), constraining predictions to physical runoff yields ($q \sim 1.0\text{--}3.0\text{ cfs/sq mi}$), immediately bringing RMSE down from $10,645\text{ cfs}$ to $581\text{ cfs}$—an **18-fold error reduction**!

### 3.2 The "Mississippi Scale Extrapolation" in Raw Models
- **Station**: `07289000` (Mississippi River at Vicksburg, MS).
- **Physical Characteristics**: Drainage area $1,144,500\text{ sq mi}$, mean streamflow $> 600,000\text{ cfs}$, flood peaks $> 1,200,000\text{ cfs}$.
- **Performance**:
  - LightGBM Raw Unweighted: RMSE = **$301,868.7\text{ cfs}$**
  - LightGBM Log-Specific Discharge: RMSE = **$221,310.6\text{ cfs}$** (**$80,558\text{ cfs}$ error reduction**)
- **Forensic Diagnosis**: In LORSO Fold 03, all 4 Mississippi gauges were removed from training. The largest remaining basin in the training set was the Missouri River at Omaha ($DA = 322,800\text{ sq mi}$). Raw tree algorithms cannot extrapolate beyond the maximum target values observed in their training leaves ($\sim 350,000\text{ cfs}$). Consequently, during massive Mississippi flood events, raw models severely under-predicted by up to $1,000,000\text{ cfs}$. Specific discharge models predicted runoff yields of $0.6\text{--}1.0\text{ cfs/sq mi}$, which multiplied by $1,144,500\text{ sq mi}$ produced realistic flow estimates.

### 3.3 Why XGBoost Log1p Succeeded on Small Basins but Failed on Floods
- XGBoost `log1p` performed exceptionally well on small-to-medium arid basins (e.g. Red River RMSE $6,451\text{ cfs}$, Texas Colorado RMSE $8,797\text{ cfs}$, Little Arkansas RMSE $450\text{ cfs}$).
- Because $\log(Q + 1)$ compresses variance, it penalizes percentage errors rather than raw $cfs$ deviations. This protects small rivers from the scale-explosion suffered by raw models.
- **The Fatal Flaw**: On extreme flood crests, $\log(Q + 1)$ suppresses upper-tail gradients. In our flood peak analysis, XGBoost `log1p` **underpredicted 80.2% of all peak days**, with an average peak deficit of $-58,067\text{ cfs}$. Under the FLOODCAST rubric (where Top-10% Peak RMSE carries 30% weight), this systematic suppression is heavily penalized.

---

## 4. Key Scientific Insights for Final Competition Modeling

1. **Specific Discharge is Non-Negotiable**: For unseen river stations, predicting specific discharge ($q = Q/A$) or log-specific discharge ($\log(q + 1)$) is mandatory to prevent catastrophic scale mismatches on both small creeks and macro-rivers.
2. **Dual-Branch Architecture Recommendation**:
   - For final competition submission, the optimal architecture is a **blended ensemble**:
     $$\hat{Q}_{\text{final}} = \alpha \cdot \hat{Q}_{\text{log\_spec\_q}} + (1 - \alpha) \cdot \hat{Q}_{\text{spec\_q}}$$
     where $\alpha \approx 0.6\text{--}0.7$.
   - This blend leverages the superior overall RMSE and variance control of `log_spec_q` while utilizing the convex upper-tail sensitivity of linear `spec_q` to capture flood surges without underpredicting.
3. **Organiser Clarifications Must Precede Final Training**:
   - As documented in `reports/unresolved_competition_questions.md`, confirmation of the daily mean vs daily maximum target (Blocker BLK-01) and NASA POWER vs Open-Meteo feature alignment (BLK-02) is required before final model submission.

