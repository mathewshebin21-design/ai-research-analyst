# Implementation milestones

Starts only after a design direction is approved. Each milestone is one pull request with tests, a change-log entry in
`docs/redesign/README.md`, and no merge to `main` without your approval.

## Rollback path

- Before M0 work merges, tag the current production commit `v1-streamlit`.
- Streamlit keeps deploying from `main` and is untouched until M8. New services deploy to separate URLs.
- Database changes are additive migrations with down scripts; nothing the Streamlit app reads is altered.
- Cutover is a DNS or link change, reversible in minutes.

## Status (21 Oct 2026)

| ID | Status |
| --- | --- |
| M0 | Done, except pushing the `v1-streamlit` tag (blocked from the build environment; one command in DEPLOY.md) |
| M1–M5, M7 | Done and tested with test doubles for the model and search |
| M3 evaluation | Dataset and runner done; **real-model precision not yet measured** (needs a Gemini key) |
| M6 | Done; browser journey passes against the real API |
| M8 | Not started: needs hosting accounts, keys, the legal checklist and a recorded real run |

## Milestones

| ID | Title | Scope | Done when | Estimate |
| --- | --- | --- | --- | --- |
| M0 | Safety net | Tag `v1-streamlit`; rollback runbook; CI runs pytest and Ruff; a failing test that reproduces the `query_evidence_sources` crash; remove fabricated metrics and "verified" labels from the Streamlit UI (separate PR, your call) | CI red on the known crash, green after fix | 0.5 wk |
| M1 | API foundation | FastAPI service, Pydantic contracts, Postgres schema and migrations, JWT auth, workspace roles, rate limits, structured logging | Contract tests; auth, RLS and rate-limit tests pass | 1.5 wk |
| M2 | Research pipeline | Question-specific planner; Tavily collection with retries, caching, de-duplication; source store; run progress over SSE | A recorded run on a real market-entry question with every source persisted and inspectable | 2 wk |
| M3 | Evidence and critique | Claim extraction, quote-span linking, entailment verifier, critic, missing-data register; labelled evaluation set (≈150 claim–passage pairs) | Precision of "supported" ≥ 0.90 on the evaluation set; unsupported-claim recall reported; regression test in CI | 2 wk |
| M4 | Document RAG | Page-level ingestion, pgvector retrieval, document and page citations, secure upload pipeline | Citation page accuracy on a fixture PDF set; malformed and oversized upload tests | 1.5 wk |
| M5 | Strategy and finance | Competitor intelligence, SWOT, PESTLE, Five Forces tied to claim IDs; Python scenario engine; explainable weighted scoring | Golden-value finance tests; every score shows weight, value and evidence coverage | 2 wk |
| M6 | Product UI | Approved design: dashboard, research workspace, evidence inspector, decision workspace, history and run comparison | Playwright end-to-end test of the acceptance journey | 3 wk |
| M7 | Boardroom export | PDF with executive summary, recommendation and conditions, scenarios, frameworks, evidence appendix with citations and assumptions | Snapshot tests; every figure in the PDF traceable to a claim or assumption | 1 wk |
| M8 | Launch | Staging, load and security checks, deployment health checks, cutover with Streamlit as fallback | Recorded acceptance run with real evidence; rollback rehearsed | 1 wk |

Total: about 14.5 engineer-weeks.

## Acceptance journey (tested in M6, recorded in M8)

1. Sign in and open a workspace.
2. Enter a market-entry question and receive an editable research plan.
3. Run it and inspect real sources, with extracts, publishers and retrieval dates.
4. Review competitor and financial analysis; every figure links to a claim or an assumption.
5. Change assumptions and see scenarios and the recommendation update.
6. Read why the recommendation was made, what it depends on and what would change it.
7. Export a PDF that carries the same evidence, assumptions and uncertainty.
