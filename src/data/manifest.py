"""
PRAVAHA Data Manifest & Provenance Tracker
Logs metadata, provenance, and SHA-256 checksums to data/MANIFEST.md.
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any

MANIFEST_PATH = Path("data/MANIFEST.md")

def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def record_manifest(
    file_path: Path,
    source: str,
    query_params: str,
    row_count: int,
    date_range: str,
    extra_notes: Optional[str] = None
) -> None:
    """
    Appends an entry to data/MANIFEST.md with full provenance metadata.
    """
    if not MANIFEST_PATH.exists():
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            f.write("# PRAVAHA Data Manifest & Provenance Log\n\n")
            f.write("| File | Source | Query / Parameters | Download Timestamp (UTC) | Rows | Date Range | SHA-256 Hash |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")

    sha256 = compute_sha256(file_path) if file_path.exists() else "N/A"
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    rel_path = file_path.as_posix()
    
    # Escape pipe characters in params
    clean_params = query_params.replace("|", "/")
    
    entry = f"| `{rel_path}` | {source} | {clean_params} | {ts} | {row_count} | {date_range} | `{sha256}` |\n"
    
    with open(MANIFEST_PATH, "a", encoding="utf-8") as f:
        f.write(entry)

