import { emailClient } from '../client';
import { Email, EmailPreviewRequest, EmailSendRequest, EmailPreviewResponse } from '@/lib/types/email.types';

export const emailsApi = {
  list: async (params?: { page?: number; limit?: number; client_id?: number; status?: string }) => {
    const { data } = await emailClient.get<Email[]>('/api/emails', { params });
    return data;
  },

  getById: async (id: number) => {
    const { data } = await emailClient.get<Email>(`/api/emails/${id}`);
    return data;
  },

  preview: async (request: EmailPreviewRequest) => {
    const { data } = await emailClient.post<EmailPreviewResponse>('/api/emails/preview', request);
    return data;
  },

  send: async (request: EmailSendRequest) => {
    const { data } = await emailClient.post<Email>('/api/emails/send', request);
    return data;
  },
};
