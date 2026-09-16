import { z } from 'zod';

export const ErrorDetailSchema = z.object({
  code: z.string(),
  message: z.string(),
  request_id: z.string().uuid(),
  details: z.record(z.string(), z.unknown()).optional(),
});
export type ErrorDetail = z.infer<typeof ErrorDetailSchema>;

export function ApiEnvelopeSchema<T extends z.ZodTypeAny>(data: T) {
  return z.object({ data, error: z.null() });
}
export type ApiEnvelope<T> = { data: T; error: null };

export const PaginationParamsSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  page_size: z.coerce.number().int().min(1).max(100).default(20),
  sort_by: z.string().optional(),
  sort_order: z.enum(['asc', 'desc']).default('desc'),
});
export type PaginationParams = z.infer<typeof PaginationParamsSchema>;

export function PaginatedSchema<T extends z.ZodTypeAny>(item: T) {
  return z.object({
    items: z.array(item),
    page: z.number().int().min(1),
    page_size: z.number().int().min(1),
    total: z.number().int().min(0),
    total_pages: z.number().int().min(0),
  });
}
export type Paginated<T extends z.ZodTypeAny> = {
  items: Array<z.infer<T>>;
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export const HealthSchema = z.object({
  status: z.literal('ok'),
  version: z.string(),
  database: z.enum(['up', 'down']),
  timestamp: z.string().datetime(),
});
export type Health = z.infer<typeof HealthSchema>;

export const StreamEventSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('token'), text: z.string() }),
  z.object({ type: z.literal('tool_call'), name: z.string() }),
  z.object({ type: z.literal('citation'), citation: z.record(z.string(), z.unknown()) }),
  z.object({ type: z.literal('reasoning'), text: z.string() }),
  z.object({ type: z.literal('done'), run_id: z.string().uuid() }),
  z.object({ type: z.literal('error'), request_id: z.string().uuid(), message: z.string() }),
]);
export type StreamEvent = z.infer<typeof StreamEventSchema>;