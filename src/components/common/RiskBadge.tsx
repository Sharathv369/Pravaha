import React from 'react';

export type RiskLevel = 'normal' | 'advisory' | 'warning' | 'critical';

interface RiskBadgeProps {
  level: RiskLevel;
  className?: string;
  showDot?: boolean;
  size?: 'sm' | 'md';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  className = '',
  showDot = true,
  size = 'md',
}) => {
  const styles: Record<
    RiskLevel,
    { bg: string; text: string; border: string; dot: string; label: string }
  > = {
    normal: {
      bg: 'bg-[#40A77A]/15',
      text: 'text-[#2D7857]',
      border: 'border-[#40A77A]/30',
      dot: 'bg-[#40A77A]',
      label: 'Normal Flow',
    },
    advisory: {
      bg: 'bg-[#D5A83E]/15',
      text: 'text-[#8F6A15]',
      border: 'border-[#D5A83E]/30',
      dot: 'bg-[#D5A83E]',
      label: 'Flow Advisory',
    },
    warning: {
      bg: 'bg-[#E58C47]/15',
      text: 'text-[#B55914]',
      border: 'border-[#E58C47]/30',
      dot: 'bg-[#E58C47] animate-pulse',
      label: 'Surge Warning',
    },
    critical: {
      bg: 'bg-[#D95F62]/15',
      text: 'text-[#A92A2D]',
      border: 'border-[#D95F62]/40',
      dot: 'bg-[#D95F62] animate-ping',
      label: 'Critical Flood Stage',
    },
  };

  const current = styles[level] || styles.normal;
  const sizeClasses =
    size === 'sm'
      ? 'px-2 py-0.5 text-[11px] gap-1 font-medium'
      : 'px-2.5 py-1 text-xs gap-1.5 font-semibold';

  return (
    <span
      className={`inline-flex items-center rounded-full border ${current.bg} ${current.text} ${current.border} ${sizeClasses} ${className}`}
    >
      {showDot && (
        <span className="relative flex h-2 w-2">
          {level === 'critical' && (
            <span
              className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${current.dot}`}
            />
          )}
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${
              level === 'critical' ? 'bg-[#D95F62]' : current.dot
            }`}
          />
        </span>
      )}
      <span>{current.label}</span>
    </span>
  );
};

export default RiskBadge;

