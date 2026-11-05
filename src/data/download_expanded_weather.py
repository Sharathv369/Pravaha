"""
Expanded NASA POWER Weather Downloader for PRAVAHA
Downloads real daily meteorological data (PRECTOTCORR, T2M_MAX, T2M_MIN, GWETTOP)
for all approved verified stations from 2010-01-01 to 2023-12-31.
Preserves raw files, logs SHA-256 hashes to MANIFEST.md.
Zero synthetic generation.
"""
import os
import sys
import json
import time
import hashlib
from pathlib import Path
import pandas as pd
import requests

from src.data.manifest import record_manifest

RAW_WEATHER_DIR = Path("data/raw/weather")
RAW_WEATHER_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "20100101"
END_DATE = "20231231"
USER_AGENT = "PRAVAHA-Floodcast/1.0 (flood-prediction-research@pravaha.org)"

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def fetch_weather_station(site_id: str, lat: float, lon: float, max_retries: int = 3) -> dict:
    raw_file = RAW_WEATHER_DIR / f"{site_id}_weather_nasapower_{START_DATE}_{END_DATE}.json"
    
    # 1. Check cache
    if raw_file.exists():
        try:
            with open(raw_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            params = data.get("properties", {}).get("parameter", {})
            prcp = params.get("PRECTOTCORR", {})
            if len(prcp) >= 5110:
                print(f"[{site_id}] Loaded from cache: {len(prcp)} records.", flush=True)
                return {
                    "site_id": site_id,
                    "status": "CACHED",
                    "file_path": str(raw_file),
                    "file_sha256": sha256_file(raw_file),
                    "record_count": len(prcp),
                    "error": None
                }
        except Exception as e:
            print(f"[{site_id}] Cache error: {e}, re-downloading...", flush=True)

    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "PRECTOTCORR,T2M_MAX,T2M_MIN,GWETTOP",
        "community": "AG",
        "longitude": round(lon, 4),
        "latitude": round(lat, 4),
        "start": START_DATE,
        "end": END_DATE,
        "format": "JSON"
    }
    headers = {"User-Agent": USER_AGENT}
    
    last_err = None
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            resp = requests.get(url, params=params, headers=headers, timeout=60)
            elapsed = time.time() - t0
            if resp.status_code == 200:
                with open(raw_file, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                f_hash = sha256_file(raw_file)
                data = resp.json()
                prcp_len = len(data.get("properties", {}).get("parameter", {}).get("PRECTOTCORR", {}))
                
                # Record to manifest
                record_manifest(
                    file_path=raw_file,
                    source="NASA POWER Daily Meteorological API (MERRA-2)",
                    query_params=f"lat={round(lat,4)}&lon={round(lon,4)}&start={START_DATE}&end={END_DATE}&params=PRECTOTCORR,T2M_MAX,T2M_MIN,GWETTOP",
                    row_count=prcp_len,
                    date_range="2010-01-01 to 2023-12-31",
                    extra_notes=f"Uniform approved weather dataset across network. Download elapsed: {elapsed:.2f}s"
                )
                print(f"[{site_id}] Downloaded {prcp_len} days in {elapsed:.2f}s.", flush=True)
                return {
                    "site_id": site_id,
                    "status": "DOWNLOADED",
                    "file_path": str(raw_file),
                    "file_sha256": f_hash,
                    "record_count": prcp_len,
                    "error": None
                }
            else:
                last_err = f"HTTP {resp.status_code}: {resp.text[:100]}"
                print(f"[{site_id}] Attempt {attempt+1} failed: {last_err}", flush=True)
                time.sleep(2.0)
        except Exception as e:
            last_err = str(e)
            print(f"[{site_id}] Attempt {attempt+1} exception: {e}", flush=True)
            time.sleep(2.0)
            
    return {
        "site_id": site_id,
        "status": "FAILED",
        "file_path": None,
        "file_sha256": None,
        "record_count": 0,
        "error": last_err
    }

def main():
    catalog_path = Path("reports/verified_station_catalog.csv")
    df_cat = pd.read_csv(catalog_path, dtype={"station_id": str})
    valid_pool = df_cat[~df_cat["verification_status"].str.startswith("REJECTED")].copy()
    print(f"Verified station pool for weather collection: {len(valid_pool)} stations.", flush=True)
    
    results = []
    for idx, row in valid_pool.iterrows():
        s_id = str(row["station_id"]).zfill(8)
        lat = float(row["latitude"])
        lon = float(row["longitude"])
        res = fetch_weather_station(s_id, lat, lon)
        results.append(res)
        time.sleep(1.0) # Polite delay
        
    success_count = sum(1 for r in results if r["status"] in ["DOWNLOADED", "CACHED"])
    print(f"\nWeather collection completed. Successfully acquired {success_count}/{len(valid_pool)} stations.", flush=True)

if __name__ == "__main__":
    main()

