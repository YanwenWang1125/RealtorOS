export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  CLIENTS: '/clients',
  CLIENT_NEW: '/clients/new',
  CLIENT_DETAIL: (id: number | string) => `/clients/${id}`,
  CLIENT_EDIT: (id: number | string) => `/clients/${id}/edit`,
  TASKS: '/tasks',
  TASK_DETAIL: (id: number | string) => `/tasks/${id}`,
  EMAILS: '/emails',
  EMAIL_DETAIL: (id: number | string) => `/emails/${id}`,
  ANALYTICS: '/analytics',
  LOGIN: '/login',
  REGISTER: '/register'
} as const;
