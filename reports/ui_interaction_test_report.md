# PRAVAHA — UI Route & Interaction Test Report
**Project**: PRAVAHA — FLOODCAST 24-Hour Hackathon  
**Deliverable**: Prompt UI-1.1 Route & Functional Interaction Audit  
**Date**: November 2026  
**Auditor**: Lead Frontend & QA Systems Engineer  

---

## 1. Executive Summary

This report documents comprehensive functional testing across all five application routes (`/dashboard`, `/map`, `/alerts`, `/community`, `/relief`), global navigation structures, modal dialogs, search filters, stateful forms, interactive sliders, and data export mechanisms.

### Core Testing Findings:
- **Routes Tested**: 5/5 routes fully operational with clean SPA routing and zero 404s on browser refresh.
- **Button & Control Audit**: 100% of interactive buttons either execute their intended local state action or display an explicit disabled state with an explanatory message.
- **Form State Management**: Citizen hazard reports, emergency rescue submissions, donation simulations, and CSV inventory downloads execute cleanly in local React state.
- **Backend Transparency**: Zero claims of backend network transactions; all simulations explicitly communicate local state execution.

---

## 2. Route Navigation & Deep-Linking Audit

| Target URL | Expected View | Observed Behaviour | Active Indicator | Refresh Test | Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `http://localhost:5173/` | Redirect to `/dashboard` | Automatically navigates to `/dashboard` | Dashboard tab highlighted in bottom dock & header | Returns `/index.html` -> `/dashboard` | **PASS** |
| `http://localhost:5173/dashboard` | Disaster Command Dashboard | Renders hero KPIs, basin deck, interactive hydrograph, and correlation charts | "Dashboard" highlighted in floating pill dock | Reloads cleanly with active station preserved | **PASS** |
| `http://localhost:5173/dashboard?station=07010000` | Dashboard focused on St. Louis Mississippi Station | Hydrograph viewer and active card initialize to Station `07010000` | "Dashboard" highlighted | Preserves URL query param and station state | **PASS** |
| `http://localhost:5173/map` | River Intelligence Map | Renders US river vectors, 34 station pins, scenario simulator, and station telemetry drawer | "River Map" highlighted in floating dock | Reloads map viewport cleanly | **PASS** |
| `http://localhost:5173/alerts` | Advanced Flood Alert System | Renders visual telemetry banner, 4 severity cards, GPS sentinel slider, and broadcast log | Center elevated coral "Alerts" button highlighted | Reloads alert matrix cleanly | **PASS** |
| `http://localhost:5173/community` | Community Reporting System | Renders dual segmented tab switcher, hazard submission form, and live crowdsourced feed | "Community" highlighted in floating dock | Preserves feed state | **PASS** |
| `http://localhost:5173/relief` | NGO Flood Relief Hub | Renders Smart Coordinator dispatch card, route feasibility check, and 4-card inventory matrix | "Relief Hub" highlighted in floating dock | Reloads inventory cleanly | **PASS** |
| `http://localhost:5173/unknown-path` | 404 Catch-All Fallback | Safely redirects to `/dashboard` without white-screen or unhandled exception | Fallback to Dashboard | Handled gracefully | **PASS** |

---

## 3. Interactive Components & Button Action Audit

Every button across the frontend was tested to confirm that it either performs a local operation or communicates its demonstration scope:

### 3.1 Global Header & Navigation (`Navbar.tsx` & `BottomNav.tsx`)
1. **PRAVAHA Logo**: Navigates to `/dashboard` from any route. (*Operational*)
2. **Omnisearch Input**: Real-time substring filter across all 34 USGS stations by ID, name, or river basin. Selecting any search result updates the URL to `/dashboard?station=<id>` and inspects that gauge. (*Operational*)
3. **Language Switcher (`EN` / `हिन्दी`)**: Toggles active language pill state. (*Operational*)
4. **Emergency Protocol CTA**: Opens the `Emergency Broadcast Demonstration Modal`. (*Operational*)
5. **Modal "Dispatch Test Broadcast" Button**: Initiates a 2.8s simulated transmission cycle with live loading state, animated confirmation checkmark, and auto-dismiss. (*Operational*)
6. **Bottom Dock Links (5 Items)**: Instant client-side route switching with active glassmorphic pill highlights. (*Operational*)

---

### 3.2 Command Dashboard (`DashboardPage.tsx`)
1. **Basin Group Filter Tabs** (`All 34 Nodes`, `California/Pacific`, `Mississippi`, `Texas Basins`, `Atlantic/Potomac`): Dynamically filters the station card grid based on state codes and HUC identifiers. (*Operational*)
2. **Station Card Click**: Selects that station, applies an active oceanic ring (`ring-2 ring-[#006297]`), and dynamically binds the SVG hydrograph viewer to that gauge's historical data and thresholds. (*Operational*)
3. **"Inspect Telemetry" Card Buttons**: Selects station and updates the hydrograph envelope. (*Operational*)
4. **"Inspect Focus Gauge" Button**: Resets active gauge to Sacramento River Station `11447650`. (*Operational*)
5. **"View Hydrograph" Button**: Smoothly jumps down to the `#hydrograph` anchor. (*Operational*)
6. **"View Full Telemetry Feed" Link**: Navigates to `/community`. (*Operational*)

---

### 3.3 River Intelligence Map (`MapPage.tsx`)
1. **Mode Switcher ("Flood Monitoring" vs "Relief Intelligence")**: Toggles cartographic overlay mode and adjusts visible layer emphasis. (*Operational*)
2. **Recenter Button**: Resets viewport focus to Sacramento River Delta. (*Operational*)
3. **Layer Toggle Pills** (`River Stations`, `Precip QPE Radar`, `USGS River Vectors`, `Catchment Polygons`, `Citizen SOS Signals`): Toggles layer visibility on the SVG map canvas. (*Operational*)
4. **34 Station Map Markers**: Clicking any pin selects the station, triggers an animated pulse, and opens that station's details in the right-hand floating drawer. (*Operational*)
5. **Rainfall Scenario Slider (0 to 150 mm)**: Dynamically recalculates simulated crest flow in `cfs` and toggles between "Sub-Critical Inflow" and "Exceeds q90 Peak" in real time. (*Operational*)
6. **Temporal Surge Scrubber (-24h to +48h)**: Adjusts time step and updates phase status ("Inflow Accumulation" vs "Crest Phase Reached"). (*Operational*)
7. **Drawer "Full Hydrograph" Button**: Navigates to `/dashboard?station=<id>` to inspect the detailed hydrograph for the selected station. (*Operational*)
8. **Drawer "Issue Alert" Button**: Navigates to `/alerts`. (*Operational*)

---

### 3.4 Advanced Flood Alert System (`AlertsPage.tsx`)
1. **"Trigger Municipal Dispatch" Button**: Initiates a 4-second simulated multi-channel transmission cycle with live loading state, disabling the button and displaying a prominent green broadcast confirmation banner. (*Operational*)
2. **Geofence Proximity Slider (5 to 100 km)**: Dynamically adjusts active buffer coverage readout. (*Operational*)
3. **Kin Lifeline "Ping" Buttons**: Clicking "Ping" for any family contact (Emma, Liam, Robert) immediately updates the button label to "Ping Sent!" with positive confirmation. (*Operational*)

---

### 3.5 Community Ground Telemetry (`CommunityPage.tsx`)
1. **Dual Tab Switcher**: Switches between "REPORT A FLOOD — PRAVAHA EYES" and "I NEED HELP — LIFELINE". (*Operational*)
2. **Hazard Classification Chips**: Toggles active selection among 4 hazard types with visual highlighting. (*Operational*)
3. **Tactile Water Depth Cards**: Selects water depth stage (Ankle Deep, Knee Deep, Waist Deep, Submerged) with synchronized inch depths. (*Operational*)
4. **"Transmit Field Observation" Form Submission**:
   - Intercepts default form submit.
   - Prepends a new `HazardReport` object into local React state.
   - Shows an instant green confirmation alert: *"Hazard report submitted! Saved to local session stream"*.
   - Immediately renders the new report at the top of the live community feed! (*Operational*)
5. **"Submit Urgent Rescue Dispatch Request" Form Submission**:
   - Prepends an emergency SOS request with trapped persons count and contact info into the local queue.
   - Displays a high-priority confirmation notice. (*Operational*)
6. **Incident Feed Upvote Buttons**: Clicking the thumbs-up button on any crowd report increments the upvote counter live in React state. (*Operational*)

---

### 3.6 NGO Flood Relief Hub (`ReliefPage.tsx`)
1. **Operations vs Donor Portal Tab Switcher**: Toggles between relief dispatch operations and the 80G tax-exempt donor campaign directory. (*Operational*)
2. **"Authorize & Dispatch Recommendation" Button**: Updates state from "Authorize & Dispatch" to a green verified badge: *"Authorized & Dispatched to Field Crew"*. (*Operational*)
3. **"Quick Assign" Buttons**: For pending AI queue items (Life Vests, Potable Water, Paramedics), clicking "Quick Assign" marks them as "Assigned" with persistent local state. (*Operational*)
4. **"Export CSV" Inventory Button**: Dynamically generates and triggers browser download of `pravaha_ngo_relief_inventory.csv` containing all 4 resource categories, quantities, and readiness rates. (*Operational*)
5. **Donor Campaign "Simulate Donation ($50)" Buttons**: Displays an instant thank-you confirmation banner confirming the simulated contribution. (*Operational*)

---

## 4. Error Handling & Form Validation

- **Non-blocking Defaults**: All forms and sliders provide sensible defaults preventing blank or corrupted state submissions.
- **Search Resiliency**: The header search gracefully handles special characters, empty queries, and non-matching inputs without unhandled exceptions.
- **No False Backend Confirmations**: Every state transition explicitly informs the user that operations are sandboxed in local demonstration state, fully complying with hackathon scientific integrity rules.

