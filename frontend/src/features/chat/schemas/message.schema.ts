import { z } from "zod";

export const responseSourceSchema = z.enum([
  "llm",
  "postgresql",
  "github_mcp",
  "multi_source",
]);

/** Backend may add sources; unknown values degrade to a neutral badge. */
export const looseResponseSourceSchema = z.string().min(1);

export const messageRoleSchema = z.enum([
  "user",
  "assistant",
  "system",
  "tool",
]);

export const messageMetadataSchema = z
  .object({
    source: looseResponseSourceSchema.optional(),
    tools_used: z.array(z.string()).optional(),
    cache_hit: z.boolean().optional(),
    similarity_score: z.number().nullable().optional(),
    model_name: z.string().nullable().optional(),
    message_type: z.string().optional(),
  })
  .loose();

export const conversationMessageSchema = z.object({
  id: z.string(),
  role: messageRoleSchema,
  content: z.string(),
  created_at: z.string(),
  metadata: messageMetadataSchema.default({}),
});

export const askResponseSchema = z.object({
  session_id: z.string(),
  answer: z.string(),
  cache_hit: z.boolean(),
  similarity_score: z.number().nullable().default(null),
  source: looseResponseSourceSchema,
  tools_used: z.array(z.string()).default([]),
  model_name: z.string().nullable().default(null),
});
