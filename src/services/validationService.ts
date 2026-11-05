import { apiClient } from './apiClient';
import { ApiLeaderboardResponse, ApiRiverSystemsResponse } from '../types/api';

export const validationService = {
  getLeaderboard: (signal?: AbortSignal): Promise<ApiLeaderboardResponse> => {
    return apiClient.get<ApiLeaderboardResponse>('/api/validation/leaderboard', undefined, { signal });
  },

  getRiverSystems: (modelName?: string, signal?: AbortSignal): Promise<ApiRiverSystemsResponse> => {
    return apiClient.get<ApiRiverSystemsResponse>(
      '/api/validation/river-systems',
      { model_name: modelName },
      { signal }
    );
  },
};

