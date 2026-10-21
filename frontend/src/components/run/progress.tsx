import { Eyebrow, Panel } from "@/components/app/status";
import type { RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

const STAGES = [
  ["research", "Searching sources"],
  ["extract", "Extracting claims"],
  ["verify", "Checking claims against quotes"],
  ["critique", "Reviewing for gaps and contradictions"],
  ["analyse", "Building analysis and recommendation"],
] as const;

export function Progress({ run, events }: { run: RunDetail; events: { agent: string; message: string; at: string }[] }) {
  const current = STAGES.findIndex(([s]) => s === run.stage);
  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
      <Panel title={run.status === "queued" ? "Waiting to start" : "Research in progress"}>
        <ol className="flex flex-col gap-3" aria-live="polite">
          {STAGES.map(([id, label], i) => (
            <li key={id} className={cn("flex items-center gap-3 text-[14px]", i < current ? "text-[var(--ok)]" : i === current ? "text-[var(--fg)]" : "text-[var(--muted)]")}>
              <span className={cn("size-2 rounded-full", i < current ? "bg-[var(--ok)]" : i === current ? "animate-pulse bg-[var(--accent)]" : "bg-[var(--line)]")} />
              {label}
            </li>
          ))}
        </ol>
        <Eyebrow className="mt-6 mb-2">Tasks</Eyebrow>
        <ul className="flex flex-col gap-1.5 text-[13px]">
          {run.tasks.map((t) => (
            <li key={t.id} className="flex justify-between gap-3">
              <span className="text-[var(--muted)]">
                {t.key} {t.title}
              </span>
              <span className={t.status === "failed" ? "text-[var(--bad)]" : t.status === "done" ? "text-[var(--ok)]" : "text-[var(--muted)]"}>{t.status}</span>
            </li>
          ))}
        </ul>
      </Panel>
      <Panel title="Activity">
        <ul className="flex max-h-[420px] flex-col gap-2 overflow-y-auto text-[12.5px]">
          {[...events].reverse().map((e, i) => (
            <li key={i} className="grid grid-cols-[52px_82px_minmax(0,1fr)] gap-2 text-[var(--muted)]">
              <span className="tnum">{new Date(e.at).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}</span>
              <span className="text-[var(--fg)]">{e.agent}</span>
              <span>{e.message}</span>
            </li>
          ))}
        </ul>
      </Panel>
    </div>
  );
}
