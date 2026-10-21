/**
 * Condensed delivery pack shown on the review page. The full versions live in
 * docs/redesign/*.md; keep both in step when either changes.
 */

export type AuditStatus = "real" | "partial" | "simulated" | "broken" | "unused";

export const auditRows: { area: string; files: string; status: AuditStatus; finding: string }[] = [
  { area: "Main report flow", files: "app.py", status: "broken", finding: "Clicking “Generate Custom Intelligence Report” raises AttributeError: AdvancedRAGPipeline has no query_evidence_sources. Reproduced headlessly at commit 00e6826." },
  { area: "Research planner", files: "planner.py", status: "simulated", finding: "Returns the same seven tasks for every question; only the question text is interpolated." },
  { area: "Tavily search", files: "tavily_search.py", status: "unused", finding: "Working HTTP client, never called by app.py. Missing keys and API errors come back as fake search results, so test_tavily.py passes with no key." },
  { area: "Evidence and verification", files: "evidence.py, rag.py", status: "simulated", finding: "Any result with a non-example URL is labelled VERIFIED_FACT. RAG attribution is a constant 0.96 with verified_source=True for every document." },
  { area: "Scores and verdict", files: "scoring.py, recommendations.py", status: "simulated", finding: "Scores are constants (84, 78, 65, 58, 42, 89) for any query. Guardrail “PASSED”, faithfulness 0.96 and relevance 0.94 are hard-coded." },
  { area: "Market, competitors, SWOT", files: "app.py", status: "simulated", finding: "Static text, including a 12.4% CAGR and two named competitors with market shares that have no source." },
  { area: "MBA decision hub", files: "app.py", status: "simulated", finding: "Fully static; shows “AI Guardrail Groundedness 0.98 (Verified)” regardless of input." },
  { area: "Financial scenarios", files: "financials.py", status: "real", finding: "Deterministic Python. Compounds capital rather than modelling revenue and costs; break-even function exists but is unused. Keep and extend." },
  { area: "PDF document RAG", files: "app.py (tab 3)", status: "partial", finding: "Real PyPDF + FAISS + MiniLM retrieval, but no page citations, index lives only in the session, uploads land in a shared data/ folder, and sentence-transformers is missing from requirements." },
  { area: "Live market ticker", files: "api_integration.py", status: "partial", finding: "Real yfinance call; on failure silently shows a fixed 90.5 EUR/INR rate still labelled “Live”." },
  { area: "PDF export", files: "pdf_export.py, src/pdf_generator.py", status: "partial", finding: "Real ReportLab output, but always prints “Guardrail Audit: Passed … 0.96 faithfulness” and writes a fixed filename that concurrent users overwrite." },
  { area: "Gemini research, history, auth", files: "src/*.py, auth.py", status: "unused", finding: "Gemini structured report, Supabase history and a login form exist but are not wired in. research.py returns a mock report on any error. Their packages are missing from requirements." },
  { area: "Tests and CI", files: "tests.py, streamlit-ci.yml", status: "partial", finding: "4 unit tests pass locally; CI only runs py_compile on app.py, so the crash above ships green." },
];

export const preserve = [
  "financials.py: deterministic model, extended into a revenue and cost model",
  "tavily_search.py: client kept, error handling rewritten so failures are errors, not results",
  "PyPDF/FAISS ingestion path, rebuilt with page-level chunks and persistent storage",
  "src/analysis.py Pydantic schemas as the starting point for API contracts",
  "src/pdf_generator.py ReportLab styling as the base for the boardroom export",
  "Supabase auth and history tables, extended with workspaces and row-level security",
];

export const architecture = [
  { layer: "Web app", tech: "Next.js 16, TypeScript, Tailwind 4, shadcn/ui, Motion, ECharts", host: "Vercel", role: "Dashboard, research workspace, evidence inspector, decision workspace, history and comparison" },
  { layer: "Research API", tech: "FastAPI, Pydantic, existing Python modules", host: "Container on Render or Fly.io", role: "Runs, plans, sources, claims, scenarios, exports; streams progress over SSE" },
  { layer: "Workers", tech: "Python job queue (RQ on Redis or Postgres queue)", host: "Same container platform", role: "Planner → researcher (Tavily) → extractor → verifier → critic; PDF ingestion; report rendering" },
  { layer: "Data", tech: "Postgres + pgvector, private object storage", host: "Supabase", role: "Workspaces, runs, sources, page-level chunks, claims, evidence links, assumptions, reports, audit log" },
  { layer: "Identity", tech: "Supabase Auth (JWT) checked in FastAPI, row-level security", host: "Supabase", role: "Owner, editor and viewer roles per workspace" },
  { layer: "Ops", tech: "Structured JSON logs, request IDs, Sentry, rate limits, budget caps", host: "Managed", role: "Per-user and per-workspace limits on runs, Tavily credits and model tokens" },
];

export const evidenceRule =
  "A claim is “supported” only when a stored source extract entails it, checked by a verifier that must quote the span it relied on. Retrieval relevance is recorded separately and never counts as support.";

export const costs = {
  perRun: [
    { item: "Tavily search", basis: "≈14 advanced searches × 2 credits + ≈10 extracts", low: 0.25, high: 0.45 },
    { item: "Language model", basis: "Plan, extract, verify ≈40 claims; ≈300k in / 30k out tokens on a Flash-class model", low: 0.15, high: 0.6 },
    { item: "Embeddings and storage", basis: "≈200 pages of uploaded PDFs", low: 0.01, high: 0.05 },
  ],
  monthly: [
    { item: "Vercel", basis: "Hobby for review, Pro for commercial use", low: 0, high: 20 },
    { item: "Supabase", basis: "Free for build, Pro for production", low: 0, high: 25 },
    { item: "API and worker container", basis: "Two small instances (≈1 GB RAM)", low: 7, high: 50 },
    { item: "Redis, Sentry, logs", basis: "Free tiers at this volume", low: 0, high: 30 },
  ],
  note: "Prices from public pricing pages as of October 2026; confirm before budgeting. A larger frontier model for verification raises the model line roughly 3–10×.",
};

export const milestones = [
  { id: "M0", title: "Safety net", weeks: "0.5", scope: "Tag current Streamlit as v1, rollback runbook, real CI (pytest + lint), failing test that reproduces the crash", done: "CI red on the known crash, green after fix; production untouched" },
  { id: "M1", title: "API foundation", weeks: "1.5", scope: "FastAPI service, Pydantic contracts, Postgres schema, auth middleware, rate limits, logging", done: "Contract tests; auth and rate-limit tests" },
  { id: "M2", title: "Research pipeline", weeks: "2", scope: "Question-specific planner, Tavily collection with retries, caching, dedupe, source store", done: "Recorded run on a real market-entry question with every source persisted" },
  { id: "M3", title: "Evidence and critique", weeks: "2", scope: "Claim extraction, quote-span linking, entailment verifier, critic, missing-data register", done: "Labelled eval set; precision of “supported” ≥ 0.9, unsupported-claim recall reported" },
  { id: "M4", title: "Document RAG", weeks: "1.5", scope: "Page-level ingestion, pgvector retrieval, document and page citations, secure upload", done: "Citation accuracy on a fixture PDF set; malformed-upload tests" },
  { id: "M5", title: "Strategy and finance", weeks: "2", scope: "Competitors, SWOT, PESTLE, Five Forces tied to claims; Python scenario engine; explainable scoring", done: "Golden-value tests for finance; every score shows weights and evidence coverage" },
  { id: "M6", title: "Product UI", weeks: "3", scope: "Approved design: dashboard, workspace, evidence inspector, decision workspace, history and compare", done: "Playwright end-to-end on the acceptance journey" },
  { id: "M7", title: "Boardroom export", weeks: "1", scope: "Report with citations, assumptions, uncertainty and appendix", done: "Export snapshot tests; every figure traceable to a claim or assumption" },
  { id: "M8", title: "Launch", weeks: "1", scope: "Staging, load and security checks, cutover with Streamlit kept as fallback", done: "Recorded acceptance run; rollback rehearsed" },
];
