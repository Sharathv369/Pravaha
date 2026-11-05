"""Router for Leave-One-River-System-Out (LORSO) validation leaderboard and river-system analytics."""

from typing import Optional
from fastapi import APIRouter, Query

from src.api.schemas import LeaderboardResponse, RiverSystemsResponse
from src.api.services.validation_service import validation_service

router = APIRouter(prefix="/api/validation", tags=["LORSO Validation Benchmarks"])


@router.get(
    "/leaderboard",
    response_model=LeaderboardResponse,
    summary="Official LORSO Validation Leaderboard",
    description=(
        "Retrieves benchmark evaluation metrics across all 5 ML model formulations evaluated under "
        "Leave-One-River-System-Out (LORSO) 23-fold spatial cross-validation. "
        "Models are ranked strictly by global Pooled R²."
    ),
)
def get_validation_leaderboard() -> LeaderboardResponse:
    """Retrieve the official LORSO benchmark rankings and out-of-system error metrics."""
    return validation_service.get_leaderboard()


@router.get(
    "/river-systems",
    response_model=RiverSystemsResponse,
    summary="Per-River-System Holdout Evaluation Analytics",
    description=(
        "Returns system-level spatial holdout performance across all 23 independent river basin clusters. "
        "Distinguishes evaluated river systems from basins with zero holdout samples."
    ),
)
def get_river_system_analytics(
    model_name: Optional[str] = Query(
        None,
        description="Target model formulation (default: 'log_spec_q'; options: 'log_spec_q', 'spec_q', 'raw', 'peak_weighted', 'log1p').",
    )
) -> RiverSystemsResponse:
    """Fetch per-basin cross-validation error metrics for a selected model formulation."""
    return validation_service.get_river_systems(model_name=model_name)

