"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Download, RotateCcw, Save } from "lucide-react";

import { cashOption, tornadoOption } from "@/components/app/charts";
import { EChart } from "@/components/app/echart";
import { ErrorNote, Eyebrow, Panel } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { api, saveBlob } from "@/lib/api";
import { assumptionKeys, assumptionMeta, eurK, formatAssumption } from "@/lib/format";
import type { Assumption, AssumptionKey, RunDetail, ScenarioOut, ScenarioResults } from "@/lib/types";
import { cn } from "@/lib/utils";

const verdictTone: Record<string, string> = {
  Go: "border-[var(--ok)] text-[var(--ok)]",
  "Conditional go": "border-[var(--accent)] text-[var(--accent)]",
  "No-go": "border-[var(--bad)] text-[var(--bad)]",
  "Insufficient evidence": "border-[var(--warn)] text-[var(--warn)]",
};

const originLabel = { evidence: "From evidence", estimate: "Model estimate", user: "Your input" };

export function Dashboard({ run, canEdit, onRunChange }: { run: RunDetail; canEdit: boolean; onRunChange: (r: RunDetail) => void }) {
  const rec = run.recommendation;
  const counts = run.claims.reduce<Record<string, number>>((m, c) => ({ ...m, [c.status]: (m[c.status] ?? 0) + 1 }), {});

  return (
    <div className="flex flex-col gap-12">
      {rec && (
        <section className="grid gap-8 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
          <div className="min-w-0 border border-[var(--line)] bg-[var(--surface)] p-6 md:p-8">
            <div className="flex flex-wrap items-center gap-3">
              <Eyebrow className="text-[var(--accent)]">Recommendation</Eyebrow>
              <span className={cn("border px-2 py-0.5 text-[11px] font-semibold tracking-[0.08em] uppercase", verdictTone[rec.verdict])}>{rec.verdict}</span>
            </div>
            <p className="font-disp mt-4 text-[clamp(24px,2.8vw,34px)] leading-[1.15]">{rec.headline}</p>
            <p className="mt-4 max-w-[62ch] text-[14.5px] leading-7 text-[var(--muted)]">{rec.summary}</p>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <div>
                <Eyebrow className="mb-2">Proceed only if</Eyebrow>
                <ul className="flex flex-col gap-2 text-[13.5px] leading-6">
                  {rec.conditions.map((c) => (
                    <li key={c} className="flex gap-3">
                      <span aria-hidden className="mt-[11px] h-px w-4 shrink-0 bg-[var(--accent)]" />
                      {c}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <Eyebrow className="mb-2">What would change this</Eyebrow>
                <ul className="flex flex-col gap-2 text-[13.5px] leading-6 text-[var(--muted)]">
                  {rec.would_change.map((c) => (
                    <li key={c}>{c}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-6 flex flex-col gap-1 border-t border-[var(--line)] pt-4 text-[13px]">
              <span>
                Confidence <strong className="font-semibold">{rec.confidence_label}</strong>{" "}
                <span className="tnum text-[var(--muted)]">({Math.round(rec.confidence * 100)} / 100)</span>
              </span>
              <span className="text-[12px] text-[var(--muted)]">
                {rec.confidence_method}. Verdict rule: {rec.rule}
              </span>
            </div>
          </div>
          <dl className="grid grid-cols-2 content-start gap-x-6 gap-y-6 lg:grid-cols-1">
            <Figure label="Weighted score" value={`${rec.overall} / 100`} />
            <Figure label="Claims supported by evidence" value={`${counts.supported ?? 0} of ${run.claims.length}`} />
            <Figure label="Sources collected" value={String(run.sources.length)} />
            <Figure label="Open findings, high severity" value={String(run.findings.filter((f) => f.severity === "high").length)} />
          </dl>
        </section>
      )}

      <Scenarios run={run} canEdit={canEdit} onRunChange={onRunChange} />

      <Panel title="How the score is built" aside={rec && <span className="tnum text-[13px]">Weighted score {rec.overall} / 100</span>}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] text-left text-[13.5px]">
            <thead>
              <tr className="text-[11px] tracking-[0.1em] text-[var(--muted)] uppercase">
                <th className="py-2 pr-4 font-semibold">Factor</th>
                <th className="py-2 pr-4 font-semibold">Weight</th>
                <th className="w-[24%] py-2 pr-4 font-semibold">Score</th>
                <th className="py-2 pr-4 font-semibold">Evidence</th>
                <th className="py-2 font-semibold">Basis</th>
              </tr>
            </thead>
            <tbody>
              {run.factors.map((f) => (
                <tr key={f.key} className="border-t border-[var(--line)] align-top">
                  <td className="py-3 pr-4">{f.label}</td>
                  <td className="tnum py-3 pr-4 text-[var(--muted)]">{Math.round(f.weight * 100)}%</td>
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-3">
                      <div className="h-1 flex-1 bg-[var(--line)]">
                        <div className="h-1 bg-[var(--accent)]" style={{ width: `${f.score}%` }} />
                      </div>
                      <span className="tnum w-6 text-right">{f.score}</span>
                    </div>
                    {f.basis !== "evidenced" && f.model_score !== null && (
                      <p className="mt-1 text-[11.5px] text-[var(--warn)]">Held at 50: the analyst&apos;s {f.model_score} had no evidence behind it</p>
                    )}
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
      </Panel>

      <div className="grid gap-12 lg:grid-cols-2">
        <Panel title="Competitors named in the evidence">
          {run.competitors.length === 0 ? (
            <p className="text-[13.5px] text-[var(--muted)]">No competitor was named in a verified claim.</p>
          ) : (
            <ul className="flex flex-col">
              {run.competitors.map((c) => (
                <li key={c.name} className="border-b border-[var(--line)] py-3 text-[13.5px] last:border-0">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <span className="font-disp text-[17px]">{c.name}</span>
                    <span className="text-[12px] text-[var(--muted)]">
                      {c.price_note || "Price not found"} · {c.claims.join(", ")}
                    </span>
                  </div>
                  <p className="text-[var(--muted)]">{c.positioning}</p>
                  {c.basis !== "evidenced" && <p className="text-[11.5px] text-[var(--warn)]">Only unsupported claims mention this competitor.</p>}
                </li>
              ))}
            </ul>
          )}
        </Panel>
        <Panel title="Open questions">
          <ul className="flex flex-col">
            {run.findings.slice(0, 6).map((f) => (
              <li key={f.id} className="flex gap-3 border-b border-[var(--line)] py-2.5 text-[13.5px] leading-6 last:border-0">
                <span className={cn("mt-2 size-1.5 shrink-0 rounded-full", f.severity === "high" ? "bg-[var(--bad)]" : f.severity === "medium" ? "bg-[var(--warn)]" : "bg-[var(--muted)]")} />
                {f.text}
              </li>
            ))}
            {run.findings.length === 0 && <li className="text-[13.5px] text-[var(--muted)]">The critic raised no findings.</li>}
          </ul>
          {run.missing.length > 0 && (
            <>
              <Eyebrow className="mt-5 mb-2">Data we do not have</Eyebrow>
              <ul className="flex flex-col gap-2 text-[13px] leading-6">
                {run.missing.map((m) => (
                  <li key={m.item} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3">
                    <span>
                      {m.item}
                      <span className="block text-[var(--muted)]">{m.plan}</span>
                    </span>
                    <span className={cn("text-[11px] font-semibold uppercase", m.impact === "High" ? "text-[var(--bad)]" : "text-[var(--warn)]")}>{m.impact}</span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </Panel>
      </div>

      <p className="border-t border-[var(--line)] pt-4 text-[12px] leading-5 text-[var(--muted)]">
        Generated with automated research and language models. Not financial, investment or legal advice. Check the cited extracts in the
        evidence inspector before relying on any figure.
      </p>
    </div>
  );
}

function Figure({ label, value }: { label: string; value: string }) {
  return (
    <div className="border-t border-[var(--line)] pt-3">
      <dt className="text-[12px] text-[var(--muted)]">{label}</dt>
      <dd className="font-disp tnum mt-1 text-[clamp(24px,2.6vw,32px)] leading-none">{value}</dd>
    </div>
  );
}

function Scenarios({ run, canEdit, onRunChange }: { run: RunDetail; canEdit: boolean; onRunChange: (r: RunDetail) => void }) {
  const saved = run.scenario;
  const initial = useMemo(() => {
    const from = saved?.assumptions ?? run.assumption_suggestions;
    return assumptionKeys.every((k) => from[k]) ? (from as Record<AssumptionKey, Assumption>) : null;
  }, [saved, run.assumption_suggestions]);
  const [draft, setDraft] = useState<Record<AssumptionKey, Assumption> | null>(initial);
  const [results, setResults] = useState<ScenarioResults | null>(saved?.results ?? null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<"save" | "export" | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const changed = draft && initial && assumptionKeys.some((k) => draft[k].value !== initial[k].value);

  useEffect(() => {
    if (!draft) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try {
        const values = Object.fromEntries(assumptionKeys.map((k) => [k, draft[k].value]));
        setResults(await api<ScenarioResults>("/finance/calculate", { method: "POST", json: { values } }));
        setError(null);
      } catch (e) {
        setError((e as Error).message);
      }
    }, 250);
  }, [draft]);

  async function saveVersion() {
    if (!draft) return;
    setBusy("save");
    try {
      const s = await api<ScenarioOut>(`/runs/${run.id}/scenarios`, { method: "POST", json: { assumptions: draft } });
      onRunChange({ ...run, scenario: s, scenario_versions: [...run.scenario_versions, { id: s.id, version: s.version, created_at: s.created_at }] });
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function exportPdf() {
    setBusy("export");
    try {
      const q = run.scenario ? `?scenario_id=${run.scenario.id}` : "";
      const rep = await api<{ download: string }>(`/runs/${run.id}/reports${q}`, { method: "POST" });
      saveBlob(await api<Blob>(rep.download, { asFile: true }), `market-entry-${run.id.slice(0, 8)}.pdf`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  const base = results?.scenarios.base;
  const cash = useMemo(() => (results ? cashOption(results) : null), [results]);
  const tornado = useMemo(() => (results ? tornadoOption(results) : null), [results]);

  return (
    <Panel
      title="Financial scenarios"
      aside={
        <div className="flex flex-wrap items-center gap-2">
          {canEdit && draft && (
            <Button size="sm" variant="outline" onClick={saveVersion} disabled={!changed || busy !== null}>
              <Save /> {busy === "save" ? "Saving…" : "Save as new version"}
            </Button>
          )}
          <Button size="sm" onClick={exportPdf} disabled={busy !== null}>
            <Download /> {busy === "export" ? "Preparing PDF…" : "Export board report"}
          </Button>
        </div>
      }
    >
      {error && <div className="mb-4"><ErrorNote>{error}</ErrorNote></div>}
      {!draft || !results || !base ? (
        <p className="text-[13.5px] text-[var(--muted)]">The analysis did not produce a full set of assumptions, so no scenario was calculated.</p>
      ) : (
        <>
          <dl className="mb-6 grid grid-cols-2 gap-6 md:grid-cols-4">
            <Figure label="Break-even month, base" value={base.break_even_month ? `Month ${base.break_even_month}` : "Not in 36 months"} />
            <Figure label="Peak funding need" value={eurK(-base.peak_funding)} />
            <Figure label="Cash at month 36" value={eurK(base.cash_36)} />
            <Figure label="Revenue over 36 months" value={eurK(base.revenue_36)} />
          </dl>
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
            {cash && <EChart option={cash} label="Cumulative cash by scenario over 36 months" className="h-[320px] w-full" />}
            <div className="flex flex-col gap-4">
              {assumptionKeys.map((k) => {
                const m = assumptionMeta[k];
                const a = draft[k];
                return (
                  <div key={k}>
                    <div className="flex items-baseline justify-between gap-2 text-[13px]">
                      <label htmlFor={`a-${k}`}>{m.label}</label>
                      <span className="tnum font-semibold">{formatAssumption(k, a.value)}</span>
                    </div>
                    <Slider
                      id={`a-${k}`}
                      aria-label={m.label}
                      disabled={!canEdit}
                      min={m.min}
                      max={Math.max(m.max, a.value)}
                      step={m.step}
                      value={[a.value]}
                      onValueChange={([v]) => setDraft({ ...draft, [k]: { ...a, value: v, origin: "user", claim: null } })}
                    />
                    <p className={cn("text-[11px]", a.origin === "estimate" ? "text-[var(--warn)]" : "text-[var(--muted)]")}>
                      {originLabel[a.origin]}
                      {a.claim ? ` · ${a.claim}` : ""}
                    </p>
                  </div>
                );
              })}
              {canEdit && changed && (
                <Button variant="ghost" size="sm" onClick={() => setDraft(initial)} className="self-start">
                  <RotateCcw /> Back to saved version {run.scenario?.version}
                </Button>
              )}
            </div>
          </div>
          <div className="mt-8 grid gap-8 lg:grid-cols-2">
            <div>
              <Eyebrow className="mb-2">Sensitivity of month-36 cash to a ±20% move</Eyebrow>
              {tornado && <EChart option={tornado} label="Sensitivity of 36-month cash to each assumption" className="h-[240px] w-full" />}
            </div>
            <div className="text-[13.5px] leading-7 text-[var(--muted)]">
              <Eyebrow className="mb-2">Reading the model</Eyebrow>
              <p>
                {results.sensitivity[0]?.label} moves the outcome most. Inputs marked <span className="text-[var(--warn)]">Model estimate</span> have no
                source behind them; replace them with your own figures before relying on the result. Calculations run in Python on the server and
                are the same ones used in the exported report.
              </p>
              <p className="mt-2 text-[12px]">Saved versions: {run.scenario_versions.map((v) => `v${v.version}`).join(", ") || "none"}</p>
            </div>
          </div>
        </>
      )}
    </Panel>
  );
}
