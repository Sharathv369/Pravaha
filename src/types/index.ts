export type RiskLevel = 'NORMAL' | 'ADVISORY' | 'WARNING' | 'CRITICAL';

export interface Station {
  station_id: string;
  station_name: string;
  river_name: string;
  river_system: string;
  basin_identifier: string;
  state_cd: string;
  latitude: number;
  longitude: number;
  drainage_area_sqmi: number;
  mean_elevation_ft: number;
  slope_pct: number;
  forest_cover_pct: number;
  current_flow_cfs: number;
  q90_threshold_cfs: number;
  trend_pct: number;
  risk_level: RiskLevel;
  has_validation_data: boolean;
}

export interface HydrographPoint {
  date: string;
  actual_cfs: number;
  predicted_cfs?: number;
  p10_cfs?: number;
  p90_cfs?: number;
  q90_threshold_cfs: number;
}

export interface AlertChannel {
  id: string;
  name: string;
  icon: string;
  status: 'ACTIVE' | 'STANDBY' | 'PAUSED';
  delivery_rate_pct: number;
  audience_reach: number;
  description: string;
}

export interface StationBroadcast {
  id: string;
  station_id: string;
  station_name: string;
  river_system: string;
  exceedance_level: string;
  broadcast_status: 'DISPATCHED' | 'QUEUED' | 'MONITORING';
  recipients_count: number;
  timestamp: string;
}

export interface KinContact {
  id: string;
  name: string;
  relation: string;
  status: 'SAFE' | 'ALERT' | 'UNREACHABLE';
  location: string;
  last_checkin: string;
}

export interface HazardReport {
  id: string;
  timestamp: string;
  basin: string;
  location_desc: string;
  hazard_type: 'HIGH_WATER' | 'BREACHED_LEVEE' | 'DEBRIS_FLOW' | 'STRUCTURAL';
  water_depth_inches: number;
  status: 'VERIFIED' | 'UNVERIFIED' | 'RESOLVED';
  photo_placeholder?: string;
  upvotes: number;
}

export interface RescueRequest {
  id: string;
  timestamp: string;
  contact_name: string;
  phone: string;
  location_desc: string;
  persons_count: number;
  medical_emergency: boolean;
  urgency: 'HIGH' | 'CRITICAL';
}

export interface NgoResource {
  id: string;
  category: string;
  title: string;
  available_units: number;
  allocated_units: number;
  in_transit_units: number;
  total_units: number;
  unit_name: string;
  icon: string;
}

export interface NgoPartner {
  id: string;
  name: string;
  operating_zone: string;
  active_teams: number;
  readiness: 'READY_DEPLOY' | 'ACTIVE_DEPLOY' | 'STANDBY';
  contact: string;
}

export interface DispatchRecommendation {
  id: string;
  target_basin: string;
  population_at_risk: number;
  urgency: 'HIGH' | 'CRITICAL';
  recommended_boats: number;
  recommended_rations: number;
  recommended_med_kits: number;
  status: 'PENDING_APPROVAL' | 'APPROVED';
}

