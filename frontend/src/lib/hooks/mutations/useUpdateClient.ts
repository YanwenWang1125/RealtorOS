import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api/endpoints/clients';
import { ClientUpdate } from '@/lib/types/client.types';

export function useUpdateClient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ClientUpdate }) => 
      clientsApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['client', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
