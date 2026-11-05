"""
Resumable Meteorological Acquisition Queue for PRAVAHA
Enforces:
1. Single-source consistency (No mixing of incompatible products).
2. Resumable progress tracking via JSON state cache.
3. Strict rate-limiting / request throttling (2s pause).
4. Short-circuit on HTTP 429 (never hanging in multi-hour blocking loops).
5. Immutable raw JSON caching.
"""
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RAW_WEATHER_DIR = Path("data/raw/weather")
RAW_WEATHER_DIR.mkdir(parents=True, exist_ok=True)
QUEUE_STATE_FILE = RAW_WEATHER_DIR / "queue_state.json"
USER_AGENT = "PRAVAHA-Floodcast/1.0 (flood-prediction-research@pravaha.org)"

class WeatherCollectionQueue:
    def __init__(self, preferred_source: str = "OPEN_METEO", fallback_source: str = "NASA_POWER"):
        self.preferred_source = preferred_source.upper()
        self.fallback_source = fallback_source.upper()
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if QUEUE_STATE_FILE.exists():
            try:
                with open(QUEUE_STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"completed_stations": {}, "failed_stations": {}, "active_source": self.preferred_source}

    def _save_state(self):
        with open(QUEUE_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def fetch_station(
        self,
        station_id: str,
        lat: float,
        lon: float,
        start_date: str = "2010-01-01",
        end_date: str = "2023-12-31"
    ) -> Dict[str, Any]:
        """
        Attempts retrieval using preferred source. If quota error (429) occurs,
        records failure and immediately halts queue to prevent multi-hour hangs.
        """
        sid = str(station_id).zfill(8)
        if sid in self.state.get("completed_stations", {}):
            logger.info(f"Station {sid} already completed in queue state.")
            return {"status": "CACHED", "station_id": sid, "file": self.state["completed_stations"][sid]}

        if self.preferred_source == "OPEN_METEO":
            raw_file = RAW_WEATHER_DIR / f"{sid}_weather_openmeteo_{start_date}_{end_date}.json"
            if raw_file.exists():
                self.state["completed_stations"][sid] = raw_file.as_posix()
                self._save_state()
                return {"status": "EXISTING_RAW", "station_id": sid, "file": raw_file.as_posix()}

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
            try:
                logger.info(f"Querying Open-Meteo for {sid} ({lat:.4f}, {lon:.4f})...")
                resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=25)
                if resp.status_code == 200:
                    with open(raw_file, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    self.state["completed_stations"][sid] = raw_file.as_posix()
                    self._save_state()
                    time.sleep(2.0) # Throttling pause
                    return {"status": "SUCCESS", "station_id": sid, "file": raw_file.as_posix()}
                elif resp.status_code == 429:
                    err_msg = f"HTTP 429 Rate Limit Exceeded: {resp.text.strip()[:120]}"
                    logger.warning(err_msg)
                    self.state["failed_stations"][sid] = {"error": err_msg, "timestamp": time.time()}
                    self._save_state()
                    return {"status": "QUOTA_EXHAUSTED", "station_id": sid, "error": err_msg}
                else:
                    err_msg = f"HTTP {resp.status_code}: {resp.text[:100]}"
                    self.state["failed_stations"][sid] = {"error": err_msg}
                    self._save_state()
                    return {"status": "HTTP_ERROR", "station_id": sid, "error": err_msg}
            except Exception as e:
                err_msg = str(e)
                self.state["failed_stations"][sid] = {"error": err_msg}
                self._save_state()
                return {"status": "NETWORK_ERROR", "station_id": sid, "error": err_msg}

        elif self.preferred_source == "NASA_POWER":
            s_clean = start_date.replace("-", "")
            e_clean = end_date.replace("-", "")
            raw_file = RAW_WEATHER_DIR / f"{sid}_weather_nasapower_{s_clean}_{e_clean}.json"
            if raw_file.exists():
                self.state["completed_stations"][sid] = raw_file.as_posix()
                self._save_state()
                return {"status": "EXISTING_RAW", "station_id": sid, "file": raw_file.as_posix()}

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
            try:
                logger.info(f"Querying NASA POWER for {sid} ({lat:.4f}, {lon:.4f})...")
                resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=45)
                if resp.status_code == 200:
                    with open(raw_file, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    self.state["completed_stations"][sid] = raw_file.as_posix()
                    self._save_state()
                    time.sleep(1.5)
                    return {"status": "SUCCESS", "station_id": sid, "file": raw_file.as_posix()}
                else:
                    err_msg = f"NASA POWER HTTP {resp.status_code}: {resp.text[:100]}"
                    self.state["failed_stations"][sid] = {"error": err_msg}
                    self._save_state()
                    return {"status": "HTTP_ERROR", "station_id": sid, "error": err_msg}
            except Exception as e:
                self.state["failed_stations"][sid] = {"error": str(e)}
                self._save_state()
                return {"status": "NETWORK_ERROR", "station_id": sid, "error": str(e)}

        return {"status": "UNKNOWN_SOURCE", "station_id": sid}

