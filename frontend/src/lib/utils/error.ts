/**
 * Error handling utility functions.
 */

import { ApiError } from '@/lib/types';

/**
 * Extract error message from API error response.
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'object' && error !== null) {
    const apiError = error as ApiError;
    return apiError.detail || apiError.error || apiError.message || 'An unexpected error occurred';
  }
  
  return 'An unexpected error occurred';
}

/**
 * Check if error is an API error.
 */
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    ('detail' in error || 'error' in error || 'message' in error)
  );
}

