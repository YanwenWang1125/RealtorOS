export interface DashboardStats {
  total_clients: number;
  active_clients: number;
  pending_tasks: number;
  completed_tasks: number;
  emails_sent_today: number;
  emails_sent_this_week: number;
  open_rate: number;
  click_rate: number;
  conversion_rate: number;
}

export interface ActivityItem {
  id: string;
  type: 'client_created' | 'task_completed' | 'email_sent' | 'email_opened' | 'email_clicked';
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}
