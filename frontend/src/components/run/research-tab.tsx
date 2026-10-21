"use client";

import { useMemo, useState } from "react";
import { ExternalLink } from "lucide-react";

import { porterOption } from "@/components/app/charts";
import { EChart } from "@/components/app/echart";
import { Eyebrow, Panel, StatusBadge } from "@/components/app/status";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

const taskStatus = { done: "Complete", running: "In progress", queued: "Queued", failed: "Failed" } as const;

export function ResearchTab({ run }: { run: RunDetail }) {
  const [taskId, setTaskId] = useState(run.tasks[0]?.id);
  const task = run.tasks.find((t) => t.id === taskId) ?? run.tasks[0];
  const claims = run.claims.filter((c) => c.task === task?.key);
  const porter = useMemo(() => porterOption(run), [run]);
  const sourceById = useMemo(() => Object.fromEntries(run.sources.map((s) => [s.id, s])), [run.sources]);

  return (
    <div className="flex flex-col gap-12">
      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <Panel title="Research plan" aside={<span className="text-[12px] text-[var(--muted)]">{run.usage.searches ?? 0} searches · {run.sources.length} sources</span>}>
          <ol className="flex flex-col">
            {run.tasks.map((t) => (
              <li key={t.id}>
                <button
                  type="button"
                  onClick={() => setTaskId(t.id)}
                  aria-pressed={t.id === task?.id}
                  className={cn(
                    "grid w-full grid-cols-[36px_minmax(0,1fr)_auto] items-baseline gap-2 border-b border-[var(--line)] py-3 text-left focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                    t.id === task?.id ? "text-[var(--fg)]" : "text-[var(--muted)] hover:text-[var(--fg)]",
                  )}
                >
                  <span className={cn("tnum text-[12px]", t.id === task?.id && "text-[var(--accent)]")}>{t.key}</span>
                  <span className="text-[14px]">
                    {t.title}
                    <span className="block text-[11.5px] text-[var(--muted)]">
                      {t.category} · {t.supported}/{t.claims} claims supported
                    </span>
                  </span>
                  <span className={cn("text-[11px]", t.status === "done" && "text-[var(--ok)]", t.status === "failed" && "text-[var(--bad)]")}>{taskStatus[t.status]}</span>
                </button>
              </li>
            ))}
          </ol>
        </Panel>

        {task && (
          <Panel title={`${task.key} · ${task.title}`}>
            {task.note && <p className="mb-4 border-l-2 border-[var(--warn)] pl-3 text-[13.5px] leading-6 text-[var(--warn)]">{task.note}</p>}
            <Eyebrow className="mb-2">Searches run</Eyebrow>
            <ul className="mb-6 flex flex-col gap-1.5 text-[13px]">
              {task.searches.map((s, i) => (
                <li key={i} className="flex flex-wrap justify-between gap-2">
                  <span className="text-[var(--muted)]">“{s.query}”</span>
                  <span className={s.status === "failed" ? "text-[var(--bad)]" : "text-[var(--muted)]"}>
                    {s.status === "failed" ? `Failed: ${s.error}` : `${s.results} results${s.status === "cached" ? " (cached)" : ""}`}
                  </span>
                </li>
              ))}
            </ul>
            <Eyebrow className="mb-2">Claims extracted</Eyebrow>
            {claims.length ? (
              <ul className="flex flex-col">
                {claims.map((c) => (
                  <li key={c.id} className="flex flex-col gap-1.5 border-b border-[var(--line)] py-3 last:border-0">
                    <div className="flex items-center gap-2">
                      <span className="tnum text-[12px] text-[var(--muted)]">{c.key}</span>
                      <StatusBadge status={c.status} />
                    </div>
                    <p className="font-disp text-[17px] leading-snug">{c.text}</p>
                    <p className="text-[12.5px] text-[var(--muted)]">
                      {[...new Set(c.evidence.filter((e) => e.relation !== "related").map((e) => sourceById[e.source_id]?.publisher))].join("; ") || "No supporting or contradicting source"}
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-[13.5px] text-[var(--muted)]">This task produced no claims.</p>
            )}
          </Panel>
        )}
      </div>

      <Panel title="Sources" aside={<span className="text-[12px] text-[var(--muted)]">Tier A: official or academic · B: industry and other · C: blogs and user content</span>}>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-[13px]">
            <thead>
              <tr className="text-[11px] tracking-[0.1em] text-[var(--muted)] uppercase">
                <th className="py-2 pr-3 font-semibold">Key</th>
                <th className="py-2 pr-3 font-semibold">Source</th>
                <th className="py-2 pr-3 font-semibold">Tier</th>
                <th className="py-2 font-semibold">Retrieved</th>
              </tr>
            </thead>
            <tbody>
              {run.sources.map((s) => (
                <tr key={s.id} className="border-t border-[var(--line)] align-top">
                  <td className="tnum py-2.5 pr-3 text-[var(--muted)]">{s.key}</td>
                  <td className="py-2.5 pr-3">
                    {s.url ? (
                      <a href={s.url} target="_blank" rel="noreferrer noopener" className="inline-flex items-start gap-1.5 hover:text-[var(--accent)]">
                        {s.title} <ExternalLink className="mt-1 size-3 shrink-0" />
                      </a>
                    ) : (
                      s.title
                    )}
                    <span className="block text-[12px] text-[var(--muted)]">
                      {s.publisher}
                      {s.published ? ` · published ${s.published.slice(0, 10)}` : ""}
                    </span>
                  </td>
                  <td className={cn("py-2.5 pr-3", s.tier === "A" ? "text-[var(--ok)]" : s.tier === "C" ? "text-[var(--warn)]" : "")}>{s.tier}</td>
                  <td className="py-2.5 text-[var(--muted)]">{s.retrieved_at.slice(0, 10)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel title="Strategic frameworks" aside={<span className="text-[12px] text-[var(--muted)]">Every entry cites the claims it rests on</span>}>
        <Tabs defaultValue="swot">
          <TabsList className="border-b border-[var(--line)]">
            {[
              ["swot", "SWOT"],
              ["pestle", "PESTLE"],
              ["porter", "Five Forces"],
            ].map(([v, l]) => (
              <TabsTrigger key={v} value={v} className="-mb-px border-b-2 border-transparent data-[state=active]:border-[var(--accent)]">
                {l}
              </TabsTrigger>
            ))}
          </TabsList>
          <TabsContent value="swot">
            {run.swot ? (
              <div className="grid gap-px bg-[var(--line)] md:grid-cols-2">
                {(["strengths", "weaknesses", "opportunities", "threats"] as const).map((k) => (
                  <div key={k} className="bg-[var(--bg)] p-5">
                    <Eyebrow className="mb-2">{k}</Eyebrow>
                    <ul className="flex flex-col gap-1.5 text-[13.5px] leading-6">
                      {run.swot![k].map((i) => (
                        <li key={i.text} className={i.basis === "evidenced" ? "" : "text-[var(--muted)]"}>
                          {i.text} <span className="text-[11.5px] text-[var(--muted)]">{i.claims.length ? `(${i.claims.join(", ")})` : "(no evidence)"}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-[13.5px] text-[var(--muted)]">Not available.</p>
            )}
          </TabsContent>
          <TabsContent value="pestle">
            <ul className="grid gap-x-8 md:grid-cols-2">
              {run.pestle.map((p) => (
                <li key={p.factor} className="grid grid-cols-[110px_64px_minmax(0,1fr)] gap-3 border-b border-[var(--line)] py-3 text-[13.5px]">
                  <span>{p.factor}</span>
                  <span className="tnum text-[var(--accent)]" aria-label={`Impact ${p.rating} of 5`}>
                    {"●".repeat(p.rating)}
                    <span className="text-[var(--line)]">{"●".repeat(5 - p.rating)}</span>
                  </span>
                  <span className="text-[var(--muted)]">
                    {p.note} {p.claims.length > 0 && <span className="text-[var(--fg)]">({p.claims.join(", ")})</span>}
                  </span>
                </li>
              ))}
            </ul>
          </TabsContent>
          <TabsContent value="porter">
            {run.porter.length > 0 && <EChart option={porter} label="Porter's five forces intensity, 1 to 5" className="h-[200px] w-full max-w-[640px]" />}
            <ul className="mt-4 flex flex-col gap-2 text-[13px] text-[var(--muted)]">
              {run.porter.map((f) => (
                <li key={f.force}>
                  <span className="text-[var(--fg)]">{f.force}:</span> {f.rationale} {f.claims.length > 0 && `(${f.claims.join(", ")})`}
                </li>
              ))}
            </ul>
          </TabsContent>
        </Tabs>
      </Panel>
    </div>
  );
}
