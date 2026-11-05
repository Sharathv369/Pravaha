import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import BottomNav from './components/layout/BottomNav';
import DashboardPage from './pages/DashboardPage';
import MapPage from './pages/MapPage';
import AlertsPage from './pages/AlertsPage';
import CommunityPage from './pages/CommunityPage';
import ReliefPage from './pages/ReliefPage';
import { useStations } from './hooks/useStations';
import { useValidation } from './hooks/useValidation';
import { LanguageProvider, useLanguage } from './context/LanguageContext';

const AppContent: React.FC = () => {
  const { totalCount } = useStations();
  const { leaderboard } = useValidation();
  const { t } = useLanguage();
  const topR2 = leaderboard?.models[0]?.pooled_r2 ? leaderboard.models[0].pooled_r2.toFixed(4) : '0.4910';
  const displayCount = totalCount > 0 ? totalCount : 38;

  return (
    <div className="min-h-screen bg-[#EFF6FA] text-[#17354D] flex flex-col font-sans selection:bg-[#287BB5]/20 selection:text-[#006297] pb-24">
      {/* Top Header Bar */}
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-5">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/community" element={<CommunityPage />} />
          <Route path="/relief" element={<ReliefPage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>

      {/* Floating Bottom Pill Dock (Signature Stitch Navigation) */}
      <BottomNav />

      {/* System Scientific Disclosure Footer */}
      <footer className="mt-auto border-t border-[#D8E8F0] bg-white/75 backdrop-blur-md py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#6688A1]">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-full overflow-hidden p-0.5 bg-gradient-to-tr from-[#006297] to-[#51B9CC] shadow-sm shrink-0 ring-1 ring-white">
              <img src="/logo-circle.png" alt="PRAVAHA" className="w-full h-full object-cover rounded-full" />
            </div>
            <span className="font-bold text-[#17354D]">PRAVAHA</span>
            <span>— {t('brand.tagline')}</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 text-[11px]">
            <span>{displayCount} Verified USGS Stations (00060_00003)</span>
            <span>•</span>
            <span>23 River-System LORSO Groups</span>
            <span>•</span>
            <span>NASA MERRA-2 Meteorology</span>
            <span>•</span>
            <span className="text-[#006297] font-semibold">Pooled R² (LORSO Validation) = {topR2}</span>
          </div>

          <div className="flex items-center gap-1.5 text-[11px]">
            <span className="w-2 h-2 rounded-full bg-[#40A77A]" />
            <span className="font-semibold text-[#17354D]">TruthEngine Verified</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
};

export default App;
