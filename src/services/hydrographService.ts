import { apiClient } from './apiClient';
import { ApiHydrographResponse } from '../types/api';

export const hydrographService = {
  getHydrograph: (
    stationId: string,
    startDate?: string,
    endDate?: string,
    modelName?: string,
    signal?: AbortSignal
  ): Promise<ApiHydrographResponse> => {
    return apiClient.get<ApiHydrographResponse>(
      `/api/stations/${stationId}/hydrograph`,
      {
        start_date: startDate,
        end_date: endDate,
        model_name: modelName,
      },
      { signal }
    );
  },
};

