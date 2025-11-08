/**
 * API endpoint constants.
 * Centralized definition of all API endpoints.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Clients
  CLIENTS: {
    BASE: `${API_BASE}/api/clients/`,
    BY_ID: (id: number) => `${API_BASE}/api/clients/${id}`,
    TASKS: (id: number) => `${API_BASE}/api/clients/${id}/tasks`,
  },
  
  // Tasks
  TASKS: {
    BASE: `${API_BASE}/api/tasks`,
    BY_ID: (id: number) => `${API_BASE}/api/tasks/${id}`,
  },
  
  // Emails
  EMAILS: {
    BASE: `${API_BASE}/api/emails`,
    BY_ID: (id: number) => `${API_BASE}/api/emails/${id}`,
    PREVIEW: `${API_BASE}/api/emails/preview`,
    SEND: `${API_BASE}/api/emails/send`,
  },
  
  // Dashboard
  DASHBOARD: {
    STATS: `${API_BASE}/api/dashboard/stats`,
    RECENT_ACTIVITY: `${API_BASE}/api/dashboard/recent-activity`,
  },
  
  // Health
  HEALTH: `${API_BASE}/health`,
} as const;

