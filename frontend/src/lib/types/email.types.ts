export type EmailStatus = 'queued' | 'sent' | 'failed' | 'delivered' | 'opened' | 'clicked' | 'bounced';

export interface Email {
  id: number;
  agent_id: number;
  task_id: number;
  client_id: number;
  to_email: string;
  subject: string;
  body: string;
  status: EmailStatus;
  sendgrid_message_id?: string;
  created_at: string;
  sent_at?: string;
  opened_at?: string;
  clicked_at?: string;
  error_message?: string;
  webhook_events?: any[];
  from_name?: string;
  from_email?: string;
}

export interface EmailPreviewRequest {
  client_id: number;
  task_id: number;
  agent_instructions?: string;
}

export interface EmailSendRequest {
  client_id: number;
  task_id: number;
  to_email: string;
  subject: string;
  body: string;
  agent_instructions?: string;
}

export interface EmailPreviewResponse {
  subject: string;
  body: string;
  preview: string;
}
