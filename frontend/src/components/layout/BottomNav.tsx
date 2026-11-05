import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  MapPin,
  AlertTriangle,
  Users,
  HeartHandshake,
} from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

export const BottomNav: React.FC = () => {
  const { t } = useLanguage();

  return (
    <nav className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 flex items-center gap-1.5 sm:gap-3 px-3.5 py-2 rounded-full bg-white/98 backdrop-blur-2xl border-2 border-white/90 shadow-[0_20px_50px_rgba(0,0,0,0.28)]">
      {/* Dashboard */}
      <NavLink
        to="/dashboard"
        className={({ isActive }) =>
          `flex flex-col sm:flex-row items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
            isActive
              ? 'bg-[#006297] text-white shadow-sm'
              : 'text-[#17354D] hover:bg-[#EFF6FA] hover:text-[#006297]'
          }`
        }
      >
        <LayoutDashboard className="w-4 h-4 shrink-0" />
        <span className="text-[11px] sm:text-xs">{t('nav.dashboard')}</span>
      </NavLink>

      {/* River Map */}
      <NavLink
        to="/map"
        className={({ isActive }) =>
          `flex flex-col sm:flex-row items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
            isActive
              ? 'bg-[#006297] text-white shadow-sm'
              : 'text-[#17354D] hover:bg-[#EFF6FA] hover:text-[#006297]'
          }`
        }
      >
        <MapPin className="w-4 h-4 shrink-0" />
        <span className="text-[11px] sm:text-xs">{t('nav.map')}</span>
      </NavLink>

      {/* Center Elevated Alerts Button */}
      <div className="relative -top-3.5 px-1">
        <NavLink
          to="/alerts"
          className="flex flex-col items-center group"
          title={t('alerts.title')}
        >
          <div className="w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-gradient-to-tr from-[#D95F62] to-[#E98985] text-white shadow-[0_8px_20px_-4px_rgba(217,95,98,0.55)] ring-4 ring-white flex items-center justify-center transform transition-transform group-hover:scale-105 active:scale-95">
            <AlertTriangle className="w-5 h-5 shrink-0 animate-pulse" />
          </div>
          <span className="mt-0.5 text-[10px] font-extrabold text-[#17354D] group-hover:text-[#006297] transition-colors">
            {t('nav.alerts')}
          </span>
        </NavLink>
      </div>

      {/* Community */}
      <NavLink
        to="/community"
        className={({ isActive }) =>
          `flex flex-col sm:flex-row items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
            isActive
              ? 'bg-[#006297] text-white shadow-sm'
              : 'text-[#17354D] hover:bg-[#EFF6FA] hover:text-[#006297]'
          }`
        }
      >
        <Users className="w-4 h-4 shrink-0" />
        <span className="text-[11px] sm:text-xs">{t('nav.community')}</span>
      </NavLink>

      {/* Relief Hub */}
      <NavLink
        to="/relief"
        className={({ isActive }) =>
          `flex flex-col sm:flex-row items-center gap-1 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
            isActive
              ? 'bg-[#006297] text-white shadow-sm'
              : 'text-[#17354D] hover:bg-[#EFF6FA] hover:text-[#006297]'
          }`
        }
      >
        <HeartHandshake className="w-4 h-4 shrink-0" />
        <span className="text-[11px] sm:text-xs">{t('nav.relief')}</span>
      </NavLink>
    </nav>
  );
};

export default BottomNav;

