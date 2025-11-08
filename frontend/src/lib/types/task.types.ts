export type TaskStatus = 'pending' | 'completed' | 'skipped' | 'cancelled';

export type FollowupType = 'Day 1' | 'Day 3' | 'Week 1' | 'Week 2' | 'Month 1' | 'Custom';

export type Priority = 'high' | 'medium' | 'low';

export interface EmailPreview {
  subject: string;
  body: string;
  custom_instructions?: string;
  timestamp?: number;
}

export interface Task {
  id: number;
  agent_id: number;
  client_id: number;
  followup_type: FollowupType;
  scheduled_for: string;
  status: TaskStatus;
  priority: Priority;
  notes?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  email_sent_id?: number;
  email_preview?: EmailPreview;
}

export interface TaskCreate {
  client_id: number;
  followup_type: FollowupType;
  scheduled_for: string;
  notes?: string;
  priority: Priority;
}

export interface TaskUpdate {
  status?: TaskStatus;
  scheduled_for?: string;
  notes?: string;
  priority?: Priority;
  email_preview?: EmailPreview;
}
