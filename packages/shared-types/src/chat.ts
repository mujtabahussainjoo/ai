import { z } from 'zod';
import { MESSAGE_ROLE } from './enums';

export const CitationSchema = z.object({
  chunk_id: z.string().uuid(),
  document_id: z.string().uuid(),
  filename: z.string(),
  page_number: z.number().int().nonnegative().nullable(),
  score: z.number().min(0).max(1).optional(),
  snippet: z.string(),
});
export type Citation = z.infer<typeof CitationSchema>;

export const MessageViewSchema = z.object({
  id: z.string().uuid().optional(),
  role: z.enum(MESSAGE_ROLE),
  content: z.string(),
  created_at: z.string().datetime().optional(),
  trace_id: z.string().uuid().optional(),
  citations: z.array(CitationSchema).optional(),
});
export type MessageView = z.infer<typeof MessageViewSchema>;

export const ConversationSummarySchema = z.object({
  id: z.string().uuid(),
  title: z.string().nullable(),
  user_id: z.string().uuid(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  message_count: z.number().int().nonnegative().optional(),
});
export type ConversationSummary = z.infer<typeof ConversationSummarySchema>;

export const ConversationDetailSchema = ConversationSummarySchema.extend({
  messages: z.array(MessageViewSchema),
});
export type ConversationDetail = z.infer<typeof ConversationDetailSchema>;

export const ChatRequestSchema = z.object({
  message: z.string().min(1).max(20000),
  conversation_id: z.string().uuid().optional(),
  agent: z.enum(['chat', 'rag', 'web_research', 'all_rounder']).default('all_rounder'),
  document_ids: z.array(z.string().uuid()).optional(),
  model: z.string().optional(),
});
export type ChatRequest = z.infer<typeof ChatRequestSchema>;

export const ChatResponseSchema = z.object({
  conversation_id: z.string().uuid(),
  message: MessageViewSchema,
  agent: z.string(),
  run_id: z.string().uuid().optional(),
});
export type ChatResponse = z.infer<typeof ChatResponseSchema>;

export const CompletionRequestSchema = z.object({
  messages: z.array(MessageViewSchema).min(1),
  provider: z.string().optional(),
  model: z.string().optional(),
  temperature: z.number().min(0).max(2).optional(),
});
export type CompletionRequest = z.infer<typeof CompletionRequestSchema>;