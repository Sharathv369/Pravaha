import { apiClient } from './apiClient';
import { ApiStationDetailResponse, ApiStationListResponse, HealthResponse } from '../types/api';

export const stationService = {
  getStations: (
    search?: string,
    riverSystem?: string,
    limit?: number,
    offset?: number,
    signal?: AbortSignal
  ): Promise<ApiStationListResponse> => {
    return apiClient.get<ApiStationListResponse>(
      '/api/stations',
      { search, river_system: riverSystem, limit, offset },
      { signal }
    );
  },

  getStationDetail: (stationId: string, signal?: AbortSignal): Promise<ApiStationDetailResponse> => {
    return apiClient.get<ApiStationDetailResponse>(`/api/stations/${stationId}`, undefined, { signal });
  },

  getHealth: (signal?: AbortSignal): Promise<HealthResponse> => {
    return apiClient.get<HealthResponse>('/health', undefined, { signal });
  },
};

