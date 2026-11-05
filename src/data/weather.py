"""
Weather Data Acquisition Module for PRAVAHA
Primary: Open-Meteo Historical Weather Archive
Fallback: NASA POWER (Prediction Of Worldwide Energy Resources) Daily Meteorological API
Both provide real, empirical meteorological observations without synthetic generation.
"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import requests

from src.data.manifest import record_manifest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_WEATHER_DIR = Path("data/raw/weather")
RAW_WEATHER_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "PRAVAHA-Floodcast/1.0 (flood-prediction-research@pravaha.org)"

def fetch_nasa_power_weather(
    site_id: str,
    lat: float,
    lon: float,
    start_date: str = "2010-01-01",
    end_date: str = "2023-12-31"
) -> pd.DataFrame:
    """
    Fallback: Fetches real daily meteorological observations from NASA POWER API.
    Parameters:
      PRECTOTCORR: Daily precipitation (mm/day)
      T2M_MAX: Daily maximum 2m air temperature (C)
      T2M_MIN: Daily minimum 2m air temperature (C)
      GWETTOP: Surface soil wetness / moisture (0 to 1 fraction)
    """
    s_clean = start_date.replace("-", "")
    e_clean = end_date.replace("-", "")
    raw_file = RAW_WEATHER_DIR / f"{site_id}_weather_nasapower_{s_clean}_{e_clean}.json"
    
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "PRECTOTCORR,T2M_MAX,T2M_MIN,GWETTOP",
        "community": "AG",
        "longitude": round(lon, 4),
        "latitude": round(lat, 4),
        "start": s_clean,
        "end": e_clean,
        "format": "JSON"
    }
    
    if not raw_file.exists():
        logger.info(f"Querying NASA POWER fallback for station {site_id} ({lat:.4f}, {lon:.4f})...")
        resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
        if resp.status_code == 200:
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(resp.text)
            record_manifest(
                file_path=raw_file,
                source="NASA POWER Daily Meteorological API (MERRA-2)",
                query_params=f"lat={lat}&lon={lon}&start={s_clean}&end={e_clean}&params=PRECTOTCORR,T2M_MAX,T2M_MIN,GWETTOP",
                row_count=0, # updated after parse
                date_range=f"{start_date} to {end_date}",
                extra_notes="Official fallback for Open-Meteo HTTP 429 quota exhaustion"
            )
        else:
            raise RuntimeError(f"NASA POWER API returned HTTP {resp.status_code}: {resp.text[:100]}")

    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    props = data.get("properties", {}).get("parameter", {})
    prcp = props.get("PRECTOTCORR", {})
    tmax = props.get("T2M_MAX", {})
    tmin = props.get("T2M_MIN", {})
    soil = props.get("GWETTOP", {})

    all_dates = sorted(list(prcp.keys()))
    records = []
    for d_str in all_dates:
        # d_str is YYYYMMDD
        formatted_date = f"{d_str[:4]}-{d_str[4:6]}-{d_str[6:8]}"
        records.append({
            "station_id": site_id,
            "date": formatted_date,
            "precipitation_mm": float(prcp[d_str]) if prcp.get(d_str, -999) > -900 else None,
            "temp_max_c": float(tmax[d_str]) if tmax.get(d_str, -999) > -900 else None,
            "temp_min_c": float(tmin[d_str]) if tmin.get(d_str, -999) > -900 else None,
            "soil_moisture": float(soil[d_str]) if soil.get(d_str, -999) > -900 else None,
            "weather_source": "NASA_POWER_MERRA2"
        })

    df = pd.DataFrame(records)
    logger.info(f"Parsed {len(df)} daily weather records from NASA POWER for station {site_id}")
    return df

def fetch_openmeteo_weather(
    site_id: str,
    lat: float,
    lon: float,
    start_date: str = "2010-01-01",
    end_date: str = "2023-12-31",
    max_retries: int = 2,
    backoff_factor: float = 2.0
) -> pd.DataFrame:
    """
    Fetches real weather from Open-Meteo Historical Weather Archive.
    Falls back gracefully to NASA POWER API if Open-Meteo limit is reached.
    """
    raw_file = RAW_WEATHER_DIR / f"{site_id}_weather_openmeteo_{start_date}_{end_date}.json"
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "hourly": "soil_moisture_0_to_7cm",
        "timezone": "auto"
    }
    headers = {"User-Agent": USER_AGENT}

    if not raw_file.exists():
        openmeteo_succeeded = False
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching Open-Meteo weather for {site_id} ({lat:.4f}, {lon:.4f}) attempt {attempt+1}")
                resp = requests.get(url, params=params, headers=headers, timeout=30)
                if resp.status_code == 200:
                    with open(raw_file, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    logger.info(f"Successfully cached raw Open-Meteo weather to {raw_file}")
                    openmeteo_succeeded = True
                    time.sleep(1.0)
                    break
                elif resp.status_code == 429:
                    logger.warning(f"Open-Meteo HTTP 429: {resp.text.strip()}")
                    break # Rate limit exceeded for day; trigger NASA fallback
                else:
                    logger.warning(f"Open-Meteo returned status {resp.status_code}")
                    time.sleep(backoff_factor ** attempt)
            except Exception as e:
                logger.warning(f"Open-Meteo request error: {e}")
                time.sleep(backoff_factor ** attempt)

        if not openmeteo_succeeded:
            logger.info(f"Switching to NASA POWER official real weather fallback for site {site_id}...")
            return fetch_nasa_power_weather(site_id, lat, lon, start_date=start_date, end_date=end_date)

        record_manifest(
            file_path=raw_file,
            source="Open-Meteo Historical Weather Archive",
            query_params=f"lat={lat}&lon={lon}&start={start_date}&end={end_date}&daily=prcp,tmax,tmin&hourly=soil_moisture",
            row_count=0,
            date_range=f"{start_date} to {end_date}"
        )

    # Read and parse Open-Meteo JSON
    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    daily = data.get("daily", {})
    daily_dates = daily.get("time", [])
    prcp = daily.get("precipitation_sum", [])
    tmax = daily.get("temperature_2m_max", [])
    tmin = daily.get("temperature_2m_min", [])

    df_daily = pd.DataFrame({
        "date": daily_dates,
        "precipitation_mm": prcp,
        "temp_max_c": tmax,
        "temp_min_c": tmin
    })

    hourly = data.get("hourly", {})
    hourly_times = hourly.get("time", [])
    hourly_sm = hourly.get("soil_moisture_0_to_7cm", [])

    if hourly_times and hourly_sm:
        df_hourly = pd.DataFrame({
            "datetime": hourly_times,
            "soil_moisture": hourly_sm
        })
        df_hourly["date"] = df_hourly["datetime"].str[:10]
        df_sm_daily = df_hourly.groupby("date")["soil_moisture"].mean().reset_index()
        df_merged = pd.merge(df_daily, df_sm_daily, on="date", how="left")
    else:
        df_merged = df_daily
        df_merged["soil_moisture"] = None

    df_merged["station_id"] = site_id
    df_merged["weather_source"] = "OPEN_METEO"
    cols = ["station_id", "date", "precipitation_mm", "temp_max_c", "temp_min_c", "soil_moisture", "weather_source"]
    df_merged = df_merged[cols].sort_values("date").reset_index(drop=True)
    return df_merged
