"use client";

import {
  forwardRef,
  useImperativeHandle,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { SendHorizontal } from "lucide-react";

import { cn } from "@/lib/cn";
import { Spinner } from "@/components/ui/spinner";
import { QUESTION_MAX_LENGTH } from "@/features/chat/constants/suggested-prompts";

export interface QuestionComposerHandle {
  focus: () => void;
  setQuestion: (value: string) => void;
}

interface QuestionComposerProps {
  isSending: boolean;
  isSessionReady: boolean;
  onSubmit: (question: string) => void;
}

export const QuestionComposer = forwardRef<
  QuestionComposerHandle,
  QuestionComposerProps
>(function QuestionComposer({ isSending, isSessionReady, onSubmit }, ref) {
  const [question, setQuestion] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useImperativeHandle(ref, () => ({
    focus: () => textareaRef.current?.focus(),
    setQuestion: (value: string) => {
      setQuestion(value);
      textareaRef.current?.focus();
    },
  }));

  const trimmedQuestion = question.trim();
  const canSubmit = Boolean(trimmedQuestion) && isSessionReady && !isSending;

  const submit = () => {
    if (!canSubmit) {
      return;
    }

    onSubmit(trimmedQuestion);
    setQuestion("");
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  const disabledReason = !isSessionReady
    ? "Select or create a session to ask a question."
    : isSending
      ? "Waiting for the current answer."
      : undefined;

  return (
    <div className="border-t border-slate-100 bg-white px-5 py-4 sm:px-6">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          submit();
        }}
        className={cn(
          "rounded-xl border bg-white transition-colors",
          "border-slate-200 focus-within:border-brand/50 focus-within:ring-2 focus-within:ring-brand/15",
        )}
      >
        <div className="flex items-end gap-2 p-2.5">
          <label htmlFor="question-input" className="sr-only">
            Ask the assistant a question
          </label>
          <textarea
            id="question-input"
            ref={textareaRef}
            rows={2}
            value={question}
            maxLength={QUESTION_MAX_LENGTH}
            disabled={!isSessionReady}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question here..."
            aria-describedby="composer-hint"
            className="scroll-panel max-h-40 min-h-[3rem] flex-1 resize-y bg-transparent px-2 py-1.5 text-sm leading-6 text-slate-800 placeholder:text-slate-400 focus:outline-none disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!canSubmit}
            aria-label="Send question"
            title={disabledReason ?? "Send question"}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand text-white transition-colors hover:bg-brand-strong focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSending ? (
              <Spinner className="h-4 w-4" />
            ) : (
              <SendHorizontal className="h-4 w-4" aria-hidden="true" />
            )}
          </button>
        </div>
      </form>

      <div
        id="composer-hint"
        className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500"
      >
        <span>
          {disabledReason ?? (
            <>
              Press <kbd className="font-sans font-semibold">Enter</kbd> to send
              · <kbd className="font-sans font-semibold">Shift + Enter</kbd> for
              new line
            </>
          )}
        </span>
        {question.length > QUESTION_MAX_LENGTH - 500 ? (
          <span>
            {question.length}/{QUESTION_MAX_LENGTH}
          </span>
        ) : null}
      </div>
    </div>
  );
});
