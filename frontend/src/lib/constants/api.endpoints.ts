/**
 * API endpoint constants.
 * Centralized definition of all API endpoints.
 * 
 * These are relative paths that will be combined with the full backend URL
 * from NEXT_PUBLIC_API_URL or API_URL environment variable.
 * The frontend now uses direct HTTPS connections (no proxy layer).
 */

// API base path - will be combined with full backend URL from environment variable
const API_BASE = '/api';

export const API_ENDPOINTS = {
  // Clients
  CLIENTS: {
    BASE: `${API_BASE}/clients/`,
    BY_ID: (id: number) => `${API_BASE}/clients/${id}`,
    TASKS: (id: number) => `${API_BASE}/clients/${id}/tasks`,
  },
  
  // Tasks
  TASKS: {
    BASE: `${API_BASE}/tasks`,
    BY_ID: (id: number) => `${API_BASE}/tasks/${id}`,
  },
  
  // Emails
  EMAILS: {
    BASE: `${API_BASE}/emails`,
    BY_ID: (id: number) => `${API_BASE}/emails/${id}`,
    PREVIEW: `${API_BASE}/emails/preview`,
    SEND: `${API_BASE}/emails/send`,
  },
  
  // Dashboard
  DASHBOARD: {
    STATS: `${API_BASE}/dashboard/stats`,
    RECENT_ACTIVITY: `${API_BASE}/dashboard/recent-activity`,
  },
  
  // Health
  HEALTH: '/health',
} as const;

