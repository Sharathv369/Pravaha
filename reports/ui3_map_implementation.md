# PRAVAHA — Google Maps-Style River Intelligence Implementation
**Document ID**: `PRAVAHA-UI3-MAP-003`  
**Phase**: PROMPT UI-3 Geographic GIS Architecture & Unobstructed Canvas  
**Engine**: Official Google Maps JavaScript API Core (`VITE_GOOGLE_MAPS_API_KEY`) + Leaflet 1.9.4 Fallback  
**Date**: November 2026  

---

## 1. Architecture Overview

The **River Intelligence GIS Engine** (`/map`) transforms PRAVAHA into a real-time geospatial command center powered natively by the **Official Google Maps JavaScript API**. Built directly with the provided API key, it features authentic Google Maps terrain, hybrid satellite, and street tiles, hardware-accelerated smooth pan and zoom, instant station search with camera animation, and an unobstructed viewport where simulations and telemetry are cleanly separated into a dedicated side panel.

```
+---------------------------------------------------------------------------------------------------+
|  ACTIVE BASIN VIEWPORT PLAQUE  |  MODE: FLOOD / RELIEF  |  LAYERS: STATIONS, SHELTERS, RADAR...  |
+------------------------------------------------------------------+--------------------------------+
|                                                                  |  DEDICATED SIDE PANEL (COL 4)  |
|  UNOBSTRUCTED GOOGLE MAPS TILE CANVAS (COL 8)                   |                                |
|                                                                  |  [Tab 1: Historic] [Tab 2: Sim]|
|  [Style: Terrain | Satellite | Streets]     [Search & FlyTo]    |                                |
|                                                                  |  OPTION 1 — HISTORIC STATION:  |
|  * 38 USGS Streamgauge Pins (Pulsing Cyan DivIcons)              |  - Name, ID, River Basin       |
|  * 8 Certified High-Ground Shelters (Emerald Shield Beacons)     |  - Drainage Area & Coordinates |
|                                                                  |  - Date Range: 7d/30d/90d/1y   |
|  [Click anywhere -> Haversine Nearest Station Discovery]        |  - Verified Hydrograph Curve   |
|                                                                  |  - USGS Flow Percentiles (q90) |
|  [Scale: Metric / Imperial]               [+] [-] [Center Gauge] |                                |
|                                                                  |  OPTION 2 — RAINFALL SIMULATOR:|
|                                                                  |  - DEMO DISCLAIMER             |
|                                                                  |  - Precip Slider: 0 - 150 mm   |
|                                                                  |  - Duration: 6h / 12h / 24h    |
|                                                                  |  - Soil Saturation Level       |
|                                                                  |  - Peak Crest vs q90 Status    |
+------------------------------------------------------------------+--------------------------------+
|  TEMPORAL SURGE PROGRESSION SLIDER: -24h (History) <--- Present ---> +48h (Forecast)             |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Official Google Maps JavaScript API & Basemap Types

The map engine natively loads the **Google Maps JavaScript API** using `VITE_GOOGLE_MAPS_API_KEY`:

1. **Terrain (`google.maps.MapTypeId.TERRAIN`)**:
   - High-fidelity topographic elevation contours, shaded relief, hydrological vectors, and land-use markings.
2. **Satellite (`google.maps.MapTypeId.HYBRID`)**:
   - High-resolution global satellite imagery overlaid with major roads, river corridor labels, and municipal boundaries.
3. **Streets (`google.maps.MapTypeId.ROADMAP`)**:
   - Precise vector cartography showing road networks, bridges, levees, and evacuation arteries.

*Note: In offline sandbox environments without internet access, the engine automatically falls back to the embedded CartoDB / Leaflet tile cache so the application never breaks or displays a blank viewport.*

---

## 3. Unobstructed Canvas & Layout Separation

In the original layout, the Rainfall Scenario Simulator and Historic Telemetry drawers floated directly across the center and right half of the map canvas, completely blocking streamgauge markers and making safe spots invisible.

### The UI-3 Resolution:
- **Two-Column Side-by-Side Grid**:
  - `lg:col-span-8`: 100% unobstructed Google Maps interactive canvas ($640\text{px}$ height).
  - `lg:col-span-4`: Dedicated right-hand dock hosting all analytical telemetry and simulation controls.
- **Zero Center Floating Modals**: The map canvas has zero intrusive cards; only minimalist native map controls (style switcher, search bar, zoom dock, and distance scale) reside along the viewport margins.

---

## 4. Location Discovery via Haversine Distance Formula

Users can click **any arbitrary point** on the continental United States map to discover the nearest verified USGS streamgauging station.

### Mathematical Implementation:
Given click coordinates $(\phi_1, \lambda_1)$ and station coordinates $(\phi_2, \lambda_2)$:
$$\Delta \phi = \frac{(\phi_2 - \phi_1)\pi}{180}, \quad \Delta \lambda = \frac{(\lambda_2 - \lambda_1)\pi}{180}$$
$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos\left(\frac{\phi_1 \pi}{180}\right)\cos\left(\frac{\phi_2 \pi}{180}\right)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$
$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$
$$d = R_{\text{Earth}} \cdot c \quad (R_{\text{Earth}} = 3958.8 \text{ miles})$$

### User Experience:
When clicked, an animated pulse marker drops on the clicked point, and a floating discovery chip appears in the bottom-left corner:
`📍 Nearest Station: SACRAMENTO R A FREEPORT CA (ID: 11447650) — 4.6 miles away [Select]`

Clicking **Select** pans and zooms the camera directly to that station, opens its verified hydrograph in the side panel, and clears the discovery marker.

---

## 5. Two Clear Side Panel Modes

The side panel features a prominent two-tab segmented toggle:

### Option 1 — Historic Station Telemetry
- **Verified Metadata**: USGS Station Name, USGS 8-digit ID, River Basin, Coordinates, and verified drainage area ($\text{mi}^2$).
- **Interactive Multi-Range Hydrograph**: Date span switcher (`7d`, `30d`, `90d`, `1y`, `Full Record`) querying the FastAPI backend `/api/v1/hydrograph/{station_id}`.
- **Dual Curves**: Plots actual verified discharge alongside LORSO holdout predictions (for evaluated stations) with a prominent dashed red $q_{90}$ flood threshold line.
- **USGS Flow Percentiles**: Minimum recorded, $Q_{50}$ median, and $Q_{90}$ flood threshold ($00060\_00003 \text{ cfs}$).
- **Record Span & Completeness**: Displays observation date range and total days of mean daily flow recorded.

### Option 2 — Rainfall Scenario Simulator
- **Demonstration Banner**: Clearly labeled `⚠️ DEMONSTRATION SCENARIO — NOT OPERATIONAL FORECAST`.
- **Precipitation Depth Slider**: $0\text{ mm}$ (Dry) to $150\text{ mm}$ (Extreme atmospheric river).
- **Storm Duration**: Selector for $6\text{h}$, $12\text{h}$, $24\text{h}$, and $48\text{h}$ accumulation windows.
- **Antecedent Soil Moisture**: Three saturation states:
  - *Dry Basin* (Runoff coefficient $C = 0.35$)
  - *Normal Moisture* ($C = 0.65$)
  - *Fully Saturated* ($C = 0.92$)
- **Peak Crest Calculation (Rational Method)**:
  $$Q_{\text{crest}} = Q_{50} + \left(A_{\text{drainage}} \times \frac{I}{\max(T, 6)} \times C \times 18.5\right)$$
- **Threshold Comparison**: Evaluates calculated crest against the station's verified $q_{90}$ flood floor and displays real-time status:
  - `SUB-CRITICAL FLOW (SAFE)` (Below $85\%$ of $q_{90}$)
  - `APPROACHING FLOOD THRESHOLD` ($85\% - 100\%$ of $q_{90}$)
  - `CRITICAL EXCEEDANCE (+X%)` (Above $q_{90}$)

---

## 6. High-Ground Safe Evacuation Spots (8 Shelters)

All 8 certified high-ground shelters are fully indexed on the map with emerald shield markers:
- **Sacramento Bluffs Civic Shelter** ($+34\text{ ft}$ freeboard, $1,500$ capacity, VHF Ch 16)
- **Potomac Ridge High Ground Center** ($+42\text{ ft}$ freeboard, $2,200$ capacity, VHF Ch 12)
- **Red River Safe Haven High School** ($+26\text{ ft}$ freeboard, $1,800$ capacity)
- **Brazos Crest Evacuation Hub** ($+38\text{ ft}$ freeboard, $3,100$ capacity)
- **Willamette Terrace Safe Complex** ($+31\text{ ft}$ freeboard, $1,200$ capacity)
- **Susquehanna Heights Relief Depot** ($+45\text{ ft}$ freeboard, $2,500$ capacity)
- **Chattahoochee Uplands Evacuation Base** ($+50\text{ ft}$ freeboard, $2,800$ capacity)
- **Colorado Plateau Emergency Refuge** ($+65\text{ ft}$ freeboard, $1,400$ capacity)

Clicking any shelter marker displays its certified flood-free status, freeboard height above surge crest, stockpiled supplies, emergency contact, and a direct link to the NGO Relief Hub logistics router.

