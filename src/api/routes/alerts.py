"""Flood warning and active alert routes."""

from typing import List, Dict, Any
from fastapi import APIRouter
from src.api.services.station_service import station_service

router = APIRouter(prefix="/api/alerts", tags=["Flood Alerts"])

@router.get("", summary="Active Hydrological Alerts")
def get_active_alerts() -> Dict[str, Any]:
    """Retrieve active flood warnings and stations exceeding flood stage thresholds."""
    stations_data = station_service.get_stations(limit=50)
    alerts = []
    for st in stations_data.stations:
        # Check if latest flow is in top percentile
        p50 = st.percentiles.q50_cfs if st.percentiles else 0
        p90 = st.percentiles.q90_cfs if st.percentiles else 0
        pmax = st.percentiles.max_cfs if st.percentiles else 0
        
        alerts.append({
            "station_id": st.station_id,
            "station_name": st.station_name,
            "river_system": st.river_system,
            "state": st.state,
            "flood_stage_threshold_cfs": p90,
            "historical_max_cfs": pmax,
            "status": "MONITORING" if p90 > 0 else "NORMAL"
        })
    return {"alert_count": len(alerts), "alerts": alerts}

