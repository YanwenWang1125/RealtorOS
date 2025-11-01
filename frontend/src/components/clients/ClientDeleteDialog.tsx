'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useDeleteClient } from '@/lib/hooks/mutations/useDeleteClient';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/Button';
import { Trash2 } from 'lucide-react';
import { Client } from '@/lib/types/client.types';

interface ClientDeleteDialogProps {
  client: Client;
  taskCount?: number;
  emailCount?: number;
}

export function ClientDeleteDialog({ client, taskCount, emailCount }: ClientDeleteDialogProps) {
  const router = useRouter();
  const { toast } = useToast();
  const deleteClient = useDeleteClient();
  const [open, setOpen] = useState(false);

  const handleDelete = async () => {
    try {
      await deleteClient.mutateAsync(client.id);

      toast({
        title: "Client deleted",
        description: `${client.name} has been removed from your CRM.`,
      });

      router.push('/clients');
    } catch (error: any) {
      toast({
        title: "Error deleting client",
        description: error.response?.data?.detail || error.message || "Please try again.",
        variant: "destructive",
      });
      setOpen(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="destructive" size="sm">
          <Trash2 className="h-4 w-4 mr-2" />
          Delete
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete <strong>{client.name}</strong> and cannot be undone.
            {(taskCount || emailCount) && (
              <div className="mt-4 p-3 bg-muted rounded-md">
                <p className="text-sm">This client has:</p>
                <ul className="text-sm list-disc list-inside mt-1">
                  {taskCount && taskCount > 0 && <li>{taskCount} task(s)</li>}
                  {emailCount && emailCount > 0 && <li>{emailCount} email(s)</li>}
                </ul>
              </div>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            Delete Client
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

