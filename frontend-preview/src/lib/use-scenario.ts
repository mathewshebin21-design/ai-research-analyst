"use client";

import { useMemo, useState } from "react";

import { baseAssumptions, projectAll, sensitivity, type Assumptions } from "@/lib/finance";

export type Control = {
  key: keyof Assumptions;
  label: string;
  min: number;
  max: number;
  step: number;
  format: (v: number) => string;
  source: string;
};

export const controls: Control[] = [
  { key: "cac", label: "Acquisition cost", min: 30, max: 110, step: 1, format: (v) => `€${v.toFixed(0)}`, source: "Assumption (no source, C7)" },
  { key: "price", label: "Price per pair", min: 119, max: 199, step: 1, format: (v) => `€${v.toFixed(0)}`, source: "Planned; band from C5" },
  { key: "returnRate", label: "Return rate", min: 0.15, max: 0.55, step: 0.01, format: (v) => `${Math.round(v * 100)}%`, source: "Benchmark 35–50%, C8" },
  { key: "repeatRate", label: "Repeat rate (12 mo)", min: 0.1, max: 0.6, step: 0.01, format: (v) => `${Math.round(v * 100)}%`, source: "Assumption" },
  { key: "marketing", label: "Marketing per month", min: 10000, max: 60000, step: 1000, format: (v) => `€${Math.round(v / 1000)}k`, source: "Plan input" },
];

export function useScenario() {
  const [assumptions, setAssumptions] = useState<Assumptions>(baseAssumptions);
  const results = useMemo(() => projectAll(assumptions), [assumptions]);
  const tornado = useMemo(() => sensitivity(assumptions), [assumptions]);
  const set = (key: keyof Assumptions, value: number) => setAssumptions((a) => ({ ...a, [key]: value }));
  const reset = () => setAssumptions(baseAssumptions);
  const changed = (Object.keys(baseAssumptions) as (keyof Assumptions)[]).some((k) => assumptions[k] !== baseAssumptions[k]);
  return { assumptions, results, tornado, set, reset, changed };
}

export type Scenario = ReturnType<typeof useScenario>;
