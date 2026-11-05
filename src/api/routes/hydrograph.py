"""Historical discharge hydrograph and LORSO prediction time-series routes."""

from typing import Optional
from fastapi import APIRouter, Path, Query
from src.api.schemas import HydrographResponse
from src.api.services.hydrograph_service import hydrograph_service

router = APIRouter(prefix="/api/stations", tags=["Hydrographs"])

@router.get("/{station_id}/hydrograph", response_model=HydrographResponse)
def get_station_hydrograph(
    station_id: str = Path(..., description="8-digit USGS station ID"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    model_name: Optional[str] = Query(None, description="ML prediction model alias"),
) -> HydrographResponse:
    return hydrograph_service.get_hydrograph(
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        model_name=model_name,
    )

