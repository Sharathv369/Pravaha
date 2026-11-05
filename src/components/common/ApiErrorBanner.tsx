import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ApiErrorBannerProps {
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export const ApiErrorBanner: React.FC<ApiErrorBannerProps> = ({
  message = 'Unable to connect to PRAVAHA FastAPI backend at http://127.0.0.1:8000.',
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`p-4 rounded-2xl bg-[#D95F62]/10 border border-[#D95F62]/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-[#A92A2D] ${className}`}
    >
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-xl bg-[#D95F62]/20 text-[#D95F62] flex items-center justify-center shrink-0">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div>
          <div className="font-bold text-[#D95F62]">Backend Connection Error</div>
          <div className="text-[11px] text-[#A92A2D]">{message}</div>
        </div>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-3 py-1.5 rounded-lg bg-[#D95F62] text-white font-semibold text-xs flex items-center gap-1.5 hover:bg-[#c24f52] transition-colors shadow-sm shrink-0"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
};

export default ApiErrorBanner;

