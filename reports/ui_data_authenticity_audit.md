# PRAVAHA — Data Authenticity & Scientific Integrity Audit Report
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt UI-1.1 Data Provenance & Scientific Authenticity Audit  
**Date**: November 2026  
**Auditor**: Senior Data & Machine Learning Quality Engineer  

---

## 1. Executive Summary

This forensic data audit inspects all data objects, numerical readouts, statistical claims, and hydrological telemetry rendered in the PRAVAHA React frontend (`frontend/src/data/mockData.ts` and associated page components).

In strict accordance with the competition guidelines and the findings of **Prompts D, E, F, and UI-0**, every numerical claim and data field has been classified into four distinct evidentiary tiers:
- **Tier A**: **VERIFIED FROM PROJECT DATA** (Directly grounded in official USGS station metadata and NASA POWER reanalysis).
- **Tier B**: **HISTORICAL MODEL VALIDATION DATA** (Derived from our 23-fold Leave-One-River-System-Out validation experiments).
- **Tier C**: **DEMONSTRATION DATA ONLY** (Interactive mockups created to demonstrate operational UI workflows).
- **Tier D**: **UNSUPPORTED CLAIM** (Marketing exaggerations, unverified live claims, or invalid statistical conflations that have been **identified, corrected, or removed**).

---

## 2. Comprehensive Data Classification Matrix

| Data Metric / Field | Displayed Value | Provenance Tier | Forensic Classification & Scientific Status |
| :--- | :--- | :--- | :--- |
| **Catalog Station Count** | 34 Stations | **Tier A** | **VERIFIED FROM PROJECT DATA**: Sourced from `reports/verified_station_catalog.csv`. Sourced from official USGS NWIS service. |
| **LORSO Evaluation Count** | 33 Stations | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: 33 stations evaluated across 23 river-system groups. Station `11447650` (Sacramento) had missing post-2015 observations and was excluded from LORSO evaluation. |
| **River-System Groups** | 23 Systems | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: Established in `reports/river_system_grouping.csv` using HUC-2/4 basin drainage boundaries to prevent spatial leakage. |
| **Discharge Target Metric** | Daily Mean (`00060_00003`) | **Tier A** | **VERIFIED FROM PROJECT DATA**: Official USGS mean daily streamflow in `cfs`. Marked as *UNCONFIRMED SPEC* regarding whether the competition organizers meant instantaneous peak daily discharge (`00060_00001`). |
| **Discharge Unit** | `cfs` (ft³/s) | **Tier A** | **VERIFIED FROM PROJECT DATA**: Strictly enforced across all 5 pages. Zero metric `m³/s` conversions used, upholding competition rules. |
| **LORSO Macro-Averaged R²** | `0.4910` | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: Grounded in `LightGBM log_spec_q` 23-fold LORSO evaluation (`reports/lors_validation_results.csv`). |
| **Overall LORSO RMSE** | `82,871.1 cfs` | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: True out-of-system spatial RMSE across all 24,088 holdout observations. |
| **Top-10% Extreme Peak RMSE** | `156,593.8 cfs` | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: Top decile extreme event evaluation across 2,423 holdout samples. |
| **Overall LORSO MAE** | `24,644.3 cfs` | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: Verified mean absolute error from LORSO validation results. |
| **Leading ML Formulation** | `log_spec_q` | **Tier B** | **HISTORICAL MODEL VALIDATION DATA**: Specific runoff logarithm target ($\ln(Q / \text{Drainage Area})$) with LightGBM regressor. |
| **Weather Input Source** | NASA POWER MERRA-2 | **Tier A** | **VERIFIED FROM PROJECT DATA**: Daily meteorological reanalysis (`PRECTOTCORR`, `T2M`, `T2MDEW`, `WS2M`, `GWETTOP`). Consistently collected across all 34 stations. |
| **Soil Moisture / Wetness** | `GWETTOP = 0.884` | **Tier A** | **VERIFIED FROM PROJECT DATA**: Labeled as NASA POWER Surface Soil Wetness Fraction (0–1 unitless range). Not volumetric soil moisture ($m^3/m^3$). |
| **Current River Flow (Real-time)** | e.g., `38,100 cfs` | **Tier C** | **DEMONSTRATION DATA ONLY**: Historical baseline observation displayed as a scenario baseline. Labeled as *Demonstration / Historical Baseline*, not live streaming telemetry. |
| **Predicted Peak Crest (+18h)** | `52,400 cfs` | **Tier C** | **DEMONSTRATION DATA ONLY**: Scenario simulation illustrating flood crest exceedance. Labeled as *Experimental Scenario Run*, not an operational public flood warning. |
| **Atmospheric River AR-4** | `112.5 mm Inflow` | **Tier C** | **DEMONSTRATION DATA ONLY**: Synthetic extreme event simulation scenario used for interactive stress-testing. |
| **Monte Carlo Risk Matrix** | 10k Run Probabilities | **Tier C** | **DEMONSTRATION DATA ONLY**: Synthetic ensemble simulation estimating 10-Yr, 25-Yr, 50-Yr, and 100-Yr exceedances. |
| **Multichannel Dispatch Pipeline** | Push, SMS, WhatsApp, Gov | **Tier C** | **DEMONSTRATION DATA ONLY**: Multi-channel emergency dispatcher simulation. All triggers are sandboxed in local state with zero external carrier transmission. |
| **Kin Lifeline Network** | 4 Family Contacts | **Tier C** | **DEMONSTRATION DATA ONLY**: Interactive local safety circle prototype with local state "Ping" triggers. |
| **Citizen Hazard Reports** | 4 Pre-seeded Reports | **Tier C** | **DEMONSTRATION DATA ONLY**: Local session state demonstration. Submissions are stored in browser memory only and never routed to emergency 911 dispatchers. |
| **Rescue Requests** | Urgent SOS Queue | **Tier C** | **DEMONSTRATION DATA ONLY**: Simulated emergency rescue intake. |
| **Smart Coordinator Dispatch** | `#DISP-SAC-9402` | **Tier C** | **DEMONSTRATION DATA ONLY**: Demonstrates physics-informed route feasibility (+1.8m safe elevation freeboard) and inventory matching. |
| **NGO Inventory Matrix** | 4 Resource Categories | **Tier C** | **DEMONSTRATION DATA ONLY**: Modeled humanitarian depot inventory for hackathon demonstration. |
| **Verified NGO Directory** | 4 Response Brigades | **Tier C** | **DEMONSTRATION DATA ONLY**: Simulated organizational directory. |
| **Donor Campaigns** | 3 Campaign Cards | **Tier C** | **DEMONSTRATION DATA ONLY**: Demonstrates 80G tax-exempt donation workflows with local state feedback. |

---

## 3. Disallowed Claims & Scientific Corrections Audit

The following unsupported claims were identified from the original Stitch HTML prototypes and have been **strictly prohibited, replaced, or corrected** in the React application:

| Original Prototype Claim | Forensic Finding | Action Taken in React Frontend | Status |
| :--- | :--- | :--- | :--- |
| **"99.4% Model Confidence" / "94.6% Confidence"** | **TIER D: UNSUPPORTED CLAIM**. Conflates statistical $R^2$ or in-sample fit with operational confidence. Our audited LORSO $R^2$ is `0.4910`. | **REPLACED**: Replaced with exact LORSO benchmark metrics: `LORSO R² = 0.4910`, `Peak RMSE = 156,594 cfs`, `Overall MAE = 24,644 cfs`. | **CORRECTED** |
| **"18-Hour Operational Forecast"** | **TIER D: UNSUPPORTED CLAIM**. The ML models were trained on daily USGS mean discharge without real-time telemetry streaming hooks. | **REPLACED**: Labeled as `EXPERIMENTAL SCENARIO OUTPUT (Scenario Run)` and `SCENARIO PROJECTION`. | **CORRECTED** |
| **"128 Active Stations Across 6 Major Basins"** | **TIER D: UNSUPPORTED CLAIM**. Fabricated number from Stitch mockup. Our project has 34 verified USGS stations and 33 evaluated LORSO stations across 23 river systems. | **REPLACED**: Corrected to `34 Verified USGS Hydrologic Nodes (33 LORSO Evaluated)` across `23 River-System Groups`. | **CORRECTED** |
| **"Live Doppler Radar QPE Mesh"** | **TIER D: UNSUPPORTED CLAIM**. The project weather source is NASA POWER MERRA-2 daily reanalysis, not live Doppler radar. | **REPLACED**: Labeled as `NASA MERRA-2 PRECIPITATION REANALYSIS` and `DEMONSTRATION RADAR OVERLAY`. | **CORRECTED** |
| **"Confirmed Emergency Siren & Cell Broadcast Dispatched"** | **TIER D: UNSUPPORTED CLAIM**. Would mislead evaluators into believing live carrier broadcast integration exists. | **REPLACED**: Guarded by `TruthBanner` stating `DEMONSTRATION SIMULATION — Safe sandbox trigger (No live 911 / EAS dispatch)`. | **CORRECTED** |
| **"911 Emergency Response Connected"** | **TIER D: UNSUPPORTED CLAIM**. Community rescue form must never claim official emergency response routing. | **REPLACED**: Prominently disclosed in `TruthBanner`: `Demonstration ground portal — Not connected to 911 or first responders. Saved to local session state only`. | **CORRECTED** |

---

## 4. Truth Engine Compliance & Visible Disclosures

To prevent any evaluator from mistaking demonstration interfaces for operational public safety infrastructure, the React application deploys the [`TruthBanner`](file:///c:/Users/Lenovo/OneDrive/Desktop/pravaha/frontend/src/components/common/TruthBanner.tsx) component across key user touchpoints:

1. **Top Status Bar**:
   - `VERIFIED USGS TELEMETRY (cfs)`: Distinguishes authentic USGS streamgauge identities, drainage areas, and historical mean flows from simulated elements.
2. **Dashboard Hydrograph**:
   - `BENCHMARK HYDROGRAPH & SCENARIO PROJECTION`: Discloses that discharge curves are based on USGS statCd `00060_00003` and out-of-system LORSO 23-fold validation holdouts.
3. **Cartographic Map**:
   - `EXPERIMENTAL CARTOGRAPHIC ENGINE`: Discloses that station locations reflect real USGS coordinates, while radar and inundation polygons are scenario simulations.
4. **Flood Alert Console**:
   - `FLOOD ALERT DISPATCH SYSTEM — SIMULATION MODE`: Confirms that SMS, WhatsApp, and siren arrays are local UI prototypes.
5. **Community Reporting**:
   - `COMMUNITY REPORTING & CROWD TELEMETRY — DEMONSTRATION MODE`: Confirms client-side local state storage only.
6. **NGO Relief Hub**:
   - `NGO RELIEF LOGISTICS & ROUTE OPTIMIZATION — SIMULATION MODE`: Discloses that route freeboard and inventory counts are logistics demonstration models.

