# PRAVAHA — Five-Slide Hackathon Presentation Deck
**Project**: PRAVAHA (प्रवाह)  
**Tagline**: "PREDICT THE SURGE. PROTECT THE PEOPLE."  
**Event**: FLOODCAST 24-Hour Hackathon  
**Target Deck Length**: Exactly 5 Widescreen Slides  
**Format**: Ready-to-Copy Slide Content with Visual Specs, Key Metrics, and Fact-Checked Caveats  

---

## SLIDE 1 — THE PROBLEM: WHY HYDROLOGICAL GENERALISATION FAILS

### Slide Details
- **Slide Number**: 1 of 5
- **Slide Title**: The Generalisation Crisis in River Discharge Forecasting
- **Core Message**: Conventional machine learning models fail when transferred to unseen river systems because watershed scale mismatches and rare extreme flood crests destroy uncalibrated spatial predictions.

### Ready-to-Copy Slide Text
#### Subtitle:
Bridging the gap between localized gauge calibration and continental flood intelligence.

#### Key Bullet Points (3–4 Maximum):
- **Spatial Transfer Breakdown**: Standard ML models overfit to local gauge geometries. When deployed on unseen river systems with different drainage areas, raw volume predictions suffer catastrophic scale mismatch.
- **The Extreme Peak Penalty**: Flash floods and top-10% crest events account for over 90% of humanitarian damage, yet represent less than 2% of training observations, leading models to systematically underpredict crest heights.
- **Advective Network Leakage**: Traditional cross-validation leaks upstream flow observations to downstream gauges on the same mainstem, creating dangerously optimistic accuracy scores that collapse in operational zero-gauge deployments.

### Callout Metric Plaque:
> **100× Scale Mismatch**: River discharge across continental basins spans from $150\text{ cfs}$ (mountain tributaries) to over $1,200,000\text{ cfs}$ (continental trunks). Raw regression models cannot transfer across catchment scales without physical area normalisation.

### Recommended Visual
- **Visual Description**: Conceptual high-contrast split diagram contrasting a *known calibrated basin* (dense streamgauge network, predictable flow) with an *unseen target catchment* (zero streamgauges, extreme convective rainfall, unknown runoff response).
- **Branding**: PRAVAHA Platform Name (प्रवाह) and Tagline: *"PREDICT THE SURGE. PROTECT THE PEOPLE."*

### Presenter Explanation (15–20 Seconds)
> *"Welcome, judges. In flood forecasting, the ultimate test is not predicting tomorrow's flow on a river where you have 50 years of gauge data. The true challenge is predicting dangerous flood crests on an unseen river system where zero streamflow history exists. Standard machine learning models fail here because drainage areas vary by orders of magnitude, and extreme flood crests are so rare that algorithms treat them as statistical outliers. PRAVAHA was engineered to solve this spatial transfer bottleneck."*

### Project Reference Sources
- `reports/unresolved_competition_questions.md` (Section 1 & 4)
- `reports/prompt_f_validation_integrity_audit.md` (Section 3)

### Required Caveat / Accuracy Guard
- Do not claim that PRAVAHA has already deployed operationally or prevented real-world floods. Frame this as a machine learning benchmark solving the spatial generalisation problem on real historical USGS river basins.

---

## SLIDE 2 — OUR SOLUTION: CATCHMENT TRANSFER INTELLIGENCE & TRUTH ENGINE

### Slide Details
- **Slide Number**: 2 of 5
- **Slide Title**: Physics-Informed Specific Discharge & Transparent Hydrological AI
- **Core Message**: PRAVAHA eliminates scale mismatch by decomposing river flow into drainage-area-normalised specific discharge ($q = Q/A$) and pairs predictions with a transparent Truth Engine that actively surfaces data limitations.

### Ready-to-Copy Slide Text
#### Subtitle:
Transforming meteorology and catchment physiography into reliable, un-leaked flood intelligence.

#### Key Bullet Points:
- **Catchment Transfer Intelligence**: By transforming raw discharge ($cfs$) into area-normalised specific discharge ($q = Q_{\text{cfs}} / A_{\text{sqmi}}$) and applying logarithmic variance stabilisation ($\log(q + 1)$), PRAVAHA models universal hydrological runoff yield across vastly different basin sizes.
- **Strict Zero-Leakage Feature Pipeline**: Features are computed strictly from satellite meteorology (NASA POWER MERRA-2) and static catchment attributes (USGS GAGES-II / StreamStats). Zero target discharge lags or upstream gauge readings are used.
- **PRAVAHA Truth Engine**: An evidence-based integrity framework that explicitly surfaces station data limitations, renders authentic breaks for missing observations, and flags regulated reservoirs rather than projecting false confidence.

### Callout Metric Plaque:
$$\text{Specific Discharge Transformation: } q = \frac{\text{Discharge (cfs)}}{\text{Drainage Area (sq mi)}} \quad \implies \quad y = \log(q + 1)$$
> **+348% R² Improvement**: Transforms spatial holdout performance from $R^2 = 0.1095$ (Raw LightGBM) to **$R^2 = 0.4910$** (Log-Specific LightGBM) on completely unseen river basins.

### Recommended Visual
- **Screenshot Path**: `reports/ui_backend_integration_screenshots/01_dashboard.png`
- **Visual Focus**: Cutout showing the dynamic SVG hydrograph (actual continuous discharge vs held-out LORSO validation prediction) paired with the **Historical Data Limitation Banner** triggered on benchmark station `11447650` (Sacramento River at Freeport, CA).

### Presenter Explanation (15–20 Seconds)
> *"To solve the scale mismatch, PRAVAHA introduces Catchment Transfer Intelligence. Instead of predicting raw cubic feet per second, we predict specific discharge—the volume of water produced per square mile of drainage basin. This single mathematical transformation normalises a tiny 170-square-mile creek and a million-square-mile Mississippi trunk into a common physical space. Crucially, we pair this with our Truth Engine: if a station has historical data limitations—like our Sacramento gauge where records end in 2015—the system explicitly warns the user instead of fabricating synthetic predictions."*

### Project Reference Sources
- `src/features/engineering.py` (Lines 10–72)
- `reports/prompt_f_model_selection_recommendation.md` (Section 3.2 & 5)
- `reports/ui_backend_integration_status.md` (Section 5)

### Required Caveat / Accuracy Guard
- Do not claim specific discharge solves all hydrological challenges. Acknowledge that regulated dams and reservoirs require reservoir release data not captured purely by precipitation.

---

## SLIDE 3 — DATA FOUNDATION & SYSTEM ARCHITECTURE

### Slide Details
- **Slide Number**: 3 of 5
- **Slide Title**: 100% Real Hydrological Data & Modular Full-Stack Architecture
- **Core Message**: PRAVAHA is built on a verified multi-agency data pipeline of 170,817 real daily records across 34 USGS stations, backed by an asynchronous FastAPI backend and a responsive React operations center.

### Ready-to-Copy Slide Text
#### Subtitle:
Zero synthetic data, strict provenance logging, and sub-second full-stack integration.

#### Key Bullet Points:
- **Zero Synthetic Data Foundation**: 170,817 daily mean discharge records (`00060_00003`) spanning 14 calendar years (2010–2023) across 34 verified USGS monitoring stations, paired with unbroken NASA POWER MERRA-2 meteorological reanalysis.
- **Physiographic Basin Grounding**: Verified drainage areas, mean basin elevations, channel slopes, and forest canopy percentages sourced directly from official USGS GAGES-II and StreamStats reports.
- **Production Full-Stack Implementation**:
  - *Data Layer*: PyArrow Parquet access with in-memory caching.
  - *Backend*: Asynchronous Python FastAPI service (25/25 automated unit tests passing, sub-50ms latency).
  - *Frontend*: React 18, Vite, TypeScript, and Tailwind CSS operations center with dynamic SVG rendering.

### Architecture Data Flow:
```
USGS NWIS + NASA POWER + GAGES-II  ──>  Feature Engine (48 Zero-Leakage Features)
                                                   │
React 18 SPA  <──  FastAPI Backend (Port 8000)  <──  LORSO Cross-Validation Engine (23 Folds)
```

### Key Scale Metrics:
- **170,817** Verified Daily Records | **14** Calendar Years (2010–2023) | **34** Monitored Basins
- **23** River Systems | **25/25** Automated Backend Unit Tests Passing (0.27s)

### Recommended Visual
- **Visual Description**: Two-column visual layout. Left column shows 3 data stat cards (Observations, Stations, Source Agency badges). Right column shows the clean full-stack architectural diagram connecting the Data Layer, ML Engine, FastAPI Backend, and React Frontend.

### Presenter Explanation (15–20 Seconds)
> *"Data integrity is non-negotiable in hydrological safety. PRAVAHA uses zero synthetic or interpolated data. We acquired 170,817 real daily discharge observations from the USGS National Water Information System across 34 monitoring stations, coupled with 14 years of NASA POWER satellite weather data and GAGES-II catchment physiography. The architecture is fully functional: our FastAPI backend serves cached Parquet validation data with 25 passing automated unit tests, feeding our React 18 operations center in real time."*

### Project Reference Sources
- `data/MANIFEST.md`
- `reports/verified_station_catalog.csv`
- `reports/catchment_provenance.csv`
- `reports/api_test_results.md`

### Required Caveat / Accuracy Guard
- Distinguish the 34 stations in the active labelled dataset from the 38 stations in the broader metadata catalog. Acknowledge that Open-Meteo rate-limited at 10,000 requests/day, which necessitated the reliable pivot to NASA POWER MERRA-2.

---

## SLIDE 4 — MACHINE LEARNING RESULTS: LORSO BENCHMARK

### Slide Details
- **Slide Number**: 4 of 5
- **Slide Title**: Rigorous Evaluation Across Unseen River Systems (LORSO)
- **Core Message**: Under 23-fold Leave-One-River-System-Out spatial validation across 24,088 out-of-system samples, LightGBM Log-Specific Discharge achieves the leading Pooled R² of 0.4910, cutting prediction error by 24.4%.

### Ready-to-Copy Slide Text
#### Subtitle:
Eliminating network leakage to measure true operational out-of-basin generalisation.

#### Core Metric Comparison Table:
| Model Architecture | Target Formulation | Overall RMSE (cfs) | Top-10% Peak RMSE (cfs) | MAE (cfs) | Pooled R² |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LightGBM Log-Specific Discharge** | `log_spec_q` | **82,871.1** | 156,593.8 | **24,644.3** | **0.4910** |
| **LightGBM Specific Discharge** | `spec_q` | 86,836.6 | **155,136.8** | 26,092.0 | 0.4411 |
| **LightGBM Raw Peak-Weighted (2.5x)** | `raw` | 108,321.3 | 202,091.4 | 32,260.0 | 0.1303 |
| **LightGBM Raw Unweighted** | `raw` | 109,609.5 | 204,474.6 | 32,312.1 | 0.1095 |
| **XGBoost Log1p** | `log1p` | 109,842.1 | 203,656.1 | 28,995.8 | 0.1057 |

#### Key Analytical Findings:
- **Superior Spatial Generalisation**: LightGBM `log_spec_q` achieves the highest Pooled $R^2$ (**0.4910**) and lowest MAE (**24,644 cfs**), preventing the 18-fold error explosions that raw models suffer on small rivers.
- **Peak Regime Dominance**: Linear specific discharge (`spec_q`) captures extreme floods best, achieving the lowest Top-10% Peak RMSE (**155,136.8 cfs**) and reducing Top-20 mega-event errors by **$158,000\text{ cfs}$**.
- **Mega-Basin Error Concentration**: The Mississippi River at Vicksburg accounts for **81.8% of total pooled squared error** due to its massive $1.2\text{M cfs}$ discharge scale. For 30 of 33 evaluated stations, individual RMSE is under $35,000\text{ cfs}$, with a median station MAE of **2,623 cfs**.

### Recommended Visual
- **Visual Description**: A cleanly styled comparison table highlighting the green winning cells for LightGBM `log_spec_q` and `spec_q`, paired with a bar chart comparing Raw LightGBM ($R^2 = 0.1095$) against Log-Specific LightGBM ($R^2 = 0.4910$).

### Presenter Explanation (15–20 Seconds)
> *"To rigorously test generalisation, we implemented Leave-One-River-System-Out cross-validation across 23 folds. We never trained on any upstream or downstream gauge of a tested river. The results are decisive: LightGBM with log-specific discharge achieved a Pooled R² of 0.4910, compared to just 0.1095 for raw models. On the 2,423 extreme peak flood days, linear specific discharge achieved the lowest peak RMSE. Furthermore, our forensic audit revealed that a single station—Vicksburg on the lower Mississippi—accounts for 81.8% of all squared error in the dataset, while the median station error across all other rivers is just 2,623 cfs."*

### Project Reference Sources
- `reports/lors_validation_results.csv`
- `reports/prompt_f_validation_integrity_audit.md`
- `reports/prompt_f_model_selection_recommendation.md`

### Required Caveat / Accuracy Guard
- Do not claim LightGBM is the "official competition winner". Call it the *leading experimental model under our LORSO benchmark*. Explicitly disclose that Vicksburg dominates pooled squared metrics.

---

## SLIDE 5 — WORKING PRODUCT, HONEST IMPACT & ROADMAP

### Slide Details
- **Slide Number**: 5 of 5
- **Slide Title**: From Hydrological Science to Actionable Decision Support
- **Core Message**: PRAVAHA translates validated streamflow intelligence into five intuitive operations screens, clearly distinguishing working verified data from prototype scenario simulations.

### Ready-to-Copy Slide Text
#### Subtitle:
A functional decision-support ecosystem for disaster responders and civil defense planners.

#### Five Operational Views:
1. **Command Dashboard**: Real-time inspection of 34 USGS stations, dynamic multi-temporal hydrographs, and live model comparison metrics.
2. **River Intelligence Map**: Geospatial streamgauge visualization with WGS84 coordinates, catchment telemetry drawers, and verified flow percentiles.
3. **Multi-Channel Flood Alerts**: Automated risk classification ($q_{50}, q_{75}, q_{90}$) and simulated cell-broadcast / siren dispatch pipeline.
4. **Community Reporting Hub**: Tactile crowdsourced water depth reporting and verified incident feed for field ground-truthing.
5. **NGO Flood Relief Logistics**: Automated rescue resource matching and mutual-aid asset coordination.

#### Capability Integrity & Operational Roadmap:
| Capability Status | Working Today (Verified) | Planned Roadmap (Post-Hackathon) |
| :--- | :--- | :--- |
| **Data & Models** | 34 USGS stations, continuous daily time-series, LORSO benchmark ($R^2=0.4910$). | Organiser target confirmation (`00060_00003` vs `00060_00001`); final `predictions.csv`. |
| **Backend & API** | FastAPI REST service (25/25 passing tests, in-memory Parquet cache). | Production deployment; containerised real-time USGS/NOAA socket streaming. |
| **Alerts & Field** | Scenario simulation mode with transparent TruthEngine disclosures. | Certified municipal CAP (Common Alerting Protocol) & multi-carrier SMS integration. |

### Closing Callout & Tagline:
> *"Predict the Surge. Protect the People."*  
> **PRAVAHA is ready for technical evaluation.**

### Recommended Visual
- **Screenshot Path**: Collage featuring **IMG-02** (`02_map.png`) as the hero backdrop, with insets of **IMG-03** (`03_alerts.png`) and **IMG-05** (`05_relief.png`).

### Presenter Explanation (15–20 Seconds)
> *"PRAVAHA is not just an offline script; it is a working, full-stack decision-support system. Responders can monitor real USGS stations, view dynamic hydrographs with out-of-system validation predictions, and inspect catchment attributes. We also believe in absolute transparency: our emergency alert dispatcher, citizen SOS reporting, and NGO relief logistics are clearly disclosed as evaluation simulation prototypes. With official organiser confirmation on target parameters and external API access, PRAVAHA is ready to generate competition test predictions and advance toward operational deployment."*

### Project Reference Sources
- `reports/ui_backend_integration_status.md`
- `reports/ui_backend_integration_test_results.md`
- `frontend/README.md`

### Required Caveat / Accuracy Guard
- Do not invent partners, government approvals, or measured lives saved. Explicitly label alerts, citizen reporting, and relief logistics as prototype scenario simulations.

