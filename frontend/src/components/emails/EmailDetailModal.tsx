'use client';

import { Email } from '@/lib/types/email.types';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useTask } from '@/lib/hooks/queries/useTasks';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/skeleton';
import { EmailStatusBadge } from '@/components/emails/EmailStatusBadge';
import { EmailBodyRenderer } from '@/components/emails/EmailBodyRenderer';
import { EmailEngagementTimeline } from '@/components/emails/EmailEngagementTimeline';
import { EmailWebhookLog } from '@/components/emails/EmailWebhookLog';
import { formatDateTime } from '@/lib/utils/format';
import { User, Calendar, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Link from 'next/link';

interface EmailDetailModalProps {
  email: Email;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function EmailDetailModal({ email, open, onOpenChange }: EmailDetailModalProps) {
  const { data: client, isLoading: clientLoading } = useClient(
    email.client_id,
    { enabled: !!email.client_id }
  );
  const { data: task, isLoading: taskLoading } = useTask(
    email.task_id || 0,
    { enabled: !!email.task_id }
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div>
            <DialogTitle className="text-2xl">{email.subject}</DialogTitle>
            <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
              <span>To: {email.to_email}</span>
              <span>•</span>
              <span>{email.sent_at ? formatDateTime(email.sent_at) : 'Not sent yet'}</span>
              <span>•</span>
              <EmailStatusBadge status={email.status} />
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Error Message Alert */}
          {email.status === 'failed' && email.error_message && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>Send Failed:</strong> {email.error_message}
                {email.error_message.includes('MessageRejected') && (
                  <div className="mt-2 text-sm">
                    <p className="font-semibold">This is likely due to AWS SES Sandbox Mode restrictions.</p>
                    <p className="mt-1">In sandbox mode, you can only send emails to verified recipient addresses.</p>
                    <p className="mt-1">To fix this:</p>
                    <ul className="list-disc list-inside mt-1 space-y-1">
                      <li>Verify the recipient email address in AWS SES Console, or</li>
                      <li>Request production access from AWS SES to send to any email address</li>
                    </ul>
                  </div>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Engagement Timeline */}
          <EmailEngagementTimeline email={email} />

          {/* Email Body */}
          <Card>
            <CardHeader>
              <CardTitle>Email Content</CardTitle>
            </CardHeader>
            <CardContent>
              <EmailBodyRenderer body={email.body} />
            </CardContent>
          </Card>

          {/* Related Items */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Client Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Client
                </CardTitle>
              </CardHeader>
              <CardContent>
                {clientLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : client ? (
                  <div className="space-y-2">
                    <Link
                      href={`/clients/${client.id}`}
                      className="font-medium hover:underline block"
                    >
                      {client.name}
                    </Link>
                    <p className="text-sm text-muted-foreground">{client.email}</p>
                    <p className="text-sm text-muted-foreground">{client.property_address}</p>
                    <p className="text-sm text-muted-foreground mt-2">Stage: {client.stage}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Client not found</p>
                )}
              </CardContent>
            </Card>

            {/* Task Card */}
            {email.task_id && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Related Task
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {taskLoading ? (
                    <Skeleton className="h-20 w-full" />
                  ) : task ? (
                    <div className="space-y-2">
                      <Link
                        href={`/tasks/${task.id}`}
                        className="font-medium hover:underline block"
                      >
                        {task.followup_type}
                      </Link>
                      <p className="text-sm text-muted-foreground">
                        Scheduled: {formatDateTime(task.scheduled_for)}
                      </p>
                      <p className="text-sm text-muted-foreground">Status: {task.status}</p>
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">Task not found</p>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Webhook Events Log */}
          <EmailWebhookLog email={email} />
        </div>
      </DialogContent>
    </Dialog>
  );
}

