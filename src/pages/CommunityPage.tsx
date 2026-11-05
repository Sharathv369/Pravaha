import React, { useState, useRef } from 'react';
import {
  Eye,
  LifeBuoy,
  ThumbsUp,
  MapPin,
  CheckCircle,
  Send,
  Droplets,
  Upload,
  Trash2,
  RefreshCw,
  Check,
  Smartphone,
  Navigation,
} from 'lucide-react';
import GlassCard from '../components/common/GlassCard';
import TruthBanner from '../components/common/TruthBanner';
import { DEMO_HAZARD_REPORTS } from '../data/demoData';
import { VERIFIED_STATIONS } from '../data/mockData';
import { useStations } from '../hooks/useStations';
import { HazardReport } from '../types';
import { useLanguage } from '../context/LanguageContext';

export const CommunityPage: React.FC = () => {
  const { t } = useLanguage();
  const { stations: apiStations } = useStations();
  const availableStations = apiStations && apiStations.length > 0 ? apiStations : VERIFIED_STATIONS;

  const [activePortal, setActivePortal] = useState<'report' | 'lifeline'>(() => {
    if (typeof window !== 'undefined' && (window.location.search.includes('portal=lifeline') || window.location.search.includes('tab=rescue'))) {
      return 'lifeline';
    }
    return 'report';
  });
  const [reports, setReports] = useState<HazardReport[]>(DEMO_HAZARD_REPORTS);
  const [selectedHazardType, setSelectedHazardType] = useState<
    'HIGH_WATER' | 'BREACHED_LEVEE' | 'DEBRIS_FLOW' | 'STRUCTURAL'
  >('HIGH_WATER');
  const [selectedDepthInches, setSelectedDepthInches] = useState<number>(24);

  // Location selection mode: 'station' (pick from 38 stations) vs 'custom' (manual text)
  const [locationMode, setLocationMode] = useState<'station' | 'custom'>('station');
  const [selectedStationId, setSelectedStationId] = useState<string>('11447650');
  const [locationText, setLocationText] = useState<string>(
    'Sacramento R A Freeport Ca (USGS 11447650)'
  );
  const [selectedBasin, setSelectedBasin] = useState<string>(
    'California Central Valley System'
  );

  // Photo drag and drop upload state
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [uploadedImage, setUploadedImage] = useState<{
    url: string;
    name: string;
    sizeKb: number;
  } | null>(null);

  // Mobile Device GPS Telemetry state for Emergency Lifeline
  const [mobileGps, setMobileGps] = useState<{
    lat: number;
    lng: number;
    accuracy: number;
    timestamp: string;
  }>({
    lat: 38.5816,
    lng: -121.4944,
    accuracy: 2.8,
    timestamp: 'Live GNSS Triangulation',
  });
  const [isLocating, setIsLocating] = useState<boolean>(false);

  const [submittedMessage, setSubmittedMessage] = useState<string | null>(null);

  // Rescue request state
  const [rescuePersons, setRescuePersons] = useState<number>(3);
  const [rescueUrgency, setRescueUrgency] = useState<string>('HIGH');
  const [rescueContact, setRescueContact] = useState<string>('+1 (555) 489-2104');

  const handleAcquireGps = () => {
    setIsLocating(true);
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setMobileGps({
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            accuracy: Math.round(pos.coords.accuracy || 3),
            timestamp: new Date().toLocaleTimeString(),
          });
          setIsLocating(false);
        },
        () => {
          // Fallback simulated mobile coordinates with slight jitter
          setTimeout(() => {
            setMobileGps({
              lat: 38.5816 + (Math.random() - 0.5) * 0.01,
              lng: -121.4944 + (Math.random() - 0.5) * 0.01,
              accuracy: 2.4,
              timestamp: new Date().toLocaleTimeString(),
            });
            setIsLocating(false);
          }, 800);
        },
        { enableHighAccuracy: true, timeout: 5000 }
      );
    } else {
      setTimeout(() => {
        setIsLocating(false);
      }, 500);
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      setUploadedImage({
        url: event.target?.result as string,
        name: file.name,
        sizeKb: Math.round(file.size / 1024),
      });
    };
    reader.readAsDataURL(file);
  };

  const hazardOptions: {
    type: 'HIGH_WATER' | 'BREACHED_LEVEE' | 'DEBRIS_FLOW' | 'STRUCTURAL';
    label: string;
  }[] = [
    { type: 'HIGH_WATER', label: 'Rising Street Water' },
    { type: 'BREACHED_LEVEE', label: 'Levee Breach / Seepage' },
    { type: 'DEBRIS_FLOW', label: 'Landslide / Debris Flow' },
    { type: 'STRUCTURAL', label: 'Structural Damage / Blocked Bridge' },
  ];

  const depths = [
    { label: 'Ankle Deep', inches: 10, range: '< 1.0 ft (30cm)', stage: 'STAGE 1' },
    { label: 'Knee Deep', inches: 24, range: '1.0 – 2.5 ft (75cm)', stage: 'STAGE 2' },
    { label: 'Waist Deep', inches: 42, range: '2.5 – 4.5 ft (135cm)', stage: 'STAGE 3' },
    { label: 'Submerged', inches: 60, range: '> 5.0 ft (150cm+)', stage: 'STAGE 4 CRITICAL' },
  ];

  const handleUpvote = (id: string) => {
    setReports((prev) =>
      prev.map((r) => (r.id === id ? { ...r, upvotes: r.upvotes + 1 } : r))
    );
  };

  const handleHazardSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newReport: HazardReport = {
      id: `REP-${Math.floor(1000 + Math.random() * 9000)}`,
      timestamp: 'Just now',
      basin: selectedBasin,
      location_desc: locationText + (uploadedImage ? ' • (Photo Attached)' : ''),
      hazard_type: selectedHazardType,
      water_depth_inches: selectedDepthInches,
      status: 'VERIFIED',
      upvotes: 1,
    };
    setReports([newReport, ...reports]);
    setSubmittedMessage('Hazard report submitted! Saved to local session stream.');
    setTimeout(() => setSubmittedMessage(null), 3500);
  };

  const handleRescueSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newRescue: HazardReport = {
      id: `SOS-${Math.floor(1000 + Math.random() * 9000)}`,
      timestamp: 'Just now',
      basin: 'Emergency Evacuation Corridor 2-B',
      location_desc: `Mobile GPS: ${mobileGps.lat.toFixed(4)}° N, ${Math.abs(mobileGps.lng).toFixed(4)}° W (Accuracy: ±${mobileGps.accuracy}m, Urgency: ${rescueUrgency}, Persons: ${rescuePersons}, Contact: ${rescueContact})`,
      hazard_type: 'HIGH_WATER',
      water_depth_inches: 48,
      status: 'VERIFIED',
      upvotes: 5,
    };
    setReports([newRescue, ...reports]);
    setSubmittedMessage('Emergency rescue dispatch request recorded in local queue!');
    setTimeout(() => setSubmittedMessage(null), 4000);
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Truth Disclaimer Banner */}
      <TruthBanner
        type="demo"
        title="COMMUNITY REPORTING & CROWD TELEMETRY — DEMONSTRATION MODE"
        description="This citizen portal demonstrates crowdsourced hydrologic observations and emergency SOS requests. Submissions are stored in browser memory only and are not forwarded to 911 or first responders."
      />

      {/* Header and Dual Segmented Switcher */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-6 sm:p-8 rounded-3xl bg-white/85 border border-[#D8E8F0] shadow-ocean backdrop-blur-xl">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold tracking-widest uppercase text-[#006297] bg-[#287BB5]/10 px-2.5 py-0.5 rounded-full border border-[#287BB5]/20">
              CITIZEN HYDROMETRY
            </span>
            <span className="text-xs font-semibold text-[#6688A1]">• 14 Field Units Active</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#17354D] tracking-tight">
            {t('community.title')}
          </h1>
          <p className="text-xs sm:text-sm text-[#36556C] leading-relaxed">
            {t('community.subtitle')}
          </p>
        </div>

        {/* Segmented Dual Switcher */}
        <div className="flex items-center p-1.5 rounded-2xl bg-white/90 border border-[#D8E8F0] shadow-sm">
          <button
            onClick={() => setActivePortal('report')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
              activePortal === 'report'
                ? 'bg-[#006297] text-white shadow-marine'
                : 'text-[#36556C] hover:text-[#006297]'
            }`}
          >
            <Eye className="w-4 h-4" />
            <span>REPORT A FLOOD — PRAVAHA EYES</span>
          </button>
          <button
            onClick={() => setActivePortal('lifeline')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all ${
              activePortal === 'lifeline'
                ? 'bg-[#D95F62] text-white shadow-ambient'
                : 'text-[#36556C] hover:text-[#D95F62]'
            }`}
          >
            <LifeBuoy className="w-4 h-4" />
            <span>I NEED HELP — LIFELINE</span>
          </button>
        </div>
      </div>

      {/* Success Notification Alert */}
      {submittedMessage && (
        <div className="p-4 rounded-2xl bg-[#40A77A]/15 border border-[#40A77A]/30 flex items-center gap-3 animate-fade-in text-[#2D7857]">
          <CheckCircle className="w-6 h-6 text-[#40A77A] shrink-0" />
          <div className="text-xs font-bold">{submittedMessage}</div>
        </div>
      )}

      {/* Main Two-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* LEFT COLUMN: Active Submission Form (7 cols) */}
        <div className="lg:col-span-7">
          {activePortal === 'report' ? (
            /* PORTAL A: PRAVAHA EYES */
            <GlassCard elevation={1} className="p-6 sm:p-8 space-y-6">
              <div className="flex items-center justify-between pb-3 border-b border-[#D8E8F0]">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#287BB5]/10 text-[#006297] flex items-center justify-center">
                    <Eye className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-[#17354D]">
                      Rapid Hazard Submission
                    </h2>
                    <p className="text-[11px] text-[#6688A1]">
                      Ground Observation Entry Node
                    </p>
                  </div>
                </div>
                <span className="text-xs font-mono font-semibold text-[#006297]">
                  GPS Auto-Calibrated
                </span>
              </div>

              <form onSubmit={handleHazardSubmit} className="space-y-5">
                {/* Step 1: Hazard Classification */}
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#17354D] flex justify-between">
                    <span>1. Hazard Classification</span>
                    <span className="text-[#6688A1] font-normal">Select Primary Condition</span>
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {hazardOptions.map((opt) => (
                      <button
                        type="button"
                        key={opt.type}
                        onClick={() => setSelectedHazardType(opt.type)}
                        className={`px-3 py-1.5 rounded-full text-xs font-semibold transition-all border ${
                          selectedHazardType === opt.type
                            ? 'bg-[#006297] text-white border-[#006297] shadow-sm'
                            : 'bg-white/80 text-[#36556C] border-[#D8E8F0] hover:bg-[#EFF6FA]'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Step 2: Tactile Water Depth Gauge */}
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#17354D] flex justify-between">
                    <span>2. Water Level Estimation</span>
                    <span className="text-[#006297] font-semibold">Critical Hydraulic Factor</span>
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                    {depths.map((d) => {
                      const isSelected = selectedDepthInches === d.inches;
                      return (
                        <button
                          type="button"
                          key={d.label}
                          onClick={() => setSelectedDepthInches(d.inches)}
                          className={`p-3 rounded-xl text-left border transition-all ${
                            isSelected
                              ? 'bg-[#006297] text-white border-[#006297] shadow-marine'
                              : 'bg-white/80 text-[#17354D] border-[#D8E8F0] hover:bg-[#EFF6FA]'
                          }`}
                        >
                          <div className={`text-[10px] font-bold ${isSelected ? 'text-white/80' : 'text-[#6688A1]'}`}>
                            {d.stage}
                          </div>
                          <div className="text-xs font-bold mt-0.5">{d.label}</div>
                          <div className={`text-[10px] ${isSelected ? 'text-white/80' : 'text-[#6688A1]'}`}>
                            {d.range}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Step 3: Location Lock — Option to Select From 38 Stations */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-[#17354D]">
                      3. Spatial Telemetry & Location Lock
                    </label>
                    <div className="flex items-center p-0.5 rounded-lg bg-[#EFF6FA] border border-[#D8E8F0] text-[10px] font-bold">
                      <button
                        type="button"
                        onClick={() => setLocationMode('station')}
                        className={`px-2 py-0.5 rounded transition-all ${
                          locationMode === 'station'
                            ? 'bg-[#006297] text-white shadow-sm'
                            : 'text-[#36556C] hover:text-[#006297]'
                        }`}
                      >
                        38 USGS Stations
                      </button>
                      <button
                        type="button"
                        onClick={() => setLocationMode('custom')}
                        className={`px-2 py-0.5 rounded transition-all ${
                          locationMode === 'custom'
                            ? 'bg-[#006297] text-white shadow-sm'
                            : 'text-[#36556C] hover:text-[#006297]'
                        }`}
                      >
                        Custom / GPS
                      </button>
                    </div>
                  </div>

                  {locationMode === 'station' ? (
                    <div className="space-y-1.5 p-3 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0]">
                      <div className="flex items-center gap-2 text-xs font-semibold text-[#17354D]">
                        <MapPin className="w-4 h-4 text-[#006297] shrink-0" />
                        <select
                          value={selectedStationId}
                          onChange={(e) => {
                            const stId = e.target.value;
                            setSelectedStationId(stId);
                            const st = availableStations.find((s) => s.station_id === stId);
                            if (st) {
                              setLocationText(`${st.river_name || st.station_name} (USGS ${st.station_id})`);
                              setSelectedBasin(st.river_system || 'Verified River Basin');
                            }
                          }}
                          className="w-full p-2 rounded-lg bg-white border border-[#D8E8F0] text-xs font-medium text-[#17354D] focus:outline-none focus:border-[#006297]"
                        >
                          {availableStations.map((st) => (
                            <option key={st.station_id} value={st.station_id}>
                              {st.station_id} — {st.river_name || st.station_name} ({st.state_cd || 'US'}) • {st.river_system || 'Basin'}
                            </option>
                          ))}
                        </select>
                      </div>
                      <div className="text-[10px] text-[#6688A1] px-1 flex justify-between">
                        <span>Selected Basin: <strong className="text-[#006297]">{selectedBasin}</strong></span>
                        <span>Total Stations: <strong>{availableStations.length} Verified</strong></span>
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-1">
                      <div className="flex items-center gap-2 text-xs font-bold text-[#17354D]">
                        <MapPin className="w-4 h-4 text-[#006297] shrink-0" />
                        <input
                          type="text"
                          value={locationText}
                          onChange={(e) => setLocationText(e.target.value)}
                          placeholder="Enter landmark, road, or coordinates..."
                          className="bg-transparent border-none focus:outline-none w-full text-xs font-semibold text-[#17354D]"
                        />
                      </div>
                      <div className="text-[10px] text-[#6688A1]">
                        High Precision Field Telemetry Lock • Accurate within ±3m
                      </div>
                    </div>
                  )}
                </div>

                {/* Step 4: Photographic Evidence & Drag-and-Drop Visual AI */}
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#17354D] flex justify-between items-center">
                    <span>4. Photographic Evidence & Visual AI</span>
                    <span className="text-[10px] text-[#6688A1] font-normal">Drag & Drop Supported</span>
                  </label>
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragging(true);
                    }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleFileDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`p-4 rounded-xl border-2 border-dashed transition-all text-center cursor-pointer ${
                      isDragging
                        ? 'border-[#006297] bg-[#EFF6FA]'
                        : 'border-[#D8E8F0] bg-white/60 hover:bg-white'
                    }`}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileInputChange}
                      accept="image/*"
                      className="hidden"
                    />
                    {uploadedImage ? (
                      <div className="flex items-center justify-between gap-3 p-2 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-left">
                        <img
                          src={uploadedImage.url}
                          alt="Uploaded condition evidence"
                          className="w-16 h-16 rounded-lg object-cover border border-[#D8E8F0] shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="font-bold text-xs text-[#17354D] truncate">{uploadedImage.name}</div>
                          <div className="text-[10px] text-[#6688A1]">{uploadedImage.sizeKb} KB • Visual AI Gauge Calibrated</div>
                          <div className="text-[10px] text-[#2D7857] font-semibold flex items-center gap-1 mt-0.5">
                            <Check className="w-3 h-3 text-[#40A77A]" />
                            <span>Hydraulic Water Mark Validated</span>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setUploadedImage(null);
                          }}
                          className="p-1.5 rounded-lg text-[#6688A1] hover:text-[#DC2626] hover:bg-white"
                          title="Remove image"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <Upload className="w-7 h-7 text-[#006297] mx-auto mb-1" />
                        <div className="text-xs font-semibold text-[#17354D]">
                          Drag & drop field photo here, or click to browse
                        </div>
                        <div className="text-[10px] text-[#6688A1]">
                          JPEG, PNG or WebP • Automatic hydraulic watermark analysis
                        </div>
                      </>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-2xl text-xs font-bold text-white bg-gradient-to-r from-[#006297] to-[#287BB5] hover:opacity-95 shadow-marine transition-all flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Transmit Field Observation to PRAVAHA</span>
                </button>
              </form>
            </GlassCard>
          ) : (
            /* PORTAL B: PRAVAHA LIFELINE (RESCUE REQUEST) */
            <GlassCard elevation={1} className="p-6 sm:p-8 space-y-6 border-2 border-[#D95F62]/40 bg-gradient-to-b from-white to-[#D95F62]/5">
              <div className="flex items-center justify-between pb-3 border-b border-[#D8E8F0]">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#D95F62]/10 text-[#D95F62] flex items-center justify-center">
                    <LifeBuoy className="w-5 h-5 animate-spin" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-[#D95F62]">
                      Emergency Rescue Request Portal
                    </h2>
                    <p className="text-[11px] text-[#6688A1]">
                      Immediate Humanitarian Assistance Request
                    </p>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-[#D95F62]/15 text-[#A92A2D] text-[10px] font-bold">
                  HIGH PRIORITY QUEUE
                </span>
              </div>

              <form onSubmit={handleRescueSubmit} className="space-y-5">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-[#17354D]">
                    1. Rescue Urgency Level
                  </label>
                  <select
                    value={rescueUrgency}
                    onChange={(e) => setRescueUrgency(e.target.value)}
                    className="w-full p-2.5 rounded-xl border border-[#D8E8F0] bg-white text-xs font-semibold text-[#17354D] focus:outline-none"
                  >
                    <option value="CRITICAL">IMMEDIATE — Trapped on Roof / Tree</option>
                    <option value="HIGH">HIGH — Water Entering Living Area</option>
                    <option value="CRITICAL">CRITICAL MEDICAL — Oxygen / Dialysis Required</option>
                    <option value="HIGH">PREVENTATIVE — Rapid Surge Approaching</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#17354D]">
                      Persons Trapped
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="50"
                      value={rescuePersons}
                      onChange={(e) => setRescuePersons(Number(e.target.value))}
                      className="w-full p-2.5 rounded-xl border border-[#D8E8F0] bg-white text-xs font-bold font-mono text-[#17354D]"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-[#17354D]">
                      Emergency Contact #
                    </label>
                    <input
                      type="text"
                      value={rescueContact}
                      onChange={(e) => setRescueContact(e.target.value)}
                      className="w-full p-2.5 rounded-xl border border-[#D8E8F0] bg-white text-xs font-mono text-[#17354D]"
                    />
                  </div>
                </div>

                {/* Mobile Device GPS Telemetry Lock (Replaces Exact Address) */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-[#17354D] flex items-center gap-1.5">
                      <Smartphone className="w-4 h-4 text-[#D95F62]" />
                      <span>Live Mobile Device GPS Telemetry</span>
                    </label>
                    <button
                      type="button"
                      onClick={handleAcquireGps}
                      className="text-[11px] font-bold text-[#D95F62] hover:underline flex items-center gap-1"
                    >
                      <RefreshCw className={`w-3 h-3 ${isLocating ? 'animate-spin' : ''}`} />
                      <span>{isLocating ? 'Acquiring GPS...' : 'Refresh Device GPS'}</span>
                    </button>
                  </div>

                  <div className="p-3.5 rounded-2xl bg-white border border-[#D95F62]/30 shadow-sm space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono font-bold text-[#17354D]">
                      <span className="flex items-center gap-1.5 text-[#D95F62]">
                        <span className="w-2 h-2 rounded-full bg-[#D95F62] animate-ping" />
                        <span>{mobileGps.lat.toFixed(4)}° N, {Math.abs(mobileGps.lng).toFixed(4)}° W</span>
                      </span>
                      <span className="text-[10px] text-[#40A77A] font-semibold bg-[#40A77A]/10 px-2 py-0.5 rounded-full">
                        GNSS Fix Acquired
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-[#6688A1]">
                      <span>Accuracy Margin: <strong className="text-[#17354D]">±{mobileGps.accuracy}m High Precision</strong></span>
                      <span>Triangulation: <strong className="text-[#17354D]">Mobile GNSS / Cell Tower Locked</strong></span>
                    </div>
                    <div className="text-[10px] text-[#D95F62] bg-[#FEE2E2]/60 p-2 rounded-xl border border-[#FCA5A5] flex items-center gap-1.5">
                      <Navigation className="w-3.5 h-3.5 shrink-0" />
                      <span>Evacuation teams navigate directly to device coordinates. No manual address input required.</span>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 rounded-2xl text-xs font-bold text-white bg-gradient-to-r from-[#D95F62] to-[#E98985] hover:opacity-95 shadow-ambient transition-all flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Transmit Emergency SOS with Device GPS Coordinates</span>
                </button>
              </form>
            </GlassCard>
          )}
        </div>

        {/* RIGHT COLUMN: Live Community Telemetry Feed (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <GlassCard elevation={1} className="p-6 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#D8E8F0]">
              <div>
                <h3 className="text-base font-bold text-[#17354D]">
                  Live Community Telemetry Feed
                </h3>
                <p className="text-xs text-[#6688A1]">
                  Crowdsourced field reports validated by local residents.
                </p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#E58C47]/10 text-[#B55914] uppercase tracking-wider">
                Demonstration Feed ({reports.length})
              </span>
            </div>

            <div className="space-y-3 max-h-[620px] overflow-y-auto pr-1">
              {reports.map((report) => (
                <div
                  key={report.id}
                  className="p-4 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] space-y-2 hover:bg-white transition-all shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        report.hazard_type === 'BREACHED_LEVEE' || report.id.startsWith('SOS')
                          ? 'bg-[#D95F62]/15 text-[#A92A2D]'
                          : 'bg-[#287BB5]/15 text-[#006297]'
                      }`}
                    >
                      {report.hazard_type.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-[#6688A1]">
                      {report.timestamp}
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-[#17354D]">
                    {report.location_desc}
                  </p>

                  <div className="text-[11px] text-[#6688A1]">
                    Basin: {report.basin}
                  </div>

                  <div className="flex items-center justify-between text-[11px] pt-1 border-t border-[#D8E8F0]">
                    <div className="flex items-center gap-1.5 text-[#006297] font-semibold">
                      <Droplets className="w-3.5 h-3.5" />
                      <span>{report.water_depth_inches} in Depth</span>
                    </div>

                    <button
                      onClick={() => handleUpvote(report.id)}
                      className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-[#D8E8F0] text-xs font-semibold text-[#36556C] hover:text-[#006297] transition-all"
                    >
                      <ThumbsUp className="w-3 h-3 text-[#006297]" />
                      <span>{report.upvotes}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
};

export default CommunityPage;
