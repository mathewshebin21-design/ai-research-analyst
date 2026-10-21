/**
 * ILLUSTRATIVE DATA ONLY.
 *
 * Every company, source, figure and extract in this file is invented for the design
 * preview. Source domains use the reserved `.example` TLD so nothing here can be
 * mistaken for a real citation. The production build replaces this module with
 * responses from the FastAPI research service.
 */

export type ClaimStatus = "supported" | "partial" | "contradicted" | "unsupported" | "missing";
export type TaskStatus = "done" | "running" | "queued" | "blocked";
export type Relation = "supports" | "contradicts" | "related";
export type SourceTier = "A" | "B" | "C";

export const question = {
  company: "Verdant Stride",
  text: "Should Verdant Stride launch its premium sustainable footwear line direct-to-consumer in Germany in 2027?",
  short: "Germany D2C launch, 2027",
  owner: "Strategy team",
  created: "18 Oct 2026",
  workspace: "Market entry · DACH",
};

export const recommendation = {
  verdict: "Run a 6-month online pilot before committing to full entry",
  stance: "Conditional go" as const,
  confidence: 0.58,
  confidenceLabel: "Moderate",
  summary:
    "Demand signals for premium sustainable footwear in Germany are consistent across sources, but unit economics depend on a customer acquisition cost that no retrieved source pins down. A capped pilot tests that assumption for a fraction of the full-entry budget.",
  conditions: [
    "Blended CAC at or below €62 by month 4 of the pilot",
    "Repeat purchase rate of at least 22% in the first cohort",
    "Packaging registration and product-claim review completed before launch",
  ],
  wouldChange: [
    "A primary survey showing willingness to pay below €140 would move the call to no-go.",
    "Confirmed retail partner shelf space would justify skipping the pilot.",
  ],
};

export type Task = {
  id: string;
  title: string;
  category: string;
  status: TaskStatus;
  queries: string[];
  sources: number;
  claims: number;
  supported: number;
  note?: string;
};

export const tasks: Task[] = [
  {
    id: "T1",
    title: "Market size and growth",
    category: "Market",
    status: "done",
    queries: ["germany premium sneaker market size 2025", "sustainable footwear demand germany survey"],
    sources: 9,
    claims: 2,
    supported: 1,
  },
  {
    id: "T2",
    title: "Customer demand and willingness to pay",
    category: "Customer",
    status: "done",
    queries: ["german consumers willingness to pay sustainable shoes", "eco footwear purchase drivers survey"],
    sources: 7,
    claims: 2,
    supported: 0,
  },
  {
    id: "T3",
    title: "Competitor landscape and positioning",
    category: "Competition",
    status: "done",
    queries: ["sustainable sneaker brands germany d2c", "premium eco footwear price points eu"],
    sources: 11,
    claims: 2,
    supported: 1,
  },
  {
    id: "T4",
    title: "Pricing and unit economics benchmarks",
    category: "Financial",
    status: "running",
    queries: ["d2c footwear customer acquisition cost europe", "footwear ecommerce return rate germany"],
    sources: 5,
    claims: 2,
    supported: 0,
    note: "No source states a CAC for this category in Germany. Using a user assumption.",
  },
  {
    id: "T5",
    title: "Regulation and product claims",
    category: "Legal / risk",
    status: "running",
    queries: ["germany packaging registration ecommerce obligations", "eu rules environmental marketing claims"],
    sources: 4,
    claims: 1,
    supported: 1,
  },
  {
    id: "T6",
    title: "Supply chain and fulfilment",
    category: "Operations",
    status: "queued",
    queries: ["eu 3pl footwear fulfilment cost per order"],
    sources: 0,
    claims: 0,
    supported: 0,
  },
  {
    id: "T7",
    title: "Financial scenarios",
    category: "Financial",
    status: "blocked",
    queries: [],
    sources: 0,
    claims: 0,
    supported: 0,
    note: "Waits on T4 benchmarks. Running on stated assumptions in the meantime.",
  },
];

export type Source = {
  id: string;
  title: string;
  publisher: string;
  domain: string;
  kind: "web" | "pdf" | "dataset";
  tier: SourceTier;
  published: string;
  retrieved: string;
  pages?: number;
};

export const sources: Source[] = [
  { id: "S1", title: "Footwear retail panel, annual release", publisher: "National statistics office", domain: "destatis-sample.example", kind: "dataset", tier: "A", published: "Mar 2026", retrieved: "18 Oct 2026" },
  { id: "S2", title: "Premium sneaker market outlook: DACH", publisher: "Market research firm", domain: "marketview.example", kind: "pdf", tier: "B", published: "Jan 2026", retrieved: "18 Oct 2026", pages: 64 },
  { id: "S3", title: "Consumer sustainability barometer 2026", publisher: "Consumer research institute", domain: "konsum-institut.example", kind: "pdf", tier: "B", published: "May 2026", retrieved: "18 Oct 2026", pages: 38 },
  { id: "S4", title: "Why eco sneakers are the next big thing", publisher: "Lifestyle magazine", domain: "trendpost.example", kind: "web", tier: "C", published: "Aug 2026", retrieved: "18 Oct 2026" },
  { id: "S5", title: "Competitor price scrape, 412 SKUs", publisher: "Collected by research agent", domain: "internal", kind: "dataset", tier: "A", published: "18 Oct 2026", retrieved: "18 Oct 2026" },
  { id: "S6", title: "D2C benchmarks report: apparel and accessories", publisher: "E-commerce association", domain: "ecom-verband.example", kind: "pdf", tier: "B", published: "Feb 2026", retrieved: "18 Oct 2026", pages: 52 },
  { id: "S7", title: "Packaging register: guidance for online sellers", publisher: "Packaging registry authority", domain: "register-sample.example", kind: "web", tier: "A", published: "Jun 2026", retrieved: "19 Oct 2026" },
  { id: "S8", title: "France eco-footwear market note", publisher: "Trade agency", domain: "trade-fr.example", kind: "pdf", tier: "B", published: "Apr 2026", retrieved: "19 Oct 2026", pages: 12 },
];

export type Evidence = {
  sourceId: string;
  extract: string;
  highlight: string;
  page?: number;
  relation: Relation;
  relevance: number;
  entailment: number;
};

export type Claim = {
  id: string;
  taskId: string;
  text: string;
  status: ClaimStatus;
  rationale: string;
  evidence: Evidence[];
};

export const claims: Claim[] = [
  {
    id: "C1",
    taskId: "T1",
    text: "Premium sneaker sales in Germany grew between 6% and 8% a year from 2023 to 2025.",
    status: "supported",
    rationale: "Two independent sources (one official dataset, one industry report) state growth inside this range for the same period and geography.",
    evidence: [
      { sourceId: "S1", extract: "Turnover in the premium athletic and lifestyle footwear segment rose by 7.1% in 2024 and 6.4% in 2025, following 7.8% in 2023.", highlight: "rose by 7.1% in 2024 and 6.4% in 2025, following 7.8% in 2023", relation: "supports", relevance: 0.91, entailment: 0.94 },
      { sourceId: "S2", extract: "We estimate the German premium sneaker segment expanded at roughly 7% per year over 2023–2025, ahead of the wider footwear market.", highlight: "expanded at roughly 7% per year over 2023–2025", page: 14, relation: "supports", relevance: 0.88, entailment: 0.86 },
    ],
  },
  {
    id: "C2",
    taskId: "T1",
    text: "The German sustainable footwear segment will grow at 12.4% CAGR through 2030.",
    status: "unsupported",
    rationale: "This figure came from the earlier report template. Three retrieved sources discuss sustainable footwear growth and score as highly relevant, but none states this number or a comparable forecast. Relevance is not support, so the claim is removed from the recommendation.",
    evidence: [
      { sourceId: "S4", extract: "Eco sneakers are booming, with brands reporting double-digit growth and shoppers increasingly asking where their shoes come from.", highlight: "brands reporting double-digit growth", relation: "related", relevance: 0.84, entailment: 0.21 },
      { sourceId: "S2", extract: "Sustainability-positioned lines are a fast-growing niche, though volumes remain too small for a reliable standalone forecast.", highlight: "too small for a reliable standalone forecast", page: 22, relation: "related", relevance: 0.81, entailment: 0.12 },
    ],
  },
  {
    id: "C3",
    taskId: "T2",
    text: "About a third of German premium footwear buyers say sustainability influences their purchase.",
    status: "partial",
    rationale: "One survey supports a figure near one third, but it measures 'all footwear buyers', not the premium segment. Treated as directional.",
    evidence: [
      { sourceId: "S3", extract: "34% of respondents who bought footwear in the past 12 months said environmental impact played an important or very important role in their choice.", highlight: "34% of respondents who bought footwear", page: 9, relation: "supports", relevance: 0.86, entailment: 0.63 },
    ],
  },
  {
    id: "C4",
    taskId: "T2",
    text: "Target customers will pay a premium of at least 20% for verified sustainable materials.",
    status: "contradicted",
    rationale: "The only survey that measures price premium reports a median of 10–15%, below the 20% the plan assumed.",
    evidence: [
      { sourceId: "S3", extract: "Among respondents willing to pay more for sustainable footwear, the median acceptable premium was 10–15%; fewer than one in five accepted a premium above 20%.", highlight: "median acceptable premium was 10–15%", page: 17, relation: "contradicts", relevance: 0.9, entailment: 0.08 },
    ],
  },
  {
    id: "C5",
    taskId: "T3",
    text: "Direct competitors price their core sneaker between €140 and €190.",
    status: "supported",
    rationale: "Computed from the agent's own price scrape (412 SKUs, 5 brands) and consistent with the industry report's price band.",
    evidence: [
      { sourceId: "S5", extract: "Median list price of core models across the five tracked brands: €159 (interquartile range €142–€186).", highlight: "Median list price of core models across the five tracked brands: €159", relation: "supports", relevance: 0.93, entailment: 0.92 },
      { sourceId: "S2", extract: "Sustainability-positioned premium sneakers cluster in a €140–€190 band in German online retail.", highlight: "cluster in a €140–€190 band", page: 31, relation: "supports", relevance: 0.89, entailment: 0.9 },
    ],
  },
  {
    id: "C6",
    taskId: "T3",
    text: "No incumbent holds more than 15% of the German sustainable sneaker niche.",
    status: "partial",
    rationale: "The source covers France. It is relevant by topic but the geography does not match, so it cannot support a claim about Germany.",
    evidence: [
      { sourceId: "S8", extract: "The eco-footwear segment remains fragmented; no single brand exceeds 15% of sales.", highlight: "no single brand exceeds 15% of sales", page: 4, relation: "related", relevance: 0.79, entailment: 0.41 },
    ],
  },
  {
    id: "C7",
    taskId: "T4",
    text: "Blended customer acquisition cost for premium footwear D2C in Germany is about €55.",
    status: "missing",
    rationale: "No retrieved source reports CAC for this category and country. The financial model uses €58 as a stated user assumption and shows the sensitivity of the result to it.",
    evidence: [
      { sourceId: "S6", extract: "Reported acquisition costs vary widely by category and channel; respondents did not provide footwear-specific figures.", highlight: "did not provide footwear-specific figures", page: 27, relation: "related", relevance: 0.74, entailment: 0.05 },
    ],
  },
  {
    id: "C8",
    taskId: "T4",
    text: "Online footwear return rates in Germany are high enough to cut contribution margin materially.",
    status: "partial",
    rationale: "One industry benchmark states the return rate clearly, but it is a single tier-B source. The margin effect is computed by the financial model, not the language model. Needs a second source before it counts as supported.",
    evidence: [
      { sourceId: "S6", extract: "Footwear has one of the highest return rates of any online category, with participants reporting 35–50% of orders returned.", highlight: "35–50% of orders returned", page: 33, relation: "supports", relevance: 0.87, entailment: 0.83 },
    ],
  },
  {
    id: "C9",
    taskId: "T5",
    text: "Online sellers shipping packaged goods to German consumers must register with the packaging registry before selling.",
    status: "supported",
    rationale: "Primary guidance from the registry authority states the obligation directly.",
    evidence: [
      { sourceId: "S7", extract: "Producers that place packaging filled with goods on the German market, including online sellers based abroad, must register before the first sale.", highlight: "must register before the first sale", relation: "supports", relevance: 0.95, entailment: 0.96 },
    ],
  },
];

export const critique = [
  { severity: "high" as const, claimId: "C2", text: "A 12.4% CAGR figure from the previous template has no source. Removed from the recommendation." },
  { severity: "high" as const, claimId: "C4", text: "The 20% price-premium assumption is contradicted by the only survey that measures it. Pricing now anchors on the observed €140–€190 band (C5) instead of a premium uplift." },
  { severity: "medium" as const, claimId: "C6", text: "Market-concentration claim relies on a France-only source. Needs a Germany source or should be dropped." },
  { severity: "medium" as const, claimId: "C7", text: "CAC is the largest driver of the result and is an assumption. Recommendation is conditional on testing it." },
  { severity: "low" as const, claimId: "C3", text: "Survey population is all footwear buyers, not the premium segment." },
];

export const missingData = [
  { item: "Customer acquisition cost, footwear, Germany", impact: "High", plan: "Measure in pilot; buy a paid benchmark if the pilot is declined" },
  { item: "Premium-segment willingness to pay", impact: "High", plan: "Commission a 600-respondent survey (est. €9k)" },
  { item: "3PL cost per order with returns", impact: "Medium", plan: "Request quotes from three providers (task T6)" },
  { item: "Market share of incumbents in Germany", impact: "Medium", plan: "Panel data purchase or exclude from scoring" },
];

export type Factor = {
  key: string;
  label: string;
  short: string;
  weight: number;
  score: number;
  coverage: number;
  note: string;
};

export const factors: Factor[] = [
  { key: "attract", short: "Market", label: "Market attractiveness", weight: 0.25, score: 72, coverage: 0.75, note: "Growth supported by C1; forecast claim C2 excluded" },
  { key: "demand", short: "Demand", label: "Customer demand", weight: 0.2, score: 61, coverage: 0.67, note: "C3 directional only; premium contradicted by C4" },
  { key: "compete", short: "Competition", label: "Competitive room", weight: 0.15, score: 58, coverage: 0.6, note: "Price band clear (C5); concentration unverified (C6)" },
  { key: "econ", short: "Economics", label: "Unit economics", weight: 0.25, score: 44, coverage: 0.33, note: "CAC missing (C7); returns pressure margin (C8)" },
  { key: "exec", short: "Execution", label: "Execution and compliance", weight: 0.15, score: 70, coverage: 0.5, note: "Registration obligation clear (C9); fulfilment not yet researched" },
];

export type Competitor = {
  name: string;
  price: number;
  transparency: number;
  shareLow: number;
  shareHigh: number;
  channel: string;
};

export const competitors: Competitor[] = [
  { name: "Northfold", price: 179, transparency: 78, shareLow: 9, shareHigh: 14, channel: "D2C + wholesale" },
  { name: "Kiefer & Moss", price: 165, transparency: 64, shareLow: 6, shareHigh: 11, channel: "Wholesale" },
  { name: "Lumen Trail", price: 149, transparency: 82, shareLow: 4, shareHigh: 8, channel: "D2C" },
  { name: "Ostwerk", price: 139, transparency: 45, shareLow: 10, shareHigh: 16, channel: "Retail chains" },
  { name: "Greyhaven", price: 189, transparency: 58, shareLow: 3, shareHigh: 6, channel: "D2C" },
];

export const verdantPosition = { name: "Verdant Stride (planned)", price: 159, transparency: 86 };

export const frameworks = {
  swot: {
    strengths: ["Material traceability already certified", "Existing D2C stack from home market"],
    weaknesses: ["No brand awareness in Germany", "CAC untested outside home market"],
    opportunities: ["Fragmented niche, no clear leader (unverified, C6)", "Price band €140–€190 matches planned €159 (C5)"],
    threats: ["High return rates (C8)", "Premium tolerance lower than assumed (C4)"],
  },
  pestle: [
    { factor: "Political", rating: 2, note: "Stable; no sector-specific trade barriers within the EU" },
    { factor: "Economic", rating: 3, note: "Segment growth 6–8% a year (C1)" },
    { factor: "Social", rating: 3, note: "Sustainability matters to about a third of buyers (C3)" },
    { factor: "Technological", rating: 2, note: "Commodity e-commerce tooling" },
    { factor: "Legal", rating: 4, note: "Packaging registration (C9); stricter rules on environmental claims" },
    { factor: "Environmental", rating: 3, note: "Return logistics add emissions and cost (C8)" },
  ],
  porter: [
    { force: "Rivalry", level: 3.6 },
    { force: "New entrants", level: 3.2 },
    { force: "Substitutes", level: 2.8 },
    { force: "Buyer power", level: 4.1 },
    { force: "Supplier power", level: 2.4 },
  ],
};

export const activity = [
  { t: "10:42", agent: "Critic", text: "Flagged C2: no source states 12.4% CAGR" },
  { t: "10:41", agent: "Verifier", text: "C4 contradicted by S3 p.17 (entailment 0.08)" },
  { t: "10:39", agent: "Researcher", text: "T4: 5 sources, none report footwear CAC" },
  { t: "10:36", agent: "Researcher", text: "T3: price scrape complete, 412 SKUs" },
  { t: "10:31", agent: "Planner", text: "Plan approved: 7 tasks, 14 queries" },
];

export const history = [
  { title: "Germany D2C launch, 2027", date: "18 Oct 2026", verdict: "Conditional go", active: true },
  { title: "Austria wholesale partner", date: "02 Oct 2026", verdict: "No-go" },
  { title: "Netherlands pop-up retail", date: "21 Sep 2026", verdict: "Go" },
];

export const statusMeta: Record<ClaimStatus, { label: string; short: string }> = {
  supported: { label: "Supported", short: "SUP" },
  partial: { label: "Partially supported", short: "PRT" },
  contradicted: { label: "Contradicted", short: "CON" },
  unsupported: { label: "Unsupported", short: "UNS" },
  missing: { label: "Missing data", short: "GAP" },
};

export function sourceById(id: string) {
  const source = sources.find((s) => s.id === id);
  if (!source) throw new Error(`Unknown source ${id}`);
  return source;
}

export function claimCounts() {
  const counts: Record<ClaimStatus, number> = { supported: 0, partial: 0, contradicted: 0, unsupported: 0, missing: 0 };
  for (const c of claims) counts[c.status] += 1;
  return counts;
}
