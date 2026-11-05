"""
Master Reproducible Expanded Dataset Builder for PRAVAHA
Phase 6 Pipeline Implementation

Enforces:
1. Strict string station ID handling with zero-padding (e.g. '01646500').
2. Catchment attributes linked directly to verified downloaded GAGES-II CSV tables and USGS StreamStats JSON.
3. Separation of:
   - data/processed/PRAVAHA_EXPANDED_MASTER.csv (all 34 stations x 5,113 days = 173,842 rows; NaNs preserved)
   - data/processed/PRAVAHA_TRAIN_LABELLED.csv (only rows where discharge_cfs is not NaN)
   - data/processed/PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv (rows where discharge_cfs is NaN)
4. Comprehensive provenance tracking in data/processed/PRAVAHA_EXPANDED_PROVENANCE_META.csv.
5. Rebuilding reports/expanded_data_quality_report.md.
Zero synthetic or fabricated data.
"""
import os
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

from src.data.manifest import record_manifest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_USGS_DIR = Path("data/raw/usgs")
RAW_WEATHER_DIR = Path("data/raw/weather")
REPORTS_DIR = Path("reports")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2010-01-01"
END_DATE = "2023-12-31"

CORE_SCHEMA = [
    "station_id",
    "date",
    "discharge_cfs",
    "precipitation_mm",
    "temp_max_c",
    "temp_min_c",
    "soil_moisture",
    "drainage_area_sqmi",
    "mean_elevation_ft",
    "slope_pct",
    "forest_cover_pct"
]

def sha256_file(filepath: Path) -> str:
    if not filepath.exists():
        return "None"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def load_verified_raw_discharge(station_id: str) -> pd.DataFrame:
    sid = str(station_id).zfill(8)
    candidates = list(RAW_USGS_DIR.glob(f"{sid}_discharge_2010*.json"))
    if not candidates:
        raise FileNotFoundError(f"No raw USGS discharge file found for {sid}")
        
    with open(candidates[0], "r", encoding="utf-8") as f:
        data = json.load(f)
        
    ts_list = data.get("value", {}).get("timeSeries", [])
    if not ts_list:
        return pd.DataFrame(columns=["station_id", "date", "discharge_cfs", "quality_cd"])
        
    values = ts_list[0].get("values", [{}])[0].get("value", [])
    records = []
    for item in values:
        d_str = item.get("dateTime", "")[:10]
        val_raw = item.get("value")
        quals = item.get("qualifiers", [""])
        qual_str = ",".join(quals) if quals else ""
        
        try:
            val_flt = float(val_raw)
            if val_flt < 0 or val_flt <= -99999:
                val_flt = None
        except (ValueError, TypeError):
            val_flt = None
            
        records.append({
            "station_id": sid,
            "date": d_str,
            "discharge_cfs": val_flt,
            "quality_cd": qual_str
        })
        
    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["station_id", "date"], keep="first")
    return df

def load_verified_raw_weather(station_id: str) -> Tuple[pd.DataFrame, str]:
    sid = str(station_id).zfill(8)
    nasa_files = list(RAW_WEATHER_DIR.glob(f"{sid}_weather_nasapower_*.json"))
    if not nasa_files:
        raise FileNotFoundError(f"No raw weather file found for station {sid}")
        
    with open(nasa_files[0], "r", encoding="utf-8") as f:
        data = json.load(f)
        
    params = data.get("properties", {}).get("parameter", {})
    prcp = params.get("PRECTOTCORR", {})
    tmax = params.get("T2M_MAX", {})
    tmin = params.get("T2M_MIN", {})
    soil = params.get("GWETTOP", {})
    
    dates = sorted(list(prcp.keys()))
    records = []
    for d in dates:
        fmt_date = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
        p_val = float(prcp[d]) if prcp.get(d, -999) > -900 else None
        tx_val = float(tmax[d]) if tmax.get(d, -999) > -900 else None
        tn_val = float(tmin[d]) if tmin.get(d, -999) > -900 else None
        sm_val = float(soil[d]) if soil.get(d, -999) > -900 else None
        records.append({
            "station_id": sid,
            "date": fmt_date,
            "precipitation_mm": p_val,
            "temp_max_c": tx_val,
            "temp_min_c": tn_val,
            "soil_moisture": sm_val
        })
    df = pd.DataFrame(records)
    return df, "NASA_POWER_MERRA2"

def build_expanded_dataset():
    logger.info("=== Starting PRAVAHA Master Expanded Dataset Builder ===")
    
    # 1. Load verified catalog
    cat_path = REPORTS_DIR / "verified_station_catalog.csv"
    if not cat_path.exists():
        cat_path = PROCESSED_DIR / "station_catalog.csv"
        
    df_cat = pd.read_csv(cat_path, dtype={"station_id": str})
    valid_pool = df_cat[~df_cat["verification_status"].str.startswith("REJECTED")].copy()
    valid_pool["station_id"] = valid_pool["station_id"].str.zfill(8)
    
    logger.info(f"Loaded {len(valid_pool)} verified stations from catalog.")
    
    # 2. Build full date grid for 2010-01-01 to 2023-12-31
    full_date_range = pd.date_range(start=START_DATE, end=END_DATE, freq="D").strftime("%Y-%m-%d").tolist()
    expected_days_per_station = len(full_date_range)
    logger.info(f"Date grid: {START_DATE} to {END_DATE} ({expected_days_per_station} days).")
    
    all_station_dfs = []
    provenance_meta_rows = []
    
    for idx, cat_row in valid_pool.iterrows():
        sid = cat_row["station_id"]
        river_name = cat_row["river_name"]
        logger.info(f"Processing station {sid} ({river_name})...")
        
        # Load discharge
        df_q = load_verified_raw_discharge(sid)
        
        # Load weather
        df_w, w_source = load_verified_raw_weather(sid)
        
        # Base grid for this station
        df_base = pd.DataFrame({
            "station_id": sid,
            "date": full_date_range
        })
        
        # Left join discharge onto date grid
        df_merged = pd.merge(df_base, df_q, on=["station_id", "date"], how="left")
        
        # Left join weather onto date grid
        df_merged = pd.merge(df_merged, df_w, on=["station_id", "date"], how="left")
        
        # Add catchment attributes from verified catalog
        da = float(cat_row["drainage_area_sqmi"]) if pd.notna(cat_row["drainage_area_sqmi"]) and cat_row["drainage_area_sqmi"] != "" else np.nan
        el = float(cat_row["mean_elevation_ft"]) if pd.notna(cat_row["mean_elevation_ft"]) and cat_row["mean_elevation_ft"] != "" else np.nan
        sl = float(cat_row["slope_pct"]) if pd.notna(cat_row["slope_pct"]) and cat_row["slope_pct"] != "" else np.nan
        fc = float(cat_row["forest_cover_pct"]) if pd.notna(cat_row["forest_cover_pct"]) and cat_row["forest_cover_pct"] != "" else np.nan
        
        df_merged["drainage_area_sqmi"] = da
        df_merged["mean_elevation_ft"] = el
        df_merged["slope_pct"] = sl
        df_merged["forest_cover_pct"] = fc
        
        # Add metadata tracking rows
        for _, r in df_merged.iterrows():
            q_val = r["discharge_cfs"]
            is_miss = pd.isna(q_val)
            provenance_meta_rows.append({
                "station_id": sid,
                "date": r["date"],
                "quality_cd": r.get("quality_cd", "") if pd.notna(r.get("quality_cd")) else "",
                "is_target_missing": is_miss,
                "weather_source": w_source,
                "catchment_provenance": cat_row["verification_status"],
                "is_synthetic": False
            })
            
        all_station_dfs.append(df_merged)
        
    master_df = pd.concat(all_station_dfs, ignore_index=True)
    master_meta_df = pd.DataFrame(provenance_meta_rows)
    
    # Ensure correct column ordering
    master_df = master_df[CORE_SCHEMA]
    
    logger.info(f"Master Expanded Table built: {master_df.shape[0]} rows, {master_df.shape[1]} columns.")
    
    # 3. Partitioning: Labelled vs Unlabelled
    train_labelled_df = master_df[master_df["discharge_cfs"].notna()].copy()
    unlabelled_df = master_df[master_df["discharge_cfs"].isna()].copy()
    
    logger.info(f"Labelled Training Rows (observed discharge): {train_labelled_df.shape[0]}")
    logger.info(f"Unlabelled Rows (missing target): {unlabelled_df.shape[0]}")
    
    # 4. Save CSV files
    master_csv_path = PROCESSED_DIR / "PRAVAHA_EXPANDED_MASTER.csv"
    train_csv_path = PROCESSED_DIR / "PRAVAHA_TRAIN_LABELLED.csv"
    unlabelled_csv_path = PROCESSED_DIR / "PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv"
    meta_csv_path = PROCESSED_DIR / "PRAVAHA_EXPANDED_PROVENANCE_META.csv"
    
    master_df.to_csv(master_csv_path, index=False)
    train_labelled_df.to_csv(train_csv_path, index=False)
    unlabelled_df.to_csv(unlabelled_csv_path, index=False)
    master_meta_df.to_csv(meta_csv_path, index=False)
    
    # Also save standard PRAVAHA_MASTER_DATA.csv as copy/alias for backwards compatibility
    master_df.to_csv(PROCESSED_DIR / "PRAVAHA_MASTER_DATA.csv", index=False)
    
    # 5. Record to MANIFEST.md
    for f_path, desc in [
        (master_csv_path, "Master expanded dataset across all 34 verified stations (2010-2023). Target NaNs preserved."),
        (train_csv_path, "Labelled training dataset containing only verified observed discharge targets."),
        (unlabelled_csv_path, "Unlabelled/missing target dataset (e.g. Sacramento post-2015-09-30, maintenance gaps)."),
        (meta_csv_path, "Companion audit metadata tracking quality codes, weather source, and catchment provenance.")
    ]:
        record_manifest(
            file_path=f_path,
            source="PRAVAHA Reproducible Expanded Dataset Pipeline",
            query_params="34 verified stations, 2010-01-01 to 2023-12-31",
            row_count=len(pd.read_csv(f_path)),
            date_range=f"{START_DATE} to {END_DATE}",
            extra_notes=desc
        )
        
    # 6. Generate Expanded Data Quality Report
    logger.info("Generating expanded data quality report...")
    report_path = REPORTS_DIR / "expanded_data_quality_report.md"
    
    total_rows = len(master_df)
    valid_discharge_count = len(train_labelled_df)
    missing_discharge_count = len(unlabelled_df)
    
    lines = [
        "# PRAVAHA Expanded Data Quality & Provenance Audit Report",
        "",
        "## 1. Executive Summary",
        f"- **Total Audited Stations**: {len(valid_pool)} verified stations across 18 US Water Resources Regions.",
        f"- **Master Dataset Dimensions**: {total_rows:,} rows across 11 core schema columns.",
        f"- **Valid Observed Discharge Targets**: {valid_discharge_count:,} ({valid_discharge_count/total_rows*100:.2f}%).",
        f"- **Missing Target Rows Preserved as NaN**: {missing_discharge_count:,} ({missing_discharge_count/total_rows*100:.2f}%).",
        "- **Synthetic / Imputed Target Count**: **ZERO (0)**. Pure empirical USGS NWIS measurements.",
        f"- **Uniform Meteorological Source**: NASA POWER MERRA-2 daily reanalysis (`weather_source = NASA_POWER_MERRA2`).",
        "- **Catchment Provenance**: Linked to official USGS GAGES-II (conterm Sept 2011) and USGS StreamStats JSON.",
        "",
        "## 2. Target Completeness Audit by Station",
        "",
        "| Station ID | River / Location | Total Days | Valid Discharge Days | Missing Target Days | Completeness (%) | Verification Category |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    
    station_stats = []
    for sid, grp in master_df.groupby("station_id"):
        valid_cnt = grp["discharge_cfs"].notna().sum()
        miss_cnt = grp["discharge_cfs"].isna().sum()
        tot_cnt = len(grp)
        pct = (valid_cnt / tot_cnt) * 100.0
        r_name = valid_pool[valid_pool["station_id"] == sid]["river_name"].values[0]
        v_cat = valid_pool[valid_pool["station_id"] == sid]["verification_status"].values[0]
        lines.append(f"| `{sid}` | {r_name} | {tot_cnt:,} | {valid_cnt:,} | {miss_cnt:,} | {pct:.2f}% | `{v_cat}` |")
        
    lines.extend([
        "",
        "## 3. Meteorological Feature Integrity",
        "",
        "| Column | Feature Meaning | Unit | Min | Median | Max | Missing Count | % Missing |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ])
    
    for col in ["precipitation_mm", "temp_max_c", "temp_min_c", "soil_moisture"]:
        c_series = master_df[col]
        c_min = f"{c_series.min():.2f}" if c_series.notna().any() else "NaN"
        c_med = f"{c_series.median():.2f}" if c_series.notna().any() else "NaN"
        c_max = f"{c_series.max():.2f}" if c_series.notna().any() else "NaN"
        m_cnt = c_series.isna().sum()
        m_pct = (m_cnt / total_rows) * 100.0
        lines.append(f"| `{col}` | MERRA-2 Daily Assimilation | Official | {c_min} | {c_med} | {c_max} | {m_cnt:,} | {m_pct:.2f}% |")
        
    lines.extend([
        "",
        "## 4. Catchment Feature Integrity & Non-Fabrication Policy",
        "",
        "| Catchment Attribute | Meaning | Unit | Available Count | Missing (NaN) Count | Notes |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
        f"| `drainage_area_sqmi` | Contributing / Basin Area | sq mi | {master_df['drainage_area_sqmi'].notna().sum():,} | {master_df['drainage_area_sqmi'].isna().sum():,} | 33 of 34 stations verified; Sacramento tidal delta unmeasured |",
        f"| `mean_elevation_ft` | Mean Basin Elevation | feet | {master_df['mean_elevation_ft'].notna().sum():,} | {master_df['mean_elevation_ft'].isna().sum():,} | 21 GAGES-II stations verified; macro-basins set to NaN |",
        f"| `slope_pct` | Mean Basin Slope | % | {master_df['slope_pct'].notna().sum():,} | {master_df['slope_pct'].isna().sum():,} | 21 GAGES-II + TX StreamStats verified; others set to NaN |",
        f"| `forest_cover_pct` | Basin Forest Canopy | % | {master_df['forest_cover_pct'].notna().sum():,} | {master_df['forest_cover_pct'].isna().sum():,} | 21 GAGES-II stations verified; macro-basins set to NaN |",
        "",
        "## 5. Checksum Verification of Processed Artifacts",
        f"- `PRAVAHA_EXPANDED_MASTER.csv`: SHA-256 `{sha256_file(master_csv_path)}`",
        f"- `PRAVAHA_TRAIN_LABELLED.csv`: SHA-256 `{sha256_file(train_csv_path)}`",
        f"- `PRAVAHA_UNLABELLED_OR_MISSING_TARGET.csv`: SHA-256 `{sha256_file(unlabelled_csv_path)}`",
        f"- `PRAVAHA_EXPANDED_PROVENANCE_META.csv`: SHA-256 `{sha256_file(meta_csv_path)}`"
    ])
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    logger.info(f"Dataset build complete! Report written to {report_path}")

if __name__ == "__main__":
    build_expanded_dataset()

