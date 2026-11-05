"""Model validation leaderboard and river system metrics routes."""

from typing import Optional
from fastapi import APIRouter, Query
from src.api.schemas import ValidationLeaderboardResponse, RiverSystemComparisonResponse
from src.api.services.validation_service import validation_service

router = APIRouter(prefix="/api/validation", tags=["Validation"])

@router.get("/leaderboard", response_model=ValidationLeaderboardResponse)
def get_leaderboard() -> ValidationLeaderboardResponse:
    return validation_service.get_leaderboard()

@router.get("/river-systems", response_model=RiverSystemComparisonResponse)
def get_river_system_metrics(
    model_name: Optional[str] = Query(None, description="Filter metrics by model alias")
) -> RiverSystemComparisonResponse:
    return validation_service.get_river_systems(model_name=model_name)

