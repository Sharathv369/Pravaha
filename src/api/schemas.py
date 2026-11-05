"""Pydantic schemas for the PRAVAHA API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Common / Error Schemas
# ---------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    """Standardized API error response format."""
    detail: str = Field(..., description="Human-readable error explanation.")
    error_code: Optional[str] = Field(None, description="Optional machine-readable error classification.")


# ---------------------------------------------------------------------------
# Phase 2: Health Schemas
# ---------------------------------------------------------------------------
class DatasetAvailability(BaseModel):
    train_labelled: bool = Field(..., description="Availability of data/processed/PRAVAHA_TRAIN_LABELLED.csv")
    station_catalog: bool = Field(..., description="Availability of reports/verified_station_catalog.csv")
    river_system_grouping: bool = Field(..., description="Availability of reports/river_system_grouping.csv")
    catchment_provenance: bool = Field(..., description="Availability of reports/catchment_provenance.csv")
    lorso_predictions: bool = Field(..., description="Availability of data/processed/prompt_e_validation_predictions.parquet")
    lorso_results: bool = Field(..., description="Availability of reports/lors_validation_results.csv")
    lorso_station_metrics: bool = Field(..., description="Availability of reports/lors_per_station_metrics.csv")
    lorso_river_metrics: bool = Field(..., description="Availability of reports/lors_per_river_system_metrics.csv")


class HealthResponse(BaseModel):
    status: str = Field("healthy", description="Overall health status: 'healthy', 'degraded', or 'unhealthy'.")
    api_title: str = Field("PRAVAHA API", description="Application title.")
    api_version: str = Field("1.0.0", description="Semantic API version.")
    datasets: DatasetAvailability = Field(..., description="Per-artifact availability breakdown.")
    verified_station_count: int = Field(..., description="Number of verified USGS streamgauging stations.")
    validation_sample_count: int = Field(..., description="Number of held-out LORSO validation samples evaluated.")
    backend_ready: bool = Field(..., description="Whether all essential datasets are loaded and ready.")


# ---------------------------------------------------------------------------
# Phase 3: Station Schemas
# ---------------------------------------------------------------------------
class StationItem(BaseModel):
    station_id: str = Field(..., description="Official 8-digit USGS station identification string.")
    station_name: str = Field(..., description="Official USGS streamgauging station title.")
    river_name: str = Field(..., description="Primary river or waterway name.")
    state_cd: Optional[int] = Field(None, description="US State FIPS integer code.")
    state: Optional[str] = Field(None, description="2-letter US state abbreviation.")
    latitude: float = Field(..., description="WGS84 latitude decimal degrees.")
    longitude: float = Field(..., description="WGS84 longitude decimal degrees.")
    drainage_area_sqmi: Optional[float] = Field(None, description="Upstream drainage basin area in square miles.")
    drainage_area_verification_status: str = Field(..., description="Verification status of the drainage area.")
    river_system: Optional[str] = Field(None, description="Independent river system basin grouping.")
    observation_start: Optional[str] = Field(None, description="Earliest recorded observation date (YYYY-MM-DD).")
    observation_end: Optional[str] = Field(None, description="Latest recorded observation date (YYYY-MM-DD).")
    total_observations: int = Field(0, description="Total count of daily mean discharge records.")
    data_quality_status: str = Field(..., description="Overall USGS and GAGES-II verification tier.")
    is_core_station: bool = Field(..., description="Flag indicating if station belongs to the core benchmark set.")
    has_2022_2023_validation: bool = Field(..., description="Whether station was evaluated in 2022-2023 LORSO holdout.")


class StationListResponse(BaseModel):
    total_count: int = Field(..., description="Total stations available in catalogue.")
    filtered_count: int = Field(..., description="Number of stations matching applied search/filter.")
    stations: List[StationItem] = Field(..., description="List of verified USGS stations.")


class FlowThresholds(BaseModel):
    min_recorded_cfs: Optional[float] = Field(None, description="Historical minimum daily mean discharge in cfs.")
    q25_cfs: Optional[float] = Field(None, description="25th percentile flow in cfs.")
    q50_median_cfs: Optional[float] = Field(None, description="50th percentile median flow in cfs.")
    q75_cfs: Optional[float] = Field(None, description="75th percentile flow in cfs.")
    q90_threshold_cfs: Optional[float] = Field(None, description="Historical 90th percentile flood threshold in cfs.")
    max_recorded_cfs: Optional[float] = Field(None, description="Historical maximum daily mean discharge in cfs.")


class StationDetailResponse(BaseModel):
    station_id: str = Field(..., description="Official 8-digit USGS station identification string.")
    station_name: str = Field(..., description="Official USGS streamgauging station title.")
    river_name: str = Field(..., description="Primary river or waterway name.")
    river_system: Optional[str] = Field(None, description="Independent river system basin grouping.")
    basin_identifier: Optional[str] = Field(None, description="Hydrologic basin HUC identifier.")
    state_cd: Optional[int] = Field(None, description="US State FIPS code.")
    state: Optional[str] = Field(None, description="2-letter US state abbreviation.")
    coordinates: Dict[str, float] = Field(..., description="WGS84 lat/lon coordinates.")
    drainage_area_sqmi: Optional[float] = Field(None, description="Drainage area in square miles.")
    drainage_area_verification_status: str = Field(..., description="Drainage area provenance tier.")
    observation_start: Optional[str] = Field(None, description="Earliest observation date.")
    observation_end: Optional[str] = Field(None, description="Latest observation date.")
    total_observations: int = Field(..., description="Total daily mean discharge observations.")
    flow_thresholds_cfs: FlowThresholds = Field(..., description="Historical streamflow statistical percentiles.")
    data_quality_status: str = Field(..., description="USGS NWIS verification status.")
    verification_reason: str = Field(..., description="Detailed provenance audit explanation.")
    has_validation_predictions: bool = Field(..., description="Whether out-of-system LORSO predictions exist.")


# ---------------------------------------------------------------------------
# Phase 4: Historical Hydrograph Schemas
# ---------------------------------------------------------------------------
class HydrographPoint(BaseModel):
    date: str = Field(..., description="ISO 8601 calendar date (YYYY-MM-DD).")
    station_id: str = Field(..., description="USGS Station ID string.")
    actual_discharge_cfs: Optional[float] = Field(None, description="USGS 00060_00003 daily mean discharge in cfs.")
    predicted_discharge_cfs: Optional[float] = Field(None, description="Held-out LORSO validation prediction in cfs.")
    prediction_model: Optional[str] = Field(None, description="Model identifier used for the holdout prediction.")
    validation_type: Optional[str] = Field(None, description="Validation methodology ('LORSO_HOLDOUT' or null).")
    data_source: str = Field("USGS_NWIS_DAILY_MEAN_00060_00003", description="Provenance of observed discharge.")
    data_status: str = Field(..., description="'OBSERVED_AND_VALIDATED' or 'OBSERVED_HISTORICAL'.")


class HydrographResponse(BaseModel):
    station_id: str = Field(..., description="USGS Station ID string.")
    station_name: str = Field(..., description="Station title.")
    model_name: Optional[str] = Field(None, description="Selected LORSO validation model.")
    target_formulation: Optional[str] = Field(None, description="Model target transformation code.")
    total_points: int = Field(..., description="Number of daily time series points returned.")
    start_date: str = Field(..., description="Earliest date in result set.")
    end_date: str = Field(..., description="Latest date in result set.")
    disclaimer: str = Field(
        "Historical USGS daily mean discharge (00060_00003). Model predictions represent historical 2022–2023 "
        "out-of-system Leave-One-River-System-Out (LORSO) validation holdouts, NOT live or future operational forecasts.",
        description="Scientific data provenance disclaimer."
    )
    data: List[HydrographPoint] = Field(..., description="Ordered chronological daily hydrograph records.")


# ---------------------------------------------------------------------------
# Phase 5: Validation Leaderboard Schemas
# ---------------------------------------------------------------------------
class LeaderboardItem(BaseModel):
    model_name: str = Field(..., description="Full model identifier.")
    target_formulation: str = Field(..., description="Mathematical target formulation ('raw', 'spec_q', 'log_spec_q', 'log1p').")
    overall_rmse_cfs: float = Field(..., description="Overall pooled Root Mean Squared Error in cfs.")
    peak_rmse_cfs: float = Field(..., description="Top-10% peak discharge pooled RMSE in cfs.")
    overall_mae_cfs: float = Field(..., description="Overall pooled Mean Absolute Error in cfs.")
    pooled_r2: float = Field(..., description="Pooled R-squared fit across all holdout observations.")
    validation_sample_count: int = Field(..., description="Total out-of-system validation sample count.")
    peak_sample_count: int = Field(..., description="Top-10% extreme event validation sample count.")
    rank_by_pooled_r2: int = Field(..., description="Model rank ordered by pooled R-squared (1 = highest).")


class LeaderboardResponse(BaseModel):
    validation_strategy: str = Field("Leave-One-River-System-Out (LORSO)", description="Cross-validation strategy.")
    total_models: int = Field(..., description="Number of evaluated model formulations.")
    total_validation_rows: int = Field(..., description="Concatenated validation observation count.")
    models: List[LeaderboardItem] = Field(..., description="Model benchmark performance rankings.")
    scientific_note: str = Field(
        "Pooled R² is calculated globally across all held-out observations simultaneously. It is not macro-averaged. "
        "RMSE and MAE represent historical out-of-system holdout prediction errors.",
        description="Methodological note on metric computation."
    )


# ---------------------------------------------------------------------------
# Phase 6: River-System Analytics Schemas
# ---------------------------------------------------------------------------
class RiverSystemItem(BaseModel):
    river_system: str = Field(..., description="Independent river system name.")
    held_out_station_ids: List[str] = Field(..., description="USGS station IDs assigned to this river system.")
    station_count: int = Field(..., description="Total streamgauging stations in this basin.")
    validation_sample_count: int = Field(..., description="Number of 2022-2023 holdout observations evaluated.")
    peak_sample_count: int = Field(..., description="Number of top-10% peak observations in this fold.")
    model_name: str = Field(..., description="Evaluated model formulation.")
    rmse_cfs: Optional[float] = Field(None, description="System-level holdout RMSE in cfs.")
    peak_rmse_cfs: Optional[float] = Field(None, description="Top-10% peak holdout RMSE in cfs.")
    mae_cfs: Optional[float] = Field(None, description="System-level holdout MAE in cfs.")
    r2: Optional[float] = Field(None, description="System-level holdout R-squared.")
    validation_status: str = Field(..., description="'EVALUATED_HOLDOUT' or 'ZERO_VALIDATION_SAMPLES'.")


class RiverSystemsResponse(BaseModel):
    total_river_systems: int = Field(..., description="Total independent river system groups (23).")
    model_name: str = Field(..., description="Reported model formulation.")
    river_systems: List[RiverSystemItem] = Field(..., description="Per-system holdout evaluation metrics.")


# ---------------------------------------------------------------------------
# Phase 7: Catchment Profile Schemas
# ---------------------------------------------------------------------------
class CatchmentAttribute(BaseModel):
    value: Optional[float] = Field(None, description="Measured numerical attribute value.")
    unit: str = Field(..., description="Unit of measurement.")
    source_dataset: Optional[str] = Field(None, description="Authoritative dataset source (e.g. USGS NWIS, GAGES-II).")
    verification_status: str = Field(..., description="'VERIFIED' or 'MISSING_OR_UNVERIFIED'.")
    explanation: Optional[str] = Field(None, description="Reason for missing value or provenance details.")


class CatchmentProfileResponse(BaseModel):
    station_id: str = Field(..., description="Official USGS Station ID string.")
    station_name: str = Field(..., description="Station title.")
    river_name: str = Field(..., description="Waterway name.")
    drainage_area_sqmi: CatchmentAttribute = Field(..., description="Upstream drainage basin area.")
    mean_elevation_ft: CatchmentAttribute = Field(..., description="Mean basin elevation.")
    slope_pct: CatchmentAttribute = Field(..., description="Mean basin topographic slope percentage.")
    forest_cover_pct: CatchmentAttribute = Field(..., description="Basin forest canopy cover percentage.")
    overall_catchment_verification: str = Field(..., description="'VERIFIED_BENCHMARK_READY' or 'VERIFIED_REQUIRES_STREAMSTATS'.")
    model_limitation_indicator: str = Field(..., description="Honest, evidence-based ML model limitation for this station.")

