"use client";

import { Database, Sparkles, Wrench } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  formatSimilarityScore,
  getSourceLabel,
  getToolLabel,
} from "@/features/chat/constants/response-labels";
import type { MessageMetadata } from "@/features/chat/types/chat.types";

interface ResponseMetadataProps {
  metadata: MessageMetadata;
}

/**
 * Compact footer describing where an answer came from. Kept secondary to
 * the answer itself, and never shows raw internal identifiers.
 */
export function ResponseMetadata({ metadata }: ResponseMetadataProps) {
  const source = getSourceLabel(metadata.source);
  const toolsUsed = metadata.tools_used ?? [];
  const similarity = formatSimilarityScore(metadata.similarity_score);
  const hasCacheHit = metadata.cache_hit === true;

  if (!metadata.source && toolsUsed.length === 0 && !hasCacheHit) {
    return null;
  }

  return (
    <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-slate-100 pt-2.5">
      {metadata.source ? (
        <Badge className={source.className} title={source.description}>
          <Database className="h-3 w-3" aria-hidden="true" />
          {source.label}
        </Badge>
      ) : null}

      {hasCacheHit ? (
        <Badge
          className="border-amber-200 bg-amber-50 text-amber-800"
          title="This answer was reused from the session semantic cache."
        >
          <Sparkles className="h-3 w-3" aria-hidden="true" />
          Semantic cache
          {similarity ? <span className="font-normal">· {similarity}</span> : null}
        </Badge>
      ) : null}

      {toolsUsed.map((toolName) => (
        <Badge key={toolName} className="border-slate-200 bg-white text-slate-600">
          <Wrench className="h-3 w-3" aria-hidden="true" />
          {getToolLabel(toolName)}
        </Badge>
      ))}

      {metadata.model_name ? (
        <span className="text-[11px] text-slate-500">
          Model: {metadata.model_name}
        </span>
      ) : null}
    </div>
  );
}
