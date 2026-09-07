import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { QuestionComposer } from "@/features/chat/components/question-composer";

function renderComposer(props: Partial<{ isSending: boolean; isSessionReady: boolean }> = {}) {
  const onSubmit = vi.fn();

  render(
    <QuestionComposer
      ref={{ current: null }}
      isSending={props.isSending ?? false}
      isSessionReady={props.isSessionReady ?? true}
      onSubmit={onSubmit}
    />,
  );

  return { onSubmit, textarea: screen.getByLabelText(/ask the assistant/i) };
}

describe("QuestionComposer", () => {
  it("sends the question on Enter and clears the input", async () => {
    const user = userEvent.setup();
    const { onSubmit, textarea } = renderComposer();

    await user.type(textarea, "Which internal employees know Python?");
    await user.keyboard("{Enter}");

    expect(onSubmit).toHaveBeenCalledExactlyOnceWith(
      "Which internal employees know Python?",
    );
    expect(textarea).toHaveValue("");
  });

  it("inserts a newline on Shift+Enter without sending", async () => {
    const user = userEvent.setup();
    const { onSubmit, textarea } = renderComposer();

    await user.type(textarea, "first line");
    await user.keyboard("{Shift>}{Enter}{/Shift}");
    await user.type(textarea, "second line");

    expect(onSubmit).not.toHaveBeenCalled();
    expect(textarea).toHaveValue("first line\nsecond line");
  });

  it("never sends a whitespace-only question", async () => {
    const user = userEvent.setup();
    const { onSubmit, textarea } = renderComposer();

    await user.type(textarea, "   ");
    await user.keyboard("{Enter}");

    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: /send question/i })).toBeDisabled();
  });

  it("explains why sending is disabled without a session", () => {
    renderComposer({ isSessionReady: false });

    expect(
      screen.getByText("Select or create a session to ask a question."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send question/i })).toBeDisabled();
  });

  it("blocks a duplicate send while a request is active", async () => {
    const user = userEvent.setup();
    const { onSubmit, textarea } = renderComposer({ isSending: true });

    await user.type(textarea, "Another question");
    await user.keyboard("{Enter}");

    expect(onSubmit).not.toHaveBeenCalled();
  });
});
