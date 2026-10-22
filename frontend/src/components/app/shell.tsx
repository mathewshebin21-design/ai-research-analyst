"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BookOpenCheck, GitCompare, LogOut, UserRound } from "lucide-react";

import { api } from "@/lib/api";
import { signOut } from "@/lib/auth";
import { date } from "@/lib/format";
import type { RunSummary } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Eyebrow } from "./status";
import { useSession } from "./session";

const nav = [
  { href: "/app", label: "Research", icon: BookOpenCheck },
  { href: "/app/compare", label: "Compare runs", icon: GitCompare },
  { href: "/app/account", label: "Account and data", icon: UserRound },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const { workspace, workspaces, setWorkspace } = useSession();
  const pathname = usePathname();
  const router = useRouter();
  const [recent, setRecent] = useState<RunSummary[]>([]);

  const pending = recent.some((r) => ["planned", "queued", "running"].includes(r.status));

  useEffect(() => {
    let live = true;
    const load = () =>
      api<RunSummary[]>(`/workspaces/${workspace.id}/runs`)
        .then((r) => live && setRecent(r.slice(0, 6)))
        .catch(() => live && setRecent([]));
    load();
    // Keep statuses fresh while a run is in progress, and immediately when a run page reports a change.
    const timer = pending ? setInterval(load, 10_000) : undefined;
    window.addEventListener("sih:runs-changed", load);
    return () => {
      live = false;
      clearInterval(timer);
      window.removeEventListener("sih:runs-changed", load);
    };
  }, [workspace.id, pathname, pending]);

  return (
    <div className="lg:grid lg:min-h-dvh lg:grid-cols-[248px_minmax(0,1fr)]">
      <aside className="border-b border-[var(--line)] bg-[var(--rail)] lg:sticky lg:top-0 lg:h-dvh lg:border-r lg:border-b-0">
        <div className="gutter flex h-full flex-col gap-6 py-5 lg:px-5">
          <div className="flex items-center justify-between gap-3 lg:block">
            <Link href="/app" className="block">
              <p className="font-disp text-[19px] leading-none tracking-tight">Strategic Intelligence</p>
              <Eyebrow className="mt-1.5">Evidence-checked research</Eyebrow>
            </Link>
            {workspaces.length > 1 && (
              <select
                aria-label="Workspace"
                value={workspace.id}
                onChange={(e) => setWorkspace(e.target.value)}
                className="mt-0 max-w-[50%] px-2 py-1 text-[12.5px] lg:mt-4 lg:max-w-full lg:w-full"
              >
                {workspaces.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
              </select>
            )}
          </div>
          <nav aria-label="Primary" className="-mx-1 flex flex-wrap gap-1 lg:mx-0 lg:flex-col">
            {nav.map(({ href, label, icon: Icon }) => {
              const active = href === "/app" ? pathname === "/app" || pathname.startsWith("/app/run") : pathname.startsWith(href);
              return (
                <Link
                  key={href}
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-2.5 border-l-2 px-3 py-2 text-[13.5px] whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-[var(--ring)]",
                    active ? "border-[var(--accent)] bg-[var(--surface-2)]" : "border-transparent text-[var(--muted)] hover:text-[var(--fg)]",
                  )}
                >
                  <Icon className="size-4" strokeWidth={1.5} />
                  {label}
                </Link>
              );
            })}
          </nav>
          {recent.length > 0 && (
            <div className="hidden lg:block">
              <Eyebrow className="mb-2">Recent questions</Eyebrow>
              <ul className="flex flex-col gap-2.5">
                {recent.map((r) => (
                  <li key={r.id}>
                    <Link href={`/app/run?id=${r.id}`} className="block text-[13px] leading-5 text-[var(--muted)] hover:text-[var(--fg)]">
                      <span className="line-clamp-2">{r.question}</span>
                      <span className="block text-[11px]">
                        {date(r.created_at)} · {r.verdict ?? r.status}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-auto hidden flex-col gap-3 text-[12px] text-[var(--muted)] lg:flex">
            <button
              type="button"
              onClick={async () => {
                await signOut();
                router.replace("/sign-in");
              }}
              className="flex items-center gap-2 hover:text-[var(--fg)]"
            >
              <LogOut className="size-3.5" /> Sign out
            </button>
            <p className="flex flex-wrap gap-x-3 gap-y-1">
              <Link href="/legal/terms">Terms</Link>
              <Link href="/legal/privacy">Privacy</Link>
              <Link href="/legal/ai-notice">AI notice</Link>
            </p>
          </div>
        </div>
      </aside>
      <main className="gutter mx-auto w-full max-w-[1240px] pt-8 pb-24 lg:px-12">{children}</main>
    </div>
  );
}
