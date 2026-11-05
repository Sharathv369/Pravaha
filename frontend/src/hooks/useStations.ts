import { useState, useEffect, useCallback } from 'react';
import { stationService } from '../services/stationService';
import { ApiStationItem } from '../types/api';

export function useStations(search?: string, riverSystem?: string) {
  const [stations, setStations] = useState<ApiStationItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [filteredCount, setFilteredCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStations = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);
    try {
      const res = await stationService.getStations(search, riverSystem, undefined, undefined, signal);
      setStations(res.stations);
      setTotalCount(res.total_count);
      setFilteredCount(res.filtered_count);
    } catch (err: unknown) {
      const errorObj = err as Error;
      if (errorObj.name !== 'AbortError') {
        setError(errorObj.message || 'Failed to fetch verified stations.');
      }
    } finally {
      setLoading(false);
    }
  }, [search, riverSystem]);

  useEffect(() => {
    const controller = new AbortController();
    fetchStations(controller.signal);
    return () => controller.abort();
  }, [fetchStations]);

  return {
    stations,
    totalCount,
    filteredCount,
    loading,
    error,
    reload: () => fetchStations(),
  };
}

