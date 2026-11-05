# PRAVAHA — Technical Judge Q&A Defense Dossier
**Project**: PRAVAHA (प्रवाह) — "PREDICT THE SURGE. PROTECT THE PEOPLE."  
**Deliverable**: 22 Anticipated Technical, Mathematical, and Architectural Judge Questions  
**Date**: November 2026  
**Audience**: Technical Hackathon Evaluation Jury  

---

## 1. Project Philosophy & Value Proposition

### Q1: What makes PRAVAHA fundamentally different from conventional flood forecasting models?
**Answer**:
> *"Most ML flood models are trained and tested on the exact same river gauges using auto-regressive streamflow lags—meaning they simply predict tomorrow's flow from today's flow. While that achieves high benchmark scores on known rivers, it completely collapses when transferred to an ungauged basin or when a gauge is destroyed by a flood.
> 
> PRAVAHA addresses **true out-of-system spatial transfer**. We use zero streamflow lags, relying strictly on physics-informed weather dynamics and static catchment physiography. By normalising discharge by drainage area ($q = Q/A$), we enable a single model to generalize across completely unseen river systems spanning mountain creeks to continental trunks."*

### Q2: Why did you name the platform "PRAVAHA"?
**Answer**:
> *"PRAVAHA is the ancient Sanskrit word for 'continuous flow' or 'stream' (प्रवाह). It embodies both the continuous physical dynamics of hydrology and our architectural commitment to seamless, uncorrupted data flow from satellite reanalysis to responder screens. Our tagline is 'Predict the Surge. Protect the People.'"*

---

## 2. Machine Learning & Hydrological Mathematics

### Q3: Why did you choose LightGBM over Deep Learning (LSTMs / Transformers) or classical hydrological models like HEC-HMS?
**Answer**:
> *"In our initial benchmarking (Phases B and C), we compared linear models (Ridge Regression), gradient-boosted decision trees (LightGBM and XGBoost), and tested complex architectures.
> 
> Gradient-boosted decision trees, particularly LightGBM, offer three decisive advantages in a 24-hour rapid deployment context:
> 1. **Robust Tabular Performance**: Gradient trees consistently outperform deep learning on heterogeneous tabular data with mixed continuous weather features and static catchment physiography.
> 2. **Invariance to Monotonic Feature Scaling**: Tree splits handle non-linear antecedent rainfall and soil moisture saturation without sensitivity to feature scale distortion.
> 3. **Computational Efficiency**: Training a 23-fold spatial cross-validation benchmark on 170,000 rows takes less than 2 seconds with LightGBM, enabling rapid forensic auditing and multi-formulation comparison that would require hours on deep recurrent networks."*

### Q4: Explain the mathematical intuition behind Specific Discharge ($q = Q / A$). Why does it work?
**Answer**:
> *"In hydrology, raw streamflow ($Q$, in $cfs$) scales primarily with watershed catchment area ($A$, in $sq\ mi$). If a model trained on a 100,000-square-mile river encounters a 1,000-square-mile river, a tree predicting raw discharge will predict baseflows of 10,000 cfs—which is physically impossible for the small basin.
> 
> Specific discharge ($q = Q / A$) measures the **areal runoff yield**—how many cubic feet per second of streamflow is generated per square mile of drainage area. A typical rainfall event generates $0.2\text{ to }2.0\text{ cfs/sq mi}$ whether the river is large or small. By predicting $q$ and then multiplying by the target river's verified drainage area ($\hat{Q} = \hat{q} \times A$), we decouple the hydrological runoff physics from the spatial scale of the basin."*

### Q5: Why did you apply a logarithmic transformation $\log(q + 1)$ to specific discharge?
**Answer**:
> *"Streamflow distributions are notoriously heavy-tailed and right-skewed. Raw specific discharge can span from $0.001\text{ cfs/sq mi}$ in arid baseflow to over $20.0\text{ cfs/sq mi}$ in a flash flood.
> 
> In raw linear space, gradient tree algorithms minimize squared error by focusing overwhelmingly on extreme outliers, creating unstable splits that overpredict quiescent baseflows. The transform $y = \log(q + 1)$ stabilizes variance across orders of magnitude, optimizing percentage error rather than raw scale. In our LORSO benchmark, this reduced Overall RMSE from $86,836\text{ cfs}$ down to **$82,871\text{ cfs}$** and improved Pooled $R^2$ from $0.4411$ to **$0.4910$**."*

### Q6: If $\log(q + 1)$ is so effective, why did linear Specific Discharge (`spec_q`) outperform it on extreme flood peaks?
**Answer**:
> *"That was one of the most critical discoveries in our Prompt F forensic audit. 
> 
> Logarithmic transformations are strictly concave—they compress the upper tail. When an unprecedented, catastrophic flood occurs (such as a 100-year crest), the gradient of the log-transformed loss function becomes very small, causing tree models to underpredict the crest peak.
> 
> Linear specific discharge (`spec_q`) maintains a constant loss gradient across the entire flow range. Consequently, on the top-10% extreme flood days, `spec_q` achieved the lowest peak error (**$155,136.8\text{ cfs}$** vs $156,593.8\text{ cfs}$ for log) and cut error on the top-20 mega-flood events by over $158,000\text{ cfs}$. This is why our recommended architecture is a **dual-branch blended ensemble** ($70\%$ `log_spec_q` for baseline volume stability, $30\%$ `spec_q` for peak responsiveness)."*

---

## 3. Validation Integrity & Data Leakage Prevention

### Q7: What is Leave-One-River-System-Out (LORSO) validation, and why was it necessary?
**Answer**:
> *"In Prompt D, our forensic audit revealed that standard Leave-One-Station-Out cross-validation was fundamentally compromised by **advective river connectivity**. For example, the Mississippi River has four gauges in our dataset: St. Paul, Clinton, St. Louis, and Vicksburg. If you hold out Vicksburg while keeping St. Louis in training, the model isn't learning rainfall-runoff physics—it is simply learning that water at St. Louis reaches Vicksburg 3 days later.
> 
> To eliminate this leakage, we grouped all 34 stations into **23 hydrologically isolated river systems**. In our LORSO benchmark, when a river system is held out, **every single connected upstream and downstream gauge is completely removed from the training set**. The model is forced to predict on a river basin it has never seen before."*

### Q8: How can you prove that your feature engineering pipeline has zero target leakage?
**Answer**:
> *"Our feature engineering module (`src/features/engineering.py`) enforces a strict architectural rule: **zero target-derived features**.
> 
> All 48 features are computed exclusively from exogenous meteorology—such as 1-day to 60-day antecedent precipitation sums, exponential decay Antecedent Precipitation Index (API $k=0.85$ and $k=0.90$), degree-day snowmelt proxies, and soil moisture trends—combined with static catchment attributes (drainage area, elevation, slope, forest cover). We use zero streamflow lags, zero moving averages of discharge, and zero upstream gauge telemetry. The target discharge variable is completely uncoupled from model inputs."*

### Q9: Why is Pooled R² (+0.4910) positive while Macro R² (-87.66) is negative? Isn't a negative R² a sign of model failure?
**Answer**:
> *"This is a vital distinction in continental hydrological statistics.
> 
> **Macro R²** calculates $R^2$ independently for each station and takes an unweighted average. On small, highly regulated, or arid rivers—like the Pecos River in New Mexico or the Texas Colorado below Mansfield Dam—discharge variance during drought periods is virtually zero. When true variance $\sigma^2 \approx 0$, any slight numerical prediction offset creates an astronomically large negative $R^2$ (e.g., $-1,200$), which destroys an unweighted arithmetic mean.
> 
> **Pooled R²** evaluates all 24,088 predictions across the continent simultaneously:
> 
> $$R^2_{\text{pooled}} = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$
> 
> A Pooled $R^2$ of **+0.4910** means that across 24,088 out-of-system predictions in diverse climates, our model explains roughly half of the total hydrological variance across the continent without seeing a single gauge measurement from the target rivers."*

### Q10: Why does the Mississippi River at Vicksburg account for 81.8% of the total pooled squared error?
**Answer**:
> *"Because squared error scales quadratically with discharge volume. 
> 
> The Mississippi at Vicksburg drains a staggering **1,144,500 square miles**—nearly 40% of the continental United States. Its flood crests exceed **1.23 million cfs**. An error of 25% on Vicksburg is 300,000 cfs, which when squared ($300,000^2 = 9 \times 10^{10}$) completely dwarfs the squared error of a river flowing at 2,000 cfs.
> 
> For 30 out of our 33 evaluated stations, individual RMSE is below 35,000 cfs, and the **median station MAE across the entire network is just 2,623 cfs**."*

---

## 4. Datasets & Unresolved Competition Requirements

### Q11: What is the target variable? Is it daily mean discharge or daily maximum discharge?
**Answer**:
> *"Our master dataset targets **USGS daily mean discharge: parameter `00060`, statistic `00003`** in cubic feet per second ($cfs$).
> 
> We identified this as an unconfirmed competition ambiguity in `reports/unresolved_competition_questions.md`. The problem statement refers to 'peak daily discharge', but in federal hydrology, instantaneous daily maximum (`00060_00001`) is only calculated for a small fraction of USGS stations, whereas daily mean (`00060_00003`) is the universal continental benchmark standard (170,817 continuous records in our dataset).
> 
> We have provisionally calibrated on daily mean discharge, and we have formally flagged this requirement for organizer confirmation."*

### Q12: Why did you use NASA POWER MERRA-2 weather data instead of Open-Meteo as specified in the hackathon brief?
**Answer**:
> *"During Phase A data ingestion, querying Open-Meteo across 34 stations and 14 years exhausted their free public rate limit (10,000 requests/day), returning **HTTP 429 Too Many Requests** with a 7.7-hour retry delay.
> 
> Rather than using synthetic mock data or halting pipeline development, our team pivoted to **NASA POWER MERRA-2 satellite reanalysis**. NASA POWER provided 100% verified, unbroken daily meteorology across all 34 basins. 
> 
> We documented this transparently in `reports/unresolved_competition_questions.md`. We also audited the feature scales: NASA POWER reports topsoil wetness as a saturation fraction (0.0 to 1.0), whereas Open-Meteo reports volumetric soil moisture ($m^3/m^3$, 0.05 to 0.45). If the organizers supply pre-extracted Open-Meteo features in the test set, we have already developed a linear calibration transform to bridge the scales."*

### Q13: How many stations are in your project? Why do some reports mention 38, others 34, and validation reports 33?
**Answer**:
> *"We investigated this exact discrepancy in our forensic audit (`reports/PPT_FACT_CHECK_REGISTER.md`):
> 
> 1. **38 stations** was our initial exploratory candidate metadata catalogue (`reports/verified_station_catalog.csv`).
> 2. **34 stations** had continuous, verified USGS records and were successfully downloaded into our master training dataset `PRAVAHA_TRAIN_LABELLED.csv` (170,817 rows).
> 3. **33 stations** were evaluated in our 2022–2023 LORSO holdout benchmark. The 34th station—Sacramento River at Freeport (`11447650`)—has historical USGS records ending on September 30, 2015, meaning it had zero rows in the modern 2022–2023 validation window.
> 
> Every number has an exact physical explanation, and our slide deck strictly uses **34 stations in the dataset** and **33 evaluated in the holdout**."*

### Q14: How does PRAVAHA handle missing data?
**Answer**:
> *"Strictly without fabrication. Across our 173,842 master records, exactly 3,025 rows (1.74%) had missing USGS discharge measurements. Rather than forward-filling, mean-imputing, or inventing synthetic values, these rows were segregated into `data/processed/PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv`.
> 
> In the frontend, our dynamic SVG hydrographs render **genuine gaps in the curve**—using SVG `M` break commands—so responders never mistake a missing gauge observation for zero flow or interpolated data."*

---

## 5. Software Architecture & Full-Stack Implementation

### Q15: How do the React frontend and FastAPI backend communicate?
**Answer**:
> *"The React frontend communicates via asynchronous HTTP REST calls using a centralized, typed client (`frontend/src/services/apiClient.ts`).
> 
> The backend exposes five core endpoints: `/api/health`, `/api/stations`, `/api/stations/{id}`, `/api/stations/{id}/hydrograph`, and `/api/validation/leaderboard`. 
> 
> When a user selects a station in the UI, React custom hooks (`useStation`, `useHydrograph`, `useCatchmentProfile`) trigger parallel non-blocking fetch queries to FastAPI on `http://127.0.0.1:8000`. The backend reads directly from in-memory cached Parquet and CSV files, delivering sub-50-millisecond response times without database latency."*

### Q16: What is the PRAVAHA Truth Engine?
**Answer**:
> *"The Truth Engine is our architectural commitment to scientific honesty and transparency in the user interface.
> 
> In standard AI dashboards, models frequently project continuous, smooth curves even when underlying data is missing or unverified. The Truth Engine prevents this by:
> 1. Displaying prominent data limitation alerts (e.g. for the Sacramento gauge where records end in 2015).
> 2. Breaking hydrograph SVG lines across missing observation periods rather than interpolating.
> 3. Clearly labeling all evaluation simulation modules (alerts, citizen reports, NGO logistics) with visible `[DEMO]` badges.
> 4. Displaying verified GAGES-II catchment source tiers and limitation commentary on every basin."*

### Q17: Are the emergency alert notifications (SMS, WhatsApp, sirens) live or simulated?
**Answer**:
> *"They are **prototype scenario simulations**. 
> 
> In a 24-hour hackathon, triggering live cellular emergency broadcasts or commercial WhatsApp Business APIs without municipal authority would be unethical and unsafe. We built the dispatch logic, the geofenced radius calculations, and the multi-channel pipeline, but it operates in safe simulation mode with explicit `TruthBanner` disclaimers. 
> 
> If approved for deployment, the backend is architectured to connect directly to standard CAP (Common Alerting Protocol) gateways."*

---

## 6. Limitations, Deployment & Future Roadmap

### Q18: What is PRAVAHA's single biggest technical limitation today?
**Answer**:
> *"Our biggest limitation is **regulated river generalisation**.
> 
> On rivers immediately downstream of major multi-purpose dams—like the Texas Colorado below Mansfield Dam (`08158000`) or the Colorado River below Glen Canyon Dam (`09380000`)—streamflow is governed by human reservoir release schedules and hydroelectric power generation, not natural meteorology. Because our models rely on meteorological precipitation and terrain slope, they cannot predict an unannounced dam gate opening.
> 
> To solve this, our post-hackathon roadmap incorporates US Army Corps of Engineers (USACE) and Bureau of Reclamation daily reservoir storage and release telemetry."*

### Q19: Does PRAVAHA currently generate future operational forecasts?
**Answer**:
> *"No, and we are careful not to claim that it does. 
> 
> In this phase of the competition, PRAVAHA operates as an **out-of-system historical validation engine**. We evaluate models on historical 2022–2023 holdout periods to prove spatial generalisation. 
> 
> The endpoint `POST /api/predict` has been deliberately postponed until the hackathon organisers clarify the exact competition test set format, target parameter (`00060_00003` vs `00060_00001`), and weather data sourcing permissions."*

### Q20: How would PRAVAHA be deployed in a real-world emergency operations center?
**Answer**:
> *"In a real-world setting, PRAVAHA would operate as a lightweight, containerized microservice:
> 1. A scheduled ingestion worker queries NOAA High-Resolution Rapid Refresh (HRRR) or National Water Model (NWM) quantitative precipitation forecasts (QPF) every 6 hours.
> 2. The feature pipeline computes antecedent decay and specific discharge yield across regional watersheds.
> 3. The FastAPI inference engine generates 24h to 72h streamflow forecasts and flags gauges crossing local 90th percentile hazard stages.
> 4. Emergency managers use the interactive map and dashboard to coordinate levee reinforcements, trigger geofenced cell broadcasts via municipal CAP servers, and position mutual-aid watercraft before flood crest arrival."*

### Q21: How do you handle extreme events on small rivers where flash flooding occurs in hours rather than days?
**Answer**:
> *"Daily mean discharge (`00060_00003`) integrated over 24 hours can smooth out sub-daily flash flood peaks on steep, small catchments. 
> 
> While daily mean models are appropriate for regional basin coordination, capturing flash flood crests on steep creeks requires sub-daily telemetry—specifically instantaneous 15-minute USGS streamgauge records and hourly precipitation radar. Our specific discharge methodology ($q = Q/A$) directly applies to hourly runoff rates, and extending the pipeline to 15-minute USGS data is a priority milestone in our future roadmap."*

### Q22: What is your team's immediate next step if you win or advance in this hackathon?
**Answer**:
> *"Our immediate next milestone is:
> 1. Obtain official organiser clarification on the three open questions: target parameter code, external weather permissions, and test set format.
> 2. Train our final dual-branch ensemble ($70\%$ LightGBM `log_spec_q` + $30\%$ `spec_q`) on the permitted training scope.
> 3. Generate the verified, zero-negative `predictions.csv` submission file.
> 4. Package the FastAPI backend and React frontend into a reproducible Docker Compose environment for final submission review."*

