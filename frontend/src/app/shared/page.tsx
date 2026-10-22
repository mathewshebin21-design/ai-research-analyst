import type { Metadata } from "next";
import { Suspense } from "react";

import { SharedView } from "@/components/run/shared-view";

export const metadata: Metadata = {
  title: "Shared report · Strategic Intelligence Hub",
  robots: { index: false, follow: false },
  referrer: "no-referrer", // keep the link token out of Referer headers sent to cited sources
};

export default function SharedPage() {
  return (
    <div className="gutter mx-auto max-w-[1240px] py-8">
      <Suspense fallback={<p className="text-sm text-[var(--muted)]">Loading…</p>}>
        <SharedView />
      </Suspense>
    </div>
  );
}
