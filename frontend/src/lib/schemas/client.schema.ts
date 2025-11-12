import { z } from 'zod';

export const clientCreateSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  email: z.string().email('Invalid email address'),
  phone: z.string().max(20, 'Phone must be less than 20 characters').optional(),
  property_address: z.string().min(1, 'Property address is required').max(200, 'Address must be less than 200 characters'),
  property_type: z.enum(['residential', 'commercial', 'land', 'other']),
  stage: z.enum(['lead', 'negotiating', 'closed', 'lost']),
  notes: z.string().max(1000, 'Notes must be less than 1000 characters').optional(),
  custom_fields: z.record(z.string(), z.any()).optional()
});

export const clientUpdateSchema = clientCreateSchema.partial();

export type ClientCreateFormData = z.infer<typeof clientCreateSchema>;
export type ClientUpdateFormData = z.infer<typeof clientUpdateSchema>;
