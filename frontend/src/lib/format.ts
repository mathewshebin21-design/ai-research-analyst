import type { AssumptionKey, ClaimStatus } from "./types";

export const statusLabel: Record<ClaimStatus, string> = {
  supported: "Supported",
  partial: "Partially supported",
  contradicted: "Contradicted",
  unsupported: "Unsupported",
  missing: "Missing data",
};

export const eurK = (v: number) => {
  const sign = v < 0 ? "−" : "";
  const abs = Math.abs(v);
  return abs >= 1_000_000 ? `${sign}€${(abs / 1_000_000).toFixed(2)}m` : `${sign}€${Math.round(abs / 1000)}k`;
};

export const assumptionMeta: Record<AssumptionKey, { label: string; share: boolean; min: number; max: number; step: number }> = {
  price: { label: "Price per unit", share: false, min: 1, max: 2000, step: 1 },
  gross_margin: { label: "Gross margin", share: true, min: 0.05, max: 0.95, step: 0.01 },
  return_rate: { label: "Return rate", share: true, min: 0, max: 0.9, step: 0.01 },
  cac: { label: "Acquisition cost per customer", share: false, min: 1, max: 1000, step: 1 },
  marketing: { label: "Marketing per month", share: false, min: 0, max: 500000, step: 1000 },
  repeat_rate: { label: "Repeat rate (12 months)", share: true, min: 0, max: 1, step: 0.01 },
  fixed_costs: { label: "Fixed costs per month", share: false, min: 0, max: 500000, step: 1000 },
  launch_cost: { label: "One-off launch cost", share: false, min: 0, max: 5000000, step: 5000 },
};

export const assumptionKeys = Object.keys(assumptionMeta) as AssumptionKey[];

export function formatAssumption(key: AssumptionKey, v: number) {
  const m = assumptionMeta[key];
  return m.share ? `${Math.round(v * 100)}%` : v >= 10000 ? eurK(v) : `€${v.toLocaleString("en-GB", { maximumFractionDigits: 0 })}`;
}

export function date(iso: string | null) {
  return iso ? new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) : "";
}
