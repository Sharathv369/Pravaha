"""Health and readiness diagnostic router."""

from fastapi import APIRouter, Response, status

from src.api import config
from src.api.schemas import DatasetAvailability, HealthResponse
from src.api.services.station_service import station_service
from src.api.services.hydrograph_service import hydrograph_service
from src.api.services.validation_service import validation_service
from src.api.services.catchment_service import catchment_service

router = APIRouter(tags=["Health & Diagnostics"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health & Artifact Diagnostic Probe",
    description="Inspects backend system readiness and verifies availability of all essential hydrologic datasets.",
)
@router.get(
    "/api/health",
    response_model=HealthResponse,
    include_in_schema=False,
)
def get_health(response: Response) -> HealthResponse:
    """Diagnostic check verifying file availability, station catalogue count, and service readiness."""
    datasets = DatasetAvailability(
        train_labelled=config.TRAIN_LABELLED_CSV.exists(),
        station_catalog=config.VERIFIED_STATION_CATALOG_CSV.exists(),
        river_system_grouping=config.RIVER_SYSTEM_GROUPING_CSV.exists(),
        catchment_provenance=config.CATCHMENT_PROVENANCE_CSV.exists(),
        lorso_predictions=config.LORSO_PREDICTIONS_PARQUET.exists(),
        lorso_results=config.LORSO_VALIDATION_RESULTS_CSV.exists(),
        lorso_station_metrics=config.LORSO_PER_STATION_METRICS_CSV.exists(),
        lorso_river_metrics=config.LORSO_PER_RIVER_SYSTEM_METRICS_CSV.exists(),
    )

    essential_ready = (
        station_service.is_ready()
        and hydrograph_service.is_ready()
        and validation_service.is_ready()
        and catchment_service.is_ready()
    )

    all_files_exist = all(datasets.model_dump().values())

    if essential_ready and all_files_exist:
        health_status = "healthy"
        backend_ready = True
        response.status_code = status.HTTP_200_OK
    elif essential_ready:
        health_status = "degraded"
        backend_ready = True
        response.status_code = status.HTTP_200_OK
    else:
        health_status = "unhealthy"
        backend_ready = False
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    station_count = station_service.get_station_count()
    validation_sample_count = 24088 if datasets.lorso_predictions else 0

    return HealthResponse(
        status=health_status,
        api_title=config.API_TITLE,
        api_version=config.API_VERSION,
        datasets=datasets,
        verified_station_count=station_count,
        validation_sample_count=validation_sample_count,
        backend_ready=backend_ready,
    )

