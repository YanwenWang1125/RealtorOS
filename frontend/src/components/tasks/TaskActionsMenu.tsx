'use client';

import { useState } from 'react';
import { Task } from '@/lib/types/task.types';
import { useDeleteTask } from '@/lib/hooks/mutations/useDeleteTask';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/Button';
import { TaskRescheduleDialog } from '@/components/tasks/TaskRescheduleDialog';
import { EmailPreviewModal } from '@/components/emails/EmailPreviewModal';
import { MoreVertical, Calendar, Mail, Trash2 } from 'lucide-react';

interface TaskActionsMenuProps {
  task: Task;
}

export function TaskActionsMenu({ task }: TaskActionsMenuProps) {
  const { toast } = useToast();
  const deleteTask = useDeleteTask();
  const [rescheduleOpen, setRescheduleOpen] = useState(false);
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  // Fetch client data eagerly if email can be sent (to reduce delay when user clicks)
  const { data: client } = useClient(task.client_id, { 
    enabled: !task.email_sent_id || emailModalOpen 
  });

  const handleDelete = async () => {
    try {
      await deleteTask.mutateAsync(task.id);
      toast({
        title: "Task deleted",
        description: "Task and associated emails have been deleted.",
      });
      setDeleteDialogOpen(false);
    } catch (error: any) {
      toast({
        title: "Error deleting task",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleSendEmail = () => {
    if (!client) {
      toast({
        title: "Loading client data",
        description: "Please wait a moment and try again.",
      });
      setEmailModalOpen(true); // Still open to trigger client fetch
      return;
    }
    setEmailModalOpen(true);
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setRescheduleOpen(true)}>
            <Calendar className="h-4 w-4 mr-2" />
            Reschedule
          </DropdownMenuItem>

          {task.status === 'pending' && !task.email_sent_id && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSendEmail}>
                <Mail className="h-4 w-4 mr-2" />
                Send Email
              </DropdownMenuItem>
            </>
          )}

          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() => setDeleteDialogOpen(true)}
            className="text-destructive"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <TaskRescheduleDialog
        task={task}
        open={rescheduleOpen}
        onOpenChange={setRescheduleOpen}
      />

      {client && (
        <EmailPreviewModal
          open={emailModalOpen}
          onOpenChange={setEmailModalOpen}
          clientId={client.id}
          clientEmail={client.email}
          clientName={client.name}
          taskId={task.id}
        />
      )}

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Task</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this task? This will also delete all associated emails. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deleteTask.isPending}
            >
              {deleteTask.isPending ? 'Deleting...' : 'Delete'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

