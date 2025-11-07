'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useClient, useClientTasks } from '@/lib/hooks/queries/useClients';
import { useEmails } from '@/lib/hooks/queries/useEmails';
import { Button } from '@/components/ui/Button';
import { ClientHeader } from '@/components/clients/ClientHeader';
import { ClientStagePipeline } from '@/components/clients/ClientStagePipeline';
import { ClientInfoCard } from '@/components/clients/ClientInfoCard';
import { ClientTimeline } from '@/components/clients/ClientTimeline';
import { ClientEmailHistory } from '@/components/clients/ClientEmailHistory';
import { ClientDeleteDialog } from '@/components/clients/ClientDeleteDialog';
import { EmailPreviewModal } from '@/components/emails/EmailPreviewModal';
import { Skeleton } from '@/components/ui/skeleton';
import { Mail, Plus, Pencil } from 'lucide-react';
import { useToast } from '@/lib/hooks/ui/useToast';

export default function ClientDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const clientId = parseInt(params.id as string);
  const [emailModalOpen, setEmailModalOpen] = useState(false);

  const { data: client, isLoading: clientLoading } = useClient(clientId);
  const { data: tasks, isLoading: tasksLoading } = useClientTasks(clientId);
  const { data: emails, isLoading: emailsLoading } = useEmails({ client_id: clientId });
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);

  if (clientLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (!client) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Client not found</h2>
        <Button onClick={() => router.push('/clients')} className="mt-4">
          Back to Clients
        </Button>
      </div>
    );
  }

  const handleSendEmail = () => {
    if (!client.email) {
      toast({
        title: "No email address",
        description: "This client doesn't have an email address. Please add one first.",
        variant: "destructive",
      });
      return;
    }

    // Find the first available task (prefer pending tasks, then any task)
    const pendingTask = tasks?.find((t: any) => t.status === 'pending');
    const firstTask = pendingTask || tasks?.[0];

    if (!firstTask) {
      toast({
        title: "No tasks available",
        description: "This client doesn't have any tasks yet. Please create a task first to send an email.",
        variant: "destructive",
      });
      return;
    }

    setSelectedTaskId(firstTask.id);
    setEmailModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
        <ClientHeader client={client} />
        <div className="flex gap-2 flex-wrap">
          <Button
            variant="outline"
            onClick={() => router.push(`/clients/${clientId}/edit`)}
          >
            <Pencil className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" onClick={handleSendEmail}>
            <Mail className="h-4 w-4 mr-2" />
            Send Email
          </Button>
          <ClientDeleteDialog
            client={client}
            taskCount={tasks?.length}
            emailCount={emails?.length}
          />
        </div>
      </div>

      {/* Stage Pipeline */}
      <ClientStagePipeline client={client} />

      {/* Info Card */}
      <ClientInfoCard client={client} />

      {/* Tasks Section */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Follow-up Tasks</h2>
          <Button variant="outline" size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Create Custom Task
          </Button>
        </div>
        {tasksLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <ClientTimeline tasks={tasks || []} />
        )}
      </div>

      {/* Emails Section */}
      <div>
        <h2 className="text-xl font-bold mb-4">Email History</h2>
        {emailsLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <ClientEmailHistory emails={emails || []} />
        )}
      </div>

      {/* Email Preview Modal */}
      {client && client.email && selectedTaskId && (
        <EmailPreviewModal
          open={emailModalOpen}
          onOpenChange={(open) => {
            setEmailModalOpen(open);
            if (!open) {
              setSelectedTaskId(null);
            }
          }}
          clientId={clientId}
          clientEmail={client.email}
          clientName={client.name}
          taskId={selectedTaskId}
        />
      )}
    </div>
  );
}
