import { StrictMode } from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { WorkspaceScreen } from "@/features/workspace/components/workspace-screen";
import {
  buildMessage,
  buildSession,
  healthPayload,
  jsonResponse,
  mockApi,
  type RouteHandler,
} from "@/test/api-mocks";

const SESSION_ID = "11111111-1111-4111-8111-111111111111";
const OTHER_SESSION_ID = "33333333-3333-4333-8333-333333333333";

const sessionPath = `/api/v1/sessions/${SESSION_ID}`;
const otherSessionPath = `/api/v1/sessions/${OTHER_SESSION_ID}`;

const assistantMessage = buildMessage({
  id: "44444444-4444-4444-8444-444444444444",
  role: "assistant",
  content: "Ravi Kumar and Ananya Sharma know Python.",
  created_at: "2026-09-08T10:02:00Z",
  metadata: {
    source: "postgresql",
    tools_used: ["search_employees"],
    cache_hit: false,
    similarity_score: null,
  },
});

function selectSessionInUrl(sessionId: string) {
  window.history.replaceState({}, "", `/?session=${sessionId}`);
}

describe("WorkspaceScreen", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the session loading state and then the session list", async () => {
    selectSessionInUrl(SESSION_ID);

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession()] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [] }),
    });

    render(<WorkspaceScreen />);

    expect(screen.getByText("Loading sessions")).toBeInTheDocument();

    expect(
      await screen.findByRole("list", { name: /conversation sessions/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /^Engineering Team Analysis/i }),
    ).toBeInTheDocument();
  });

  it("renders the empty chat state with suggested prompts", async () => {
    selectSessionInUrl(SESSION_ID);

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession()] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [] }),
    });

    render(<WorkspaceScreen />);

    expect(
      await screen.findByText("Ask about your workforce and technology"),
    ).toBeInTheDocument();

    const promptButton = screen.getByRole("button", {
      name: "Which internal employees know Python?",
    });

    await userEvent.click(promptButton);

    expect(screen.getByLabelText(/ask the assistant/i)).toHaveValue(
      "Which internal employees know Python?",
    );
  });

  it("renders the stored history for the selected session", async () => {
    selectSessionInUrl(SESSION_ID);

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession({ message_count: 2 })] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({
          session: buildSession({ message_count: 2 }),
          messages: [buildMessage(), assistantMessage],
        }),
    });

    render(<WorkspaceScreen />);

    expect(
      await screen.findByText("Ravi Kumar and Ananya Sharma know Python."),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Which internal employees know Python?"),
    ).toBeInTheDocument();
    expect(screen.getByText("Internal workforce data")).toBeInTheDocument();
    expect(screen.getByText("Employee search")).toBeInTheDocument();
  });

  it("creates a session when none exist and selects it", async () => {
    const createdSession = buildSession({
      session_id: OTHER_SESSION_ID,
      title: "New conversation",
    });

    const fetchMock = mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () => jsonResponse({ count: 0, sessions: [] }),
      "POST /api/v1/sessions": () => jsonResponse(createdSession, 201),
      [`GET ${otherSessionPath}`]: () =>
        jsonResponse({ session: createdSession, messages: [] }),
    });

    // Strict Mode runs effects twice: bootstrapping must stay idempotent.
    render(
      <StrictMode>
        <WorkspaceScreen />
      </StrictMode>,
    );

    expect(
      await screen.findByRole("heading", { name: "New conversation", level: 1 }),
    ).toBeInTheDocument();

    const createCalls = fetchMock.mock.calls.filter(
      ([, init]) => (init as RequestInit | undefined)?.method === "POST",
    );

    // React Strict Mode double effects must not create duplicate sessions.
    expect(createCalls).toHaveLength(1);
    expect(window.location.search).toBe(`?session=${OTHER_SESSION_ID}`);
  });

  it("sends a question, shows the answer, and refreshes the session list", async () => {
    const user = userEvent.setup();

    selectSessionInUrl(SESSION_ID);

    let historyCallCount = 0;

    const fetchMock = mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession()] }),
      "POST /api/v1/ask": () =>
        jsonResponse({
          session_id: SESSION_ID,
          answer: "Ravi Kumar and Ananya Sharma know Python.",
          cache_hit: true,
          similarity_score: 0.96,
          source: "postgresql",
          tools_used: ["search_employees"],
          model_name: "qwen3:8b",
        }),
      [`GET ${sessionPath}`]: () => {
        historyCallCount += 1;

        return jsonResponse({
          session: buildSession({ message_count: historyCallCount > 1 ? 2 : 0 }),
          messages:
            historyCallCount > 1
              ? [
                  buildMessage(),
                  {
                    ...assistantMessage,
                    metadata: {
                      source: "postgresql",
                      tools_used: ["search_employees"],
                      cache_hit: true,
                      similarity_score: 0.96,
                    },
                  },
                ]
              : [],
        });
      },
    });

    render(<WorkspaceScreen />);

    const textarea = await screen.findByLabelText(/ask the assistant/i);

    await user.type(textarea, "Which internal employees know Python?");
    await user.keyboard("{Enter}");

    expect(
      await screen.findByText("Ravi Kumar and Ananya Sharma know Python."),
    ).toBeInTheDocument();

    // The optimistic question is replaced by, not duplicated alongside,
    // the authoritative history.
    expect(
      screen.getAllByText("Which internal employees know Python?"),
    ).toHaveLength(1);

    expect(screen.getByText(/Semantic cache/)).toBeInTheDocument();
    expect(screen.getByText("· 96% match")).toBeInTheDocument();

    const askCalls = fetchMock.mock.calls.filter(([url]) =>
      String(url).endsWith("/api/v1/ask"),
    );

    expect(askCalls).toHaveLength(1);
    expect(JSON.parse(String((askCalls[0][1] as RequestInit).body))).toEqual({
      session_id: SESSION_ID,
      question: "Which internal employees know Python?",
      context: null,
    });

    await waitFor(() => {
      const sessionListCalls = fetchMock.mock.calls.filter(([url]) =>
        String(url).includes("/api/v1/sessions?limit="),
      );

      expect(sessionListCalls.length).toBeGreaterThan(1);
    });
  });

  it("keeps the question available for retry when the ask request fails", async () => {
    const user = userEvent.setup();

    selectSessionInUrl(SESSION_ID);

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession()] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [] }),
      "POST /api/v1/ask": () =>
        jsonResponse(
          {
            error: {
              code: "agent_execution_failed",
              message: "The AI assistant could not complete the request.",
              details: {},
            },
          },
          502,
        ),
    });

    render(<WorkspaceScreen />);

    const textarea = await screen.findByLabelText(/ask the assistant/i);

    await user.type(textarea, "Find popular FastAPI repositories on GitHub.");
    await user.keyboard("{Enter}");

    expect(
      await screen.findByText(
        "The AI assistant could not complete the request.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("switches to another session and loads its own history", async () => {
    const user = userEvent.setup();

    selectSessionInUrl(SESSION_ID);

    const otherSession = buildSession({
      session_id: OTHER_SESSION_ID,
      title: "GitHub FastAPI Repos",
    });

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 2, sessions: [buildSession(), otherSession] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [buildMessage()] }),
      [`GET ${otherSessionPath}`]: () =>
        jsonResponse({
          session: otherSession,
          messages: [
            buildMessage({
              id: "55555555-5555-4555-8555-555555555555",
              role: "assistant",
              content: "tiangolo/fastapi is the most popular option.",
              metadata: {
                source: "github_mcp",
                tools_used: ["search_github_repositories"],
                cache_hit: false,
              },
            }),
          ],
        }),
    });

    render(<WorkspaceScreen />);

    await screen.findByText("Which internal employees know Python?");

    await user.click(
      screen.getByRole("button", { name: /^GitHub FastAPI Repos/i }),
    );

    expect(
      await screen.findByText("tiangolo/fastapi is the most popular option."),
    ).toBeInTheDocument();
    expect(screen.getByText("Current GitHub data")).toBeInTheDocument();
    expect(
      screen.queryByText("Which internal employees know Python?"),
    ).not.toBeInTheDocument();
    expect(window.location.search).toBe(`?session=${OTHER_SESSION_ID}`);
  });

  it("deletes a session after confirmation and selects the next one", async () => {
    const user = userEvent.setup();

    selectSessionInUrl(SESSION_ID);

    const otherSession = buildSession({
      session_id: OTHER_SESSION_ID,
      title: "GitHub FastAPI Repos",
    });

    const deleteHandler = vi.fn<RouteHandler>(() =>
      jsonResponse({
        session_id: SESSION_ID,
        session_deleted: true,
        semantic_cache_entries_deleted: 2,
      }),
    );

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 2, sessions: [buildSession(), otherSession] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [] }),
      [`GET ${otherSessionPath}`]: () =>
        jsonResponse({ session: otherSession, messages: [] }),
      [`DELETE ${sessionPath}`]: deleteHandler,
    });

    render(<WorkspaceScreen />);

    await screen.findByRole("list", { name: /conversation sessions/i });

    await user.click(
      screen.getByRole("button", { name: /Actions for Engineering Team Analysis/i }),
    );
    await user.click(screen.getByRole("menuitem", { name: "Delete" }));

    const dialog = await screen.findByRole("dialog", { name: "Delete session" });

    await user.click(
      within(dialog).getByRole("button", { name: "Delete session" }),
    );

    await waitFor(() => expect(deleteHandler).toHaveBeenCalledOnce());

    await waitFor(() =>
      expect(window.location.search).toBe(`?session=${OTHER_SESSION_ID}`),
    );
    expect(
      screen.queryByRole("button", { name: /^Engineering Team Analysis/i }),
    ).not.toBeInTheDocument();
  });

  it("renames a session through the actions menu", async () => {
    const user = userEvent.setup();

    selectSessionInUrl(SESSION_ID);

    const renamedSession = buildSession({ title: "Backend Skills Overview" });

    const renameHandler = vi.fn<RouteHandler>(() =>
      jsonResponse(renamedSession),
    );

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession()] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [] }),
      [`PATCH ${sessionPath}`]: renameHandler,
    });

    render(<WorkspaceScreen />);

    await screen.findByRole("list", { name: /conversation sessions/i });

    await user.click(
      screen.getByRole("button", {
        name: /Actions for Engineering Team Analysis/i,
      }),
    );
    await user.click(screen.getByRole("menuitem", { name: "Rename" }));

    const dialog = await screen.findByRole("dialog", { name: "Rename session" });
    const input = within(dialog).getByLabelText("Session title");

    await user.clear(input);
    await user.type(input, "Backend Skills Overview");
    await user.click(
      within(dialog).getByRole("button", { name: "Save changes" }),
    );

    await waitFor(() => expect(renameHandler).toHaveBeenCalledOnce());

    expect(renameHandler.mock.calls[0][0].body).toEqual({
      title: "Backend Skills Overview",
    });
    expect(
      await screen.findByRole("heading", {
        name: "Backend Skills Overview",
        level: 1,
      }),
    ).toBeInTheDocument();
  });

  it("recovers when the selected session is no longer on the backend", async () => {
    const recoverySession = buildSession({
      session_id: OTHER_SESSION_ID,
      title: "Python Developers Search",
    });

    selectSessionInUrl(SESSION_ID);

    let sessionListCallCount = 0;

    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () => {
        sessionListCallCount += 1;

        return jsonResponse(
          sessionListCallCount === 1
            ? { count: 1, sessions: [buildSession()] }
            : { count: 1, sessions: [recoverySession] },
        );
      },
      [`GET ${sessionPath}`]: () =>
        jsonResponse(
          {
            detail: {
              code: "session_not_found",
              message: "The requested session was not found.",
            },
          },
          404,
        ),
      [`GET ${otherSessionPath}`]: () =>
        jsonResponse({ session: recoverySession, messages: [] }),
    });

    render(<WorkspaceScreen />);

    expect(
      await screen.findByText(/That session has expired/i),
    ).toBeInTheDocument();

    await waitFor(() =>
      expect(window.location.search).toBe(`?session=${OTHER_SESSION_ID}`),
    );
    expect(
      await screen.findByRole("heading", {
        name: "Python Developers Search",
        level: 1,
      }),
    ).toBeInTheDocument();
  });

  it("shows backend health and reports an unreachable backend", async () => {
    selectSessionInUrl(SESSION_ID);

    mockApi({
      "GET /api/v1/health": () =>
        jsonResponse({
          ...healthPayload,
          status: "degraded",
          dependencies: {
            ...healthPayload.dependencies,
            ollama: { status: "unavailable", message: "OllamaUnavailableError" },
          },
        }),
      "GET /api/v1/sessions": () =>
        jsonResponse({ count: 1, sessions: [buildSession()] }),
      [`GET ${sessionPath}`]: () =>
        jsonResponse({ session: buildSession(), messages: [] }),
    });

    render(<WorkspaceScreen />);

    const status = await screen.findByRole("region", { name: /system status/i });

    expect(
      within(status).getByText("Some services are degraded"),
    ).toBeInTheDocument();
    expect(within(status).getByText("Unavailable")).toBeInTheDocument();
    // FastAPI reports "degraded" overall; Postgres and Redis stay healthy.
    expect(within(status).getByText("Degraded")).toBeInTheDocument();
    expect(within(status).getAllByText("Healthy")).toHaveLength(2);
  });

  it("surfaces a session-list failure with a retry action", async () => {
    mockApi({
      "GET /api/v1/health": () => jsonResponse(healthPayload),
      "GET /api/v1/sessions": () =>
        jsonResponse(
          {
            error: {
              code: "application_error",
              message: "Sessions are temporarily unavailable.",
              details: {},
            },
          },
          500,
        ),
    });

    render(<WorkspaceScreen />);

    expect(
      await screen.findByText("Sessions are temporarily unavailable."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
  });
});
