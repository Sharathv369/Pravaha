# PRAVAHA — API Automated Test Execution Results
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt API-1 Test Suite Report  
**Date**: November 2026  
**Test Harness**: Python `unittest` + Starlette `TestClient` (HTTP transport)  
**Test Suite Path**: `src/api/tests/test_api.py`  
**Execution Environment**: Python 3.10.11 on Windows (Virtualenv `.venv`)  
**Result**: 25 Passed, 0 Failed, 0 Errors, 0 Skipped (100% Pass Rate)  
**Execution Time**: 0.268 seconds  

---

## 1. Test Suite Summary Matrix

```
======================================================================
TEST CLUSTER                     TEST COUNT   PASSED   FAILED   STATUS
======================================================================
1. Health & Sitemap Diagnostics           2        2        0   PASS
2. Station Registry & Search              7        7        0   PASS
3. Historical Hydrograph Time-Series      7        7        0   PASS
4. Validation Leaderboard                 2        2        0   PASS
5. River-System Spatial Analytics         1        1        0   PASS
6. Catchment Profiles & Limitations       4        4        0   PASS
7. Ground Truth Data Authenticity         2        2        0   PASS
======================================================================
TOTAL                                    25       25        0   PASS (100%)
======================================================================
```

---

## 2. Granular Test Case Breakdown

### Cluster 1: Health & Sitemap Diagnostics
- `test_health_endpoint_healthy`: Evaluates `GET /health`. Confirms HTTP 200, status `healthy`, API title `PRAVAHA API`, version `1.0.0`, verified station count 38, validation samples 24,088, and all 8 dataset boolean indicators `true`.
- `test_root_endpoint`: Evaluates `GET /`. Verifies platform title, version, documentation endpoints (`/docs`, `/redoc`), and sitemap list.

### Cluster 2: Station Registry & Search
- `test_list_stations_all`: Evaluates `GET /api/stations`. Confirms 38 total candidate stations returned, each with 8-digit string `station_id` retaining leading zeros.
- `test_search_station_by_id_and_name`: Evaluates query parameter `?search=01646500` (exact station match) and `?search=potomac` (fuzzy river match). Confirms filtered counts match expected basins.
- `test_filter_by_river_system`: Evaluates query parameter `?river_system=Potomac%20River`. Confirms isolated return of station `01646500`.
- `test_station_pagination`: Evaluates `?limit=5&offset=0`. Verifies exactly 5 records returned with `total_count = 38`.
- `test_get_station_detail_success`: Evaluates `GET /api/stations/01646500`. Verifies coordinates, drainage area ($11,564.57\text{ sq mi}$), state code `24` (`MD`), and statistical percentiles ($q_{50} = 7,240.0\text{ cfs}$, $q_{90} = 25,500.0\text{ cfs}$, $\max = 192,000.0\text{ cfs}$).
- `test_get_station_detail_leading_zero_normalization`: Evaluates `GET /api/stations/1646500` (7-digit input). Verifies normalization to `01646500` with HTTP 200.
- `test_get_station_detail_not_found`: Evaluates `GET /api/stations/99999999`. Confirms standard HTTP 404 with descriptive detail message.

### Cluster 3: Historical Hydrograph Time-Series
- `test_hydrograph_date_range`: Evaluates `GET /api/stations/01646500/hydrograph?start_date=2022-01-01&end_date=2022-01-05`. Confirms exactly 5 chronological points returned, with observed discharge, holdout prediction, model name, and provenance fields populated.
- `test_hydrograph_pre_validation_period_null_prediction`: Evaluates `start_date=2015-06-01&end_date=2015-06-03`. Confirms historical actual discharge is returned, while `predicted_discharge_cfs`, `prediction_model`, and `validation_type` are strictly `null`.
- `test_hydrograph_model_selection`: Evaluates parameter `?model_name=spec_q` and `?model_name=log1p`. Confirms proper routing to canonical models (`LightGBM Specific Discharge`, `XGBoost Log1p`).
- `test_hydrograph_invalid_date_range`: Evaluates `?start_date=2023-01-01&end_date=2022-01-01` ($T_{\text{start}} > T_{\text{end}}$). Confirms rejection with HTTP 400.
- `test_hydrograph_malformed_date`: Evaluates `?start_date=invalid-date`. Confirms rejection with HTTP 400.
- `test_hydrograph_unknown_station`: Evaluates `GET /api/stations/99999999/hydrograph`. Confirms rejection with HTTP 404.
- `test_hydrograph_unknown_model`: Evaluates `?model_name=non_existent_model`. Confirms rejection with HTTP 400 listing supported models.

### Cluster 4: Validation Leaderboard
- `test_validation_leaderboard`: Evaluates `GET /api/validation/leaderboard`. Confirms 5 models ranked strictly by Pooled $R^2$. Rank 1 is `LightGBM Log-Specific Discharge` ($R^2 = 0.4910$, RMSE $= 82,871.13\text{ cfs}$, Top-10% Peak RMSE $= 156,593.84\text{ cfs}$, sample count $= 24,088$).
- `test_validation_leaderboard_matches_source_csv`: Directly verifies API metrics against `reports/lors_validation_results.csv` row values.

### Cluster 5: River-System Spatial Analytics
- `test_river_systems_analytics`: Evaluates `GET /api/validation/river-systems`. Confirms all 23 independent river system clusters are represented. Verifies `California Central Valley System` holds 2 assigned stations (`11447650` and `11303500`) with 730 evaluated samples.

### Cluster 6: Catchment Profiles & Model Limitations
- `test_catchment_profile_verified_station`: Evaluates station `01646500`. Confirms all 4 attributes verified (`drainage_area_sqmi = 11564.57`, `mean_elevation_ft = 1269.03`, `slope_pct = 11.70`, `forest_cover_pct = 58.58`).
- `test_catchment_profile_unverified_attributes`: Evaluates station `07010000`. Confirms drainage area is verified ($697,000.0\text{ sq mi}$), while elevation, slope, and forest cover are `MISSING_OR_UNVERIFIED` with `failure_reason = "StreamStats lacks..."`.
- `test_catchment_profile_regulated_limitation`: Evaluates station `08158000` (Colorado River at Austin, TX). Confirms explicit limitation text detailing upstream reservoir regulation (Mansfield Dam).
- `test_catchment_profile_truncated_record_limitation`: Evaluates station `11447650` (Sacramento River at Freeport, CA). Confirms explicit limitation text noting observation end date of `2015-09-30` and zero modern validation samples.

### Cluster 7: Ground Truth Data Authenticity
- `test_hydrograph_matches_raw_csv_record`: Compares API response for `01646500` on `2010-01-01` ($22,100.0\text{ cfs}$) against line 2 of `data/processed/PRAVAHA_TRAIN_LABELLED.csv`. Confirms bit-for-bit mathematical identity.
- `test_missing_artifact_diagnostic_reporting`: Mocks a missing artifact path using `unittest.mock.patch`. Verifies that `/health` immediately reports `status = "degraded"` and marks the specific missing artifact as `false`.

---

## 3. Data Integrity & Floating-Point Sanitization

A recursive JSON validator (`assert_no_nan_or_inf`) was executed across all test payloads. Results:
- **`NaN` floats detected**: **0**
- **`Infinity` floats detected**: **0**
- **Missing numerical fields**: Serialized cleanly as `null` in accordance with RFC 8259 JSON standards.
- **Station ID leading zeros**: 100% preserved as strings across all responses.

