"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "motion/react";

import { useSession } from "@/components/app/session";
import { ErrorNote, Eyebrow } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api, ApiError, streamEvents } from "@/lib/api";
import { date } from "@/lib/format";
import type { RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Dashboard } from "./dashboard";
import { EvidenceTab } from "./evidence-tab";
import { PlanEditor } from "./plan-editor";
import { Progress } from "./progress";
import { ResearchTab } from "./research-tab";

const tabs = [
  { id: "dashboard", label: "Executive dashboard" },
  { id: "research", label: "Research workspace" },
  { id: "evidence", label: "Evidence inspector" },
] as const;

export function RunView() {
  const params = useSearchParams();
  const router = useRouter();
  const { workspace } = useSession();
  const id = params.get("id") ?? "";
  const view = (params.get("view") as (typeof tabs)[number]["id"]) ?? "dashboard";
  const [run, setRun] = useState<RunDetail | null>(null);
  const [events, setEvents] = useState<{ agent: string; message: string; at: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const r = await api<RunDetail>(`/runs/${id}`);
      setRun((prev) => {
        if (prev && prev.status !== r.status) window.dispatchEvent(new Event("sih:runs-changed"));
        return r;
      });
      setEvents(r.events);
    } catch (e) {
      setError(e instanceof ApiError && e.status === 404 ? "This run does not exist or you no longer have access." : (e as Error).message);
    }
  }, [id]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (id) load();
  }, [id, load]);

  const active = run?.status === "queued" || run?.status === "running";
  useEffect(() => {
    if (!active || !run) return;
    const ctrl = new AbortController();
    const last = run.events.at(-1)?.id ?? 0;
    streamEvents(
      `/runs/${run.id}/events?after=${last}`,
      (e) => {
        if (e.event === "done") load();
        else setEvents((list) => [...list, JSON.parse(e.data)]);
      },
      ctrl.signal,
    ).catch(() => {});
    const poll = setInterval(load, 4000);
    return () => {
      ctrl.abort();
      clearInterval(poll);
    };
    // Re-subscribe only when the run starts or stops being active.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active, run?.id]);

  if (error) return <ErrorNote>{error}</ErrorNote>;
  if (!run) return <p className="text-sm text-[var(--muted)]">Loading…</p>;
  const canEdit = workspace.role !== "viewer";

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <Eyebrow>
          {run.workspace_name} · opened {date(run.created_at)}
          {run.finished_at ? ` · completed ${date(run.finished_at)}` : ""}
        </Eyebrow>
        <h1 className="font-disp max-w-[32ch] text-[clamp(26px,3.2vw,40px)] leading-[1.12]">{run.question}</h1>
      </header>

      {run.status === "planned" && <PlanEditor run={run} canEdit={canEdit} onChange={setRun} />}
      {active && <Progress run={run} events={events} />}
      {run.status === "failed" && (
        <div className="flex flex-col gap-4">
          <ErrorNote>The research run stopped: {run.error}</ErrorNote>
          <p className="text-[13.5px] text-[var(--muted)]">Nothing was invented to fill the gap. Retrying keeps the plan and starts the research again.</p>
          {canEdit && (
            <Button
              className="self-start"
              onClick={async () => {
                try {
                  await api(`/runs/${run.id}/start`, { method: "POST" });
                  load();
                } catch (e) {
                  setError((e as Error).message);
                }
              }}
            >
              Retry research
            </Button>
          )}
          {events.length > 0 && <Progress run={run} events={events} />}
        </div>
      )}
      {run.status === "completed" && (
        <>
          <nav aria-label="Run views" className="flex gap-1 overflow-x-auto border-b border-[var(--line)]">
            {tabs.map((t) => (
              <button
                key={t.id}
                type="button"
                aria-current={view === t.id ? "page" : undefined}
                onClick={() => router.replace(`/app/run?id=${run.id}&view=${t.id}`, { scroll: false })}
                className={cn(
                  "-mb-px border-b-2 px-3 py-2 text-[13.5px] whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                  view === t.id ? "border-[var(--accent)] text-[var(--fg)]" : "border-transparent text-[var(--muted)] hover:text-[var(--fg)]",
                )}
              >
                {t.label}
              </button>
            ))}
          </nav>
          <motion.div key={view} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            {view === "dashboard" && <Dashboard run={run} canEdit={canEdit} onRunChange={setRun} />}
            {view === "research" && <ResearchTab run={run} />}
            {view === "evidence" && <EvidenceTab run={run} canEdit={canEdit} onRunChange={setRun} />}
          </motion.div>
        </>
      )}
    </div>
  );
}
