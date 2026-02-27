import axios from 'axios';
import type {
  NetworkOverview,
  DiagnosisResult,
  FaultHistory,
  SegmentHealthResponse,
  DistrictsResponse,
} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const apiService = {
  async getNetworkOverview(): Promise<NetworkOverview> {
    const response = await api.get<NetworkOverview>('/network-overview');
    return response.data;
  },

  async runDiagnosis(): Promise<DiagnosisResult> {
    const response = await api.post<DiagnosisResult>('/run-diagnosis');
    return response.data;
  },

  async getFaultHistory(): Promise<FaultHistory> {
    const response = await api.get<FaultHistory>('/history');
    return response.data;
  },

  async getSegmentHealth(village: string): Promise<SegmentHealthResponse> {
    const response = await api.get<SegmentHealthResponse>('/segment-health', {
      params: { village },
    });
    return response.data;
  },

  async getDistricts(): Promise<DistrictsResponse> {
    const response = await api.get<DistrictsResponse>('/districts');
    return response.data;
  },

  async simulateFault(village: string, segment: string, faultType: string): Promise<void> {
    await api.post('/simulate-fault', null, {
      params: {
        village,
        segment,
        fault_type: faultType,
      },
    });
  },

  async clearFaults(village?: string): Promise<void> {
    await api.post('/clear-faults', null, {
      params: village ? { village } : {},
    });
  },
};
