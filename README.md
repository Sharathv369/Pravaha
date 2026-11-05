# PRAVAHA — Hydrologic Intelligence Platform
**FLOODCAST 24-Hour Hackathon** | **Streamflow Regression & Flood Peak Forecasting**  
**API Engine**: FastAPI 0.162.0, Uvicorn, Pydantic v2, Pandas, PyArrow  
**ML Backbone**: LightGBM Log-Specific Discharge (`log_spec_q`) via 23-Fold Leave-One-River-System-Out (LORSO) Validation  

---

## 1. Project Overview

PRAVAHA is an AI-powered hydrological platform engineered for continuous daily streamflow estimation and non-linear flood crest evaluation across 34 verified USGS streamgauging stations.

This repository provides:
1. **FastAPI Backend (`src/api/`)**: A high-performance, read-only RESTful API serving verified station catalogues, historical daily mean discharge records (`00060_00003`), physiographic catchment attributes, and out-of-system LORSO cross-validation predictions.
2. **Offline ML Pipeline (`src/models/`, `src/evaluate/`)**: 23-fold spatial validation benchmarking across 5 distinct model formulations evaluated over 24,088 held-out spatial observations.
3. **React Frontend (`frontend/`)**: An oceanic-themed hydrological operations center developed with React 18, Vite, TypeScript, and Tailwind CSS.

---

## 2. Backend Architecture

The backend application is structured under `src/api/`:

```
src/api/
├── main.py                    # FastAPI entry point, CORS middleware, global error handling
├── config.py                  # Immutable path resolution, model aliases, FIPS state lookup
├── schemas.py                 # Pydantic v2 data models with strict validation
├── dependencies.py            # Service dependency providers
├── services/                  # In-memory cached data access layer
│   ├── station_service.py     # USGS station registry, search, and statistical percentiles
│   ├── hydrograph_service.py  # Continuous daily time-series & validation prediction joins
│   ├── validation_service.py  # LORSO leaderboard rankings and 23 river-system analytics
│   └── catchment_service.py   # Physiographic attribute verification & limitation commentary
├── routers/                   # Modular REST API route handlers
│   ├── health.py              # GET /health system readiness probe
│   ├── stations.py            # GET /api/stations, /{id}, /{id}/hydrograph, /{id}/catchment-profile
│   └── validation.py          # GET /api/validation/leaderboard, /api/validation/river-systems
└── tests/
    └── test_api.py            # Automated test suite (25 test cases, 100% pass rate)
```

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.10+ (configured in `.venv`)
- Core dependencies: `fastapi`, `uvicorn`, `pydantic`, `pandas`, `pyarrow`, `httpx`

### 3. Quick Start & Full-Stack Execution

### Prerequisites
- Python 3.10+ (configured in `.venv`)
- Node.js 18+ (tested with Node 20)
- Core Python packages: `fastapi`, `uvicorn`, `pydantic`, `pandas`, `pyarrow`, `httpx`

### 3.1 Start the FastAPI Backend
From the project root:
```bash
# Launch Uvicorn ASGI server
.venv/Scripts/uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```
The API is available at:
- **Base URL**: `http://127.0.0.1:8000/`
- **Interactive Swagger UI**: `http://127.0.0.1:8000/docs`
- **Health Diagnostic Probe**: `http://127.0.0.1:8000/api/health`

### 3.2 Start the React Frontend
In a separate terminal window:
```bash
cd frontend
npm run dev
```
The frontend application will launch at `http://localhost:5173/` and automatically connect to the FastAPI backend at `http://127.0.0.1:8000`.

### 3.3 Run Automated Tests
```bash
# Backend unit test suite (25 automated tests)
.venv/Scripts/python.exe -m unittest src/api/tests/test_api.py -v

# Frontend build verification
npm --prefix frontend run build

# End-to-end integration verification and screenshot capture
.venv/Scripts/python.exe scratch/run_integration_verification.py
```

---

## 4. API Endpoints Reference

### 4.1 Diagnostic Endpoints
- **`GET /`**: Platform sitemap, metadata, and documentation links.
- **`GET /health`**: Diagnostic readiness probe inspecting the availability of 8 essential data files.

### 4.2 USGS Station Endpoints
- **`GET /api/stations`**: Returns verified catalogue of 38 candidate stations.
  - *Query Parameters*: `search` (string), `river_system` (string), `limit` (int), `offset` (int).
- **`GET /api/stations/{station_id}`**: Metadata, coordinates, observation bounds, and statistical percentiles ($q_{25}, q_{50}, q_{75}, q_{90}, \max$).
  - *Path Parameter*: `station_id` (string with leading zeros, e.g. `01646500`).
- **`GET /api/stations/{station_id}/hydrograph`**: Continuous daily streamflow time-series joined with LORSO validation holdout predictions.
  - *Query Parameters*: `start_date` (`YYYY-MM-DD`), `end_date` (`YYYY-MM-DD`), `model_name` (`log_spec_q`, `spec_q`, `raw`, `peak_weighted`, `log1p`).
- **`GET /api/stations/{station_id}/catchment-profile`**: Measured drainage area, elevation, slope, and forest cover with verification tiers and model limitation indicators.

### 4.3 Validation Benchmark Endpoints
- **`GET /api/validation/leaderboard`**: Benchmark rankings across all 5 model formulations under 23-fold spatial cross-validation, strictly ordered by Pooled $R^2$.
- **`GET /api/validation/river-systems`**: Per-basin spatial holdout metrics across all 23 independent river system clusters.
  - *Query Parameter*: `model_name` (optional, default: `log_spec_q`).

---

## 5. Authoritative Data Sources

1. **Streamflow Observations**: Authentic USGS National Water Information System (NWIS) daily mean discharge (`00060_00003`) in cubic feet per second (`cfs`) spanning 2010-01-01 through 2023-12-31 (170,817 labeled rows in `data/processed/PRAVAHA_TRAIN_LABELLED.csv`).
2. **Meteorological Reanalysis**: NASA POWER MERRA-2 daily weather (`precipitation_mm`, `temp_max_c`, `temp_min_c`, `soil_moisture` wetness fraction 0–1).
3. **Catchment Physiography**: USGS GAGES-II and USGS StreamStats basin characteristics (`reports/catchment_provenance.csv`).
4. **Validation Benchmark**: Leave-One-River-System-Out (LORSO) 23-fold spatial holdouts (`data/processed/prompt_e_validation_predictions.parquet`, `reports/lors_validation_results.csv`).

---

## 6. Official LORSO Benchmark Results

| Model Formulation | Target Formulation | Pooled $R^2$ | Overall RMSE | Top-10% Peak RMSE | Overall MAE | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **LightGBM Prompt K Optimized (3.5x)** | `log_spec_q` | **0.6090** | **72,626 cfs** | **127,638 cfs** | **23,150 cfs** | **Current Champion** |
| **LightGBM Prompt I Champion (2.5x)** | `log_spec_q` | 0.5964 | 73,793 cfs | 128,553 cfs | 22,887 cfs | Production Baseline |
| **LightGBM Log-Specific Discharge** | `log_spec_q` | 0.4910 | 82,871 cfs | 156,594 cfs | 24,644 cfs | Prompt E Baseline |
| **LightGBM Specific Discharge** | `spec_q` | 0.4411 | 86,837 cfs | 155,137 cfs | 26,092 cfs | Baseline |
| **LightGBM Raw Peak-Weighted (2.5x)** | `raw` | 0.1303 | 108,321 cfs | 202,091 cfs | 32,260 cfs | Baseline |
| **LightGBM Raw Unweighted** | `raw` | 0.1095 | 109,610 cfs | 204,475 cfs | 32,312 cfs | Baseline |
| **XGBoost Log1p** | `log1p` | 0.1057 | 109,842 cfs | 203,656 cfs | 28,996 cfs | Baseline |

---

## 7. Known Limitations & Postponed Features

1. **No Real-Time Ingest**: The API does not establish live HTTP socket streams to external USGS servers.
2. **No Live Inference Endpoint**: `POST /api/predict` is deliberately postponed until final competition model approval.
3. **Regulated Basins**: Stations located immediately downstream of major reservoirs (e.g. `08158000` below Mansfield Dam on the Texas Colorado, `09380000` below Glen Canyon Dam) have negative spatial holdout $R^2$ scores because reservoir release rules cannot be captured purely from meteorological precipitation.
4. **Truncated Historical Records**: Station `11447650` (Sacramento River at Freeport, CA) records end on 2015-09-30 and has 0 modern validation samples for 2022–2023.

