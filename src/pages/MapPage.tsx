import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Compass,
  Waves,
  Activity,
  ShieldCheck,
  Calendar,
  ExternalLink,
  X,
  PhoneCall,
  Plus,
  Minus,
  Crosshair,
  Search,
  Maximize2,
  MapPin,
  ArrowRight,
} from 'lucide-react';
import TruthBanner from '../components/common/TruthBanner';
import ApiErrorBanner from '../components/common/ApiErrorBanner';
import { useStations } from '../hooks/useStations';
import { useStation } from '../hooks/useStation';
import { useHydrograph } from '../hooks/useHydrograph';
import { ApiStationItem, ApiHydrographPoint } from '../types/api';
import { useLanguage } from '../context/LanguageContext';
import { VERIFIED_STATIONS } from '../data/mockData';

// Declare Google Maps & Leaflet globals
declare const google: any;
declare const L: any;

export interface SafeSpot {
  id: string;
  name: string;
  name_hi: string;
  basin: string;
  basin_hi: string;
  latitude: number;
  longitude: number;
  elevation_freeboard_ft: number;
  capacity: number;
  supplies: string;
  supplies_hi: string;
  contact: string;
}

export const SAFE_SPOTS: SafeSpot[] = [
  {
    id: 'SHELTER-01',
    name: 'Sacramento Bluffs Civic Shelter',
    name_hi: 'सैक्रामेंटो ब्लफ़्स नागरिक आश्रय',
    basin: 'California Central Valley',
    basin_hi: 'कैलिफ़ोर्निया सेंट्रल वैली',
    latitude: 38.62,
    longitude: -121.35,
    elevation_freeboard_ft: 34,
    capacity: 1500,
    supplies: 'Medical Bay, Potable Water, Emergency Gen',
    supplies_hi: 'चिकित्सा कक्ष, पेयजल, आपातकालीन जनरेटर',
    contact: 'VHF Ch 16 / 916-555-0192',
  },
  {
    id: 'SHELTER-02',
    name: 'Potomac Ridge High Ground Center',
    name_hi: 'पोटोमैक रिज उच्च भूमि केंद्र',
    basin: 'Potomac River Basin',
    basin_hi: 'पोटोमैक नदी बेसिन',
    latitude: 39.15,
    longitude: -77.30,
    elevation_freeboard_ft: 42,
    capacity: 2200,
    supplies: 'Helipad, FEMA Rations, Solar Microgrid',
    supplies_hi: 'हेलीपैड, फेमा राशन, सौर माइक्रोग्रिड',
    contact: 'VHF Ch 12 / 202-555-0144',
  },
  {
    id: 'SHELTER-03',
    name: 'Red River Safe Haven High School',
    name_hi: 'रेड रिवर सेफ हेवन हाई स्कूल',
    basin: 'Red River System',
    basin_hi: 'रेड रिवर सिस्टम',
    latitude: 47.95,
    longitude: -97.05,
    elevation_freeboard_ft: 26,
    capacity: 1800,
    supplies: 'Warm Beds, Infant Care, Satellite Comms',
    supplies_hi: 'गर्म बिस्तर, शिशु देखभाल, उपग्रह संचार',
    contact: '701-555-0188',
  },
  {
    id: 'SHELTER-04',
    name: 'Brazos Crest Evacuation Hub',
    name_hi: 'ब्राजोस क्रेस्ट निकासी केंद्र',
    basin: 'Brazos River Basin',
    basin_hi: 'ब्राजोस नदी बेसिन',
    latitude: 30.65,
    longitude: -96.35,
    elevation_freeboard_ft: 38,
    capacity: 3100,
    supplies: 'Amphibious Fleet Staging, Mobile Clinic',
    supplies_hi: 'उभयचर बेड़ा, सचल क्लिनिक',
    contact: '979-555-0112',
  },
  {
    id: 'SHELTER-05',
    name: 'Willamette Terrace Safe Complex',
    name_hi: 'विलामेट टेरेस सुरक्षित परिसर',
    basin: 'Willamette River',
    basin_hi: 'विलामेट नदी',
    latitude: 45.48,
    longitude: -122.62,
    elevation_freeboard_ft: 31,
    capacity: 1200,
    supplies: 'Water Purification, Pet Shelter, Warm Blankets',
    supplies_hi: 'जल शोधन, पालतू पशु आश्रय, कंबल',
    contact: '503-555-0176',
  },
  {
    id: 'SHELTER-06',
    name: 'Susquehanna Heights Relief Depot',
    name_hi: 'सस्क्यूहाना हाइट्स राहत डिपो',
    basin: 'Susquehanna River',
    basin_hi: 'सस्क्यूहाना नदी',
    latitude: 40.30,
    longitude: -76.85,
    elevation_freeboard_ft: 45,
    capacity: 2500,
    supplies: 'National Guard Logistics, Trauma First Aid',
    supplies_hi: 'राष्ट्रीय रसद, आपातकालीन प्राथमिक उपचार',
    contact: '717-555-0133',
  },
  {
    id: 'SHELTER-07',
    name: 'Chattahoochee Uplands Evacuation Base',
    name_hi: 'चट्टाहूची अपलैंड्स निकासी बेस',
    basin: 'Apalachicola Basin',
    basin_hi: 'अपलाचिकोला बेसिन',
    latitude: 33.78,
    longitude: -84.45,
    elevation_freeboard_ft: 50,
    capacity: 2800,
    supplies: 'Disaster Relief Pantry, Power Station, Comms Hub',
    supplies_hi: 'आपदा राहत भंडार, पावर स्टेशन, संचार हब',
    contact: '404-555-0199',
  },
  {
    id: 'SHELTER-08',
    name: 'Colorado Plateau Emergency Refuge',
    name_hi: 'कोलोराडो पठार आपातकालीन शरण',
    basin: 'Colorado River Basin',
    basin_hi: 'कोलोराडो नदी बेसिन',
    latitude: 39.08,
    longitude: -108.55,
    elevation_freeboard_ft: 65,
    capacity: 1400,
    supplies: 'Mountain Rescue, Cold Weather Rations, Drone Bay',
    supplies_hi: 'पर्वत बचाव, शीतकालीन राशन, ड्रोन बे',
    contact: '970-555-0160',
  },
];

// Haversine distance calculator in statute miles
function calculateHaversineMiles(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 3958.8; // Earth radius in miles
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Number((R * c).toFixed(1));
}

export interface CitizenSosSignal {
  id: string;
  lat: number;
  lng: number;
  title: string;
  basin: string;
  depth: string;
  urgency: 'CRITICAL' | 'HIGH' | 'MODERATE';
  time: string;
}

export const CITIZEN_SOS_SIGNALS: CitizenSosSignal[] = [
  { id: 'SOS-01', lat: 38.58, lng: -121.49, title: 'Sacramento Levee Seepage', basin: 'California Central Valley', depth: '48 in', urgency: 'CRITICAL', time: '12m ago' },
  { id: 'SOS-02', lat: 38.64, lng: -121.39, title: 'American River Submerged Road', basin: 'California Central Valley', depth: '36 in', urgency: 'HIGH', time: '24m ago' },
  { id: 'SOS-03', lat: 38.48, lng: -121.52, title: 'Freeport Slough Trapped Vehicle', basin: 'California Central Valley', depth: '42 in', urgency: 'CRITICAL', time: '8m ago' },
  { id: 'SOS-04', lat: 39.02, lng: -77.15, title: 'Potomac Towpath Breach', basin: 'Potomac River Basin', depth: '24 in', urgency: 'MODERATE', time: '35m ago' },
  { id: 'SOS-05', lat: 38.92, lng: -77.08, title: 'Georgetown Waterfront Surge', basin: 'Potomac River Basin', depth: '30 in', urgency: 'HIGH', time: '18m ago' },
  { id: 'SOS-06', lat: 30.27, lng: -97.74, title: 'Shoal Creek Debris Jam', basin: 'Colorado River Basin', depth: '28 in', urgency: 'HIGH', time: '40m ago' },
  { id: 'SOS-07', lat: 38.62, lng: -90.18, title: 'St. Louis Riverfront Wall Crest', basin: 'Mississippi River', depth: '52 in', urgency: 'CRITICAL', time: '5m ago' },
  { id: 'SOS-08', lat: 47.92, lng: -97.03, title: 'Red River Coulee Inflow Blockage', basin: 'Red River System', depth: '22 in', urgency: 'MODERATE', time: '50m ago' },
];

export const MapPage: React.FC = () => {
  const navigate = useNavigate();
  const { language, t } = useLanguage();
  const {
    stations: apiStations,
    error: stationsError,
    reload: refetchStations,
  } = useStations();

  // Ensure all 38 verified stations are always available (API first, fallback to mockData)
  const stations: ApiStationItem[] = useMemo(() => {
    if (apiStations && apiStations.length > 0) return apiStations;
    return (VERIFIED_STATIONS.map((s) => ({
      station_id: s.station_id,
      station_name: s.station_name,
      river_name: s.river_name,
      river_system: s.river_system,
      state_cd: Number(s.state_cd) || 0,
      state: String(s.state_cd),
      latitude: s.latitude,
      longitude: s.longitude,
      drainage_area_sqmi: s.drainage_area_sqmi,
      drainage_area_verification_status: 'VERIFIED',
      observation_start: '2010-01-01',
      observation_end: '2023-12-31',
      total_observations: 5113,
      data_quality_status: 'VERIFIED',
      is_core_station: s.has_validation_data,
      has_2022_2023_validation: s.has_validation_data,
    })) as unknown as ApiStationItem[]);
  }, [apiStations]);

  // Selected station / shelter / interaction states
  const [selectedStationId, setSelectedStationId] = useState<string>('11447650');
  const [selectedSafeSpotId, setSelectedSafeSpotId] = useState<string | null>(null);
  const [selectedSosId, setSelectedSosId] = useState<string | null>(null);
  const [sidePanelTab, setSidePanelTab] = useState<'historic' | 'simulator'>('historic');
  const [mapMode, setMapMode] = useState<'flood' | 'relief'>('flood');
  const [timeStep, setTimeStep] = useState<number>(0); // 0 = Present, -24 to +48
  const [mapStyle, setMapStyle] = useState<'terrain' | 'satellite' | 'streets'>(() => {
    if (typeof window !== 'undefined' && window.location.search.includes('style=satellite')) {
      return 'satellite';
    }
    if (typeof window !== 'undefined' && window.location.search.includes('style=streets')) {
      return 'streets';
    }
    return 'terrain';
  });
  const [stationSearch, setStationSearch] = useState<string>('');
  const [hydroDateRange, setHydroDateRange] = useState<'7d' | '30d' | '90d' | '1y' | 'all'>('30d');
  const [engineMode, setEngineMode] = useState<'google' | 'leaflet'>('google');

  // Nearest station discovery on arbitrary map click
  const [nearestDiscovery, setNearestDiscovery] = useState<{
    station: ApiStationItem;
    distanceMiles: number;
    clickLat: number;
    clickLng: number;
  } | null>(null);

  // Rainfall Scenario Simulator State (Option 2)
  const [rainfallInflow, setRainfallInflow] = useState<number>(45); // mm
  const [scenarioDuration, setScenarioDuration] = useState<number>(24); // hours: 6, 12, 24, 48
  const [soilMoisture, setSoilMoisture] = useState<'DRY' | 'NORMAL' | 'SATURATED'>('NORMAL');

  // Active Map Layers
  const [activeLayers, setActiveLayers] = useState({
    stations: true,
    shelters: true,
    radar: true,
    vectors: true,
    polygons: true,
    sos: true,
  });

  // Map DOM & Engine references
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const googleMapRef = useRef<any>(null);
  const googleMarkersRef = useRef<any[]>([]);
  const googleShelterMarkersRef = useRef<any[]>([]);
  const googleSosMarkersRef = useRef<any[]>([]);
  const googleClickMarkerRef = useRef<any>(null);

  const leafletMapRef = useRef<any>(null);
  const tileLayerRef = useRef<any>(null);
  const stationMarkersGroupRef = useRef<any>(null);
  const shelterMarkersGroupRef = useRef<any>(null);
  const sosMarkersGroupRef = useRef<any>(null);
  const clickMarkerRef = useRef<any>(null);

  // Station and Hydrograph details
  const { station: selectedDetail } = useStation(selectedStationId);
  const currentStationSummary =
    stations.find((s) => s.station_id === selectedStationId) || stations[0];

  // Dynamically compute hydrograph dates based on the selected station's real observation window
  const dateParams = useMemo(() => {
    const endStr = selectedDetail?.observation_end || currentStationSummary?.observation_end || '2023-12-31';
    const startStr = selectedDetail?.observation_start || currentStationSummary?.observation_start || '2010-01-01';

    const [yStr, mStr, dStr] = endStr.split('-');
    const endYear = parseInt(yStr, 10) || 2023;
    const endMonth = parseInt(mStr, 10) || 12;
    const endDay = parseInt(dStr, 10) || 31;

    const endDate = new Date(Date.UTC(endYear, endMonth - 1, endDay));
    let startDate = new Date(endDate);

    if (hydroDateRange === '7d') {
      startDate.setUTCDate(endDate.getUTCDate() - 7);
    } else if (hydroDateRange === '30d') {
      startDate.setUTCDate(endDate.getUTCDate() - 30);
    } else if (hydroDateRange === '90d') {
      startDate.setUTCDate(endDate.getUTCDate() - 90);
    } else if (hydroDateRange === '1y') {
      startDate.setUTCFullYear(endDate.getUTCFullYear() - 1);
    } else {
      return { start: startStr, end: endStr };
    }

    const fmt = (d: Date) => d.toISOString().split('T')[0];
    return { start: fmt(startDate), end: fmt(endDate) };
  }, [hydroDateRange, selectedDetail, currentStationSummary]);

  const { hydrograph: hydroData } = useHydrograph(
    selectedStationId,
    dateParams.start,
    dateParams.end,
    'log_spec_q'
  );

  const selectedShelter = SAFE_SPOTS.find((s) => s.id === selectedSafeSpotId);

  // Toggle layer visibility
  const toggleLayer = (key: keyof typeof activeLayers) => {
    setActiveLayers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Format CFS numbers cleanly
  const formatCfs = (val: number | null | undefined) => {
    if (val == null || isNaN(val)) return '—';
    if (val >= 1000000) return `${(val / 1000000).toFixed(2)}M cfs`;
    if (val >= 1000) return `${(val / 1000).toFixed(1)}k cfs`;
    return `${Math.round(val).toLocaleString()} cfs`;
  };

  // Scenario Crest Flow Calculation using Rational Method Runoff
  const drainageSqMi = selectedDetail?.drainage_area_sqmi || currentStationSummary?.drainage_area_sqmi || 2500;
  const runoffCoeff = soilMoisture === 'DRY' ? 0.35 : soilMoisture === 'NORMAL' ? 0.65 : 0.92;
  const intensityFactor = rainfallInflow / Math.max(scenarioDuration, 6);
  const medianFlow = selectedDetail?.flow_thresholds_cfs?.q50_median_cfs || 12000;
  const q90Threshold = selectedDetail?.flow_thresholds_cfs?.q90_threshold_cfs || 35000;
  const simulatedCrestFlow = Math.round(
    medianFlow + drainageSqMi * intensityFactor * runoffCoeff * 18.5
  );
  const isSurgeOverThreshold = simulatedCrestFlow > q90Threshold;
  const isApproachingThreshold = !isSurgeOverThreshold && simulatedCrestFlow > q90Threshold * 0.85;

  // Tile layer URL definitions for Leaflet fallback (OpenStreetMap & ESRI)
  const tileUrls = {
    terrain: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    streets: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  };

  // 1. Initialize Map: Google Maps JavaScript API (Primary) with Leaflet Fallback
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Check if Google Maps is loaded and ready
    if (typeof google !== 'undefined' && google.maps && google.maps.Map) {
      if (!googleMapRef.current) {
        try {
          const mapType =
            mapStyle === 'satellite'
              ? google.maps.MapTypeId.HYBRID
              : mapStyle === 'streets'
              ? google.maps.MapTypeId.ROADMAP
              : google.maps.MapTypeId.TERRAIN;

          const gMap = new google.maps.Map(mapContainerRef.current, {
            center: { lat: 38.5, lng: -96.5 },
            zoom: 4,
            mapTypeId: mapType,
            disableDefaultUI: true,
            gestureHandling: 'greedy',
            zoomControl: false,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false,
          });

          // Handle arbitrary click for Haversine discovery on Google Maps
          gMap.addListener('click', (e: any) => {
            const clickLat = e.latLng.lat();
            const clickLng = e.latLng.lng();

            let nearest: ApiStationItem | null = null;
            let minDist = Infinity;
            stations.forEach((st) => {
              const dist = calculateHaversineMiles(clickLat, clickLng, st.latitude, st.longitude);
              if (dist < minDist) {
                minDist = dist;
                nearest = st;
              }
            });

            if (nearest) {
              setNearestDiscovery({
                station: nearest,
                distanceMiles: minDist,
                clickLat,
                clickLng,
              });

              if (googleClickMarkerRef.current) {
                googleClickMarkerRef.current.setMap(null);
              }

              const clickPinSvg = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
                <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" fill="#006297" stroke="#ffffff" stroke-width="2.5"/>
                  <circle cx="12" cy="12" r="4" fill="#ffffff"/>
                </svg>
              `)}`;

              googleClickMarkerRef.current = new google.maps.Marker({
                position: { lat: clickLat, lng: clickLng },
                map: gMap,
                icon: {
                  url: clickPinSvg,
                  scaledSize: new google.maps.Size(22, 22),
                  anchor: new google.maps.Point(11, 11),
                },
              });
            }
          });

          googleMapRef.current = gMap;
          setEngineMode('google');
          return;
        } catch (e) {
          console.warn('Google Maps initialization failed, proceeding with Leaflet fallback:', e);
        }
      }
    }

    // Leaflet Fallback Engine
    if (typeof L !== 'undefined' && !leafletMapRef.current && !googleMapRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [38.5, -96.5],
        zoom: 4,
        zoomControl: false,
        attributionControl: false,
      });

      const baseTile = L.tileLayer(tileUrls[mapStyle], {
        maxZoom: 18,
        subdomains: 'abcd',
      }).addTo(map);
      tileLayerRef.current = baseTile;

      L.control.attribution({ position: 'bottomright', prefix: false })
        .addAttribution('&copy; OpenStreetMap &copy; CARTO &copy; USGS')
        .addTo(map);

      stationMarkersGroupRef.current = L.layerGroup().addTo(map);
      shelterMarkersGroupRef.current = L.layerGroup().addTo(map);
      sosMarkersGroupRef.current = L.layerGroup().addTo(map);

      map.on('click', (e: any) => {
        const clickLat = e.latlng.lat;
        const clickLng = e.latlng.lng;

        let nearest: ApiStationItem | null = null;
        let minDist = Infinity;
        stations.forEach((st) => {
          const dist = calculateHaversineMiles(clickLat, clickLng, st.latitude, st.longitude);
          if (dist < minDist) {
            minDist = dist;
            nearest = st;
          }
        });

        if (nearest) {
          setNearestDiscovery({
            station: nearest,
            distanceMiles: minDist,
            clickLat,
            clickLng,
          });

          if (clickMarkerRef.current) {
            map.removeLayer(clickMarkerRef.current);
          }
          const clickIcon = L.divIcon({
            className: 'click-pulse-pin',
            html: `
              <div style="position:relative; width:24px; height:24px; display:flex; align-items:center; justify-content:center;">
                <span style="position:absolute; width:24px; height:24px; border-radius:50%; background:rgba(0,98,151,0.4); animation:ping 1s cubic-bezier(0,0,0.2,1) infinite;"></span>
                <span style="width:10px; height:10px; border-radius:50%; background:#006297; border:2px solid #ffffff; box-shadow:0 2px 6px rgba(0,0,0,0.3);"></span>
              </div>
            `,
            iconSize: [24, 24],
            iconAnchor: [12, 12],
          });
          clickMarkerRef.current = L.marker([clickLat, clickLng], { icon: clickIcon }).addTo(map);
        }
      });

      leafletMapRef.current = map;
      setEngineMode('leaflet');
    }
  }, [mapStyle, stations]);

  // 2. Update Map Style (Terrain / Satellite / Streets)
  const handleSetMapStyle = (newStyle: 'terrain' | 'satellite' | 'streets') => {
    setMapStyle(newStyle);

    if (googleMapRef.current && typeof google !== 'undefined' && google.maps) {
      if (newStyle === 'satellite') {
        googleMapRef.current.setMapTypeId(google.maps.MapTypeId.HYBRID);
      } else if (newStyle === 'streets') {
        googleMapRef.current.setMapTypeId(google.maps.MapTypeId.ROADMAP);
      } else {
        googleMapRef.current.setMapTypeId(google.maps.MapTypeId.TERRAIN);
      }
    } else if (leafletMapRef.current && tileLayerRef.current) {
      leafletMapRef.current.removeLayer(tileLayerRef.current);
      const newTile = L.tileLayer(tileUrls[newStyle], {
        maxZoom: 18,
        subdomains: 'abcd',
      }).addTo(leafletMapRef.current);
      tileLayerRef.current = newTile;
    }
  };

  // 3. Render Markers for Google Maps & Leaflet
  useEffect(() => {
    // A. Render on Google Maps
    if (googleMapRef.current && typeof google !== 'undefined' && google.maps) {
      // Clear previous markers
      googleMarkersRef.current.forEach((m) => m.setMap(null));
      googleMarkersRef.current = [];
      googleShelterMarkersRef.current.forEach((m) => m.setMap(null));
      googleShelterMarkersRef.current = [];
      googleSosMarkersRef.current.forEach((m) => m.setMap(null));
      googleSosMarkersRef.current = [];

      // Render 38 USGS Streamgauge Stations with parameter-specific risk colors
      if (activeLayers.stations) {
        stations.forEach((st) => {
          const isSelected = selectedStationId === st.station_id && !selectedSafeSpotId && !selectedSosId;
          // Data-tier color coding
          let pinColor = '#006297'; // Standard baseflow blue
          if (st.station_id === '07010000' || st.station_id === '08158000') {
            pinColor = '#DC2626'; // High surge / crest exceedance
          } else if (st.station_id === '11447650') {
            pinColor = '#D5A83E'; // Historical Record Only (data ended 2015)
          } else if (st.station_id === '02087500' || st.station_id === '01646500') {
            pinColor = '#E58C47'; // Elevated runoff watch
          } else if (st.has_2022_2023_validation) {
            pinColor = '#287BB5'; // LORSO validated streamgauge
          } else {
            pinColor = '#51B9CC'; // Labelled discharge only
          }
          if (isSelected) pinColor = '#004B75';

          const size = isSelected ? 32 : 22;

          const stationSvg = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
            <svg width="${size}" height="${size}" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg">
              <circle cx="14" cy="14" r="12" fill="${pinColor}" stroke="#ffffff" stroke-width="2.5" />
              <path d="M7 14h3l2-5 4 10 2-5h3" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          `)}`;

          const marker = new google.maps.Marker({
            position: { lat: st.latitude, lng: st.longitude },
            map: googleMapRef.current,
            title: `${st.river_name || st.station_name} (ID: ${st.station_id})`,
            zIndex: isSelected ? 100 : 10,
            icon: {
              url: stationSvg,
              scaledSize: new google.maps.Size(size, size),
              anchor: new google.maps.Point(size / 2, size / 2),
            },
          });

          marker.addListener('click', () => {
            setSelectedStationId(st.station_id);
            setSelectedSafeSpotId(null);
            setSelectedSosId(null);
            setSidePanelTab('historic');
            setNearestDiscovery(null);
            googleMapRef.current.panTo({ lat: st.latitude, lng: st.longitude });
          });

          googleMarkersRef.current.push(marker);
        });
      }

      // Render 8 Certified High-Ground Evacuation Shelters (Emerald Green)
      if (activeLayers.shelters) {
        SAFE_SPOTS.forEach((shelter) => {
          const isShelterSelected = selectedSafeSpotId === shelter.id;
          const size = isShelterSelected ? 34 : 26;

          const shelterSvg = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
            <svg width="${size}" height="${size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" fill="#10B981" stroke="#ffffff" stroke-width="2.5"/>
              <path d="M16 8l5 2v5c0 4-2.5 7-5 8-2.5-1-5-4-5-8v-5l5-2z" fill="#047857" stroke="#ffffff" stroke-width="1.2"/>
            </svg>
          `)}`;

          const marker = new google.maps.Marker({
            position: { lat: shelter.latitude, lng: shelter.longitude },
            map: googleMapRef.current,
            title: `${language === 'HI' ? shelter.name_hi : shelter.name} (+${shelter.elevation_freeboard_ft} ft freeboard)`,
            zIndex: isShelterSelected ? 120 : 20,
            icon: {
              url: shelterSvg,
              scaledSize: new google.maps.Size(size, size),
              anchor: new google.maps.Point(size / 2, size / 2),
            },
          });

          marker.addListener('click', () => {
            setSelectedSafeSpotId(shelter.id);
            setSelectedSosId(null);
            setNearestDiscovery(null);
            googleMapRef.current.panTo({ lat: shelter.latitude, lng: shelter.longitude });
          });

          googleShelterMarkersRef.current.push(marker);
        });
      }

      // Render Citizen SOS Signals on Google Maps (Glowing Red/Coral Beacon)
      if (activeLayers.sos) {
        CITIZEN_SOS_SIGNALS.forEach((sos) => {
          const isSosSelected = selectedSosId === sos.id;
          const size = isSosSelected ? 32 : 24;

          const sosSvg = `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
            <svg width="${size}" height="${size}" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg">
              <circle cx="14" cy="14" r="12" fill="#EF4444" stroke="#ffffff" stroke-width="2.5"/>
              <circle cx="14" cy="14" r="6" fill="#FEE2E2"/>
              <text x="14" y="18" font-size="12" font-weight="900" fill="#EF4444" text-anchor="middle" font-family="sans-serif">!</text>
            </svg>
          `)}`;

          const marker = new google.maps.Marker({
            position: { lat: sos.lat, lng: sos.lng },
            map: googleMapRef.current,
            title: `Citizen SOS: ${sos.title} (Water Depth: ${sos.depth}, ${sos.time})`,
            zIndex: isSosSelected ? 150 : 30,
            icon: {
              url: sosSvg,
              scaledSize: new google.maps.Size(size, size),
              anchor: new google.maps.Point(size / 2, size / 2),
            },
          });

          marker.addListener('click', () => {
            setSelectedSosId(sos.id);
            setSelectedSafeSpotId(null);
            setNearestDiscovery(null);
            googleMapRef.current.panTo({ lat: sos.lat, lng: sos.lng });
          });

          googleSosMarkersRef.current.push(marker);
        });
      }
      return;
    }

    // B. Render on Leaflet (Fallback)
    if (!leafletMapRef.current || !stationMarkersGroupRef.current || !shelterMarkersGroupRef.current) return;

    stationMarkersGroupRef.current.clearLayers();
    shelterMarkersGroupRef.current.clearLayers();
    if (sosMarkersGroupRef.current) sosMarkersGroupRef.current.clearLayers();

    if (activeLayers.stations) {
      stations.forEach((st) => {
        const isSelected = selectedStationId === st.station_id && !selectedSafeSpotId && !selectedSosId;
        let pinColor = '#006297';
        if (st.station_id === '07010000' || st.station_id === '08158000') {
          pinColor = '#DC2626';
        } else if (st.station_id === '11447650') {
          pinColor = '#D5A83E'; // Historical Record Only (data ended 2015)
        } else if (st.station_id === '02087500' || st.station_id === '01646500') {
          pinColor = '#E58C47';
        } else if (st.has_2022_2023_validation) {
          pinColor = '#287BB5';
        } else {
          pinColor = '#51B9CC';
        }
        if (isSelected) pinColor = '#004B75';

        const ringColor = isSelected ? 'rgba(0,98,151,0.35)' : 'rgba(40,123,181,0.25)';
        const size = isSelected ? 32 : 24;

        const iconHtml = `
          <div style="position:relative; width:${size}px; height:${size}px; display:flex; align-items:center; justify-content:center; cursor:pointer;">
            ${isSelected ? `<span style="position:absolute; width:${size + 14}px; height:${size + 14}px; border-radius:50%; background:${ringColor}; animation:pulse 1.8s infinite;"></span>` : ''}
            <div style="width:${size}px; height:${size}px; border-radius:50%; background:${pinColor}; border:2px solid #ffffff; box-shadow:0 3px 10px rgba(0,40,75,0.3); display:flex; align-items:center; justify-content:center; color:#ffffff; font-weight:bold; font-size:11px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
            </div>
          </div>
        `;

        const icon = L.divIcon({
          className: `station-pin-${st.station_id}`,
          html: iconHtml,
          iconSize: [size, size],
          iconAnchor: [size / 2, size / 2],
        });

        const marker = L.marker([st.latitude, st.longitude], { icon });
        marker.on('click', (e: any) => {
          L.DomEvent.stopPropagation(e);
          setSelectedStationId(st.station_id);
          setSelectedSafeSpotId(null);
          setSelectedSosId(null);
          setSidePanelTab('historic');
          setNearestDiscovery(null);
          if (leafletMapRef.current) {
            leafletMapRef.current.flyTo([st.latitude, st.longitude], 9, { duration: 0.8 });
          }
        });
        marker.bindTooltip(
          `<div style="font-family:Inter,sans-serif; font-size:11px; padding:2px 4px;">
            <div style="font-weight:700; color:#17354D;">${st.river_name || st.station_name}</div>
            <div style="color:#6688A1; font-family:monospace; font-size:10px;">ID: ${st.station_id} • ${st.drainage_area_sqmi?.toLocaleString() || 'Verified'} mi²</div>
          </div>`,
          { direction: 'top', offset: [0, -size / 2] }
        );
        stationMarkersGroupRef.current.addLayer(marker);
      });
    }

    if (activeLayers.shelters) {
      SAFE_SPOTS.forEach((shelter) => {
        const isShelterSelected = selectedSafeSpotId === shelter.id;
        const size = isShelterSelected ? 34 : 26;

        const shelterHtml = `
          <div style="position:relative; width:${size}px; height:${size}px; display:flex; align-items:center; justify-content:center; cursor:pointer;">
            <span style="position:absolute; width:${size + 12}px; height:${size + 12}px; border-radius:50%; background:rgba(16,185,129,0.35); animation:pulse 2s infinite;"></span>
            <div style="width:${size}px; height:${size}px; border-radius:50%; background:#10B981; border:2.5px solid #ffffff; box-shadow:0 3px 12px rgba(16,185,129,0.4); display:flex; align-items:center; justify-content:center; color:#ffffff;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
              </svg>
            </div>
          </div>
        `;

        const icon = L.divIcon({
          className: `shelter-pin-${shelter.id}`,
          html: shelterHtml,
          iconSize: [size, size],
          iconAnchor: [size / 2, size / 2],
        });

        const marker = L.marker([shelter.latitude, shelter.longitude], { icon });
        marker.on('click', (e: any) => {
          L.DomEvent.stopPropagation(e);
          setSelectedSafeSpotId(shelter.id);
          setSelectedSosId(null);
          setNearestDiscovery(null);
          if (leafletMapRef.current) {
            leafletMapRef.current.flyTo([shelter.latitude, shelter.longitude], 10, { duration: 0.8 });
          }
        });
        marker.bindTooltip(
          `<div style="font-family:Inter,sans-serif; font-size:11px; padding:2px 4px;">
            <div style="font-weight:700; color:#10B981;">${language === 'HI' ? shelter.name_hi : shelter.name}</div>
            <div style="color:#17354D; font-size:10px;">+${shelter.elevation_freeboard_ft} ft Freeboard • ${shelter.capacity.toLocaleString()} cap</div>
          </div>`,
          { direction: 'top', offset: [0, -size / 2] }
        );
        shelterMarkersGroupRef.current.addLayer(marker);
      });
    }

    // Citizen SOS Markers on Leaflet
    if (activeLayers.sos && sosMarkersGroupRef.current) {
      CITIZEN_SOS_SIGNALS.forEach((sos) => {
        const isSosSelected = selectedSosId === sos.id;
        const size = isSosSelected ? 32 : 24;

        const sosHtml = `
          <div style="position:relative; width:${size}px; height:${size}px; display:flex; align-items:center; justify-content:center; cursor:pointer;">
            <span style="position:absolute; width:${size + 14}px; height:${size + 14}px; border-radius:50%; background:rgba(239,68,68,0.45); animation:pulse 1.4s infinite;"></span>
            <div style="width:${size}px; height:${size}px; border-radius:50%; background:#EF4444; border:2.5px solid #ffffff; box-shadow:0 3px 12px rgba(239,68,68,0.5); display:flex; align-items:center; justify-content:center; color:#ffffff; font-weight:900; font-size:12px;">
              !
            </div>
          </div>
        `;

        const icon = L.divIcon({
          className: `sos-pin-${sos.id}`,
          html: sosHtml,
          iconSize: [size, size],
          iconAnchor: [size / 2, size / 2],
        });

        const marker = L.marker([sos.lat, sos.lng], { icon });
        marker.on('click', (e: any) => {
          L.DomEvent.stopPropagation(e);
          setSelectedSosId(sos.id);
          setSelectedSafeSpotId(null);
          setNearestDiscovery(null);
          if (leafletMapRef.current) {
            leafletMapRef.current.flyTo([sos.lat, sos.lng], 10, { duration: 0.8 });
          }
        });
        marker.bindTooltip(
          `<div style="font-family:Inter,sans-serif; font-size:11px; padding:2px 4px;">
            <div style="font-weight:700; color:#EF4444;">Citizen SOS: ${sos.title}</div>
            <div style="color:#17354D; font-size:10px;">Depth: ${sos.depth} • ${sos.time}</div>
          </div>`,
          { direction: 'top', offset: [0, -size / 2] }
        );
        sosMarkersGroupRef.current.addLayer(marker);
      });
    }
  }, [stations, selectedStationId, selectedSafeSpotId, selectedSosId, activeLayers, language]);

  // 4. Map Zoom & Bounds Controls
  const handleZoomIn = () => {
    if (googleMapRef.current) {
      googleMapRef.current.setZoom((googleMapRef.current.getZoom() || 4) + 1);
    } else if (leafletMapRef.current) {
      leafletMapRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (googleMapRef.current) {
      googleMapRef.current.setZoom((googleMapRef.current.getZoom() || 4) - 1);
    } else if (leafletMapRef.current) {
      leafletMapRef.current.zoomOut();
    }
  };

  const handleFitBoundsAllStations = () => {
    if (googleMapRef.current && stations.length > 0 && typeof google !== 'undefined' && google.maps) {
      const bounds = new google.maps.LatLngBounds();
      stations.forEach((s) => bounds.extend({ lat: s.latitude, lng: s.longitude }));
      googleMapRef.current.fitBounds(bounds, { top: 50, right: 50, bottom: 50, left: 50 });
    } else if (leafletMapRef.current && stations.length > 0) {
      const bounds = L.latLngBounds(stations.map((s) => [s.latitude, s.longitude]));
      leafletMapRef.current.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
    }
  };

  const handleCenterActiveStation = () => {
    const target = stations.find((s) => s.station_id === selectedStationId);
    if (target) {
      if (googleMapRef.current) {
        googleMapRef.current.panTo({ lat: target.latitude, lng: target.longitude });
        googleMapRef.current.setZoom(9);
      } else if (leafletMapRef.current) {
        leafletMapRef.current.flyTo([target.latitude, target.longitude], 9, { duration: 0.8 });
      }
    }
  };

  // Station search jump handler
  const handleSelectSearchedStation = (stationId: string) => {
    setSelectedStationId(stationId);
    setSelectedSafeSpotId(null);
    setSidePanelTab('historic');
    setStationSearch('');
    const target = stations.find((s) => s.station_id === stationId);
    if (target) {
      if (googleMapRef.current) {
        googleMapRef.current.panTo({ lat: target.latitude, lng: target.longitude });
        googleMapRef.current.setZoom(9);
      } else if (leafletMapRef.current) {
        leafletMapRef.current.flyTo([target.latitude, target.longitude], 9, { duration: 0.8 });
      }
    }
  };

  // Filtered station search results
  const filteredSearchStations = useMemo(() => {
    if (!stationSearch.trim()) return [];
    const q = stationSearch.toLowerCase();
    return stations.filter(
      (s) =>
        s.station_id.includes(q) ||
        s.station_name.toLowerCase().includes(q) ||
        s.river_name.toLowerCase().includes(q) ||
        (s.river_system && s.river_system.toLowerCase().includes(q))
    ).slice(0, 6);
  }, [stationSearch, stations]);

  // Render Mini Hydrograph Sparkline / Curve
  const validHydroPoints: ApiHydrographPoint[] = (hydroData?.data || []).filter(
    (p: ApiHydrographPoint) => p.actual_discharge_cfs !== null && p.actual_discharge_cfs !== undefined
  );

  const renderHydroChart = () => {
    if (validHydroPoints.length >= 3) {
      const actualVals = validHydroPoints.map((p) => p.actual_discharge_cfs as number);
      const predVals = validHydroPoints
        .filter((p) => p.predicted_discharge_cfs != null)
        .map((p) => p.predicted_discharge_cfs as number);

      const minV = Math.min(...actualVals, ...predVals, 0);
      const maxV = Math.max(...actualVals, ...predVals, q90Threshold * 1.1, minV + 1);

      const makePath = (vals: number[]) => {
        return vals
          .map((v, i) => {
            const x = (i / (vals.length - 1)) * 320;
            const y = 130 - ((v - minV) / (maxV - minV)) * 110;
            return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)},${y.toFixed(1)}`;
          })
          .join(' ');
      };

      const q90Y = 130 - ((q90Threshold - minV) / (maxV - minV)) * 110;

      return (
        <svg className="w-full h-36" viewBox="0 0 320 140" preserveAspectRatio="none">
          {q90Y >= 0 && q90Y <= 140 && (
            <rect x="0" y="0" width="320" height={Math.max(0, q90Y)} fill="#D95F62" fillOpacity="0.06" />
          )}

          {q90Y >= 0 && q90Y <= 140 && (
            <g>
              <line x1="0" x2="320" y1={q90Y} y2={q90Y} stroke="#D95F62" strokeWidth="1.5" strokeDasharray="4 3" />
              <text x="315" y={Math.max(12, q90Y - 4)} fill="#D95F62" fontSize="9" fontWeight="bold" textAnchor="end">
                q90 Flood ({formatCfs(q90Threshold)})
              </text>
            </g>
          )}

          {predVals.length > 0 && (
            <path d={makePath(predVals)} fill="none" stroke="#E58C47" strokeWidth="2" strokeDasharray="3 2" />
          )}

          <path d={makePath(actualVals)} fill="none" stroke="#006297" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
      );
    }

    return (
      <svg className="w-full h-36" viewBox="0 0 320 140" preserveAspectRatio="none">
        <line x1="0" x2="320" y1="40" y2="40" stroke="#D95F62" strokeWidth="1.5" strokeDasharray="4 3" />
        <text x="315" y="34" fill="#D95F62" fontSize="9" fontWeight="bold" textAnchor="end">
          q90 Flood ({formatCfs(q90Threshold)})
        </text>
        <path d="M0,110 Q80,105 160,75 T320,45" fill="none" stroke="#006297" strokeWidth="2.5" strokeLinecap="round" />
      </svg>
    );
  };

  return (
    <div className="space-y-4 pb-14">
      {/* Truth Disclaimer Banner */}
      <TruthBanner
        type="demo"
        title="GOOGLE MAPS RIVER INTELLIGENCE ENGINE — VERIFIED USGS HYDROMETRY"
        description="Streamgauge locations, coordinates, drainage basins, and flow percentiles reflect 38 verified USGS stations in the PRAVAHA dataset. Powered by the official Google Maps JavaScript API."
      />

      {stationsError && (
        <ApiErrorBanner
          message={`Failed to connect to FastAPI station service (${stationsError}). Operating on verified offline catalogue.`}
          onRetry={refetchStations}
        />
      )}

      {/* TOP CONTROL STRIP: Viewport Basin Metadata, Mode Switcher, & Layer Filters */}
      <div className="p-4 sm:p-5 rounded-3xl bg-white/90 backdrop-blur-md border border-[#D8E8F0] shadow-sm flex flex-col gap-3">
        <div className="w-full flex flex-wrap items-center justify-between gap-3">
          {/* Active Basin Viewport Plaque */}
          <div className="flex items-center gap-3 px-3 py-1.5 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0]">
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-[#006297]" />
              <div>
                <div className="text-[10px] font-bold tracking-wider uppercase text-[#006297] flex items-center gap-1.5">
                  <span>{t('map.viewport')}</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#40A77A] animate-pulse" />
                  <span className="text-[9px] text-[#2D7857] font-semibold lowercase">
                    ({engineMode === 'google' ? 'google maps api' : 'gis fallback'})
                  </span>
                </div>
                <div className="text-xs font-mono font-bold text-[#17354D]">
                  {selectedDetail?.coordinates?.latitude
                    ? `${selectedDetail.coordinates.latitude.toFixed(4)}° N, ${Math.abs(
                        selectedDetail.coordinates.longitude
                      ).toFixed(4)}° W`
                    : currentStationSummary
                    ? `${currentStationSummary.latitude.toFixed(4)}° N, ${Math.abs(
                        currentStationSummary.longitude
                      ).toFixed(4)}° W`
                    : 'Loading coordinates...'}
                  <span className="font-normal text-[#6688A1] ml-1">
                    ({selectedDetail?.river_system || currentStationSummary?.river_system || 'Verified System'})
                  </span>
                </div>
              </div>
            </div>
            <div className="h-6 w-px bg-[#D8E8F0]" />
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-[#36556C]">
              <span className="w-2 h-2 rounded-full bg-[#40A77A]" />
              <span className="font-semibold">
                {selectedDetail?.drainage_area_sqmi != null
                  ? `${selectedDetail.drainage_area_sqmi.toLocaleString()} mi² Drainage`
                  : currentStationSummary?.drainage_area_sqmi != null
                  ? `${currentStationSummary.drainage_area_sqmi.toLocaleString()} mi² Drainage`
                  : t('map.drainage')}
              </span>
            </div>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-2">
            <div className="flex items-center p-1 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0] shadow-sm">
              <button
                onClick={() => {
                  setMapMode('flood');
                  setActiveLayers((prev) => ({
                    ...prev,
                    stations: true,
                    radar: true,
                    vectors: true,
                    polygons: true,
                    shelters: true,
                    sos: true,
                  }));
                  setSelectedSafeSpotId(null);
                  setSelectedSosId(null);
                  if (!selectedStationId) setSelectedStationId('11447650');
                  setSidePanelTab('historic');
                  if (googleMapRef.current) {
                    googleMapRef.current.panTo({ lat: 38.4557, lng: -121.5016 });
                    googleMapRef.current.setZoom(6);
                  } else if (leafletMapRef.current) {
                    leafletMapRef.current.setView([38.4557, -121.5016], 6);
                  }
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
                  mapMode === 'flood'
                    ? 'bg-[#006297] text-white shadow-sm'
                    : 'text-[#36556C] hover:text-[#006297]'
                }`}
              >
                <Waves className="w-3.5 h-3.5" />
                <span>{t('map.floodMode')}</span>
              </button>
              <button
                onClick={() => {
                  setMapMode('relief');
                  setActiveLayers((prev) => ({
                    ...prev,
                    shelters: true,
                    sos: true,
                    stations: true,
                    radar: false,
                    polygons: false,
                  }));
                  const firstShelter = SAFE_SPOTS[0];
                  setSelectedSafeSpotId(firstShelter.id);
                  setSelectedSosId(null);
                  if (googleMapRef.current) {
                    googleMapRef.current.panTo({ lat: firstShelter.latitude, lng: firstShelter.longitude });
                    googleMapRef.current.setZoom(7);
                  } else if (leafletMapRef.current) {
                    leafletMapRef.current.setView([firstShelter.latitude, firstShelter.longitude], 7);
                  }
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
                  mapMode === 'relief'
                    ? 'bg-[#006297] text-white shadow-sm'
                    : 'text-[#36556C] hover:text-[#006297]'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>{t('map.reliefMode')}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Layer Filter Pills Strip */}
        <div className="w-full flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5">
          <button
            onClick={() => toggleLayer('stations')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border flex items-center gap-1.5 ${
              activeLayers.stations
                ? 'bg-[#006297] text-white border-[#006297] shadow-sm'
                : 'bg-white/80 text-[#36556C] border-[#D8E8F0]'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>{t('map.layer.stations')}</span>
          </button>
          <button
            onClick={() => toggleLayer('shelters')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border flex items-center gap-1.5 ${
              activeLayers.shelters
                ? 'bg-[#2D7857] text-white border-[#2D7857] shadow-sm'
                : 'bg-white/80 text-[#36556C] border-[#D8E8F0]'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" />
            <span>{t('map.layer.shelters')}</span>
          </button>
          <button
            onClick={() => toggleLayer('radar')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
              activeLayers.radar
                ? 'bg-[#287BB5] text-white border-[#287BB5] shadow-sm'
                : 'bg-white/80 text-[#36556C] border-[#D8E8F0]'
            }`}
          >
            {t('map.layer.radar')}
          </button>
          <button
            onClick={() => toggleLayer('vectors')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
              activeLayers.vectors
                ? 'bg-[#287BB5] text-white border-[#287BB5] shadow-sm'
                : 'bg-white/80 text-[#36556C] border-[#D8E8F0]'
            }`}
          >
            {t('map.layer.vectors')}
          </button>
          <button
            onClick={() => toggleLayer('polygons')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
              activeLayers.polygons
                ? 'bg-[#287BB5] text-white border-[#287BB5] shadow-sm'
                : 'bg-white/80 text-[#36556C] border-[#D8E8F0]'
            }`}
          >
            {t('map.layer.polygons')}
          </button>
          <button
            onClick={() => toggleLayer('sos')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all border ${
              activeLayers.sos
                ? 'bg-[#D95F62] text-white border-[#D95F62] shadow-sm'
                : 'bg-white/80 text-[#36556C] border-[#D8E8F0]'
            }`}
          >
            {t('map.layer.sos')}
          </button>
        </div>
      </div>

      {/* TWO-COLUMN DOCK: GOOGLE MAPS INTERACTIVE VIEWPORT (COL 8) + DEDICATED SIDE PANEL AWAY FROM MAP (COL 4) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* LEFT COLUMN: 100% UNOBSTRUCTED GOOGLE MAPS CANVAS */}
        <div className="lg:col-span-8 flex flex-col gap-3">
          <div className="relative w-full h-[640px] rounded-3xl overflow-hidden border border-[#D8E8F0] shadow-ocean select-none">
            {/* Real Map Viewport Container */}
            <div
              id="pravaha-map-viewport"
              ref={mapContainerRef}
              className="absolute inset-0 w-full h-full z-0"
            />

            {/* Top-Left Controls: Map Style Switcher (Terrain / Satellite / Streets) */}
            <div
              className={`absolute top-4 left-4 z-20 flex items-center p-1 rounded-2xl transition-all shadow-xl backdrop-blur-xl ${
                mapStyle === 'satellite'
                  ? 'bg-[#0B1E2E]/92 border border-white/30 shadow-[0_8px_32px_rgba(0,0,0,0.5)]'
                  : 'bg-white/95 border border-[#D8E8F0] shadow-ambient'
              }`}
            >
              <button
                type="button"
                onClick={() => handleSetMapStyle('terrain')}
                className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all ${
                  mapStyle === 'terrain'
                    ? 'bg-[#006297] text-white shadow-marine'
                    : mapStyle === 'satellite'
                    ? 'text-white/90 hover:text-white hover:bg-white/20'
                    : 'text-[#17354D] hover:text-[#006297] hover:bg-[#EFF6FA]'
                }`}
              >
                {t('map.style.terrain')}
              </button>
              <button
                type="button"
                onClick={() => handleSetMapStyle('satellite')}
                className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all ${
                  mapStyle === 'satellite'
                    ? 'bg-[#0088CC] text-white shadow-marine ring-1 ring-white/50'
                    : 'text-[#17354D] hover:text-[#006297] hover:bg-[#EFF6FA]'
                }`}
              >
                {t('map.style.satellite')}
              </button>
              <button
                type="button"
                onClick={() => handleSetMapStyle('streets')}
                className={`px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all ${
                  mapStyle === 'streets'
                    ? 'bg-[#006297] text-white shadow-marine'
                    : mapStyle === 'satellite'
                    ? 'text-white/90 hover:text-white hover:bg-white/20'
                    : 'text-[#17354D] hover:text-[#006297] hover:bg-[#EFF6FA]'
                }`}
              >
                {t('map.style.streets')}
              </button>
            </div>

            {/* Top-Right Controls: Instant Station Search Jump & Fit Bounds */}
            <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
              <div className="relative w-48 sm:w-64">
                <Search
                  className={`absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 pointer-events-none transition-colors ${
                    mapStyle === 'satellite' ? 'text-white/70' : 'text-[#6688A1]'
                  }`}
                />
                <input
                  type="text"
                  value={stationSearch}
                  onChange={(e) => setStationSearch(e.target.value)}
                  placeholder={t('map.searchPlaceholder')}
                  className={`w-full h-8.5 pl-8 pr-7 rounded-xl text-xs transition-all shadow-md focus:outline-none ${
                    mapStyle === 'satellite'
                      ? 'bg-[#0B1E2E]/92 text-white placeholder:text-white/60 border border-white/30 backdrop-blur-xl focus:bg-[#0B1E2E] focus:border-[#0088CC]'
                      : 'bg-white/95 text-[#17354D] placeholder:text-[#6688A1] border border-[#D8E8F0] backdrop-blur-md focus:bg-white focus:border-[#006297]'
                  }`}
                />
                {stationSearch && (
                  <button
                    onClick={() => setStationSearch('')}
                    className={`absolute right-2 top-1/2 -translate-y-1/2 transition-colors ${
                      mapStyle === 'satellite' ? 'text-white/70 hover:text-white' : 'text-[#6688A1] hover:text-[#17354D]'
                    }`}
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}

                {/* Instant Search Suggestions */}
                {filteredSearchStations.length > 0 && (
                  <div
                    className={`absolute top-10 left-0 right-0 rounded-2xl backdrop-blur-xl border shadow-2xl p-1.5 z-50 space-y-1 ${
                      mapStyle === 'satellite'
                        ? 'bg-[#0B1E2E]/98 border-white/25 text-white'
                        : 'bg-white/98 border-[#D8E8F0] text-[#17354D]'
                    }`}
                  >
                    {filteredSearchStations.map((st) => (
                      <div
                        key={st.station_id}
                        onClick={() => handleSelectSearchedStation(st.station_id)}
                        className={`p-2 rounded-xl cursor-pointer transition-colors flex items-center justify-between text-xs ${
                          mapStyle === 'satellite'
                            ? 'hover:bg-white/10 text-white'
                            : 'hover:bg-[#EFF6FA] text-[#17354D]'
                        }`}
                      >
                        <div>
                          <div className="font-bold">{st.river_name || st.station_name}</div>
                          <div
                            className={`text-[10px] ${
                              mapStyle === 'satellite' ? 'text-white/60' : 'text-[#6688A1]'
                            }`}
                          >
                            ID: {st.station_id}
                          </div>
                        </div>
                        <ArrowRight
                          className={`w-3.5 h-3.5 ${
                            mapStyle === 'satellite' ? 'text-[#0088CC]' : 'text-[#006297]'
                          }`}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Fit All 38 Stations Button */}
              <button
                type="button"
                onClick={handleFitBoundsAllStations}
                className={`p-2 rounded-xl backdrop-blur-md transition-all shadow-md ${
                  mapStyle === 'satellite'
                    ? 'bg-[#0B1E2E]/92 text-white border border-white/30 hover:bg-[#0088CC]'
                    : 'bg-white/95 text-[#006297] border border-[#D8E8F0] hover:bg-white'
                }`}
                title={t('map.fitBounds')}
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            </div>

            {/* Bottom-Right Controls: Google Maps Zoom [+] [-] and [Center] */}
            <div className="absolute bottom-5 right-4 z-20 flex flex-col items-end gap-2">
              <div
                className={`flex flex-col rounded-2xl backdrop-blur-md overflow-hidden shadow-ocean transition-all ${
                  mapStyle === 'satellite'
                    ? 'bg-[#0B1E2E]/92 border border-white/30'
                    : 'bg-white/95 border border-[#D8E8F0]'
                }`}
              >
                <button
                  type="button"
                  onClick={handleZoomIn}
                  className={`p-2.5 transition-colors border-b ${
                    mapStyle === 'satellite'
                      ? 'hover:bg-white/15 text-white border-white/20'
                      : 'hover:bg-[#EFF6FA] text-[#006297] border-[#D8E8F0]'
                  }`}
                  title="Zoom In (+)"
                >
                  <Plus className="w-4 h-4 font-bold" />
                </button>
                <button
                  type="button"
                  onClick={handleZoomOut}
                  className={`p-2.5 transition-colors ${
                    mapStyle === 'satellite'
                      ? 'hover:bg-white/15 text-white'
                      : 'hover:bg-[#EFF6FA] text-[#006297]'
                  }`}
                  title="Zoom Out (−)"
                >
                  <Minus className="w-4 h-4 font-bold" />
                </button>
              </div>

              {/* Center on Active Station */}
              <button
                type="button"
                onClick={handleCenterActiveStation}
                className={`p-2.5 rounded-xl backdrop-blur-md transition-all shadow-md ${
                  mapStyle === 'satellite'
                    ? 'bg-[#0B1E2E]/92 text-white border border-white/30 hover:bg-[#0088CC]'
                    : 'bg-white/95 text-[#006297] border border-[#D8E8F0] hover:bg-white'
                }`}
                title="Center on Active Station"
              >
                <Crosshair className="w-4 h-4" />
              </button>
            </div>

            {/* Bottom-Left Controls: Nearest Station Discovery Notification Chip */}
            <div className="absolute bottom-5 left-4 z-20 flex flex-col gap-1.5 max-w-sm">
              {nearestDiscovery ? (
                <div
                  className={`p-2.5 rounded-2xl backdrop-blur-xl border shadow-ocean flex items-center justify-between gap-3 text-xs animate-fade-in ${
                    mapStyle === 'satellite'
                      ? 'bg-[#0B1E2E]/95 border-white/30 text-white'
                      : 'bg-white/95 border-[#006297]/30 text-[#17354D]'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div
                      className={`text-[10px] uppercase font-bold flex items-center gap-1 ${
                        mapStyle === 'satellite' ? 'text-[#0088CC]' : 'text-[#006297]'
                      }`}
                    >
                      <MapPin className="w-3 h-3" />
                      {t('map.nearestStation')} ({nearestDiscovery.distanceMiles} mi away)
                    </div>
                    <div className="font-bold line-clamp-1">
                      {nearestDiscovery.station.river_name || nearestDiscovery.station.station_name}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedStationId(nearestDiscovery.station.station_id);
                      setSelectedSafeSpotId(null);
                      setSidePanelTab('historic');
                    }}
                    className="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-[#006297] text-white hover:bg-[#287BB5] transition-all whitespace-nowrap"
                  >
                    Select
                  </button>
                </div>
              ) : (
                <div
                  className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl backdrop-blur-md shadow-md text-[11px] transition-all ${
                    mapStyle === 'satellite'
                      ? 'bg-[#0B1E2E]/92 text-white/90 border border-white/30'
                      : 'bg-white/88 text-[#6688A1] border border-[#D8E8F0]'
                  }`}
                >
                  <MapPin
                    className={`w-3.5 h-3.5 ${
                      mapStyle === 'satellite' ? 'text-[#0088CC]' : 'text-[#006297]'
                    }`}
                  />
                  <span>{t('map.clickPrompt')}</span>
                </div>
              )}
            </div>
          </div>

          {/* Station Data-Tier Legend */}
          <div className="px-4 py-2.5 rounded-2xl bg-white/90 backdrop-blur-md border border-[#D8E8F0] shadow-sm flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[10px] font-semibold text-[#36556C]">
            <span className="font-bold text-[11px] text-[#17354D]">Station Data Tiers:</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-[#287BB5] border border-white shadow-sm inline-block" />33 LORSO Evaluated</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-[#51B9CC] border border-white shadow-sm inline-block" />4 Labelled Discharge Only</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-[#D5A83E] border border-white shadow-sm inline-block" />1 Historical Record Only (ended 2015)</span>
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-[#10B981] border border-white shadow-sm inline-block" />8 Demo Shelters</span>
          </div>

          {/* Temporal Progression Slider (Underneath the map canvas) */}
          <div className="p-4 rounded-3xl bg-white/90 backdrop-blur-md border border-[#D8E8F0] shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-[#006297]" />
              <span className="text-xs font-bold text-[#17354D]">Temporal Surge Progression</span>
              <span className="text-xs font-mono font-bold text-[#006297]">
                {timeStep === 0
                  ? 'T=0 (Present)'
                  : timeStep > 0
                  ? `T+${timeStep}h (Forecast)`
                  : `T${timeStep}h (History)`}
              </span>
            </div>

            <div className="flex-1 max-w-xl w-full flex items-center gap-3">
              <span className="text-[10px] font-mono text-[#6688A1]">-24h</span>
              <input
                type="range"
                min="-24"
                max="48"
                step="6"
                value={timeStep}
                onChange={(e) => setTimeStep(Number(e.target.value))}
                className="w-full h-2 bg-[#D8E8F0] rounded-lg appearance-none cursor-pointer accent-[#006297]"
              />
              <span className="text-[10px] font-mono text-[#6688A1]">+48h</span>
            </div>

            <div className="text-[11px] font-semibold text-[#6688A1]">
              {timeStep > 12 ? (
                <span className="text-[#D95F62] font-bold">● Crest Phase Reached</span>
              ) : (
                <span className="text-[#40A77A]">● Inflow Accumulation</span>
              )}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: DEDICATED SIDE PANEL (AWAY FROM MAP) */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          {/* Active Citizen SOS Emergency Signal Details */}
          {selectedSosId ? (
            <div className="w-full rounded-3xl bg-gradient-to-b from-[#FEE2E2]/70 via-white to-white border-2 border-[#EF4444] shadow-ocean p-5 space-y-4 animate-fade-in">
              <div className="flex items-start justify-between pb-3 border-b border-[#FCA5A5]">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#EF4444] text-white flex items-center gap-1 animate-pulse">
                      <span>!</span>
                      <span>ACTIVE CITIZEN SOS</span>
                    </span>
                    <span className="text-[10px] font-mono font-bold text-[#DC2626]">
                      {selectedSosId}
                    </span>
                  </div>
                  <h3 className="font-bold text-base text-[#17354D]">
                    {CITIZEN_SOS_SIGNALS.find((s) => s.id === selectedSosId)?.title}
                  </h3>
                  <p className="text-xs text-[#DC2626] font-semibold">
                    {CITIZEN_SOS_SIGNALS.find((s) => s.id === selectedSosId)?.basin}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedSosId(null)}
                  className="p-1 rounded-lg hover:bg-[#FEE2E2] text-[#6688A1] hover:text-[#17354D]"
                  title="Close SOS Details"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-white border border-[#FCA5A5]">
                  <span className="text-[10px] text-[#6688A1] uppercase font-semibold block">Water Depth</span>
                  <div className="text-sm font-bold font-mono text-[#DC2626]">
                    {CITIZEN_SOS_SIGNALS.find((s) => s.id === selectedSosId)?.depth}
                  </div>
                </div>
                <div className="p-2.5 rounded-xl bg-white border border-[#FCA5A5]">
                  <span className="text-[10px] text-[#6688A1] uppercase font-semibold block">Urgency Status</span>
                  <div className="text-sm font-bold font-mono text-[#DC2626]">
                    {CITIZEN_SOS_SIGNALS.find((s) => s.id === selectedSosId)?.urgency}
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-white border border-[#FCA5A5] text-xs space-y-1">
                <div className="text-[10px] font-bold text-[#6688A1] uppercase">Ground Intelligence Feed</div>
                <p className="text-[#17354D] text-xs">
                  Field report submitted {CITIZEN_SOS_SIGNALS.find((s) => s.id === selectedSosId)?.time}. Rising water impeding evacuation routes.
                </p>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={() => navigate('/relief')}
                  className="flex-1 py-2.5 rounded-xl text-xs font-bold text-center text-white bg-[#DC2626] hover:bg-[#B91C1C] shadow-sm transition-all flex items-center justify-center gap-1.5"
                >
                  <span>Dispatch Amphibious Unit</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setSelectedSosId(null)}
                  className="py-2.5 px-4 rounded-xl text-xs font-semibold text-[#6688A1] hover:text-[#17354D] bg-[#EFF6FA] hover:bg-[#D8E8F0] transition-all"
                >
                  {t('action.close')}
                </button>
              </div>
            </div>
          ) : selectedShelter ? (
            <div className="w-full rounded-3xl bg-white/95 backdrop-blur-xl border-2 border-[#40A77A] shadow-ocean p-5 space-y-3.5 animate-fade-in">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-1.5">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-[#D5A83E]/15 text-[#8F6A15] flex items-center gap-1">
                      <ShieldCheck className="w-3 h-3" />
                      Demonstration Scenario
                    </span>
                    <span className="text-[10px] font-mono font-bold text-[#6688A1]">
                      ID: {selectedShelter.id}
                    </span>
                  </div>
                  <h3 className="font-bold text-base text-[#17354D]">
                    {language === 'HI' ? selectedShelter.name_hi : selectedShelter.name}
                  </h3>
                  <p className="text-xs text-[#006297] font-semibold">
                    {language === 'HI' ? selectedShelter.basin_hi : selectedShelter.basin}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedSafeSpotId(null)}
                  className="p-1 rounded-lg hover:bg-[#EFF6FA] text-[#6688A1] hover:text-[#17354D]"
                  title="Close Safe Spot Details"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Freeboard Elevation and Evacuation Capacity */}
              <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-[#D8E8F0]">
                <div className="p-2.5 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0]">
                  <span className="text-[10px] text-[#6688A1] uppercase font-semibold block">
                    {t('map.safeSpot.freeboard')}
                  </span>
                  <div className="text-sm font-bold font-mono text-[#2D7857]">
                    +{selectedShelter.elevation_freeboard_ft} ft Freeboard
                  </div>
                </div>
                <div className="p-2.5 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0]">
                  <span className="text-[10px] text-[#6688A1] uppercase font-semibold block">
                    {t('map.safeSpot.capacity')}
                  </span>
                  <div className="text-sm font-bold font-mono text-[#006297]">
                    {selectedShelter.capacity.toLocaleString()} evacuees
                  </div>
                </div>
              </div>

              {/* Supplies and Emergency Contact */}
              <div className="p-3 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-1 text-xs">
                <span className="text-[10px] font-bold text-[#6688A1] uppercase tracking-wider block">
                  {t('map.safeSpot.supplies')}
                </span>
                <p className="text-xs text-[#17354D] font-medium leading-relaxed">
                  {language === 'HI' ? selectedShelter.supplies_hi : selectedShelter.supplies}
                </p>
              </div>

              <div className="flex items-center justify-between text-xs p-2.5 rounded-xl bg-[#40A77A]/10 border border-[#40A77A]/20 text-[#2D7857]">
                <div className="flex items-center gap-1.5 font-semibold">
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>{t('map.safeSpot.contact')}:</span>
                </div>
                <span className="font-mono font-bold text-xs">{selectedShelter.contact}</span>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={() => navigate('/relief')}
                  className="flex-1 py-2.5 rounded-xl text-xs font-bold text-center text-white bg-[#006297] hover:bg-[#287BB5] shadow-sm transition-all"
                >
                  {t('map.safeSpot.findRoute')}
                </button>
                <button
                  onClick={() => setSelectedSafeSpotId(null)}
                  className="py-2.5 px-4 rounded-xl text-xs font-semibold text-[#6688A1] hover:text-[#17354D] bg-[#EFF6FA] hover:bg-[#D8E8F0] transition-all"
                >
                  {t('action.close')}
                </button>
              </div>
              <p className="text-[9px] text-[#8F6A15] leading-relaxed px-1">
                ⚠ Demonstration scenario only. Shelter locations, capacity figures, and contact numbers are illustrative and have not been verified against official emergency management records. Do not use for real evacuation decisions.
              </p>
            </div>
          ) : (
            /* DEDICATED TWO-TAB SIDE PANEL: OPTION 1 (HISTORIC) VS OPTION 2 (SIMULATOR) */
            <div className="w-full rounded-3xl bg-white/95 backdrop-blur-xl border border-[#D8E8F0] shadow-ocean p-5 space-y-4">
              {/* Clean Option Tab Switcher */}
              <div className="grid grid-cols-2 p-1 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0]">
                <button
                  type="button"
                  onClick={() => setSidePanelTab('historic')}
                  className={`py-2 px-2 rounded-xl text-xs font-bold transition-all ${
                    sidePanelTab === 'historic'
                      ? 'bg-white text-[#006297] shadow-sm border border-[#D8E8F0]'
                      : 'text-[#6688A1] hover:text-[#17354D]'
                  }`}
                >
                  {t('map.tab.historic')}
                </button>
                <button
                  type="button"
                  onClick={() => setSidePanelTab('simulator')}
                  className={`py-2 px-2 rounded-xl text-xs font-bold transition-all ${
                    sidePanelTab === 'simulator'
                      ? 'bg-white text-[#006297] shadow-sm border border-[#D8E8F0]'
                      : 'text-[#6688A1] hover:text-[#17354D]'
                  }`}
                >
                  {t('map.tab.simulator')}
                </button>
              </div>

              {/* TAB 1: OPTION 1 — HISTORIC STATION TELEMETRY */}
              {sidePanelTab === 'historic' && (
                <div className="space-y-3.5 animate-fade-in">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          selectedStationId === '11447650'
                            ? 'bg-[#D5A83E]/15 text-[#8F6A15]'
                            : selectedDetail?.has_validation_predictions
                            ? 'bg-[#40A77A]/15 text-[#2D7857]'
                            : 'bg-[#287BB5]/15 text-[#1A5A8A]'
                        }`}
                      >
                        {selectedStationId === '11447650'
                          ? 'Historical Record Only'
                          : selectedDetail?.has_validation_predictions
                          ? 'LORSO Evaluated'
                          : 'Labelled Discharge'}
                      </span>
                      <span className="text-[10px] font-mono font-bold text-[#6688A1]">
                        ID: {selectedStationId}
                      </span>
                    </div>
                    <h3 className="font-bold text-base text-[#17354D]">
                      {selectedDetail?.station_name || currentStationSummary?.station_name || 'USGS Station'}
                    </h3>
                    <p className="text-xs text-[#006297] font-semibold">
                      {selectedDetail?.river_system || currentStationSummary?.river_system || 'River Basin'}
                    </p>
                  </div>

                  {/* Coordinates & Drainage Basin */}
                  <div className="grid grid-cols-2 gap-2 text-xs pt-1 border-t border-[#D8E8F0]">
                    <div>
                      <span className="text-[10px] text-[#6688A1] uppercase font-semibold">Coordinates</span>
                      <div className="text-xs font-semibold font-mono text-[#17354D]">
                        {selectedDetail?.coordinates
                          ? `${selectedDetail.coordinates.latitude.toFixed(3)}°, ${selectedDetail.coordinates.longitude.toFixed(3)}°`
                          : `${currentStationSummary?.latitude.toFixed(3)}°, ${currentStationSummary?.longitude.toFixed(3)}°`}
                      </div>
                    </div>
                    <div>
                      <span className="text-[10px] text-[#6688A1] uppercase font-semibold">Drainage Basin</span>
                      <div className="text-xs font-semibold font-mono text-[#17354D]">
                        {selectedDetail?.drainage_area_sqmi != null
                          ? `${selectedDetail.drainage_area_sqmi.toLocaleString()} mi²`
                          : currentStationSummary?.drainage_area_sqmi != null
                          ? `${currentStationSummary.drainage_area_sqmi.toLocaleString()} mi²`
                          : 'N/A'}
                      </div>
                    </div>
                  </div>

                  {/* Date Range Selector for Hydrograph */}
                  <div className="space-y-1.5 pt-1">
                    <div className="flex items-center justify-between text-[10px] font-bold text-[#6688A1] uppercase tracking-wider">
                      <span>Hydrograph Date Span</span>
                      <span className="font-mono text-[#006297] text-[10px]">{dateParams.start} → {dateParams.end}</span>
                    </div>
                    <div className="flex items-center gap-1 p-1 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0]">
                      {(['7d', '30d', '90d', '1y', 'all'] as const).map((range) => (
                        <button
                          key={range}
                          onClick={() => setHydroDateRange(range)}
                          className={`flex-1 py-1 rounded-lg text-[10px] font-bold uppercase transition-all ${
                            hydroDateRange === range
                              ? 'bg-white text-[#006297] shadow-sm'
                              : 'text-[#6688A1] hover:text-[#17354D]'
                          }`}
                        >
                          {range}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Interactive Hydrograph Display */}
                  <div className="p-3 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-1.5">
                    <div className="flex justify-between items-center text-[10px] font-bold text-[#6688A1]">
                      <span className="uppercase">Discharge Series (cfs)</span>
                      <div className="flex items-center gap-2">
                        <span className="text-[#006297]">● Actual</span>
                        <span className="text-[#E58C47]">-- LORSO Pred</span>
                      </div>
                    </div>
                    <div className="w-full">{renderHydroChart()}</div>
                  </div>

                  {/* Verified USGS Flow Percentiles Grid */}
                  <div className="p-3 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-1.5 text-xs">
                    <div className="flex items-center justify-between text-[10px] font-bold text-[#6688A1] uppercase tracking-wider">
                      <span>Verified USGS Flow Percentiles</span>
                      <span>(00060_00003 cfs)</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center pt-1">
                      <div className="p-1.5 rounded-lg bg-white/80 border border-[#D8E8F0]">
                        <div className="text-[9px] text-[#6688A1]">Min Rec</div>
                        <div className="text-[11px] font-mono font-bold text-[#17354D]">
                          {formatCfs(selectedDetail?.flow_thresholds_cfs?.min_recorded_cfs)}
                        </div>
                      </div>
                      <div className="p-1.5 rounded-lg bg-white/80 border border-[#D8E8F0]">
                        <div className="text-[9px] text-[#6688A1]">Q50 Median</div>
                        <div className="text-[11px] font-mono font-bold text-[#006297]">
                          {formatCfs(selectedDetail?.flow_thresholds_cfs?.q50_median_cfs)}
                        </div>
                      </div>
                      <div className="p-1.5 rounded-lg bg-white/80 border border-[#D8E8F0]">
                        <div className="text-[9px] text-[#6688A1]">Q90 Flood</div>
                        <div className="text-[11px] font-mono font-bold text-[#D95F62]">
                          {formatCfs(selectedDetail?.flow_thresholds_cfs?.q90_threshold_cfs)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Record Span & Observations Count */}
                  <div className="flex justify-between items-center text-[11px] text-[#6688A1] px-1">
                    <span>Record Span:</span>
                    <span className="font-mono font-semibold text-[#17354D]">
                      {selectedDetail?.observation_start || '2010-01-01'} → {selectedDetail?.observation_end || '2023-12-31'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-[11px] text-[#6688A1] px-1">
                    <span>Total Mean Observations:</span>
                    <span className="font-mono font-semibold text-[#006297]">
                      {selectedDetail?.total_observations?.toLocaleString() || '5,113'} days
                    </span>
                  </div>

                  {/* Historical Record Only warning for Sacramento Freeport station */}
                  {selectedStationId === '11447650' && (
                    <div className="p-2.5 rounded-xl bg-[#D5A83E]/15 border border-[#D5A83E]/30 text-[10px] text-[#8F6A15] font-semibold leading-relaxed">
                      ⚠ Historical Record Only — Observation window ended 2015-09-30. No recent telemetry available. LORSO evaluation not performed for this station.
                    </div>
                  )}

                  {/* Action CTA Buttons */}
                  <div className="flex items-center gap-2 pt-1">
                    <button
                      onClick={() => navigate(`/dashboard?station=${selectedStationId}#hydrograph`)}
                      className="flex-1 py-2 rounded-xl text-xs font-bold text-center text-[#006297] bg-[#EFF6FA] hover:bg-[#D8E8F0] transition-all flex items-center justify-center gap-1"
                    >
                      <span>{t('action.fullHydrograph')}</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => navigate('/alerts')}
                      className="flex-1 py-2 rounded-xl text-xs font-bold text-center text-white bg-gradient-to-r from-[#D95F62] to-[#E58C47] hover:opacity-95 shadow-sm transition-all"
                    >
                      {t('action.issueAlert')}
                    </button>
                  </div>
                </div>
              )}

              {/* TAB 2: OPTION 2 — RAINFALL SCENARIO SIMULATOR */}
              {sidePanelTab === 'simulator' && (
                <div className="space-y-4 animate-fade-in">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-sm text-[#17354D]">
                        {t('map.scenario.title')}
                      </h4>
                      <p className="text-[10px] text-[#6688A1]">
                        {t('map.scenario.subtitle')}
                      </p>
                    </div>
                    <TruthBanner inline type="demo" />
                  </div>

                  {/* Prominent Demonstration Disclaimer */}
                  <div className="p-2.5 rounded-xl bg-[#D5A83E]/15 border border-[#D5A83E]/30 text-[10px] text-[#8F6A15] font-semibold leading-relaxed">
                    ⚠️ {t('map.scenario.disclaimer')}
                  </div>

                  {/* Rainfall Depth Slider */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-medium text-[#36556C]">{t('map.scenario.inflow')}:</span>
                      <span className="font-mono font-bold text-[#006297]">{rainfallInflow} mm</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="150"
                      step="5"
                      value={rainfallInflow}
                      onChange={(e) => setRainfallInflow(Number(e.target.value))}
                      className="w-full h-2 bg-[#D8E8F0] rounded-lg appearance-none cursor-pointer accent-[#006297]"
                    />
                    <div className="flex justify-between text-[10px] text-[#6688A1]">
                      <span>Dry (0 mm)</span>
                      <span>Moderate (50 mm)</span>
                      <span>Extreme (150 mm)</span>
                    </div>
                  </div>

                  {/* Storm Duration Selector */}
                  <div className="space-y-1.5">
                    <span className="text-xs font-medium text-[#36556C] block">
                      {t('map.scenario.duration')}:
                    </span>
                    <div className="grid grid-cols-4 gap-1.5">
                      {([6, 12, 24, 48] as const).map((hrs) => (
                        <button
                          key={hrs}
                          type="button"
                          onClick={() => setScenarioDuration(hrs)}
                          className={`py-1.5 rounded-xl text-xs font-bold transition-all ${
                            scenarioDuration === hrs
                              ? 'bg-[#006297] text-white shadow-sm'
                              : 'bg-[#EFF6FA] text-[#36556C] hover:bg-[#D8E8F0]'
                          }`}
                        >
                          {hrs}h
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Antecedent Soil Saturation */}
                  <div className="space-y-1.5">
                    <span className="text-xs font-medium text-[#36556C] block">
                      {t('map.scenario.soil')}:
                    </span>
                    <div className="grid grid-cols-3 gap-1.5">
                      <button
                        type="button"
                        onClick={() => setSoilMoisture('DRY')}
                        className={`py-1.5 px-1 rounded-xl text-[10px] font-bold transition-all ${
                          soilMoisture === 'DRY'
                            ? 'bg-[#006297] text-white shadow-sm'
                            : 'bg-[#EFF6FA] text-[#36556C] hover:bg-[#D8E8F0]'
                        }`}
                      >
                        {t('map.scenario.soil.dry')}
                      </button>
                      <button
                        type="button"
                        onClick={() => setSoilMoisture('NORMAL')}
                        className={`py-1.5 px-1 rounded-xl text-[10px] font-bold transition-all ${
                          soilMoisture === 'NORMAL'
                            ? 'bg-[#006297] text-white shadow-sm'
                            : 'bg-[#EFF6FA] text-[#36556C] hover:bg-[#D8E8F0]'
                        }`}
                      >
                        {t('map.scenario.soil.normal')}
                      </button>
                      <button
                        type="button"
                        onClick={() => setSoilMoisture('SATURATED')}
                        className={`py-1.5 px-1 rounded-xl text-[10px] font-bold transition-all ${
                          soilMoisture === 'SATURATED'
                            ? 'bg-[#006297] text-white shadow-sm'
                            : 'bg-[#EFF6FA] text-[#36556C] hover:bg-[#D8E8F0]'
                        }`}
                      >
                        {t('map.scenario.soil.saturated')}
                      </button>
                    </div>
                  </div>

                  {/* Calculated Scenario Results Card */}
                  <div className="p-3.5 rounded-2xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-2 text-xs">
                    <div className="flex justify-between items-center">
                      <span className="text-[#6688A1]">{t('map.scenario.peak')}:</span>
                      <span
                        className={`font-mono font-bold text-sm ${
                          isSurgeOverThreshold
                            ? 'text-[#D95F62]'
                            : isApproachingThreshold
                            ? 'text-[#E58C47]'
                            : 'text-[#2D7857]'
                        }`}
                      >
                        {formatCfs(simulatedCrestFlow)}
                      </span>
                    </div>

                    <div className="flex justify-between items-center pt-1 border-t border-[#D8E8F0]/70">
                      <span className="text-[#6688A1]">Station Flood Floor (q90):</span>
                      <span className="font-mono font-bold text-[#17354D]">
                        {formatCfs(q90Threshold)}
                      </span>
                    </div>

                    <div className="flex justify-between items-center pt-1 border-t border-[#D8E8F0]/70">
                      <span className="text-[#6688A1]">{t('map.scenario.status')}:</span>
                      <span
                        className={`font-bold px-2 py-0.5 rounded-full text-[10px] ${
                          isSurgeOverThreshold
                            ? 'bg-[#D95F62]/15 text-[#A92A2D]'
                            : isApproachingThreshold
                            ? 'bg-[#E58C47]/15 text-[#B55914]'
                            : 'bg-[#40A77A]/15 text-[#2D7857]'
                        }`}
                      >
                        {isSurgeOverThreshold
                          ? `CRITICAL EXCEEDANCE (+${Math.round(((simulatedCrestFlow - q90Threshold) / q90Threshold) * 100)}%)`
                          : isApproachingThreshold
                          ? 'APPROACHING FLOOD THRESHOLD'
                          : 'SUB-CRITICAL FLOW (SAFE)'}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapPage;
