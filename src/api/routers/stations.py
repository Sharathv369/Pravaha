"""Router for USGS streamgauging stations, historical hydrographs, and catchment profiles."""

from typing import Optional
from fastapi import APIRouter, Path, Query

from src.api.schemas import (
    CatchmentProfileResponse,
    HydrographResponse,
    StationDetailResponse,
    StationListResponse,
)
from src.api.services.catchment_service import catchment_service
from src.api.services.hydrograph_service import hydrograph_service
from src.api.services.station_service import station_service

router = APIRouter(prefix="/api/stations", tags=["USGS Stations & Hydrology"])


@router.get(
    "",
    response_model=StationListResponse,
    summary="Verified USGS Streamgauging Station Catalogue",
    description=(
        "Retrieves the complete catalogue of verified USGS monitoring stations. "
        "Supports fuzzy searching by station ID, station name, or river, as well as filtering by river system."
    ),
)
def list_stations(
    search: Optional[str] = Query(
        None,
        description="Fuzzy search filter matching station ID (e.g. '01646500'), name, or river.",
    ),
    river_system: Optional[str] = Query(
        None,
        description="Filter stations belonging to a specific river system basin (e.g. 'Potomac River').",
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of stations to return.",
    ),
    offset: Optional[int] = Query(
        None,
        ge=0,
        description="Number of stations to skip for pagination.",
    ),
) -> StationListResponse:
    """List verified USGS stations matching search and filter criteria."""
    return station_service.get_stations(
        search=search,
        river_system=river_system,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{station_id}",
    response_model=StationDetailResponse,
    summary="Single USGS Station Metadata & Flow Percentiles",
    description=(
        "Retrieves verified metadata, geographic coordinates, observation date range, "
        "and historical discharge percentiles (q50, q90 threshold) for a single station."
    ),
)
def get_station(
    station_id: str = Path(
        ...,
        description="Official 8-digit USGS station identification string (e.g. '01646500').",
        min_length=7,
        max_length=15,
    )
) -> StationDetailResponse:
    """Fetch metadata and statistical percentiles for a verified station."""
    return station_service.get_station_detail(station_id)


@router.get(
    "/{station_id}/hydrograph",
    response_model=HydrographResponse,
    summary="Historical Discharge Hydrograph & LORSO Validation Predictions",
    description=(
        "Returns the continuous daily mean discharge time-series alongside held-out LORSO validation predictions. "
        "Predictions represent historical 2022–2023 spatial cross-validation holdouts (not live forecasts)."
    ),
)
def get_station_hydrograph(
    station_id: str = Path(
        ...,
        description="Official 8-digit USGS station identification string (e.g. '01646500').",
    ),
    start_date: Optional[str] = Query(
        None,
        description="Earliest date to include in format YYYY-MM-DD (e.g. '2022-01-01').",
    ),
    end_date: Optional[str] = Query(
        None,
        description="Latest date to include in format YYYY-MM-DD (e.g. '2023-12-31').",
    ),
    model_name: Optional[str] = Query(
        None,
        description="Validation model formulation (default: 'log_spec_q'; options: 'log_spec_q', 'spec_q', 'raw', 'peak_weighted', 'log1p').",
    ),
) -> HydrographResponse:
    """Query historical daily mean discharge and matching out-of-system validation predictions."""
    return hydrograph_service.get_hydrograph(
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        model_name=model_name,
    )


@router.get(
    "/{station_id}/catchment-profile",
    response_model=CatchmentProfileResponse,
    summary="Catchment Physiography & ML Model Limitation Profile",
    description=(
        "Returns verified physiographic catchment characteristics (drainage area, elevation, slope, forest canopy) "
        "and an evidence-based model limitation indicator reflecting actual LORSO benchmark findings."
    ),
)
def get_catchment_profile(
    station_id: str = Path(
        ...,
        description="Official 8-digit USGS station identification string (e.g. '01646500').",
    ),
) -> CatchmentProfileResponse:
    """Retrieve verified catchment attributes and evidence-backed limitation commentary."""
    return catchment_service.get_catchment_profile(station_id)

