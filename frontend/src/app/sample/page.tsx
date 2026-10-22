import type { Metadata } from "next";
import { Suspense } from "react";

import { SharedView } from "@/components/run/shared-view";

export const metadata: Metadata = {
  title: "Sample report · Strategic Intelligence Hub",
  description: "What a finished, evidence-checked market-entry report looks like.",
};

export default function SamplePage() {
  return (
    <div className="gutter mx-auto max-w-[1240px] py-8">
      <Suspense fallback={<p className="text-sm text-[var(--muted)]">Loading…</p>}>
        <SharedView sample />
      </Suspense>
    </div>
  );
}
