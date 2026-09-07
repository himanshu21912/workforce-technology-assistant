"use client";

import { ArrowDown } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { AssistantThinking } from "@/features/chat/components/assistant-thinking";
import { ChatMessage } from "@/features/chat/components/chat-message";
import { EmptyConversation } from "@/features/chat/components/empty-conversation";
import { useChatScroll } from "@/features/chat/hooks/use-chat-scroll";
import type { ChatMessage as ChatMessageModel } from "@/features/chat/types/chat.types";

interface MessageListProps {
  messages: ChatMessageModel[];
  sessionId: string | null;
  isLoadingHistory: boolean;
  isAwaitingAnswer: boolean;
  onSelectPrompt: (prompt: string) => void;
}

function HistorySkeleton() {
  return (
    <div className="space-y-6" aria-busy="true">
      <span className="sr-only">Loading conversation</span>
      {[0, 1].map((item) => (
        <div key={item} className="flex gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-16 w-full rounded-xl" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function MessageList({
  messages,
  sessionId,
  isLoadingHistory,
  isAwaitingAnswer,
  onSelectPrompt,
}: MessageListProps) {
  const visibleMessages = messages.filter(
    (message) => message.role === "user" || message.role === "assistant",
  );

  const { containerRef, isPinnedToBottom, scrollToBottom } = useChatScroll({
    messageCount: visibleMessages.length + (isAwaitingAnswer ? 1 : 0),
    sessionId,
  });

  return (
    <div className="relative min-h-0 flex-1">
      <div
        ref={containerRef}
        className="scroll-panel h-full overflow-y-auto px-5 py-5 sm:px-6"
      >
        {isLoadingHistory ? (
          <HistorySkeleton />
        ) : visibleMessages.length === 0 && !isAwaitingAnswer ? (
          <EmptyConversation onSelectPrompt={onSelectPrompt} />
        ) : (
          <div className="space-y-6">
            {visibleMessages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isAwaitingAnswer ? <AssistantThinking /> : null}
          </div>
        )}
      </div>

      {!isPinnedToBottom && visibleMessages.length > 0 ? (
        <button
          type="button"
          onClick={() => scrollToBottom("smooth")}
          className="absolute bottom-4 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 shadow-md hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand"
        >
          <ArrowDown className="h-3.5 w-3.5" aria-hidden="true" />
          Jump to latest
        </button>
      ) : null}
    </div>
  );
}
