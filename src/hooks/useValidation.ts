import { useState, useEffect, useCallback } from 'react';
import { validationService } from '../services/validationService';
import { ApiLeaderboardResponse, ApiRiverSystemsResponse } from '../types/api';

export function useValidation(modelName?: string) {
  const [leaderboard, setLeaderboard] = useState<ApiLeaderboardResponse | null>(null);
  const [riverSystems, setRiverSystems] = useState<ApiRiverSystemsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchValidationData = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const [lbRes, rsRes] = await Promise.all([
        validationService.getLeaderboard(signal),
        validationService.getRiverSystems(modelName, signal),
      ]);
      setLeaderboard(lbRes);
      setRiverSystems(rsRes);
    } catch (err: unknown) {
      const errorObj = err as Error;
      if (errorObj.name !== 'AbortError') {
        setError(errorObj.message || 'Failed to fetch LORSO validation benchmarks.');
      }
    } finally {
      setLoading(false);
    }
  }, [modelName]);

  useEffect(() => {
    const controller = new AbortController();
    fetchValidationData(controller.signal);
    return () => controller.abort();
  }, [fetchValidationData]);

  return {
    leaderboard,
    riverSystems,
    loading,
    error,
    reload: () => fetchValidationData(),
  };
}

