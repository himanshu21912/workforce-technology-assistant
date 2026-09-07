"use client";

import { useEffect, useId, useRef, useState } from "react";
import { MoreVertical, Pencil, Trash2 } from "lucide-react";

import { IconButton } from "@/components/ui/icon-button";

interface SessionActionsMenuProps {
  sessionTitle: string;
  onRename: () => void;
  onDelete: () => void;
}

export function SessionActionsMenu({
  sessionTitle,
  onRename,
  onDelete,
}: SessionActionsMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const menuId = useId();

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const handlePointerDown = (event: PointerEvent) => {
      if (
        containerRef.current &&
        event.target instanceof Node &&
        !containerRef.current.contains(event.target)
      ) {
        setIsOpen(false);
      }
    };

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return (
    <div ref={containerRef} className="relative">
      <IconButton
        label={`Actions for ${sessionTitle}`}
        aria-haspopup="menu"
        aria-expanded={isOpen}
        aria-controls={isOpen ? menuId : undefined}
        onClick={() => setIsOpen((current) => !current)}
        className="h-7 w-7"
      >
        <MoreVertical className="h-4 w-4" aria-hidden="true" />
      </IconButton>

      {isOpen ? (
        <div
          id={menuId}
          role="menu"
          aria-label={`Actions for ${sessionTitle}`}
          className="absolute right-0 z-20 mt-1 w-40 overflow-hidden rounded-lg border border-slate-200 bg-white py-1 shadow-lg"
        >
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setIsOpen(false);
              onRename();
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50 focus-visible:bg-slate-50 focus-visible:outline-none"
          >
            <Pencil className="h-3.5 w-3.5" aria-hidden="true" />
            Rename
          </button>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setIsOpen(false);
              onDelete();
            }}
            className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50 focus-visible:bg-rose-50 focus-visible:outline-none"
          >
            <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
            Delete
          </button>
        </div>
      ) : null}
    </div>
  );
}
