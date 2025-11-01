'use client';

import { useParams, useRouter } from 'next/navigation';
import { useClient } from '@/lib/hooks/queries/useClients';
import { useUpdateClient } from '@/lib/hooks/mutations/useUpdateClient';
import ClientForm from '@/components/clients/ClientForm';
import { useToast } from '@/lib/hooks/ui/useToast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/skeleton';

export default function ClientEditPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const clientId = parseInt(params.id as string);

  const { data: client, isLoading } = useClient(clientId);
  const updateClient = useUpdateClient();

  const handleSave = async (clientData: any) => {
    try {
      await updateClient.mutateAsync({ id: clientId, data: clientData });

      toast({
        title: "Client updated!",
        description: "Changes have been saved successfully.",
      });

      router.push(`/clients/${clientId}`);
    } catch (error: any) {
      toast({
        title: "Error updating client",
        description: error.response?.data?.detail || error.message || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleCancel = () => {
    router.push(`/clients/${clientId}`);
  };

  if (isLoading) {
    return <Skeleton className="h-96 w-full" />;
  }

  if (!client) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Client not found</h2>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Edit Client</CardTitle>
        </CardHeader>
        <CardContent>
          <ClientForm
            client={client}
            onSave={handleSave}
            onCancel={handleCancel}
            isSubmitting={updateClient.isPending}
          />
        </CardContent>
      </Card>
    </div>
  );
}
