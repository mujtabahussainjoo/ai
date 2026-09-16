import { z } from 'zod';
import { DOCUMENT_STATUS, JOB_STATUS } from './enums';
import { CitationSchema } from './chat';

export const DocumentViewSchema = z.object({
  id: z.string().uuid(),
  filename: z.string(),
  content_type: z.string(),
  size_bytes: z.number().int().nonnegative(),
  status: z.enum(DOCUMENT_STATUS),
  owner_id: z.string().uuid(),
  created_at: z.string().datetime(),
  error_message: z.string().nullable().optional(),
});
export type DocumentView = z.infer<typeof DocumentViewSchema>;

export const UploadResultSchema = z.object({
  document_id: z.string().uuid(),
  filename: z.string(),
  content_type: z.string(),
  size_bytes: z.number().int().nonnegative(),
  status: z.enum(DOCUMENT_STATUS),
  job_id: z.string().uuid().nullable(),
});
export type UploadResult = z.infer<typeof UploadResultSchema>;

export const IngestionJobViewSchema = z.object({
  id: z.string().uuid(),
  document_id: z.string().uuid(),
  status: z.enum(JOB_STATUS),
  progress: z.number().int().min(0).max(100),
  stage: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});
export type IngestionJobView = z.infer<typeof IngestionJobViewSchema>;

export const ChunkViewSchema = z.object({
  id: z.string().uuid(),
  document_id: z.string().uuid(),
  page_number: z.number().int().nonnegative().nullable().optional(),
  chunk_index: z.number().int().nonnegative(),
  content: z.string(),
  token_count: z.number().int().nonnegative().optional(),
});
export type ChunkView = z.infer<typeof ChunkViewSchema>;

export const RetrievalRequestSchema = z.object({
  query: z.string().min(1).max(5000),
  document_ids: z.array(z.string().uuid()).optional(),
  top_k: z.number().int().min(1).max(50).default(6),
  filters: z.record(z.string(), z.unknown()).optional(),
});
export type RetrievalRequest = z.infer<typeof RetrievalRequestSchema>;

export const RetrievedChunkSchema = z.object({
  chunk_id: z.string().uuid(),
  document_id: z.string().uuid(),
  filename: z.string(),
  page_number: z.number().int().nonnegative().nullable().optional(),
  content: z.string(),
  score: z.number().min(0).max(1).optional(),
});
export type RetrievedChunk = z.infer<typeof RetrievedChunkSchema>;

export const RetrievalResponseSchema = z.object({
  query: z.string(),
  results: z.array(RetrievedChunkSchema),
  total: z.number().int().nonnegative(),
});
export type RetrievalResponse = z.infer<typeof RetrievalResponseSchema>;

export const RagChatRequestSchema = z.object({
  question: z.string().min(1).max(5000),
  conversation_id: z.string().uuid().optional(),
  document_ids: z.array(z.string().uuid()).optional(),
  top_k: z.number().int().min(1).max(50).default(6),
  rerank: z.boolean().default(false),
});
export type RagChatRequest = z.infer<typeof RagChatRequestSchema>;

export const RagChatResponseSchema = z.object({
  answer: z.string(),
  citations: z.array(CitationSchema),
  insufficient_evidence: z.boolean(),
  conversation_id: z.string().uuid(),
  run_id: z.string().uuid().optional(),
});
export type RagChatResponse = z.infer<typeof RagChatResponseSchema>;