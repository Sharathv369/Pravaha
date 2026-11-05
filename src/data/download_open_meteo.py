"""
Open-Meteo Historical Weather Ingestion Module for PRAVAHA
Ingests daily reanalysis weather features for 34 verified USGS streamgauging stations.
Period: 2010-01-01 to 2023-12-31 (5,113 days per station).
"""
import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_OM_DIR = PROJECT_ROOT / "data" / "raw" / "open_meteo"
RAW_OM_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "PRAVAHA-Floodcast/1.0 (flood-prediction-research@pravaha.org)"
BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARS = [
    "precipitation_sum",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "soil_moisture_0_to_7cm_mean",
    "et0_fao_evapotranspiration"
]

def fetch_open_meteo_station(
    station_id: str,
    lat: float,
    lon: float,
    start_date: str = "2010-01-01",
    end_date: str = "2023-12-31",
    max_retries: int = 8
) -> Dict[str, Any]:
    raw_file = RAW_OM_DIR / f"{station_id}_open_meteo_{start_date}_{end_date}.json"
    
    if raw_file.exists():
        logger.info(f"[{station_id}] Loading cached raw Open-Meteo data from {raw_file.name}")
        with open(raw_file, "r", encoding="utf-8") as f:
            return json.load(f)
            
    params = {
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "start_date": start_date,
        "end_date": end_date,
        "daily": ",".join(DAILY_VARS),
        "timezone": "UTC"
    }
    headers = {"User-Agent": USER_AGENT}
    
    for attempt in range(max_retries):
        try:
            logger.info(f"[{station_id}] Requesting Open-Meteo ({lat:.4f}, {lon:.4f}) attempt {attempt+1}/{max_retries}...")
            resp = requests.get(BASE_URL, params=params, headers=headers, timeout=45)
            
            if resp.status_code == 200:
                data = resp.json()
                with open(raw_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                logger.info(f"[{station_id}] Successfully cached raw response ({raw_file.stat().st_size} bytes)")
                return data
            elif resp.status_code == 429:
                wait_sec = 30 + (attempt + 1) * 15
                logger.warning(f"[{station_id}] HTTP 429 Rate Limit encountered. Backing off for {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                logger.warning(f"[{station_id}] HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(5 + 2 ** attempt)
        except Exception as e:
            logger.warning(f"[{station_id}] Network error: {e}. Retrying in {5 + 2 ** attempt}s...")
            time.sleep(5 + 2 ** attempt)
            
    raise RuntimeError(f"Failed to fetch Open-Meteo data for station {station_id} after {max_retries} attempts.")

def ingest_all_34_stations():
    cat_df = pd.read_csv(PROJECT_ROOT / "reports" / "verified_station_catalog.csv")
    cat_df["site_id_str"] = cat_df["station_id"].astype(str)
    cat_df["clean_id"] = cat_df["site_id_str"].apply(lambda s: "0" + s if len(s) == 8 and s.startswith("4085") else s.zfill(8))
    
    # 34 expanded master stations
    master_df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "PRAVAHA_EXPANDED_MASTER.csv", usecols=["station_id"])
    target_ids = sorted(master_df["station_id"].astype(str).str.zfill(8).unique().tolist())
    
    logger.info(f"Total target stations for Open-Meteo ingestion: {len(target_ids)}")
    
    all_frames = []
    metadata_log = []
    
    for idx, sid in enumerate(target_ids, 1):
        st_meta = cat_df[cat_df["clean_id"] == sid].iloc[0]
        lat = float(st_meta["latitude"])
        lon = float(st_meta["longitude"])
        name = st_meta["station_name"]
        
        logger.info(f"Processing ({idx}/{len(target_ids)}): Station {sid} - {name}")
        raw_json = fetch_open_meteo_station(sid, lat, lon)
        
        # Polite pause between requests to prevent 429 rate limit
        time.sleep(2.5)
        
        daily = raw_json.get("daily", {})
        dates = daily.get("time", [])
        
        df_station = pd.DataFrame({
            "station_id": sid,
            "date": dates,
            "om_precipitation_mm": daily.get("precipitation_sum", []),
            "om_temp_max_c": daily.get("temperature_2m_max", []),
            "om_temp_min_c": daily.get("temperature_2m_min", []),
            "om_temp_mean_c": daily.get("temperature_2m_mean", []),
            "om_soil_moisture_m3m3": daily.get("soil_moisture_0_to_7cm_mean", []),
            "om_et0_mm": daily.get("et0_fao_evapotranspiration", [])
        })
        
        all_frames.append(df_station)
        metadata_log.append({
            "station_id": sid,
            "station_name": name,
            "latitude": lat,
            "longitude": lon,
            "elevation_m": raw_json.get("elevation", None),
            "rows_ingested": len(df_station),
            "start_date": dates[0] if dates else None,
            "end_date": dates[-1] if dates else None,
            "missing_precip": df_station["om_precipitation_mm"].isna().sum(),
            "missing_tmax": df_station["om_temp_max_c"].isna().sum(),
            "missing_tmin": df_station["om_temp_min_c"].isna().sum(),
            "missing_tmean": df_station["om_temp_mean_c"].isna().sum(),
            "missing_soil": df_station["om_soil_moisture_m3m3"].isna().sum(),
            "missing_et0": df_station["om_et0_mm"].isna().sum()
        })
        
    final_weather_df = pd.concat(all_frames, ignore_index=True)
    out_csv = PROCESSED_DIR / "PRAVAHA_OPEN_METEO_WEATHER.csv"
    final_weather_df.to_csv(out_csv, index=False)
    logger.info(f"Successfully saved combined Open-Meteo weather dataset to {out_csv} ({final_weather_df.shape[0]} rows, {final_weather_df.shape[1]} cols)")
    
    meta_df = pd.DataFrame(metadata_log)
    meta_df.to_csv(PROJECT_ROOT / "reports" / "g1_open_meteo_ingestion_log.csv", index=False)
    logger.info(f"Saved ingestion audit log to reports/g1_open_meteo_ingestion_log.csv")

if __name__ == "__main__":
    ingest_all_34_stations()

