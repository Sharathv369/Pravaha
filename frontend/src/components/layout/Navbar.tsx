import React, { useState, useEffect } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Search,
  Clock,
  Radio,
  CheckCircle,
  AlertTriangle,
  X,
  Volume2,
} from 'lucide-react';
import { VERIFIED_STATIONS } from '../../data/mockData';
import { useStations } from '../../hooks/useStations';
import { useLanguage } from '../../context/LanguageContext';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { stations: apiStations } = useStations();
  const { language, setLanguage, t } = useLanguage();
  const [showBroadcastModal, setShowBroadcastModal] = useState(false);
  const [broadcastSent, setBroadcastSent] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Array<{ station_id: string; station_name: string; river_name: string }>>([]);
  const [utcTime, setUtcTime] = useState<string>('');

  // Active pool of stations (API first, fallback to mockData if offline)
  const availableStations = apiStations.length > 0 ? apiStations : VERIFIED_STATIONS;

  // Live UTC Clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(
        now.toUTCString().split(' ').slice(4, 5)[0] + ' UTC'
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  // Search filter
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    const q = searchQuery.toLowerCase();
    const matches = availableStations.filter(
      (s) =>
        s.station_id.includes(q) ||
        s.station_name.toLowerCase().includes(q) ||
        s.river_name.toLowerCase().includes(q) ||
        (s.river_system && s.river_system.toLowerCase().includes(q))
    ).slice(0, 5);
    setSearchResults(matches);
  }, [searchQuery, availableStations]);

  const handleSelectStation = (stationId: string) => {
    setSearchQuery('');
    setSearchResults([]);
    navigate(`/dashboard?station=${stationId}`);
  };

  const handleTriggerBroadcast = () => {
    setBroadcastSent(true);
    setTimeout(() => {
      setBroadcastSent(false);
      setShowBroadcastModal(false);
    }, 2800);
  };

  return (
    <>
      <header className="sticky top-0 z-40 bg-white/88 backdrop-blur-xl border-b border-[#D8E8F0] shadow-[0_1px_8px_rgba(32,92,137,0.06)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-3">
            {/* Primary Brand Logo - Seamless Circular Glassmorphic Insignia */}
            <NavLink to="/dashboard" className="flex items-center gap-3 shrink-0 group">
              <div className="relative w-11 h-11 sm:w-12 sm:h-12 rounded-full overflow-hidden p-[1.5px] bg-gradient-to-tr from-[#004b75] via-[#006297] to-[#51B9CC] shadow-[0_4px_18px_rgba(0,140,210,0.32)] ring-2 ring-white/90 group-hover:scale-105 group-hover:shadow-[0_6px_24px_rgba(0,180,255,0.48)] transition-all duration-200 shrink-0">
                <img
                  src="/logo-circle.png"
                  alt="PRAVAHA Official Logo"
                  className="w-full h-full object-cover rounded-full"
                />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-lg text-[#006297] tracking-tight group-hover:text-[#287BB5] transition-colors">
                    PRAVAHA
                  </span>
                  <span className="hidden sm:inline-block text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-full bg-[#287BB5]/10 text-[#006297] border border-[#287BB5]/20">
                    CORE v4.2
                  </span>
                </div>
                <span className="hidden sm:block text-[10px] font-medium text-[#6688A1] tracking-wider">
                  {t('brand.tagline')}
                </span>
              </div>
            </NavLink>

            {/* Omnisearch Bar with Quick Results */}
            <div className="relative flex-1 max-w-md hidden md:block">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6688A1] pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder={t('nav.search')}
                  className="w-full h-9 pl-9 pr-4 rounded-xl bg-[#EFF6FA]/80 border border-[#D8E8F0] text-xs font-medium text-[#17354D] placeholder:text-[#6688A1] focus:outline-none focus:bg-white focus:border-[#287BB5] transition-all shadow-inner"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#6688A1] hover:text-[#17354D]"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Search Dropdown Results */}
              {searchResults.length > 0 && (
                <div className="absolute top-11 left-0 right-0 rounded-2xl bg-white border border-[#D8E8F0] shadow-2xl p-2 z-50 space-y-1">
                  <div className="px-2 py-1 text-[10px] uppercase font-bold text-[#6688A1] tracking-wider">
                    USGS Hydrologic Stations
                  </div>
                  {searchResults.map((s) => (
                    <div
                      key={s.station_id}
                      onClick={() => handleSelectStation(s.station_id)}
                      className="p-2 rounded-xl hover:bg-[#EFF6FA] cursor-pointer transition-colors flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-bold text-[#17354D]">{s.river_name}</div>
                        <div className="text-[10px] text-[#6688A1]">{s.station_name}</div>
                      </div>
                      <span className="font-mono text-[10px] font-bold text-[#006297] bg-[#287BB5]/10 px-2 py-0.5 rounded-full">
                        {s.station_id}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right Cluster: Live Clock, Language, Gauges Status, Alert CTA */}
            <div className="flex items-center gap-2 sm:gap-3 shrink-0">
              {/* UTC Clock */}
              <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-[11px] font-mono font-semibold text-[#36556C]">
                <Clock className="w-3.5 h-3.5 text-[#006297]" />
                <span>{utcTime || 'UTC Live'}</span>
              </div>

              {/* Language Switcher (Visible on all viewports) */}
              <div className="flex items-center p-0.5 rounded-lg bg-[#EFF6FA] border border-[#D8E8F0] shadow-sm">
                <button
                  type="button"
                  onClick={() => setLanguage('EN')}
                  className={`px-2 py-1 rounded-md text-[11px] font-bold transition-all ${
                    language === 'EN'
                      ? 'bg-white text-[#006297] shadow-sm border border-[#D8E8F0]'
                      : 'text-[#6688A1] hover:text-[#17354D]'
                  }`}
                  aria-label="Switch to English"
                >
                  EN
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage('HI')}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                    language === 'HI'
                      ? 'bg-[#006297] text-white shadow-sm'
                      : 'text-[#6688A1] hover:text-[#17354D]'
                  }`}
                  aria-label="हिन्दी भाषा चुनें"
                >
                  हिन्दी
                </button>
              </div>

              {/* Verified USGS Nodes Badge */}
              <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#40A77A]/10 border border-[#40A77A]/25 text-[10px] font-semibold text-[#2D7857]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#40A77A] animate-pulse" />
                <span>33 EVALUATED LORSO GAUGES</span>
              </div>

              {/* Emergency Dispatch Button */}
              <button
                onClick={() => setShowBroadcastModal(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-[#D95F62] to-[#E58C47] hover:opacity-95 shadow-sm active:scale-95 transition-all"
                title="Trigger Emergency Siren Protocol"
              >
                <Radio className="w-3.5 h-3.5 animate-pulse" />
                <span className="hidden sm:inline">{t('nav.emergency')}</span>
                <span className="sm:hidden">ALERT</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Emergency Broadcast Demonstration Modal */}
      {showBroadcastModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
          <div className="relative w-full max-w-lg rounded-2xl bg-white border border-[#D8E8F0] shadow-2xl p-6 overflow-hidden">
            <div className="flex items-start justify-between pb-4 border-b border-[#D8E8F0]">
              <div className="flex items-center gap-2.5">
                <div className="w-10 h-10 rounded-xl bg-[#D95F62]/10 text-[#D95F62] flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-[#17354D]">
                    Simulate Emergency Siren & Broadcast Protocol
                  </h3>
                  <p className="text-xs text-[#6688A1]">
                    Regional multi-channel emergency alert dispatch test
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowBroadcastModal(false)}
                className="p-1 rounded-lg text-[#6688A1] hover:bg-[#EFF6FA]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="py-4 space-y-3">
              <div className="p-3 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] text-xs text-[#36556C] space-y-1">
                <div className="flex justify-between font-semibold text-[#17354D]">
                  <span>Target Basin:</span>
                  <span className="text-[#006297]">Sacramento River (Station 11447650)</span>
                </div>
                <div className="flex justify-between">
                  <span>Trigger Condition:</span>
                  <span className="font-medium text-[#D95F62]">
                    Flow Exceeds Historical 90th Percentile (q90 = 38,500 cfs)
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Channels Armed:</span>
                  <span className="font-medium">SMS Gateway, WhatsApp Sentinel, Siren Array, Push</span>
                </div>
              </div>

              {broadcastSent ? (
                <div className="p-4 rounded-xl bg-[#40A77A]/15 border border-[#40A77A]/30 text-center space-y-2">
                  <CheckCircle className="w-8 h-8 text-[#40A77A] mx-auto animate-bounce" />
                  <p className="font-bold text-[#2D7857] text-sm">
                    Simulation Broadcast Dispatched!
                  </p>
                  <p className="text-xs text-[#36556C]">
                    Simulated dispatch transmitted to 34,200 mobile units and 4 sirens active.
                  </p>
                </div>
              ) : (
                <div className="space-y-3 text-xs text-[#6688A1]">
                  <p>
                    Triggering this test simulates immediate broadcast siren alerts and SMS gateway
                    dispatch across the active catchment zone.
                  </p>
                  <div className="p-2.5 rounded-lg bg-[#E58C47]/10 border border-[#E58C47]/25 text-[#B55914] text-[11px] font-semibold flex items-center gap-2">
                    <Volume2 className="w-4 h-4 shrink-0" />
                    <span>DEMONSTRATION SIMULATION — Safe sandbox trigger (No live 911/EAS)</span>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-[#D8E8F0]">
              <button
                onClick={() => setShowBroadcastModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-[#36556C] hover:bg-[#EFF6FA]"
              >
                Cancel
              </button>
              <button
                onClick={handleTriggerBroadcast}
                disabled={broadcastSent}
                className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-[#D95F62] to-[#E58C47] hover:opacity-95 shadow-md active:scale-95 transition-all disabled:opacity-50"
              >
                {broadcastSent ? 'Transmitting...' : 'Dispatch Test Broadcast'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
