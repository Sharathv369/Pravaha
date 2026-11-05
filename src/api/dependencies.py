"""Dependency injection helpers for FastAPI routers."""

from src.api.services.catchment_service import CatchmentService, catchment_service
from src.api.services.hydrograph_service import HydrographService, hydrograph_service
from src.api.services.station_service import StationService, station_service
from src.api.services.validation_service import ValidationService, validation_service


def get_station_service() -> StationService:
    """Provide the global StationService instance."""
    return station_service


def get_hydrograph_service() -> HydrographService:
    """Provide the global HydrographService instance."""
    return hydrograph_service


def get_validation_service() -> ValidationService:
    """Provide the global ValidationService instance."""
    return validation_service


def get_catchment_service() -> CatchmentService:
    """Provide the global CatchmentService instance."""
    return catchment_service

