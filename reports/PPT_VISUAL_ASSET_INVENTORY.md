# PRAVAHA — Hackathon Visual Asset Inventory & Layout Guide
**Project**: PRAVAHA (प्रवाह) — "PREDICT THE SURGE. PROTECT THE PEOPLE."  
**Deliverable**: Visual Asset Mapping & Slide Layout Recommendations for 5-Slide Presentation  
**Date**: November 2026  
**Target Resolution**: 16:9 Widescreen Presentation Slides  

---

## 1. Verified Visual Asset Inventory

All screenshot files listed below exist on disk, captured during live runtime of the React application connected to the FastAPI backend:

| Asset ID | File Path | Resolution | Size | Screen Name | Key Visual Elements Visible |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **IMG-01** | `reports/ui_backend_integration_screenshots/01_dashboard.png` | 1440 × 900 | 344 KB | Main Command Dashboard | • Verified station selector with 34 USGS streamgauges.<br>• Dynamic SVG hydrograph showing daily mean flow (`00060_00003`) and 2022–2023 holdout curve.<br>• Dedicated **Historical Data Limitation Banner (2015-09-30)** on Sacramento gauge `11447650`.<br>• Hero metric tile displaying **Pooled R² (LORSO Validation): 0.4910**.<br>• Verified GAGES-II catchment physiography card. |
| **IMG-02** | `reports/ui_backend_integration_screenshots/02_map.png` | 1440 × 900 | 252 KB | Interactive Hydrological Map | • 34 WGS84 streamgauge markers plotted across US hydrological corridors.<br>• Dynamic layer pill indicating `River Stations (38)`.<br>• Station telemetry drawer showing verified flow percentiles ($q_{25}, q_{50}, q_{90}$).<br>• Real historical discharge sparkline.<br>• Explicit `[DEMO]` tags on simulated radar and rainfall runoff slider. |
| **IMG-03** | `reports/ui_backend_integration_screenshots/03_alerts.png` | 1440 × 900 | 321 KB | Advanced Flood Alert System | • Hero header with `Verified USGS Dataset (38 Stations)`.<br>• Scenic visual banner featuring benchmark station `USGS 11447650`.<br>• 4-stage risk classification cards defining $q_{90}, q_{75}, q_{50}$ thresholds.<br>• Station broadcast table dynamically listing authentic USGS stations and river systems.<br>• Multi-channel dispatch simulator with simulation disclosure banner. |
| **IMG-04** | `reports/ui_backend_integration_screenshots/04_community.png` | 1440 × 900 | 206 KB | Community Reporting System | • Prominent disclaimer: `COMMUNITY REPORTING & RESCUE LIFELINE — EVALUATION SIMULATION ONLY`.<br>• Tactile crowdsourced water depth gauge (0–60 inches).<br>• Live citizen incident upvote feed.<br>• High-ground emergency rescue dispatch request form. |
| **IMG-05** | `reports/ui_backend_integration_screenshots/05_relief.png` | 1440 × 900 | 239 KB | NGO Flood Relief Hub | • Prominent disclaimer: `NGO & CIVIL DEFENSE LOGISTICS HUB — EVALUATION DEMONSTRATION`.<br>• Smart coordinator priority dispatch recommendation card (`#SAC-9402`).<br>• Resource inventory tracking (rescue boats, food rations, medical kits, shelters).<br>• Verified rescue partner directory. |

### Supplementary Responsive Assets (Mobile Viewports):
- `reports/ui_qa_screenshots/dashboard_mobile.png` (390 × 844, 169 KB)
- `reports/ui_qa_screenshots/map_mobile.png` (390 × 844, 114 KB)
- `reports/ui_qa_screenshots/alerts_mobile.png` (390 × 844, 133 KB)
- `reports/ui_qa_screenshots/community_mobile.png` (390 × 844, 97 KB)
- `reports/ui_qa_screenshots/relief_mobile.png` (390 × 844, 93 KB)

---

## 2. Slide-by-Slide Visual Allocation & Layout Blueprint

### Slide 1 — The Problem: Why Hydrological Generalisation Fails
- **Recommended Layout**: Split Layout (40% Left Problem Statement / 60% Right Graphic).
- **Primary Visual**: High-contrast conceptual split diagram illustrating:
  - **Left**: Standard catchment (known calibration curve).
  - **Right**: Unseen target catchment (scale mismatch, flash surge, zero downstream gauges).
- **Secondary Element**: Callout box displaying the competition focus:
  > *"Predicting flood peaks across unseen river basins without target observation leakage."*
- **Branding**: PRAVAHA logo (प्रवाह) and tagline: *"PREDICT THE SURGE. PROTECT THE PEOPLE."*

---

### Slide 2 — Our Solution: Catchment Transfer Intelligence & Truth Engine
- **Recommended Layout**: Split Showcase (45% Solution Architecture / 55% Hero Screenshot).
- **Primary Visual**: Cutout of **IMG-01** (`reports/ui_backend_integration_screenshots/01_dashboard.png`) focused on:
  - The dynamic SVG hydrograph showing the actual streamflow curve and the predicted out-of-system holdout curve.
  - The **Historical Data Limitation Banner** on station `11447650` (illustrating the Truth Engine in action).
- **Key Callout Annotation**:
  - Draw a subtle callout box around the formula plaque:
    $$q = \frac{\text{Discharge (cfs)}}{\text{Drainage Area (sq mi)}}$$
  - Callout label: *"Specific Discharge normalisation resolves the 100-fold scale mismatch between mountain creeks and continental trunks."*

---

### Slide 3 — Data Foundation & System Architecture
- **Recommended Layout**: Two-Column Architecture Grid (50% Data Scale & Sources / 50% Technical Architecture Diagram).
- **Left Column**: Data Scale Cards:
  - **170,817** labelled daily observations (2010–2023, 14 years).
  - **34** verified USGS streamgauging stations.
  - **23** hydrologically isolated river systems.
  - **Zero Synthetic Data** | USGS NWIS (`00060_00003`) + NASA POWER MERRA-2 + GAGES-II.
- **Right Column**: Clean Mermaid/Vector Architecture Diagram showing:
  - *Data Ingestion* (USGS + NASA POWER + GAGES-II) $\to$
  - *ML Engine* (48 features, LORSO 23 folds, LightGBM `log_spec_q`) $\to$
  - *FastAPI Backend* (In-memory cached parquet data access, 25/25 unit tests) $\to$
  - *React Frontend* (Vite + Tailwind, dynamic hydrograph, interactive map).

---

### Slide 4 — Empirical Machine Learning Benchmark
- **Recommended Layout**: Centered Performance Dashboard (60% Metric Comparison Table / 40% Key Insights & Station Breakdown).
- **Primary Visual**: Clean, beautifully styled benchmark comparison table:

| Model Architecture | Target Formulation | Overall RMSE (cfs) | Top-10% Peak RMSE (cfs) | MAE (cfs) | Pooled R² |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LightGBM Log-Specific Discharge** | `log_spec_q` | **82,871.1** | 156,593.8 | **24,644.3** | **0.4910** |
| **LightGBM Specific Discharge** | `spec_q` | 86,836.6 | **155,136.8** | 26,092.0 | 0.4411 |
| **LightGBM Raw Peak-Weighted (2.5x)** | `raw` | 108,321.3 | 202,091.4 | 32,260.0 | 0.1303 |
| **LightGBM Raw Unweighted** | `raw` | 109,609.5 | 204,474.6 | 32,312.1 | 0.1095 |
| **XGBoost Log1p** | `log1p` | 109,842.1 | 203,656.1 | 28,995.8 | 0.1057 |

- **Side Panel Highlights**:
  - **+348% R² Improvement**: `log_spec_q` (0.4910) vs raw models (0.1095).
  - **Extreme Peak Champion**: `spec_q` achieves lowest peak RMSE (155,136.8 cfs).
  - **Vicksburg Macro-Dominance**: Mississippi at Vicksburg accounts for 81.8% of pooled squared error; median station RMSE is **5,586.9 cfs**.

---

### Slide 5 — Full-Stack Product, Honest Capabilities & Future Roadmap
- **Recommended Layout**: 3-Card Multi-Screen Showcase (55% Top/Left Product Screens / 45% Bottom/Right Roadmap & Capabilities).
- **Product Visuals**:
  - Hero image: **IMG-02** (`reports/ui_backend_integration_screenshots/02_map.png`) showing 34 river station pins and the active basin viewport.
  - Inset image 1: **IMG-03** (`reports/ui_backend_integration_screenshots/03_alerts.png`) showing the multi-channel dispatch matrix.
  - Inset image 2: **IMG-05** (`reports/ui_backend_integration_screenshots/05_relief.png`) showing the NGO coordinator recommendation.
- **Side Column**: Clear 2-Tier Breakdown:
  - **Working Today**:
    - Live FastAPI REST API + React Vite SPA.
    - Verified USGS time-series & LORSO holdout predictions.
    - Transparent Truth Engine & station limitation alerts.
  - **Operational Roadmap**:
    - Final competition inference pipeline (`predictions.csv`).
    - Organiser confirmation on target parameter (`00060_00003` vs `00060_00001`).
    - Live NOAA/USGS socket telemetry ingest.
    - Certified municipal CAP / cell broadcast integration.
- **Closing Tagline**: *"PREDICT THE SURGE. PROTECT THE PEOPLE."*

---

## 3. Presentation Graphic Styling Notes

- **Color Palette**:
  - Deep Marine Background: `#17354D` (for dark title/closing slide) or Crisp Light `#F4F9FC` (for content slides).
  - Primary Hydro Blue: `#006297` (headers, primary cards).
  - Clear Cyan: `#51B9CC` (accents, hydrograph curves, key metrics).
  - Success Green: `#40A77A` (verified tags, normal risk).
  - Alert Amber/Coral: `#D95F62` / `#E58C47` (flood thresholds, critical callouts).
- **Typography**: Clean modern sans-serif (Inter, Roboto, or Arial). Bold tabular numbers for all numerical metrics.
- **Card Styling**: Rounded corners (16px), subtle borders (`#D8E8F0`), soft ambient drop shadows.

