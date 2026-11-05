# PRAVAHA — React + FastAPI Integration Status Report
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt UI-2 Full-Stack Frontend-Backend Integration Audit  
**Backend**: FastAPI 0.162.0 on `http://127.0.0.1:8000`  
**Frontend**: React 18, Vite, TypeScript, Tailwind CSS on `http://localhost:5173`  
**Generated At**: 2026-11-05  

---

## 1. Executive Summary

In Prompt UI-2, the existing React frontend (`frontend/`) was fully connected to the FastAPI backend (`src/api/`). Hardcoded demonstration catalogs were replaced with live API responses powered by verified USGS station records, continuous historical daily mean discharge (`00060_00003`), GAGES-II catchment physiography, and 23-fold Leave-One-River-System-Out (LORSO) spatial validation holdout predictions.

The original Google Stitch **Oceanic Hydrological Intelligence** visual aesthetic, color palette, card hierarchy, and typography were 100% preserved. Where backend endpoints do not exist (citizen reports, relief shelter logistics, cellular emergency dispatch simulation), demonstration data was neatly isolated into `frontend/src/data/demoData.ts` and accompanied by clear, non-intrusive truth disclaimers.

---

## 2. Page-by-Page Integration Matrix

| Page / Route | Component | Connected Backend Endpoint(s) | Verified Data Elements Replaced | Retained Demonstration Features |
| :--- | :--- | :--- | :--- | :--- |
| **Main Command Dashboard** (`/dashboard`) | `DashboardPage.tsx` | `GET /api/stations`<br>`GET /api/stations/{id}`<br>`GET /api/stations/{id}/hydrograph`<br>`GET /api/stations/{id}/catchment-profile`<br>`GET /api/validation/leaderboard` | • Station catalog list (34 verified USGS stations).<br>• Selected station metadata, coordinates, drainage area.<br>• Flow percentiles ($q_{25}, q_{50}, q_{75}, q_{90}, \max$ in `cfs`).<br>• Continuous daily discharge hydrograph points.<br>• Out-of-system LORSO predictions (2022–2023 holdout).<br>• Catchment physiographic attributes & limitation indicator.<br>• Benchmark leaderboard (5 models, Pooled $R^2$ = 0.4910). | • Monte Carlo exceedance matrix scenario demonstration.<br>• Antecedent rainfall correlation indicators. |
| **Interactive Map** (`/map`) | `MapPage.tsx` | `GET /api/stations`<br>`GET /api/stations/{id}`<br>`GET /api/stations/{id}/hydrograph` | • Station markers plotted at exact WGS84 coordinates.<br>• Dynamic station count pill (`River Stations (34)`).<br>• Telemetry drawer showing verified flow percentiles.<br>• Actual historical sparkline for selected streamgauge. | • Simulated QPE radar overlay.<br>• Catchment polygon scenario boundaries.<br>• Rainfall runoff simulator slider.<br>• Citizen SOS signals (14 pins). |
| **Flood Alert Dispatch** (`/alerts`) | `AlertsPage.tsx` | `GET /api/stations`<br>`GET /api/stations/{id}` | • Active station broadcast logs populated with authentic USGS station IDs, names, and river systems.<br>• Alert hazard stages mapped against authentic flow percentiles ($> q_{90}$ Critical, $> q_{75}$ Warning, $> q_{50}$ Advisory).<br>• Risk card station count (`34 Total`). | • Multi-channel dispatch simulator (SMS, WhatsApp, Siren, Push).<br>• Simulated GPS geofence radius slider.<br>• Kin Lifeline family check-in network. |
| **Community Reporting** (`/community`) | `CommunityPage.tsx` | Local demo state (`frontend/src/data/demoData.ts`) | N/A (Frontend prototype for hackathon response evaluation) | • Tactile water depth reporting slider.<br>• Incident upvote feed.<br>• High-ground rescue dispatch request form. |
| **NGO Flood Relief** (`/relief`) | `ReliefPage.tsx` | Local demo state (`frontend/src/data/demoData.ts`) | N/A (Frontend prototype for hackathon response evaluation) | • Dispatch recommendation card (`#SAC-9402`).<br>• Resource inventory allocation.<br>• Mutual-aid NGO partner directory. |

---

## 3. Data Source & Endpoint Mapping

```
FastAPI Backend (http://127.0.0.1:8000)
│
├── /api/health ─────────────────────────> System Readiness Probe
│
├── /api/stations ───────────────────────> Station Selector Grid (Dashboard)
│                                         Map Station Pins & Viewport (Map)
│                                         Station Broadcast History (Alerts)
│                                         Global Search Dropdown (Navbar)
│
├── /api/stations/{id} ──────────────────> Selected Station Header & Badge (Dashboard)
│                                         Flow Percentiles Grid (Dashboard, Map)
│                                         Station Coordinates & Drainage Area (Map)
│
├── /api/stations/{id}/hydrograph ───────> Dynamic SVG Hydrograph (Dashboard)
│                                         Mini Discharge Sparkline (Map)
│
├── /api/stations/{id}/catchment-profile > Catchment Physiography Card (Dashboard)
│                                         Model Limitation Badge (Dashboard)
│
└── /api/validation/leaderboard ─────────> Top Model Metric Plaque (Dashboard)
                                          Global Pooled R² Badge (Navbar)
                                          Benchmark Comparison Table (Truth Engine)
```

---

## 4. Error Handling and Fallback Architecture

1. **Typed Fetch Client (`apiClient.ts`)**:
   - Centralized `fetch` wrapper using `VITE_API_BASE_URL` (default: `http://127.0.0.1:8000`).
   - Strict `ApiError` class capturing HTTP status codes, detail messages, and request aborts.
   - Transparent error extraction from FastAPI's standardized error schema (`{"detail": "..."}`).

2. **Dedicated React Service Hooks**:
   - `useStations(riverSystem?)`: Handles loading state, network error state, caching, and retry.
   - `useStation(stationId)`: Manages station detail retrieval.
   - `useHydrograph(stationId, start, end, model)`: Retrieves time-series records and validation holdouts.
   - `useValidation()`: Loads official 5-model LORSO leaderboard rankings.
   - `useCatchmentProfile(stationId)`: Manages verified physiography and limitation commentary.

3. **User-Facing Error UI (`ApiErrorBanner.tsx`)**:
   - Renders non-intrusive warning banners when backend connectivity is interrupted.
   - Provides a one-click "Retry Connection" button that triggers `reload()` on failed hooks without reloading the entire page.

4. **Graceful Fallback Mode**:
   - If the backend is temporarily offline, the frontend falls back safely to verified baseline records in `mockData.ts` to ensure UI stability during initial render.

---

## 5. Truth Engine & Scientific Data Integrity Compliance

| Requirement | Implementation Detail | Status |
| :--- | :--- | :---: |
| **Streamflow Units** | Every discharge label across all 5 pages strictly uses **`cfs` (cubic feet per second)**. No metric $m^3/s$ or unspecified units. | COMPLIANT |
| **Target Definition** | Target parameter is strictly identified as **USGS daily mean discharge: `00060_00003`**. The target is never claimed to be instantaneous maximum. | COMPLIANT |
| **Holdout Evaluation** | Model metrics are labeled strictly as **Pooled R² (LORSO Validation) = 0.4910** and holdout prediction error (RMSE = 82,871 cfs). Never labeled as "macro-averaged" or "live accuracy". | COMPLIANT |
| **Station 11447650 Limitation** | Station `11447650` (Sacramento River at Freeport, CA) observations end on `2015-09-30`. The UI explicitly displays a data limitation notice (`Historical Data Limitation (2015-09-30)`) and renders 0 modern 2022–2023 holdout predictions without inventing values. | COMPLIANT |
| **Missing Observation Integrity** | Missing streamflow dates are rendered with authentic breaks in the SVG path (`M` command start rather than line interpolation `L`). | COMPLIANT |
| **Station Count Label** | Navigation bar and dashboard cards dynamically report: `"Stations in PRAVAHA historical dataset (34 Total)"`. | COMPLIANT |
| **Demonstration Transparency** | Community reporting, emergency dispatch, and relief logistics carry explicit `TruthBanner` disclaimers: `[DEMO] Multi-channel broadcast is simulated for evaluation purposes. No real municipal notifications are sent.` | COMPLIANT |

---

## 6. Verification Summary

- **Backend Unit Tests**: 25/25 passing (`src/api/tests/test_api.py`, run time 0.27s).
- **Frontend TypeScript Build**: 0 errors, 0 warnings (`npm run build`, bundle size 325.35 kB).
- **End-to-End Full-Stack Verification**: 5/5 API endpoints verified passing in live runtime.
- **Headless Chrome Visual Capture**: 5/5 full-page desktop screenshots captured at `1440x900` resolution in `reports/ui_backend_integration_screenshots/`.

