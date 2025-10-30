/**
 * Task type definitions for RealtorOS.
 * 
 * This module defines TypeScript types for task-related
 * data structures in the RealtorOS application.
 */

export interface Task {
  id: string
  client_id: string
  followup_type: 'Day 1' | 'Day 3' | 'Week 1' | 'Week 2' | 'Month 1' | 'Custom'
  scheduled_for: string
  status: 'pending' | 'completed' | 'skipped' | 'cancelled'
  email_sent_id?: string
  created_at: string
  updated_at: string
  completed_at?: string
  notes?: string
  priority: 'high' | 'medium' | 'low'
}

export interface TaskCreate {
  client_id: string
  followup_type: 'Day 1' | 'Day 3' | 'Week 1' | 'Week 2' | 'Month 1' | 'Custom'
  scheduled_for: string
  notes?: string
  priority: 'high' | 'medium' | 'low'
}

export interface TaskUpdate {
  status?: 'pending' | 'completed' | 'skipped' | 'cancelled'
  scheduled_for?: string
  notes?: string
  priority?: 'high' | 'medium' | 'low'
}
