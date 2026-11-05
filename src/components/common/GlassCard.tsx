import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  elevation?: 1 | 2 | 3;
  hoverEffect?: boolean;
  onClick?: () => void;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  elevation = 1,
  hoverEffect = false,
  onClick,
}) => {
  const elevationClasses = {
    1: 'bg-white/80 backdrop-blur-md border border-[#D8E8F0] shadow-ambient',
    2: 'bg-white/90 backdrop-blur-lg border border-[#C6DEEA] shadow-ocean',
    3: 'bg-white/95 backdrop-blur-xl border border-[#B0D3E5] shadow-marine',
  };

  const hoverClasses = hoverEffect
    ? 'hover:-translate-y-1 hover:shadow-ocean hover:border-[#287BB5]/40 transition-all duration-200 cursor-pointer'
    : '';

  return (
    <div
      onClick={onClick}
      className={`rounded-2xl ${elevationClasses[elevation]} ${hoverClasses} ${className}`}
    >
      {children}
    </div>
  );
};

export default GlassCard;

