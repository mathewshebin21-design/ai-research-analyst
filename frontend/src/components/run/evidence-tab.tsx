"use client";

import { useMemo, useState } from "react";

import { Extract } from "@/components/app/highlight";
import { Eyebrow, StatusBadge } from "@/components/app/status";
import { statusLabel } from "@/lib/format";
import type { ClaimStatus, RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

const filters = ["all", "supported", "partial", "contradicted", "unsupported", "missing"] as const;

export function EvidenceTab({ run }: { run: RunDetail }) {
  const [filter, setFilter] = useState<(typeof filters)[number]>("all");
  const firstProblem = run.claims.find((c) => c.status !== "supported") ?? run.claims[0];
  const [claimId, setClaimId] = useState(firstProblem?.id);
  const counts = run.claims.reduce<Record<string, number>>((m, c) => ({ ...m, [c.status]: (m[c.status] ?? 0) + 1 }), {});
  const list = run.claims.filter((c) => filter === "all" || c.status === filter);
  // The detail always shows a claim from the filtered list.
  const claim = list.find((c) => c.id === claimId) ?? list[0];
  const sources = useMemo(() => Object.fromEntries(run.sources.map((s) => [s.id, s])), [run.sources]);

  if (run.claims.length === 0) return <p className="text-[13.5px] text-[var(--muted)]">This run produced no claims.</p>;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap gap-2" role="group" aria-label="Filter claims by status">
        {filters.map((s) => (
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
            {s === "all" ? `All claims ${run.claims.length}` : `${statusLabel[s as ClaimStatus]} ${counts[s] ?? 0}`}
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
                aria-pressed={c.id === claim.id}
                className={cn(
                  "flex w-full flex-col gap-1.5 border-b border-l-2 border-[var(--line)] py-3 pr-2 pl-4 text-left focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                  c.id === claim.id ? "border-l-[var(--accent)] bg-[var(--surface)]" : "border-l-transparent hover:bg-[var(--surface)]",
                )}
              >
                <span className="flex items-center gap-2">
                  <span className="tnum text-[12px] text-[var(--muted)]">{c.key}</span>
                  <StatusBadge status={c.status} />
                </span>
                <span className="text-[13.5px] leading-6">{c.text}</span>
              </button>
            </li>
          ))}
        </ul>

        {!claim ? (
          <p className="text-[13.5px] text-[var(--muted)]">No claims have this status.</p>
        ) : (
        <article className="min-w-0 border border-[var(--line)] bg-[var(--surface)] p-6 md:p-8">
          <div className="flex flex-wrap items-center gap-3">
            <Eyebrow>
              Claim {claim.key}
              {claim.task ? ` · Task ${claim.task}` : ""} · {claim.kind}
            </Eyebrow>
            <StatusBadge status={claim.status} />
          </div>
          <h2 className="font-disp mt-3 text-[clamp(22px,2.4vw,28px)] leading-snug">{claim.text}</h2>
          <div className="mt-5 border-l-2 border-[var(--accent)] pl-4">
            <Eyebrow className="mb-1">Why this status</Eyebrow>
            <p className="max-w-[62ch] text-[14px] leading-7">{claim.status_reason}</p>
          </div>

          <Eyebrow className="mt-8 mb-3">Source extracts</Eyebrow>
          {claim.evidence.length === 0 && <p className="text-[13.5px] text-[var(--muted)]">No retrieved passage addressed this claim.</p>}
          <ol className="flex flex-col gap-7">
            {claim.evidence.map((e, i) => {
              const s = sources[e.source_id];
              return (
                <li key={i} className="flex flex-col gap-3">
                  <blockquote className="font-disp text-[17px] leading-[1.6] italic">
                    “<Extract e={e} />”
                  </blockquote>
                  <p className="text-[12.5px] text-[var(--muted)]">
                    <sup className="mr-1 text-[var(--accent)]">{i + 1}</sup>
                    {s?.key} {s?.publisher}
                    {s?.title ? <>, <em>{s.title}</em></> : null}
                    {e.page ? `, page ${e.page}` : ""} · tier {s?.tier}
                    {s?.url && (
                      <>
                        {" · "}
                        <a href={s.url} target="_blank" rel="noreferrer noopener" className="text-[var(--accent)] underline underline-offset-2">
                          open source
                        </a>
                      </>
                    )}
                  </p>
                  {e.scope_issue && <p className="text-[12.5px] text-[var(--warn)]">Scope mismatch: {e.scope_issue}</p>}
                  {e.note && <p className="text-[12.5px] text-[var(--muted)]">Verifier: {e.note}</p>}
                  <div className="grid max-w-md grid-cols-[120px_minmax(0,1fr)_36px] items-center gap-x-3 gap-y-1.5 text-[12px]">
                    <span className="text-[var(--muted)]">Topic relevance</span>
                    <div className="h-1 bg-[var(--line)]">
                      <div className="h-1 bg-[var(--muted)]" style={{ width: `${e.relevance * 100}%` }} />
                    </div>
                    <span className="tnum text-right">{e.relevance.toFixed(2)}</span>
                    <span className="text-[var(--muted)]">{e.relation === "contradicts" ? "Contradicts claim" : "Supports claim"}</span>
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
            A source can be highly relevant to the topic and still not support the claim. Only the second score, backed by an exact quote, decides the
            status. Checked by {claim.evidence[0]?.model ?? "the verifier"} with rules version {String(run.settings.status_rules ?? "v1")}.
          </p>
        </article>
        )}
      </div>
    </div>
  );
}
