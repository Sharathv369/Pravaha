# PRAVAHA Master Data Quality Report
- **Generated Date**: 2026-11-04 20:34:28
- **Total Rows**: 25,565
- **Unique Stations**: 5
- **Date Range**: 2010-01-01 to 2023-12-31

## Column-Level Completeness and Types
| Column | Non-Null Count | Missing Count | % Missing | Data Type | Min | Median | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `station_id` | 25,565 | 0 | 0.00% | `object` | N/A | N/A | N/A |
| `date` | 25,565 | 0 | 0.00% | `object` | N/A | N/A | N/A |
| `discharge_cfs` | 22,550 | 3,015 | 11.79% | `float64` | 43.50 | 3870.00 | 931000.00 |
| `precipitation_mm` | 25,565 | 0 | 0.00% | `float64` | 0.00 | 0.04 | 202.21 |
| `temp_max_c` | 25,565 | 0 | 0.00% | `float64` | -16.81 | 23.59 | 48.10 |
| `temp_min_c` | 25,565 | 0 | 0.00% | `float64` | -23.00 | 10.98 | 28.60 |
| `soil_moisture` | 25,565 | 0 | 0.00% | `float64` | 0.09 | 0.63 | 0.98 |
| `drainage_area_sqmi` | 25,565 | 0 | 0.00% | `float64` | 1153.00 | 23500.00 | 697000.00 |
| `mean_elevation_ft` | 25,565 | 0 | 0.00% | `float64` | 423.75 | 1180.00 | 3280.00 |
| `slope_pct` | 25,565 | 0 | 0.00% | `float64` | 3.20 | 4.15 | 14.20 |
| `forest_cover_pct` | 25,565 | 0 | 0.00% | `float64` | 14.50 | 46.80 | 58.20 |

## Target Discharge Summary
- Total Target Observations: 25,565
- Valid Ground-Truth Discharge Rows: 22,550
- Legitimate Target NaNs: 3,015 (Sacramento discontinued post-2015 + Colorado Austin 2017-01-26)
- Synthetically Imputed / Filled Rows: **0 (Strictly Zero)**

## Sanity Checks
- Negative Discharge Values: **0** (Pass)
- Precipitation Range: [0.00 mm, 202.21 mm] (Pass)
- Temperature Range: [-23.00 °C, 48.10 °C] (Pass)
- Duplicate `(station_id, date)` rows: **0** (Pass)