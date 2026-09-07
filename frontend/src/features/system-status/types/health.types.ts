import type { z } from "zod";

import type {
  dependencyHealthSchema,
  dependencyStatusSchema,
  healthResponseSchema,
} from "@/features/system-status/schemas/health.schema";

export type DependencyStatus = z.infer<typeof dependencyStatusSchema>;
export type DependencyHealth = z.infer<typeof dependencyHealthSchema>;
export type HealthResponse = z.infer<typeof healthResponseSchema>;

export type ServiceIndicatorStatus =
  | "loading"
  | "connected"
  | "degraded"
  | "unavailable";

export interface ServiceIndicator {
  key: string;
  label: string;
  status: ServiceIndicatorStatus;
  message: string | null;
}
