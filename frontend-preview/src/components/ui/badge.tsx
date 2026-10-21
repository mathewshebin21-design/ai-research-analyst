import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 whitespace-nowrap border px-2 py-0.5 text-[11px] font-medium leading-4 [&_svg]:size-3",
  {
    variants: {
      variant: {
        default: "border-transparent bg-[var(--surface-2)] text-[var(--fg)]",
        outline: "border-[var(--line)] text-[var(--muted)]",
        supported: "border-transparent bg-[var(--ok-bg)] text-[var(--ok)]",
        partial: "border-transparent bg-[var(--warn-bg)] text-[var(--warn)]",
        contradicted: "border-transparent bg-[var(--bad-bg)] text-[var(--bad)]",
        unsupported: "border-[var(--bad)] border-dashed text-[var(--bad)]",
        missing: "border-[var(--line)] border-dashed text-[var(--muted)]",
      },
      shape: { pill: "rounded-full", square: "rounded-[3px]" },
    },
    defaultVariants: { variant: "default", shape: "pill" },
  },
);

function Badge({
  className,
  variant,
  shape,
  ...props
}: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span data-slot="badge" className={cn(badgeVariants({ variant, shape }), className)} {...props} />;
}

export { Badge, badgeVariants };
