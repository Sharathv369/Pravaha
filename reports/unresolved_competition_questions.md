# PRAVAHA — Unresolved Competition Requirements & Blocker Register
**Project**: PRAVAHA — FLOODCAST 24-Hour Regression Hackathon  
**Deliverable**: Phase E0 Audit Document  
**Date**: November 2026  
**Auditor**: Lead ML & Backend Systems Engineer  

---

## Executive Summary

This document forensically audits the critical ambiguities, unconfirmed parameters, and structural discrepancies between the official FLOODCAST Problem Statement (PS) and the empirical data pipeline developed to date. 

All experiments in Prompt E (Leave-One-River-System-Out Validation) have proceeded **provisionally** using the verified USGS daily mean streamflow (`00060_00003`) and NASA POWER MERRA-2 meteorological features. However, no model can be declared "competition-ready" until the five core operational questions documented below receive formal organizer clarification.

---

## 1. Target Definition Discrepancy: Daily Mean vs Daily Maximum

### 1.1 The Ambiguity
The FLOODCAST hackathon documentation exhibits linguistic ambiguity in specifying the prediction target:
- In the primary task header, it states: *"For each (station_id, date) in test.csv, predict discharge_cfs (non-negative float, daily river discharge in cubic feet per second)."*
- In problem descriptions and scoring rubrics, it references *"peak daily discharge"*, while emphasizing that *"missing flood peaks is penalized most"*.

### 1.2 USGS Parameter Code Distinctions
USGS National Water Information System (NWIS) publishes three distinct daily streamflow products for parameter code `00060` (Discharge in $cfs$):
1. **Statistic Code `00003` (Daily Mean Discharge)**:
   - The time-weighted arithmetic mean of all instantaneous discharge measurements recorded during a 24-hour calendar day.
   - **Availability**: Continuous, verified, and unbroken across all 34 PRAVAHA stations from 2010 to 2023 (170,817 valid observations).
   - **Continental Benchmark Standard**: Standard target in academic continental hydrology (e.g., Caravan, CAMELS, Daymet/NLDAS benchmarks).
2. **Statistic Code `00001` (Daily Maximum Discharge)**:
   - The single highest instantaneous peak discharge recorded during the 24-hour calendar day.
   - **Availability**: Spotty and irregular. While station `08158000` (Colorado River at Austin, TX) has recorded `00060_00001` data (`data/raw/usgs/08158000_discharge_max_2010-01-01_2023-12-31.json`), many other USGS gauges do not systematically compute or publish daily maximum unit statistics.
3. **Annual Peak Streamflow (`00060_00000` Peak Flow Files)**:
   - Contains only 1 record per year representing the annual instantaneous flood crest. Inapplicable as a daily continuous target.

### 1.3 Hydrological Impact of the Difference
During quiescent baseflow periods, daily maximum and daily mean streamflow differ by less than $3\text{--}8\%$. However, during flash flood events on small to medium watersheds:
- The instantaneous crest (`00001`) can be $200\%\text{ to }500\%$ higher than the 24-hour integrated mean (`00003`).
- If the organizers evaluate submissions against daily maximum flow (`00001`), models trained on daily mean (`00003`) will systematically under-predict flood peaks, incurring heavy penalties on the Top-10% Peak RMSE metric (30% weight).

**Operational Status**: `NEEDS ORGANISER CONFIRMATION` (Target currently treated as daily mean `00060_00003` provisionally).

---

## 2. Weather Data Source: NASA POWER MERRA-2 vs Open-Meteo

### 2.1 The Issue
The FLOODCAST Problem Statement explicitly names **Open-Meteo** as the target weather data provider. 

During Phase A data acquisition:
- Open-Meteo returned **HTTP 429 Too Many Requests** (`Retry-After: 27886s`, rate limit exhausted at 10,000 requests/day).
- To preserve absolute data integrity without synthetic mock data, the engineering team pivoted to **NASA POWER MERRA-2** (satellite and reanalysis meteorology), which successfully supplied 100% real, unbroken weather data across all 34 stations for 2010–2023.

### 2.2 Parameter & Unit Mapping Audit

| Weather Parameter | Open-Meteo Specification | NASA POWER Variable Used | Physical Unit | Physical Definition & Discrepancy Note |
| :--- | :--- | :--- | :---: | :--- |
| **Precipitation** | `precipitation_sum` | `PRECTOTCORR` | $mm/\text{day}$ | Bias-corrected total precipitation. Physically equivalent. |
| **Max Temperature** | `temperature_2m_max` | `T2M_MAX` | $^\circ C$ | Maximum 2-meter air temperature. Physically equivalent. |
| **Min Temperature** | `temperature_2m_min` | `T2M_MIN` | $^\circ C$ | Minimum 2-meter air temperature. Physically equivalent. |
| **Soil Moisture** | `soil_moisture_0_to_7cm` | `GWETTOP` | Fraction vs $m^3/m^3$ | **CRITICAL DISCREPANCY**: Open-Meteo reports volumetric soil moisture ($m^3/m^3$, typical range $0.05\text{--}0.45$). NASA POWER reports topsoil wetness fraction ($0.0\text{--}1.0$, dimensionless saturation ratio). They are not interchangeable on raw numerical scales. |
| **Solar Radiation** | `shortwave_radiation_sum` | `ALLSKY_SFC_SW_DWN` | $MJ/m^2/\text{day}$ | Total downward shortwave insolation. |
| **Wind Speed** | `wind_speed_10m_max` | `WS2M` | $m/s$ | NASA POWER provides 2-meter wind speed; Open-Meteo provides 10-meter wind speed. |
| **Relative Humidity** | `relative_humidity_2m_mean` | `RH2M` | $\%$ | 2-meter relative humidity percentage. |

### 2.3 Operational Risk
If the competition evaluation test set `test.csv` comes pre-populated with weather variables sourced from Open-Meteo, models trained on NASA POWER variables will suffer domain shift, particularly on `soil_moisture` (`GWETTOP` vs volumetric).

**Operational Status**: `NEEDS ORGANISER CONFIRMATION` (Whether test features are pre-extracted Open-Meteo or if teams query their own weather APIs).

---

## 3. Competition Scoring Formula & Dimensional Blending

### 3.1 The Ambiguity
The competition documents state that submissions will be evaluated according to:
- **Overall RMSE**: 40% weight
- **Top-10% Peak RMSE**: 30% weight
- **MAE**: 20% weight
- **R²**: 10% weight

### 3.2 The Mathematical Impossibility of Direct Linear Summation
As verified in Phase 2 of our forensic audit:
$$\mathcal{L} = 0.40 \cdot \text{RMSE} + 0.30 \cdot \text{RMSE}_{\text{top10}} + 0.20 \cdot \text{MAE} - 0.10 \cdot R^2$$
is dimensionally invalid:
1. $\text{RMSE}$, $\text{RMSE}_{\text{top10}}$, and $\text{MAE}$ are expressed in physical units: **cubic feet per second ($cfs$)**, with values on the order of $10,000\text{--}150,000\text{ cfs}$.
2. $R^2$ is a unitless, scale-free correlation ratio bounded $(-\infty, 1.0]$. Adding $0.10 \times 0.82 = 0.082$ to $50,000\text{ cfs}$ is completely negligible and mathematically meaningless.
3. If $R^2$ is negative on an unseen basin (e.g. $R^2 = -50.0$), subtracting $0.10 \times R^2$ adds $5.0$ to the loss, which has zero parity with the actual squared discharge error.

### 3.3 Exact Clarification Required
The organizers must clarify the exact platform scoring script:
- Is raw RMSE the sole leaderboard sorting metric during the live event (as indicated in some guidelines)?
- If composite scoring is used, what is the exact normalization formula? (e.g., Normalized RMSE $\text{NRMSE} = \text{RMSE} / \bar{y}$, or ranks, or min-max normalization across participants?)

**Operational Status**: `NEEDS ORGANISER CONFIRMATION`.

---

## 4. River Connectivity Classification

### 4.1 Audited Classifications
In Phase E2, we audited all 34 stations and established four distinct categories of river connectivity:
1. **Verified Upstream/Downstream Mainstem Flow Cascade**:
   - Stations located on the exact same continuous river channel (e.g., Mississippi River: St. Paul $\to$ Clinton $\to$ St. Louis $\to$ Vicksburg; Upper Colorado: Kremmling $\to$ CO-UT $\to$ Lees Ferry).
   - **Evidence**: USGS NHD flow lines, sequential drainage areas, HUC mainstem mapping.
2. **Verified Watershed / Sub-Basin Network**:
   - Stations located on confluent tributaries within the same sub-basin (e.g., Missouri River at Omaha with Platte River at Louisville; Columbia River with Salmon and Willamette rivers; Ohio River with Greenbrier and Wabash rivers).
   - **Evidence**: Shared HUC-2/HUC-4 drainage networks.
3. **Standalone Independent River Basins**:
   - Stations that drain directly into oceans, bays, or terminal lakes without any connection to other dataset gauges (e.g., Potomac River, Susquehanna River, Neuse River, Catawba River, Fox River, Kawishiwi River, Logan River).
   - **Evidence**: Independent coastal or terminal outlets.
4. **Name-Similarity False Friends**:
   - Stations sharing a name but having zero physical or watershed connection:
     - `08158000`: Colorado River at Austin, TX (flows to Matagorda Bay, Gulf of Mexico, HUC 12).
     - `09058000` / `09163500` / `09380000`: Colorado River in CO/UT/AZ (flows to Gulf of California, HUC 14).

**Operational Status**: `VERIFIED` in `reports/river_system_grouping.csv` and `reports/river_system_grouping_audit.md`.

---

## 5. Competition Rules & Submission Constraints

### 5.1 Permitted Training Period
- In our offline validation, we have strictly enforced a training date cutoff: $\text{Date} \le 2021\text{-}12\text{-}31$.
- Held-out evaluation is strictly $2022\text{-}01\text{-}01$ to $2023\text{-}12\text{-}31$.
- **Unconfirmed**: What will be the exact calendar test period in the organizers' `test.csv`?

### 5.2 External Data-Source Restrictions
- Rule 8 states: *"No pre-trained competition model may be submitted. The final competition model must be trained during the authorised hackathon window."*
- Rule 1 states: *"All data must be real... Never fabricate, simulate, interpolate-to-fill, or mock discharge values."*
- **Unconfirmed**: Will organizers allow training on our 29 additional verified USGS stations, or must models be trained strictly on the 5 core stations?

### 5.3 Final Submission Requirements
- Format: `predictions.csv` with columns `(station_id, date, discharge_cfs)`.
- No negative predictions ($\ge 0.0\text{ cfs}$).
- Docker container / inference script requirements: Unconfirmed whether inference code or only CSV predictions must be uploaded.

---

## 6. Master Blocker & Clarification Register

| Blocker ID | Description | Existing Project Evidence | Effect on Model Validity | Exact Clarification Required | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **BLK-01** | Target Definition: Daily Mean (`00003`) vs Peak Crest (`00001`) | Full master dataset uses USGS `00060_00003`. Exploratory download of `08158000` confirms `00060_00001` exists for some stations. | If target is daily maximum, daily mean models will underpredict flood crests by 50–300%. | Confirm whether competition target `discharge_cfs` is USGS daily mean (`00060_00003`) or daily maximum (`00060_00001`). | `NEEDS ORGANISER CONFIRMATION` |
| **BLK-02** | Weather Data API: NASA POWER vs Open-Meteo | Open-Meteo returned HTTP 429 quota exhaustion. NASA POWER used uniformly across all 34 stations. | Discrepancy in soil moisture units ($m^3/m^3$ vs saturation fraction) could cause feature shift if test set provides Open-Meteo data. | Confirm whether test weather is pre-supplied or queried by teams, and approve NASA POWER fallback. | `NEEDS ORGANISER CONFIRMATION` |
| **BLK-03** | Composite Metric Scoring Formula | Current implementation in `metrics.py` sums dimensional $cfs$ errors with weights 0.40, 0.30, 0.20, omitting $R^2$. | Inability to reproduce exact leaderboard score without the organizers' normalization denominator. | Provide exact code snippet or formula for leaderboard score calculation and metric normalization. | `NEEDS ORGANISER CONFIRMATION` |
| **BLK-04** | Station Scope for Final Training | 34 stations downloaded, cleaned, and verified (170,817 rows); 5 core stations identified. | If training is restricted to 5 core stations, models trained on 34 stations will be disqualified. | Confirm whether models may train on additional verified USGS stations or strictly the 5 core stations. | `NEEDS ORGANISER CONFIRMATION` |
| **BLK-05** | River System Grouping Integrity | 23 river systems defined; 6 multi-station cascades verified with zero-network leakage. | Strategy C previously leaked upstream Mississippi flow; Prompt E resolves this via LORSO. | Fully resolved internally. Awaiting validation results under LORSO. | `VERIFIED` |

---

## 7. Provisional Operational Guidance

Until official clarification is received from the hackathon organizers:
1. **Target**: Continue using USGS parameter `00060_00003` (daily mean discharge in $cfs$) as the provisional gold-standard continuous target.
2. **Weather**: Continue using NASA POWER MERRA-2 meteorological features uniformly.
3. **Validation**: Treat all Leave-One-River-System-Out (LORSO) validation metrics as **provisional benchmarks**.
4. **Model Selection**: Evaluate models based on separate, uncombined metrics (RMSE, Peak RMSE, MAE, R²) rather than an unnormalized composite loss.

