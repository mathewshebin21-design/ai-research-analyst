"use client";

import { useMemo, useState } from "react";
import { motion } from "motion/react";
import { BookOpenCheck, FileSearch, LayoutDashboard, Lock, RotateCcw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { eurK } from "@/lib/finance";
import {
  activity,
  claimCounts,
  claims,
  critique,
  factors,
  frameworks,
  history,
  missingData,
  question,
  recommendation,
  sourceById,
  statusMeta,
  tasks,
  type ClaimStatus,
  type TaskStatus,
} from "@/lib/sample-data";
import { controls, useScenario } from "@/lib/use-scenario";
import type { View } from "@/lib/use-hash-route";
import { cn } from "@/lib/utils";
import { cashOption, competitorOption, porterOption, tornadoOption, type Palette } from "../shared/charts";
import { EChart } from "../shared/echart";
import { HighlightedExtract } from "../shared/highlight";
import { IllustrativeTag } from "../shared/illustrative";
import { laterNav, navItems, type PreviewProps } from "../shared/types";

const palette: Palette = {
  fg: "#efe9dc",
  muted: "#a3a9b4",
  line: "rgba(239,233,220,0.13)",
  surface: "#0f1e35",
  accent: "#c8a65d",
  series: { base: "#c8a65d", optimistic: "#efe9dc", conservative: "#7d8aa0" },
  ok: "#8fc3a5",
  warn: "#dcb062",
  bad: "#e39a86",
  font: "Hanken Grotesk, system-ui, sans-serif",
};

const navIcons: Record<View, typeof LayoutDashboard> = {
  dashboard: LayoutDashboard,
  workspace: BookOpenCheck,
  evidence: FileSearch,
};

const taskStatusLabel: Record<TaskStatus, string> = { done: "Complete", running: "In progress", queued: "Queued", blocked: "Blocked" };

function Eyebrow({ children, className }: { children: React.ReactNode; className?: string }) {
  return <p className={cn("text-[10.5px] font-semibold tracking-[0.16em] text-[var(--muted)] uppercase", className)}>{children}</p>;
}

function Panel({ title, aside, children, className }: { title: string; aside?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={cn("min-w-0 border-t border-[var(--line)] pt-4", className)}>
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-disp text-[21px] leading-tight">{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

function StatusBadge({ status }: { status: ClaimStatus }) {
  return (
    <Badge variant={status} shape="square">
      {statusMeta[status].label}
    </Badge>
  );
}

export function ExecutivePreview({ view, go }: PreviewProps) {
  const scenario = useScenario();

  return (
    <div className="lg:grid lg:min-h-dvh lg:grid-cols-[248px_minmax(0,1fr)]">
      <aside className="border-b border-[var(--line)] bg-[#081120] lg:sticky lg:top-0 lg:h-dvh lg:border-r lg:border-b-0">
        <div className="gutter flex h-full flex-col gap-6 py-5 lg:px-5">
          <div className="flex items-center justify-between gap-3 lg:block">
            <div>
              <p className="font-disp text-[19px] leading-none tracking-tight">Verdant Stride</p>
              <Eyebrow className="mt-1.5">Strategy office</Eyebrow>
            </div>
            <IllustrativeTag className="lg:mt-4" />
          </div>
          <nav aria-label="Primary" className="-mx-1 flex gap-1 overflow-x-auto lg:mx-0 lg:flex-col">
            {navItems.map((n) => {
              const Icon = navIcons[n.view];
              const active = n.view === view;
              return (
                <button
                  key={n.view}
                  type="button"
                  onClick={() => go("executive", n.view)}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-2.5 border-l-2 px-3 py-2 text-left text-[13.5px] whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                    active ? "border-[var(--accent)] bg-[var(--surface-2)] text-[var(--fg)]" : "border-transparent text-[var(--muted)] hover:text-[var(--fg)]",
                  )}
                >
                  <Icon className="size-4" strokeWidth={1.5} />
                  {n.label}
                </button>
              );
            })}
            {laterNav.map((l) => (
              <span key={l} className="hidden items-center gap-2.5 border-l-2 border-transparent px-3 py-2 text-[13.5px] text-[var(--muted)]/50 lg:flex" title="Designed after approval">
                <Lock className="size-3.5" strokeWidth={1.5} />
                {l}
              </span>
            ))}
          </nav>
          <div className="mt-auto hidden lg:block">
            <Eyebrow className="mb-2">Recent questions</Eyebrow>
            <ul className="flex flex-col gap-2">
              {history.map((h) => (
                <li key={h.title} className={cn("text-[13px] leading-5", h.active ? "text-[var(--fg)]" : "text-[var(--muted)]")}>
                  {h.title}
                  <span className="block text-[11px] text-[var(--muted)]">
                    {h.date} · {h.verdict}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </aside>

      <motion.main
        key={view}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: [0.2, 0.7, 0.2, 1] }}
        className="gutter mx-auto w-full max-w-[1240px] pt-8 pb-28 lg:px-12"
      >
        <header className="mb-8 flex flex-col gap-3">
          <Eyebrow>
            {question.workspace} · opened {question.created} · {question.owner}
          </Eyebrow>
          <h1 className="font-disp max-w-[30ch] text-[clamp(26px,3.2vw,40px)] leading-[1.12] font-normal">{question.text}</h1>
        </header>
        {view === "dashboard" && <Dashboard scenario={scenario} />}
        {view === "workspace" && <Workspace />}
        {view === "evidence" && <Evidence />}
      </motion.main>
    </div>
  );
}

function Dashboard({ scenario }: { scenario: ReturnType<typeof useScenario> }) {
  const base = scenario.results.base;
  const counts = claimCounts();
  const overall = Math.round(factors.reduce((s, f) => s + f.weight * f.score, 0));
  const cash = useMemo(() => cashOption(scenario.results, palette, { labels: true }), [scenario.results]);
  const tornado = useMemo(() => tornadoOption(scenario.tornado, palette), [scenario.tornado]);
  const comp = useMemo(() => competitorOption(palette), []);

  const figures = [
    { label: "Break-even month, base", value: base.breakEvenMonth ? `Month ${base.breakEvenMonth}` : "Not in 36 months" },
    { label: "Peak funding need", value: eurK(-base.peakFunding) },
    { label: "Cash position at month 36", value: eurK(base.cash36) },
    { label: "Claims supported by evidence", value: `${counts.supported} of ${claims.length}` },
  ];

  return (
    <div className="flex flex-col gap-12">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        <div className="min-w-0 border border-[var(--line)] bg-[var(--surface)] p-6 md:p-8">
          <div className="flex flex-wrap items-center gap-3">
            <Eyebrow className="text-[var(--accent)]">Recommendation</Eyebrow>
            <span className="border border-[var(--accent)] px-2 py-0.5 text-[11px] font-semibold tracking-[0.08em] text-[var(--accent)] uppercase">{recommendation.stance}</span>
          </div>
          <p className="font-disp mt-4 text-[clamp(26px,3vw,36px)] leading-[1.15]">{recommendation.verdict}</p>
          <p className="mt-4 max-w-[62ch] text-[14.5px] leading-7 text-[var(--muted)]">{recommendation.summary}</p>
          <div className="mt-6 grid gap-6 md:grid-cols-2">
            <div>
              <Eyebrow className="mb-2">Proceed only if</Eyebrow>
              <ul className="flex flex-col gap-2 text-[13.5px] leading-6">
                {recommendation.conditions.map((c) => (
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
                {recommendation.wouldChange.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          </div>
          <div className="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-[var(--line)] pt-4 text-[13px]">
            <span>
              Confidence <strong className="font-semibold">{recommendation.confidenceLabel}</strong>{" "}
              <span className="tnum text-[var(--muted)]">({Math.round(recommendation.confidence * 100)} / 100)</span>
            </span>
            <span className="text-[var(--muted)]">Derived from evidence coverage, not model self-assessment</span>
          </div>
        </div>
        <dl className="grid grid-cols-2 content-start gap-x-6 gap-y-6 lg:grid-cols-1">
          {figures.map((f) => (
            <div key={f.label} className="border-t border-[var(--line)] pt-3">
              <dt className="text-[12px] text-[var(--muted)]">{f.label}</dt>
              <dd className="font-disp tnum mt-1 text-[clamp(24px,2.6vw,32px)] leading-none">{f.value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <Panel
        title="Financial scenarios"
        aside={
          <span className="text-[12px] text-[var(--muted)]">Cumulative cash, 36 months · computed deterministically, not by the model</span>
        }
      >
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.7fr)_minmax(0,1fr)]">
          <EChart option={cash} label="Cumulative cash by scenario over 36 months" className="h-[300px] w-full" />
          <div className="flex flex-col gap-4">
            {controls.map((c) => (
              <div key={c.key}>
                <div className="flex items-baseline justify-between gap-2 text-[13px]">
                  <label htmlFor={`ex-${c.key}`}>{c.label}</label>
                  <span className="tnum font-semibold">{c.format(scenario.assumptions[c.key])}</span>
                </div>
                <Slider
                  id={`ex-${c.key}`}
                  aria-label={c.label}
                  min={c.min}
                  max={c.max}
                  step={c.step}
                  value={[scenario.assumptions[c.key]]}
                  onValueChange={([v]) => scenario.set(c.key, v)}
                />
                <p className="text-[11px] text-[var(--muted)]">{c.source}</p>
              </div>
            ))}
            <Button variant="outline" size="sm" onClick={scenario.reset} disabled={!scenario.changed} className="self-start">
              <RotateCcw /> Reset to base case
            </Button>
          </div>
        </div>
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <div>
            <Eyebrow className="mb-2">Sensitivity of month-36 cash to a ±20% move</Eyebrow>
            <EChart option={tornado} label="Sensitivity of 36-month cash to each assumption" className="h-[220px] w-full" />
          </div>
          <div className="text-[13.5px] leading-7 text-[var(--muted)]">
            <Eyebrow className="mb-2">Reading the model</Eyebrow>
            <p>
              Acquisition cost moves the outcome more than any other input, and it is the one input with no source behind it. That is
              why the recommendation is a capped pilot: it buys a measured CAC before the full budget is committed.
            </p>
          </div>
        </div>
      </Panel>

      <Panel title="How the score is built" aside={<span className="tnum text-[13px]">Weighted score {overall} / 100</span>}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-[13.5px]">
            <thead>
              <tr className="text-[11px] tracking-[0.1em] text-[var(--muted)] uppercase">
                <th className="py-2 pr-4 font-semibold">Factor</th>
                <th className="py-2 pr-4 font-semibold">Weight</th>
                <th className="w-[28%] py-2 pr-4 font-semibold">Score</th>
                <th className="py-2 pr-4 font-semibold">Evidence</th>
                <th className="py-2 font-semibold">Basis</th>
              </tr>
            </thead>
            <tbody>
              {factors.map((f) => (
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
                  </td>
                  <td className={cn("tnum py-3 pr-4", f.coverage < 0.5 ? "text-[var(--warn)]" : "text-[var(--muted)]")}>{Math.round(f.coverage * 100)}%</td>
                  <td className="py-3 text-[var(--muted)]">{f.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <div className="grid gap-12 lg:grid-cols-2">
        <Panel title="Competitive position" aside={<span className="text-[12px] text-[var(--muted)]">Bubble size: share estimate range</span>}>
          <EChart option={comp} label="Competitor price versus supply-chain transparency" className="h-[300px] w-full" />
        </Panel>
        <Panel title="Open questions">
          <ul className="flex flex-col">
            {critique.slice(0, 3).map((c) => (
              <li key={c.claimId} className="flex gap-3 border-b border-[var(--line)] py-3 text-[13.5px] leading-6 last:border-0">
                <span className={cn("mt-2 size-1.5 shrink-0 rounded-full", c.severity === "high" ? "bg-[var(--bad)]" : "bg-[var(--warn)]")} />
                <span>
                  {c.text} <span className="text-[var(--muted)]">({c.claimId})</span>
                </span>
              </li>
            ))}
          </ul>
          <Eyebrow className="mt-5 mb-2">Data we do not have</Eyebrow>
          <ul className="flex flex-col gap-2 text-[13px] leading-6">
            {missingData.map((m) => (
              <li key={m.item} className="grid grid-cols-[minmax(0,1fr)_auto] gap-3">
                <span>
                  {m.item}
                  <span className="block text-[var(--muted)]">{m.plan}</span>
                </span>
                <span className={cn("text-[11px] font-semibold uppercase", m.impact === "High" ? "text-[var(--bad)]" : "text-[var(--warn)]")}>{m.impact}</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>
    </div>
  );
}

function Workspace() {
  const [taskId, setTaskId] = useState("T1");
  const task = tasks.find((t) => t.id === taskId)!;
  const taskClaims = claims.filter((c) => c.taskId === taskId);
  const porter = useMemo(() => porterOption(palette), []);

  return (
    <div className="flex flex-col gap-12">
      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Panel title="Research plan" aside={<span className="text-[12px] text-[var(--muted)]">7 tasks · generated for this question</span>}>
          <ol className="flex flex-col">
            {tasks.map((t) => (
              <li key={t.id}>
                <button
                  type="button"
                  onClick={() => setTaskId(t.id)}
                  aria-pressed={t.id === taskId}
                  className={cn(
                    "grid w-full grid-cols-[36px_minmax(0,1fr)_auto] items-baseline gap-2 border-b border-[var(--line)] py-3 text-left transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                    t.id === taskId ? "text-[var(--fg)]" : "text-[var(--muted)] hover:text-[var(--fg)]",
                  )}
                >
                  <span className={cn("tnum text-[12px]", t.id === taskId && "text-[var(--accent)]")}>{t.id}</span>
                  <span className="text-[14px]">
                    {t.title}
                    <span className="block text-[11.5px] text-[var(--muted)]">
                      {t.category} · {t.sources} sources · {t.supported}/{t.claims} claims supported
                    </span>
                  </span>
                  <span
                    className={cn(
                      "text-[11px] whitespace-nowrap",
                      t.status === "done" && "text-[var(--ok)]",
                      t.status === "running" && "text-[var(--accent)]",
                      t.status === "blocked" && "text-[var(--bad)]",
                    )}
                  >
                    {taskStatusLabel[t.status]}
                  </span>
                </button>
              </li>
            ))}
          </ol>
        </Panel>

        <Panel title={`${task.id} · ${task.title}`}>
          {task.note && <p className="mb-4 border-l-2 border-[var(--warn)] pl-3 text-[13.5px] leading-6 text-[var(--warn)]">{task.note}</p>}
          <Eyebrow className="mb-2">Searches run</Eyebrow>
          {task.queries.length ? (
            <ul className="mb-6 flex flex-wrap gap-2">
              {task.queries.map((q) => (
                <li key={q} className="border border-[var(--line)] px-2.5 py-1 text-[12.5px] text-[var(--muted)]">
                  {q}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mb-6 text-[13.5px] text-[var(--muted)]">None yet.</p>
          )}
          <Eyebrow className="mb-2">Claims extracted</Eyebrow>
          {taskClaims.length ? (
            <ul className="flex flex-col">
              {taskClaims.map((c) => (
                <li key={c.id} className="flex flex-col gap-1.5 border-b border-[var(--line)] py-3 last:border-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="tnum text-[12px] text-[var(--muted)]">{c.id}</span>
                    <StatusBadge status={c.status} />
                  </div>
                  <p className="font-disp text-[17px] leading-snug">{c.text}</p>
                  <p className="text-[12.5px] text-[var(--muted)]">Sources: {c.evidence.map((e) => sourceById(e.sourceId).publisher).join("; ")}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[13.5px] text-[var(--muted)]">This task has not produced claims yet.</p>
          )}
          <Eyebrow className="mt-6 mb-2">Agent activity</Eyebrow>
          <ul className="flex flex-col gap-1.5 text-[12.5px]">
            {activity.map((a) => (
              <li key={a.t + a.text} className="grid grid-cols-[44px_80px_minmax(0,1fr)] gap-2 text-[var(--muted)]">
                <span className="tnum">{a.t}</span>
                <span className="text-[var(--fg)]">{a.agent}</span>
                <span>{a.text}</span>
              </li>
            ))}
          </ul>
        </Panel>
      </div>

      <Panel title="Strategic frameworks" aside={<span className="text-[12px] text-[var(--muted)]">Every entry cites the claim it rests on</span>}>
        <Tabs defaultValue="swot">
          <TabsList className="border-b border-[var(--line)]">
            {["swot", "pestle", "porter"].map((t) => (
              <TabsTrigger key={t} value={t} className="-mb-px border-b-2 border-transparent data-[state=active]:border-[var(--accent)]">
                {t === "swot" ? "SWOT" : t === "pestle" ? "PESTLE" : "Five Forces"}
              </TabsTrigger>
            ))}
          </TabsList>
          <TabsContent value="swot">
            <div className="grid gap-px bg-[var(--line)] md:grid-cols-2">
              {(Object.entries(frameworks.swot) as [string, string[]][]).map(([k, items]) => (
                <div key={k} className="bg-[var(--bg)] p-5">
                  <Eyebrow className="mb-2">{k}</Eyebrow>
                  <ul className="flex flex-col gap-1.5 text-[13.5px] leading-6">
                    {items.map((i) => (
                      <li key={i}>{i}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="pestle">
            <ul className="grid gap-x-8 md:grid-cols-2">
              {frameworks.pestle.map((p) => (
                <li key={p.factor} className="grid grid-cols-[110px_64px_minmax(0,1fr)] gap-3 border-b border-[var(--line)] py-3 text-[13.5px]">
                  <span>{p.factor}</span>
                  <span className="tnum text-[var(--accent)]" aria-label={`Impact ${p.rating} of 5`}>
                    {"●".repeat(p.rating)}
                    <span className="text-[var(--line)]">{"●".repeat(5 - p.rating)}</span>
                  </span>
                  <span className="text-[var(--muted)]">{p.note}</span>
                </li>
              ))}
            </ul>
          </TabsContent>
          <TabsContent value="porter">
            <EChart option={porter} label="Porter's five forces intensity, 1 to 5" className="h-[200px] w-full max-w-[640px]" />
          </TabsContent>
        </Tabs>
      </Panel>
    </div>
  );
}

function Evidence() {
  const [filter, setFilter] = useState<ClaimStatus | "all">("all");
  const [claimId, setClaimId] = useState("C2");
  const counts = claimCounts();
  const list = claims.filter((c) => filter === "all" || c.status === filter);
  const claim = claims.find((c) => c.id === claimId)!;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap gap-2" role="group" aria-label="Filter claims by status">
        {(["all", "supported", "partial", "contradicted", "unsupported", "missing"] as const).map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setFilter(s)}
            aria-pressed={filter === s}
            className={cn(
              "border px-3 py-1 text-[12.5px] transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
              filter === s ? "border-[var(--accent)] text-[var(--fg)]" : "border-[var(--line)] text-[var(--muted)] hover:text-[var(--fg)]",
            )}
          >
            {s === "all" ? `All claims ${claims.length}` : `${statusMeta[s].label} ${counts[s]}`}
          </button>
        ))}
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.5fr)]">
        <ul className="flex min-w-0 flex-col border-t border-[var(--line)]">
          {list.map((c) => (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => setClaimId(c.id)}
                aria-pressed={c.id === claimId}
                className={cn(
                  "flex w-full flex-col gap-1.5 border-b border-l-2 border-[var(--line)] py-3 pr-2 pl-4 text-left transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                  c.id === claimId ? "border-l-[var(--accent)] bg-[var(--surface)]" : "border-l-transparent hover:bg-[var(--surface)]",
                )}
              >
                <span className="flex items-center gap-2">
                  <span className="tnum text-[12px] text-[var(--muted)]">{c.id}</span>
                  <StatusBadge status={c.status} />
                </span>
                <span className="text-[13.5px] leading-6">{c.text}</span>
              </button>
            </li>
          ))}
        </ul>

        <article className="min-w-0 border border-[var(--line)] bg-[var(--surface)] p-6 md:p-8">
          <div className="flex flex-wrap items-center gap-3">
            <Eyebrow>Claim {claim.id} · Task {claim.taskId}</Eyebrow>
            <StatusBadge status={claim.status} />
          </div>
          <h2 className="font-disp mt-3 text-[clamp(22px,2.4vw,28px)] leading-snug">{claim.text}</h2>
          <div className="mt-5 border-l-2 border-[var(--accent)] pl-4">
            <Eyebrow className="mb-1">Verifier finding</Eyebrow>
            <p className="max-w-[62ch] text-[14px] leading-7">{claim.rationale}</p>
          </div>

          <Eyebrow className="mt-8 mb-3">Source extracts</Eyebrow>
          <ol className="flex flex-col gap-6">
            {claim.evidence.map((e, i) => {
              const s = sourceById(e.sourceId);
              return (
                <li key={e.sourceId + i} className="flex flex-col gap-3">
                  <blockquote className="font-disp text-[18px] leading-[1.6] italic">
                    “<HighlightedExtract text={e.extract} highlight={e.highlight} markClassName="bg-[rgba(200,166,93,0.22)] px-0.5 text-[var(--fg)] not-italic" />”
                  </blockquote>
                  <p className="text-[12.5px] text-[var(--muted)]">
                    <sup className="mr-1 text-[var(--accent)]">{i + 1}</sup>
                    {s.publisher}, <em>{s.title}</em>, {s.published}
                    {e.page ? `, p. ${e.page}` : ""} · {s.domain} · tier {s.tier} · retrieved {s.retrieved}
                  </p>
                  <div className="grid max-w-md grid-cols-[110px_minmax(0,1fr)_36px] items-center gap-x-3 gap-y-1.5 text-[12px]">
                    <span className="text-[var(--muted)]">Topic relevance</span>
                    <div className="h-1 bg-[var(--line)]">
                      <div className="h-1 bg-[var(--muted)]" style={{ width: `${e.relevance * 100}%` }} />
                    </div>
                    <span className="tnum text-right">{e.relevance.toFixed(2)}</span>
                    <span className="text-[var(--muted)]">Supports claim</span>
                    <div className="h-1 bg-[var(--line)]">
                      <div
                        className={cn("h-1", e.relation === "supports" ? "bg-[var(--ok)]" : e.relation === "contradicts" ? "bg-[var(--bad)]" : "bg-[var(--warn)]")}
                        style={{ width: `${e.entailment * 100}%` }}
                      />
                    </div>
                    <span className="tnum text-right">{e.entailment.toFixed(2)}</span>
                  </div>
                </li>
              );
            })}
          </ol>
          <p className="mt-8 border-t border-[var(--line)] pt-4 text-[12px] leading-5 text-[var(--muted)]">
            A source can be highly relevant to the topic and still not support the claim. Only the second score decides the status.
          </p>
        </article>
      </div>
    </div>
  );
}
