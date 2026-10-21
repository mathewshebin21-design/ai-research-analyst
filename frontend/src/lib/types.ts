export type ClaimStatus = "supported" | "partial" | "contradicted" | "unsupported" | "missing";
export type RunStatus = "draft" | "planned" | "queued" | "running" | "completed" | "failed";

export type Workspace = { id: string; name: string; role: "owner" | "editor" | "viewer" };

export type RunSummary = {
  id: string;
  workspace_id: string;
  question: string;
  status: RunStatus;
  stage: string | null;
  error: string | null;
  verdict: string | null;
  created_at: string;
  finished_at: string | null;
};

export type TaskOut = {
  id: string;
  key: string;
  title: string;
  category: string;
  rationale: string;
  queries: string[];
  status: "queued" | "running" | "done" | "failed";
  note: string | null;
  searches: { query: string; status: string; error: string | null; results: number }[];
  claims: number;
  supported: number;
};

export type SourceOut = {
  id: string;
  key: string;
  kind: "web" | "pdf";
  url: string | null;
  title: string;
  publisher: string;
  tier: "A" | "B" | "C";
  published: string | null;
  retrieved_at: string;
  document_id: string | null;
};

export type EvidenceOut = {
  source_id: string;
  passage: string;
  page: number | null;
  quote: string | null;
  quote_start: number | null;
  quote_end: number | null;
  relation: "supports" | "contradicts" | "related";
  entailment: number;
  relevance: number;
  scope_issue: string | null;
  note: string;
  model: string;
};

export type ClaimOut = {
  id: string;
  key: string;
  task: string | null;
  text: string;
  kind: "fact" | "figure" | "forecast";
  status: ClaimStatus;
  status_reason: string;
  evidence: EvidenceOut[];
};

export type Cited = { text: string; claims: string[]; basis: "evidenced" | "unsupported" | "no_evidence"; coverage: number };

export type Factor = {
  key: string;
  label: string;
  weight: number;
  score: number;
  model_score: number | null;
  coverage: number;
  claims: string[];
  rationale: string;
  basis: string;
};

export type Recommendation = {
  verdict: "Go" | "Conditional go" | "No-go" | "Insufficient evidence";
  rule: string;
  overall: number;
  coverage: number;
  confidence: number;
  confidence_label: string;
  confidence_method: string;
  headline: string;
  summary: string;
  conditions: string[];
  would_change: string[];
  cited: string[];
};

export type AssumptionKey = "price" | "gross_margin" | "return_rate" | "cac" | "marketing" | "repeat_rate" | "fixed_costs" | "launch_cost";
export type Assumption = { value: number; origin: "evidence" | "estimate" | "user"; claim: string | null; note: string };

export type Projection = {
  revenue: number[];
  ebitda: number[];
  cumulative_cash: number[];
  break_even_month: number | null;
  payback_month: number | null;
  peak_funding: number;
  revenue_36: number;
  cash_36: number;
};

export type ScenarioResults = {
  scenarios: Record<"conservative" | "base" | "optimistic", Projection>;
  sensitivity: { key: string; label: string; low: number; high: number }[];
  months: number;
};

export type ScenarioOut = { id: string; version: number; assumptions: Record<AssumptionKey, Assumption>; results: ScenarioResults; created_at: string };

export type RunDetail = RunSummary & {
  workspace_name: string;
  objective: string | null;
  context: Record<string, string | null>;
  usage: Record<string, number>;
  settings: Record<string, string | number>;
  document_ids: string[];
  started_at: string | null;
  tasks: TaskOut[];
  sources: SourceOut[];
  claims: ClaimOut[];
  findings: { id: string; severity: "high" | "medium" | "low"; code: string; text: string; claim_id: string | null }[];
  missing: { item: string; impact: string; plan: string }[];
  recommendation: Recommendation | null;
  factors: Factor[];
  swot: Record<"strengths" | "weaknesses" | "opportunities" | "threats", Cited[]> | null;
  pestle: { factor: string; rating: number; note: string; claims: string[]; basis: string }[];
  porter: { force: string; level: number; rationale: string; claims: string[]; basis: string }[];
  competitors: { name: string; positioning: string; price_note: string; strengths: string; weaknesses: string; claims: string[]; basis: string }[];
  assumption_suggestions: Partial<Record<AssumptionKey, Assumption>>;
  scenario: ScenarioOut | null;
  scenario_versions: { id: string; version: number; created_at: string }[];
  events: { id: number; at: string; agent: string; message: string }[];
};

export type DocumentOut = { id: string; filename: string; pages: number; size_bytes: number; status: string; uploaded_at: string };

export type Me = {
  id: string;
  email: string | null;
  needs_terms: boolean;
  current_terms_version: string;
  current_privacy_version: string;
  terms_accepted_at: string | null;
};
