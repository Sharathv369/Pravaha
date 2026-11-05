import React from 'react';

interface OceanButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  children: React.ReactNode;
  fullWidth?: boolean;
}

export const OceanButton: React.FC<OceanButtonProps> = ({
  variant = 'primary',
  size = 'md',
  icon,
  children,
  fullWidth = false,
  className = '',
  disabled,
  ...props
}) => {
  const sizeClasses = {
    sm: 'text-xs px-3 py-1.5 rounded-lg gap-1.5',
    md: 'text-sm px-4 py-2.5 rounded-xl gap-2',
    lg: 'text-base px-6 py-3.5 rounded-2xl gap-2.5 font-semibold',
  };

  const variantClasses = {
    primary:
      'bg-gradient-to-r from-[#006297] to-[#287BB5] text-white shadow-marine hover:opacity-95 hover:shadow-ocean active:scale-[0.98]',
    secondary:
      'bg-white/80 border border-[#D8E8F0] text-[#17354D] hover:bg-[#EFF6FA] hover:border-[#287BB5]/40 active:scale-[0.98]',
    danger:
      'bg-gradient-to-r from-[#D95F62] to-[#E98985] text-white shadow-ambient hover:opacity-95 active:scale-[0.98]',
    ghost:
      'bg-transparent text-[#36556C] hover:bg-[#EFF6FA] hover:text-[#006297] active:scale-[0.98]',
    outline:
      'bg-transparent border border-[#287BB5] text-[#287BB5] hover:bg-[#287BB5]/10 active:scale-[0.98]',
  };

  const disabledClasses = disabled
    ? 'opacity-50 cursor-not-allowed pointer-events-none'
    : 'cursor-pointer transition-all duration-150';

  return (
    <button
      className={`inline-flex items-center justify-center font-medium ${sizeClasses[size]} ${variantClasses[variant]} ${disabledClasses} ${fullWidth ? 'w-full' : ''} ${className}`}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="inline-flex shrink-0">{icon}</span>}
      <span>{children}</span>
    </button>
  );
};

export default OceanButton;

