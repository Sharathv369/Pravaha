# PRAVAHA — Live Demonstration & Evaluator Walkthrough Guide

This document provides a 3-minute rapid demonstration script and step-by-step evaluator walkthrough of the full-stack PRAVAHA platform.

---

## 🚀 1. One-Click System Launch

To launch both the FastAPI hydrological backend and the React operational dashboard simultaneously:

```bash
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1    # On Windows
source .venv/bin/activate       # On Linux/macOS

# Run the master dual-service launcher
python run_pravaha.py
```

- **Backend REST API**: `http://127.0.0.1:8000` (Swagger docs at `/docs`)
- **Frontend Dashboard**: `http://localhost:5173`

---

## 🧭 2. Step-by-Step UI Demonstration Script (3-Minute Tour)

### Minute 1: National Hydrological Overview & Telemetry
1. Open `http://localhost:5173` in your browser.
2. **Dashboard Overview**:
   - Highlight the **Truth Engine Banner** at the top verifying USGS Parameter `00060_00003` (Continuous Daily Mean Discharge in CFS).
   - Review national summary cards: **Active River Stations (33)**, **Monitoring Basins (23)**, **Validation Samples (24,088)**.
3. **Station Selector & Real Hydrograph**:
   - Select **Potomac River near Washington, DC (`01646500`)** or **Mississippi River at St. Paul, MN (`05331000`)**.
   - Inspect the interactive hydrograph: authentic historical discharge curve joined with 2022–2023 Leave-One-River-System-Out (LORSO) ML predictions.
   - Note the authentic SVG path breaks where historical records contain missing days (zero interpolation).

### Minute 2: Interactive GIS Flood Map & Terrain Layers
1. Click **River Map** in the navigation bar (`/map`).
2. Toggle between **Terrain Mode** and **High-Contrast Satellite Mode**.
3. Inspect the color-coded flood crest risk rings (Low: Cyan, Moderate: Amber, Major: Coral, Extreme: Crimson).
4. Select a station pin to view the slide-out catchment drawer with measured drainage area, elevation, and upstream dam-regulation limitation flags.
5. Demonstrate the **Runoff Scenario Slider** showing dynamic hydraulic stage responses.

### Minute 3: Disaster Coordination & Community Sentinel
1. Navigate to **Flood Alerts** (`/alerts`):
   - Review active hydrological severity tiers and time-to-peak warning thresholds.
   - Test the **Multi-Channel Emergency Broadcast Simulator** (Cell Broadcast, WhatsApp alert, Siren ping).
   - Test the **Kin Safety Circle** family member check-in simulation.
2. Navigate to **Community Sentinel** (`/community`):
   - Review crowdsourced citizen water depth reports and high-ground emergency SOS rescue beacons with GPS telemetry.
3. Navigate to **Relief Hub** (`/relief`):
   - Inspect real-time shelter capacity, medical supply inventory dispatch, and NGO logistics routing.

---

## 🔬 3. Machine Learning Model Audit Tour

Evaluators can review the independent machine learning audit reports in `reports/`:
- [`reports/prompt_k_accuracy_optimization.md`](../reports/prompt_k_accuracy_optimization.md) — Technical optimization report detailing the 14 experimental tracks.
- [`reports/prompt_k_final_recommendation.md`](../reports/prompt_k_final_recommendation.md) — Executive memo confirming the 3.5x peak-weighted LightGBM champion ($R^2 = 0.6090$, RMSE $= 72,626\text{ CFS}$).
- [`reports/prompt_k_canonical_benchmark_comparison.csv`](../reports/prompt_k_canonical_benchmark_comparison.csv) — Head-to-head comparison on the canonical 2022–2023 benchmark.

---

## 📸 4. Visual Asset Archive

High-resolution screenshots for all views, mobile layouts, and high-contrast satellite modes are archived in:
- `artifacts/screenshots/`
