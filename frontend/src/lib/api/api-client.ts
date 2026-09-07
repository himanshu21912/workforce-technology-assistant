import type { ZodType } from "zod";

import { API_BASE_URL } from "@/lib/env";
import {
  ApiError,
  fallbackMessageForStatus,
  parseErrorBody,
} from "@/lib/api/errors";

type HttpMethod = "GET" | "POST" | "PATCH" | "DELETE";

interface RequestOptions<TResponse> {
  method?: HttpMethod;
  path: string;
  body?: unknown;
  signal?: AbortSignal;
  /** Validates and narrows the parsed response payload. */
  schema: ZodType<TResponse>;
}

function buildUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  return `${API_BASE_URL}${normalizedPath}`;
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

async function readJsonBody(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text.trim()) {
    return null;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch (error) {
    // A failing response may carry a non-JSON body (an HTML error page or
    // a server traceback). Report the failure, never the body.
    if (!response.ok) {
      throw new ApiError({
        kind: "http",
        message: fallbackMessageForStatus(response.status),
        status: response.status,
        cause: error,
      });
    }

    throw new ApiError({
      kind: "parse",
      message: "The assistant service returned a malformed response.",
      status: response.status,
      cause: error,
    });
  }
}

function throwForErrorResponse(response: Response, body: unknown): never {
  const parsed = parseErrorBody(body);

  throw new ApiError({
    kind: parsed?.kind ?? (response.status === 422 ? "validation" : "http"),
    message: parsed?.message ?? fallbackMessageForStatus(response.status),
    status: response.status,
    code: parsed?.code,
    details: parsed?.details,
  });
}

/**
 * Performs a JSON request against the FastAPI backend and validates the
 * response against a Zod schema. Every failure surfaces as an ApiError.
 */
export async function apiRequest<TResponse>({
  method = "GET",
  path,
  body,
  signal,
  schema,
}: RequestOptions<TResponse>): Promise<TResponse> {
  const headers: Record<string, string> = { Accept: "application/json" };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  let response: Response;

  try {
    response = await fetch(buildUrl(path), {
      method,
      headers,
      signal,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch (error) {
    if (isAbortError(error)) {
      throw error;
    }

    throw new ApiError({
      kind: "network",
      message:
        "Cannot reach the assistant service. Check that the backend is running.",
      cause: error,
    });
  }

  const payload = await readJsonBody(response);

  if (!response.ok) {
    throwForErrorResponse(response, payload);
  }

  const validation = schema.safeParse(payload);

  if (!validation.success) {
    throw new ApiError({
      kind: "parse",
      message: "The assistant service returned an unexpected response format.",
      status: response.status,
      details: validation.error.issues,
    });
  }

  return validation.data;
}
