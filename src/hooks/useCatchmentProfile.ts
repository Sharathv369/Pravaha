import { useState, useEffect, useCallback } from 'react';
import { catchmentService } from '../services/catchmentService';
import { ApiCatchmentProfileResponse } from '../types/api';

export function useCatchmentProfile(stationId: string | null) {
  const [catchmentProfile, setCatchmentProfile] = useState<ApiCatchmentProfileResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async (signal?: AbortSignal) => {
    if (!stationId) {
      setCatchmentProfile(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await catchmentService.getCatchmentProfile(stationId, signal);
      setCatchmentProfile(res);
    } catch (err: unknown) {
      const errorObj = err as Error;
      if (errorObj.name !== 'AbortError') {
        setError(errorObj.message || `Failed to fetch catchment profile for station ${stationId}`);
      }
    } finally {
      setLoading(false);
    }
  }, [stationId]);

  useEffect(() => {
    const controller = new AbortController();
    fetchProfile(controller.signal);
    return () => controller.abort();
  }, [fetchProfile]);

  return {
    catchmentProfile,
    loading,
    error,
    reload: () => fetchProfile(),
  };
}

