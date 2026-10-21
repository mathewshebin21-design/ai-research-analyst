"use client";

import { designs, type Design, type View } from "@/lib/use-hash-route";
import { cn } from "@/lib/utils";

const names: Record<Design, [string, string]> = {
  executive: ["A", "Executive"],
  command: ["B", "Command"],
  minimal: ["C", "Minimal"],
};

/** Review harness, not part of the product: swaps designs while keeping the current view. */
export function PreviewSwitcher({ design, view, go }: { design: Design; view: View; go: (d: Design | null, v?: View) => void }) {
  return (
    <div
      className="fixed z-40 left-1/2 -translate-x-1/2 flex max-w-[calc(100vw-24px)] items-center gap-1 overflow-x-auto rounded-full border border-black/15 bg-white/90 p-1 text-[12px] text-neutral-800 shadow-xl backdrop-blur"
      style={{ bottom: "calc(12px + env(safe-area-inset-bottom, 0px))", fontFamily: "var(--font-review), system-ui, sans-serif" }}
    >
      <button
        type="button"
        onClick={() => go(null)}
        className="rounded-full px-3 py-1.5 whitespace-nowrap hover:bg-black/5 focus-visible:outline-2 focus-visible:outline-neutral-900"
      >
        ← <span className="hidden sm:inline">Review </span>brief
      </button>
      {designs.map((d) => (
        <button
          key={d}
          type="button"
          aria-current={d === design}
          onClick={() => go(d, view)}
          className={cn(
            "rounded-full px-3 py-1.5 whitespace-nowrap focus-visible:outline-2 focus-visible:outline-neutral-900",
            d === design ? "bg-neutral-900 text-white" : "hover:bg-black/5",
          )}
        >
          {names[d][0]}
          <span className="hidden sm:inline"> · {names[d][1]}</span>
        </button>
      ))}
    </div>
  );
}
