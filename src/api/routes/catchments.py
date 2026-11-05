"""Catchment physiography and model limitation routes."""

from fastapi import APIRouter, Path
from src.api.schemas import CatchmentProfileResponse
from src.api.services.catchment_service import catchment_service

router = APIRouter(prefix="/api/stations", tags=["Catchments"])

@router.get("/{station_id}/catchment-profile", response_model=CatchmentProfileResponse)
def get_catchment_profile(
    station_id: str = Path(..., description="8-digit USGS station ID")
) -> CatchmentProfileResponse:
    return catchment_service.get_catchment_profile(station_id)

