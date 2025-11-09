import axios, { AxiosError } from 'axios';
import { useAuthStore } from '@/store/useAuthStore';

// Use relative path /api which will be proxied by Next.js rewrites
// This allows the backend URL to be configured at runtime via environment variables
// The rewrites in next.config.mjs will proxy /api/* to the actual backend URL
const getApiBaseUrl = () => {
  // In browser, use relative path (will be proxied by Next.js)
  if (typeof window !== 'undefined') {
    return '/api';
  }
  // On server side, try to use environment variable, fallback to relative path
  return process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || '/api';
};

export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Helper function to get service URL
const getServiceUrl = (serviceEnvVar: string | undefined) => {
  if (typeof window !== 'undefined') {
    // In browser, use relative path (will be proxied by Next.js)
    return serviceEnvVar ? `/api` : '/api';
  }
  // On server side, use environment variable if available, otherwise fallback to /api
  return serviceEnvVar || process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || '/api';
};

// CRM service client - uses CRM URL if available (for microservices), otherwise falls back to API URL
export const crmClient = axios.create({
  baseURL: getServiceUrl(process.env.NEXT_PUBLIC_CRM_URL),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Task service client - uses Task URL if available (for microservices), otherwise falls back to API URL
export const taskClient = axios.create({
  baseURL: getServiceUrl(process.env.NEXT_PUBLIC_TASK_URL),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Email service client - uses Email URL if available (for microservices), otherwise falls back to API URL
export const emailClient = axios.create({
  baseURL: getServiceUrl(process.env.NEXT_PUBLIC_EMAIL_URL),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Analytics service client - uses Analytics URL if available (for microservices), otherwise falls back to API URL
export const analyticsClient = axios.create({
  baseURL: getServiceUrl(process.env.NEXT_PUBLIC_ANALYTICS_URL),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for auth tokens
const requestInterceptor = (config: any) => {
  // Get token from auth store
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

apiClient.interceptors.request.use(requestInterceptor, (error) => {
  return Promise.reject(error);
});

// Apply same interceptor to all service clients
crmClient.interceptors.request.use(requestInterceptor, (error) => {
  return Promise.reject(error);
});

taskClient.interceptors.request.use(requestInterceptor, (error) => {
  return Promise.reject(error);
});

emailClient.interceptors.request.use(requestInterceptor, (error) => {
  return Promise.reject(error);
});

analyticsClient.interceptors.request.use(requestInterceptor, (error) => {
  return Promise.reject(error);
});

// Response interceptor for error handling
const responseInterceptor = (response: any) => response;
const responseErrorInterceptor = (err: unknown) => {
  // Be defensive: errors aren't always AxiosError
  if (axios.isAxiosError(err)) {
    const status = err.response?.status;
    // Avoid logging huge/circular payloads
    const detail = ((): unknown => {
      const data = err.response?.data as any;
      if (!data) return undefined;
      if (typeof data === 'string') return data;
      if (typeof data?.detail === 'string') return data.detail;
      try {
        return JSON.stringify(data);
      } catch {
        return '[non-serializable error payload]';
      }
    })();

    // Handle authentication errors
    if (status === 401 || status === 403) {
      // Clear auth store and redirect to login
      useAuthStore.getState().logout();
      // Only redirect if we're on the client side
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }

    // Don't log 404 errors - they're expected when resources don't exist
    // and are handled gracefully by the UI
    if (status === 404) {
      // Silently reject - UI will handle the "not found" state
      return Promise.reject(err);
    }

    // Log other errors
    if (status) {
      console.error('API Error:', status, detail ?? err.message);
    } else if (err.request) {
      console.error('Network Error:', err.message);
    } else {
      console.error('Request Error:', err.message);
    }
    return Promise.reject(err);
  }

  // Unknown error shape
  console.error('Unexpected Error:', err);
  return Promise.reject(err);
};

apiClient.interceptors.response.use(responseInterceptor, responseErrorInterceptor);
// Apply same interceptor to all service clients
crmClient.interceptors.response.use(responseInterceptor, responseErrorInterceptor);
taskClient.interceptors.response.use(responseInterceptor, responseErrorInterceptor);
emailClient.interceptors.response.use(responseInterceptor, responseErrorInterceptor);
analyticsClient.interceptors.response.use(responseInterceptor, responseErrorInterceptor);
