/**
 * Deterministic scenario model used by the design preview.
 *
 * Production calculations stay in Python (see docs/redesign/ARCHITECTURE.md); this is a
 * TypeScript mirror so the preview's assumption controls respond instantly without a
 * backend. No language model touches these numbers.
 */

export type Assumptions = {
  price: number; // € list price per pair
  grossMargin: number; // share of net revenue after product cost
  returnRate: number; // share of orders returned
  cac: number; // € blended acquisition cost per new customer
  marketing: number; // € paid marketing per month
  repeatRate: number; // share of customers who buy again within a year
  fixedCosts: number; // € operating costs per month
  launchCost: number; // € one-off launch investment
};

export const baseAssumptions: Assumptions = {
  price: 159,
  grossMargin: 0.62,
  returnRate: 0.35,
  cac: 58,
  marketing: 30000,
  repeatRate: 0.4,
  fixedCosts: 15000,
  launchCost: 150000,
};

const FULFILMENT_PER_ORDER = 8;
const RETURN_HANDLING_PER_RETURN = 9;
export const MONTHS = 36;

export type ScenarioKey = "conservative" | "base" | "optimistic";

export const scenarioShifts: Record<ScenarioKey, { label: string; cac: number; repeatRate: number; returnRate: number }> = {
  conservative: { label: "Conservative", cac: 1.25, repeatRate: 0.8, returnRate: 1.1 },
  base: { label: "Base", cac: 1, repeatRate: 1, returnRate: 1 },
  optimistic: { label: "Optimistic", cac: 0.8, repeatRate: 1.2, returnRate: 0.9 },
};

export type Projection = {
  revenue: number[];
  ebitda: number[];
  cumulativeCash: number[];
  breakEvenMonth: number | null;
  paybackMonth: number | null;
  peakFunding: number;
  revenue36: number;
  cash36: number;
};

export function project(a: Assumptions): Projection {
  const revenue: number[] = [];
  const ebitda: number[] = [];
  const cumulativeCash: number[] = [];
  let customers = 0;
  let cash = -a.launchCost;
  let peakFunding = cash;
  let breakEvenMonth: number | null = null;
  let paybackMonth: number | null = null;

  for (let m = 1; m <= MONTHS; m++) {
    const newCustomers = a.marketing / a.cac;
    const repeatOrders = customers * (a.repeatRate / 12);
    customers += newCustomers;
    const orders = newCustomers + repeatOrders;
    const netRevenue = orders * (1 - a.returnRate) * a.price;
    const grossProfit =
      netRevenue * a.grossMargin - orders * FULFILMENT_PER_ORDER - orders * a.returnRate * RETURN_HANDLING_PER_RETURN;
    const monthEbitda = grossProfit - a.marketing - a.fixedCosts;
    cash += monthEbitda;
    revenue.push(netRevenue);
    ebitda.push(monthEbitda);
    cumulativeCash.push(cash);
    peakFunding = Math.min(peakFunding, cash);
    if (breakEvenMonth === null && monthEbitda >= 0) breakEvenMonth = m;
    if (paybackMonth === null && cash >= 0) paybackMonth = m;
  }

  return {
    revenue,
    ebitda,
    cumulativeCash,
    breakEvenMonth,
    paybackMonth,
    peakFunding,
    revenue36: revenue.reduce((s, v) => s + v, 0),
    cash36: cash,
  };
}

export function applyScenario(a: Assumptions, key: ScenarioKey): Assumptions {
  const s = scenarioShifts[key];
  return {
    ...a,
    cac: a.cac * s.cac,
    repeatRate: Math.min(1, a.repeatRate * s.repeatRate),
    returnRate: Math.min(0.95, a.returnRate * s.returnRate),
  };
}

export function projectAll(a: Assumptions): Record<ScenarioKey, Projection> {
  return {
    conservative: project(applyScenario(a, "conservative")),
    base: project(a),
    optimistic: project(applyScenario(a, "optimistic")),
  };
}

export type SensitivityRow = { key: keyof Assumptions; label: string; low: number; high: number };

const sensitivityLabels: Partial<Record<keyof Assumptions, string>> = {
  cac: "Acquisition cost",
  repeatRate: "Repeat rate",
  returnRate: "Return rate",
  grossMargin: "Gross margin",
  price: "Price",
  fixedCosts: "Fixed costs",
};

/** 36-month cash change when each driver moves ±20%, sorted by swing. */
export function sensitivity(a: Assumptions, swing = 0.2): SensitivityRow[] {
  const base = project(a).cash36;
  return (Object.keys(sensitivityLabels) as (keyof Assumptions)[])
    .map((key) => {
      const lowCase = project({ ...a, [key]: a[key] * (1 - swing) }).cash36 - base;
      const highCase = project({ ...a, [key]: a[key] * (1 + swing) }).cash36 - base;
      return { key, label: sensitivityLabels[key]!, low: lowCase, high: highCase };
    })
    .sort((x, y) => Math.abs(y.high - y.low) - Math.abs(x.high - x.low));
}

export const eur = (v: number, digits = 0) =>
  new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR", maximumFractionDigits: digits }).format(v);

export const eurK = (v: number) => {
  const sign = v < 0 ? "−" : "";
  const abs = Math.abs(v);
  if (abs >= 1_000_000) return `${sign}€${(abs / 1_000_000).toFixed(2)}m`;
  return `${sign}€${Math.round(abs / 1000)}k`;
};

export const pct = (v: number, digits = 0) => `${(v * 100).toFixed(digits)}%`;
