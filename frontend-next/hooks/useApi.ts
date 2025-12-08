/**
 * useApi Hook
 * 
 * Generic hook for making API calls with loading state,
 * error handling, and toast notifications.
 * 
 * @module hooks/useApi
 */

'use client';

import { useState, useCallback } from 'react';
import type { ApiError, HttpError } from '@/types/api';
import { isHttpError } from '@/types/api';

// ============================================================================
// Types
// ============================================================================

/** API call state */
export interface ApiState<T> {
    data: T | null;
    loading: boolean;
    error: ApiError | null;
}

/** API call options */
export interface UseApiOptions {
    /** Show toast notification on error (default: true) */
    showErrorToast?: boolean;
    /** Show toast notification on success (default: false) */
    showSuccessToast?: boolean;
    /** Success message for toast */
    successMessage?: string;
    /** Custom error message (overrides API error) */
    errorMessage?: string;
    /** Reset data on new request (default: false) */
    resetOnRequest?: boolean;
}

/** API function that returns a promise */
export type ApiFn<TData, TParams extends unknown[]> = (...args: TParams) => Promise<TData>;

/** Return type for useApi hook */
export interface UseApiReturn<TData, TParams extends unknown[]> {
    data: TData | null;
    loading: boolean;
    error: ApiError | null;
    execute: (...args: TParams) => Promise<TData | null>;
    reset: () => void;
    setData: (data: TData | null) => void;
}

// ============================================================================
// Toast Notification (Simple Implementation)
// ============================================================================

/** Toast notification type */
type ToastType = 'success' | 'error' | 'warning' | 'info';

/**
 * Show toast notification.
 * Replace with your toast library (react-hot-toast, sonner, etc.)
 */
function showToast(message: string, type: ToastType): void {
    // Simple implementation using console and alert
    // TODO: Replace with proper toast library
    const prefix = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️',
    }[type];

    console.log(`[Toast ${type}] ${message}`);

    // For critical errors, show alert as fallback
    if (type === 'error' && typeof window !== 'undefined') {
        // Use a timeout to not block execution
        setTimeout(() => {
            // Check if document has a toast container, otherwise use console
            const toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                console.error(`${prefix} ${message}`);
            }
        }, 0);
    }
}

// ============================================================================
// useApi Hook
// ============================================================================

/**
 * Generic hook for API calls with state management and error handling.
 * 
 * @param apiFn - The API function to call
 * @param options - Hook options
 * @returns Object with data, loading, error, and execute function
 * 
 * @example
 * ```tsx
 * const { data, loading, error, execute } = useApi(
 *   (id: string) => api.getSensor(id),
 *   { showErrorToast: true }
 * );
 * 
 * // Call the API
 * const sensor = await execute('sensor-123');
 * ```
 */
export function useApi<TData, TParams extends unknown[]>(
    apiFn: ApiFn<TData, TParams>,
    options: UseApiOptions = {}
): UseApiReturn<TData, TParams> {
    const {
        showErrorToast = true,
        showSuccessToast = false,
        successMessage,
        errorMessage,
        resetOnRequest = false,
    } = options;

    const [state, setState] = useState<ApiState<TData>>({
        data: null,
        loading: false,
        error: null,
    });

    /**
     * Execute the API call.
     */
    const execute = useCallback(
        async (...args: TParams): Promise<TData | null> => {
            setState((prev) => ({
                data: resetOnRequest ? null : prev.data,
                loading: true,
                error: null,
            }));

            try {
                const result = await apiFn(...args);

                setState({
                    data: result,
                    loading: false,
                    error: null,
                });

                if (showSuccessToast && successMessage) {
                    showToast(successMessage, 'success');
                }

                return result;
            } catch (error) {
                const apiError = parseError(error, errorMessage);

                setState((prev) => ({
                    data: prev.data,
                    loading: false,
                    error: apiError,
                }));

                if (showErrorToast) {
                    showToast(apiError.message, 'error');
                }

                return null;
            }
        },
        [apiFn, showErrorToast, showSuccessToast, successMessage, errorMessage, resetOnRequest]
    );

    /**
     * Reset state to initial values.
     */
    const reset = useCallback(() => {
        setState({
            data: null,
            loading: false,
            error: null,
        });
    }, []);

    /**
     * Manually set data (useful for optimistic updates).
     */
    const setData = useCallback((data: TData | null) => {
        setState((prev) => ({
            ...prev,
            data,
        }));
    }, []);

    return {
        data: state.data,
        loading: state.loading,
        error: state.error,
        execute,
        reset,
        setData,
    };
}

// ============================================================================
// useMutation Hook
// ============================================================================

/**
 * Hook optimized for mutation operations (POST, PUT, DELETE).
 * Similar to useApi but with different defaults.
 * 
 * @example
 * ```tsx
 * const { execute, loading } = useMutation(
 *   (data: CreateSensorRequest) => api.createSensor(data),
 *   { successMessage: 'Sensor created successfully' }
 * );
 * ```
 */
export function useMutation<TData, TParams extends unknown[]>(
    mutationFn: ApiFn<TData, TParams>,
    options: UseApiOptions = {}
): UseApiReturn<TData, TParams> {
    return useApi(mutationFn, {
        showErrorToast: true,
        showSuccessToast: true,
        resetOnRequest: true,
        ...options,
    });
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Parse unknown error to standardized ApiError.
 */
function parseError(error: unknown, customMessage?: string): ApiError {
    // Default error
    const defaultError: ApiError = {
        status: 500,
        message: customMessage || 'An unexpected error occurred',
    };

    if (!error) {
        return defaultError;
    }

    // Handle HttpError from api-client
    if (isHttpError(error)) {
        return {
            status: error.status,
            message: customMessage || error.data?.message || error.message,
            detail: error.data?.detail,
            errors: error.data?.errors,
        };
    }

    // Handle standard Error
    if (error instanceof Error) {
        return {
            status: 500,
            message: customMessage || error.message,
        };
    }

    // Handle plain object
    if (typeof error === 'object' && error !== null) {
        const errObj = error as Record<string, unknown>;
        return {
            status: (errObj.status as number) || 500,
            message: customMessage || String(errObj.message || defaultError.message),
            detail: errObj.detail as string | undefined,
        };
    }

    // Handle string
    if (typeof error === 'string') {
        return {
            status: 500,
            message: customMessage || error,
        };
    }

    return defaultError;
}

/**
 * Format validation errors for display.
 */
export function formatValidationErrors(error: ApiError): string[] {
    if (!error.errors || error.errors.length === 0) {
        return [error.message];
    }

    return error.errors.map((err) => {
        const field = err.loc.slice(1).join('.');
        return field ? `${field}: ${err.msg}` : err.msg;
    });
}
