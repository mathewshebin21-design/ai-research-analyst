"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { ErrorNote, Field } from "@/components/app/status";
import { Button } from "@/components/ui/button";
import { authMode, signIn, signUp } from "@/lib/auth";

export default function SignIn() {
  const router = useRouter();
  const [mode, setMode] = useState<"in" | "up">("in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "up") {
        const r = await signUp(email, password);
        if (r === "check-email") {
          setNotice("Check your email to confirm your address, then sign in.");
          setMode("in");
          return;
        }
      } else {
        await signIn(email, password);
      }
      router.replace("/app");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="gutter mx-auto flex min-h-dvh max-w-[420px] flex-col justify-center py-12">
      <Link href="/" className="font-disp text-[20px]">
        Strategic Intelligence Hub
      </Link>
      <h1 className="font-disp mt-8 text-[30px]">{mode === "in" ? "Sign in" : "Create an account"}</h1>
      {authMode === "dev" && (
        <p className="mt-2 text-[12.5px] text-[var(--warn)]">Development sign-in: any email works and no password is checked.</p>
      )}
      <form onSubmit={submit} className="mt-6 flex flex-col gap-4">
        <Field label="Email" htmlFor="email">
          <input id="email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="px-3 py-2" />
        </Field>
        <Field label="Password" htmlFor="password" hint={mode === "up" ? "At least 8 characters." : undefined}>
          <input
            id="password"
            type="password"
            autoComplete={mode === "in" ? "current-password" : "new-password"}
            required={authMode === "supabase"}
            minLength={authMode === "supabase" ? 8 : undefined}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="px-3 py-2"
          />
        </Field>
        {error && <ErrorNote>{error}</ErrorNote>}
        {notice && <p className="text-[13px] text-[var(--ok)]">{notice}</p>}
        <Button type="submit" disabled={busy}>
          {busy ? "Please wait…" : mode === "in" ? "Sign in" : "Create account"}
        </Button>
      </form>
      <button type="button" onClick={() => setMode(mode === "in" ? "up" : "in")} className="mt-4 self-start text-[13px] text-[var(--muted)] underline-offset-4 hover:underline">
        {mode === "in" ? "New here? Create an account" : "Already have an account? Sign in"}
      </button>
    </div>
  );
}
