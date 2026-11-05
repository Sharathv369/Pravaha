"""
USGS NWIS Daily Mean Discharge Downloader for PRAVAHA
Collects daily mean discharge (statCd 00003, parameterCd 00060)
for all verified candidate stations from 2010-01-01 to 2023-12-31.
Preserves raw files, logs SHA-256 hashes, and builds coverage reports.
Zero synthetic substitution.
"""
import os
import json
import time
import hashlib
from pathlib import Path
import pandas as pd
import requests

from src.data.manifest import record_manifest

RAW_USGS_DIR = Path("data/raw/usgs")
REPORTS_DIR = Path("reports")
RAW_USGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = "2010-01-01"
END_DATE = "2023-12-31"
EXPECTED_DAYS = 5113

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def fetch_discharge_station(site_id: str, max_retries: int = 3) -> dict:
    raw_path = RAW_USGS_DIR / f"{site_id}_discharge_{START_DATE}_{END_DATE}.json"
    
    # 1. Check cache
    if raw_path.exists():
        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ts = data["value"]["timeSeries"]
            if ts and len(ts) > 0:
                values = ts[0]["values"][0]["value"]
                print(f"[{site_id}] Loaded from cache: {len(values)} records.")
                return {
                    "site_id": site_id,
                    "status": "CACHED",
                    "file_path": str(raw_path),
                    "file_sha256": sha256_file(raw_path),
                    "record_count": len(values),
                    "error": None
                }
        except Exception as e:
            print(f"[{site_id}] Cache read error: {e}, re-downloading...")
            
    # 2. Live NWIS download
    url = "https://waterservices.usgs.gov/nwis/dv/"
    params = {
        "format": "json",
        "sites": site_id,
        "startDT": START_DATE,
        "endDT": END_DATE,
        "statCd": "00003",
        "parameterCd": "00060",
        "siteStatus": "all"
    }
    headers = {"User-Agent": "PRAVAHA-Floodcast/1.0", "Accept-Encoding": "gzip, deflate"}
    
    last_err = None
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            resp = requests.get(url, params=params, headers=headers, timeout=25)
            elapsed = time.time() - t0
            if resp.status_code == 200:
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                file_hash = sha256_file(raw_path)
                data = resp.json()
                ts = data.get("value", {}).get("timeSeries", [])
                val_count = 0
                if ts and len(ts) > 0:
                    val_count = len(ts[0].get("values", [{}])[0].get("value", []))
                
                # Log to manifest
                record_manifest(
                    file_path=raw_path,
                    source="USGS NWIS Daily Values Service (dv)",
                    query_params=f"sites={site_id}&startDT={START_DATE}&endDT={END_DATE}&statCd=00003&parameterCd=00060",
                    row_count=val_count,
                    date_range=f"{START_DATE} to {END_DATE}",
                    extra_notes=f"Daily mean streamflow (00060_00003). Download elapsed: {elapsed:.2f}s"
                )
                print(f"[{site_id}] Downloaded {val_count} records in {elapsed:.2f}s.")
                return {
                    "site_id": site_id,
                    "status": "DOWNLOADED",
                    "file_path": str(raw_path),
                    "file_sha256": file_hash,
                    "record_count": val_count,
                    "error": None
                }
            else:
                last_err = f"HTTP {resp.status_code}: {resp.text[:100]}"
                print(f"[{site_id}] Attempt {attempt+1} failed: {last_err}")
                time.sleep(1.5)
        except Exception as e:
            last_err = str(e)
            print(f"[{site_id}] Attempt {attempt+1} exception: {e}")
            time.sleep(1.5)
            
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
    if not catalog_path.exists():
        catalog_path = Path("data/processed/station_catalog.csv")
        
    df_cat = pd.read_csv(catalog_path, dtype={"station_id": str})
    valid_pool = df_cat[~df_cat["verification_status"].str.startswith("REJECTED")].copy()
    print(f"Verified station pool for discharge collection: {len(valid_pool)} stations.")
    
    results = []
    for idx, row in valid_pool.iterrows():
        s_id = str(row["station_id"]).zfill(8)
        res = fetch_discharge_station(s_id)
        res["station_name"] = row["station_name"]
        res["river_name"] = row["river_name"]
        res["verification_status"] = row["verification_status"]
        results.append(res)
        time.sleep(0.5)  # Polite throttle
        
    # Generate coverage report
    cov_rows = []
    for r in results:
        count = r["record_count"]
        pct = (count / EXPECTED_DAYS) * 100.0 if count else 0.0
        cov_rows.append({
            "station_id": r["site_id"],
            "river_name": r["river_name"],
            "verification_status": r["verification_status"],
            "download_status": r["status"],
            "record_count": count,
            "expected_days": EXPECTED_DAYS,
            "completeness_pct": round(pct, 2),
            "file_sha256": r["file_sha256"],
            "error_notes": r["error"] if r["error"] else "None"
        })
        
    df_cov = pd.DataFrame(cov_rows)
    df_cov.to_csv(REPORTS_DIR / "station_coverage_report.csv", index=False)
    
    # Generate Markdown coverage report
    md = [
        "# USGS Daily Mean Discharge Data Coverage Report",
        f"- **Audit Period**: {START_DATE} to {END_DATE} ({EXPECTED_DAYS} total days)",
        f"- **Verified Stations Audited**: {len(valid_pool)}",
        f"- **Successful Ingestion Count**: {len(df_cov[df_cov['download_status'].isin(['DOWNLOADED', 'CACHED'])])}",
        "",
        "| Station ID | River / Location | Valid Days | Expected Days | Completeness (%) | Status | Checksum (SHA-256) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]
    for _, r in df_cov.iterrows():
        sha_short = str(r["file_sha256"])[:12] + "..." if r["file_sha256"] else "None"
        md.append(f"| `{r['station_id']}` | {r['river_name']} | {r['record_count']:,} | {r['expected_days']:,} | {r['completeness_pct']}% | `{r['download_status']}` | `{sha_short}` |")
        
    with open(REPORTS_DIR / "station_coverage_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print(f"Discharge collection completed. Coverage report written to {REPORTS_DIR / 'station_coverage_report.md'}")

if __name__ == "__main__":
    main()

