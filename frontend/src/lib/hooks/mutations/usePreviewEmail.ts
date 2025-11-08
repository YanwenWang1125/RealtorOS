import { useMutation } from '@tanstack/react-query';
import { emailsApi } from '@/lib/api/endpoints/emails';
import { EmailPreviewRequest } from '@/lib/types/email.types';

export function usePreviewEmail() {
  return useMutation({
    mutationFn: (request: EmailPreviewRequest) => emailsApi.preview(request),
    retry: 1, // Retry once on failure
  });
}

