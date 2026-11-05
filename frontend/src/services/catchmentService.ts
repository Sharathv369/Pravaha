import { apiClient } from './apiClient';
import { ApiCatchmentProfileResponse } from '../types/api';

export const catchmentService = {
  getCatchmentProfile: (stationId: string, signal?: AbortSignal): Promise<ApiCatchmentProfileResponse> => {
    return apiClient.get<ApiCatchmentProfileResponse>(
      `/api/stations/${stationId}/catchment-profile`,
      undefined,
      { signal }
    );
  },
};

