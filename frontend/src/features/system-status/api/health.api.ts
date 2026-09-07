import { apiEndpoints } from "@/lib/api/endpoints";
import { apiRequest } from "@/lib/api/api-client";
import { healthResponseSchema } from "@/features/system-status/schemas/health.schema";
import type { HealthResponse } from "@/features/system-status/types/health.types";

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiRequest({
    path: apiEndpoints.health(),
    schema: healthResponseSchema,
    signal,
  });
}
