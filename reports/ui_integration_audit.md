# PRAVAHA — UI/UX Reference Inspection & Integration Audit
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt UI-0 Primary Audit Document  
**Date**: November 2026  
**Auditor & Systems Architect**: Lead ML & Backend Systems Engineer  

---

## Executive Summary

This audit evaluates the architectural gap between the existing Python-based ML codebase and the five UI/UX screens provided in `design-reference/PRAVAHA_Stitch_UI_Reference (1).zip` (generated via Google Stitch).

The primary objective is to plan a seamless, realistic, and scientifically honest integration roadmap that transforms static HTML/Tailwind mockups into a responsive, operational frontend connected to our verified machine learning backend, **without presenting fake operational data as real telemetry**.

---

## 1. Existing Project Architecture & Current State

### 1.1 Technical Stack Audit
Inspection of the root directory and `src/` modules reveals:
- **Frontend Framework**: **NONE**. The repository currently contains no `package.json`, no React/Vue/Svelte framework, and no frontend build configuration.
- **Backend Framework**: `fastapi`, `uvicorn`, and `pydantic` are listed in `requirements.txt`, but **no API server (`main.py` or `api/`) has been deployed or instantiated yet**.
- **Data & Model Pipelines**:
  - `src/data/`: Complete, verified data acquisition and processing pipeline for USGS NWIS daily streamflow and NASA POWER meteorology.
  - `src/features/engineering.py`: 48 verified leakage-free features (rolling precipitation, temperatures, soil moisture dynamics, static catchment properties).
  - `src/models/`: Offline batch ML training and validation engines (`advanced_experiments.py`, `prompt_e_lorso_benchmark.py`).
  - `src/evaluate/`: Strict metric calculation (`metrics.py`, `validation.py`, `authenticate_dataset.py`).
- **Database Configuration**: **NONE**. All processed data is stored in high-performance local Parquet and CSV files in `data/processed/` (e.g. `PRAVAHA_TRAIN_LABELLED.csv`, `prompt_e_validation_predictions.parquet`).
- **Commands for Running Current System**:
  ```powershell
  # Virtual environment activation
  .\.venv\Scripts\Activate.ps1
  # Execute validation benchmarks
  .\.venv\Scripts\python.exe -m src.models.prompt_e_lorso_benchmark
  ```

---

## 2. Stitch Reference Package Inspection

The extracted package `stitch_pravaha_disaster_command_center` contains:
1. `pravaha_main_dashboard/` (`code.html` 59.7 KB, `screen.png` 10.8 MB)
2. `pravaha_interactive_google_maps/` (`code.html` 42.0 KB, `screen.png` 961 KB)
3. `pravaha_advanced_flood_alert_system/` (`code.html` 43.3 KB, `screen.png` 589 KB)
4. `pravaha_community_reporting_system/` (`code.html` 52.1 KB, `screen.png` 623 KB)
5. `pravaha_ngo_flood_relief_hub/` (`code.html` 57.3 KB, `screen.png` 426 KB)
6. `oceanic_hydrological_intelligence/DESIGN.md` (13.8 KB design specification)

### 2.1 Technical Assessment of Stitch Deliverables
- **Format**: All five screens are **standalone, self-contained static HTML prototypes**.
- **Styling**: Loaded via `<script src="https://cdn.tailwindcss.com">` with an inline Tailwind theme configuration block extending custom oceanic color tokens.
- **Typography & Icons**: Uses Google Web Fonts for `Inter` and `Material Symbols Outlined`.
- **Interactivity**: Strictly simulated via minimal vanilla JavaScript:
  - Button active click animations (`scale-95`).
  - Simple tab switching (toggling `hidden` class on container divs).
  - Slider value text mirroring (`radiusSlider.addEventListener('input', ...)`).
  - No real chart libraries (hydrographs are hardcoded SVG `<polyline>` tags).
  - No real map engine (the map is a static SVG/CSS mockup with placeholder pins).

---

## 3. Design System & Visual Language Preservation

The design system documented in `oceanic_hydrological_intelligence/DESIGN.md` must be preserved faithfully:

### 3.1 Color Palette
- **Canvas Base**: Atmospheric light sky `#EFF6FA` / `#F6F9FF`.
- **Glass Surfaces**: `rgba(255, 255, 255, 0.76)` with `backdrop-filter: blur(12px)` and border `#D8E8F0`.
- **Primary Ocean Blue**: `#287BB5` (triggers, active tabs, primary curves).
- **Deep Marine Slate**: `#17354D` (headings, high-contrast text).
- **Clear Cyan**: `#51B9CC` (projections, secondary indicators).
- **Semantic Risk Indicators**:
  - Normal: `#40A77A` (Green)
  - Advisory: `#D5A83E` (Amber)
  - Warning: `#E58C47` (Orange)
  - Critical / Surge: `#D95F62` (Red)
  - Emergency Broadcast Accent: `#E98985` (Soft Coral)

### 3.2 Typography & Spacing
- **Font Family**: Inter, paired with `font-variant-numeric: tabular-nums` for all telemetry, timestamps, discharge numbers, and coordinates.
- **Corner Radii**: `12px` (`0.75rem`) for buttons, `16px` to `20px` (`1.25rem`) for cards.
- **Elevation**: Ambient marine-tinted shadows (`0 10px 30px -10px rgba(32, 92, 137, 0.08)`) with zero harsh black drop shadows.

---

## 4. Gap Analysis: Frontend vs Backend Functionality

| Screen / Feature | Stitch UI Prototype State | Existing PRAVAHA Backend State | Integration Feasibility & Strategy |
| :--- | :--- | :--- | :--- |
| **Main Dashboard: Station Telemetry** | Hardcoded cards for 5 core stations with fake instantaneous flows. | 34 real USGS stations with daily mean discharge up to 2023. | **HIGH**: Expose `/api/stations` and `/api/stations/{id}/latest` to populate real USGS stations. |
| **Main Dashboard: Hydrographs** | Hardcoded SVG `<polyline>` points. | 14 years of real USGS discharge + 2 years of out-of-system model predictions. | **HIGH**: Replace SVG with Recharts or Chart.js powered by `/api/stations/{id}/hydrograph`. |
| **Interactive Map** | Static image/SVG with hardcoded pin overlays. | Verified coordinates (lat/long), state, and river basin for 34 stations. | **HIGH**: Implement Leaflet or MapLibre React component consuming `/api/stations/geojson`. |
| **AI Prediction & Truth Engine** | Fake "99.4% Confidence" banner. | Real LORSO validation results, RMSE, MAE, R², and p10/p50/p90 quantile intervals. | **HIGH**: Build dedicated Truth Engine tab displaying real verified ML metrics and uncertainty envelopes. |
| **Flood Alert Dispatch Pipeline** | Simulated SMS, WhatsApp, Siren toggle switches. | No external SMS or siren gateways configured. | **MEDIUM (DEMO ONLY)**: Retain as an operational broadcast simulator with mock preview modals. |
| **Community Reporting Feed** | Static mock incident list with mock photo tags. | No user submission database or image storage. | **MEDIUM (DEMO ONLY)**: Implement local-storage mock form for hazard reporting; label clearly as prototype. |
| **NGO Relief Hub & Dispatch** | Static resource matrix (boats, rations, shelters). | No logistics or warehouse inventory database. | **MEDIUM (DEMO ONLY)**: Retain as demonstration resource matrix; label as future module. |

---

## 5. Recommended Technical Architecture

To implement the frontend cleanly without disturbing the verified ML engine:

```
c:\Users\Lenovo\OneDrive\Desktop\pravaha\
├── frontend/                     # NEW: React 18 + Vite + Tailwind CSS Application
│   ├── src/
│   │   ├── components/           # Reusable Oceanic Glassmorphic components
│   │   │   ├── common/           # GlassCard, OceanButton, RiskBadge, StatPill
│   │   │   ├── dashboard/        # StationCard, HydrographViewer, BasinOverview
│   │   │   ├── map/              # RiverNetworkMap, StationMarker, InundationOverlay
│   │   │   └── shared/           # TopNavbar, AlertBanner, TruthEngineModal
│   │   ├── pages/                # Route Views
│   │   │   ├── DashboardPage.jsx # Screen 1: Command Center Dashboard
│   │   │   ├── MapPage.jsx       # Screen 2: Interactive River Map
│   │   │   ├── AlertsPage.jsx    # Screen 3: Flood Alert System
│   │   │   ├── CommunityPage.jsx # Screen 4: Community Reporting (Demo Mode)
│   │   │   └── ReliefPage.jsx    # Screen 5: NGO Relief Hub (Demo Mode)
│   │   └── services/api.js       # Axios/Fetch client connected to FastAPI
├── src/api/                      # NEW: Lightweight FastAPI Backend Service
│   ├── main.py                   # FastAPI app entry point & CORS configuration
│   ├── routes/
│   │   ├── stations.py           # Endpoints for station metadata & hydrographs
│   │   ├── predictions.py        # Endpoints for real model predictions & quantiles
│   │   └── validation.py         # Endpoints for LORSO benchmarks & audit metrics
```

---

## 6. Implementation Sequence & Next Steps

1. **Step 1: Backend Foundation (FastAPI)**:
   - Create `src/api/` and implement read-only data endpoints serving verified USGS station data, hydrograph histories, and model predictions directly from existing Parquet files.
2. **Step 2: Frontend Scaffold (Vite + React + Tailwind)**:
   - Initialize `frontend/` using Vite, configure Tailwind CSS with the exact Oceanic color palette and Inter typography from `DESIGN.md`.
3. **Step 3: Core Functional Integration**:
   - Implement Screen 1 (Disaster Command Dashboard) and Screen 2 (Interactive River Map) connected to live FastAPI endpoints.
4. **Step 4: Truth Engine & Hydrograph Component**:
   - Embed real Recharts-based hydrographs with historical ground truth, LightGBM predicted flow, and p10–p90 uncertainty bands.
5. **Step 5: Demonstration Feature Containment**:
   - Implement Screen 3 (Alerts), Screen 4 (Community Reports), and Screen 5 (NGO Hub) with explicit "Demonstration Prototype" disclaimers to preserve scientific integrity.

