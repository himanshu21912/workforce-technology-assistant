export type ApiErrorKind =
  | "network"
  | "http"
  | "validation"
  | "parse";

interface ApiErrorOptions {
  kind: ApiErrorKind;
  message: string;
  status?: number;
  code?: string;
  details?: unknown;
  cause?: unknown;
}

/**
 * Typed error raised by the API client for every failure mode, so UI
 * code never has to inspect raw responses or stack traces.
 */
export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;
  readonly code?: string;
  readonly details?: unknown;

  constructor({
    kind,
    message,
    status,
    code,
    details,
    cause,
  }: ApiErrorOptions) {
    super(message, cause === undefined ? undefined : { cause });
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
    this.code = code;
    this.details = details;
  }

  get isNotFound(): boolean {
    return this.status === 404 || this.code === "session_not_found";
  }

  get isNetworkError(): boolean {
    return this.kind === "network";
  }
}

export function isApiError(value: unknown): value is ApiError {
  return value instanceof ApiError;
}

/**
 * Human-readable message for any thrown value, without leaking stack
 * traces or internal object shapes into the UI.
 */
export function toErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again.",
): string {
  if (isApiError(error)) {
    return error.message;
  }

  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return fallback;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

interface ParsedErrorBody {
  message?: string;
  code?: string;
  details?: unknown;
  kind?: ApiErrorKind;
}

/**
 * FastAPI 422 payloads: { detail: [{ loc, msg, type }] }.
 */
function parseValidationDetail(detail: unknown[]): ParsedErrorBody | null {
  const messages = detail
    .map((item) => {
      if (!isRecord(item)) {
        return null;
      }

      const message = typeof item.msg === "string" ? item.msg : null;

      if (!message) {
        return null;
      }

      const location = Array.isArray(item.loc)
        ? item.loc.filter((part) => typeof part === "string").at(-1)
        : undefined;

      return location ? `${String(location)}: ${message}` : message;
    })
    .filter((item): item is string => Boolean(item));

  if (messages.length === 0) {
    return null;
  }

  return {
    kind: "validation",
    code: "validation_error",
    message: messages.join(" "),
    details: detail,
  };
}

/**
 * Understands every error shape the backend can produce:
 *
 * - the application format: { error: { code, message, details } }
 * - FastAPI HTTPException with a dict detail: { detail: { code, message } }
 * - FastAPI HTTPException with a string detail: { detail: "..." }
 * - FastAPI request validation: { detail: [{ loc, msg, type }] }
 */
export function parseErrorBody(body: unknown): ParsedErrorBody | null {
  if (!isRecord(body)) {
    return null;
  }

  const applicationError = body.error;

  if (isRecord(applicationError)) {
    const message =
      typeof applicationError.message === "string"
        ? applicationError.message
        : undefined;
    const code =
      typeof applicationError.code === "string"
        ? applicationError.code
        : undefined;

    if (message || code) {
      return {
        message,
        code,
        details: applicationError.details,
      };
    }
  }

  const detail = body.detail;

  if (Array.isArray(detail)) {
    return parseValidationDetail(detail);
  }

  if (isRecord(detail)) {
    return {
      message: typeof detail.message === "string" ? detail.message : undefined,
      code: typeof detail.code === "string" ? detail.code : undefined,
      details: detail,
    };
  }

  if (typeof detail === "string" && detail.trim()) {
    return { message: detail };
  }

  return null;
}

const STATUS_FALLBACK_MESSAGES: Record<number, string> = {
  400: "The request was rejected by the assistant service.",
  404: "The requested resource was not found.",
  422: "The request could not be processed. Please adjust your input.",
  500: "The assistant service reported an internal error.",
  502: "The AI assistant could not complete the request.",
  503: "The assistant service is temporarily unavailable.",
};

export function fallbackMessageForStatus(status: number): string {
  return (
    STATUS_FALLBACK_MESSAGES[status] ??
    `The assistant service responded with an unexpected error (${status}).`
  );
}
