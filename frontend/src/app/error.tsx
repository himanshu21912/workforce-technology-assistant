"use client";

import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // The message is intentionally not rendered: it may contain internals.
    void error;
  }, [error]);

  return (
    <div className="flex h-dvh flex-col items-center justify-center bg-canvas px-6 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-rose-50 text-rose-600">
        <AlertTriangle className="h-6 w-6" aria-hidden="true" />
      </span>
      <h1 className="mt-4 text-lg font-semibold text-slate-900">
        The assistant could not be loaded
      </h1>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">
        An unexpected error interrupted the application. Reloading usually
        resolves it. If the problem continues, check that the backend service is
        running.
      </p>
      <Button className="mt-5" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}
