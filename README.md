# 🌊 PRAVAHA — AI Flood Forecasting & Disaster Response Web Application

**PRAVAHA** (Sanskrit for *Continuous Flow*) is a real-time river discharge forecasting and emergency disaster management platform. Built with **React 18**, **TypeScript**, **Vite**, and **Tailwind CSS**, it combines hydrological telemetry, machine learning predictive intelligence, interactive GIS mapping, and community-driven rescue coordination.

---

## 🌟 Key Features & Architecture

- **🌊 National Hydrological Dashboard (`/`)**: Real-time river stages, discharge gauges, and flood risk categorization across continental US river basins using verified USGS telemetry.
- **🗺️ Interactive GIS Flood Map (`/map`)**: Dynamic basin boundary overlays, hydrological heatmaps, terrain/satellite toggles, and runoff simulations.
- **🚨 Early Warning & Evacuation Alerts (`/alerts`)**: Multi-channel broadcast simulations, emergency sirens, and time-to-peak warning thresholds.
- **🤝 Humanitarian Relief & Logistics Hub (`/relief`)**: Real-time emergency shelter occupancy, disaster inventory routing, and NGO dispatch coordination.
- **🛡️ Community Sentinel (`/community`)**: Crowdsourced citizen water level reports, emergency rescue SOS beacons with GPS coordinates.
- **👨‍👩‍👧 Kin Safety Circle (`/alerts`)**: Family member check-in ping network during flood evacuation scenarios.
- **🔬 Model Evaluation & Truth Engine (`/`)**: Transparent machine learning audit displaying out-of-system LORSO validation performance, hydrograph curves, and prediction confidence intervals.
- **🌐 Multilingual Support**: Built-in localization support (English, Hindi, Bengali) via React Context.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **npm**: v9.0.0 or higher

### 1. Installation
Clone the repository and install dependencies using the lockfile:
```bash
git clone https://github.com/Sharathv369/Pravaha.git
cd Pravaha

# Install dependencies
npm ci
# or
npm install
```

### 2. Environment Configuration
Copy `.env.example` to `.env` or `.env.local`:
```bash
cp .env.example .env.local
```

Configurable parameters:
```env
# URL for the PRAVAHA FastAPI backend service (Default: http://127.0.0.1:8000)
VITE_API_BASE_URL=http://127.0.0.1:8000

# Optional: Google Maps JavaScript API Key (for Google tile overlays)
VITE_GOOGLE_MAPS_API_KEY=
```

> **Note on Standalone / Offline Operation:**  
> The application includes comprehensive mock and fallback telemetry in `src/data/demoData.ts` and `src/data/mockData.ts`. If the FastAPI backend is not running, the frontend gracefully degrades to high-fidelity offline mode without crashing.

### 3. Development Server
Start the local Vite development server:
```bash
npm run dev
```
The application will be available at `http://localhost:5173/` (or `http://localhost:3000/`).

### 4. Production Build
Typecheck and create an optimized production bundle:
```bash
npm run build
```
To preview the production build locally:
```bash
npm run preview
```

---

## 🔌 Backend API Integration

The frontend seamlessly connects to the PRAVAHA FastAPI backend. Verified endpoints include:

| Endpoint | Method | Purpose |
|:---|:---:|:---|
| `/api/health` | `GET` | Service status diagnostic and reporting station health |
| `/api/stations` | `GET` | Real USGS station catalog (33 continental monitoring stations) |
| `/api/stations/{id}` | `GET` | Station metadata, flow percentiles (min, median, q90, max in `cfs`) |
| `/api/stations/{id}/hydrograph` | `GET` | Historical daily mean discharge (`00060_00003`) & ML forecast curves |
| `/api/stations/{id}/catchment-profile` | `GET` | Physiography (drainage area, elevation, slope, forest canopy) |
| `/api/validation/leaderboard` | `GET` | ML model benchmarks ranked by Leave-One-River-System-Out R² |

---

## 📁 Project Structure

```text
├── public/                    # Static assets, branding logos, favicon
├── src/
│   ├── assets/                # Application logos & vector badges
│   ├── components/            # Modular React components
│   │   ├── alerts/            # Alert cards, broadcast simulators, broadcast modals
│   │   ├── common/            # GlassCard, OceanButton, RiskBadge, StatCard, TruthBanner
│   │   ├── community/         # Citizen report forms, SOS beacon cards
│   │   ├── dashboard/         # National telemetry metrics, quick-filter panels
│   │   ├── layout/            # Top Navbar and responsive mobile BottomNav
│   │   ├── map/               # Map controls, layer toggles, legend
│   │   └── relief/            # Shelter cards, supply dispatch logs
│   ├── context/               # React Context providers (LanguageContext)
│   ├── data/                  # High-fidelity demo data & offline fallback fixtures
│   ├── hooks/                 # Custom React data-fetching hooks (useStations, useHydrograph)
│   ├── pages/                 # Full application pages (Dashboard, Map, Alerts, Relief, Community)
│   ├── services/              # API clients & HTTP request interceptors (apiClient)
│   ├── types/                 # TypeScript interfaces and API schemas
│   ├── App.tsx                # Application layout & navigation router
│   ├── index.css              # Global styles, Tailwind directives, custom scrollbars
│   └── main.tsx               # Application mounting entrypoint
├── index.html                 # HTML shell with viewport and Google Font imports
├── package.json               # Node packages and build scripts
├── postcss.config.js          # PostCSS processor config
├── tailwind.config.js         # Tailwind theme, emergency warning colors & animations
├── tsconfig.json              # TypeScript compilation rules
└── vite.config.ts             # Vite bundler configuration
```

---

## 🧪 Quality & Verification

- **TypeScript Compliance**: Strict type-checking enabled (`tsc --noEmit`).
- **Responsive Layout**: Designed for desktop monitoring command centers down to mobile field emergency operations.
- **Hydrological Integrity**: All discharge units strictly follow USGS standards (`cfs` — cubic feet per second).

---

## 📄 License
MIT License. Developed for flood risk reduction, civil protection, and emergency humanitarian logistics.
