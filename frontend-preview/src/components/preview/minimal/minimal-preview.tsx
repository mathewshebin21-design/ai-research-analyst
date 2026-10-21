"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { ArrowLeft, ArrowRight } from "lucide-react";

import { Slider } from "@/components/ui/slider";
import { eurK } from "@/lib/finance";
import {
  claimCounts,
  claims,
  critique,
  factors,
  frameworks,
  missingData,
  question,
  recommendation,
  sourceById,
  statusMeta,
  tasks,
  type ClaimStatus,
} from "@/lib/sample-data";
import { controls, useScenario } from "@/lib/use-scenario";
import { cn } from "@/lib/utils";
import { cashOption, competitorOption, tornadoOption, type Palette } from "../shared/charts";
import { EChart } from "../shared/echart";
import { HighlightedExtract } from "../shared/highlight";
import { IllustrativeTag } from "../shared/illustrative";
import { laterNav, navItems, type PreviewProps } from "../shared/types";

const palette: Palette = {
  fg: "#121212",
  muted: "#6c675d",
  line: "#dcd7cc",
  surface: "#fffefb",
  accent: "#121212",
  series: { base: "#121212", optimistic: "#2d6a4c", conservative: "#9e3626" },
  ok: "#2d6a4c",
  warn: "#8c5f0b",
  bad: "#9e3626",
  font: "Schibsted Grotesk, system-ui, sans-serif",
};

const ease = [0.22, 1, 0.36, 1] as const;

const statusInk: Record<ClaimStatus, string> = {
  supported: "text-[var(--ok)]",
  partial: "text-[var(--warn)]",
  contradicted: "text-[var(--bad)]",
  unsupported: "text-[var(--bad)]",
  missing: "text-[var(--muted)]",
};

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <p className={cn("text-[11px] tracking-[0.14em] text-[var(--muted)] uppercase", className)}>{children}</p>;
}

function Chapter({ label, title, children }: { label: string; title: string; children: React.ReactNode }) {
  return (
    <section className="grid gap-6 border-t border-[var(--fg)] pt-6 md:grid-cols-[200px_minmax(0,1fr)] md:gap-12">
      <div className="flex flex-col gap-1">
        <Label>{label}</Label>
        <h2 className="font-disp text-[30px] leading-none">{title}</h2>
      </div>
      <div className="min-w-0">{children}</div>
    </section>
  );
}

export function MinimalPreview({ view, go }: PreviewProps) {
  const scenario = useScenario();

  return (
    <div>
      <header className="gutter mx-auto flex max-w-[1180px] flex-wrap items-center justify-between gap-x-8 gap-y-3 py-6">
        <p className="font-disp text-[22px] leading-none italic">Verdant Stride</p>
        <nav aria-label="Primary" className="flex flex-wrap items-center gap-x-6 gap-y-1 text-[14px]">
          {navItems.map((n) => (
            <button
              key={n.view}
              type="button"
              onClick={() => go("minimal", n.view)}
              aria-current={n.view === view ? "page" : undefined}
              className={cn("relative py-1 transition-colors focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-[var(--ring)]", n.view === view ? "text-[var(--fg)]" : "text-[var(--muted)] hover:text-[var(--fg)]")}
            >
              {n.label.replace("Executive d", "D")}
              {n.view === view && <motion.span layoutId="min-nav" className="absolute inset-x-0 -bottom-0.5 h-px bg-[var(--fg)]" transition={{ duration: 0.45, ease }} />}
            </button>
          ))}
          <span className="hidden text-[var(--muted)]/60 xl:inline" title="Designed after approval">
            {laterNav.join(" · ")}
          </span>
        </nav>
        <IllustrativeTag />
      </header>

      <AnimatePresence mode="wait" initial={false}>
        <motion.main
          key={view}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.6, ease }}
          className="gutter mx-auto max-w-[1180px] pt-6 pb-32"
        >
          {view === "dashboard" && <Dashboard scenario={scenario} />}
          {view === "workspace" && <Workspace />}
          {view === "evidence" && <Evidence />}
        </motion.main>
      </AnimatePresence>
    </div>
  );
}

function Dashboard({ scenario }: { scenario: ReturnType<typeof useScenario> }) {
  const base = scenario.results.base;
  const counts = claimCounts();
  const cash = useMemo(() => cashOption(scenario.results, palette, { labels: true }), [scenario.results]);
  const tornado = useMemo(() => tornadoOption(scenario.tornado, palette), [scenario.tornado]);
  const comp = useMemo(() => competitorOption(palette), []);
  const a = scenario.assumptions;

  const numbers = [
    { value: base.breakEvenMonth ? `${base.breakEvenMonth}` : "—", unit: base.breakEvenMonth ? "months to break even" : "no break-even in 36 months" },
    { value: eurK(-base.peakFunding), unit: "peak funding need" },
    { value: eurK(base.cash36), unit: "cash at month 36" },
    { value: `${counts.supported}/${claims.length}`, unit: "claims supported" },
  ];

  return (
    <div className="flex flex-col gap-20">
      <section className="flex flex-col gap-8">
        <Label>
          {question.workspace} · {question.created}
        </Label>
        <h1 className="font-disp max-w-[22ch] text-[clamp(38px,6vw,76px)] leading-[0.98] tracking-[-0.01em]">{question.text}</h1>
        <div className="grid gap-8 border-t border-[var(--line)] pt-8 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
          <div>
            <Label className="mb-3">The answer · {recommendation.stance}</Label>
            <p className="font-disp text-[clamp(28px,3.4vw,42px)] leading-[1.08] italic">{recommendation.verdict}.</p>
            <p className="mt-5 max-w-[58ch] text-[15.5px] leading-7 text-[var(--muted)]">{recommendation.summary}</p>
          </div>
          <div className="flex flex-col gap-5 text-[14.5px] leading-6">
            <div>
              <Label className="mb-2">Only if</Label>
              <ul className="flex flex-col gap-1.5">
                {recommendation.conditions.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
            <p className="border-t border-[var(--line)] pt-4 text-[var(--muted)]">
              <span className="text-[var(--fg)]">{recommendation.confidenceLabel} confidence</span>, {Math.round(recommendation.confidence * 100)} of 100. Set by how much of
              the case rests on evidence, not by the model’s own view of itself.
            </p>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-2 gap-y-8 border-y border-[var(--line)] py-8 md:grid-cols-4">
        {numbers.map((n, i) => (
          <div key={n.unit} className={cn("flex flex-col gap-2 px-0 md:px-6", i > 0 && "md:border-l md:border-[var(--line)]", i === 0 && "md:pl-0")}>
            <motion.span key={n.value} initial={{ opacity: 0.3 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }} className="font-disp tnum text-[clamp(40px,5vw,64px)] leading-none">
              {n.value}
            </motion.span>
            <span className="text-[13px] text-[var(--muted)]">{n.unit}</span>
          </div>
        ))}
      </section>

      <Chapter label="Scenarios" title="The money">
        <p className="mb-6 max-w-[62ch] text-[17px] leading-8">
          At <strong className="font-semibold">€{a.cac.toFixed(0)}</strong> to win a customer, a <strong className="font-semibold">€{a.price.toFixed(0)}</strong> price, a{" "}
          <strong className="font-semibold">{Math.round(a.returnRate * 100)}%</strong> return rate and{" "}
          <strong className="font-semibold">{eurK(a.marketing)}</strong> a month on marketing, the base case{" "}
          {base.breakEvenMonth ? (
            <>
              turns a monthly profit in month <strong className="font-semibold">{base.breakEvenMonth}</strong>
            </>
          ) : (
            "does not reach a monthly profit within three years"
          )}{" "}
          and needs <strong className="font-semibold">{eurK(-base.peakFunding)}</strong> of funding at its low point.
        </p>
        <EChart option={cash} label="Cumulative cash by scenario over 36 months" className="h-[320px] w-full" />
        <div className="mt-8 grid gap-x-10 gap-y-6 sm:grid-cols-2 lg:grid-cols-3">
          {controls.map((c) => (
            <div key={c.key}>
              <div className="flex items-baseline justify-between gap-2">
                <label htmlFor={`mn-${c.key}`} className="text-[13.5px]">
                  {c.label}
                </label>
                <span className="font-disp tnum text-[22px] leading-none">{c.format(a[c.key])}</span>
              </div>
              <Slider id={`mn-${c.key}`} aria-label={c.label} min={c.min} max={c.max} step={c.step} value={[a[c.key]]} onValueChange={([v]) => scenario.set(c.key, v)} />
              <p className="text-[11.5px] text-[var(--muted)]">{c.source}</p>
            </div>
          ))}
          <div className="flex items-end">
            <button
              type="button"
              onClick={scenario.reset}
              disabled={!scenario.changed}
              className="border-b border-[var(--fg)] pb-0.5 text-[13.5px] disabled:border-transparent disabled:text-[var(--muted)]"
            >
              Return to the base case
            </button>
          </div>
        </div>
        <div className="mt-12 grid gap-8 md:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
          <EChart option={tornado} label="Sensitivity of 36-month cash to each assumption" className="h-[230px] w-full" />
          <p className="self-center text-[15px] leading-7 text-[var(--muted)]">
            Move each input by a fifth and watch the month-36 cash. Acquisition cost swings it the most, and it is the one number no source
            gives us.
          </p>
        </div>
      </Chapter>

      <Chapter label="Scoring" title={`Why ${Math.round(factors.reduce((t, f) => t + f.weight * f.score, 0))}`}>
        <ul className="flex flex-col">
          {factors.map((f) => (
            <li key={f.key} className="grid grid-cols-[minmax(0,1fr)_auto] items-baseline gap-x-6 gap-y-1 border-b border-[var(--line)] py-4 md:grid-cols-[220px_80px_minmax(0,1fr)_64px]">
              <span className="text-[15px]">{f.label}</span>
              <span className="font-disp tnum text-[34px] leading-none md:order-4 md:text-right">{f.score}</span>
              <span className="text-[12.5px] text-[var(--muted)] md:order-2">
                weight {Math.round(f.weight * 100)}%<span className="block">evidence {Math.round(f.coverage * 100)}%</span>
              </span>
              <span className="col-span-2 text-[14px] text-[var(--muted)] md:order-3 md:col-span-1">{f.note}</span>
            </li>
          ))}
        </ul>
      </Chapter>

      <Chapter label="Market" title="Who is there">
        <EChart option={comp} label="Competitor price versus supply-chain transparency" className="h-[320px] w-full" />
      </Chapter>

      <Chapter label="Doubts" title="What we don’t know">
        <div className="grid gap-10 md:grid-cols-2">
          <ul className="flex flex-col gap-4 text-[15px] leading-7">
            {critique.map((c) => (
              <li key={c.claimId}>
                <span className={cn("mr-2 text-[11px] tracking-[0.14em] uppercase", c.severity === "high" ? "text-[var(--bad)]" : "text-[var(--muted)]")}>{c.severity}</span>
                {c.text}
              </li>
            ))}
          </ul>
          <ul className="flex flex-col gap-4 text-[15px] leading-7">
            {missingData.map((m) => (
              <li key={m.item}>
                {m.item}
                <span className="block text-[13.5px] text-[var(--muted)]">
                  {m.impact} impact. {m.plan}.
                </span>
              </li>
            ))}
          </ul>
        </div>
      </Chapter>
    </div>
  );
}

function Workspace() {
  const [open, setOpen] = useState("T4");

  return (
    <div className="flex flex-col gap-20">
      <section className="flex flex-col gap-6">
        <Label>Research plan · generated for this question</Label>
        <h1 className="font-disp max-w-[20ch] text-[clamp(38px,6vw,72px)] leading-[0.98]">Seven questions before we can answer one.</h1>
      </section>

      <ol className="flex flex-col border-t border-[var(--fg)]">
        {tasks.map((t) => {
          const isOpen = open === t.id;
          const taskClaims = claims.filter((c) => c.taskId === t.id);
          return (
            <li key={t.id} className="border-b border-[var(--line)]">
              <button
                type="button"
                onClick={() => setOpen(isOpen ? "" : t.id)}
                aria-expanded={isOpen}
                className="grid w-full grid-cols-[48px_minmax(0,1fr)_auto] items-baseline gap-4 py-5 text-left focus-visible:outline-2 focus-visible:outline-[var(--ring)]"
              >
                <span className="tnum text-[13px] text-[var(--muted)]">{t.id}</span>
                <span className="font-disp text-[clamp(22px,2.6vw,30px)] leading-tight">{t.title}</span>
                <span
                  className={cn(
                    "text-[12px] tracking-[0.1em] uppercase",
                    t.status === "done" && "text-[var(--ok)]",
                    t.status === "running" && "text-[var(--fg)]",
                    t.status === "queued" && "text-[var(--muted)]",
                    t.status === "blocked" && "text-[var(--bad)]",
                  )}
                >
                  {t.status === "running" ? (
                    <span className="inline-flex items-center gap-2">
                      <motion.span className="size-1.5 rounded-full bg-current" animate={{ opacity: [1, 0.2, 1] }} transition={{ duration: 1.6, repeat: Infinity }} />
                      in progress
                    </span>
                  ) : (
                    t.status
                  )}
                </span>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.5, ease }}
                    className="overflow-hidden"
                  >
                    <div className="grid gap-8 pb-8 pl-0 md:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] md:pl-16">
                      <div className="flex flex-col gap-4 text-[14px]">
                        {t.note && <p className="text-[var(--warn)]">{t.note}</p>}
                        <div>
                          <Label className="mb-2">Searched</Label>
                          {t.queries.length ? (
                            <ul className="flex flex-col gap-1 text-[var(--muted)]">
                              {t.queries.map((q) => (
                                <li key={q}>“{q}”</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-[var(--muted)]">Nothing yet.</p>
                          )}
                        </div>
                        <p className="tnum text-[var(--muted)]">
                          {t.sources} sources collected · {t.supported} of {t.claims} claims supported
                        </p>
                      </div>
                      <ul className="flex flex-col gap-4">
                        {taskClaims.map((c) => (
                          <li key={c.id} className="flex flex-col gap-1">
                            <span className={cn("text-[11px] tracking-[0.14em] uppercase", statusInk[c.status])}>
                              {c.id} · {statusMeta[c.status].label}
                            </span>
                            <span className="font-disp text-[21px] leading-snug">{c.text}</span>
                          </li>
                        ))}
                        {!taskClaims.length && <li className="text-[14px] text-[var(--muted)]">No claims yet.</li>}
                      </ul>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </li>
          );
        })}
      </ol>

      <Chapter label="Frameworks" title="The usual lenses">
        <div className="grid gap-12">
          <div className="grid gap-px bg-[var(--line)] sm:grid-cols-2">
            {(Object.entries(frameworks.swot) as [string, string[]][]).map(([k, items]) => (
              <div key={k} className="bg-[var(--bg)] p-5 sm:p-6">
                <p className="font-disp mb-3 text-[24px] capitalize italic">{k}</p>
                <ul className="flex flex-col gap-1.5 text-[14.5px] leading-6">
                  {items.map((i) => (
                    <li key={i}>{i}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="grid gap-12 md:grid-cols-2">
            <div>
              <Label className="mb-3">PESTLE · impact out of 5</Label>
              <ul className="flex flex-col">
                {frameworks.pestle.map((p) => (
                  <li key={p.factor} className="grid grid-cols-[minmax(0,1fr)_32px] gap-x-4 border-b border-[var(--line)] py-3 text-[14.5px]">
                    <span>{p.factor}</span>
                    <span className="font-disp tnum text-right text-[24px] leading-none">{p.rating}</span>
                    <span className="col-span-2 text-[13px] text-[var(--muted)]">{p.note}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <Label className="mb-3">Five Forces · intensity out of 5</Label>
              <ul className="flex flex-col">
                {frameworks.porter.map((f) => (
                  <li key={f.force} className="flex flex-col gap-2 border-b border-[var(--line)] py-3">
                    <div className="flex items-baseline justify-between text-[14.5px]">
                      <span>{f.force}</span>
                      <span className="font-disp tnum text-[24px] leading-none">{f.level.toFixed(1)}</span>
                    </div>
                    <div className="h-px bg-[var(--line)]">
                      <motion.div
                        className="h-px bg-[var(--fg)]"
                        initial={false}
                        animate={{ width: `${(f.level / 5) * 100}%` }}
                        transition={{ duration: 0.8, ease }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </Chapter>
    </div>
  );
}

function Evidence() {
  const [index, setIndex] = useState(1);
  const claim = claims[index];
  const counts = claimCounts();
  const step = (d: number) => setIndex((i) => (i + d + claims.length) % claims.length);

  return (
    <div className="grid gap-12 lg:grid-cols-[260px_minmax(0,1fr)]">
      <aside className="flex flex-col gap-6 lg:sticky lg:top-6 lg:self-start">
        <div>
          <Label className="mb-3">Evidence file</Label>
          <ul className="flex flex-col gap-1 text-[13px] text-[var(--muted)]">
            {(Object.keys(counts) as ClaimStatus[]).map((s) => (
              <li key={s} className="flex justify-between">
                <span>{statusMeta[s].label}</span>
                <span className="tnum text-[var(--fg)]">{counts[s]}</span>
              </li>
            ))}
          </ul>
        </div>
        <ol className="flex flex-row flex-wrap gap-1 lg:flex-col lg:gap-0">
          {claims.map((c, i) => (
            <li key={c.id}>
              <button
                type="button"
                onClick={() => setIndex(i)}
                aria-current={i === index}
                className={cn(
                  "relative flex w-full items-baseline gap-3 py-1.5 pr-2 text-left text-[13px] focus-visible:outline-2 focus-visible:outline-[var(--ring)] lg:pl-4",
                  i === index ? "text-[var(--fg)]" : "text-[var(--muted)] hover:text-[var(--fg)]",
                )}
              >
                {i === index && <motion.span layoutId="min-claim" className="absolute top-1 bottom-1 left-0 hidden w-px bg-[var(--fg)] lg:block" transition={{ duration: 0.4, ease }} />}
                <span className="tnum">{c.id}</span>
                <span className={cn("hidden truncate lg:inline", i === index && statusInk[c.status])}>{statusMeta[c.status].label}</span>
              </button>
            </li>
          ))}
        </ol>
      </aside>

      <div className="min-w-0">
        <AnimatePresence mode="wait" initial={false}>
          <motion.article
            key={claim.id}
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -24 }}
            transition={{ duration: 0.45, ease }}
            className="flex flex-col gap-10"
          >
            <header className="flex flex-col gap-5">
              <Label className={statusInk[claim.status]}>
                Claim {claim.id} · {statusMeta[claim.status].label}
              </Label>
              <h1 className="font-disp text-[clamp(32px,4.4vw,56px)] leading-[1.04]">{claim.text}</h1>
              <p className="max-w-[60ch] border-l border-[var(--fg)] pl-5 text-[16px] leading-7">{claim.rationale}</p>
            </header>

            {claim.evidence.map((e, i) => {
              const s = sourceById(e.sourceId);
              return (
                <figure key={e.sourceId + i} className="grid gap-5 border-t border-[var(--line)] pt-8 md:grid-cols-[minmax(0,1fr)_220px] md:gap-10">
                  <blockquote className="font-disp text-[clamp(22px,2.4vw,30px)] leading-[1.3]">
                    “<HighlightedExtract text={e.extract} highlight={e.highlight} markClassName="bg-transparent text-[var(--fg)] underline decoration-[var(--fg)] decoration-1 underline-offset-[6px]" />”
                  </blockquote>
                  <figcaption className="flex flex-col gap-4 text-[13px] text-[var(--muted)]">
                    <span>
                      <span className="text-[var(--fg)]">{s.publisher}</span>
                      <span className="block italic">{s.title}</span>
                      {s.published}
                      {e.page ? ` · page ${e.page}` : ""} · tier {s.tier}
                    </span>
                    <span className="flex flex-col gap-1">
                      <span className="flex justify-between">
                        Relevant to topic <span className="tnum text-[var(--fg)]">{e.relevance.toFixed(2)}</span>
                      </span>
                      <span className="flex justify-between">
                        Supports the claim{" "}
                        <span className={cn("tnum", e.relation === "supports" ? "text-[var(--ok)]" : e.relation === "contradicts" ? "text-[var(--bad)]" : "text-[var(--warn)]")}>
                          {e.entailment.toFixed(2)}
                        </span>
                      </span>
                    </span>
                  </figcaption>
                </figure>
              );
            })}
          </motion.article>
        </AnimatePresence>

        <div className="mt-12 flex items-center justify-between border-t border-[var(--fg)] pt-5 text-[14px]">
          <button type="button" onClick={() => step(-1)} className="inline-flex items-center gap-2 focus-visible:outline-2 focus-visible:outline-[var(--ring)]">
            <ArrowLeft className="size-4" /> Previous claim
          </button>
          <span className="tnum text-[var(--muted)]">
            {index + 1} / {claims.length}
          </span>
          <button type="button" onClick={() => step(1)} className="inline-flex items-center gap-2 focus-visible:outline-2 focus-visible:outline-[var(--ring)]">
            Next claim <ArrowRight className="size-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
