"use client";

import { ArrowRight } from "lucide-react";

import { architecture, auditRows, costs, evidenceRule, milestones, preserve, type AuditStatus } from "@/lib/brief";
import type { Design } from "@/lib/use-hash-route";
import { cn } from "@/lib/utils";
import type { Go } from "./shared/types";

const statusStyle: Record<AuditStatus, string> = {
  real: "bg-[var(--ok-bg)] text-[var(--ok)]",
  partial: "bg-[var(--warn-bg)] text-[var(--warn)]",
  simulated: "bg-[var(--bad-bg)] text-[var(--bad)]",
  broken: "bg-[var(--bad)] text-white",
  unused: "border border-dashed border-[var(--line)] text-[var(--muted)]",
};

const directions: { id: Design; letter: string; name: string; line: string; swatches: string[]; fonts: string; sample: string; sampleClass: string }[] = [
  {
    id: "executive",
    letter: "A",
    name: "Executive Intelligence",
    line: "A board paper you can interrogate. Navy and ivory, gold used only for the decision and its conditions.",
    swatches: ["#0b1628", "#162a47", "#efe9dc", "#c8a65d"],
    fonts: "Newsreader · Hanken Grotesk",
    sample: "Run a 6-month online pilot",
    sampleClass: "bg-[#0b1628] text-[#efe9dc] [font-family:var(--font-newsreader)] text-[22px] leading-tight",
  },
  {
    id: "command",
    letter: "B",
    name: "Intelligence Command",
    line: "An analyst terminal. Graphite panels, electric-blue focus, every claim and source addressable by ID.",
    swatches: ["#0d0f12", "#1b1f26", "#e4e8ee", "#3b8cff"],
    fonts: "IBM Plex Sans · IBM Plex Mono",
    sample: "C2 · UNSUPPORTED · ent 0.21",
    sampleClass: "bg-[#0d0f12] text-[#3b8cff] [font-family:var(--font-plex-mono)] text-[14px] tracking-wide",
  },
  {
    id: "minimal",
    letter: "C",
    name: "Minimal Intelligence",
    line: "An editorial long-read. Warm white, black type, large numerals and quiet motion between states.",
    swatches: ["#f8f6f1", "#efebe3", "#121212", "#6c675d"],
    fonts: "Instrument Serif · Schibsted Grotesk",
    sample: "€329k peak funding",
    sampleClass: "bg-[#f8f6f1] text-[#121212] [font-family:var(--font-instrument)] text-[26px] italic",
  },
];

function Section({ id, title, kicker, children }: { id: string; title: string; kicker: string; children: React.ReactNode }) {
  return (
    <section id={id} className="grid gap-5 border-t border-[var(--line)] py-10 md:grid-cols-[220px_minmax(0,1fr)] md:gap-10">
      <header className="flex flex-col gap-1">
        <p className="text-[11px] font-semibold tracking-[0.12em] text-[var(--muted)] uppercase">{kicker}</p>
        <h2 className="text-xl font-semibold">{title}</h2>
      </header>
      <div className="min-w-0">{children}</div>
    </section>
  );
}

export function Brief({ go }: { go: Go }) {
  const runLow = costs.perRun.reduce((s, r) => s + r.low, 0);
  const runHigh = costs.perRun.reduce((s, r) => s + r.high, 0);
  const monthLow = costs.monthly.reduce((s, r) => s + r.low, 0);
  const monthHigh = costs.monthly.reduce((s, r) => s + r.high, 0);
  const weeks = milestones.reduce((s, m) => s + Number(m.weeks), 0);

  return (
    <main className="gutter mx-auto max-w-[1180px] py-10 [font-family:var(--font-hanken)]">
      <header className="flex flex-col gap-4 pb-10">
        <p className="text-[11px] font-semibold tracking-[0.12em] text-[var(--muted)] uppercase">
          AI Research Analyst · redesign review · 21 Oct 2026
        </p>
        <h1 className="max-w-3xl text-[clamp(28px,4vw,44px)] leading-[1.1] font-semibold tracking-tight">
          Three directions for the Strategic Intelligence Hub
        </h1>
        <p className="max-w-[65ch] text-[15px] leading-7 text-[var(--muted)]">
          Each preview is a working Next.js build of the same three screens: executive dashboard, research workspace and evidence
          inspector. All data is illustrative and labelled as such. Pick one direction to approve; nothing in production changes
          until you do.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        {directions.map((d) => (
          <button
            key={d.id}
            type="button"
            onClick={() => go(d.id, "dashboard")}
            className="group flex flex-col overflow-hidden rounded-[var(--radius)] border border-[var(--line)] bg-[var(--surface)] text-left transition-shadow hover:shadow-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--ring)]"
          >
            <div className={cn("flex h-28 items-end p-4", d.sampleClass)}>{d.sample}</div>
            <div className="flex flex-1 flex-col gap-3 p-4">
              <div className="flex items-baseline justify-between gap-2">
                <h2 className="text-base font-semibold">
                  {d.letter}. {d.name}
                </h2>
                <ArrowRight className="size-4 shrink-0 text-[var(--muted)] transition-transform group-hover:translate-x-0.5" />
              </div>
              <p className="text-sm leading-6 text-[var(--muted)]">{d.line}</p>
              <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                <div className="flex">
                  {d.swatches.map((s) => (
                    <span key={s} className="size-5 border border-black/10 first:rounded-l-full last:rounded-r-full" style={{ background: s }} />
                  ))}
                </div>
                <span className="text-[11px] text-[var(--muted)]">{d.fonts}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
      <p className="pt-3 text-xs text-[var(--muted)]">
        Inside a preview, the bar at the bottom switches direction while keeping the screen you are on.
      </p>

      <div className="pt-10">
        <Section id="audit" kicker="1 · Repository audit" title="What is real today">
          <p className="mb-4 max-w-[65ch] text-sm leading-6 text-[var(--muted)]">
            Audited at commit 00e6826 by reading every file and running the app headlessly. The deployed Streamlit URL was not
            reachable from the build environment, so findings come from the code and the local run.
          </p>
          <div className="overflow-x-auto rounded-[var(--radius)] border border-[var(--line)] bg-[var(--surface)]">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="text-[11px] tracking-[0.08em] text-[var(--muted)] uppercase">
                <tr className="border-b border-[var(--line)]">
                  <th className="px-3 py-2 font-semibold">Area</th>
                  <th className="px-3 py-2 font-semibold">Status</th>
                  <th className="px-3 py-2 font-semibold">Finding</th>
                </tr>
              </thead>
              <tbody>
                {auditRows.map((r) => (
                  <tr key={r.area} className="border-b border-[var(--line)] align-top last:border-0">
                    <td className="px-3 py-2.5">
                      <div className="font-medium">{r.area}</div>
                      <div className="text-xs text-[var(--muted)] [font-family:var(--font-plex-mono)]">{r.files}</div>
                    </td>
                    <td className="px-3 py-2.5">
                      <span className={cn("rounded-full px-2 py-0.5 text-[11px] font-semibold capitalize", statusStyle[r.status])}>{r.status}</span>
                    </td>
                    <td className="px-3 py-2.5 leading-6 text-[var(--muted)]">{r.finding}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <h3 className="pt-6 pb-2 text-sm font-semibold">Preserved and extended</h3>
          <ul className="grid gap-1.5 text-sm leading-6 text-[var(--muted)] md:grid-cols-2">
            {preserve.map((p) => (
              <li key={p} className="flex gap-2">
                <span aria-hidden className="text-[var(--ok)]">✓</span>
                {p}
              </li>
            ))}
          </ul>
        </Section>

        <Section id="architecture" kicker="2 · Proposed architecture" title="Keep Python, add an API">
          <p className="mb-4 max-w-[65ch] text-sm leading-6 text-[var(--muted)]">{evidenceRule}</p>
          <div className="grid gap-px overflow-hidden rounded-[var(--radius)] border border-[var(--line)] bg-[var(--line)]">
            {architecture.map((a) => (
              <div key={a.layer} className="grid gap-1 bg-[var(--surface)] px-4 py-3 md:grid-cols-[150px_minmax(0,1fr)_170px] md:gap-4">
                <div className="text-sm font-semibold">{a.layer}</div>
                <div className="min-w-0 text-sm leading-6">
                  {a.tech}
                  <div className="text-[var(--muted)]">{a.role}</div>
                </div>
                <div className="text-xs text-[var(--muted)] md:text-right">{a.host}</div>
              </div>
            ))}
          </div>
          <p className="pt-3 text-xs leading-5 text-[var(--muted)]">
            Financial figures are always computed in Python. The Streamlit app stays deployed from main throughout and is the
            rollback path until cutover.
          </p>
        </Section>

        <Section id="costs" kicker="3 · Cost estimate" title="What it costs to run">
          <div className="grid gap-4 md:grid-cols-2">
            {[
              { title: "Per research run", rows: costs.perRun, low: runLow, high: runHigh, money: (v: number) => `$${v.toFixed(2)}` },
              { title: "Fixed, per month", rows: costs.monthly, low: monthLow, high: monthHigh, money: (v: number) => `$${v.toFixed(0)}` },
            ].map((block) => (
              <div key={block.title} className="rounded-[var(--radius)] border border-[var(--line)] bg-[var(--surface)] p-4">
                <div className="flex items-baseline justify-between gap-2 border-b border-[var(--line)] pb-3">
                  <h3 className="text-sm font-semibold">{block.title}</h3>
                  <span className="tnum text-lg font-semibold">
                    {block.money(block.low)}–{block.money(block.high)}
                  </span>
                </div>
                <ul className="flex flex-col gap-2.5 pt-3">
                  {block.rows.map((r) => (
                    <li key={r.item} className="grid grid-cols-[minmax(0,1fr)_auto] gap-x-3 text-sm">
                      <span className="font-medium">{r.item}</span>
                      <span className="tnum text-right">
                        {block.money(r.low)}–{block.money(r.high)}
                      </span>
                      <span className="col-span-2 text-xs leading-5 text-[var(--muted)]">{r.basis}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <p className="pt-3 text-xs leading-5 text-[var(--muted)]">
            {costs.note} At 300 runs a month that is roughly ${Math.round(runLow * 300 + monthLow)}–${Math.round(runHigh * 300 + monthHigh)} in
            total. Build effort is about {weeks} engineer-weeks across the milestones below.
          </p>
        </Section>

        <Section id="milestones" kicker="4 · Implementation" title="Milestones after approval">
          <ol className="flex flex-col">
            {milestones.map((m) => (
              <li key={m.id} className="grid gap-1 border-b border-[var(--line)] py-3 last:border-0 md:grid-cols-[56px_minmax(0,1fr)_minmax(0,1fr)_64px] md:gap-4">
                <span className="text-xs font-semibold text-[var(--muted)] [font-family:var(--font-plex-mono)]">{m.id}</span>
                <div className="min-w-0 text-sm leading-6">
                  <div className="font-semibold">{m.title}</div>
                  <div className="text-[var(--muted)]">{m.scope}</div>
                </div>
                <div className="min-w-0 text-sm leading-6 text-[var(--muted)]">
                  <span className="text-[11px] font-semibold tracking-[0.08em] uppercase">Done when </span>
                  {m.done}
                </div>
                <span className="tnum text-sm md:text-right">{m.weeks} wk</span>
              </li>
            ))}
          </ol>
          <p className="pt-3 text-xs leading-5 text-[var(--muted)]">
            Each milestone lands as its own pull request with tests and a changelog entry. Nothing merges to main until you approve
            it.
          </p>
        </Section>

        <Section id="decision" kicker="5 · Decision needed" title="Approve one direction">
          <p className="max-w-[65ch] text-sm leading-6 text-[var(--muted)]">
            Reply with A, B or C, plus anything to carry over from the others. Work stops here until then.
          </p>
        </Section>
      </div>
    </main>
  );
}
