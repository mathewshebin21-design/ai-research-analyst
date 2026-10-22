"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { useSession } from "@/components/app/session";
import { ErrorNote, Eyebrow, Panel } from "@/components/app/status";
import { api } from "@/lib/api";
import { date, money } from "@/lib/format";
import type { RunSummary } from "@/lib/types";

type Row = {
  id: string;
  question: string;
  finished_at: string | null;
  verdict: string | null;
  overall: number | null;
  confidence: number | null;
  claims: Record<string, number>;
  sources: number;
  factors: Record<string, number>;
  break_even_month: number | null;
  peak_funding: number | null;
  currency_symbol: string;
};

const factorLabels: Record<string, string> = { attract: "Market attractiveness", demand: "Customer demand", compete: "Competitive room", econ: "Unit economics", exec: "Execution and compliance" };

export function Compare() {
  const { workspace } = useSession();
  const params = useSearchParams();
  const router = useRouter();
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [rows, setRows] = useState<Row[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const a = params.get("a") ?? "";
  const b = params.get("b") ?? "";

  useEffect(() => {
    api<RunSummary[]>(`/workspaces/${workspace.id}/runs`).then((r) => setRuns(r.filter((x) => x.status === "completed"))).catch((e) => setError(e.message));
  }, [workspace.id]);

  useEffect(() => {
    if (!a || !b) return;
    api<{ runs: Row[] }>(`/compare?a=${a}&b=${b}`).then((r) => setRows(r.runs)).catch((e) => setError(e.message));
  }, [a, b]);

  const pick = (key: "a" | "b", id: string) => {
    const next = new URLSearchParams(params);
    next.set(key, id);
    router.replace(`/app/compare?${next}`);
  };

  const lines: [string, (r: Row) => string][] = [
    ["Verdict", (r) => r.verdict ?? "—"],
    ["Weighted score", (r) => (r.overall != null ? `${r.overall} / 100` : "—")],
    ["Confidence", (r) => (r.confidence != null ? `${Math.round(r.confidence * 100)} / 100` : "—")],
    ["Claims supported", (r) => `${r.claims.supported ?? 0} of ${Object.values(r.claims).reduce((s, n) => s + n, 0)}`],
    ["Claims contradicted or unsupported", (r) => String((r.claims.contradicted ?? 0) + (r.claims.unsupported ?? 0))],
    ["Sources", (r) => String(r.sources)],
    ...Object.entries(factorLabels).map(([k, l]) => [l, (r: Row) => String(r.factors[k] ?? "—")] as [string, (r: Row) => string]),
    ["Break-even month (base)", (r) => (r.break_even_month ? `Month ${r.break_even_month}` : "Not in 36 months")],
    ["Peak funding need (base)", (r) => (r.peak_funding != null ? money(-r.peak_funding, r.currency_symbol) : "—")],
  ];

  return (
    <div className="flex flex-col gap-8">
      <header>
        <Eyebrow>{workspace.name}</Eyebrow>
        <h1 className="font-disp mt-2 text-[clamp(26px,3vw,36px)]">Compare two runs</h1>
      </header>
      {error && <ErrorNote>{error}</ErrorNote>}
      <div className="grid gap-4 md:grid-cols-2">
        {(["a", "b"] as const).map((k) => (
          <label key={k} className="flex flex-col gap-1.5 text-[13px]">
            {k === "a" ? "First run" : "Second run"}
            <select value={k === "a" ? a : b} onChange={(e) => pick(k, e.target.value)} className="px-2 py-2">
              <option value="">Choose a completed run</option>
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.question.slice(0, 80)} ({date(r.created_at)})
                </option>
              ))}
            </select>
          </label>
        ))}
      </div>
      {runs.length < 2 && <p className="text-[13.5px] text-[var(--muted)]">You need two completed runs to compare.</p>}
      {rows && (
        <Panel title="Side by side">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-[13.5px]">
              <thead>
                <tr>
                  <th className="w-[30%] py-2" />
                  {rows.map((r) => (
                    <th key={r.id} className="font-disp py-2 pr-4 align-bottom text-[16px] font-normal">
                      {r.question}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {lines.map(([label, f]) => (
                  <tr key={label} className="border-t border-[var(--line)]">
                    <td className="py-2.5 pr-4 text-[var(--muted)]">{label}</td>
                    {rows.map((r) => (
                      <td key={r.id} className="tnum py-2.5 pr-4">
                        {f(r)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      )}
    </div>
  );
}
