import { beforeEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";

import { apiRequest } from "@/lib/api/api-client";
import { ApiError } from "@/lib/api/errors";

const schema = z.object({ value: z.string() });

type FetchSignature = (
  input: RequestInfo | URL,
  init?: RequestInit,
) => Promise<Response>;

function mockFetch(response: Response | Error) {
  const fetchMock = vi.fn<FetchSignature>(() =>
    response instanceof Error
      ? Promise.reject(response)
      : Promise.resolve(response),
  );

  vi.stubGlobal("fetch", fetchMock);

  return fetchMock;
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("apiRequest", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns validated data and sets JSON headers for a body", async () => {
    const fetchMock = mockFetch(jsonResponse({ value: "ok" }));

    const result = await apiRequest({
      method: "POST",
      path: "/api/v1/ask",
      body: { question: "hi" },
      schema,
    });

    expect(result).toEqual({ value: "ok" });

    const [url, init] = fetchMock.mock.calls[0];

    expect(url).toBe("http://localhost:8000/api/v1/ask");
    expect(init?.method).toBe("POST");
    expect(
      (init?.headers as Record<string, string>)["Content-Type"],
    ).toBe("application/json");
    expect(init?.body).toBe(JSON.stringify({ question: "hi" }));
  });

  it("throws a typed error carrying the backend message and code", async () => {
    mockFetch(
      jsonResponse(
        {
          error: {
            code: "session_not_found",
            message: "The requested session was not found.",
            details: {},
          },
        },
        404,
      ),
    );

    const error = await apiRequest({ path: "/api/v1/sessions/x", schema }).catch(
      (caught: unknown) => caught,
    );

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).status).toBe(404);
    expect((error as ApiError).code).toBe("session_not_found");
    expect((error as ApiError).isNotFound).toBe(true);
    expect((error as ApiError).message).toBe(
      "The requested session was not found.",
    );
  });

  it("distinguishes network failures from backend errors", async () => {
    mockFetch(new TypeError("Failed to fetch"));

    const error = (await apiRequest({ path: "/api/v1/health", schema }).catch(
      (caught: unknown) => caught,
    )) as ApiError;

    expect(error.isNetworkError).toBe(true);
    expect(error.message).toContain("Cannot reach the assistant service");
  });

  it("reports malformed JSON as a parse error", async () => {
    mockFetch(new Response("<html>oops</html>", { status: 200 }));

    const error = (await apiRequest({ path: "/api/v1/health", schema }).catch(
      (caught: unknown) => caught,
    )) as ApiError;

    expect(error.kind).toBe("parse");
  });

  it("reports a non-JSON error body by status instead of leaking it", async () => {
    mockFetch(
      new Response("Traceback (most recent call last): ...", { status: 500 }),
    );

    const error = (await apiRequest({ path: "/api/v1/ask", schema }).catch(
      (caught: unknown) => caught,
    )) as ApiError;

    expect(error.kind).toBe("http");
    expect(error.status).toBe(500);
    expect(error.message).toBe(
      "The assistant service reported an internal error.",
    );
    expect(error.message).not.toContain("Traceback");
  });

  it("rejects responses that do not match the schema", async () => {
    mockFetch(jsonResponse({ unexpected: 1 }));

    const error = (await apiRequest({ path: "/api/v1/health", schema }).catch(
      (caught: unknown) => caught,
    )) as ApiError;

    expect(error.kind).toBe("parse");
    expect(error.message).toContain("unexpected response format");
  });

  it("propagates aborts instead of wrapping them", async () => {
    const controller = new AbortController();

    vi.stubGlobal(
      "fetch",
      vi.fn<FetchSignature>(() => {
        controller.abort();

        return Promise.reject(
          new DOMException("The operation was aborted.", "AbortError"),
        );
      }),
    );

    const error = await apiRequest({
      path: "/api/v1/health",
      schema,
      signal: controller.signal,
    }).catch((caught: unknown) => caught);

    expect(error).toBeInstanceOf(DOMException);
  });
});
