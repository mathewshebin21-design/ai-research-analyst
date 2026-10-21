"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { api, ApiError } from "@/lib/api";
import type { Me, Workspace } from "@/lib/types";

type Session = {
  me: Me;
  workspaces: Workspace[];
  workspace: Workspace;
  setWorkspace: (id: string) => void;
  reloadWorkspaces: () => Promise<void>;
};

const Ctx = createContext<Session | null>(null);
const WS_KEY = "sih.workspace";

function remembered(): string | null {
  try {
    return localStorage.getItem(WS_KEY);
  } catch {
    return null;
  }
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<{ me: Me; workspaces: Workspace[]; current: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const me = await api<Me>("/me");
      if (me.needs_terms) {
        router.replace("/accept-terms");
        return;
      }
      let workspaces = await api<Workspace[]>("/workspaces");
      if (workspaces.length === 0) {
        await api("/workspaces", { method: "POST", json: { name: "My research" } });
        workspaces = await api<Workspace[]>("/workspaces");
      }
      const saved = remembered();
      const current = workspaces.find((w) => w.id === saved)?.id ?? workspaces[0].id;
      setState({ me, workspaces, current });
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) router.replace("/sign-in");
      else if (e instanceof ApiError && e.code === "terms_required") router.replace("/accept-terms");
      else setError(e instanceof Error ? e.message : "Something went wrong.");
    }
  }, [router]);

  useEffect(() => {
    // Session bootstrap: the API is the source of truth for sign-in and consent.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  if (error)
    return (
      <div className="gutter mx-auto max-w-lg py-24 text-center">
        <p className="font-disp text-2xl">The service is unavailable</p>
        <p className="mt-3 text-sm text-[var(--muted)]">{error}</p>
        <button type="button" onClick={() => { setError(null); load(); }} className="mt-6 border border-[var(--line)] px-4 py-2 text-sm">
          Try again
        </button>
      </div>
    );
  if (!state) return <div className="grid min-h-dvh place-items-center text-sm text-[var(--muted)]">Loading your workspace…</div>;

  const workspace = state.workspaces.find((w) => w.id === state.current)!;
  return (
    <Ctx.Provider
      value={{
        me: state.me,
        workspaces: state.workspaces,
        workspace,
        setWorkspace: (id) => {
          try {
            localStorage.setItem(WS_KEY, id);
          } catch {}
          setState({ ...state, current: id });
        },
        reloadWorkspaces: load,
      }}
    >
      {children}
    </Ctx.Provider>
  );
}

export function useSession(): Session {
  const s = useContext(Ctx);
  if (!s) throw new Error("useSession outside SessionProvider");
  return s;
}
