"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { toErrorMessage } from "@/lib/api/errors";
import { useIsMounted } from "@/hooks/use-is-mounted";
import { getHealth } from "@/features/system-status/api/health.api";
import type {
  HealthResponse,
  ServiceIndicator,
} from "@/features/system-status/types/health.types";

const REFRESH_INTERVAL_MS = 45_000;

const DEPENDENCY_LABELS: Record<string, string> = {
  postgres: "PostgreSQL Database",
  redis: "Redis Cache",
  ollama: "Ollama LLM Service",
};

export interface UseSystemHealthResult {
  health: HealthResponse | null;
  indicators: ServiceIndicator[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

function buildIndicators(
  health: HealthResponse | null,
  isLoading: boolean,
  error: string | null,
): ServiceIndicator[] {
  const apiIndicator: ServiceIndicator = {
    key: "api",
    label: "FastAPI Service",
    status: health
      ? health.status === "ok"
        ? "connected"
        : "degraded"
      : isLoading
        ? "loading"
        : "unavailable",
    message: health ? null : error,
  };

  const dependencyKeys = health
    ? Object.keys(health.dependencies)
    : Object.keys(DEPENDENCY_LABELS);

  const dependencyIndicators = dependencyKeys.map<ServiceIndicator>((key) => {
    const dependency = health?.dependencies[key];

    return {
      key,
      label: DEPENDENCY_LABELS[key] ?? key,
      status: dependency
        ? dependency.status === "connected"
          ? "connected"
          : "unavailable"
        : isLoading
          ? "loading"
          : "unavailable",
      message: dependency?.message ?? null,
    };
  });

  return [apiIndicator, ...dependencyIndicators];
}

export function useSystemHealth(): UseSystemHealthResult {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isMounted = useIsMounted();
  const abortControllerRef = useRef<AbortController | null>(null);

  const refresh = useCallback(async () => {
    abortControllerRef.current?.abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await getHealth(controller.signal);

      if (!isMounted() || controller.signal.aborted) {
        return;
      }

      setHealth(response);
      setError(null);
    } catch (caught) {
      if (controller.signal.aborted || !isMounted()) {
        return;
      }

      setHealth(null);
      setError(
        toErrorMessage(caught, "System status is currently unavailable."),
      );
    } finally {
      if (isMounted() && !controller.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, [isMounted]);

  useEffect(() => {
    async function checkHealth() {
      await refresh();
    }

    void checkHealth();

    const interval = window.setInterval(() => {
      void checkHealth();
    }, REFRESH_INTERVAL_MS);

    return () => {
      window.clearInterval(interval);
      abortControllerRef.current?.abort();
    };
  }, [refresh]);

  return {
    health,
    indicators: buildIndicators(health, isLoading, error),
    isLoading,
    error,
    refresh,
  };
}
