/**
 * API endpoint constants.
 * Centralized definition of all API endpoints.
 * 
 * Uses relative paths which will be proxied by Next.js rewrites.
 * The rewrites in next.config.mjs will proxy /api/* to the actual backend URL
 * configured via NEXT_PUBLIC_API_URL or API_URL environment variable at runtime.
 */

// Use relative paths - Next.js rewrites will handle the proxying
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

