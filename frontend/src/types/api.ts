/**
 * TypeScript interfaces matching PRAVAHA FastAPI backend Pydantic schemas.
 */

export interface DatasetAvailability {
  train_labelled: boolean;
  station_catalog: boolean;
  river_system_grouping: boolean;
  catchment_provenance: boolean;
  lorso_predictions: boolean;
  lorso_results: boolean;
  lorso_station_metrics: boolean;
  lorso_river_metrics: boolean;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  api_title: string;
  api_version: string;
  datasets: DatasetAvailability;
  verified_station_count: number;
  validation_sample_count: number;
  backend_ready: boolean;
}

export interface ApiStationItem {
  station_id: string;
  station_name: string;
  river_name: string;
  state_cd: number | null;
  state: string | null;
  latitude: number;
  longitude: number;
  drainage_area_sqmi: number | null;
  drainage_area_verification_status: string;
  river_system: string | null;
  observation_start: string | null;
  observation_end: string | null;
  total_observations: number;
  data_quality_status: string;
  is_core_station: boolean;
  has_2022_2023_validation: boolean;
}

export interface ApiStationListResponse {
  total_count: number;
  filtered_count: number;
  stations: ApiStationItem[];
}

export interface FlowThresholds {
  min_recorded_cfs: number | null;
  q25_cfs: number | null;
  q50_median_cfs: number | null;
  q75_cfs: number | null;
  q90_threshold_cfs: number | null;
  max_recorded_cfs: number | null;
}

export interface ApiStationDetailResponse {
  station_id: string;
  station_name: string;
  river_name: string;
  river_system: string | null;
  basin_identifier: string | null;
  state_cd: number | null;
  state: string | null;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  drainage_area_sqmi: number | null;
  drainage_area_verification_status: string;
  observation_start: string | null;
  observation_end: string | null;
  total_observations: number;
  flow_thresholds_cfs: FlowThresholds;
  data_quality_status: string;
  verification_reason: string;
  has_validation_predictions: boolean;
}

export interface ApiHydrographPoint {
  date: string;
  station_id: string;
  actual_discharge_cfs: number | null;
  predicted_discharge_cfs: number | null;
  prediction_model: string | null;
  validation_type: string | null;
  data_source: string;
  data_status: string;
}

export interface ApiHydrographResponse {
  station_id: string;
  station_name: string;
  model_name: string | null;
  target_formulation: string | null;
  total_points: number;
  start_date: string;
  end_date: string;
  disclaimer: string;
  data: ApiHydrographPoint[];
}

export interface ApiLeaderboardItem {
  model_name: string;
  target_formulation: string;
  overall_rmse_cfs: number;
  peak_rmse_cfs: number;
  overall_mae_cfs: number;
  pooled_r2: number;
  validation_sample_count: number;
  peak_sample_count: number;
  rank_by_pooled_r2: number;
}

export interface ApiLeaderboardResponse {
  validation_strategy: string;
  total_models: number;
  total_validation_rows: number;
  models: ApiLeaderboardItem[];
  scientific_note: string;
}

export interface ApiRiverSystemItem {
  river_system: string;
  held_out_station_ids: string[];
  station_count: number;
  validation_sample_count: number;
  peak_sample_count: number;
  model_name: string;
  rmse_cfs: number | null;
  peak_rmse_cfs: number | null;
  mae_cfs: number | null;
  r2: number | null;
  validation_status: string;
}

export interface ApiRiverSystemsResponse {
  total_river_systems: number;
  model_name: string;
  river_systems: ApiRiverSystemItem[];
}

export interface ApiCatchmentAttribute {
  value: number | null;
  unit: string;
  source_dataset: string | null;
  verification_status: string;
  explanation: string | null;
}

export interface ApiCatchmentProfileResponse {
  station_id: string;
  station_name: string;
  river_name: string;
  drainage_area_sqmi: ApiCatchmentAttribute;
  mean_elevation_ft: ApiCatchmentAttribute;
  slope_pct: ApiCatchmentAttribute;
  forest_cover_pct: ApiCatchmentAttribute;
  overall_catchment_verification: string;
  model_limitation_indicator: string;
}

