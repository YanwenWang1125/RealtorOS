import axios, { AxiosError } from 'axios';
import { useAuthStore } from '@/store/useAuthStore';

// Use environment variable directly - no proxy layer
// NEXT_PUBLIC_API_URL must be set at build time for browser code
// API_URL can be used at runtime for server-side code
const getApiBaseUrl = () => {
  // Get the API URL from environment
  const envUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
  
  // Require API URL to be set - no fallback to /api
  if (!envUrl) {
    const errorMsg = typeof window !== 'undefined'
      ? '❌ ERROR: NEXT_PUBLIC_API_URL environment variable is required. Please set it at build time or ensure it is available in the browser.'
      : '❌ ERROR: NEXT_PUBLIC_API_URL or API_URL environment variable is required for server-side requests.';
    
    console.error(errorMsg);
    console.error(`   NEXT_PUBLIC_API_URL: ${process.env.NEXT_PUBLIC_API_URL || 'NOT SET'}`);
    console.error(`   API_URL: ${process.env.API_URL || 'NOT SET'}`);
    throw new Error(errorMsg);
  }
  
  // Ensure HTTPS is used (not HTTP) to avoid CORS issues
  let apiUrl = envUrl;
  if (apiUrl.startsWith('http://') && !apiUrl.includes('localhost')) {
    apiUrl = apiUrl.replace('http://', 'https://');
    console.warn('⚠️  Converted HTTP to HTTPS:', apiUrl);
  }
  
  // Validate URL format
  try {
    new URL(apiUrl);
  } catch (e) {
    const errorMsg = `❌ ERROR: Invalid API URL format: ${apiUrl}`;
    console.error(errorMsg);
    throw new Error(errorMsg);
  }
  
  if (typeof window !== 'undefined') {
    console.log('🌐 Browser: Using API URL directly:', apiUrl);
  } else if (process.env.NODE_ENV !== 'production') {
    console.log('🖥️  Server: Using API URL:', apiUrl);
  }
  
  return apiUrl;
};

const apiBaseUrl = getApiBaseUrl();
export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Log the actual baseURL being used (development only)
if (process.env.NODE_ENV !== 'production' && typeof window === 'undefined') {
  console.log('📡 apiClient baseURL:', apiBaseUrl);
}

// Helper function to get service URL
// Uses service-specific URL if provided, otherwise falls back to main API URL
const getServiceUrl = (serviceEnvVar: string | undefined) => {
  const mainApiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
  const urlToUse = serviceEnvVar || mainApiUrl;
  
  // Require URL to be set - no fallback
  if (!urlToUse) {
    const errorMsg = serviceEnvVar
      ? `❌ ERROR: ${serviceEnvVar} environment variable is required.`
      : '❌ ERROR: NEXT_PUBLIC_API_URL or API_URL environment variable is required.';
    console.error(errorMsg);
    throw new Error(errorMsg);
  }
  
  // Ensure HTTPS is used (not HTTP) to avoid CORS issues
  let finalUrl = urlToUse;
  if (finalUrl.startsWith('http://') && !finalUrl.includes('localhost')) {
    finalUrl = finalUrl.replace('http://', 'https://');
    console.warn('⚠️  Converted HTTP to HTTPS:', finalUrl);
  }
  
  // Validate URL format
  try {
    new URL(finalUrl);
  } catch (e) {
    const errorMsg = `❌ ERROR: Invalid service URL format: ${finalUrl}`;
    console.error(errorMsg);
    throw new Error(errorMsg);
  }
  
  if (process.env.NODE_ENV !== 'production') {
    if (typeof window !== 'undefined') {
      console.log(`🌐 Browser: Service URL (${serviceEnvVar ? 'custom' : 'default'}) =`, finalUrl);
    } else {
      console.log(`🖥️  Server: Service URL (${serviceEnvVar ? 'custom' : 'default'}) =`, finalUrl);
    }
  }
  
  return finalUrl;
};

// CRM service client - uses CRM URL if available (for microservices), otherwise falls back to API URL
const crmBaseUrl = getServiceUrl(process.env.NEXT_PUBLIC_CRM_URL);
export const crmClient = axios.create({
  baseURL: crmBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Log the actual baseURL being used (development only)
if (process.env.NODE_ENV !== 'production' && typeof window === 'undefined') {
  console.log('📡 crmClient baseURL:', crmBaseUrl);
}

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
