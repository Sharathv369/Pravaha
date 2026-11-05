# PRAVAHA Expanded Data Quality & Provenance Audit Report

## 1. Executive Summary
- **Total Audited Stations**: 34 verified stations across 18 US Water Resources Regions.
- **Master Dataset Dimensions**: 173,842 rows across 11 core schema columns.
- **Valid Observed Discharge Targets**: 170,817 (98.26%).
- **Missing Target Rows Preserved as NaN**: 3,025 (1.74%).
- **Synthetic / Imputed Target Count**: **ZERO (0)**. Pure empirical USGS NWIS measurements.
- **Uniform Meteorological Source**: NASA POWER MERRA-2 daily reanalysis (`weather_source = NASA_POWER_MERRA2`).
- **Catchment Provenance**: Linked to official USGS GAGES-II (conterm Sept 2011) and USGS StreamStats JSON.

## 2. Target Completeness Audit by Station

| Station ID | River / Location | Total Days | Valid Discharge Days | Missing Target Days | Completeness (%) | Verification Category |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `01570500` | Susquehanna River At Harrisburg, Pa | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `01646500` | Potomac River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `02087500` | Neuse River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `02146000` | Catawba River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `02322500` | Santa Fe River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `03183500` | Greenbrier River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `03335500` | Wabash River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `040851385` | Fox River | 5,113 | 5,109 | 4 | 99.92% | `VERIFIED_BENCHMARK_READY` |
| `05127000` | Kawishiwi River | 5,113 | 5,112 | 1 | 99.98% | `VERIFIED_BENCHMARK_READY` |
| `05331000` | Mississippi River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `05420500` | Mississippi River At Clinton, Ia | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `06334500` | Little Missouri River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `06610000` | Missouri River At Omaha, Ne | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `06805500` | Platte River At Louisville, Nebr. | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `07010000` | Mississippi River At St. Louis, Mo | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `07144100` | L Arkansas R Nr Sedgwick, Ks | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `07289000` | Mississippi River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `07337000` | Red River At Index, Ar | 5,113 | 5,109 | 4 | 99.92% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `08068000` | W Fk San Jacinto Rv Nr Conroe, Tx | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `08158000` | Colorado Rv At Austin, Tx | 5,113 | 5,112 | 1 | 99.98% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `08164000` | Lavaca Rv Nr Edna, Tx | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `08181800` | San Antonio Rv Nr Elmendorf, Tx | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `08378500` | Pecos River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `09058000` | Colorado River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `09163500` | Colorado River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `09380000` | Colorado River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `10109000` | Logan River Above State Dam, | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `11152500` | Salinas R Nr Spreckels Ca | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `11303500` | San Joaquin R Nr Vernalis Ca | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `11447650` | Sacramento R A Freeport Ca | 5,113 | 2,099 | 3,014 | 41.05% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `12119000` | Cedar River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |
| `12472800` | Columbia River Below Priest Rapids Dam, Wa | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_REQUIRES_STREAMSTATS` |
| `13317000` | Salmon River | 5,113 | 5,112 | 1 | 99.98% | `VERIFIED_BENCHMARK_READY` |
| `14211720` | Willamette River | 5,113 | 5,113 | 0 | 100.00% | `VERIFIED_BENCHMARK_READY` |

## 3. Meteorological Feature Integrity

| Column | Feature Meaning | Unit | Min | Median | Max | Missing Count | % Missing |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `precipitation_mm` | MERRA-2 Daily Assimilation | Official | 0.00 | 0.09 | 237.30 | 0 | 0.00% |
| `temp_max_c` | MERRA-2 Daily Assimilation | Official | -29.75 | 20.20 | 48.10 | 0 | 0.00% |
| `temp_min_c` | MERRA-2 Daily Assimilation | Official | -44.44 | 8.17 | 30.95 | 0 | 0.00% |
| `soil_moisture` | MERRA-2 Daily Assimilation | Official | 0.08 | 0.57 | 1.00 | 0 | 0.00% |

## 4. Catchment Feature Integrity & Non-Fabrication Policy

| Catchment Attribute | Meaning | Unit | Available Count | Missing (NaN) Count | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `drainage_area_sqmi` | Contributing / Basin Area | sq mi | 168,729 | 5,113 | 33 of 34 stations verified; Sacramento tidal delta unmeasured |
| `mean_elevation_ft` | Mean Basin Elevation | feet | 107,373 | 66,469 | 21 GAGES-II stations verified; macro-basins set to NaN |
| `slope_pct` | Mean Basin Slope | % | 112,486 | 61,356 | 21 GAGES-II + TX StreamStats verified; others set to NaN |
| `forest_cover_pct` | Basin Forest Canopy | % | 107,373 | 66,469 | 21 GAGES-II stations verified; macro-basins set to NaN |

## 5. Checksum Verification of Processed Artifacts
- `PRAVAHA_EXPANDED_MASTER.csv`: SHA-256 `ce919793f82d4fb753794dec5f995292b5936722343bd1eba3d2c6704603e6ff`
- `PRAVAHA_TRAIN_LABELLED.csv`: SHA-256 `5f4b4bb7a980784ce251f5935190a0e9195ec13f921ae078e72580de3b2f557b`
- `PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv`: SHA-256 `4e9b010e590b251977d604d173ae024f0a7e1518428f7c090cdd79d6d6fdf5b2`
- `PRAVAHA_EXPANDED_PROVENANCE_META.csv`: SHA-256 `3a0b0559a910b0c80ef1bafc61678e50acd7c0f65b41c51a734199347fa33d98`