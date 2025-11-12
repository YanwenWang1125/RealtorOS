import { emailClient } from '../client';
import { Email, EmailPreviewRequest, EmailSendRequest, EmailPreviewResponse } from '@/lib/types/email.types';
import { getApiPath } from '../utils/path';

export const emailsApi = {
  list: async (params?: { page?: number; limit?: number; client_id?: number; status?: string }) => {
    // Backend route is "/api/emails/" (with trailing slash), so we need trailing slash to avoid 301 redirect
    const path = getApiPath(emailClient.defaults.baseURL, '/emails/');
    const { data } = await emailClient.get<Email[]>(path, { params });
    return data;
  },

  getById: async (id: number) => {
    const path = getApiPath(emailClient.defaults.baseURL, `/emails/${id}`);
    const { data } = await emailClient.get<Email>(path);
    return data;
  },

  preview: async (request: EmailPreviewRequest) => {
    const path = getApiPath(emailClient.defaults.baseURL, '/emails/preview');
    const { data } = await emailClient.post<EmailPreviewResponse>(path, request);
    return data;
  },

  send: async (request: EmailSendRequest) => {
    const path = getApiPath(emailClient.defaults.baseURL, '/emails/send');
    const { data } = await emailClient.post<Email>(path, request);
    return data;
  },

  delete: async (id: number) => {
    const path = getApiPath(emailClient.defaults.baseURL, `/emails/${id}`);
    const { data } = await emailClient.delete<{ success: boolean }>(path);
    return data;
  },

  bulkDelete: async (ids: number[]) => {
    const path = getApiPath(emailClient.defaults.baseURL, '/emails/bulk');
    const { data } = await emailClient.delete<{ success: boolean; deleted_count: number; failed_ids: number[]; total_requested: number }>(path, {
      data: { ids }
    });
    return data;
  },
};
