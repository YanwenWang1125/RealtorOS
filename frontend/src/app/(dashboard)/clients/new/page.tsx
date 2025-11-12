'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ClientForm from '@/components/clients/ClientForm';
import { useCreateClient } from '@/lib/hooks/mutations/useCreateClient';
import { useToast } from '@/lib/hooks/ui/useToast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { TaskSelectionDialog } from '@/components/tasks/TaskSelectionDialog';

export default function ClientCreatePage() {
  const router = useRouter();
  const { toast } = useToast();
  const createClient = useCreateClient();
  const [showTaskDialog, setShowTaskDialog] = useState(false);
  const [newClientId, setNewClientId] = useState<number | null>(null);
  const [newClientName, setNewClientName] = useState<string>('');

  const handleSave = async (clientData: any) => {
    try {
      // Clean up the data: convert empty strings to undefined for optional fields
      const dataToSend: any = {
        name: clientData.name?.trim(),
        email: clientData.email?.trim(),
        property_address: clientData.property_address?.trim(),
        property_type: clientData.property_type,
        stage: clientData.stage,
        phone: clientData.phone?.trim() || undefined,
        notes: clientData.notes?.trim() || undefined,
        custom_fields: clientData.custom_fields && Object.keys(clientData.custom_fields).length > 0 
          ? clientData.custom_fields 
          : {},
      };

      // Validate required fields
      if (!dataToSend.name || !dataToSend.email || !dataToSend.property_address) {
        toast({
          title: "Validation Error",
          description: "Please fill in all required fields (Name, Email, Property Address).",
          variant: "destructive",
        });
        return;
      }

      console.log('Creating client with data:', dataToSend);
      const newClient = await createClient.mutateAsync(dataToSend);

      toast({
        title: "Client created!",
        description: clientData.create_tasks 
          ? "Now select which follow-up tasks to create."
          : "Client created successfully.",
      });

      // If user wants to create tasks, show the task selection dialog
      if (clientData.create_tasks) {
        setNewClientId(newClient.id);
        setNewClientName(newClient.name);
        setShowTaskDialog(true);
      } else {
        // Navigate to client detail page
        router.push(`/clients/${newClient.id}`);
      }
    } catch (error: any) {
      console.error('Error creating client:', error);
      const errorMessage = 
        error?.response?.data?.detail || 
        error?.response?.data?.message ||
        error?.message || 
        'Please try again.';
      
      toast({
        title: "Error creating client",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handleTaskDialogClose = (open: boolean) => {
    setShowTaskDialog(open);
    if (!open && newClientId) {
      // Navigate to client detail page after dialog closes
      router.push(`/clients/${newClientId}`);
    }
  };

  const handleCancel = () => {
    router.push('/clients');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create New Client</CardTitle>
          <CardDescription>
            Add a new client to your CRM. You can optionally create follow-up tasks after saving.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ClientForm
            onSave={handleSave}
            onCancel={handleCancel}
            isSubmitting={createClient.isPending}
          />
        </CardContent>
      </Card>

      {newClientId && newClientName && (
        <TaskSelectionDialog
          open={showTaskDialog}
          onOpenChange={handleTaskDialogClose}
          clientId={newClientId}
          clientName={newClientName}
        />
      )}
    </div>
  );
}
