import { describe, expect, it } from "vitest";

import { filterSessions } from "@/features/sessions/utils/filter-sessions";
import { buildSession } from "@/test/api-mocks";

const sessions = [
  buildSession({ session_id: "a", title: "Engineering Team Analysis" }),
  buildSession({ session_id: "b", title: "GitHub FastAPI Repos" }),
];

describe("filterSessions", () => {
  it("returns the backend order when the search term is empty", () => {
    expect(filterSessions(sessions, "   ")).toEqual(sessions);
  });

  it("matches titles case-insensitively", () => {
    expect(filterSessions(sessions, "fastapi")).toEqual([sessions[1]]);
  });

  it("returns nothing when no title matches", () => {
    expect(filterSessions(sessions, "kubernetes")).toEqual([]);
  });
});
