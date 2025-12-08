/**
 * QorSense API Client
 * 
 * Centralized API configuration with environment-based URL,
 * request/response interceptors, and error handling.
 */

import axios, { AxiosError, AxiosRequestConfig } from 'axios';

// API Base URL from environment or fallback to localhost
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000, // 30 second timeout
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token if available
apiClient.interceptors.request.use(
    (config) => {
        // Future: Add JWT token from localStorage/sessionStorage
        // const token = localStorage.getItem('access_token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`;
        // }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor - handle errors globally
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error: AxiosError) => {
        // Handle specific error codes
        if (error.response) {
            // Server responded with error status
            switch (error.response.status) {
                case 401:
                    // Unauthorized - redirect to login (future)
                    console.error('Unauthorized access');
                    break;
                case 403:
                    // Forbidden
                    console.error('Access forbidden');
                    break;
                case 404:
                    console.error('Resource not found');
                    break;
                case 500:
                    console.error('Internal server error');
                    break;
                default:
                    console.error(`API Error: ${error.response.status}`);
            }
        } else if (error.request) {
            // Request made but no response received
            console.error('No response from server - check if backend is running');
        } else {
            // Error in request configuration
            console.error('Request configuration error:', error.message);
        }

        return Promise.reject(error);
    }
);

// ========================================
// Backward Compatibility API
// ========================================
// Export old-style API for existing components
export const api = {
    healthCheck: async () => {
        try {
            const res = await apiClient.get('/');
            return res.status === 200;
        } catch (error) {
            return false;
        }
    },

    getSensors: async (): Promise<Sensor[]> => {
        const res = await apiClient.get('/sensors');
        // Backend returns PaginatedResponse: { items: [...], total, page, size, pages }
        // Extract items array for backward compatibility with existing components
        if (res.data && Array.isArray(res.data.items)) {
            return res.data.items;
        }
        // Fallback: if response is already an array (legacy support)
        if (Array.isArray(res.data)) {
            return res.data;
        }
        // Default to empty array if unexpected format
        console.warn('Unexpected sensors response format:', res.data);
        return [];
    },

    createSensor: async (data: CreateSensorData) => {
        const res = await apiClient.post('/sensors', data);
        return res.data;
    },

    uploadReadings: async (sensorId: string, formData: FormData) => {
        // Note: sensor_id is already in FormData from the modal component
        // CRITICAL: For FormData uploads, we must NOT set Content-Type header.
        // Using a fresh axios instance without the default Content-Type header.
        const response = await fetch(`${apiClient.defaults.baseURL}/sensors/upload-csv`, {
            method: 'POST',
            body: formData,
            // Don't set Content-Type - browser will set it with correct boundary
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(error.detail || `Upload failed with status ${response.status}`);
        }

        return response.json();
    },

    analyzeSensor: async (sensorId: string, config?: any) => {
        const payload = {
            sensor_id: sensorId,
            sensor_type: "Bio",
            values: [],
            config: config
        };
        const res = await apiClient.post('/analyze', payload);
        return res.data;
    },

    getSensorHistory: async (sensorId: string) => {
        const res = await apiClient.get(`/sensors/${sensorId}/history`);
        return res.data;
    },

    generateSynthetic: async (req: any) => {
        const res = await apiClient.post('/synthetic/generate', req);
        return res.data.data;
    },

    generateReport: async (result: any, rawData: number[]) => {
        const payload = { ...result, data: rawData };
        const res = await apiClient.post('/reports/generate', payload, {
            responseType: 'blob',
        });
        return res.data;
    }
};

// ========================================
// Type Definitions (Backward Compatibility)
// ========================================
export type SourceType = 'CSV' | 'SCADA' | 'IoT';
export type SensorStatus = 'Normal' | 'Warning' | 'Critical' | 'Unknown';

export interface Sensor {
    id: string;
    name: string;
    location: string;
    source_type: SourceType;
    organization_id?: number;
    latest_health_score?: number;
    latest_status?: SensorStatus;
    latest_analysis_timestamp?: string;
}

export interface CreateSensorData {
    name: string;
    location: string;
    source_type: SourceType;
    organization_id?: number;
}

// Export configured axios instance as default
export default apiClient;

// Export base URL for direct use
export { API_BASE_URL };
