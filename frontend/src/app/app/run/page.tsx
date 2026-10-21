import { Suspense } from "react";

import { RunView } from "@/components/run/run-view";

export default function RunPage() {
  return (
    <Suspense fallback={<p className="text-sm text-[var(--muted)]">Loading…</p>}>
      <RunView />
    </Suspense>
  );
}
