import { z } from "zod";

export const dependencyStatusSchema = z.enum(["connected", "unavailable"]);

export const dependencyHealthSchema = z.object({
  status: dependencyStatusSchema,
  message: z.string().nullable().default(null),
});

export const healthResponseSchema = z.object({
  status: z.enum(["ok", "degraded"]),
  service: z.object({
    name: z.string(),
    version: z.string(),
    environment: z.string(),
  }),
  dependencies: z.record(z.string(), dependencyHealthSchema),
});
