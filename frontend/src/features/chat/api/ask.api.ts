import { apiEndpoints } from "@/lib/api/endpoints";
import { apiRequest } from "@/lib/api/api-client";
import { askResponseSchema } from "@/features/chat/schemas/message.schema";
import type { AskRequest, AskResponse } from "@/features/chat/types/chat.types";

export function askQuestion(
  request: AskRequest,
  signal?: AbortSignal,
): Promise<AskResponse> {
  return apiRequest({
    method: "POST",
    path: apiEndpoints.ask(),
    body: request,
    schema: askResponseSchema,
    signal,
  });
}
