import axios from 'axios';
import { AnalysisResult, SensorDataInput, SyntheticRequest, SyntheticResponse } from '@/types';

const API_URL = 'http://127.0.0.1:8000';

export interface Sensor {
    id: string;
    name: string;
    location: string;
    source_type: 'CSV' | 'SCADA' | 'IoT';
    organization_id?: number;
    latest_health_score?: number;
    latest_status?: 'Normal' | 'Warning' | 'Critical' | 'Unknown';
    latest_analysis_timestamp?: string;
}

export interface CreateSensorData {
    name: string;
    location: string;
    source_type: 'CSV' | 'SCADA';
}

export const api = {
    healthCheck: async () => {
        try {
            const res = await axios.get(`${API_URL}/`);
            return res.status === 200;
        } catch (error) {
            return false;
        }
    },

    getSensors: async (): Promise<Sensor[]> => {
        const res = await axios.get<Sensor[]>(`${API_URL}/sensors`);
        return res.data;
    },

    createSensor: async (data: CreateSensorData): Promise<Sensor> => {
        const res = await axios.post<Sensor>(`${API_URL}/sensors`, data);
        return res.data;
    },

    uploadReadings: async (sensorId: string, formData: FormData) => {
        const res = await axios.post(`${API_URL}/upload-csv`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return res.data;
    },

    analyzeSensor: async (sensorId: string, config?: any): Promise<AnalysisResult> => {
        // We need to construct a SensorDataInput with just ID for the new flow
        // The backend expects specific payload for analyze, or we can use the new logic if implemented
        // But based on backend/main.py 'analyze_sensor' it accepts SensorDataInput which has sensor_id
        // So we send { sensor_id: sensorId, sensor_type: "Bio", values: [] } to trigger DB fetch
        const payload = {
            sensor_id: sensorId,
            sensor_type: "Bio", // Default or derived
            values: [], // Empty values triggers DB fetch in backend
            config: config // Optional configuration from settings
        };
        const res = await axios.post<AnalysisResult>(`${API_URL}/analyze`, payload);
        return res.data;
    },

    getSensorHistory: async (sensorId: string): Promise<AnalysisResult[]> => {
        const res = await axios.get<AnalysisResult[]>(`${API_URL}/sensors/${sensorId}/history`);
        return res.data;
    },

    // Keeping for compatibility if needed, but likely unused in new flow
    generateSynthetic: async (req: SyntheticRequest): Promise<number[]> => {
        const res = await axios.post<SyntheticResponse>(`${API_URL}/generate-synthetic`, req);
        return res.data.data;
    },

    generateReport: async (result: AnalysisResult, rawData: number[]) => {
        const payload = { ...result, data: rawData };
        const res = await axios.post(`${API_URL}/report`, payload, {
            responseType: 'blob',
        });
        return res.data;
    }
};
