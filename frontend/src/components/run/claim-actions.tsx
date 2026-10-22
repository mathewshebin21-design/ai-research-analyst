"use client";

import { useEffect, useRef, useState } from "react";
import { FileUp, Flag, Link2, Type } from "lucide-react";

import { ErrorNote, Eyebrow } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { statusLabel } from "@/lib/format";
import type { ClaimOut, ClaimStatus, DocumentOut, RunDetail } from "@/lib/types";
import { cn } from "@/lib/utils";

type Mode = "url" | "text" | "document";
const modes: { id: Mode; label: string; icon: typeof Link2 }[] = [
  { id: "url", label: "Link", icon: Link2 },
  { id: "text", label: "Paste text", icon: Type },
  { id: "document", label: "Your PDF", icon: FileUp },
];

export function ClaimActions({ run, claim, onRunChange }: { run: RunDetail; claim: ClaimOut; onRunChange: (r: RunDetail) => void }) {
  const [mode, setMode] = useState<Mode>("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [title, setTitle] = useState("");
  const [docId, setDocId] = useState("");
  const [docs, setDocs] = useState<DocumentOut[]>([]);
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api<DocumentOut[]>(`/workspaces/${run.workspace_id}/documents`).then(setDocs).catch(() => setDocs([]));
  }, [run.workspace_id]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setOutcome(null);
    const json = mode === "url" ? { url } : mode === "text" ? { text, title: title || null } : { document_id: docId };
    try {
      const r = await api<{ result: { source_key: string; previous_status: ClaimStatus; status: ClaimStatus }; run: RunDetail }>(
        `/runs/${run.id}/claims/${claim.id}/evidence`,
        { method: "POST", json },
      );
      onRunChange(r.run);
      const { previous_status: a, status: b, source_key } = r.result;
      setOutcome(
        a === b
          ? `Checked ${source_key}. It did not change the status: still ${statusLabel[b].toLowerCase()}.`
          : `Checked ${source_key}. ${claim.key} moved from ${statusLabel[a].toLowerCase()} to ${statusLabel[b].toLowerCase()}.`,
      );
      setUrl("");
      setText("");
      setTitle("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function upload(file: File) {
    const body = new FormData();
    body.append("file", file);
    try {
      const doc = await api<DocumentOut>(`/workspaces/${run.workspace_id}/documents`, { method: "POST", body });
      setDocs((d) => [doc, ...d]);
      setDocId(doc.id);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function toggleDispute() {
    setBusy(true);
    try {
      const r = claim.user_flag
        ? await api<RunDetail>(`/runs/${run.id}/claims/${claim.id}/dispute`, { method: "DELETE" })
        : await api<RunDetail>(`/runs/${run.id}/claims/${claim.id}/dispute`, { method: "POST", json: { note } });
      onRunChange(r);
      setNote("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const ready = mode === "url" ? /^https?:\/\//.test(url) : mode === "text" ? text.trim().length >= 40 : Boolean(docId);

  return (
    <div className="mt-8 flex flex-col gap-6 border-t border-[var(--line)] pt-6">
      <form onSubmit={submit} className="flex flex-col gap-3">
        <Eyebrow>Add your own evidence</Eyebrow>
        <p className="text-[12.5px] leading-5 text-[var(--muted)]">
          It is checked the same way as searched sources, with an exact quote. On its own it can make a claim partially supported; a second
          independent source is needed for supported.
        </p>
        <div className="flex gap-1" role="tablist" aria-label="Evidence type">
          {modes.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={mode === id}
              onClick={() => setMode(id)}
              className={cn(
                "inline-flex items-center gap-1.5 border px-3 py-1.5 text-[12.5px] focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                mode === id ? "border-[var(--accent)] text-[var(--fg)]" : "border-[var(--line)] text-[var(--muted)] hover:text-[var(--fg)]",
              )}
            >
              <Icon className="size-3.5" /> {label}
            </button>
          ))}
        </div>
        {mode === "url" && (
          <input aria-label="Source link" type="url" placeholder="https://…" value={url} onChange={(e) => setUrl(e.target.value)} className="px-3 py-2 text-[13.5px]" />
        )}
        {mode === "text" && (
          <>
            <input aria-label="Where the text comes from" placeholder="Where it comes from, e.g. 2026 customer survey" value={title} onChange={(e) => setTitle(e.target.value)} className="px-3 py-2 text-[13.5px]" />
            <textarea aria-label="Source text" rows={4} placeholder="Paste the passage that supports or contradicts the claim" value={text} onChange={(e) => setText(e.target.value)} className="px-3 py-2 text-[13.5px]" />
          </>
        )}
        {mode === "document" && (
          <div className="flex flex-wrap items-center gap-2">
            <select aria-label="Document" value={docId} onChange={(e) => setDocId(e.target.value)} className="min-w-0 flex-1 px-2 py-2 text-[13.5px]">
              <option value="">Choose a document</option>
              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename} ({d.pages} pp)
                </option>
              ))}
            </select>
            <input ref={fileRef} type="file" accept="application/pdf" className="sr-only" aria-label="Upload a PDF" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
            <Button type="button" size="sm" variant="outline" onClick={() => fileRef.current?.click()}>
              <FileUp /> Upload PDF
            </Button>
          </div>
        )}
        <Button type="submit" size="sm" disabled={!ready || busy} className="self-start">
          {busy ? "Checking against the claim…" : "Check this evidence"}
        </Button>
        {outcome && <p role="status" className="text-[13px] text-[var(--ok)]">{outcome}</p>}
        {error && <ErrorNote>{error}</ErrorNote>}
      </form>

      <div className="flex flex-col gap-2">
        <Eyebrow>{claim.user_flag ? "Disputed" : "Think this claim is wrong?"}</Eyebrow>
        {claim.user_flag ? (
          <p className="text-[13px] text-[var(--warn)]">
            Disputed{claim.user_note ? `: ${claim.user_note}` : ""}. It counts as no evidence in the decision until the dispute is cleared.
          </p>
        ) : (
          <input aria-label="Reason for dispute" placeholder="Why, e.g. the source is out of date" value={note} onChange={(e) => setNote(e.target.value)} className="px-3 py-2 text-[13px]" />
        )}
        <Button type="button" size="sm" variant="outline" onClick={toggleDispute} disabled={busy} className="self-start">
          <Flag /> {claim.user_flag ? "Clear dispute" : "Dispute this claim"}
        </Button>
      </div>
    </div>
  );
}
