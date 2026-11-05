# PRAVAHA — Frontend-Backend API Contract Draft
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt UI-0 API Specifications Document  
**Date**: November 2026  
**Auditor & Backend Architect**: Lead ML & Backend Systems Engineer  

---

## 1. Architectural Overview & Current State Disclosure

### 1.1 Existing vs Proposed Endpoints Status
- **EXISTING ENDPOINTS**: **ZERO (0)**.  
  The current PRAVAHA codebase is an offline machine learning and data engineering pipeline. While `fastapi`, `uvicorn`, and `pydantic` are listed in `requirements.txt`, no web server or API endpoints currently exist.
- **PROPOSED ENDPOINTS**: **NINE (9)** RESTful endpoints defined below.  
  All proposed endpoints are designed to be served by a lightweight, read-only FastAPI application querying our existing, verified Parquet and CSV datasets in `data/processed/` and `reports/`.

---

## 2. API Contract Specification (Proposed Endpoints)

### Endpoint 1: Station Catalogue & Metadata
- **Route**: `GET /api/stations`
- **Purpose**: Supplies the frontend map and dropdown menus with all verified USGS monitoring stations.
- **Source File**: `reports/verified_station_catalog.csv` merged with `reports/river_system_grouping.csv`.
- **Query Parameters**:
  - `state` (optional, string): Filter by 2-letter state code (e.g., `TX`, `NC`).
  - `river_system` (optional, string): Filter by river system group.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "count": 34,
    "stations": [
      {
        "station_id": "01646500",
        "station_name": "POTOMAC RIVER NEAR WASH, DC LITTLE FALLS PUMP STA",
        "river_name": "Potomac River",
        "river_system": "Potomac River",
        "basin_identifier": "HUC_0207_POTOMAC",
        "state_cd": "MD",
        "latitude": 38.949778,
        "longitude": -77.127639,
        "drainage_area_sqmi": 11564.57,
        "mean_elevation_ft": 1269.03,
        "slope_pct": 11.70,
        "forest_cover_pct": 58.58,
        "is_core_station": true,
        "verification_status": "VERIFIED_BENCHMARK_READY",
        "has_2022_2023_validation": true
      }
    ]
  }
  ```

---

### Endpoint 2: Single Station Detail & Real-Time Status
- **Route**: `GET /api/stations/{station_id}`
- **Purpose**: Provides detailed catchment parameters, latest recorded flow, flood thresholds, and data quality indicators for a selected basin.
- **Source File**: `data/processed/PRAVAHA_TRAIN_LABELLED.csv`.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "station_id": "01646500",
    "station_name": "Potomac River near Washington, DC",
    "river_system": "Potomac River",
    "coordinates": { "latitude": 38.949778, "longitude": -77.127639 },
    "catchment": {
      "drainage_area_sqmi": 11564.57,
      "mean_elevation_ft": 1269.03,
      "slope_pct": 11.70,
      "forest_cover_pct": 58.58
    },
    "flow_thresholds_cfs": {
      "q50_median": 4820.0,
      "q90_flood_threshold": 24800.0,
      "historical_max_recorded": 194000.0
    },
    "latest_observation": {
      "date": "2023-12-31",
      "discharge_cfs": 14200.0,
      "precipitation_mm": 4.2,
      "temperature_mean_c": 6.8,
      "soil_moisture_wetness": 0.74,
      "current_risk_level": "ADVISORY"
    },
    "data_quality": {
      "target_parameter": "USGS_00060_00003_DAILY_MEAN",
      "weather_source": "NASA_POWER_MERRA2",
      "target_imputed": false,
      "quality_code": "APPROVED"
    }
  }
  ```

---

### Endpoint 3: Hydrograph & Out-of-System Model Predictions
- **Route**: `GET /api/stations/{station_id}/hydrograph`
- **Purpose**: Returns the daily historical time-series alongside our models' out-of-system predictions for rendering Recharts dual-curve hydrographs.
- **Source File**: `data/processed/prompt_e_validation_predictions.parquet`.
- **Query Parameters**:
  - `start_date` (optional, default: `2022-01-01`): Earliest date.
  - `end_date` (optional, default: `2023-12-31`): Latest date.
  - `model` (optional, default: `LightGBM Log-Specific Discharge`): Model name.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "station_id": "01646500",
    "model_name": "LightGBM Log-Specific Discharge",
    "target_formulation": "log_spec_q",
    "validation_regime": "LEAVE_ONE_RIVER_SYSTEM_OUT",
    "unit": "cfs",
    "q90_threshold_cfs": 24800.0,
    "time_series": [
      {
        "date": "2022-01-01",
        "actual_discharge_cfs": 12800.0,
        "predicted_discharge_cfs": 13410.5,
        "absolute_error_cfs": 610.5,
        "is_flood_peak": false
      },
      {
        "date": "2022-01-02",
        "actual_discharge_cfs": 26900.0,
        "predicted_discharge_cfs": 25120.0,
        "absolute_error_cfs": 1780.0,
        "is_flood_peak": true
      }
    ]
  }
  ```

---

### Endpoint 4: Probabilistic Uncertainty Intervals (Quantile Regression)
- **Route**: `GET /api/stations/{station_id}/uncertainty`
- **Purpose**: Delivers the validated $p10$, $p50$, and $p90$ empirical quantile bounds (from Phase C4) to render probabilistic flood risk envelopes.
- **Source File**: `data/processed/model_predictions_val.parquet`.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "station_id": "01646500",
    "nominal_coverage_target_pct": 80.0,
    "empirical_achieved_coverage_pct": 72.1,
    "mean_interval_width_cfs": 10445.3,
    "time_series": [
      {
        "date": "2022-01-01",
        "actual_cfs": 12800.0,
        "p10_lower_bound_cfs": 8200.0,
        "p50_median_expectation_cfs": 13100.0,
        "p90_upper_surge_bound_cfs": 18645.0,
        "is_inside_interval": true
      }
    ]
  }
  ```

---

### Endpoint 5: LORSO Model Validation Benchmark Leaderboard
- **Route**: `GET /api/validation/leaderboard`
- **Purpose**: Powers the **Truth Engine Dashboard**, displaying official unnormalized competition metrics across all 5 evaluated architectures.
- **Source File**: `reports/lors_validation_results.csv`.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "evaluation_regime": "LEAVE_ONE_RIVER_SYSTEM_OUT",
    "validation_period": "2022-01-01 to 2023-12-31",
    "total_validation_rows": 24088,
    "total_evaluated_river_systems": 23,
    "active_stations": 33,
    "metrics_unnormalized": true,
    "models": [
      {
        "model_name": "LightGBM Log-Specific Discharge",
        "target_formulation": "log_spec_q",
        "peak_weighted": false,
        "pooled_rmse_cfs": 82871.1,
        "pooled_peak_rmse_cfs": 156593.8,
        "pooled_mae_cfs": 24644.3,
        "pooled_r2": 0.4910,
        "macro_rmse_cfs": 31814.4,
        "macro_mae_cfs": 24642.4
      },
      {
        "model_name": "LightGBM Specific Discharge",
        "target_formulation": "spec_q",
        "peak_weighted": false,
        "pooled_rmse_cfs": 86836.6,
        "pooled_peak_rmse_cfs": 155136.8,
        "pooled_mae_cfs": 26092.0,
        "pooled_r2": 0.4411,
        "macro_rmse_cfs": 34348.2,
        "macro_mae_cfs": 26090.0
      }
    ]
  }
  ```

---

### Endpoint 6: River System Comparison Breakdown
- **Route**: `GET /api/validation/river-systems`
- **Purpose**: Supplies the per-river-system comparative matrix for inspecting geographic generalisation across all 23 systems.
- **Source File**: `reports/prompt_f_river_system_comparison.csv`.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "count": 23,
    "river_systems": [
      {
        "river_system": "Mississippi River Mainstem",
        "n_stations": 4,
        "n_samples": 2920,
        "n_peak_samples": 292,
        "winning_model_rmse": "LightGBM Log-Specific Discharge",
        "lowest_rmse_cfs": 221310.6,
        "winning_model_peak_rmse": "LightGBM Specific Discharge",
        "lowest_peak_rmse_cfs": 401240.2
      }
    ]
  }
  ```

---

### Endpoint 7: Catchment Similarity & Extrapolation Warnings
- **Route**: `GET /api/stations/{station_id}/catchment-profile`
- **Purpose**: Compares a station's drainage area, elevation, slope, and climate against the training corpus to generate **Model Extrapolation Warnings** for users.
- **Source File**: `reports/verified_station_catalog.csv`.
- **Response Schema (`200 OK`)**:
  ```json
  {
    "station_id": "07289000",
    "station_name": "Mississippi River at Vicksburg, MS",
    "drainage_area_sqmi": 1144500.0,
    "is_extrapolation_risk": true,
    "extrapolation_reasons": [
      "Drainage area (1.14M sq mi) exceeds all other training basins by over 300%",
      "Model relies heavily on specific discharge normalization to scale predictions"
    ],
    "catchment_similarity_percentile": 99.8
  }
  ```

---

### Endpoint 8: Model Live Inference (Single Day)
- **Route**: `POST /api/predict`
- **Purpose**: Accepts meteorological inputs for an unseen basin and executes inference through the trained LightGBM `log_spec_q` model.
- **Request Body**:
  ```json
  {
    "drainage_area_sqmi": 4500.0,
    "mean_elevation_ft": 850.0,
    "slope_pct": 4.5,
    "forest_cover_pct": 35.0,
    "precipitation_mm": 45.2,
    "temp_max_c": 22.0,
    "temp_min_c": 14.0,
    "soil_moisture": 0.85,
    "prcp_sum_7d": 112.0
  }
  ```
- **Response Schema (`200 OK`)**:
  ```json
  {
    "predicted_discharge_cfs": 8420.5,
    "predicted_specific_discharge_cfssqmi": 1.871,
    "uncertainty_p10_cfs": 5890.0,
    "uncertainty_p90_cfs": 12400.0,
    "flood_surge_warning": true
  }
  ```

---

### Endpoint 9: Demonstration & Operational Mock Feeds
- **Route**: `GET /api/demo/{module_name}`
- **Purpose**: Serves structured static mock feeds for demonstration modules (Alerts, Community Reports, NGO inventory) with an explicit prototype watermark.
- **Allowed `module_name`**: `alerts`, `community-reports`, `ngo-inventory`.
- **Response Header**: `X-Pravaha-Data-Type: DEMONSTRATION_PROTOTYPE_ONLY`
- **Response Schema (`200 OK`)**:
  ```json
  {
    "module": "community-reports",
    "is_demonstration_data": true,
    "disclaimer": "This feed contains simulated citizen incident reports for UI demonstration.",
    "incidents": [
      {
        "id": "INC-104",
        "timestamp": "2026-11-04T22:15:00Z",
        "basin": "Sacramento River Delta",
        "hazard_type": "BREACHED_LEVEE",
        "water_depth_inches": 36,
        "status": "UNVERIFIED_CROWD_REPORT"
      }
    ]
  }
  ```

---

## 3. Error Handling & Standard Status Codes

| HTTP Status Code | Scenario | JSON Response Shape |
| :---: | :--- | :--- |
| **`400 Bad Request`** | Invalid date format or unrecognized model parameter. | `{"detail": "Invalid model formulation requested. Must be one of: log_spec_q, spec_q, raw"}` |
| **`404 Not Found`** | Requested station ID does not exist in the 34-station catalogue. | `{"detail": "Station '99999999' not found in verified USGS catalogue"}` |
| **`422 Unprocessable`** | Missing required meteorological feature in `/api/predict`. | `{"detail": "Missing required catchment feature: drainage_area_sqmi"}` |
| **`503 Unavailable`** | Parquet data file temporarily unreadable. | `{"detail": "Validation predictions store is currently locked or rebuilding"}` |

