import { useMutation, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '@/lib/api/endpoints/clients';

export function useBulkDeleteClients() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ids: number[]) => clientsApi.bulkDelete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

