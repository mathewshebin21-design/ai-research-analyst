import { Badge } from "@/components/ui/badge";
import { statusLabel } from "@/lib/format";
import type { ClaimStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

export function StatusBadge({ status }: { status: ClaimStatus }) {
  return (
    <Badge variant={status} shape="square">
      {statusLabel[status]}
    </Badge>
  );
}

export function Eyebrow({ children, className }: { children: React.ReactNode; className?: string }) {
  return <p className={cn("text-[10.5px] font-semibold tracking-[0.16em] text-[var(--muted)] uppercase", className)}>{children}</p>;
}

export function Panel({ title, aside, children, className }: { title: string; aside?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return (
    <section className={cn("min-w-0 border-t border-[var(--line)] pt-4", className)}>
      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-disp text-[21px] leading-tight">{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}

export function ErrorNote({ children }: { children: React.ReactNode }) {
  return (
    <p role="alert" className="border-l-2 border-[var(--bad)] bg-[var(--bad-bg)] px-3 py-2 text-[13.5px] text-[var(--bad)]">
      {children}
    </p>
  );
}

export function Field({ label, hint, children, htmlFor }: { label: string; hint?: string; htmlFor: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={htmlFor} className="text-[13px]">
        {label}
      </label>
      {children}
      {hint && <p className="text-[11.5px] text-[var(--muted)]">{hint}</p>}
    </div>
  );
}
