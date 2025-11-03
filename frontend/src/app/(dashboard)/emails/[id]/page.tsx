'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEmail } from '@/lib/hooks/queries/useEmails';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useTask } from '@/lib/hooks/queries/useTasks';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/skeleton';
import { EmailStatusBadge } from '@/components/emails/EmailStatusBadge';
import { EmailBodyRenderer } from '@/components/emails/EmailBodyRenderer';
import { EmailEngagementTimeline } from '@/components/emails/EmailEngagementTimeline';
import { EmailWebhookLog } from '@/components/emails/EmailWebhookLog';
import { formatDateTime } from '@/lib/utils/format';
import { ArrowLeft, User, Calendar } from 'lucide-react';
import Link from 'next/link';

export default function EmailDetailPage() {
  const params = useParams();
  const router = useRouter();
  const emailId = parseInt(params.id as string);

  // Poll for engagement updates every 10 seconds
  const { data: email, isLoading } = useEmail(emailId, {
    refetchInterval: (data) => {
      // Stop polling if opened or email is older than 24 hours
      if (!data) return false;
      if (data.opened_at) return false;

      const sentAt = data.sent_at ? new Date(data.sent_at) : null;
      if (sentAt && (Date.now() - sentAt.getTime()) > 24 * 60 * 60 * 1000) {
        return false;
      }

      return 10000; // Poll every 10 seconds
    }
  });

  const { data: client } = useClient(email?.client_id || 0, { enabled: !!email });
  const { data: task } = useTask(email?.task_id || 0, { enabled: !!email?.task_id });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!email) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Email not found</h2>
        <Button onClick={() => router.push('/emails')} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Emails
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Button variant="outline" onClick={() => router.push('/emails')}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Back to Emails
      </Button>

      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">{email.subject}</h1>
        <div className="flex gap-4 mt-2 text-muted-foreground">
          <span>To: {email.to_email}</span>
          <span>•</span>
          <span>{email.sent_at ? formatDateTime(email.sent_at) : 'Not sent yet'}</span>
          <span>•</span>
          <EmailStatusBadge status={email.status} />
        </div>
      </div>

      {/* Breadcrumbs */}
      <div className="flex gap-2 text-sm text-muted-foreground">
        {client && (
          <>
            <Link href={`/clients/${client.id}`} className="hover:underline">
              {client.name}
            </Link>
            <span>→</span>
          </>
        )}
        {task && (
          <>
            <Link href={`/tasks/${task.id}`} className="hover:underline">
              {task.followup_type}
            </Link>
            <span>→</span>
          </>
        )}
        <span>Email</span>
      </div>

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
        {client && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <User className="h-5 w-5" />
                Client
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Link
                href={`/clients/${client.id}`}
                className="font-medium hover:underline block"
              >
                {client.name}
              </Link>
              <p className="text-sm text-muted-foreground mt-1">{client.email}</p>
              <p className="text-sm text-muted-foreground">{client.property_address}</p>
              <p className="text-sm text-muted-foreground mt-2">Stage: {client.stage}</p>
            </CardContent>
          </Card>
        )}

        {/* Task Card */}
        {task && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Related Task
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Link
                href={`/tasks/${task.id}`}
                className="font-medium hover:underline block"
              >
                {task.followup_type}
              </Link>
              <p className="text-sm text-muted-foreground mt-1">
                Scheduled: {formatDateTime(task.scheduled_for)}
              </p>
              <p className="text-sm text-muted-foreground">Status: {task.status}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Webhook Events Log */}
      <EmailWebhookLog email={email} />
    </div>
  );
}
