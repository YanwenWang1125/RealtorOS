import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api/endpoints/clients';
import { ClientCreate } from '@/lib/types/client.types';

export function useCreateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (client: ClientCreate) => clientsApi.create(client),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
