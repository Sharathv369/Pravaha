# PRAVAHA — UI-3.1 Geographic Data Accuracy Audit
**Date:** 2026-11-05  
**Auditor:** Antigravity (Senior Frontend / QA Engineer Pass)  
**Build:** `dist/assets/index-9IIf3uqQ.js` (416 KB) — TypeScript zero errors ✅

---

## 1. Station Count Accuracy

> [!IMPORTANT]
> The PRAVAHA dataset contains **38 total USGS station catalogue entries**, not all with equal data coverage.

| Tier | Count | Description | Marker Colour |
|------|-------|-------------|---------------|
| **LORSO Evaluated** | 33 | Full LORSO ML validation with holdout and 2022–2023 evaluation period. `has_validation_data: true` in mockData.ts. | Blue `#287BB5` |
| **Labelled Discharge Only** | 4 | Historical discharge data present, no modern LORSO evaluation. `has_validation_data: false`. | Cyan `#51B9CC` |
| **Historical Record Only** | 1 | Sacramento R A Freeport CA (`11447650`) — observation window ended **2015-09-30**. No LORSO evaluation. | Amber `#D5A83E` |
| **High-Surge Stations** | 2 (overlap) | Mississippi at St. Louis (`07010000`), Colorado at Austin TX (`08158000`) — marked red for active surge exceedance | Red `#DC2626` |
| **Elevated Runoff Watch** | 2 (overlap) | Potomac (`01646500`), Neuse (`02087500`) — elevated runoff amber | Orange `#E58C47` |

**Total: 38 catalogue entries, 34 with expanded labelled discharge, 33 with LORSO evaluation.**

### Corrections Applied
- Station `11447650` marker now renders in **amber** (`#D5A83E`) in both Google Maps and Leaflet fallback engines, distinguishing it from LORSO-evaluated stations.
- Side panel badge now shows:
  - `LORSO Evaluated` (green) for 33 stations
  - `Labelled Discharge` (blue) for 4 historical stations
  - `Historical Record Only` (amber) for station `11447650`
- A **data-tier legend strip** was added below the map canvas displaying all 5 tier categories with coloured dot icons.
- A **Station Historical Record Only warning** is displayed in the side panel when `11447650` is selected, stating: *"Observation window ended 2015-09-30. No recent telemetry. LORSO evaluation not performed."*

---

## 2. Evacuation Shelter Provenance Audit

> [!CAUTION]
> None of the 8 shelters in `SAFE_SPOTS` can be verified against official emergency management records. All are **demonstration scenarios only** and must not be used for real evacuation decisions.

| ID | Name | Coordinates | Basin | Provenance Status |
|----|------|-------------|-------|-------------------|
| SHELTER-01 | Sacramento Bluffs Civic Shelter | 38.62°N, 121.35°W | California Central Valley | **UNVERIFIED** — No authoritative source located. VHF Ch 16 / phone number is fabricated. |
| SHELTER-02 | Potomac Ridge High Ground Center | 39.15°N, 77.30°W | Potomac River Basin | **UNVERIFIED** — No FEMA/state registration found. |
| SHELTER-03 | Red River Safe Haven High School | 47.95°N, 97.05°W | Red River System | **UNVERIFIED** — Generic location near Fargo/Grand Forks area. Not verified against ND HSEM records. |
| SHELTER-04 | Brazos Crest Evacuation Hub | 30.65°N, 96.35°W | Brazos River Basin | **UNVERIFIED** — Approximate location in Brazos corridor. No TDEM verification. |
| SHELTER-05 | Willamette Terrace Safe Complex | 45.48°N, 122.62°W | Willamette River | **UNVERIFIED** — Generic Portland-area coordinates. Not found in OEM shelter registry. |
| SHELTER-06 | Susquehanna Heights Relief Depot | 40.30°N, 76.85°W | Susquehanna River | **UNVERIFIED** — Approximate Harrisburg-area location. PEMA registry not checked. |
| SHELTER-07 | Chattahoochee Uplands Evacuation Base | 33.78°N, 84.45°W | Apalachicola Basin | **UNVERIFIED** — Atlanta metro area. GEMA registry not confirmed. |
| SHELTER-08 | Colorado Plateau Emergency Refuge | 39.08°N, 108.55°W | Colorado River Basin | **UNVERIFIED** — Grand Junction CO area. CDEM registry not confirmed. |

### Corrections Applied
- All shelter markers previously displayed **"CERTIFIED FLOOD-FREE SAFE ZONE"** badge — this has been corrected to **"Demonstration Scenario"** (amber styling).
- Shelter side panel now displays a prominent **provenance disclaimer**: *"Demonstration scenario only. Shelter locations, capacity figures, and contact numbers are illustrative and have not been verified against official emergency management records. Do not use for real evacuation decisions."*
- Language context key `map.safeSpot.certified` updated from "CERTIFIED FLOOD-FREE SAFE ZONE" to "Demonstration Scenario" (both English and Hindi).

---

## 3. Map Interaction Verification

| Feature | Status | Notes |
|---------|--------|-------|
| Station marker click (Google Maps) | ✅ WORKING | `marker.addListener('click', ...)` → sets `selectedStationId`, pans map |
| Station marker click (Leaflet fallback) | ✅ WORKING | `marker.on('click', ...)` → `flyTo` + sets state |
| Historic Station side panel | ✅ WORKING | Loads from `useStation` hook → real API data |
| Real historical hydrograph | ✅ WORKING | `useHydrograph` fetches from FastAPI `/hydrograph/{id}` |
| Nearest-station discovery on map click | ✅ WORKING | Haversine distance calculated correctly |
| Distance display chip | ✅ WORKING | Shows `X.X mi away` with correct Haversine formula |
| Rainfall Scenario disclaimer | ✅ PRESENT | `⚠️ DEMONSTRATION SCENARIO — NOT OPERATIONAL FORECAST` prominently displayed |
| Mobile bottom sheet | ✅ WORKING | Side panel stacks below map on `< lg` breakpoint via `grid-cols-1` |
| Station search jump | ✅ WORKING | Instant search filters, click jumps map to station and updates side panel |
| Fit All 38 Stations button | ✅ WORKING | `fitBounds` / `fitBounds` with padding |
| Zoom In / Out | ✅ WORKING | Custom controls call `setZoom` / `zoomIn` / `zoomOut` |
| Map Style switcher (Terrain/Satellite/Streets) | ✅ WORKING | `handleSetMapStyle` updates Google Maps type or Leaflet tile layer |
| Flood Mode / Relief Logistics toggle | ✅ WORKING | Updates `mapMode` and layer visibility |
| Shelter click + side panel | ✅ WORKING | Displays freeboard, capacity, supplies, emergency contact |
| Citizen SOS click + side panel | ✅ WORKING | Shows urgency, water depth, dispatch button to relief page |

---

## 4. Data Limitations

| Station | Limitation |
|---------|-----------|
| `11447650` Sacramento Freeport | Observation end: 2015-09-30. No LORSO evaluation. Drainage area marked "Unverified" in some API responses. |
| `01438000` Neversink River at Port Jervis | `has_validation_data: false` — labelled discharge only |
| `03611500` Ohio River | `has_validation_data: false` — labelled discharge only |
| `06454500` Big Sioux River | `has_validation_data: false` — labelled discharge only |
| `06752000` South Platte River | `has_validation_data: false` — labelled discharge only |

---

## 5. Known Remaining Issues

| Issue | Severity | Status |
|-------|----------|--------|
| Shelter data not verified against official emergency management registries | HIGH | Properly labelled as "Demonstration Scenario" — no fabricated replacements |
| Citizen SOS signals are demonstration data, not live crowdsourced reports | MEDIUM | Correctly labelled with "DEMO" in layer toggle: `Citizen SOS Signals (14) • Demo` |
| Temporal Surge Progression slider does not drive any real model output | LOW | Labelled as progression display only; no fake forecasts generated |

---

*Report generated by PRAVAHA UI-3.1 geographic accuracy audit. Build: `index-9IIf3uqQ.js` (416 KB). Zero TypeScript errors.*

