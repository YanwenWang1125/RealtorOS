import { z } from 'zod';

export const taskCreateSchema = z.object({
  client_id: z.number().int().min(1, { message: "Please select a client" }),
  followup_type: z.enum(['Day 1', 'Day 3', 'Week 1', 'Week 2', 'Month 1', 'Custom']),
  scheduled_for: z.string().datetime(),
  notes: z.string().max(500, 'Notes must be less than 500 characters').optional(),
  priority: z.enum(['high', 'medium', 'low'])
});

export const taskUpdateSchema = z.object({
  status: z.enum(['pending', 'completed', 'skipped', 'cancelled']).optional(),
  scheduled_for: z.string().datetime().optional(),
  notes: z.string().max(500).optional(),
  priority: z.enum(['high', 'medium', 'low']).optional()
});

export type TaskCreateFormData = z.infer<typeof taskCreateSchema>;
export type TaskUpdateFormData = z.infer<typeof taskUpdateSchema>;
