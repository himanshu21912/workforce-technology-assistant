const DEFAULT_API_BASE_URL = "http://localhost:8000";

function normalizeBaseUrl(value: string): string {
  return value.trim().replace(/\/+$/, "");
}

/**
 * Public base URL of the FastAPI backend.
 *
 * Read once at module scope so Next.js can inline the value at build
 * time. Never place secrets behind a NEXT_PUBLIC_ variable.
 */
export const API_BASE_URL: string = normalizeBaseUrl(
  process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL,
);
