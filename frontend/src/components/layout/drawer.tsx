"use client";

import { useEffect, type ReactNode } from "react";
import { X } from "lucide-react";

import { cn } from "@/lib/cn";
import { IconButton } from "@/components/ui/icon-button";

interface DrawerProps {
  isOpen: boolean;
  title: string;
  side: "left" | "right";
  onClose: () => void;
  children: ReactNode;
  className?: string;
}

/** Off-canvas panel used for the sidebar and About panel on small screens. */
export function Drawer({
  isOpen,
  title,
  side,
  onClose,
  children,
  className,
}: DrawerProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className={cn("fixed inset-0 z-40", className)}>
      <button
        type="button"
        aria-label={`Close ${title}`}
        onClick={onClose}
        className="absolute inset-0 cursor-default bg-slate-900/40"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={cn(
          "absolute inset-y-0 flex w-[88%] max-w-sm flex-col bg-white shadow-xl",
          side === "left" ? "left-0" : "right-0",
        )}
      >
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
          <IconButton label={`Close ${title}`} onClick={onClose}>
            <X className="h-4 w-4" aria-hidden="true" />
          </IconButton>
        </div>
        <div className="scroll-panel min-h-0 flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
}
