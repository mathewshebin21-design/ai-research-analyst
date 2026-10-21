import { cn } from "@/lib/utils";

/** Persistent marker so no screen of the preview can be mistaken for real research. */
export function IllustrativeTag({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border border-dashed border-[var(--warn)] px-2 py-0.5 text-[10px] font-semibold tracking-[0.08em] text-[var(--warn)] uppercase",
        className,
      )}
    >
      <span aria-hidden className="size-1.5 rounded-full bg-[var(--warn)]" />
      Illustrative data
    </span>
  );
}
