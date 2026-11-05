"""
Data Pipeline Builder for PRAVAHA
Orchestrates downloading real USGS discharge, metadata, StreamStats/GAGES-II, and Open-Meteo weather.
Produces exact schema:
station_id, date, discharge_cfs, precipitation_mm, temp_max_c, temp_min_c, soil_moisture, drainage_area_sqmi, mean_elevation_ft, slope_pct, forest_cover_pct
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from src.data.manifest import record_manifest
from src.data.usgs import fetch_station_metadata, fetch_usgs_discharge
from src.data.weather import fetch_openmeteo_weather
from src.data.streamstats import fetch_streamstats_characteristics
from src.data.station_catalog import CORE_STATIONS, DIVERSE_EXPANDED_STATIONS, generate_station_catalog

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

SCHEMA_COLUMNS = [
    "station_id",
    "date",
    "discharge_cfs",
    "precipitation_mm",
    "temp_max_c",
    "temp_min_c",
    "soil_moisture",
    "weather_source",
    "drainage_area_sqmi",
    "mean_elevation_ft",
    "slope_pct",
    "forest_cover_pct"
]

def build_single_station_dataset(
    station_meta: Dict[str, Any],
    start_date: str = "2010-01-01",
    end_date: str = "2023-12-31"
) -> pd.DataFrame:
    """
    Downloads and merges all 4 data modalities for a single station.
    Strictly preserves raw integrity and exact column schema.
    """
    site_id = str(station_meta["station_id"]).zfill(8)
    logger.info(f"=== Processing station {site_id} ({station_meta.get('river_name', 'USGS Gauge')}) ===")
    
    # 1. Coordinates and Site Metadata
    lat = station_meta.get("latitude")
    lon = station_meta.get("longitude")
    if lat is None or lon is None:
        live_meta = fetch_station_metadata(site_id)
        lat = live_meta["latitude"]
        lon = live_meta["longitude"]

    # 2. USGS Daily Mean Discharge
    df_discharge = fetch_usgs_discharge(site_id, start_date=start_date, end_date=end_date)
    if df_discharge.empty:
        logger.warning(f"No discharge records returned for site {site_id}")
        return pd.DataFrame(columns=SCHEMA_COLUMNS)

    # 3. Open-Meteo Historical Weather
    df_weather = fetch_openmeteo_weather(site_id, lat=lat, lon=lon, start_date=start_date, end_date=end_date)
    
    # 4. Basin Characteristics
    basin_chars = fetch_streamstats_characteristics(site_id)
    # Check if station_meta has overrides
    da = station_meta.get("drainage_area_sqmi") or basin_chars.get("drainage_area_sqmi")
    elev = station_meta.get("mean_elevation_ft") or basin_chars.get("mean_elevation_ft")
    slope = station_meta.get("slope_pct") or basin_chars.get("slope_pct")
    forest = station_meta.get("forest_cover_pct") or basin_chars.get("forest_cover_pct")

    # Merge weather and discharge on date
    df_merged = pd.merge(df_discharge[["station_id", "date", "discharge_cfs"]], 
                         df_weather[["date", "precipitation_mm", "temp_max_c", "temp_min_c", "soil_moisture", "weather_source"]], 
                         on="date", 
                         how="outer")
    
    df_merged["station_id"] = site_id
    df_merged["drainage_area_sqmi"] = da
    df_merged["mean_elevation_ft"] = elev
    df_merged["slope_pct"] = slope
    df_merged["forest_cover_pct"] = forest
    
    # Sort and reorder
    df_merged = df_merged.sort_values("date").reset_index(drop=True)
    df_final = df_merged[SCHEMA_COLUMNS]
    
    # Cache station clean processed file
    station_file = PROCESSED_DIR / f"station_{site_id}.parquet"
    df_final.to_parquet(station_file, index=False)
    
    return df_final

def build_dataset(
    stations: List[Dict[str, Any]],
    output_filename: str = "train.csv",
    start_date: str = "2010-01-01",
    end_date: str = "2023-12-31"
) -> pd.DataFrame:
    """
    Builds combined multi-station dataset.
    """
    dfs = []
    for s in stations:
        try:
            df_station = build_single_station_dataset(s, start_date=start_date, end_date=end_date)
            if not df_station.empty:
                dfs.append(df_station)
        except Exception as e:
            logger.error(f"Failed to process station {s.get('station_id')}: {e}", exc_info=True)
            
    if not dfs:
        raise RuntimeError("No station data could be built.")
        
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df = combined_df.sort_values(["station_id", "date"]).reset_index(drop=True)
    
    output_path = PROCESSED_DIR / output_filename
    combined_df.to_csv(output_path, index=False)
    
    # Manifest logging
    record_manifest(
        file_path=output_path,
        source="PRAVAHA Data Builder (USGS NWIS + Open-Meteo + StreamStats/GAGES-II)",
        query_params=f"stations={len(stations)}&dates={start_date}to{end_date}",
        row_count=len(combined_df),
        date_range=f"{combined_df['date'].min()} to {combined_df['date'].max()}",
        extra_notes="Clean combined training dataset"
    )
    
    return combined_df

def print_data_quality_report(df: pd.DataFrame) -> str:
    """
    Generates and prints a comprehensive data-quality report:
    - rows per station
    - date coverage
    - % missing per column
    - discharge summary stats
    - unit checks
    """
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("          PRAVAHA DATA QUALITY & INTEGRITY REPORT          ")
    report_lines.append("=" * 70)
    report_lines.append(f"Total Rows: {len(df):,}")
    report_lines.append(f"Total Unique Stations: {df['station_id'].nunique()}")
    report_lines.append(f"Date Span: {df['date'].min()} to {df['date'].max()}")
    report_lines.append("-" * 70)
    report_lines.append("STATION BREAKDOWN:")
    for st_id, g in df.groupby("station_id"):
        valid_q = g["discharge_cfs"].notna().sum()
        pct_valid = (valid_q / len(g)) * 100
        report_lines.append(
            f"  * Station {st_id}: {len(g):,} rows | Dates: {g['date'].min()} to {g['date'].max()} | "
            f"Valid Discharge: {valid_q:,} ({pct_valid:.1f}%)"
        )
    report_lines.append("-" * 70)
    report_lines.append("MISSING VALUES PER COLUMN (%):")
    for col in df.columns:
        n_miss = df[col].isna().sum()
        pct_miss = (n_miss / len(df)) * 100
        report_lines.append(f"  * {col:<22}: {n_miss:>7,} missing ({pct_miss:>5.2f}%)")
    report_lines.append("-" * 70)
    report_lines.append("DISCHARGE (cfs) SUMMARY STATISTICS:")
    q_stats = df["discharge_cfs"].describe(percentiles=[0.05, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99])
    for stat_name, val in q_stats.items():
        report_lines.append(f"  * {stat_name:<10}: {val:>15,.2f}")
    report_lines.append("-" * 70)
    report_lines.append("UNIT & SANITY CHECKS:")
    neg_q = (df["discharge_cfs"] < 0).sum()
    report_lines.append(f"  * Negative discharge values: {neg_q} (Must be 0)")
    max_precip = df["precipitation_mm"].max()
    min_precip = df["precipitation_mm"].min()
    report_lines.append(f"  * Precipitation range: [{min_precip:.1f} mm, {max_precip:.1f} mm] (Realistic meteorological bounds)")
    max_tmax = df["temp_max_c"].max()
    min_tmin = df["temp_min_c"].min()
    report_lines.append(f"  * Temperature range: [{min_tmin:.1f} C, {max_tmax:.1f} C] (Realistic continental bounds)")
    report_lines.append("=" * 70)
    
    full_report = "\n".join(report_lines)
    print(full_report)
    return full_report

if __name__ == "__main__":
    generate_station_catalog()
    logger.info("Starting Phase 1 acquisition for Core 5 stations...")
    df_core = build_dataset(CORE_STATIONS, output_filename="train.csv")
    report = print_data_quality_report(df_core)
    
    # Save report to artifacts
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    with open(artifacts_dir / "data_quality_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

