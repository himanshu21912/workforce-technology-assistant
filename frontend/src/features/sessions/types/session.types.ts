import type { z } from "zod";

import type {
  chatSessionSchema,
  deleteSessionResponseSchema,
  sessionHistorySchema,
  sessionListResponseSchema,
} from "@/features/sessions/schemas/session.schema";

export type ChatSession = z.infer<typeof chatSessionSchema>;
export type SessionListResponse = z.infer<typeof sessionListResponseSchema>;
export type SessionHistory = z.infer<typeof sessionHistorySchema>;
export type DeleteSessionResponse = z.infer<
  typeof deleteSessionResponseSchema
>;
