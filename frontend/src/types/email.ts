/**
 * Email type definitions for RealtorOS.
 * 
 * This module defines TypeScript types for email-related
 * data structures in the RealtorOS application.
 */

export interface Email {
  id: string
  task_id: string
  client_id: string
  to_email: string
  subject: string
  body: string
  status: 'queued' | 'sent' | 'delivered' | 'opened' | 'clicked' | 'failed' | 'bounced'
  sendgrid_message_id?: string
  created_at: string
  sent_at?: string
  opened_at?: string
  clicked_at?: string
  error_message?: string
}

export interface EmailPreviewRequest {
  client_id: string
  task_id: string
  agent_instructions?: string
}

export interface EmailSendRequest {
  client_id: string
  task_id: string
  agent_instructions?: string
}
