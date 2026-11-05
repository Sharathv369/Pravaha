# PRAVAHA Data Dictionary & Variable Provenance

This document provides a comprehensive audit of all parameters downloaded and processed for PRAVAHA, including source codes, definitions, distributions, and mapping to the FLOODCAST competition schema.

---

## 1. Parameters in Downloaded & Processed Datasets

| Column Name | Dataset | Original Field Code | Plain-English Meaning | Unit | Data Type | Min / Median / Max | % Missing | Example Value | Organizer Schema Column? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`station_id`** | USGS NWIS / Processed | `site_no` | Unique 8-digit USGS station identifier | Dimensionless | `string` / `int64` | `01646500` / `07010000` / `11447650` | 0.00% | `01646500` | **`station_id`** |
| **`date`** | All Datasets / Processed | `dateTime` / `date` | Calendar date of observation | YYYY-MM-DD | `string` | `2010-01-01` / `2016-12-31` / `2023-12-31` | 0.00% | `2010-01-01` | **`date`** |
| **`discharge_cfs`** | USGS NWIS Daily Values | `00060` (stat `00003`) | Mean daily stream discharge rate | $\text{ft}^3/\text{s}$ (cfs) | `float64` | `43.50` / `3,870.00` / `931,000.00` | 11.79% | `22,100.0` | **`discharge_cfs`** |
| **`precipitation_mm`** | NASA POWER Daily Point | `PRECTOTCORR` | Bias-corrected daily total precipitation | mm/day | `float64` | `0.00` / `0.04` / `202.21` | 0.00% | `0.24` | **`precipitation_mm`** |
| **`temp_max_c`** | NASA POWER Daily Point | `T2M_MAX` | Daily maximum air temperature at 2m height | °C | `float64` | `-16.81` / `23.59` / `48.10` | 0.00% | `4.14` | **`temp_max_c`** |
| **`temp_min_c`** | NASA POWER Daily Point | `T2M_MIN` | Daily minimum air temperature at 2m height | °C | `float64` | `-23.00` / `10.98` / `28.60` | 0.00% | `-3.29` | **`temp_min_c`** |
| **`soil_moisture`** | NASA POWER Daily Point | `GWETTOP` | Surface topsoil wetness (0–5 cm depth) | Dimensionless fraction (0–1) | `float64` | `0.09` / `0.63` / `0.98` | 0.00% | `0.87` | **`soil_moisture`** |
| **`weather_source`** | Provenance Tracking | N/A | Provider flag for meteorological observations | String | `string` | N/A (Categorical) | 0.00% | `NASA_POWER_MERRA2` | No (Audit column) |
| **`drainage_area_sqmi`** | StreamStats / GAGES-II | `DRNAREA` / `CONTDA` | Upstream contributing catchment drainage area | $\text{sq mi}$ | `float64` | `1,150.00` / `23,500.00` / `697,000.00` | 0.00% | `11,560.0` | **`drainage_area_sqmi`** |
| **`mean_elevation_ft`** | StreamStats / GAGES-II | `ELEV` / `ELEV_MEAN_M_BASIN` | Mean catchment elevation above sea level | ft | `float64` | `310.00` / `1,180.00` / `3,280.00` | 0.00% | `1,056.0` | **`mean_elevation_ft`** |
| **`slope_pct`** | StreamStats / GAGES-II | `BSLD_PCT` / `BSLOPGM` | Average topographical basin slope | % | `float64` | `3.20` / `4.10` / `14.20` | 0.00% | `8.40` | **`slope_pct`** |
| **`forest_cover_pct`** | StreamStats / GAGES-II | `FOREST` / `FOR_PCT` | Catchment surface covered by forest canopy | % | `float64` | `14.50` / `44.10` / `58.20` | 0.00% | `58.20` | **`forest_cover_pct`** |
| **`quality_cd`** | USGS NWIS Daily Values | `qualifiers` | USGS measurement validation status code | Code (`A`, `P`, `e`) | `string` | N/A (Categorical) | 11.79% | `A` (Approved) | No (Preserved in raw) |
| **`latitude`** | USGS NWIS Site Service | `dec_lat_va` | Gage station geographic latitude | Decimal degrees | `float64` | `30.2458` / `38.4557` / `38.9498` | 0.00% | `38.9498` | No (Site metadata) |
| **`longitude`** | USGS NWIS Site Service | `dec_long_va` | Gage station geographic longitude | Decimal degrees | `float64` | `-121.5011` / `-90.1796` / `-77.1276` | 0.00% | `-77.1276` | No (Site metadata) |
| **`station_name`** | USGS NWIS Site Service | `station_nm` | Official USGS river station description | Text | `string` | N/A (5 names) | 0.00% | `POTOMAC RIVER NEAR WASH, DC...` | No (Site metadata) |
| **`state_code`** | USGS NWIS Site Service | `state_cd` | FIPS two-digit state numeric code | Code | `string` | `06` / `29` / `48` | 0.00% | `24` (MD) | No (Site metadata) |

---

## 2. Dataset-Specific Breakdown

### 2.1 USGS NWIS Daily Discharge (`data/raw/usgs/*_discharge_*.json`)
- **Source**: USGS National Water Information System (NWIS) Daily Values REST API.
- **Downloaded Fields**:
  - `dateTime`: ISO timestamp representing the local calendar date.
  - `value`: Daily mean discharge rate in cubic feet per second (`00060`, stat `00003`). Negative or `-999999` values represent missing data and are kept as `NaN`.
  - `qualifiers`: Data quality flags assigned by USGS hydrographers (`A` = Approved, `P` = Provisional, `e` = Value estimated).
- **Missing Data Note**: 3,015 total days are missing out of 25,565 (11.79%). 3,014 of these missing days belong to Station `11447650` (Sacramento at Freeport), where official daily mean computation ceased after September 30, 2015. Exactly 1 missing day belongs to Station `08158000` (Colorado at Austin) on `2017-01-26`.

### 2.2 USGS Station Metadata (`data/raw/usgs/*_site_meta.rdb`)
- **Source**: USGS NWIS Site Web Service (Expanded Tab-Delimited RDB format).
- **Downloaded Fields**:
  - `agency_cd`: "USGS".
  - `site_no`: 8-digit station identification number.
  - `station_nm`: Geographic station designation.
  - `site_tp_cd`: Site type code (`ST` = Stream).
  - `dec_lat_va` / `dec_long_va`: High-precision latitude and longitude (NAD83 datum).
  - `state_cd` / `county_cd`: FIPS jurisdiction codes.
  - `alt_va`: Gage orifice datum elevation (NGVD29 feet).
  - `huc_cd`: 8-digit Hydrologic Unit Code.
  - `drain_area_va`: Drainage area reported in the USGS station master file.

### 2.3 Weather Data: NASA POWER vs. Open-Meteo
- **NASA POWER Daily API (`data/raw/weather/*_nasapower_*.json`)**:
  - `PRECTOTCORR`: MERRA-2 bias-corrected total precipitation in mm/day.
  - `T2M_MAX` / `T2M_MIN`: Maximum and minimum air temperatures at 2m above ground in °C.
  - `GWETTOP`: Surface soil wetness fraction in the 0–5 cm layer (dimensionless fraction, 0.0 to 1.0).
- **Open-Meteo Archive API**:
  - Targeted parameters: `precipitation_sum` (daily mm), `temperature_2m_max` (°C), `temperature_2m_min` (°C), and `soil_moisture_0_to_7cm` (hourly volumetric water content $\text{m}^3/\text{m}^3$, aggregated to daily mean).
  - *Status*: Open-Meteo hit free-tier daily rate exhaustion (`HTTP 429 Too Many Requests`). NASA POWER was engaged as the empirical, un-interpolated fallback.

### 2.4 Catchment Basin Attributes (`data/raw/streamstats/*_streamstats.json` & GAGES-II)
- **USGS StreamStats GageStatsServices**:
  - `DRNAREA`: Drainage area in square miles. (Found in 01646500, 02087500, 07010000; coded as `CONTDA` in 08158000).
  - `ELEV`: Mean basin elevation in feet (Available for 02087500).
  - `BSLD_PCT` / `BSLOPGM` / `BSLOPCM`: Basin slope percentage (Available for 02087500, 08158000).
  - `FOREST`: Basin forest cover percentage (Available for 02087500).
- **USGS GAGES-II Benchmark Dataset (ScienceBase)**:
  - Benchmark authoritative values used where StreamStats services do not provide comprehensive delineation for large or tidal basins (e.g. Mississippi continental reach `07010000` and Sacramento delta reach `11447650`).

---

## 3. Parameters Available from Sources but NOT Downloaded

The following variables exist in the official APIs/sources but have not yet been downloaded. Each is evaluated for its potential hydrological utility:

| Source | Parameter Code / Name | Description | Hydrological Prediction Value / Assessment |
| :--- | :--- | :--- | :--- |
| **NASA POWER** | `ALLSKY_SFC_SW_DWN` | All-Sky Surface Shortwave Downward Irradiance ($\text{MJ}/\text{m}^2/\text{day}$) | **High (Snowmelt/ET)**: Directly controls net radiation available for snowpack melting in alpine basins (Sacramento, Colorado) and potential evapotranspiration. |
| **NASA POWER** | `GWETROOT` | Root-Zone Soil Wetness (0–100 cm depth, fraction 0–1) | **High (Runoff Generation)**: Deep infiltration capacity dictates whether heavy rainfall produces surface runoff or percolates into deep storage. |
| **NASA POWER** | `RH2M` | Relative Humidity at 2 Meters (%) | **Moderate**: Indicates atmospheric moisture deficit; affects evaporation and pre-storm atmospheric saturation. |
| **NASA POWER** | `WS2M` | Wind Speed at 2 Meters ($\text{m}/\text{s}$) | **Low/Moderate**: Influences aerodynamic conductance in evapotranspiration formulations. |
| **NASA POWER** | `SNODP` | Surface Snow Depth (cm) | **Very High**: Crucial for snowmelt-dominated rivers; tracks available solid water storage prior to warm spring surge events. |
| **Open-Meteo** | `snowfall_sum` | Daily snowfall volume (liquid water equivalent / cm) | **High**: Distinguishes delayed snowpack accumulation from immediate liquid rainfall runoff. |
| **Open-Meteo** | `et0_fao_evapotranspiration` | Daily reference evapotranspiration (mm) | **High**: Measures catchment moisture loss back to atmosphere between storms. |
| **Open-Meteo** | `soil_temperature_0_to_7cm` | Near-surface soil temperature (°C) | **High (Frozen Ground)**: Sub-zero soil temperature creates an impermeable concrete frost layer, causing extreme flash floods from moderate rain. |
| **StreamStats** | `LC19DEV` | Percent Developed Land (NLCD 2019, %) | **Moderate**: Higher impervious developed cover increases flood hydrograph peak flashiness and reduces lag times. |
| **StreamStats** | `LC19_WOODY` | Percentage of Woody Wetlands (%) | **Moderate**: Wetland attenuation delays flood wave crests and increases natural catchment retention. |
| **StreamStats** | `REGL_INDEX` | Catchment Regulation Index | **High (Flow Attenuation)**: Measures dam storage volume relative to annual runoff; reservoirs heavily alter natural flood peaks. |
| **StreamStats** | `PRECIP` | 30-Year Normal Mean Annual Precipitation (inches) | **Moderate**: Catchment aridity baseline; dry basins require higher antecedent rainfall before initiating runoff. |
| **USGS NWIS** | `00065` | Gage height / River Stage (feet) | **Very High (Stage-Discharge)**: Stage is directly measured by pressure transducers; however, during the hackathon test period, target stage is typically unavailable. |
| **USGS NWIS** | `00010` | Water Temperature (°C) | **Low**: Affects aquatic ecology and viscosity, but minimal impact on discharge prediction. |

