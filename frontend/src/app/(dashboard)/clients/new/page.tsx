'use client';

import { useRouter } from 'next/navigation';
import ClientForm from '@/components/clients/ClientForm';
import { useCreateClient } from '@/lib/hooks/mutations/useCreateClient';
import { useToast } from '@/lib/hooks/ui/useToast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';

export default function ClientCreatePage() {
  const router = useRouter();
  const { toast } = useToast();
  const createClient = useCreateClient();

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
        description: "Follow-up tasks are being scheduled in the background.",
      });

      // Navigate to client detail page
      router.push(`/clients/${newClient.id}`);
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

  const handleCancel = () => {
    router.push('/clients');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Create New Client</CardTitle>
          <CardDescription>
            Add a new client to your CRM. Follow-up tasks will be automatically created.
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
    </div>
  );
}
