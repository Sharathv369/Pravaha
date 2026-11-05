# PRAVAHA — Competition Blockers & Operational Readiness Status
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt F Final Blocker Status Report (Phase F9)  
**Date**: November 2026  
**Auditor**: Lead ML & Backend Systems Engineer  

---

## Executive Summary

While the **Leave-One-River-System-Out (LORSO)** validation benchmark has established that **LightGBM Log-Specific Discharge** is our highest-performing spatial generalisation architecture, several external operational questions cannot be solved internally without explicit guidance from the FLOODCAST hackathon organizers.

This report documents the current status, available evidence, unanswered questions, and required clarifications for each blocker.

---

## 1. Master Blocker Audit Table

| Blocker ID | Domain | Issue Title | Current Status | Requires Organiser Confirmation? |
| :---: | :--- | :--- | :---: | :---: |
| **BLK-01** | Target Formulation | USGS Daily Mean (`00060_00003`) vs Daily Maximum Crest (`00060_00001`) | `NEEDS ORGANISER CONFIRMATION` | **YES** |
| **BLK-02** | Meteorological Features | NASA POWER MERRA-2 vs Open-Meteo API | `NEEDS ORGANISER CONFIRMATION` | **YES** |
| **BLK-03** | Scoring Metric | Official Platform Metric Normalisation & Composite Formula | `NEEDS ORGANISER CONFIRMATION` | **YES** |
| **BLK-04** | Training Scope | 34 Expanded Stations vs 5 Core Stations Eligibility | `NEEDS ORGANISER CONFIRMATION` | **YES** |
| **BLK-05** | Hydrographic Isolation | River Network Connectivity & LORSO Validation Design | `VERIFIED INTERNALLY` | **NO** |

---

## 2. In-Depth Blocker Analysis

### Blocker BLK-01: Target Definition (Daily Mean vs Daily Maximum)
- **Current Status**: `NEEDS ORGANISER CONFIRMATION`
- **Available Evidence**:
  - The master dataset `data/processed/PRAVAHA_TRAIN_LABELLED.csv` contains 170,817 valid daily streamflow records sourced from USGS NWIS parameter `00060_00003` (Discharge, cubic feet per second, daily mean).
  - An exploratory download of station `08158000` (`08158000_discharge_max_2010-01-01_2023-12-31.json`) confirmed that USGS statCd `00001` (Daily Maximum) is published for some stations, but is unavailable continuously across all 34 stations.
  - The Problem Statement uses both phrases: *"predict daily river discharge (discharge_cfs)"* and *"peak daily discharge"*.
- **What Remains Unanswered**:
  - Did the organizers construct the test set ground truth from USGS daily mean (`00003`) or daily maximum (`00001`)?
- **Operational Risk**:
  - If the test set evaluates daily maximum flow, models trained on daily mean flow will underpredict flood crests by $50\%\text{--}300\%$, heavily degrading the Top-10% Peak RMSE score (30% weight).

---

### Blocker BLK-02: Meteorological Source (NASA POWER vs Open-Meteo)
- **Current Status**: `NEEDS ORGANISER CONFIRMATION`
- **Available Evidence**:
  - The Problem Statement suggests Open-Meteo for weather acquisition.
  - Open-Meteo API returned HTTP 429 quota exhaustion (10,000 calls/day free tier).
  - NASA POWER MERRA-2 supplied 100% real, unbroken weather features across all 34 stations.
  - Parameter mappings match on precipitation and temperature, but **differ on soil moisture**: Open-Meteo reports volumetric soil moisture ($m^3/m^3$, range $0.05\text{--}0.45$), while NASA POWER reports topsoil wetness saturation fraction ($0.0\text{--}1.0$).
- **What Remains Unanswered**:
  - Will the competition evaluation `test.csv` provide pre-extracted Open-Meteo weather features, or are participants expected to query their own weather APIs during inference?
  - Does the platform accept submissions utilizing NASA POWER reanalysis meteorology?
- **Operational Risk**:
  - If `test.csv` contains Open-Meteo volumetric soil moisture without conversion, models trained on NASA POWER wetness fractions will experience feature domain shift.

---

### Blocker BLK-03: Competition Scoring Normalisation
- **Current Status**: `NEEDS ORGANISER CONFIRMATION`
- **Available Evidence**:
  - The Problem Statement assigns weights: Overall RMSE (40%), Top-10% Peak RMSE (30%), MAE (20%), and R² (10%).
  - Directly summing dimensional discharge errors ($cfs$) with dimensionless $R^2$ is mathematically invalid without an explicit normalization standard (such as dividing errors by standard deviation $\sigma_y$ or basin mean $\bar{y}$).
- **What Remains Unanswered**:
  - What is the exact formula or platform code used to score submissions on the leaderboard?
  - Is the live leaderboard ranked by raw RMSE, with composite scoring applied only for final awards?
- **Operational Risk**:
  - Optimizing for an arbitrary ad-hoc composite loss could lead to suboptimal decisions compared to optimizing for the true evaluation metric.

---

### Blocker BLK-04: Station Eligibility Scope (Core 5 vs Expanded 34)
- **Current Status**: `NEEDS ORGANISER CONFIRMATION`
- **Available Evidence**:
  - 5 core stations were originally provided: Potomac (`01646500`), Neuse (`02087500`), Mississippi (`07010000`), Colorado (`08158000`), Sacramento (`11447650`).
  - 29 additional verified USGS stations were acquired, cleaned, and verified with official GAGES-II and StreamStats catchment attributes.
  - Rule 7 states: *"Any extra station data used for training must be restricted to dates before the actual competition test period once that period is known."*
- **What Remains Unanswered**:
  - Are participants allowed to submit models trained on the expanded 34-station dataset, or will submissions be evaluated exclusively on models trained on the 5 core stations?
- **Operational Risk**:
  - Submitting an expanded model if the organizers strictly enforce training on the 5 core stations could risk disqualification.

---

### Blocker BLK-05: River Network Hydrographic Isolation
- **Current Status**: `VERIFIED INTERNALLY`
- **Available Evidence**:
  - All 34 stations were audited against USGS NWIS site metadata, Hydrologic Unit Codes (HUC), and NHD flow lines.
  - 23 river systems were established. In our Leave-One-River-System-Out benchmark, all upstream/downstream cascades (e.g. Mississippi and Upper Colorado mainstems) were held out simultaneously with zero training leakage.
- **Resolution**: Fully resolved internally. No organizer confirmation required.

---

## 3. Operational Protocol for Final Competition Phase

To ensure compliance with all competition rules while maintaining engineering rigor:
1. **Maintain Dual Training Scripts**:
   - Primary Pipeline: Trained on the 33 verified stations with verified drainage areas.
   - Fallback Pipeline: Trained strictly on the 4 core stations with verified drainage areas (Potomac, Neuse, Mississippi, Colorado) for instant adaptation if external stations are restricted.
2. **Transparent Target Handling**:
   - Continue using USGS daily mean discharge (`00060_00003`) provisionally.
   - If organizers confirm daily maximum (`00060_00001`), execute an automated retrain using daily maximum targets during the official competition window.
3. **No Premature Deployment**:
   - In strict compliance with Rule 8 (*"No pre-trained competition model may be submitted. The final competition model must be trained during the authorised hackathon window"*), the final submission model will be trained strictly upon receiving the official competition test set.

