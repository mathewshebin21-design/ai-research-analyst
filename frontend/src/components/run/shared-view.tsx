"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { motion } from "motion/react";

import { ErrorNote, Eyebrow } from "@/components/app/status";
import { API_URL } from "@/lib/api";
import { date } from "@/lib/format";
import type { RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Dashboard } from "./dashboard";
import { EvidenceTab } from "./evidence-tab";
import { ResearchTab } from "./research-tab";

const tabs = [
  { id: "dashboard", label: "Executive dashboard" },
  { id: "research", label: "Research" },
  { id: "evidence", label: "Evidence" },
] as const;

/** The read-only report behind a share link. No sign-in; nothing on this page can change the run. */
export function SharedView() {
  const token = useSearchParams().get("t") ?? "";
  const [run, setRun] = useState<RunDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<(typeof tabs)[number]["id"]>("dashboard");

  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/shared/${encodeURIComponent(token)}`)
      .then(async (r) => {
        if (r.ok) return setRun(await r.json());
        setError(r.status === 429 ? "Too many requests. Wait a minute and reload." : "This link is not valid or has been turned off.");
      })
      .catch(() => setError("The report could not be loaded. Check your connection and try again."));
  }, [token]);

  if (!token) return <ErrorNote>This link is incomplete. Ask the sender for the full link.</ErrorNote>;
  if (error) return <ErrorNote>{error}</ErrorNote>;
  if (!run) return <p className="text-sm text-[var(--muted)]">Loading…</p>;

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Eyebrow>
            Shared read-only report · {run.workspace_name}
            {run.finished_at ? ` · completed ${date(run.finished_at)}` : ""}
          </Eyebrow>
          <Link href="/" className="text-[12.5px] text-[var(--muted)] hover:text-[var(--fg)]">
            Strategic Intelligence Hub
          </Link>
        </div>
        <h1 className="font-disp max-w-[32ch] text-[clamp(26px,3.2vw,40px)] leading-[1.12]">{run.question}</h1>
      </header>
      <nav aria-label="Report views" className="flex gap-1 overflow-x-auto border-b border-[var(--line)]">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            aria-current={view === t.id ? "page" : undefined}
            onClick={() => setView(t.id)}
            className={cn(
              "-mb-px border-b-2 px-3 py-2 text-[13.5px] whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
              view === t.id ? "border-[var(--accent)] text-[var(--fg)]" : "border-transparent text-[var(--muted)] hover:text-[var(--fg)]",
            )}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <motion.div key={view} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        {view === "dashboard" && <Dashboard run={run} canEdit={false} onRunChange={setRun} shared />}
        {view === "research" && <ResearchTab run={run} />}
        {view === "evidence" && <EvidenceTab run={run} canEdit={false} onRunChange={setRun} />}
      </motion.div>
      <p className="text-[12px] leading-5 text-[var(--muted)]">
        <Link href="/legal/ai-notice" className="underline underline-offset-2">
          How this report was made
        </Link>{" "}
        ·{" "}
        <Link href="/legal/privacy" className="underline underline-offset-2">
          Privacy
        </Link>
      </p>
    </div>
  );
}
