import axios, { AxiosError } from 'axios';
import { useAuthStore } from '@/store/useAuthStore';

// Use environment variable directly to avoid CORS redirect issues
// Next.js rewrites can cause HTTP->HTTPS redirects which break CORS preflight
// By using the HTTPS URL directly, we avoid redirect issues
const getApiBaseUrl = () => {
  // Get the API URL from environment
  const envUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
  
  // In browser, use HTTPS URL directly if available (avoids CORS redirect issues)
  // Fall back to relative path /api which will be proxied by Next.js rewrites
  if (typeof window !== 'undefined') {
    if (envUrl && envUrl.startsWith('https://')) {
      // Use HTTPS URL directly - avoids proxy redirect issues
      console.log('🌐 Browser: Using HTTPS URL directly:', envUrl);
      return envUrl;
    }
    // Fallback to relative path - will be proxied by Next.js rewrites
    // This is the expected behavior when NEXT_PUBLIC_API_URL is not set at build time
    console.log('🌐 Browser: Using relative path /api (will be proxied by Next.js)');
    console.log(`   NEXT_PUBLIC_API_URL: ${envUrl || 'NOT SET (using proxy)'}`);
    return '/api';
  }
  
  // On server side, use environment variable, fallback to relative path
  const serverUrl = envUrl || '/api';
  if (process.env.NODE_ENV !== 'production') {
    console.log('🖥️  Server: Axios baseURL =', serverUrl);
  }
  return serverUrl;
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
const getServiceUrl = (serviceEnvVar: string | undefined) => {
  const mainApiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL;
  
  if (typeof window !== 'undefined') {
    // In browser, use HTTPS URL directly if available (avoids CORS redirect issues)
    // Use service-specific URL if provided, otherwise use main API URL
    const urlToUse = serviceEnvVar || mainApiUrl;
    
    if (urlToUse && urlToUse.startsWith('https://')) {
      // Use HTTPS URL directly
      if (process.env.NODE_ENV !== 'production') {
        console.log(`🌐 Browser: Service URL (${serviceEnvVar ? 'custom' : 'default'}) =`, urlToUse);
      }
      return urlToUse;
    }
    
    // Fallback to relative path for local dev
    return '/api';
  }
  
  // On server side, use environment variable if available, otherwise fallback to /api
  const serverUrl = serviceEnvVar || mainApiUrl || '/api';
  if (process.env.NODE_ENV !== 'production' && serviceEnvVar) {
    console.log(`🖥️  Server: Service URL (${serviceEnvVar ? 'custom' : 'default'}) =`, serverUrl);
  }
  return serverUrl;
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
