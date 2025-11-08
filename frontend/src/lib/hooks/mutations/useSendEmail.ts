import { useMutation, useQueryClient } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';
import { EmailSendRequest } from '@/lib/types/email.types';

export function useSendEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: EmailSendRequest) => emailsApi.send(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}
