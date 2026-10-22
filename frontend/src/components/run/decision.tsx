"use client";

import { useEffect, useRef, useState } from "react";
import { RotateCcw, Save } from "lucide-react";

import { ErrorNote, Eyebrow, Panel } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { api } from "@/lib/api";
import type { Condition, Decision, RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

const verdictTone: Record<string, string> = {
  Go: "border-[var(--ok)] text-[var(--ok)]",
  "Conditional go": "border-[var(--accent)] text-[var(--accent)]",
  "No-go": "border-[var(--bad)] text-[var(--bad)]",
  "Insufficient evidence": "border-[var(--warn)] text-[var(--warn)]",
};

const conditionStates: { id: Condition["status"]; label: string; tone: string }[] = [
  { id: "open", label: "Open", tone: "border-[var(--line)] text-[var(--muted)]" },
  { id: "met", label: "Met", tone: "border-[var(--ok)] bg-[var(--ok-bg)] text-[var(--ok)]" },
  { id: "not_met", label: "Not met", tone: "border-[var(--bad)] bg-[var(--bad-bg)] text-[var(--bad)]" },
];

const toPercent = (w: Record<string, number>) => Object.fromEntries(Object.entries(w).map(([k, v]) => [k, Math.round(v * 100)]));

export function DecisionWorkspace({ run, canEdit, onRunChange }: { run: RunDetail; canEdit: boolean; onRunChange: (r: RunDetail) => void }) {
  const saved = run.decision;
  const [weights, setWeights] = useState<Record<string, number>>(saved ? toPercent(saved.weights) : {});
  const [preview, setPreview] = useState<Decision | null>(saved);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const dirty = saved ? Object.entries(toPercent(saved.weights)).some(([k, v]) => weights[k] !== v) : false;

  useEffect(() => {
    if (!saved || !dirty) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try {
        setPreview(await api<Decision>(`/runs/${run.id}/decision`, { method: "POST", json: { weights } }));
        setError(null);
      } catch (e) {
        setError((e as Error).message);
      }
    }, 250);
  }, [weights, dirty, saved, run.id]);

  if (!saved || !preview) return null;
  const shown = dirty ? preview : saved;

  async function persist(reset = false) {
    setBusy(true);
    try {
      const d = reset
        ? await api<Decision>(`/runs/${run.id}/decision/weights`, { method: "DELETE" })
        : await api<Decision>(`/runs/${run.id}/decision`, { method: "POST", json: { weights, save: true } });
      onRunChange({ ...run, decision: d });
      setWeights(toPercent(d.weights));
      setPreview(d);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function setCondition(index: number, status: Condition["status"], note: string) {
    try {
      const items = await api<Condition[]>(`/runs/${run.id}/conditions/${index}`, { method: "PUT", json: { status, note } });
      onRunChange({ ...run, conditions: items });
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <Panel
      title="Decision workspace"
      aside={<span className="text-[12px] text-[var(--muted)]">Change what matters most to you; the verdict follows fixed rules</span>}
    >
      {error && <div className="mb-4"><ErrorNote>{error}</ErrorNote></div>}

      <div className="mb-6 flex flex-wrap items-center gap-x-6 gap-y-3 border border-[var(--line)] bg-[var(--surface)] px-5 py-4">
        <div className="flex items-center gap-3">
          <Eyebrow>{dirty ? "Preview" : "Current verdict"}</Eyebrow>
          <span className={cn("border px-2 py-0.5 text-[11px] font-semibold tracking-[0.08em] uppercase", verdictTone[shown.verdict])}>{shown.verdict}</span>
        </div>
        <span className="tnum text-[14px]">Score {shown.overall} / 100</span>
        <span className="text-[14px]">
          Confidence {shown.confidence_label} <span className="tnum text-[var(--muted)]">({Math.round(shown.confidence * 100)})</span>
        </span>
        <span className="text-[12px] text-[var(--muted)]">{shown.rule}</span>
      </div>
      {!dirty && saved.changed && (
        <p className="mb-6 border-l-2 border-[var(--warn)] pl-3 text-[13.5px] leading-6 text-[var(--warn)]">
          The recommendation above was written as &ldquo;{saved.original_verdict}&rdquo; (score {saved.original_overall}).
          {saved.custom_weights ? " Your saved weights" : " Changes to the evidence since then"} give &ldquo;{saved.verdict}&rdquo; (score {saved.overall}).
        </p>
      )}

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-[13.5px]">
          <thead>
            <tr className="text-[11px] tracking-[0.1em] text-[var(--muted)] uppercase">
              <th className="py-2 pr-4 font-semibold">Factor</th>
              <th className="w-[26%] py-2 pr-4 font-semibold">Weight</th>
              <th className="py-2 pr-4 font-semibold">Score</th>
              <th className="py-2 pr-4 font-semibold">Evidence</th>
              <th className="py-2 font-semibold">Basis</th>
            </tr>
          </thead>
          <tbody>
            {shown.factors.map((f) => (
              <tr key={f.key} className="border-t border-[var(--line)] align-top">
                <td className="py-3 pr-4">{f.label}</td>
                <td className="py-3 pr-4">
                  <div className="flex items-center gap-3">
                    <Slider
                      aria-label={`Weight for ${f.label}`}
                      min={0}
                      max={100}
                      step={5}
                      value={[weights[f.key] ?? 0]}
                      onValueChange={([v]) => setWeights({ ...weights, [f.key]: v })}
                    />
                    <span className="tnum w-10 text-right text-[var(--muted)]">{Math.round(f.weight * 100)}%</span>
                  </div>
                </td>
                <td className="tnum py-3 pr-4">
                  {f.score}
                  {f.basis !== "evidenced" && <span className="block text-[11px] text-[var(--warn)]">held at 50</span>}
                </td>
                <td className={cn("tnum py-3 pr-4", f.coverage < 0.5 ? "text-[var(--warn)]" : "text-[var(--muted)]")}>{Math.round(f.coverage * 100)}%</td>
                <td className="py-3 text-[var(--muted)]">
                  {f.rationale} <span className="text-[var(--fg)]">{f.claims.join(", ")}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-3">
        {canEdit && (
          <Button size="sm" onClick={() => persist()} disabled={!dirty || busy}>
            <Save /> Save these weights
          </Button>
        )}
        {canEdit && saved.custom_weights && (
          <Button size="sm" variant="outline" onClick={() => persist(true)} disabled={busy}>
            <RotateCcw /> Back to standard weights
          </Button>
        )}
        <span className="text-[12px] text-[var(--muted)]">
          {dirty ? "Previewing. Weights are rescaled to add up to 100%." : saved.custom_weights ? "Using your saved weights." : "Using standard weights."}
          {!canEdit && " You can preview but not save weights with view-only access."}
        </span>
      </div>

      {run.conditions.length > 0 && (
        <div className="mt-10">
          <Eyebrow className="mb-3">Conditions to proceed</Eyebrow>
          <ul className="flex flex-col">
            {run.conditions.map((c, i) => (
              <ConditionRow key={i} c={c} canEdit={canEdit} onSave={(status, note) => setCondition(i, status, note)} />
            ))}
          </ul>
        </div>
      )}
    </Panel>
  );
}

function ConditionRow({ c, canEdit, onSave }: { c: Condition; canEdit: boolean; onSave: (s: Condition["status"], note: string) => void }) {
  const [note, setNote] = useState(c.note);
  return (
    <li className="grid gap-3 border-b border-[var(--line)] py-3 last:border-0 md:grid-cols-[minmax(0,1fr)_auto]">
      <div className="min-w-0">
        <p className="text-[14px] leading-6">{c.text}</p>
        {canEdit ? (
          <input
            aria-label={`Note for: ${c.text}`}
            value={note}
            placeholder="Add evidence or a note, e.g. what the pilot showed"
            onChange={(e) => setNote(e.target.value)}
            onBlur={() => note !== c.note && onSave(c.status, note)}
            className="mt-1.5 w-full px-2 py-1 text-[12.5px]"
          />
        ) : (
          c.note && <p className="text-[12.5px] text-[var(--muted)]">{c.note}</p>
        )}
      </div>
      <div className="flex gap-1 self-start" role="group" aria-label={`Status of: ${c.text}`}>
        {conditionStates.map((s) => (
          <button
            key={s.id}
            type="button"
            disabled={!canEdit}
            aria-pressed={c.status === s.id}
            onClick={() => onSave(s.id, note)}
            className={cn(
              "border px-2.5 py-1 text-[12px] transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)] disabled:cursor-default",
              c.status === s.id ? s.tone : "border-[var(--line)] text-[var(--muted)] hover:text-[var(--fg)]",
            )}
          >
            {s.label}
          </button>
        ))}
      </div>
    </li>
  );
}
