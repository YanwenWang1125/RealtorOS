import { TaskStatus, FollowupType, Priority } from '@/lib/types/task.types';

export const TASK_STATUSES: TaskStatus[] = [
  'pending',
  'completed',
  'skipped',
  'cancelled'
];

export const FOLLOWUP_TYPES: FollowupType[] = [
  'Day 1',
  'Day 3',
  'Week 1',
  'Week 2',
  'Month 1',
  'Custom'
];

export const PRIORITY_LEVELS: Priority[] = ['high', 'medium', 'low'];

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  pending: 'Pending',
  completed: 'Completed',
  skipped: 'Skipped',
  cancelled: 'Cancelled'
};

export const PRIORITY_LABELS: Record<Priority, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low'
};

export const TASK_STATUS_COLORS: Record<TaskStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  skipped: 'bg-gray-100 text-gray-800',
  cancelled: 'bg-red-100 text-red-800'
};

export const PRIORITY_COLORS: Record<Priority, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-yellow-100 text-yellow-700',
  low: 'bg-green-100 text-green-700'
};
