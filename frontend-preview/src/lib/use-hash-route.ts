"use client";

import { useCallback, useSyncExternalStore } from "react";

export const designs = ["executive", "command", "minimal"] as const;
export const views = ["dashboard", "workspace", "evidence"] as const;
export type Design = (typeof designs)[number];
export type View = (typeof views)[number];
export type Route = { design: Design | null; view: View };

// Routes are bare hash tokens such as #command-evidence so links survive hosts that
// only forward simple anchors.
function parse(hash: string): Route {
  const [d, v] = hash.replace(/^#/, "").split("-");
  const design = (designs as readonly string[]).includes(d) ? (d as Design) : null;
  const view = (views as readonly string[]).includes(v) ? (v as View) : "dashboard";
  return { design, view };
}

function subscribe(onChange: () => void) {
  window.addEventListener("hashchange", onChange);
  return () => window.removeEventListener("hashchange", onChange);
}

export function useHashRoute() {
  const hash = useSyncExternalStore(subscribe, () => window.location.hash, () => "");
  const route = parse(hash);
  const go = useCallback((design: Design | null, view: View = "dashboard") => {
    const next = design ? `#${design}-${view}` : "#brief";
    if (window.location.hash !== next) window.location.hash = next;
    window.scrollTo({ top: 0 });
  }, []);
  return { route, go };
}
