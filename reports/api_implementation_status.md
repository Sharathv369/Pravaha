# PRAVAHA — API Implementation Status Report
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt API-1 Backend Implementation & Architecture Document  
**Date**: November 2026  
**Backend Architect**: Senior Machine Learning & Systems Software Engineer  
**Framework**: FastAPI 0.162.0, Uvicorn 0.54.0, Pydantic v2 (2.14.2), Pandas 2.3.3, PyArrow 25.0.1  
**Status**: Fully Implemented, Tested, and Verified  

---

## 1. Executive Summary

In adherence to the **Prompt API-1** instructions, a modular, high-performance, read-only **FastAPI** backend has been developed and integrated into the existing PRAVAHA Python codebase.

The API exposes verified USGS streamgauging stations, historical continuous daily mean discharge observations (`00060_00003`), physiographic catchment attributes, and out-of-system **Leave-One-River-System-Out (LORSO)** validation predictions without modifying existing datasets, retraining models, or fabricating data.

### Core Achievements
1. **Zero Data Distortion**: All endpoints query immutable local datasets (`data/processed/` and `reports/`). Station IDs retain leading zeros as 8-digit strings (`01646500`).
2. **Clear Scientific Separation**: Historical discharge observations (2010–2023) and held-out validation predictions (2022–2023) are explicitly isolated. Predictions are strictly labeled as historical LORSO holdout evaluations, never as live operational forecasts.
3. **Data Integrity**: JSON responses strictly serialize floating-point numbers without `NaN` or `Infinity`. Missing values evaluate to `null`. Dates are formatted in strict ISO 8601 (`YYYY-MM-DD`).
4. **Comprehensive Test Coverage**: All 25 automated unit tests pass in 0.27s, verifying endpoint responses, parameter validation, edge cases, error conditions, and exact matches against source CSV and Parquet records.

---

## 2. Backend Architecture & Directory Structure

The backend is organized cleanly under `src/api/`:

```
src/api/
├── __init__.py                  # Package declaration
├── config.py                    # Path resolution, model aliases, state FIPS mappings
├── schemas.py                   # Pydantic v2 request/response data contracts
├── dependencies.py              # Dependency injection providers
├── main.py                      # FastAPI app entry point, CORS middleware, error handlers
├── services/                    # In-memory cached data access layer
│   ├── __init__.py
│   ├── station_service.py       # Station catalogue & historical percentile caching
│   ├── hydrograph_service.py    # Hydrograph observations & LORSO prediction joiner
│   ├── validation_service.py    # LORSO leaderboard & 23 river-system analytics
│   └── catchment_service.py     # Physiographic attributes & model limitation profiler
├── routers/                     # HTTP REST routing layer
│   ├── __init__.py
│   ├── health.py                # GET /health readiness probe
│   ├── stations.py              # Station catalogue, detail, hydrograph, catchment
│   └── validation.py            # LORSO leaderboard & river-system analytics
└── tests/                       # Automated test suite
    ├── __init__.py
    └── test_api.py              # 25 comprehensive unit tests (unittest + TestClient)
```

---

## 3. Implemented API Endpoints Directory

| Method | Endpoint Route | Router | Purpose / Return Data | Status Codes |
| :---: | :--- | :--- | :--- | :---: |
| `GET` | `/` | `main.py` | API root information, sitemap, documentation links. | `200` |
| `GET` | `/health` | `health.py` | Diagnostic readiness probe inspecting 8 essential artifact files. | `200`, `503` |
| `GET` | `/api/stations` | `stations.py` | Verified catalogue of 38 candidate stations with search, river system filter, and pagination. | `200`, `503` |
| `GET` | `/api/stations/{station_id}` | `stations.py` | Detailed metadata, coordinates, and historical flow percentiles ($q_{50}$, $q_{90}$). | `200`, `404`, `503` |
| `GET` | `/api/stations/{station_id}/hydrograph` | `stations.py` | Continuous daily discharge series joined with LORSO validation predictions (default: `log_spec_q`). | `200`, `400`, `404`, `503` |
| `GET` | `/api/stations/{station_id}/catchment-profile` | `stations.py` | Verified catchment physiography (area, elevation, slope, forest cover) and model limitation indicator. | `200`, `404`, `503` |
| `GET` | `/api/validation/leaderboard` | `validation.py` | Official LORSO benchmark leaderboard ranking 5 models by Pooled $R^2$ ($0.4910$). | `200`, `503` |
| `GET` | `/api/validation/river-systems` | `validation.py` | Spatial holdout metrics across all 23 independent river system clusters. | `200`, `503` |

---

## 4. Endpoint Specifications & Parameter Details

### 4.1 Health Check (`GET /health`)
- **Query Parameters**: None.
- **Response**:
  ```json
  {
    "status": "healthy",
    "api_title": "PRAVAHA API",
    "api_version": "1.0.0",
    "datasets": {
      "train_labelled": true,
      "station_catalog": true,
      "river_system_grouping": true,
      "catchment_provenance": true,
      "lorso_predictions": true,
      "lorso_results": true,
      "lorso_station_metrics": true,
      "lorso_river_metrics": true
    },
    "verified_station_count": 38,
    "validation_sample_count": 24088,
    "backend_ready": true
  }
  ```

### 4.2 Station Catalogue (`GET /api/stations`)
- **Query Parameters**:
  - `search` (optional string): Case-insensitive search on station ID, name, or river (e.g. `potomac`, `01646500`).
  - `river_system` (optional string): Filter by exact river system name (e.g. `Potomac River`).
  - `limit` (optional integer, 1–100): Pagination limit.
  - `offset` (optional integer, $\ge 0$): Pagination offset.
- **Key Fields**: `station_id` (string), `station_name`, `river_name`, `state`, `latitude`, `longitude`, `drainage_area_sqmi`, `drainage_area_verification_status`, `river_system`, `observation_start`, `observation_end`, `data_quality_status`.

### 4.3 Station Detail (`GET /api/stations/{station_id}`)
- **Path Parameter**: `station_id` (string, e.g. `01646500`). Normalizes 7-digit IDs by padding leading zeros.
- **Key Fields**: Coordinates, drainage area, historical observation date range, `flow_thresholds_cfs` (`min`, `q25`, `q50_median`, `q75`, `q90_threshold`, `max`), and NWIS verification tier.
- **Error**: Returns `404 Not Found` for unrecognized station IDs.

### 4.4 Historical Hydrograph (`GET /api/stations/{station_id}/hydrograph`)
- **Path Parameter**: `station_id` (string).
- **Query Parameters**:
  - `start_date` (optional string, `YYYY-MM-DD`): Lower date bound.
  - `end_date` (optional string, `YYYY-MM-DD`): Upper date bound.
  - `model_name` (optional string, default: `log_spec_q`): Accepts canonical names or formulation aliases (`log_spec_q`, `spec_q`, `raw`, `peak_weighted`, `log1p`).
- **Response Structure**:
  ```json
  {
    "station_id": "01646500",
    "station_name": "POTOMAC RIVER NEAR WASH, DC LITTLE FALLS PUMP STA",
    "model_name": "LightGBM Log-Specific Discharge",
    "target_formulation": "log_spec_q",
    "total_points": 730,
    "start_date": "2022-01-01",
    "end_date": "2023-12-31",
    "disclaimer": "Historical USGS daily mean discharge (00060_00003)...",
    "data": [
      {
        "date": "2022-01-01",
        "station_id": "01646500",
        "actual_discharge_cfs": 3370.0,
        "predicted_discharge_cfs": 7335.50,
        "prediction_model": "LightGBM Log-Specific Discharge",
        "validation_type": "LORSO_HOLDOUT",
        "data_source": "USGS_NWIS_DAILY_MEAN_00060_00003",
        "data_status": "OBSERVED_AND_VALIDATED"
      }
    ]
  }
  ```
- **Error Conditions**: Returns `400 Bad Request` if `start_date > end_date`, if date format is invalid, or if model name is unrecognized.

### 4.5 Catchment Profile (`GET /api/stations/{station_id}/catchment-profile`)
- **Path Parameter**: `station_id` (string).
- **Key Fields**: Per-attribute objects for `drainage_area_sqmi`, `mean_elevation_ft`, `slope_pct`, and `forest_cover_pct`, each detailing `value`, `unit`, `source_dataset`, `verification_status` (`VERIFIED` or `MISSING_OR_UNVERIFIED`), and `explanation`.
- **Model Limitation Indicator**: Factual, audit-backed commentary explaining basin-specific performance (e.g. reservoir control on the Texas Colorado, truncated historical records on the Sacramento River at Freeport, or unverified physiography).

### 4.6 Validation Leaderboard (`GET /api/validation/leaderboard`)
- **Query Parameters**: None.
- **Rankings**:
  1. `LightGBM Log-Specific Discharge` (`log_spec_q`): Pooled $R^2 = 0.4910$, RMSE $= 82,871\text{ cfs}$, Top-10% Peak RMSE $= 156,594\text{ cfs}$, MAE $= 24,644\text{ cfs}$.
  2. `LightGBM Specific Discharge` (`spec_q`): Pooled $R^2 = 0.4411$, RMSE $= 86,837\text{ cfs}$, Top-10% Peak RMSE $= 155,137\text{ cfs}$.
  3. `LightGBM Raw Peak-Weighted (2.5x)` (`raw`): Pooled $R^2 = 0.1303$, RMSE $= 108,321\text{ cfs}$.
  4. `LightGBM Raw Unweighted` (`raw`): Pooled $R^2 = 0.1095$, RMSE $= 109,610\text{ cfs}$.
  5. `XGBoost Log1p` (`log1p`): Pooled $R^2 = 0.1057$, RMSE $= 109,842\text{ cfs}$.

### 4.7 River-System Analytics (`GET /api/validation/river-systems`)
- **Query Parameters**: `model_name` (optional, default: `log_spec_q`).
- **Response**: All 23 independent river system clusters, assigned station IDs, observation sample counts, and holdout error metrics. Explicitly notes zero-sample stations (e.g. `11447650` in the California Central Valley System).

---

## 5. Local Execution Instructions

To launch the PRAVAHA API locally from the project root:

```bash
# Using the project's virtual environment:
.venv/Scripts/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 6. Postponed Features & Strict Boundaries

Per the competition guidelines, the following features are strictly **postponed** and **not implemented**:
1. `POST /api/predict`: Live ML inference is not served without final model sign-off.
2. Real-Time Telemetry: No external polling to live USGS or NOAA feeds.
3. Live Alert Dispatch: No telecom SMS, WhatsApp, or acoustic siren triggering.
4. Disaster Relief Routing: No real NGO inventory or live vehicle dispatch.

