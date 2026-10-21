import type { EvidenceOut } from "@/lib/types";

/** Marks the exact span the verifier quoted, using the offsets stored by the API. */
export function Extract({ e }: { e: EvidenceOut }) {
  const text = e.passage;
  if (e.quote_start == null || e.quote_end == null || e.quote_end > text.length) return <>{text}</>;
  return (
    <>
      {text.slice(0, e.quote_start)}
      <mark className="bg-[rgba(200,166,93,0.22)] px-0.5 text-[var(--fg)] not-italic">{text.slice(e.quote_start, e.quote_end)}</mark>
      {text.slice(e.quote_end)}
    </>
  );
}
