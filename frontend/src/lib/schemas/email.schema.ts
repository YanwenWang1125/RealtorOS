import { z } from 'zod';

export const emailPreviewSchema = z.object({
  client_id: z.number().int().positive(),
  task_id: z.number().int().positive(),
  agent_instructions: z.string().max(500).optional()
});

export const emailSendSchema = z.object({
  client_id: z.number().int().positive(),
  task_id: z.number().int().positive(),
  to_email: z.string().email(),
  subject: z.string().min(1),
  body: z.string().min(1),
  agent_instructions: z.string().max(500).optional()
});

export type EmailPreviewFormData = z.infer<typeof emailPreviewSchema>;
export type EmailSendFormData = z.infer<typeof emailSendSchema>;
