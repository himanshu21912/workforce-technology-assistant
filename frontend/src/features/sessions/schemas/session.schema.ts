import { z } from "zod";

import { conversationMessageSchema } from "@/features/chat/schemas/message.schema";

export const chatSessionSchema = z.object({
  session_id: z.string(),
  title: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  message_count: z.number().int().nonnegative(),
});

export const sessionListResponseSchema = z.object({
  count: z.number().int().nonnegative(),
  sessions: z.array(chatSessionSchema),
});

export const sessionHistorySchema = z.object({
  session: chatSessionSchema,
  messages: z.array(conversationMessageSchema),
});

export const deleteSessionResponseSchema = z.object({
  session_id: z.string(),
  session_deleted: z.boolean(),
  semantic_cache_entries_deleted: z.number().int().nonnegative(),
});
