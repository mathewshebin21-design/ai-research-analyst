"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ErrorNote } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/lib/api";
import type { Me } from "@/lib/types";

export default function AcceptTerms() {
  const router = useRouter();
  const [me, setMe] = useState<Me | null>(null);
  const [agreed, setAgreed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api<Me>("/me")
      .then((m) => (m.needs_terms ? setMe(m) : router.replace("/app")))
      .catch((e) => (e instanceof ApiError && e.status === 401 ? router.replace("/sign-in") : setError(e.message)));
  }, [router]);

  async function accept() {
    if (!me) return;
    try {
      await api("/me/accept-terms", { method: "POST", json: { terms_version: me.current_terms_version, privacy_version: me.current_privacy_version } });
      router.replace("/app");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not record your acceptance.");
    }
  }

  return (
    <div className="gutter mx-auto flex min-h-dvh max-w-[560px] flex-col justify-center gap-5 py-12">
      <h1 className="font-disp text-[30px]">{me?.terms_accepted_at ? "Our terms have changed" : "Before you start"}</h1>
      <p className="text-[15px] leading-7 text-[var(--muted)]">Please read and accept these documents. They explain what the service does, what it does not do, and how your data is handled.</p>
      <ul className="flex flex-col gap-2 text-[14.5px]">
        <li>
          <Link className="text-[var(--accent)] underline underline-offset-4" href="/legal/terms" target="_blank">Terms of Service</Link>, including that outputs are not financial, investment or legal advice
        </li>
        <li>
          <Link className="text-[var(--accent)] underline underline-offset-4" href="/legal/privacy" target="_blank">Privacy Notice</Link> (UK GDPR)
        </li>
        <li>
          <Link className="text-[var(--accent)] underline underline-offset-4" href="/legal/ai-notice" target="_blank">AI and Evidence Notice</Link>
        </li>
        <li>
          <Link className="text-[var(--accent)] underline underline-offset-4" href="/legal/acceptable-use" target="_blank">Acceptable Use Policy</Link>
        </li>
      </ul>
      <label className="flex items-start gap-3 text-[14px] leading-6">
        <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} className="mt-1 size-4 accent-[var(--accent)]" />
        I have read and accept the Terms of Service and Acceptable Use Policy, and I have read the Privacy Notice. I confirm I am 18 or over and using the service for business purposes.
      </label>
      {error && <ErrorNote>{error}</ErrorNote>}
      <Button onClick={accept} disabled={!agreed || !me} className="self-start">
        Accept and continue
      </Button>
      {me && <p className="text-[11.5px] text-[var(--muted)]">Version {me.current_terms_version}. Your acceptance and its date are recorded.</p>}
    </div>
  );
}
