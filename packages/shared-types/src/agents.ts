import { z } from 'zod';
import { AGENT_KIND } from './enums';
import { MessageViewSchema } from './chat';

export const ToolCallViewSchema = z.object({
  id: z.string().uuid().optional(),
  name: z.string(),
  arguments: z.record(z.string(), z.unknown()),
  status: z.enum(['pending', 'approved', 'denied', 'completed', 'failed']).default('pending'),
  output: z.string().nullable().optional(),
  started_at: z.string().datetime().nullable().optional(),
  finished_at: z.string().datetime().nullable().optional(),
});
export type ToolCallView = z.infer<typeof ToolCallViewSchema>;

export const AgentRunViewSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  kind: z.enum(AGENT_KIND),
  status: z.enum(['queued', 'running', 'needs_approval', 'completed', 'failed', 'cancelled']),
  model: z.string().nullable().optional(),
  summary: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
  token_usage: z.record(z.string(), z.number()).optional(),
  started_at: z.string().datetime().nullable().optional(),
  finished_at: z.string().datetime().nullable().optional(),
});
export type AgentRunView = z.infer<typeof AgentRunViewSchema>;

export const AgentRunDetailSchema = AgentRunViewSchema.extend({
  messages: z.array(MessageViewSchema).optional(),
  tool_calls: z.array(ToolCallViewSchema).optional(),
});
export type AgentRunDetail = z.infer<typeof AgentRunDetailSchema>;

export const AgentRunRequestSchema = z.object({
  kind: z.enum(AGENT_KIND).default('all_rounder'),
  message: z.string().min(1).max(20000),
  conversation_id: z.string().uuid().optional(),
  document_ids: z.array(z.string().uuid()).optional(),
  model: z.string().optional(),
});
export type AgentRunRequest = z.infer<typeof AgentRunRequestSchema>;

export const ApprovalRequestViewSchema = z.object({
  id: z.string().uuid(),
  run_id: z.string().uuid(),
  tool_name: z.string(),
  arguments: z.record(z.string(), z.unknown()),
  reason: z.string().nullable().optional(),
  requested_at: z.string().datetime(),
  expires_at: z.string().datetime().nullable().optional(),
});
export type ApprovalRequestView = z.infer<typeof ApprovalRequestViewSchema>;

export const ApprovalDecisionSchema = z.object({
  decision: z.enum(['approve', 'deny']),
  reason: z.string().max(500).optional(),
});
export type ApprovalDecision = z.infer<typeof ApprovalDecisionSchema>;