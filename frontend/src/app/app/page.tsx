"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FileUp, Trash2 } from "lucide-react";

import { useSession } from "@/components/app/session";
import { ErrorNote, Eyebrow, Field, Panel } from "@/components/app/status";
import { UsageMeter, useUsage } from "@/components/app/usage";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { currencies, date } from "@/lib/format";
import type { DocumentOut, RunDetail, RunSummary } from "@/lib/types";
import { cn } from "@/lib/utils";

const statusText: Record<string, string> = {
  planned: "Plan ready for review",
  queued: "Queued",
  running: "Researching",
  completed: "Complete",
  failed: "Failed",
  draft: "Draft",
};

export default function ResearchHome() {
  const { workspace } = useSession();
  const router = useRouter();
  const canEdit = workspace.role !== "viewer";
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [form, setForm] = useState({ question: "", company: "", geography: "", notes: "", currency: "GBP" });
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const usage = useUsage(workspace.id);

  const seq = useRef(0);
  const load = useCallback(async () => {
    const mine = ++seq.current;
    const [r, d] = await Promise.all([
      api<RunSummary[]>(`/workspaces/${workspace.id}/runs`),
      api<DocumentOut[]>(`/workspaces/${workspace.id}/documents`),
    ]);
    if (mine !== seq.current) return; // a newer load (e.g. after an upload) already applied
    setRuns(r);
    setDocs(d);
  }, [workspace.id]);

  useEffect(() => {
     
    load().catch((e) => setError(e.message));
  }, [load]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const run = await api<RunDetail>(`/workspaces/${workspace.id}/runs`, {
        method: "POST",
        json: { ...form, company: form.company || null, geography: form.geography || null, notes: form.notes || null, document_ids: selected },
      });
      router.push(`/app/run?id=${run.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create the plan.");
      setBusy(false);
    }
  }

  async function upload(file: File) {
    setUploading(true);
    setError(null);
    const body = new FormData();
    body.append("file", file);
    try {
      const doc = await api<DocumentOut>(`/workspaces/${workspace.id}/documents`, { method: "POST", body });
      setSelected((s) => [...s, doc.id]);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  async function removeDoc(id: string) {
    try {
      await api(`/documents/${id}`, { method: "DELETE" });
      setDocs((d) => d.filter((x) => x.id !== id));
      setSelected((s) => s.filter((x) => x !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete the document.");
    }
  }

  return (
    <div className="flex flex-col gap-12">
      <header className="flex flex-col gap-2">
        <Eyebrow>{workspace.name}</Eyebrow>
        <h1 className="font-disp text-[clamp(28px,3.4vw,40px)] leading-tight">What decision are you making?</h1>
      </header>

      {canEdit ? (
        <form onSubmit={submit} className="grid gap-8 border border-[var(--line)] bg-[var(--surface)] p-6 md:p-8 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          <div className="flex flex-col gap-4">
            <Field label="Market-entry question" htmlFor="question" hint="Be specific about the product, market, channel and timing.">
              <textarea
                id="question"
                required
                minLength={15}
                rows={3}
                value={form.question}
                onChange={(e) => setForm({ ...form, question: e.target.value })}
                placeholder="Should we launch our premium sustainable footwear line direct-to-consumer in Germany in 2027?"
                className="font-disp px-3 py-2 text-[18px] leading-snug"
              />
            </Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Your company (optional)" htmlFor="company">
                <input id="company" value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} className="px-3 py-2" />
              </Field>
              <Field label="Geography (optional)" htmlFor="geography">
                <input id="geography" value={form.geography} onChange={(e) => setForm({ ...form, geography: e.target.value })} className="px-3 py-2" />
              </Field>
            </div>
            <Field label="Currency for financial figures" htmlFor="currency" hint="Amounts are estimated and shown in this currency; they are not converted later.">
              <select id="currency" value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} className="px-3 py-2 sm:max-w-[260px]">
                {currencies.map((c) => (
                  <option key={c.code} value={c.code}>
                    {c.label}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Context the researchers should know (optional)" htmlFor="notes">
              <textarea id="notes" rows={2} value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="px-3 py-2" />
            </Field>
            {error && <ErrorNote>{error}</ErrorNote>}
            <div className="flex flex-wrap items-center gap-4">
              <Button type="submit" disabled={busy}>
                {busy ? "Drafting a research plan…" : "Draft research plan"}
              </Button>
              <span className="text-[12px] text-[var(--muted)]">Nothing is searched until you approve the plan.</span>
            </div>
            <UsageMeter usage={usage} className="max-w-[360px]" />
          </div>

          <div className="flex min-w-0 flex-col gap-3">
            <Eyebrow>Your documents</Eyebrow>
            <p className="text-[12.5px] leading-5 text-[var(--muted)]">
              Add PDFs such as internal memos or market reports. Selected documents are searched alongside the web and cited by page.
            </p>
            <input ref={fileRef} type="file" accept="application/pdf" className="sr-only" id="upload" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
            <Button type="button" variant="outline" size="sm" disabled={uploading} onClick={() => fileRef.current?.click()} className="self-start">
              <FileUp /> {uploading ? "Checking and indexing…" : "Upload PDF"}
            </Button>
            <ul className="flex flex-col">
              {docs.map((d) => (
                <li key={d.id} className="flex items-center gap-3 border-b border-[var(--line)] py-2 text-[13px]">
                  <input
                    type="checkbox"
                    aria-label={`Use ${d.filename} in this question`}
                    checked={selected.includes(d.id)}
                    onChange={(e) => setSelected((s) => (e.target.checked ? [...s, d.id] : s.filter((x) => x !== d.id)))}
                    className="size-4 accent-[var(--accent)]"
                  />
                  <span className="min-w-0 flex-1 truncate">{d.filename}</span>
                  <span className="text-[11.5px] text-[var(--muted)]">{d.pages} pp</span>
                  <button type="button" aria-label={`Delete ${d.filename}`} onClick={() => removeDoc(d.id)} className="text-[var(--muted)] hover:text-[var(--bad)]">
                    <Trash2 className="size-3.5" />
                  </button>
                </li>
              ))}
              {docs.length === 0 && <li className="text-[12.5px] text-[var(--muted)]">No documents yet.</li>}
            </ul>
          </div>
        </form>
      ) : (
        <p className="text-[14px] text-[var(--muted)]">You have view-only access to this workspace.</p>
      )}

      <Panel
        title="Research history"
        aside={
          <span className="flex gap-4 text-[12.5px]">
            <Link href="/sample" className="text-[var(--muted)] hover:text-[var(--fg)]">
              Sample report
            </Link>
            <Link href="/app/compare" className="text-[var(--accent)]">
              Compare two runs
            </Link>
          </span>
        }
      >
        {runs === null ? (
          <p className="text-[13px] text-[var(--muted)]">Loading…</p>
        ) : runs.length === 0 ? (
          <p className="text-[13.5px] text-[var(--muted)]">
            Your questions and their results will appear here. To see what a finished report looks like first,{" "}
            <Link href="/sample" className="text-[var(--accent)] underline underline-offset-2">
              open the sample report
            </Link>
            .
          </p>
        ) : (
          <ul className="flex flex-col">
            {runs.map((r) => (
              <li key={r.id}>
                <Link href={`/app/run?id=${r.id}`} className="grid gap-1 border-b border-[var(--line)] py-3 transition-colors hover:bg-[var(--surface)] sm:grid-cols-[minmax(0,1fr)_160px_120px] sm:gap-4 sm:px-2">
                  <span className="text-[14px]">{r.question}</span>
                  <span className={cn("text-[12.5px]", r.status === "failed" ? "text-[var(--bad)]" : r.verdict ? "text-[var(--accent)]" : "text-[var(--muted)]")}>
                    {r.verdict ?? statusText[r.status]}
                  </span>
                  <span className="text-[12px] text-[var(--muted)] sm:text-right">{date(r.created_at)}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}
