import { Suspense } from "react";

import { Compare } from "./compare";

export default function ComparePage() {
  return (
    <Suspense fallback={<p className="text-sm text-[var(--muted)]">Loading…</p>}>
      <Compare />
    </Suspense>
  );
}
