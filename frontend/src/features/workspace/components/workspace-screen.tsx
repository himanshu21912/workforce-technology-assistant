"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { toErrorMessage } from "@/lib/api/errors";
import { AppShell } from "@/components/layout/app-shell";
import { Drawer } from "@/components/layout/drawer";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { Toast } from "@/components/ui/toast";
import { ChatPanel } from "@/features/chat/components/chat-panel";
import type { QuestionComposerHandle } from "@/features/chat/components/question-composer";
import { useChat } from "@/features/chat/hooks/use-chat";
import { AboutCard } from "@/features/project-info/components/about-card";
import { SessionInfoCard } from "@/features/project-info/components/session-info-card";
import { RenameSessionDialog } from "@/features/sessions/components/rename-session-dialog";
import { SessionSidebar } from "@/features/sessions/components/session-sidebar";
import { useSelectedSessionId } from "@/features/sessions/hooks/use-selected-session-id";
import { useSessionHistory } from "@/features/sessions/hooks/use-session-history";
import { useSessions } from "@/features/sessions/hooks/use-sessions";
import { SystemStatusCard } from "@/features/system-status/components/system-status-card";
import { useSystemHealth } from "@/features/system-status/hooks/use-system-health";
import type { ChatSession } from "@/features/sessions/types/session.types";

export function WorkspaceScreen() {
  const sessionsState = useSessions();
  const { selectedSessionId, isRestoring, selectSession } =
    useSelectedSessionId();
  const historyState = useSessionHistory(selectedSessionId);
  const healthState = useSystemHealth();

  const composerRef = useRef<QuestionComposerHandle | null>(null);
  const hasBootstrappedRef = useRef(false);

  const [isSessionDrawerOpen, setIsSessionDrawerOpen] = useState(false);
  const [isInfoDrawerOpen, setIsInfoDrawerOpen] = useState(false);
  const [sessionToRename, setSessionToRename] = useState<ChatSession | null>(
    null,
  );
  const [renameError, setRenameError] = useState<string | null>(null);
  const [sessionToDelete, setSessionToDelete] = useState<ChatSession | null>(
    null,
  );
  const [isClearAllOpen, setIsClearAllOpen] = useState(false);
  const [isClearingAll, setIsClearingAll] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const {
    sessions,
    isLoading: isLoadingSessions,
    error: sessionsError,
    isCreating,
    pendingDeleteId,
    pendingRenameId,
    refresh: refreshSessions,
    createSession,
    renameSession,
    deleteSession,
    removeSessionLocally,
  } = sessionsState;

  const handleSelectSession = useCallback(
    (sessionId: string) => {
      selectSession(sessionId);
      setIsSessionDrawerOpen(false);
    },
    [selectSession],
  );

  const handleCreateSession = useCallback(async () => {
    try {
      const session = await createSession();

      selectSession(session.session_id);
      setIsSessionDrawerOpen(false);
      window.setTimeout(() => composerRef.current?.focus(), 0);
    } catch (caught) {
      setNotice(toErrorMessage(caught, "The session could not be created."));
    }
  }, [createSession, selectSession]);

  // Restore or establish a valid selection exactly once per mount.
  useEffect(() => {
    if (
      hasBootstrappedRef.current ||
      isRestoring ||
      isLoadingSessions ||
      sessionsError
    ) {
      return;
    }

    hasBootstrappedRef.current = true;

    async function bootstrapSelection() {
      const isSelectionValid =
        selectedSessionId !== null &&
        sessions.some((session) => session.session_id === selectedSessionId);

      if (isSelectionValid) {
        return;
      }

      if (sessions.length > 0) {
        if (selectedSessionId) {
          setNotice(
            "The previously opened session is no longer available. The most recent session was opened instead.",
          );
        }

        selectSession(sessions[0].session_id);

        return;
      }

      await handleCreateSession();
    }

    void bootstrapSelection();
  }, [
    isRestoring,
    isLoadingSessions,
    sessionsError,
    sessions,
    selectedSessionId,
    selectSession,
    handleCreateSession,
  ]);

  /** Recovers from a session that the backend no longer knows about. */
  const handleSessionMissing = useCallback(
    async (missingSessionId: string) => {
      removeSessionLocally(missingSessionId);
      setNotice("That session has expired. A different session was opened.");

      let availableSessions: ChatSession[] = [];

      try {
        availableSessions = await refreshSessions();
      } catch {
        availableSessions = [];
      }

      const nextSession = availableSessions.find(
        (session) => session.session_id !== missingSessionId,
      );

      if (nextSession) {
        selectSession(nextSession.session_id);

        return;
      }

      selectSession(null);
      await handleCreateSession();
    },
    [removeSessionLocally, refreshSessions, selectSession, handleCreateSession],
  );

  useEffect(() => {
    if (!historyState.isNotFound || !selectedSessionId) {
      return;
    }

    async function recoverMissingSession(missingSessionId: string) {
      await handleSessionMissing(missingSessionId);
    }

    void recoverMissingSession(selectedSessionId);
  }, [historyState.isNotFound, selectedSessionId, handleSessionMissing]);

  const serverMessages = useMemo(
    () => historyState.history?.messages ?? [],
    [historyState.history],
  );

  const handleTurnCompleted = useCallback(() => {
    void refreshSessions().catch(() => {
      // The sidebar keeps its previous state; the error surfaces on reload.
    });
  }, [refreshSessions]);

  const chat = useChat({
    sessionId: selectedSessionId,
    serverMessages,
    applyHistory: historyState.applyHistory,
    onTurnCompleted: handleTurnCompleted,
    onSessionMissing: (sessionId) => {
      void handleSessionMissing(sessionId);
    },
  });

  const selectedSession = useMemo(() => {
    if (historyState.history) {
      return historyState.history.session;
    }

    return (
      sessions.find((session) => session.session_id === selectedSessionId) ??
      null
    );
  }, [historyState.history, sessions, selectedSessionId]);

  const cacheHitCount = useMemo(
    () =>
      serverMessages.filter((message) => message.metadata.cache_hit === true)
        .length,
    [serverMessages],
  );

  const handleRenameSubmit = useCallback(
    async (title: string) => {
      if (!sessionToRename) {
        return;
      }

      setRenameError(null);

      try {
        const updated = await renameSession(sessionToRename.session_id, title);

        if (updated.session_id === selectedSessionId && historyState.history) {
          historyState.applyHistory({
            ...historyState.history,
            session: updated,
          });
        }

        setSessionToRename(null);
      } catch (caught) {
        setRenameError(
          toErrorMessage(caught, "The session could not be renamed."),
        );
      }
    },
    [sessionToRename, renameSession, selectedSessionId, historyState],
  );

  const handleDeleteConfirmed = useCallback(async () => {
    if (!sessionToDelete) {
      return;
    }

    const deletedSessionId = sessionToDelete.session_id;

    try {
      await deleteSession(deletedSessionId);
      setSessionToDelete(null);

      if (deletedSessionId !== selectedSessionId) {
        return;
      }

      const remaining = sessions.filter(
        (session) => session.session_id !== deletedSessionId,
      );

      if (remaining.length > 0) {
        selectSession(remaining[0].session_id);

        return;
      }

      selectSession(null);
      await handleCreateSession();
    } catch (caught) {
      setSessionToDelete(null);
      setNotice(toErrorMessage(caught, "The session could not be deleted."));
    }
  }, [
    sessionToDelete,
    deleteSession,
    selectedSessionId,
    sessions,
    selectSession,
    handleCreateSession,
  ]);

  const handleClearAllConfirmed = useCallback(async () => {
    setIsClearingAll(true);

    try {
      for (const session of [...sessions]) {
        await deleteSession(session.session_id);
      }

      selectSession(null);
      setIsClearAllOpen(false);
      await handleCreateSession();
    } catch (caught) {
      setNotice(
        toErrorMessage(caught, "The sessions could not all be deleted."),
      );
      await refreshSessions().catch(() => undefined);
    } finally {
      setIsClearingAll(false);
      setIsClearAllOpen(false);
    }
  }, [
    sessions,
    deleteSession,
    selectSession,
    handleCreateSession,
    refreshSessions,
  ]);

  const renderSidebar = (showBrandHeader: boolean) => (
    <SessionSidebar
      showBrandHeader={showBrandHeader}
      sessions={sessions}
      selectedSessionId={selectedSessionId}
      isLoading={isLoadingSessions}
      isCreating={isCreating}
      error={sessionsError}
      pendingDeleteId={pendingDeleteId}
      onRetry={() => {
        void refreshSessions().catch(() => undefined);
      }}
      onCreateSession={() => {
        void handleCreateSession();
      }}
      onSelectSession={handleSelectSession}
      onRenameSession={(session) => {
        setRenameError(null);
        setSessionToRename(session);
      }}
      onDeleteSession={setSessionToDelete}
      onClearAllSessions={() => setIsClearAllOpen(true)}
    />
  );

  const projectInfo = (
    <div className="space-y-3">
      <AboutCard />
      <SystemStatusCard
        indicators={healthState.indicators}
        health={healthState.health}
        isLoading={healthState.isLoading}
        error={healthState.error}
        onRefresh={() => {
          void healthState.refresh();
        }}
      />
      <SessionInfoCard
        session={selectedSession}
        cacheHitCount={cacheHitCount}
      />
    </div>
  );

  return (
    <>
      <AppShell
        sidebar={renderSidebar(true)}
        aside={projectInfo}
        main={
          <ChatPanel
            session={selectedSession}
            messages={chat.messages}
            isLoadingHistory={historyState.isLoading}
            isSending={chat.isSending}
            historyError={historyState.error}
            sendError={chat.error}
            canRetrySend={Boolean(chat.failedQuestion)}
            composerRef={composerRef}
            onSubmitQuestion={(question) => {
              void chat.sendQuestion(question);
            }}
            onSelectPrompt={(prompt) =>
              composerRef.current?.setQuestion(prompt)
            }
            onRefresh={() => {
              void historyState.reload();
              void refreshSessions().catch(() => undefined);
            }}
            onRetryHistory={() => {
              void historyState.reload();
            }}
            onRetrySend={() => {
              void chat.retryFailedQuestion();
            }}
            onDismissSendError={chat.dismissError}
            onRenameSession={() => {
              if (selectedSession) {
                setRenameError(null);
                setSessionToRename(selectedSession);
              }
            }}
            onOpenSessions={() => setIsSessionDrawerOpen(true)}
            onOpenProjectInfo={() => setIsInfoDrawerOpen(true)}
          />
        }
      />

      <Drawer
        isOpen={isSessionDrawerOpen}
        title="Sessions"
        side="left"
        onClose={() => setIsSessionDrawerOpen(false)}
        className="lg:hidden"
      >
        {renderSidebar(false)}
      </Drawer>

      <Drawer
        isOpen={isInfoDrawerOpen}
        title="About this assistant"
        side="right"
        onClose={() => setIsInfoDrawerOpen(false)}
        className="xl:hidden"
      >
        <div className="p-3">{projectInfo}</div>
      </Drawer>

      <RenameSessionDialog
        key={sessionToRename?.session_id ?? "no-session"}
        session={sessionToRename}
        isSaving={pendingRenameId !== null}
        error={renameError}
        onSubmit={(title) => {
          void handleRenameSubmit(title);
        }}
        onCancel={() => {
          setSessionToRename(null);
          setRenameError(null);
        }}
      />

      <ConfirmDialog
        isOpen={sessionToDelete !== null}
        title="Delete session"
        description={`"${sessionToDelete?.title ?? ""}" and its cached answers will be permanently removed.`}
        confirmLabel="Delete session"
        isConfirming={pendingDeleteId !== null}
        onConfirm={() => {
          void handleDeleteConfirmed();
        }}
        onCancel={() => setSessionToDelete(null)}
      />

      <ConfirmDialog
        isOpen={isClearAllOpen}
        title="Clear all sessions"
        description={`All ${sessions.length} sessions, their conversation history, and cached answers will be permanently removed.`}
        confirmLabel="Clear all sessions"
        isConfirming={isClearingAll}
        onConfirm={() => {
          void handleClearAllConfirmed();
        }}
        onCancel={() => setIsClearAllOpen(false)}
      />

      <Toast message={notice} onDismiss={() => setNotice(null)} />
    </>
  );
}
