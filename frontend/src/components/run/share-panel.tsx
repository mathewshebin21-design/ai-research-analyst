"use client";

import { useEffect, useState } from "react";
import { Check, Copy, Link2, Presentation, X } from "lucide-react";

import { ErrorNote, Panel } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api, saveBlob } from "@/lib/api";
import { date } from "@/lib/format";
import type { RunDetail } from "@/lib/types";

type Share = { id: string; created_at: string };

export function SharePanel({ run, canEdit }: { run: RunDetail; canEdit: boolean }) {
  const [links, setLinks] = useState<Share[]>([]);
  const [fresh, setFresh] = useState<{ id: string; url: string } | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState<"share" | "slides" | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Share[]>(`/runs/${run.id}/shares`).then(setLinks).catch(() => setLinks([]));
  }, [run.id]);

  async function create() {
    setBusy("share");
    try {
      const s = await api<Share & { token: string }>(`/runs/${run.id}/shares`, { method: "POST" });
      setLinks((l) => [...l, { id: s.id, created_at: s.created_at }]);
      setFresh({ id: s.id, url: `${window.location.origin}/shared?t=${s.token}` });
      setCopied(false);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  async function revoke(id: string) {
    try {
      await api(`/runs/${run.id}/shares/${id}`, { method: "DELETE" });
      setLinks((l) => l.filter((s) => s.id !== id));
      if (fresh?.id === id) setFresh(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function copy() {
    if (!fresh) return;
    try {
      await navigator.clipboard.writeText(fresh.url);
      setCopied(true);
    } catch {
      setError("Copying was blocked by the browser. Select the link and copy it by hand.");
    }
  }

  async function slides() {
    setBusy("slides");
    try {
      saveBlob(await api<Blob>(`/runs/${run.id}/slides`, { method: "POST", asFile: true }), `market-entry-${run.id.slice(0, 8)}.pptx`);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <Panel
      title="Share and present"
      aside={
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant="outline" onClick={slides} disabled={busy !== null}>
            <Presentation /> {busy === "slides" ? "Preparing slides…" : "Export slides"}
          </Button>
          {canEdit && (
            <Button size="sm" onClick={create} disabled={busy !== null}>
              <Link2 /> {busy === "share" ? "Creating…" : "Create read-only link"}
            </Button>
          )}
        </div>
      }
    >
      {error && <div className="mb-4"><ErrorNote>{error}</ErrorNote></div>}
      <p className="max-w-[72ch] text-[13.5px] leading-6 text-[var(--muted)]">
        A read-only link lets someone without an account see this report: the recommendation, scenarios, research and every cited extract,
        including extracts from documents you uploaded. They cannot change anything. Anyone holding the link can open it, so turn it off when
        it is no longer needed.
      </p>
      {fresh && (
        <div className="mt-4 flex flex-col gap-2 border border-[var(--accent)] bg-[var(--surface)] p-4">
          <label htmlFor="share-url" className="text-[12px] text-[var(--muted)]">
            New link. Copy it now: for security it is shown only once.
          </label>
          <div className="flex flex-wrap gap-2">
            <input id="share-url" readOnly value={fresh.url} onFocus={(e) => e.target.select()} className="tnum min-w-0 flex-1 px-2 py-1.5 text-[12.5px]" />
            <Button size="sm" variant="outline" onClick={copy}>
              {copied ? <Check /> : <Copy />} {copied ? "Copied" : "Copy link"}
            </Button>
          </div>
        </div>
      )}
      {links.length > 0 && (
        <ul className="mt-4 flex flex-col" aria-label="Active links">
          {links.map((s, i) => (
            <li key={s.id} className="flex items-center justify-between gap-3 border-b border-[var(--line)] py-2 text-[13px] last:border-0">
              <span>
                Link {i + 1} · created {date(s.created_at)}
              </span>
              {canEdit && (
                <Button size="sm" variant="ghost" onClick={() => revoke(s.id)} aria-label={`Turn off link ${i + 1}`}>
                  <X /> Turn off
                </Button>
              )}
            </li>
          ))}
        </ul>
      )}
      {links.length === 0 && !fresh && <p className="mt-3 text-[12.5px] text-[var(--muted)]">No active links.</p>}
    </Panel>
  );
}
