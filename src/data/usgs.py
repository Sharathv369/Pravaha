"""
USGS NWIS Data Acquisition Module for PRAVAHA
Handles daily discharge (parameter 00060, stat 00003) and station metadata.
"""
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import pandas as pd
import requests

from src.data.manifest import record_manifest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_USGS_DIR = Path("data/raw/usgs")
RAW_USGS_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "PRAVAHA-Floodcast/1.0 (flood-prediction-research@pravaha.org)"

def fetch_station_metadata(site_id: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Fetches real USGS station metadata (latitude, longitude, site name, state, huc).
    Uses https://waterservices.usgs.gov/nwis/site/?format=rdb&sites=...
    """
    raw_meta_file = RAW_USGS_DIR / f"{site_id}_site_meta.rdb"
    url = f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={site_id}&siteOutput=expanded&siteStatus=all"
    
    headers = {"User-Agent": USER_AGENT}
    
    if not raw_meta_file.exists():
        response = None
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading USGS metadata for station {site_id} (attempt {attempt+1})")
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    with open(raw_meta_file, "w", encoding="utf-8") as f:
                        f.write(response.text)
                    break
                else:
                    logger.warning(f"USGS metadata request returned status {response.status_code}")
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.warning(f"USGS metadata request failed: {e}")
                time.sleep(2 ** attempt)
        if not raw_meta_file.exists():
            raise RuntimeError(f"Failed to fetch metadata for site {site_id} from {url}")
        
        record_manifest(
            file_path=raw_meta_file,
            source="USGS NWIS Site Service",
            query_params=f"sites={site_id}&format=rdb",
            row_count=len(response.text.splitlines()) if response else 0,
            date_range="N/A",
            extra_notes="Station metadata RDB format"
        )

    # Parse RDB file
    with open(raw_meta_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    data_lines = [l for l in lines if not l.startswith("#")]
    if len(data_lines) < 2:
        raise ValueError(f"Unexpected RDB format for site {site_id}")
        
    headers = data_lines[0].strip().split("\t")
    # data_lines[1] is formatting definition (e.g., 5s 15s)
    values = data_lines[2].strip().split("\t")
    
    row_dict = dict(zip(headers, values))
    lat = float(row_dict.get("dec_lat_va"))
    lon = float(row_dict.get("dec_long_va"))
    station_name = row_dict.get("station_nm", "")
    state_code = row_dict.get("state_cd", "")
    drain_area = row_dict.get("drain_area_va", "")
    
    meta = {
        "station_id": site_id,
        "station_name": station_name,
        "latitude": lat,
        "longitude": lon,
        "state_code": state_code,
        "drain_area_va": float(drain_area) if drain_area and drain_area.strip() else None,
        "huc_cd": row_dict.get("huc_cd", "")
    }
    return meta

def fetch_usgs_discharge(
    site_id: str,
    start_date: str = "2010-01-01",
    end_date: str = "2023-12-31",
    max_retries: int = 3
) -> pd.DataFrame:
    """
    Fetches real USGS NWIS daily mean discharge (00060, stat 00003).
    Treats negative or -999999 as missing (NaN).
    Preserves quality_cd without filling target discharge.
    """
    raw_json_file = RAW_USGS_DIR / f"{site_id}_discharge_{start_date}_{end_date}.json"
    url = (
        f"https://waterservices.usgs.gov/nwis/dv/"
        f"?format=json&sites={site_id}&startDT={start_date}&endDT={end_date}&parameterCd=00060&statCd=00003"
    )
    headers = {"User-Agent": USER_AGENT}
    
    if not raw_json_file.exists():
        success = False
        for attempt in range(max_retries):
            try:
                logger.info(f"Downloading USGS discharge for {site_id} [{start_date} to {end_date}] (attempt {attempt+1})")
                resp = requests.get(url, headers=headers, timeout=60)
                if resp.status_code == 200:
                    with open(raw_json_file, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    success = True
                    break
                else:
                    logger.warning(f"HTTP {resp.status_code} from NWIS API for {site_id}")
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.warning(f"Request error for site {site_id}: {e}")
                time.sleep(2 ** attempt)
                
        if not success:
            logger.info(f"Attempting fallback via dataretrieval package for {site_id}...")
            try:
                import dataretrieval.nwis as nwis
                df_dv, _ = nwis.get_dv(sites=site_id, start=start_date, end=end_date, parameterCd='00060', statCd='00003')
                # Save as raw csv/json fallback
                raw_fallback_file = RAW_USGS_DIR / f"{site_id}_discharge_{start_date}_{end_date}_fallback.csv"
                df_dv.to_csv(raw_fallback_file)
                record_manifest(
                    file_path=raw_fallback_file,
                    source="USGS dataretrieval package (fallback)",
                    query_params=f"sites={site_id}&param=00060&stat=00003",
                    row_count=len(df_dv),
                    date_range=f"{start_date} to {end_date}",
                    extra_notes="Fallback retrieval"
                )
                df_clean = df_dv.reset_index()
                # find value col and cd col
                val_cols = [c for c in df_clean.columns if '00060_00003' in c and not c.endswith('_cd')]
                cd_cols = [c for c in df_clean.columns if c.endswith('_cd')]
                val_col = val_cols[0] if val_cols else df_clean.columns[1]
                cd_col = cd_cols[0] if cd_cols else "quality_cd"
                
                df_res = pd.DataFrame({
                    "station_id": site_id,
                    "date": pd.to_datetime(df_clean["datetime"]).dt.strftime("%Y-%m-%d"),
                    "discharge_cfs": pd.to_numeric(df_clean[val_col], errors="coerce"),
                    "quality_cd": df_clean[cd_col] if cd_col in df_clean.columns else "A"
                })
                # Treat negative or -999999 as missing
                df_res.loc[df_res["discharge_cfs"] < 0, "discharge_cfs"] = None
                df_res.loc[df_res["discharge_cfs"] <= -99999, "discharge_cfs"] = None
                return df_res
            except Exception as fb_err:
                raise RuntimeError(f"Both NWIS API and dataretrieval fallback failed for {site_id}: {fb_err}")
                
        record_manifest(
            file_path=raw_json_file,
            source="USGS NWIS DV JSON API",
            query_params=f"sites={site_id}&startDT={start_date}&endDT={end_date}&parameterCd=00060&statCd=00003",
            row_count=0, # updated after parse
            date_range=f"{start_date} to {end_date}"
        )

    # Parse JSON
    with open(raw_json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    time_series = data.get("value", {}).get("timeSeries", [])
    if not time_series:
        logger.warning(f"No timeSeries records found in USGS JSON for site {site_id}")
        return pd.DataFrame(columns=["station_id", "date", "discharge_cfs", "quality_cd"])
        
    records = []
    # Primary time series for 00060_00003
    for ts in time_series:
        variable_code = ts.get("variable", {}).get("variableCode", [{}])[0].get("value", "")
        values_list = ts.get("values", [{}])[0].get("value", [])
        for entry in values_list:
            d_str = entry.get("dateTime", "")[:10]
            val_raw = entry.get("value", None)
            qualifiers = entry.get("qualifiers", [""])
            qual_str = ",".join(qualifiers) if qualifiers else ""
            
            try:
                val_flt = float(val_raw)
                if val_flt < 0 or val_flt <= -99999:
                    val_flt = None
            except (ValueError, TypeError):
                val_flt = None
                
            records.append({
                "station_id": site_id,
                "date": d_str,
                "discharge_cfs": val_flt,
                "quality_cd": qual_str
            })
            
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.drop_duplicates(subset=["station_id", "date"], keep="first")
        df = df.sort_values("date").reset_index(drop=True)
        logger.info(f"Parsed {len(df)} daily records for USGS station {site_id} ({df['date'].min()} to {df['date'].max()})")
    return df

