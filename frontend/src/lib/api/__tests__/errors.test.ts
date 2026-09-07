import { describe, expect, it } from "vitest";

import {
  ApiError,
  fallbackMessageForStatus,
  isApiError,
  parseErrorBody,
  toErrorMessage,
} from "@/lib/api/errors";

describe("parseErrorBody", () => {
  it("reads the application error format", () => {
    const parsed = parseErrorBody({
      error: {
        code: "session_not_found",
        message: "The requested session was not found.",
        details: { session_id: "abc" },
      },
    });

    expect(parsed).toEqual({
      code: "session_not_found",
      message: "The requested session was not found.",
      details: { session_id: "abc" },
    });
  });

  it("reads a FastAPI HTTPException dict detail", () => {
    const parsed = parseErrorBody({
      detail: {
        code: "session_not_found",
        message: "Session 123 was not found.",
      },
    });

    expect(parsed?.code).toBe("session_not_found");
    expect(parsed?.message).toBe("Session 123 was not found.");
  });

  it("reads a FastAPI HTTPException string detail", () => {
    expect(parseErrorBody({ detail: "Not authorised" })?.message).toBe(
      "Not authorised",
    );
  });

  it("reads FastAPI request validation errors", () => {
    const parsed = parseErrorBody({
      detail: [
        {
          loc: ["body", "question"],
          msg: "String should have at least 1 character",
          type: "string_too_short",
        },
      ],
    });

    expect(parsed?.kind).toBe("validation");
    expect(parsed?.message).toBe(
      "question: String should have at least 1 character",
    );
  });

  it("returns null for unrecognised payloads", () => {
    expect(parseErrorBody({ unexpected: true })).toBeNull();
    expect(parseErrorBody("plain text")).toBeNull();
  });
});

describe("ApiError", () => {
  it("identifies not-found responses by status or code", () => {
    expect(
      new ApiError({ kind: "http", message: "missing", status: 404 })
        .isNotFound,
    ).toBe(true);

    expect(
      new ApiError({
        kind: "http",
        message: "missing",
        status: 400,
        code: "session_not_found",
      }).isNotFound,
    ).toBe(true);

    expect(
      new ApiError({ kind: "http", message: "boom", status: 500 }).isNotFound,
    ).toBe(false);
  });

  it("is detected by the type guard", () => {
    expect(isApiError(new ApiError({ kind: "network", message: "x" }))).toBe(
      true,
    );
    expect(isApiError(new Error("x"))).toBe(false);
  });
});

describe("toErrorMessage", () => {
  it("prefers the API error message and falls back otherwise", () => {
    expect(
      toErrorMessage(new ApiError({ kind: "http", message: "Backend said no" })),
    ).toBe("Backend said no");
    expect(toErrorMessage({}, "fallback")).toBe("fallback");
  });
});

describe("fallbackMessageForStatus", () => {
  it("provides a readable message for unmapped statuses", () => {
    expect(fallbackMessageForStatus(418)).toContain("418");
  });
});
