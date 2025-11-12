'use client';

import { useState } from 'react';
import { Task } from '@/lib/types/task.types';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useEmail } from '@/lib/hooks/queries/useEmails';
import { useTask } from '@/lib/hooks/queries/useTasks';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/skeleton';
import { TaskStatusBadge } from '@/components/tasks/TaskStatusBadge';
import { TaskPriorityBadge } from '@/components/tasks/TaskPriorityBadge';
import { TaskActionsMenu } from '@/components/tasks/TaskActionsMenu';
import { EmailPreviewModal } from '@/components/emails/EmailPreviewModal';
import { formatDateTime } from '@/lib/utils/format';
import { Calendar, User, Mail, FileText, Eye } from 'lucide-react';
import Link from 'next/link';

interface TaskDetailModalProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TaskDetailModal({ task, open, onOpenChange }: TaskDetailModalProps) {
  const [emailPreviewOpen, setEmailPreviewOpen] = useState(false);
  // Use useTask hook to get the latest task data, which will auto-refresh when task is updated
  const { data: latestTask } = useTask(task.id, { enabled: open });
  // Use latest task data if available, otherwise fall back to prop
  const currentTask = latestTask || task;
  
  const { data: client, isLoading: clientLoading } = useClient(currentTask.client_id);
  const { data: email, isLoading: emailLoading } = useEmail(
    currentTask.email_sent_id || 0,
    { enabled: !!currentTask.email_sent_id }
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex justify-between items-start">
            <div>
              <DialogTitle className="text-2xl">{currentTask.followup_type}</DialogTitle>
            </div>
            <TaskActionsMenu task={currentTask} />
          </div>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Task Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Task Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Scheduled:</span>
                <span className="text-sm">{formatDateTime(currentTask.scheduled_for)}</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Status:</span>
                <TaskStatusBadge status={currentTask.status} />
              </div>

              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Priority:</span>
                <TaskPriorityBadge priority={currentTask.priority} />
              </div>

              {currentTask.notes && (
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Notes:</span>
                  </div>
                  <p className="text-sm text-muted-foreground pl-6">{currentTask.notes}</p>
                </div>
              )}

              {currentTask.completed_at && (
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Completed:</span>
                  <span className="text-sm">{formatDateTime(currentTask.completed_at)}</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Client Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Client</CardTitle>
            </CardHeader>
            <CardContent>
              {clientLoading ? (
                <Skeleton className="h-20 w-full" />
              ) : client ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <Link
                      href={`/clients/${client.id}`}
                      className="font-medium hover:underline"
                    >
                      {client.name}
                    </Link>
                  </div>
                  <p className="text-sm text-muted-foreground pl-6">{client.email}</p>
                  <p className="text-sm text-muted-foreground pl-6">{client.property_address}</p>
                  <p className="text-sm text-muted-foreground pl-6">Stage: {client.stage}</p>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Client not found</p>
              )}
            </CardContent>
          </Card>

          {/* Email Preview (if pending) */}
          {currentTask.status === 'pending' && !currentTask.email_sent_id && client && client.email && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Email Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Preview and edit the email that will be sent for this task. You can make changes before sending.
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => setEmailPreviewOpen(true)}
                    className="w-full"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Preview & Edit Email
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Email Info (if sent) */}
          {currentTask.email_sent_id && (
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Email Sent</CardTitle>
              </CardHeader>
              <CardContent>
                {emailLoading ? (
                  <Skeleton className="h-20 w-full" />
                ) : email ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <Link
                        href={`/emails/${email.id}`}
                        className="font-medium hover:underline"
                      >
                        {email.subject}
                      </Link>
                    </div>
                    <p className="text-sm text-muted-foreground pl-6">
                      Status: {email.status}
                    </p>
                    {email.sent_at && (
                      <p className="text-sm text-muted-foreground pl-6">
                        Sent: {formatDateTime(email.sent_at)}
                      </p>
                    )}
                    {email.opened_at && (
                      <p className="text-sm text-green-600 pl-6">
                        ✓ Opened: {formatDateTime(email.opened_at)}
                      </p>
                    )}
                    {email.clicked_at && (
                      <p className="text-sm text-purple-600 pl-6">
                        ✓ Clicked: {formatDateTime(email.clicked_at)}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Email not found</p>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Email Preview Modal */}
        {client && client.email && (
          <EmailPreviewModal
            open={emailPreviewOpen}
            onOpenChange={setEmailPreviewOpen}
            clientId={currentTask.client_id}
            clientEmail={client.email}
            clientName={client.name}
            taskId={currentTask.id}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}

