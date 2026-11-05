"""USGS station catalogue and metadata endpoint routes."""

from typing import Optional
from fastapi import APIRouter, Path, Query
from src.api.schemas import StationListResponse, StationDetailResponse
from src.api.services.station_service import station_service

router = APIRouter(prefix="/api/stations", tags=["Stations"])

@router.get("", response_model=StationListResponse)
def list_stations(
    search: Optional[str] = Query(None, description="Fuzzy search matching station ID, name, or river."),
    river_system: Optional[str] = Query(None, description="Filter by river system basin."),
    limit: Optional[int] = Query(None, ge=1, le=100),
    offset: Optional[int] = Query(None, ge=0),
) -> StationListResponse:
    return station_service.get_stations(search=search, river_system=river_system, limit=limit, offset=offset)

@router.get("/{station_id}", response_model=StationDetailResponse)
def get_station(
    station_id: str = Path(..., min_length=7, max_length=15)
) -> StationDetailResponse:
    return station_service.get_station_detail(station_id)
