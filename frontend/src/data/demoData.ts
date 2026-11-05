/**
 * PRAVAHA — Demonstration & Evaluation Simulation Data
 * 
 * DEMO ONLY — NO LIVE EXTERNAL BACKEND
 * These records support interactive scenario testing, civil defense exercises,
 * citizen reporting workflows, and relief logistics demonstrations for the FLOODCAST hackathon.
 * 
 * Note: Streamflow records, station metadata, hydrographs, and model validations
 * are retrieved dynamically from the FastAPI backend at http://127.0.0.1:8000.
 */

import {
  AlertChannel,
  KinContact,
  HazardReport,
  NgoResource,
  NgoPartner,
  DispatchRecommendation,
} from '../types';

export const DEMO_ALERT_CHANNELS: AlertChannel[] = [
  {
    id: 'sms',
    name: 'Cellular Emergency Broadcast',
    icon: 'cell_tower',
    status: 'ACTIVE',
    delivery_rate_pct: 99.4,
    audience_reach: 124800,
    description: 'Direct-to-tower CAP geofence SMS alert with zero data requirement.'
  },
  {
    id: 'whatsapp',
    name: 'WhatsApp Community Sentinel',
    icon: 'chat',
    status: 'ACTIVE',
    delivery_rate_pct: 98.1,
    audience_reach: 84300,
    description: 'Automated 2-way verified broadcast bot with multilingual translation.'
  },
  {
    id: 'siren',
    name: 'Municipal Riverfront Siren Grid',
    icon: 'campaign',
    status: 'STANDBY',
    delivery_rate_pct: 100.0,
    audience_reach: 340000,
    description: 'Acoustic siren array positioned along vulnerable riverfront dikes.'
  },
  {
    id: 'inapp',
    name: 'PRAVAHA Citizen Mobile Alert',
    icon: 'notifications_active',
    status: 'ACTIVE',
    delivery_rate_pct: 99.8,
    audience_reach: 65120,
    description: 'Real-time push notifications with GPS-targeted evacuation routes.'
  }
];

export const DEMO_KIN_CONTACTS: KinContact[] = [
  {
    id: 'kin-1',
    name: 'Emma (Spouse)',
    relation: 'Immediate Family',
    status: 'SAFE',
    location: 'High-Ground Shelter (Riverview)',
    last_checkin: '8 mins ago'
  },
  {
    id: 'kin-2',
    name: 'Liam (Son)',
    relation: 'Immediate Family',
    status: 'SAFE',
    location: 'Central High Ground Assembly',
    last_checkin: '15 mins ago'
  },
  {
    id: 'kin-3',
    name: 'Robert (Father)',
    relation: 'Extended Family',
    status: 'ALERT',
    location: 'Zone B Lowland Residence',
    last_checkin: '45 mins ago'
  }
];

export const DEMO_HAZARD_REPORTS: HazardReport[] = [
  {
    id: 'REP-1042',
    timestamp: '12m ago',
    basin: 'Mississippi River at St. Louis',
    location_desc: '4th Street Underpass submerged near riverwall',
    hazard_type: 'HIGH_WATER',
    water_depth_inches: 34,
    status: 'VERIFIED',
    upvotes: 42
  },
  {
    id: 'REP-1039',
    timestamp: '28m ago',
    basin: 'San Joaquin River at Vernalis',
    location_desc: 'Riparian buffer overflow on Agricultural Route 132',
    hazard_type: 'BREACHED_LEVEE',
    water_depth_inches: 48,
    status: 'VERIFIED',
    upvotes: 68
  },
  {
    id: 'REP-1035',
    timestamp: '45m ago',
    basin: 'Colorado River at Austin',
    location_desc: 'Shoal Creek bridge obstruction due to tree debris',
    hazard_type: 'DEBRIS_FLOW',
    water_depth_inches: 18,
    status: 'UNVERIFIED',
    upvotes: 19
  },
  {
    id: 'REP-1028',
    timestamp: '1h 10m ago',
    basin: 'Potomac River near Washington',
    location_desc: 'C&O Canal towpath washed out near Little Falls',
    hazard_type: 'DEBRIS_FLOW',
    water_depth_inches: 12,
    status: 'RESOLVED',
    upvotes: 84
  }
];

export const DEMO_NGO_RESOURCES: NgoResource[] = [
  {
    id: 'res-boats',
    category: 'Water Rescue',
    title: 'Inflatable Rescue Watercraft',
    available_units: 14,
    allocated_units: 8,
    in_transit_units: 4,
    total_units: 26,
    unit_name: 'Boats',
    icon: 'sailing'
  },
  {
    id: 'res-rations',
    category: 'Sustenance',
    title: 'Emergency Food Rations (72h)',
    available_units: 4200,
    allocated_units: 2800,
    in_transit_units: 1500,
    total_units: 8500,
    unit_name: 'Ration Packs',
    icon: 'lunch_dining'
  },
  {
    id: 'res-medical',
    category: 'Healthcare',
    title: 'Trauma & Triage Medical Packs',
    available_units: 850,
    allocated_units: 420,
    in_transit_units: 200,
    total_units: 1470,
    unit_name: 'Kits',
    icon: 'medical_services'
  },
  {
    id: 'res-shelters',
    category: 'Shelter',
    title: 'Certified High-Ground Shelters',
    available_units: 3,
    allocated_units: 5,
    in_transit_units: 0,
    total_units: 8,
    unit_name: 'Facilities',
    icon: 'holiday_village'
  }
];

export const DEMO_NGO_PARTNERS: NgoPartner[] = [
  {
    id: 'ngo-1',
    name: 'Pacific Disaster Response Core',
    operating_zone: 'California Central Valley & Delta',
    active_teams: 18,
    readiness: 'ACTIVE_DEPLOY',
    contact: '+1 (555) 019-2831'
  },
  {
    id: 'ngo-2',
    name: 'Midwest Water Rescue & Evacuation',
    operating_zone: 'Mississippi & Missouri Mainstem',
    active_teams: 24,
    readiness: 'ACTIVE_DEPLOY',
    contact: '+1 (555) 018-9942'
  },
  {
    id: 'ngo-3',
    name: 'Lone Star Flood Relief Brigade',
    operating_zone: 'Texas Gulf Coastal Basins',
    active_teams: 12,
    readiness: 'READY_DEPLOY',
    contact: '+1 (555) 014-7721'
  },
  {
    id: 'ngo-4',
    name: 'Appalachian Search & Rapid Rescue',
    operating_zone: 'Potomac, Susquehanna & Ohio Basins',
    active_teams: 8,
    readiness: 'STANDBY',
    contact: '+1 (555) 012-3349'
  }
];

export const DEMO_DISPATCH_RECOMMENDATION: DispatchRecommendation = {
  id: 'DISP-SAC-9402',
  target_basin: 'Mississippi River at St. Louis (Stage 3 Cresting)',
  population_at_risk: 14200,
  urgency: 'CRITICAL',
  recommended_boats: 6,
  recommended_rations: 1200,
  recommended_med_kits: 250,
  status: 'PENDING_APPROVAL'
};

export const DEMO_SOS_SIGNALS = [
  { id: 'sos-1', lat: 38.62, lon: -121.52, urgency: 'HIGH', message: 'Elderly trapped near lower levee road' },
  { id: 'sos-2', lat: 38.54, lon: -121.48, urgency: 'MEDIUM', message: 'Vehicle stalled in 24 inch standing water' },
  { id: 'sos-3', lat: 38.68, lon: -121.36, urgency: 'LOW', message: 'Sump pump failure in basement' },
];
