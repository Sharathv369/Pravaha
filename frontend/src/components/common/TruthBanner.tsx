import React from 'react';
import { ShieldAlert, ShieldCheck, Info } from 'lucide-react';

interface TruthBannerProps {
  type?: 'demo' | 'verified' | 'unconfirmed';
  title?: string;
  description?: string;
  className?: string;
  inline?: boolean;
}

export const TruthBanner: React.FC<TruthBannerProps> = ({
  type = 'demo',
  title,
  description,
  className = '',
  inline = false,
}) => {
  if (inline) {
    if (type === 'verified') {
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#40A77A]/15 text-[#2D7857] border border-[#40A77A]/30 ${className}`}
        >
          <ShieldCheck className="w-3.5 h-3.5 text-[#40A77A]" />
          <span>VERIFIED USGS TELEMETRY (cfs)</span>
        </span>
      );
    }
    if (type === 'unconfirmed') {
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#D5A83E]/15 text-[#8F6A15] border border-[#D5A83E]/30 ${className}`}
        >
          <Info className="w-3.5 h-3.5 text-[#D5A83E]" />
          <span>BENCHMARK DATA — UNCONFIRMED SPEC</span>
        </span>
      );
    }
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#E58C47]/15 text-[#B55914] border border-[#E58C47]/30 ${className}`}
      >
        <ShieldAlert className="w-3.5 h-3.5 text-[#E58C47]" />
        <span>DEMONSTRATION PROTOTYPE — NOT LIVE</span>
      </span>
    );
  }

  if (type === 'verified') {
    return (
      <div
        className={`flex items-start gap-3 p-3.5 rounded-xl bg-[#40A77A]/10 border border-[#40A77A]/25 text-[#17354D] ${className}`}
      >
        <ShieldCheck className="w-5 h-5 text-[#2D7857] shrink-0 mt-0.5" />
        <div className="text-xs">
          <p className="font-semibold text-[#2D7857]">
            {title || 'USGS Official Hydrographic Data (00060_00003)'}
          </p>
          <p className="text-[#36556C] mt-0.5">
            {description ||
              'Telemetry sourced from 34 verified USGS streamgauging stations with historical MERRA-2 meteorology. Flow rates in cubic feet per second (cfs).'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex items-start gap-3 p-3.5 rounded-xl bg-[#E58C47]/10 border border-[#E58C47]/30 text-[#17354D] ${className}`}
    >
      <ShieldAlert className="w-5 h-5 text-[#B55914] shrink-0 mt-0.5" />
      <div className="text-xs">
        <p className="font-semibold text-[#B55914]">
          {title || 'DEMONSTRATION MODE — NOT CONNECTED TO LIVE 911 / PUBLIC SAFETY'}
        </p>
        <p className="text-[#36556C] mt-0.5">
          {description ||
            'This dispatch/crowdsourcing feature is an interactive engineering simulation for the FLOODCAST hackathon. Submissions are saved to local session state only.'}
        </p>
      </div>
    </div>
  );
};

export default TruthBanner;

