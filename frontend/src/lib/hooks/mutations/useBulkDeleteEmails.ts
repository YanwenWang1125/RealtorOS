import { useMutation, useQueryClient } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';

export function useBulkDeleteEmails() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ids: number[]) => emailsApi.bulkDelete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

