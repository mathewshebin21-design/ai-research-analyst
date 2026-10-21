"use client";

import { useMemo, useState } from "react";
import { motion } from "motion/react";
import { Activity, BookOpenCheck, FileSearch, FileText, History, LayoutDashboard, Search, Swords, Wallet } from "lucide-react";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { eurK } from "@/lib/finance";
import {
  activity,
  claimCounts,
  claims,
  critique,
  factors,
  frameworks,
  missingData,
  question,
  recommendation,
  sourceById,
  sources,
  statusMeta,
  tasks,
  type ClaimStatus,
} from "@/lib/sample-data";
import { controls, useScenario } from "@/lib/use-scenario";
import type { View } from "@/lib/use-hash-route";
import { cn } from "@/lib/utils";
import { cashOption, competitorOption, coverageHeatmap, evidenceGraph, porterOption, radarOption, tornadoOption, type Palette } from "../shared/charts";
import { EChart } from "../shared/echart";
import { HighlightedExtract } from "../shared/highlight";
import { IllustrativeTag } from "../shared/illustrative";
import { navItems, type PreviewProps } from "../shared/types";

const palette: Palette = {
  fg: "#e4e8ee",
  muted: "#8a93a3",
  line: "#272c35",
  surface: "#14171c",
  accent: "#3b8cff",
  series: { base: "#3b8cff", optimistic: "#3ccf91", conservative: "#f5b841" },
  ok: "#3ccf91",
  warn: "#f5b841",
  bad: "#ff6464",
  font: "IBM Plex Mono, ui-monospace, monospace",
};

const navIcons: Record<View, typeof LayoutDashboard> = { dashboard: LayoutDashboard, workspace: BookOpenCheck, evidence: FileSearch };
const laterIcons = [
  { icon: Swords, label: "Competitors" },
  { icon: Wallet, label: "Financial model" },
  { icon: FileText, label: "Reports" },
  { icon: History, label: "History" },
];

const statusText: Record<ClaimStatus, string> = {
  supported: "text-[var(--ok)]",
  partial: "text-[var(--warn)]",
  contradicted: "text-[var(--bad)]",
  unsupported: "text-[var(--bad)]",
  missing: "text-[var(--muted)]",
};

function Panel({ id, title, meta, children, className }: { id: string; title: string; meta?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={cn("flex min-w-0 flex-col rounded-[var(--radius)] border border-[var(--line)] bg-[var(--surface)]", className)}>
      <header className="flex items-center justify-between gap-3 border-b border-[var(--line)] px-3 py-2">
        <h2 className="font-num truncate text-[11px] tracking-[0.12em] text-[var(--muted)] uppercase">
          <span className="text-[var(--accent)]">{id}</span> · {title}
        </h2>
        {meta && <div className="font-num shrink-0 text-[11px] text-[var(--muted)]">{meta}</div>}
      </header>
      <div className="min-w-0 flex-1 p-3">{children}</div>
    </section>
  );
}

function Mono({ children, className }: { children: React.ReactNode; className?: string }) {
  return <span className={cn("font-num tnum", className)}>{children}</span>;
}

export function CommandPreview({ view, go }: PreviewProps) {
  const scenario = useScenario();
  const counts = claimCounts();
  const done = tasks.filter((t) => t.status === "done").length;

  return (
    <div className="md:grid md:min-h-dvh md:grid-cols-[56px_minmax(0,1fr)]">
      <nav aria-label="Primary" className="flex items-center gap-1 border-b border-[var(--line)] bg-[#0a0c0f] px-2 py-2 md:sticky md:top-0 md:h-dvh md:flex-col md:border-r md:border-b-0 md:py-3">
        <div className="font-num mr-2 grid size-9 place-items-center rounded-[var(--radius)] bg-[var(--accent)] text-[13px] font-semibold text-[var(--primary-fg)] md:mr-0 md:mb-3">VS</div>
        {navItems.map((n) => {
          const Icon = navIcons[n.view];
          const active = n.view === view;
          return (
            <Tooltip key={n.view}>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  aria-label={n.label}
                  aria-current={active ? "page" : undefined}
                  onClick={() => go("command", n.view)}
                  className={cn(
                    "grid size-10 place-items-center rounded-[var(--radius)] transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                    active ? "bg-[var(--surface-2)] text-[var(--accent)] shadow-[inset_2px_0_0_var(--accent)]" : "text-[var(--muted)] hover:text-[var(--fg)]",
                  )}
                >
                  <Icon className="size-[18px]" strokeWidth={1.6} />
                </button>
              </TooltipTrigger>
              <TooltipContent side="right">{n.label}</TooltipContent>
            </Tooltip>
          );
        })}
        <span className="mx-1 h-6 w-px bg-[var(--line)] md:my-2 md:h-px md:w-6" />
        {laterIcons.map(({ icon: Icon, label }) => (
          <Tooltip key={label}>
            <TooltipTrigger asChild>
              <span tabIndex={0} aria-label={`${label}, designed after approval`} className="hidden size-10 place-items-center text-[var(--muted)]/40 sm:grid">
                <Icon className="size-[18px]" strokeWidth={1.6} />
              </span>
            </TooltipTrigger>
            <TooltipContent side="right">{label} · designed after approval</TooltipContent>
          </Tooltip>
        ))}
      </nav>

      <div className="min-w-0">
        <header className="gutter sticky top-0 z-30 flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-[var(--line)] bg-[var(--bg)]/95 py-2.5 backdrop-blur md:px-5">
          <Mono className="text-[12px] text-[var(--muted)]">RUN-2026-1018-DE</Mono>
          <div className="flex min-w-[200px] flex-1 items-center gap-2 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--surface)] px-2.5 py-1.5 text-[12.5px] text-[var(--muted)]">
            <Search className="size-3.5" />
            <span className="truncate">Search claims, sources, tasks</span>
            <kbd className="font-num ml-auto rounded border border-[var(--line)] px-1 text-[10px]">⌘K</kbd>
          </div>
          <div className="font-num flex flex-wrap items-center gap-3 text-[11.5px]">
            <span className="flex items-center gap-1.5">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-[var(--accent)] opacity-60" />
                <span className="relative inline-flex size-2 rounded-full bg-[var(--accent)]" />
              </span>
              RUNNING {done}/{tasks.length}
            </span>
            <span className="text-[var(--muted)]">TAVILY 61/400 CR</span>
            <span className="text-[var(--muted)]">MODEL $0.31/$2.00</span>
            <IllustrativeTag />
          </div>
        </header>

        <div className="gutter font-num flex gap-5 overflow-x-auto border-b border-[var(--line)] py-1.5 text-[11px] whitespace-nowrap text-[var(--muted)] md:px-5">
          <span className="text-[var(--fg)]">{question.short.toUpperCase()}</span>
          {(Object.keys(counts) as ClaimStatus[]).map((s) => (
            <span key={s}>
              {statusMeta[s].short} <span className={statusText[s]}>{counts[s]}</span>
            </span>
          ))}
          <span>SOURCES {sources.length}</span>
          <span>
            VERDICT <span className="text-[var(--accent)]">{recommendation.stance.toUpperCase()}</span>
          </span>
          <span>CONF {recommendation.confidence.toFixed(2)}</span>
        </div>

        <motion.main key={view} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }} className="gutter pt-4 pb-28 md:px-5">
          {view === "dashboard" && <Dashboard scenario={scenario} />}
          {view === "workspace" && <Workspace />}
          {view === "evidence" && <Evidence />}
        </motion.main>
      </div>
    </div>
  );
}

function Dashboard({ scenario }: { scenario: ReturnType<typeof useScenario> }) {
  const r = scenario.results;
  const cash = useMemo(() => cashOption(r, palette, { area: true, labels: true }), [r]);
  const tornado = useMemo(() => tornadoOption(scenario.tornado, palette), [scenario.tornado]);
  const radar = useMemo(() => radarOption(palette), []);
  const heat = useMemo(() => coverageHeatmap(palette), []);
  const comp = useMemo(() => competitorOption(palette), []);
  const overall = factors.reduce((s, f) => s + f.weight * f.score, 0);

  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-12">
      <Panel id="D1" title="Decision" meta={`CONF ${recommendation.confidence.toFixed(2)}`} className="lg:col-span-4">
        <p className="text-[11px] tracking-[0.1em] text-[var(--accent)] uppercase">{recommendation.stance}</p>
        <p className="mt-1 text-[19px] leading-snug font-medium">{recommendation.verdict}</p>
        <div className="mt-3 flex items-center gap-2">
          <div className="flex h-1.5 flex-1 gap-0.5">
            {Array.from({ length: 20 }, (_, i) => (
              <span key={i} className={cn("flex-1", i < Math.round(recommendation.confidence * 20) ? "bg-[var(--accent)]" : "bg-[var(--line)]")} />
            ))}
          </div>
          <Mono className="text-[11px] text-[var(--muted)]">coverage-derived</Mono>
        </div>
        <ul className="mt-4 flex flex-col gap-2 text-[12.5px] leading-5">
          {recommendation.conditions.map((c, i) => (
            <li key={c} className="grid grid-cols-[34px_minmax(0,1fr)] gap-2">
              <Mono className="text-[var(--muted)]">G{i + 1}</Mono>
              <span>
                {c} <Mono className="text-[10.5px] text-[var(--warn)]">PENDING</Mono>
              </span>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel id="D2" title="Score vector" meta={`W ${overall.toFixed(1)}`} className="lg:col-span-4">
        <EChart option={radar} label="Factor scores against evidence coverage" className="h-[230px] w-full" />
        <p className="font-num text-[10.5px] text-[var(--muted)]">solid = score · dashed = evidence coverage %</p>
      </Panel>

      <Panel id="D3" title="Verification matrix" meta="claims × status" className="lg:col-span-4">
        <EChart option={heat} label="Claims per research task by verification status" className="h-[230px] w-full" />
      </Panel>

      <Panel
        id="F1"
        title="Cumulative cash · 36m"
        meta={
          <span className="flex gap-3">
            <span>BE M{r.base.breakEvenMonth ?? "—"}</span>
            <span>PEAK {eurK(r.base.peakFunding)}</span>
            <span className="hidden sm:inline">M36 {eurK(r.base.cash36)}</span>
          </span>
        }
        className="lg:col-span-8"
      >
        <EChart option={cash} label="Cumulative cash by scenario" className="h-[280px] w-full" />
      </Panel>

      <Panel
        id="F2"
        title="Assumptions"
        meta={
          scenario.changed ? (
            <button type="button" onClick={scenario.reset} className="text-[var(--accent)] hover:underline">
              RESET
            </button>
          ) : (
            "BASE"
          )
        }
        className="lg:col-span-4"
      >
        <div className="flex flex-col gap-3">
          {controls.map((c) => (
            <label key={c.key} htmlFor={`cm-${c.key}`} className="grid grid-cols-[minmax(0,1fr)_64px] items-center gap-x-3 gap-y-1">
              <span className="text-[12px]">{c.label}</span>
              <Mono className="text-right text-[12px] text-[var(--accent)]">{c.format(scenario.assumptions[c.key])}</Mono>
              <input
                id={`cm-${c.key}`}
                type="range"
                min={c.min}
                max={c.max}
                step={c.step}
                value={scenario.assumptions[c.key]}
                onChange={(e) => scenario.set(c.key, Number(e.target.value))}
                className="col-span-2 h-1 w-full cursor-pointer accent-[var(--accent)]"
              />
              <Mono className="col-span-2 text-[10.5px] text-[var(--muted)]">{c.source}</Mono>
            </label>
          ))}
        </div>
      </Panel>

      <Panel id="F3" title="Sensitivity ±20%" meta="Δ cash M36" className="lg:col-span-6">
        <EChart option={tornado} label="Sensitivity of 36-month cash to each assumption" className="h-[220px] w-full" />
      </Panel>

      <Panel id="M1" title="Competitive map" meta="price × transparency" className="lg:col-span-6">
        <EChart option={comp} label="Competitor positioning" className="h-[220px] w-full" />
      </Panel>

      <Panel id="Q1" title="Critic queue" meta={`${critique.length} OPEN`} className="lg:col-span-7">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-[12.5px]">
            <tbody>
              {critique.map((c) => (
                <tr key={c.claimId} className="border-b border-[var(--line)] align-top last:border-0">
                  <td className="py-2 pr-3">
                    <Mono
                      className={cn(
                        "rounded-sm px-1.5 py-0.5 text-[10.5px] uppercase",
                        c.severity === "high" ? "bg-[var(--bad-bg)] text-[var(--bad)]" : c.severity === "medium" ? "bg-[var(--warn-bg)] text-[var(--warn)]" : "text-[var(--muted)]",
                      )}
                    >
                      {c.severity}
                    </Mono>
                  </td>
                  <td className="py-2 pr-3">
                    <Mono className="text-[var(--accent)]">{c.claimId}</Mono>
                  </td>
                  <td className="py-2 leading-5">{c.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel id="Q2" title="Missing data" meta="impact" className="lg:col-span-5">
        <ul className="flex flex-col gap-2.5 text-[12.5px]">
          {missingData.map((m) => (
            <li key={m.item} className="grid grid-cols-[minmax(0,1fr)_56px] gap-2">
              <span className="leading-5">
                {m.item}
                <span className="block text-[11.5px] text-[var(--muted)]">{m.plan}</span>
              </span>
              <Mono className={cn("text-right text-[11px]", m.impact === "High" ? "text-[var(--bad)]" : "text-[var(--warn)]")}>{m.impact.toUpperCase()}</Mono>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}

function Workspace() {
  const [taskId, setTaskId] = useState("T3");
  const task = tasks.find((t) => t.id === taskId)!;
  const taskClaims = claims.filter((c) => c.taskId === taskId);
  const taskSources = [...new Set(taskClaims.flatMap((c) => c.evidence.map((e) => e.sourceId)))].map(sourceById);
  const porter = useMemo(() => porterOption(palette), []);

  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-12">
      <Panel id="P1" title="Plan" meta="7 TASKS" className="lg:col-span-3">
        <ul className="font-num flex flex-col text-[12px]">
          {tasks.map((t) => (
            <li key={t.id}>
              <button
                type="button"
                onClick={() => setTaskId(t.id)}
                aria-pressed={t.id === taskId}
                className={cn(
                  "grid w-full grid-cols-[28px_minmax(0,1fr)_auto] items-center gap-2 rounded-[var(--radius)] px-2 py-1.5 text-left focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                  t.id === taskId ? "bg-[var(--surface-2)] text-[var(--fg)]" : "text-[var(--muted)] hover:text-[var(--fg)]",
                )}
              >
                <span className="text-[var(--accent)]">{t.id}</span>
                <span className="font-txt truncate text-[12.5px]">{t.title}</span>
                <span
                  className={cn(
                    "text-[10px] uppercase",
                    t.status === "done" && "text-[var(--ok)]",
                    t.status === "running" && "text-[var(--accent)]",
                    t.status === "blocked" && "text-[var(--bad)]",
                  )}
                >
                  {t.status}
                </span>
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-4 border-t border-[var(--line)] pt-3">
          <p className="font-num mb-2 text-[10.5px] text-[var(--muted)]">PIPELINE</p>
          <div className="font-num flex flex-wrap items-center gap-1 text-[10.5px]">
            {["PLAN", "SEARCH", "EXTRACT", "VERIFY", "CRITIQUE", "SCORE"].map((s, i) => (
              <span key={s} className="flex items-center gap-1">
                <span className={cn("rounded-sm border px-1.5 py-0.5", i < 4 ? "border-[var(--accent)] text-[var(--accent)]" : "border-[var(--line)] text-[var(--muted)]")}>{s}</span>
                {i < 5 && <span className="text-[var(--muted)]">→</span>}
              </span>
            ))}
          </div>
        </div>
      </Panel>

      <Panel id={task.id} title={task.title} meta={`${task.sources} SRC · ${task.supported}/${task.claims} SUP`} className="lg:col-span-6">
        {task.note && <p className="mb-3 rounded-[var(--radius)] border border-[var(--warn)]/40 bg-[var(--warn-bg)] px-2.5 py-1.5 text-[12px] text-[var(--warn)]">{task.note}</p>}
        <p className="font-num mb-1.5 text-[10.5px] text-[var(--muted)]">QUERIES · TAVILY ADVANCED</p>
        <ul className="font-num mb-4 flex flex-col gap-1 text-[12px]">
          {task.queries.length ? (
            task.queries.map((q, i) => (
              <li key={q} className="flex gap-2">
                <span className="text-[var(--muted)]">&gt;</span>
                <span className="min-w-0 flex-1 truncate">{q}</span>
                <span className="text-[var(--muted)]">{[6, 5, 4, 3][i] ?? 2} hits</span>
              </li>
            ))
          ) : (
            <li className="text-[var(--muted)]">— no queries yet</li>
          )}
        </ul>
        <p className="font-num mb-1.5 text-[10.5px] text-[var(--muted)]">SOURCES LINKED TO CLAIMS</p>
        <div className="mb-4 overflow-x-auto">
          <table className="w-full min-w-[460px] text-left text-[12px]">
            <thead className="font-num text-[10px] text-[var(--muted)]">
              <tr>
                <th className="py-1 pr-2 font-normal">ID</th>
                <th className="py-1 pr-2 font-normal">PUBLISHER</th>
                <th className="py-1 pr-2 font-normal">KIND</th>
                <th className="py-1 pr-2 font-normal">TIER</th>
                <th className="py-1 font-normal">DATE</th>
              </tr>
            </thead>
            <tbody>
              {taskSources.map((s) => (
                <tr key={s.id} className="border-t border-[var(--line)]">
                  <td className="font-num py-1.5 pr-2 text-[var(--accent)]">{s.id}</td>
                  <td className="py-1.5 pr-2">{s.publisher}</td>
                  <td className="font-num py-1.5 pr-2 text-[var(--muted)] uppercase">{s.kind}</td>
                  <td className={cn("font-num py-1.5 pr-2", s.tier === "A" ? "text-[var(--ok)]" : s.tier === "C" ? "text-[var(--warn)]" : "")}>{s.tier}</td>
                  <td className="font-num py-1.5 text-[var(--muted)]">{s.published}</td>
                </tr>
              ))}
              {!taskSources.length && (
                <tr>
                  <td colSpan={5} className="py-2 text-[var(--muted)]">
                    No sources linked to claims yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <p className="font-num mb-1.5 text-[10.5px] text-[var(--muted)]">CLAIMS</p>
        <ul className="flex flex-col gap-1.5 text-[12.5px]">
          {taskClaims.map((c) => (
            <li key={c.id} className="grid grid-cols-[28px_36px_minmax(0,1fr)] gap-2">
              <Mono className="text-[var(--accent)]">{c.id}</Mono>
              <Mono className={cn("text-[11px]", statusText[c.status])}>{statusMeta[c.status].short}</Mono>
              <span className="leading-5">{c.text}</span>
            </li>
          ))}
          {!taskClaims.length && <li className="text-[var(--muted)]">No claims yet.</li>}
        </ul>
      </Panel>

      <Panel id="L1" title="Agent log" meta={<Activity className="size-3.5 text-[var(--accent)]" />} className="lg:col-span-3">
        <ul className="font-num flex flex-col gap-2 text-[11.5px]">
          {activity.map((a) => (
            <li key={a.t + a.text} className="leading-4">
              <span className="text-[var(--muted)]">{a.t}</span> <span className="text-[var(--accent)]">[{a.agent.toUpperCase()}]</span>
              <span className="block text-[var(--fg)]">{a.text}</span>
            </li>
          ))}
        </ul>
      </Panel>

      <Panel id="X1" title="SWOT" meta="claim-linked" className="lg:col-span-5">
        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-[var(--radius)] bg-[var(--line)] text-[12px]">
          {(Object.entries(frameworks.swot) as [string, string[]][]).map(([k, items]) => (
            <div key={k} className="bg-[var(--surface)] p-2.5">
              <p className="font-num mb-1 text-[10px] text-[var(--accent)] uppercase">{k}</p>
              <ul className="flex flex-col gap-1 leading-4">
                {items.map((i) => (
                  <li key={i}>{i}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </Panel>
      <Panel id="X2" title="PESTLE" meta="impact 1–5" className="lg:col-span-4">
        <ul className="flex flex-col gap-1.5 text-[12px]">
          {frameworks.pestle.map((p) => (
            <li key={p.factor} className="grid grid-cols-[22px_70px_minmax(0,1fr)] items-center gap-2">
              <Mono className="text-[var(--accent)]">{p.factor[0]}</Mono>
              <div className="flex gap-0.5" aria-label={`${p.factor}: impact ${p.rating} of 5`}>
                {Array.from({ length: 5 }, (_, i) => (
                  <span key={i} className={cn("h-2.5 flex-1", i < p.rating ? "bg-[var(--accent)]" : "bg-[var(--line)]")} />
                ))}
              </div>
              <span className="truncate text-[var(--muted)]" title={p.note}>
                {p.note}
              </span>
            </li>
          ))}
        </ul>
      </Panel>
      <Panel id="X3" title="Five forces" meta="1–5" className="lg:col-span-3">
        <EChart option={porter} label="Porter's five forces" className="h-[170px] w-full" />
      </Panel>
    </div>
  );
}

function Evidence() {
  const [claimId, setClaimId] = useState("C4");
  const graph = useMemo(() => evidenceGraph(palette, claimId), [claimId]);
  const claim = claims.find((c) => c.id === claimId)!;

  return (
    <div className="grid grid-cols-1 gap-3 lg:grid-cols-12">
      <Panel id="E1" title="Claims" meta={`${claims.length} · ENT MAX`} className="lg:col-span-4">
        <ul className="flex flex-col text-[12.5px]">
          {claims.map((c) => {
            const best = Math.max(...c.evidence.map((e) => e.entailment));
            return (
              <li key={c.id}>
                <button
                  type="button"
                  onClick={() => setClaimId(c.id)}
                  aria-pressed={c.id === claimId}
                  className={cn(
                    "grid w-full grid-cols-[28px_36px_minmax(0,1fr)_34px] items-start gap-2 rounded-[var(--radius)] px-2 py-2 text-left focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                    c.id === claimId ? "bg-[var(--surface-2)] shadow-[inset_2px_0_0_var(--accent)]" : "hover:bg-[var(--surface-2)]",
                  )}
                >
                  <Mono className="text-[var(--accent)]">{c.id}</Mono>
                  <Mono className={cn("text-[11px]", statusText[c.status])}>{statusMeta[c.status].short}</Mono>
                  <span className="line-clamp-2 leading-5">{c.text}</span>
                  <Mono className="text-right text-[11px] text-[var(--muted)]">{best.toFixed(2)}</Mono>
                </button>
              </li>
            );
          })}
        </ul>
      </Panel>

      <Panel id={claim.id} title={statusMeta[claim.status].label} meta={`TASK ${claim.taskId}`} className="lg:col-span-5">
        <p className="text-[16px] leading-snug font-medium">{claim.text}</p>
        <p className="mt-3 rounded-[var(--radius)] border border-[var(--line)] bg-[var(--bg)] p-2.5 text-[12.5px] leading-5 text-[var(--muted)]">
          <span className="font-num text-[10.5px] text-[var(--accent)]">VERIFIER › </span>
          {claim.rationale}
        </p>
        <ul className="mt-4 flex flex-col gap-4">
          {claim.evidence.map((e, i) => {
            const s = sourceById(e.sourceId);
            return (
              <li key={e.sourceId + i} className="rounded-[var(--radius)] border border-[var(--line)]">
                <div className="font-num flex flex-wrap items-center justify-between gap-2 border-b border-[var(--line)] px-2.5 py-1.5 text-[11px]">
                  <span>
                    <span className="text-[var(--accent)]">{s.id}</span> {s.domain}
                    {e.page ? ` · p.${e.page}` : ""} · TIER {s.tier}
                  </span>
                  <span className={cn("uppercase", e.relation === "supports" ? "text-[var(--ok)]" : e.relation === "contradicts" ? "text-[var(--bad)]" : "text-[var(--warn)]")}>
                    {e.relation === "related" ? "relevant, not support" : e.relation}
                  </span>
                </div>
                <p className="px-2.5 py-2.5 text-[13px] leading-6">
                  <HighlightedExtract text={e.extract} highlight={e.highlight} markClassName="bg-[rgba(59,140,255,0.22)] text-[var(--fg)] outline outline-1 outline-[var(--accent)]/50" />
                </p>
                <div className="font-num grid grid-cols-2 gap-px border-t border-[var(--line)] bg-[var(--line)] text-[11px]">
                  <span className="bg-[var(--surface)] px-2.5 py-1.5">
                    REL <span className="text-[var(--fg)]">{e.relevance.toFixed(2)}</span> <span className="text-[var(--muted)]">retrieval</span>
                  </span>
                  <span className="bg-[var(--surface)] px-2.5 py-1.5">
                    ENT <span className={e.entailment >= 0.7 ? "text-[var(--ok)]" : e.entailment >= 0.4 ? "text-[var(--warn)]" : "text-[var(--bad)]"}>{e.entailment.toFixed(2)}</span>{" "}
                    <span className="text-[var(--muted)]">verifier</span>
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
        <p className="font-num mt-3 text-[10.5px] leading-4 text-[var(--muted)]">
          RULE: SUPPORTED ⇔ ENT ≥ 0.70 ON A TIER-A SOURCE OR ≥ 2 INDEPENDENT SOURCES. RELEVANCE NEVER COUNTS AS SUPPORT.
        </p>
      </Panel>

      <Panel id="G1" title="Evidence graph" meta="click a claim" className="lg:col-span-3">
        <EChart
          option={graph}
          label="Network of claims and the sources linked to them"
          className="h-[340px] w-full"
          onClick={(p) => {
            if (p.name && claims.some((c) => c.id === p.name)) setClaimId(p.name);
          }}
        />
        <ul className="font-num mt-2 flex flex-col gap-1 text-[10.5px] text-[var(--muted)]">
          <li>
            <span className="text-[var(--ok)]">━</span> supports <span className="ml-2 text-[var(--bad)]">━</span> contradicts <span className="ml-2">┅</span> relevant only
          </li>
          <li>● claim · ■ source</li>
        </ul>
      </Panel>
    </div>
  );
}
