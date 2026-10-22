"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RefreshCw } from "lucide-react";

import { ErrorNote, Eyebrow, Panel } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { date, money, statusLabel } from "@/lib/format";
import type { Changes, RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

/** Re-run the same question and plan later, by hand or every month, and compare with this run. */
export function RefreshPanel({ run, canEdit, onRunChange }: { run: RunDetail; canEdit: boolean; onRunChange: (r: RunDetail) => void }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  if (!canEdit) return null;

  async function refresh() {
    setBusy(true);
    try {
      const next = await api<RunDetail>(`/runs/${run.id}/refresh`, { method: "POST" });
      window.dispatchEvent(new Event("sih:runs-changed"));
      router.push(`/app/run?id=${next.id}`);
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  }

  async function schedule(monthly: boolean) {
    try {
      await api(`/runs/${run.id}/refresh-schedule`, { method: "PUT", json: { monthly } });
      onRunChange({ ...run, refresh_monthly: monthly });
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <Panel
      title="Keep this decision current"
      aside={
        <Button size="sm" variant="outline" onClick={refresh} disabled={busy}>
          <RefreshCw /> {busy ? "Preparing…" : "Refresh with new data"}
        </Button>
      }
    >
      {error && <div className="mb-4"><ErrorNote>{error}</ErrorNote></div>}
      <p className="max-w-[72ch] text-[13.5px] leading-6 text-[var(--muted)]">
        A refresh asks the same question with the same reviewed plan and searches again, then shows what changed: the verdict, claims whose
        evidence moved, new and dropped sources, and the base case. You can edit the plan before it starts. Starting a refresh uses one run.
      </p>
      <label className="mt-4 flex items-center gap-2.5 text-[13.5px]">
        <input type="checkbox" checked={run.refresh_monthly} onChange={(e) => schedule(e.target.checked)} className="size-4 accent-[var(--accent)]" />
        Refresh automatically every month
      </label>
      <p className="mt-1 pl-6.5 text-[12px] text-[var(--muted)]">
        {run.refresh_monthly
          ? `The next refresh starts about a month after ${date(run.finished_at)}, if the workspace has runs left.`
          : "Off. Each automatic refresh uses one run from the monthly allowance."}
      </p>
    </Panel>
  );
}

const fmtFigure = (key: string, v: number | null, sym: string) =>
  v === null ? "Not reached" : key === "break_even_month" ? `Month ${v}` : money(key === "peak_funding" ? -v : v, sym);

export function ChangesPanel({ changes, sym, linkPrevious }: { changes: Changes; sym: string; linkPrevious: boolean }) {
  const v = changes.verdict;
  const verdictMoved = v.before !== v.after || v.score_before !== v.score_after;
  const nothing =
    !verdictMoved &&
    !changes.claims_changed.length &&
    !changes.claims_new.length &&
    !changes.claims_dropped.length &&
    !changes.sources_new.length &&
    !changes.sources_dropped.length &&
    !changes.figures.length &&
    !changes.competitors_new.length &&
    !changes.competitors_dropped.length;
  const since = date(changes.previous_finished_at);
  return (
    <Panel
      title={`What changed since ${since}`}
      aside={
        linkPrevious && (
          <Link href={`/app/run?id=${changes.previous_run_id}`} className="text-[12.5px] text-[var(--accent)]">
            Open the earlier run
          </Link>
        )
      }
    >
      <div className="mb-5 flex flex-wrap items-baseline gap-x-6 gap-y-2 border border-[var(--line)] bg-[var(--surface)] px-5 py-4 text-[14px]">
        <Eyebrow>Verdict</Eyebrow>
        {verdictMoved ? (
          <span>
            {v.before} <span className="tnum text-[var(--muted)]">({v.score_before})</span> → <strong className="font-semibold">{v.after}</strong>{" "}
            <span className="tnum text-[var(--muted)]">({v.score_after})</span>
          </span>
        ) : (
          <span>
            Unchanged: {v.after} <span className="tnum text-[var(--muted)]">({v.score_after})</span>
          </span>
        )}
      </div>
      {nothing ? (
        <p className="text-[13.5px] text-[var(--muted)]">The new search found the same evidence: no claim, source, figure or competitor changed.</p>
      ) : (
        <div className="grid gap-8 lg:grid-cols-2">
          <ChangeList title="Claims whose evidence moved">
            {changes.claims_changed.map((c) => (
              <li key={c.after.key}>
                <span className="text-[var(--muted)]">{c.after.key}</span> {c.after.text}
                <span className="block text-[12px]">
                  <Tone status={c.before.status} /> → <Tone status={c.after.status} />
                </span>
              </li>
            ))}
          </ChangeList>
          <ChangeList title="New claims">
            {changes.claims_new.map((c) => (
              <li key={c.key}>
                <span className="text-[var(--muted)]">{c.key}</span> {c.text} <span className="block text-[12px]"><Tone status={c.status} /></span>
              </li>
            ))}
          </ChangeList>
          <ChangeList title="Claims no longer found">
            {changes.claims_dropped.map((c) => (
              <li key={c.key} className="text-[var(--muted)]">
                {c.text}
              </li>
            ))}
          </ChangeList>
          <ChangeList title="Base case">
            {changes.figures.map((f) => (
              <li key={f.key} className="flex flex-wrap justify-between gap-2">
                <span>{f.label}</span>
                <span className="tnum">
                  {fmtFigure(f.key, f.before, sym)} → <strong className="font-semibold">{fmtFigure(f.key, f.after, sym)}</strong>
                </span>
              </li>
            ))}
          </ChangeList>
          <ChangeList title="Sources">
            {changes.sources_new.map((s) => (
              <li key={`n-${s.key}`}>
                <span className="text-[var(--ok)]">New</span> {s.title}
              </li>
            ))}
            {changes.sources_dropped.map((s) => (
              <li key={`d-${s.key}`} className="text-[var(--muted)]">
                <span className="text-[var(--bad)]">Dropped</span> {s.title}
              </li>
            ))}
          </ChangeList>
          <ChangeList title="Competitors">
            {changes.competitors_new.map((c) => (
              <li key={`n-${c}`}>
                <span className="text-[var(--ok)]">New</span> {c}
              </li>
            ))}
            {changes.competitors_dropped.map((c) => (
              <li key={`d-${c}`} className="text-[var(--muted)]">
                <span className="text-[var(--bad)]">No longer named</span> {c}
              </li>
            ))}
          </ChangeList>
        </div>
      )}
      <p className="mt-5 text-[12px] text-[var(--muted)]">
        {changes.claims_unchanged} claims kept the same status. {changes.method}
      </p>
    </Panel>
  );
}

function ChangeList({ title, children }: { title: string; children: React.ReactNode[] }) {
  if (!children.flat().length) return null;
  return (
    <div className="min-w-0">
      <Eyebrow className="mb-2">{title}</Eyebrow>
      <ul className="flex flex-col gap-2.5 text-[13.5px] leading-6">{children}</ul>
    </div>
  );
}

function Tone({ status }: { status: keyof typeof statusLabel }) {
  const tone = { supported: "text-[var(--ok)]", partial: "text-[var(--warn)]", contradicted: "text-[var(--bad)]", unsupported: "text-[var(--muted)]", missing: "text-[var(--muted)]" };
  return <span className={cn(tone[status])}>{statusLabel[status]}</span>;
}
