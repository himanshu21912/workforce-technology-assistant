import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// jsdom does not implement element scrolling APIs used by the chat panel.
if (!Element.prototype.scrollTo) {
  Element.prototype.scrollTo = vi.fn();
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  window.history.replaceState({}, "", "/");
});
