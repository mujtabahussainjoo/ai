import { z } from 'zod';
import { MODEL_CAPABILITY, PROVIDER_NAME } from './enums';

export const ProviderConfigViewSchema = z.object({
  provider: z.enum(PROVIDER_NAME),
  enabled: z.boolean(),
  model_chat: z.string().nullable().optional(),
  model_reasoning: z.string().nullable().optional(),
  model_embedding: z.string().nullable().optional(),
  model_image: z.string().nullable().optional(),
  base_url: z.string().nullable().optional(),
  capabilities: z.array(z.enum(MODEL_CAPABILITY)).optional(),
  has_key: z.boolean(),
  fallback_order: z.number().int().nonnegative().optional(),
});
export type ProviderConfigView = z.infer<typeof ProviderConfigViewSchema>;

export const ProviderConfigUpdateSchema = z.object({
  provider: z.enum(PROVIDER_NAME),
  enabled: z.boolean().optional(),
  model_chat: z.string().nullable().optional(),
  model_reasoning: z.string().nullable().optional(),
  model_embedding: z.string().nullable().optional(),
  model_image: z.string().nullable().optional(),
  base_url: z.string().nullable().optional(),
  fallback_order: z.number().int().nonnegative().optional(),
  api_key: z.string().min(1).optional(),
});
export type ProviderConfigUpdate = z.infer<typeof ProviderConfigUpdateSchema>;

export const SettingValueSchema = z.record(z.string(), z.unknown());
export type SettingValue = z.infer<typeof SettingValueSchema>;

export const AppSettingViewSchema = z.object({
  key: z.string(),
  value: SettingValueSchema,
  group: z.string().nullable().optional(),
  updated_at: z.string().datetime(),
  updated_by: z.string().uuid().nullable().optional(),
});
export type AppSettingView = z.infer<typeof AppSettingViewSchema>;

export const SettingUpdateSchema = z.object({
  key: z.string(),
  value: SettingValueSchema,
});
export type SettingUpdate = z.infer<typeof SettingUpdateSchema>;

export const FeatureFlagSchema = z.object({
  key: z.string(),
  enabled: z.boolean(),
  description: z.string().nullable().optional(),
});
export type FeatureFlag = z.infer<typeof FeatureFlagSchema>;