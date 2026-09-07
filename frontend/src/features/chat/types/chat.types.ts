import type { z } from "zod";

import type {
  askResponseSchema,
  conversationMessageSchema,
  messageMetadataSchema,
  messageRoleSchema,
  responseSourceSchema,
} from "@/features/chat/schemas/message.schema";

export type ResponseSource = z.infer<typeof responseSourceSchema>;
export type MessageRole = z.infer<typeof messageRoleSchema>;
export type MessageMetadata = z.infer<typeof messageMetadataSchema>;
export type ConversationMessage = z.infer<typeof conversationMessageSchema>;
export type AskResponse = z.infer<typeof askResponseSchema>;

export interface AskRequest {
  session_id: string;
  question: string;
  context: string | null;
}

/** A locally rendered message that the backend has not yet confirmed. */
export interface OptimisticMessage extends ConversationMessage {
  pending: true;
}

export type ChatMessage = ConversationMessage | OptimisticMessage;
