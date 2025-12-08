/**
 * QorSense API Type Definitions
 * 
 * TypeScript interfaces matching backend Pydantic models.
 */

// ========================================
// Sensor Types
// ========================================

export type SourceType = 'CSV' | 'SCADA' | 'IoT';
export type SensorStatus = 'Normal' | 'Warning' | 'Critical' | 'Unknown' | 'No Data' | 'Healthy';

export interface Sensor {
    id: string;
    name: string;
    location: string;
    source_type: SourceType;
    organization_id?: number;
    latest_health_score?: number;
    latest_status?: SensorStatus;
    latest_analysis_timestamp?: string | null;
}

export interface SensorCreate {
    name: string;
    location: string;
    source_type: SourceType;
    organization_id?: number;
}

// ========================================
// Analysis Types
// ========================================

export interface AnalysisMetrics {
    bias: number;
    slope: number;
    noise_std: number;
    snr_db: number;
    hysteresis: number;
    hysteresis_x: number[];
    hysteresis_y: number[];
    hurst: number;
    hurst_r2: number;
    dfa_scales: number[];
    dfa_fluctuations: number[];
    timestamps?: string[];
    trend?: number[];
    residuals?: number[];
}

export interface AnalysisResult {
    sensor_id: string;
    timestamp: string;
    health_score: number;
    status: SensorStatus;
    diagnosis: string;
    metrics: AnalysisMetrics;
    flags: string[];
    recommendation: string;
    prediction?: string;
}

export interface SensorDataInput {
    sensor_id: string;
    sensor_type?: string;
    values?: number[];
    timestamps?: string[];
    config?: {
        window_size?: number;
        start_date?: string;
        end_date?: string;
        [key: string]: any;
    };
}

// ========================================
// Synthetic Data Types
// ========================================

export type SyntheticDataType = 'Normal' | 'Drifting' | 'Noisy' | 'Oscillation';

export interface SyntheticRequest {
    type: SyntheticDataType;
    length: number;
}

export interface SyntheticResponse {
    data: number[];
    timestamps: number[];
    type: SyntheticDataType;
    length: number;
}

// ========================================
// Report Types
// ========================================

export interface ReportRequest {
    sensor_id: string;
    health_score: number;
    diagnosis: string;
    metrics: AnalysisMetrics;
    flags: string[];
    recommendation: string;
    data?: number[];
}

// ========================================
// API Response Types
// ========================================

export interface ApiError {
    detail: string;
}

export interface HealthCheckResponse {
    status: string;
    service: string;
    version: string;
}

export interface UploadResponse {
    message: string;
    count: number;
}

export interface StreamDataResponse {
    status: string;
    sensor_id: string;
    timestamp: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    size: number;
    pages: number;
}
