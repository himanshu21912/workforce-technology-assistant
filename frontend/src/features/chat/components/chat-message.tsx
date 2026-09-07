"use client";

import { Bot, User } from "lucide-react";

import { cn } from "@/lib/cn";
import { formatTime } from "@/lib/format/date";
import { MarkdownContent } from "@/features/chat/components/markdown-content";
import { ResponseMetadata } from "@/features/chat/components/response-metadata";
import type { ChatMessage as ChatMessageModel } from "@/features/chat/types/chat.types";

interface ChatMessageProps {
  message: ChatMessageModel;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const timestamp = formatTime(message.created_at);

  return (
    <article className="flex gap-3">
      <span
        className={cn(
          "mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-brand-soft text-brand-strong" : "bg-emerald-50 text-emerald-700",
        )}
        aria-hidden="true"
      >
        {isUser ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </span>

      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <h3 className="text-sm font-semibold text-slate-900">
            {isUser ? "You" : "Assistant"}
          </h3>
          {timestamp ? (
            <time
              dateTime={message.created_at}
              className="text-xs text-slate-500"
            >
              {timestamp}
            </time>
          ) : null}
        </div>

        <div
          className={cn(
            "mt-1.5 rounded-xl border px-3.5 py-2.5",
            isUser
              ? "inline-block max-w-full border-brand/15 bg-brand-soft"
              : "border-emerald-100 bg-emerald-50/40",
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm leading-6 text-slate-800 [overflow-wrap:anywhere]">
              {message.content}
            </p>
          ) : (
            <>
              <MarkdownContent content={message.content} />
              <ResponseMetadata metadata={message.metadata} />
            </>
          )}
        </div>
      </div>
    </article>
  );
}
