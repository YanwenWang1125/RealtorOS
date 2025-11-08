import { EmailStatus } from '@/lib/types/email.types';

export const EMAIL_STATUSES: EmailStatus[] = [
  'queued',
  'sent',
  'failed',
  'delivered',
  'opened',
  'clicked',
  'bounced'
];

export const EMAIL_STATUS_LABELS: Record<EmailStatus, string> = {
  queued: 'Queued',
  sent: 'Sent',
  failed: 'Failed',
  delivered: 'Delivered',
  opened: 'Opened',
  clicked: 'Clicked',
  bounced: 'Bounced'
};

export const EMAIL_STATUS_COLORS: Record<EmailStatus, string> = {
  queued: 'bg-yellow-100 text-yellow-700',
  sent: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  delivered: 'bg-blue-100 text-blue-700',
  opened: 'bg-purple-100 text-purple-700',
  clicked: 'bg-indigo-100 text-indigo-700',
  bounced: 'bg-orange-100 text-orange-700'
};
