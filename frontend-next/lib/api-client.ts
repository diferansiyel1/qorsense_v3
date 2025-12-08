/**
 * Type-safe API Client
 * 
 * Provides typed API methods for all backend endpoints.
 */

import apiClient from './api';
import type {
    Sensor,
    SensorCreate,
    AnalysisResult,
    SensorDataInput,
    SyntheticRequest,
    ReportRequest,
} from '@/types/api';

/**
 * Sensor API methods
 */
export const sensorApi = {
    /**
     * Get all sensors
     */
    getAll: async (): Promise<Sensor[]> => {
        const response = await apiClient.get<Sensor[]>('/sensors');
        return response.data;
    },

    /**
     * Create a new sensor
     */
    create: async (sensor: SensorCreate): Promise<Sensor> => {
        const response = await apiClient.post<Sensor>('/sensors', sensor);
        return response.data;
    },

    /**
     * Get sensor analysis history
     */
    getHistory: async (sensorId: string): Promise<AnalysisResult[]> => {
        const response = await apiClient.get<AnalysisResult[]>(`/sensors/${sensorId}/history`);
        return response.data;
    },

    /**
     * Upload CSV data
     */
    uploadCsv: async (file: File, sensorId: string): Promise<{ message: string; count: number }> => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('sensor_id', sensorId);

        const response = await apiClient.post('/sensors/upload-csv', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
    },

    /**
     * Stream single data point
     */
    streamData: async (data: { sensor_id: string; value: number; timestamp?: string }) => {
        const response = await apiClient.post('/sensors/stream-data', data);
        return response.data;
    },
};

/**
 * Analytics API methods
 */
export const analyticsApi = {
    /**
     * Analyze sensor data
     */
    analyze: async (data: SensorDataInput): Promise<AnalysisResult> => {
        const response = await apiClient.post<AnalysisResult>('/analyze', data);
        return response.data;
    },
};

/**
 * Synthetic data generation
 */
export const syntheticApi = {
    /**
     * Generate synthetic data
     */
    generate: async (request: SyntheticRequest): Promise<{ data: number[]; timestamps: number[] }> => {
        const response = await apiClient.post('/synthetic/generate', request);
        return response.data;
    },
};

/**
 * Report generation
 */
export const reportApi = {
    /**
     * Generate PDF report
     */
    generate: async (request: ReportRequest): Promise<Blob> => {
        const response = await apiClient.post('/reports/generate', request, {
            responseType: 'blob',
        });
        return response.data;
    },
};

/**
 * Health check
 */
export const healthApi = {
    /**
     * Check API health
     */
    check: async (): Promise<{ status: string; service: string; version: string }> => {
        const response = await apiClient.get('/health');
        return response.data;
    },
};
