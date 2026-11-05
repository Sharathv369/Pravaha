import React from 'react';
import GlassCard from './GlassCard';

interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  subtext?: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: React.ReactNode;
  badge?: string;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  unit,
  subtext,
  trend,
  trendValue,
  icon,
  badge,
  className = '',
}) => {
  return (
    <GlassCard elevation={1} className={`p-5 flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-[#36556C] uppercase tracking-wider">
          {label}
        </span>
        {icon && (
          <div className="w-9 h-9 rounded-xl bg-[#EFF6FA] border border-[#D8E8F0] flex items-center justify-center text-[#006297]">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1.5">
        <span className="text-2xl lg:text-3xl font-extrabold text-[#17354D] tracking-tight tabular-nums">
          {value}
        </span>
        {unit && (
          <span className="text-xs font-semibold text-[#6688A1] uppercase tracking-wide">
            {unit}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between pt-1 text-xs">
        {subtext && <span className="text-[#6688A1] text-xs font-medium">{subtext}</span>}
        {badge && (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#287BB5]/10 text-[#006297] border border-[#287BB5]/20">
            {badge}
          </span>
        )}
        {trendValue && (
          <span
            className={`inline-flex items-center gap-0.5 font-semibold text-xs ${
              trend === 'up'
                ? 'text-[#D95F62]'
                : trend === 'down'
                ? 'text-[#40A77A]'
                : 'text-[#36556C]'
            }`}
          >
            {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '●'} {trendValue}
          </span>
        )}
      </div>
    </GlassCard>
  );
};

export default StatCard;

