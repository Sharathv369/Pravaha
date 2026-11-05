# PRAVAHA — UI Screen & Component Architecture Mapping
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt UI-0 Component Architecture Document  
**Date**: November 2026  
**Auditor & UI Architect**: Lead Frontend & Systems Engineer  

---

## 1. Global Component Inventory & Design Tokens

To preserve the visual fidelity of the Google Stitch designs, the React application will be constructed using a shared atomic component hierarchy adhering strictly to the `Oceanic Hydrological Intelligence` design system.

### 1.1 Atomic & Structural Components

| Component Name | File Path | Props | Purpose & Visual Style |
| :--- | :--- | :--- | :--- |
| **`GlassCard`** | `components/common/GlassCard.jsx` | `children, className, elevation=1, padding='md'` | Foundational surface. `rgba(255, 255, 255, 0.76)`, `backdrop-blur-md`, border `#D8E8F0`, rounded-2xl, ambient marine shadow. |
| **`OceanButton`** | `components/common/OceanButton.jsx` | `variant='primary'|'secondary'|'danger'|'ghost', size='sm'|'md'|'lg', icon, onClick` | Primary ocean blue (`#287BB5`) or secondary glass styling. Active `scale-95` micro-interaction. |
| **`RiskBadge`** | `components/common/RiskBadge.jsx` | `severity='normal'|'advisory'|'warning'|'critical', pulse=false` | Pill badge (`rounded-full`, text-xs, semibold). Critical shows animated pulsing dot. |
| **`TabularMetric`** | `components/common/TabularMetric.jsx` | `label, value, unit, trend, delta` | Renders numerical values with `font-variant-numeric: tabular-nums` to ensure strict vertical column alignment. |
| **`TopNavbar`** | `components/shared/TopNavbar.jsx` | `activeTab, onSelectTab, systemStatus` | Main header: PRAVAHA wave logo, live telemetry sync pill, route tabs, and Emergency Broadcast CTA. |
| **`TruthBanner`** | `components/shared/TruthBanner.jsx` | `verified=true, disclaimer` | Transparent tag distinguishing **Verified USGS/ML Data** from **Demonstration Mockup Data**. |

---

## 2. Screen 1: Disaster Command Dashboard (`pravaha_main_dashboard`)

**Proposed Route**: `/` or `/dashboard`  
**Purpose**: Primary command overview displaying real-time river network status, active basin telemetry, and flood risk projections.

```
DashboardPage
├── TopNavbar
├── DashboardHeroMetrics
│   ├── StatCard: Active USGS Monitoring Stations (Real: 34 stations)
│   ├── StatCard: Basins at High/Critical Risk (Dynamic threshold calculation)
│   ├── StatCard: Peak Discharge Observation (Historical vs Predicted 24h peak)
│   └── StatCard: AI Model Validation Accuracy (Real: R² = 0.4910, RMSE = 82.8k cfs)
├── MainContentGrid (12-column layout)
│   ├── Left Column (8-column span): Priority River Basin Matrix
│   │   ├── StationFilterTabs (All, Mississippi, Colorado, Atlantic, Pacific)
│   │   └── StationCardList (Scrollable cards for active basins)
│   │       └── StationTelemetryCard (USGS ID, River Name, Drainage Area, Actual CFS, Predicted CFS, MiniHydrograph)
│   └── Right Column (4-column span): Predictive Analytics & Risk Matrix
│       ├── HydrographInspectionPanel (Detailed Recharts dual-line actual vs predicted + p10/p90 uncertainty envelope)
│       ├── TruthEngineSummaryCard (LORSO out-of-system validation metrics)
│       └── MonteCarloRiskMatrix (Probabilistic exceedance risk tiles)
```

### Key Interactive States:
- **Station Selection**: Clicking a `StationTelemetryCard` updates the `HydrographInspectionPanel` with that station's real time-series.
- **Date Range Scrubber**: Allows toggling between historical observation years (2010–2021) and out-of-system validation holdout (2022–2023).

---

## 3. Screen 2: Interactive River Intelligence Map (`pravaha_interactive_google_maps`)

**Proposed Route**: `/map`  
**Purpose**: Full-bleed cartographic interface mapping all 34 USGS stations, river networks, drainage basins, and localized inundation hazard levels.

```
MapPage
├── TopNavbar
├── MapContainerLayout (Full-screen relative viewport)
│   ├── GeospatialMapEngine (Leaflet or MapLibre canvas)
│   │   ├── BaseMapTileLayer (CartoDB Positron or Mapbox Light for clean oceanic aesthetic)
│   │   ├── StationMarkersLayer (34 geo-located pins colored by risk status: Green/Amber/Red)
│   │   └── RiverSystemPolylines (USGS NHD mainstem vectors)
│   ├── FloatingLayerControls (Elevation 2 glass panel)
│   │   ├── LayerToggle: "Sensor Stations"
│   │   ├── LayerToggle: "Precipitation Radar (NASA POWER)"
│   │   ├── LayerToggle: "River Basins (HUC-2/HUC-4 boundaries)"
│   │   └── LayerToggle: "Hazard Inundation Buffer"
│   ├── StationInfoDrawer (Floating glass panel, opens on marker click)
│   │   ├── StationHeader (Station Name, River System, Drainage Area)
│   │   ├── CurrentDischargePill (Live flow in CFS)
│   │   ├── RealTimeMiniHydrograph (Past 30 days actual flow + 7-day predicted trajectory)
│   │   └── CloseDrawerButton
│   └── TimeScrubberSlider (Temporal playback for flood surge progression)
```

### Charting & Map Component Requirements:
- **Map Library**: `leaflet` with `react-leaflet` or `maplibre-gl`.
- **Custom Marker Icons**: SVG pulsing pins matching the Oceanic design system tokens (`#287BB5` for normal, `#D95F62` for critical surge).

---

## 4. Screen 3: Advanced Flood Alert System (`pravaha_advanced_flood_alert_system`)

**Proposed Route**: `/alerts`  
**Purpose**: Multi-channel early warning dispatch console for municipal authorities and vulnerable catchment communities.

```
AlertsPage
├── TopNavbar
├── AlertSystemContainer
│   ├── MobileSentinelBanner (GPS catchment monitoring overview)
│   ├── MultiChannelPipelineMatrix
│   │   ├── DispatchChannelCard: SMS Emergency Gateway (Twilio/AWS SNS simulation)
│   │   ├── DispatchChannelCard: WhatsApp Broadcast Sentinel (Meta API simulation)
│   │   ├── DispatchChannelCard: Regional Siren Relay Network (Municipal sirens simulation)
│   │   └── DispatchChannelCard: Public Mobile Notification App
│   ├── ActiveGaugingStationBroadcastsTable
│   │   └── BroadcastRow (Station ID, River Basin, Exceedance Level, Broadcast Status, Recipients)
│   └── KinLifelineSafetyCircle (Family check-in network & emergency SOS monitor)
```

*Truth Engine Disclosure*: All dispatch toggles, delivery statistics, and siren triggers are explicitly tagged with `TruthBanner` as an **Operational Broadcast Simulation Prototype**.

---

## 5. Screen 4: Community Ground Telemetry (`pravaha_community_reporting_system`)

**Proposed Route**: `/community`  
**Purpose**: Crowdsourced citizen incident reporting, field hazard telemetry, and localized rescue request portal.

```
CommunityReportingPage
├── TopNavbar
├── CitizenNetworkHeader
├── ReportingGrid (Two-column split view)
│   ├── Left Column: Submission Forms
│   │   ├── TabSwitcher: "Hazard Report" vs "Emergency Rescue Request"
│   │   ├── HazardSubmissionForm (Water depth slider, hazard category, photo upload mock, GPS tag)
│   │   └── RescueRequestForm (Urgency level, persons trapped, medical emergency toggle, contact)
│   └── Right Column: Live Community Telemetry Feed
│       ├── FeedFilters (All Incidents, High Water, Blocked Evacuation, Structural Damage)
│       └── IncidentCardList (Crowdsourced incident cards with timestamp, verification chip, photo thumbnail)
```

*Truth Engine Disclosure*: Reports submitted through this form are stored in local browser state and displayed in the demonstration feed. A prominent notice informs users: *"Demonstration Portal — Not connected to live 911 emergency services"*.

---

## 6. Screen 5: NGO Flood Relief Hub (`pravaha_ngo_flood_relief_hub`)

**Proposed Route**: `/relief`  
**Purpose**: Logistics coordination center connecting emergency relief organizations, supplies, and evacuation shelters with affected river basins.

```
NgoReliefPage
├── TopNavbar
├── ReliefOperationsHeader
├── SmartDispatchHeroCard
│   ├── RecommendedDispatchBanner (e.g., Priority Recommendation #SAC-9402)
│   ├── ResourceAllocationBreakdown (Inflatable boats, rations, medical packs)
│   └── DispatchApprovalButton
├── ResourceInventoryMatrix
│   ├── InventoryCard: Rescue Watercraft (Fleet readiness & deployment status)
│   ├── InventoryCard: Emergency Food Rations (Available days of supply)
│   ├── InventoryCard: Portable Medical Kits (Triage readiness)
│   └── InventoryCard: Certified High-Ground Shelters (Occupancy & capacity)
└── VerifiedPartnerDirectory
    └── PartnerCardList (Pacific Disaster Response, Delta Water Rescue, etc.)
```

*Truth Engine Disclosure*: Inventory levels and dispatch recommendations are labeled as **Relief Logistics Simulation**.

---

## 7. Responsive Breakpoint Adaptations

| Screen / Viewport | Mobile (`< 768px`) | Tablet (`768px – 1024px`) | Desktop (`> 1024px`) |
| :--- | :--- | :--- | :--- |
| **Command Dashboard** | Single column; hero stats in 2x2 grid; hydrographs collapse into expander drawers. | 2-column layout; priority basin list (6 cols) and hydrographs (6 cols). | 12-column split (8 cols basin matrix, 4 cols analytics & hydrographs). Container max 1600px. |
| **Interactive Map** | Map fills 60% viewport height; station drawer appears as bottom-sheet modal. | 50/50 horizontal split between map and telemetry sidebar. | Full-bleed map with floating elevation-2 glass overlay panels and drawer. |
| **Alerts & Broadcasts** | Pipeline cards stack vertically; single-column broadcast feed. | 2-column grid for channels; horizontal scrolling for station tables. | 4-column channel matrix; high-density tabular broadcast view. |
| **Community Feed** | Tab switcher toggles between "Submit" and "Live Feed". | Side-by-side 50/50 split. | 5-column submission form, 7-column incident feed. |
| **NGO Relief Hub** | Inventory cards stack into vertical feed; dispatch modal fills screen. | 2x2 inventory grid; partner directory below. | Hero dispatch recommendation on top; 4-column inventory matrix; side partner directory. |

---

## 8. State Management Architecture

```
AppState (Zustand or React Context)
├── stations: Array<Station>             # Fetched from /api/stations
├── activeStationId: string              # Currently selected station for inspection
├── selectedDateRange: [string, string]  # Temporal slider filter
├── modelFormulation: string             # 'log_spec_q' | 'spec_q' | 'raw_weighted'
├── mapLayers: {                         # Map overlay visibility toggles
│     sensors: boolean,
│     radar: boolean,
│     basins: boolean,
│     inundation: boolean
│   }
├── mockCommunityReports: Array<Report>  # LocalStorage-backed crowd reports
└── mockAlertQueue: Array<Alert>         # Local simulation alert queue
```

