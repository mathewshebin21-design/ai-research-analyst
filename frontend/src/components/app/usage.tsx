"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { date } from "@/lib/format";
import type { Usage } from "@/lib/types";
import { cn } from "@/lib/utils";

export function useUsage(workspaceId: string) {
  const [usage, setUsage] = useState<Usage | null>(null);
  useEffect(() => {
    let live = true;
    const load = () =>
      api<Usage>(`/workspaces/${workspaceId}/usage`)
        .then((u) => live && setUsage(u))
        .catch(() => live && setUsage(null));
    load();
    window.addEventListener("sih:runs-changed", load);
    return () => {
      live = false;
      window.removeEventListener("sih:runs-changed", load);
    };
  }, [workspaceId]);
  return usage;
}

/** Runs left this month: one run is used when research starts, whether by hand or by a monthly refresh. */
export function UsageMeter({ usage, className }: { usage: Usage | null; className?: string }) {
  if (!usage) return null;
  const share = usage.limit ? usage.runs_used / usage.limit : 1;
  const low = usage.remaining <= Math.max(1, Math.round(usage.limit * 0.1));
  // period_end is the first moment of next month, which is the day the allowance resets.
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <div className="flex items-baseline justify-between gap-2 text-[12px]">
        <span className={low ? "text-[var(--warn)]" : "text-[var(--muted)]"}>
          <strong className="tnum font-semibold text-[var(--fg)]">{usage.remaining}</strong> of {usage.limit} runs left
        </span>
        <span className="text-[11px] text-[var(--muted)]">resets {date(usage.period_end)}</span>
      </div>
      <div
        role="meter"
        aria-label="Runs used this month"
        aria-valuemin={0}
        aria-valuemax={usage.limit}
        aria-valuenow={usage.runs_used}
        className="h-1 w-full bg-[var(--line)]"
      >
        <div className={cn("h-full", low ? "bg-[var(--warn)]" : "bg-[var(--accent)]")} style={{ width: `${Math.min(100, share * 100)}%` }} />
      </div>
    </div>
  );
}
