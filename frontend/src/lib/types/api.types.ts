/**
 * Type definitions for API-related types.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  error?: string;
  message?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface QueryParams {
  page?: number;
  limit?: number;
  [key: string]: string | number | undefined;
}

