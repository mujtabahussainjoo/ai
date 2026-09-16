export const ROLE = ['admin', 'user'] as const;
export type Role = (typeof ROLE)[number];

export const AGENT_KIND = [
  'chat',
  'rag',
  'web_research',
  'all_rounder',
  'recommendation',
  'coding',
  'image',
] as const;
export type AgentKind = (typeof AGENT_KIND)[number];

export const MESSAGE_ROLE = ['user', 'assistant', 'system', 'tool'] as const;
export type MessageRole = (typeof MESSAGE_ROLE)[number];

export const TOOL_CATEGORY = ['read', 'write', 'action'] as const;
export type ToolCategory = (typeof TOOL_CATEGORY)[number];

export const AGENT_RUN_STATUS = ['queued', 'running', 'needs_approval', 'completed', 'failed', 'cancelled'] as const;
export type AgentRunStatus = (typeof AGENT_RUN_STATUS)[number];

export const JOB_STATUS = ['queued', 'processing', 'completed', 'failed'] as const;
export type JobStatus = (typeof JOB_STATUS)[number];

export const PROVIDER_NAME = ['openai', 'anthropic', 'google', 'ollama', 'huggingface'] as const;
export type ProviderName = (typeof PROVIDER_NAME)[number];

export const MODEL_CAPABILITY = [
  'chat',
  'reasoning',
  'coding',
  'vision',
  'embedding',
  'image_generation',
  'tool_use',
] as const;
export type ModelCapability = (typeof MODEL_CAPABILITY)[number];

export const FEEDBACK_CATEGORY = ['rating', 'correction', 'safety', 'preference', 'other'] as const;
export type FeedbackCategory = (typeof FEEDBACK_CATEGORY)[number];

export const DOCUMENT_STATUS = ['uploaded', 'processing', 'ready', 'failed', 'deleted'] as const;
export type DocumentStatus = (typeof DOCUMENT_STATUS)[number];