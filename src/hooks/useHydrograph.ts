import { useState, useEffect, useCallback } from 'react';
import { hydrographService } from '../services/hydrographService';
import { ApiHydrographResponse } from '../types/api';

export function useHydrograph(
  stationId: string | null,
  startDate?: string,
  endDate?: string,
  modelName?: string
) {
  const [hydrograph, setHydrograph] = useState<ApiHydrographResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Default to 2022-2023 LORSO holdout window, or 2015 for Sacramento truncated station
  const defaultStart = stationId === '11447650' ? '2015-01-01' : '2022-01-01';
  const defaultEnd = stationId === '11447650' ? '2015-09-30' : '2023-12-31';

  const effectiveStart = startDate || defaultStart;
  const effectiveEnd = endDate || defaultEnd;

  const fetchHydrograph = useCallback(async (signal?: AbortSignal) => {
    if (!stationId) {
      setHydrograph(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await hydrographService.getHydrograph(
        stationId,
        effectiveStart,
        effectiveEnd,
        modelName || 'log_spec_q',
        signal
      );
      setHydrograph(res);
    } catch (err: unknown) {
      const errorObj = err as Error;
      if (errorObj.name !== 'AbortError') {
        setError(errorObj.message || `Failed to fetch hydrograph for station ${stationId}`);
      }
    } finally {
      setLoading(false);
    }
  }, [stationId, effectiveStart, effectiveEnd, modelName]);

  useEffect(() => {
    const controller = new AbortController();
    fetchHydrograph(controller.signal);
    return () => controller.abort();
  }, [fetchHydrograph]);

  return {
    hydrograph,
    loading,
    error,
    reload: () => fetchHydrograph(),
  };
}

