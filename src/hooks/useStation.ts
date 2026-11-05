import { useState, useEffect, useCallback } from 'react';
import { stationService } from '../services/stationService';
import { ApiStationDetailResponse } from '../types/api';

export function useStation(stationId: string | null) {
  const [station, setStation] = useState<ApiStationDetailResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDetail = useCallback(async (signal?: AbortSignal) => {
    if (!stationId) {
      setStation(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await stationService.getStationDetail(stationId, signal);
      setStation(res);
    } catch (err: unknown) {
      const errorObj = err as Error;
      if (errorObj.name !== 'AbortError') {
        setError(errorObj.message || `Failed to fetch details for station ${stationId}`);
      }
    } finally {
      setLoading(false);
    }
  }, [stationId]);

  useEffect(() => {
    const controller = new AbortController();
    fetchDetail(controller.signal);
    return () => controller.abort();
  }, [fetchDetail]);

  return {
    station,
    loading,
    error,
    reload: () => fetchDetail(),
  };
}

