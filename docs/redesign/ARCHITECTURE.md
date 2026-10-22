# Proposed architecture

Principle: keep the Python research code, put a typed API in front of it, and build the new interface against that API.
The Streamlit app keeps running from `main` until cutover and is the rollback path.

```
Browser ── Next.js 16 (Vercel) ──HTTPS + JWT──▶ FastAPI (container) ──▶ Postgres + pgvector (Supabase)
                                    ▲  SSE progress        │                 Private object storage
                                    │                      ▼
                                    └──────────── Worker queue ──▶ Tavily, language model, ReportLab
```

## Components

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Web app | Next.js 16 App Router, TypeScript, Tailwind 4, shadcn/ui (Radix), Motion, ECharts | Dashboard, research workspace, evidence inspector, decision workspace, history and comparison. No business logic: every figure comes from the API. |
| API | FastAPI, Pydantic v2 | Auth check, rate limits, validation, run orchestration, read models for the UI, report download. |
| Workers | Python, RQ on Redis (or a Postgres-backed queue) | Long-running research runs, PDF ingestion, report rendering. Progress streamed to the UI over Server-Sent Events. |
| Data | Postgres 16 + pgvector on Supabase | All durable state (schema below). |
| Files | Supabase Storage, private bucket | Uploaded PDFs and generated reports; served only through short-lived signed URLs. |
| Identity | Supabase Auth (JWT) verified in FastAPI; Postgres row-level security | Workspace roles: owner, editor, viewer. |

ECharts is used instead of Plotly in the web app: it covers every chart in the previews (lines, tornado, radar, heatmap,
scatter, force graph) at a fraction of Plotly's bundle size. Plotly remains an option for the PDF export if server-side
rendering of charts is needed there.

## Research pipeline

1. **Planner** turns the question into 5–9 tasks, each with search queries and the framework it feeds. Output is
   schema-validated; the user can edit the plan before it runs.
2. **Researcher** runs Tavily searches per task with retries, timeouts, result caching (keyed on query + date) and URL
   de-duplication. Every result is stored as a `source` with retrieval time, publisher, tier and raw content hash.
   Failures are recorded as failed searches, never as results.
3. **Extractor** proposes atomic claims from sources and uploaded documents, each pointing at candidate passages.
4. **Verifier** decides, per claim and passage, whether the passage *entails*, *contradicts* or is merely *related to*
   the claim, and must return the exact quoted span it relied on. The span is checked to be a literal substring of the
   stored passage; if it is not, the verdict is discarded.
5. **Critic** reviews the draft: claims without support, single-source claims, geography or date mismatches, numbers that
   appear in the draft but in no source, and contradictions. Findings are stored and shown, not silently fixed.
6. **Analyst** builds market, competitor, SWOT, PESTLE and Five Forces views where every entry cites claim IDs.
7. **Scorer and finance engine** (deterministic Python) compute scores and scenarios from claims and explicit assumptions.

### Evidence rule

A claim's status is derived, never asserted by a model:

| Status | Rule |
| --- | --- |
| Supported | Entailment ≥ 0.70 on a tier-A source, or on two independent sources |
| Partially supported | Entailment ≥ 0.40, or support from a single tier-B/C source, or a scope mismatch (geography, segment, date) |
| Contradicted | A passage contradicts the claim with ≥ 0.70 confidence and nothing of equal tier supports it |
| Unsupported | Relevant passages retrieved, none entails the claim |
| Missing data | No relevant passage; the figure, if used, becomes a labelled assumption |

Retrieval relevance is stored and displayed but never changes a status. Thresholds are calibrated on the evaluation set
(M3) and versioned with each run.

## Data model (core tables)

`workspaces`, `memberships(role)`, `runs(question, status, plan_version, cost)`, `tasks`, `searches(query, status, error)`,
`sources(url, publisher, tier, retrieved_at, content_hash)`, `documents(storage_key, sha256, pages)`,
`chunks(document_id|source_id, page, text, embedding)`, `claims(task_id, text, status, status_reason)`,
`evidence_links(claim_id, chunk_id, quote_start, quote_end, relation, entailment, relevance, verifier_version)`,
`critique_findings`, `assumptions(key, value, unit, origin: user|source|default, claim_id?)`, `scenarios`,
`scores(factor, weight, value, coverage)`, `reports(storage_key, run_id, created_by)`, `audit_log`.

Runs are immutable once complete; changing an assumption creates a new scenario version, so comparisons and exports are
reproducible.

## Financial model

Python, pure functions, no model calls. Inputs are assumptions with provenance. Outputs: monthly revenue, gross profit,
contribution, EBITDA, cumulative cash, break-even and payback months, peak funding, and ±20% sensitivity per driver for
conservative, base and optimistic cases. Golden-value tests pin results. The preview's TypeScript mirror
(`frontend-preview/src/lib/finance.ts`) exists only so the design can respond to sliders without a backend.

## Security and operations

| Concern | Measure |
| --- | --- |
| Authentication | Supabase Auth; JWT verified on every API request (issuer, audience, expiry). |
| Authorization | Workspace role checks in the API plus row-level security in Postgres as a second layer. |
| Rate limiting | Per user and per IP on the API (Redis token bucket); per-workspace monthly caps on runs, Tavily credits and model spend, enforced before a run starts. |
| Document handling | PDF only; size cap (25 MB) and page cap; magic-byte check; parsed in the worker, never in the API process; stored under a random key in a private bucket; filenames never used as paths; optional ClamAV scan. |
| Secrets | Host secret stores only; no keys in the repo; `.streamlit/secrets.toml` git-ignored. |
| Logging | Structured JSON logs with request and run IDs; no document text or API keys in logs; Sentry for exceptions. |
| CI | Ruff, mypy, pytest (unit, contract, golden finance, evaluation regression) for Python; ESLint, TypeScript, Playwright for the web app. |
| Deployment checks | Health and readiness endpoints, migration check, smoke test on staging, then promote. |

## Language model

The current code uses Gemini. The pipeline calls the model through one adapter so the provider can be chosen per step
(a Flash-class model for extraction, a stronger model for verification if the evaluation set shows it is needed). The
choice is made on M3 evaluation results, not up front.

## As built (differences from the plan above)

| Planned | Built | Why |
| --- | --- | --- |
| pgvector embeddings | BM25 lexical retrieval over page-level passages | No dependency or extra cost; deterministic; good enough for candidate selection because the verifier, not retrieval, decides support. Embeddings can be added behind the same `PassageIndex`. |
| RQ on Redis | Database-backed job queue (`jobs` table, `SKIP LOCKED` on Postgres), worker in-process or separate | One fewer service to run and pay for. |
| Redis rate limiter | In-process token bucket per user | Correct for a single API instance; swap for Redis or proxy limits when scaling out. |
| Supabase Storage | Files on the API's persistent disk under random names | Simpler first deployment; the storage functions are isolated in `intel/rag/pdf.py`. |
| Factor scores from the model | Scores from the model, but held at 50 unless they cite supported or partial claims | Prevents confident scores with no evidence. |
| (not planned) Decision workspace | `intel/decision.py` recomputes the score and verdict from current claim statuses and the user's weights | The model's recommendation stays as written; the dashboard shows when evidence or weights now give a different verdict. |
| (not planned) User evidence | `intel/user_evidence.py`: SSRF-safe fetch (public addresses only, 3 MB, 3 redirects), then the same verifier and status rules; user sources are tier B | One user source can make a claim at most partially supported. |
| (not planned) Share links | `share_links` table stores a SHA-256 of the token; `/shared/{token}` returns the report without activity, costs, members or settings | The token is shown once; turning a link off takes effect at once. |
| (not planned) Refresh and changes | `intel/growth.py`: refresh copies the plan and saved weights; the comparison matches claims by word overlap and sources by address; monthly refresh is queued by the worker | Deterministic, explainable comparison; no model call. |
| (not planned) Sample report | `frontend/public/sample-run.json`, shown at `/sample` without the API; replace with `python -m intel.export_sample RUN_ID "note"` | Lets visitors see a report before signing up. The current file comes from test fixtures and says so. |
