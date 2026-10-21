"use client";

import { useState } from "react";
import { Plus, X } from "lucide-react";

import { ErrorNote, Eyebrow, Panel } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import type { RunDetail, RunSummary } from "@/lib/types";

const CATEGORIES = ["Market", "Customer", "Competition", "Financial", "Legal / risk", "Operations", "Other"];
type Draft = { title: string; category: string; queries: string[] };

export function PlanEditor({ run, canEdit, onChange }: { run: RunDetail; canEdit: boolean; onChange: (r: RunDetail) => void }) {
  const [tasks, setTasks] = useState<Draft[]>(run.tasks.map((t) => ({ title: t.title, category: t.category, queries: [...t.queries] })));
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const searches = tasks.reduce((n, t) => n + t.queries.filter((q) => q.trim()).length, 0);

  const update = (i: number, patch: Partial<Draft>) => {
    setTasks((ts) => ts.map((t, j) => (j === i ? { ...t, ...patch } : t)));
    setDirty(true);
  };

  async function start() {
    setBusy(true);
    setError(null);
    try {
      if (dirty) {
        const clean = tasks.map((t) => ({ ...t, queries: t.queries.map((q) => q.trim()).filter(Boolean) })).filter((t) => t.title.trim() && t.queries.length);
        onChange(await api<RunDetail>(`/runs/${run.id}/plan`, { method: "PUT", json: { tasks: clean } }));
      }
      const s = await api<RunSummary>(`/runs/${run.id}/start`, { method: "POST" });
      onChange({ ...run, ...s });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start the research.");
      setBusy(false);
    }
  }

  return (
    <Panel title="Research plan" aside={<span className="text-[12px] text-[var(--muted)]">{tasks.length} tasks · {searches} web searches</span>}>
      {run.objective && <p className="mb-6 max-w-[65ch] text-[14.5px] leading-7 text-[var(--muted)]">{run.objective}</p>}
      <ol className="flex flex-col">
        {tasks.map((t, i) => (
          <li key={i} className="grid gap-3 border-b border-[var(--line)] py-4 md:grid-cols-[36px_minmax(0,1fr)_auto]">
            <span className="tnum pt-2 text-[12px] text-[var(--accent)]">T{i + 1}</span>
            <div className="flex min-w-0 flex-col gap-2">
              <div className="flex flex-wrap gap-2">
                <input aria-label={`Task ${i + 1} title`} value={t.title} disabled={!canEdit} onChange={(e) => update(i, { title: e.target.value })} className="font-disp min-w-0 flex-1 px-2 py-1.5 text-[17px]" />
                <select aria-label={`Task ${i + 1} category`} value={t.category} disabled={!canEdit} onChange={(e) => update(i, { category: e.target.value })} className="px-2 py-1.5 text-[12.5px]">
                  {CATEGORIES.map((c) => (
                    <option key={c}>{c}</option>
                  ))}
                </select>
              </div>
              <Eyebrow>Searches</Eyebrow>
              {t.queries.map((q, j) => (
                <div key={j} className="flex gap-2">
                  <input
                    aria-label={`Task ${i + 1} search ${j + 1}`}
                    value={q}
                    disabled={!canEdit}
                    onChange={(e) => update(i, { queries: t.queries.map((x, k) => (k === j ? e.target.value : x)) })}
                    className="min-w-0 flex-1 px-2 py-1 text-[13px] text-[var(--muted)]"
                  />
                  {canEdit && t.queries.length > 1 && (
                    <button type="button" aria-label="Remove search" onClick={() => update(i, { queries: t.queries.filter((_, k) => k !== j) })} className="text-[var(--muted)] hover:text-[var(--fg)]">
                      <X className="size-4" />
                    </button>
                  )}
                </div>
              ))}
              {canEdit && t.queries.length < 3 && (
                <button type="button" onClick={() => update(i, { queries: [...t.queries, ""] })} className="self-start text-[12px] text-[var(--accent)]">
                  + Add search
                </button>
              )}
            </div>
            {canEdit && tasks.length > 1 && (
              <button type="button" aria-label={`Remove task ${i + 1}`} onClick={() => { setTasks(tasks.filter((_, k) => k !== i)); setDirty(true); }} className="self-start text-[12px] text-[var(--muted)] hover:text-[var(--bad)]">
                Remove
              </button>
            )}
          </li>
        ))}
      </ol>
      {canEdit && (
        <div className="mt-5 flex flex-wrap items-center gap-4">
          {tasks.length < 10 && (
            <Button variant="outline" size="sm" onClick={() => { setTasks([...tasks, { title: "", category: "Other", queries: [""] }]); setDirty(true); }}>
              <Plus /> Add task
            </Button>
          )}
          <Button onClick={start} disabled={busy || searches === 0}>
            {busy ? "Starting…" : "Approve plan and start research"}
          </Button>
          <span className="text-[12px] text-[var(--muted)]">Typically 2–5 minutes. You can leave this page.</span>
        </div>
      )}
      {error && <div className="mt-4"><ErrorNote>{error}</ErrorNote></div>}
    </Panel>
  );
}
