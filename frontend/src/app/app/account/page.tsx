"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useSession } from "@/components/app/session";
import { ErrorNote, Eyebrow, Panel } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api, saveBlob } from "@/lib/api";
import { signOut } from "@/lib/auth";
import { date } from "@/lib/format";

export default function Account() {
  const { me } = useSession();
  const router = useRouter();
  const [confirm, setConfirm] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function exportData() {
    try {
      saveBlob(await api<Blob>("/me/export", { asFile: true }), "my-data.json");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function remove() {
    setBusy(true);
    try {
      await api("/me", { method: "DELETE" });
      await signOut();
      router.replace("/");
    } catch (e) {
      setError((e as Error).message);
      setBusy(false);
    }
  }

  return (
    <div className="flex max-w-[760px] flex-col gap-10">
      <header>
        <Eyebrow>Account</Eyebrow>
        <h1 className="font-disp mt-2 text-[clamp(26px,3vw,36px)]">Your account and data</h1>
        <p className="mt-2 text-[14px] text-[var(--muted)]">
          Signed in as {me.email ?? me.id}. Terms version {me.current_terms_version} accepted {date(me.terms_accepted_at)}.
        </p>
      </header>
      {error && <ErrorNote>{error}</ErrorNote>}
      <Panel title="Download your data">
        <p className="mb-4 text-[14px] leading-7 text-[var(--muted)]">
          A JSON file with your account details, the questions you asked, their sources, claims and analysis, your document list and your activity log.
        </p>
        <Button variant="outline" onClick={exportData}>
          Export my data
        </Button>
      </Panel>
      <Panel title="Delete your account">
        <p className="mb-4 text-[14px] leading-7 text-[var(--muted)]">
          This permanently deletes your account, the workspaces you own, their research runs and reports, and every document you uploaded. People you
          shared a workspace with lose access to it. A pseudonymous record that you accepted our terms is kept, as our{" "}
          <Link href="/legal/privacy" className="text-[var(--accent)] underline underline-offset-2">
            privacy notice
          </Link>{" "}
          explains. This cannot be undone.
        </p>
        <label htmlFor="confirm" className="text-[13px]">
          Type DELETE to confirm
        </label>
        <div className="mt-1.5 flex flex-wrap gap-3">
          <input id="confirm" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="px-3 py-2" autoComplete="off" />
          <Button onClick={remove} disabled={confirm !== "DELETE" || busy} className="bg-[var(--bad)] text-[var(--bg)]">
            {busy ? "Deleting…" : "Delete account permanently"}
          </Button>
        </div>
      </Panel>
    </div>
  );
}
