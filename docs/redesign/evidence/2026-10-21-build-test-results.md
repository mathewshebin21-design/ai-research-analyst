# Build test results, 21 October 2026

Branch `claude/ai-research-analyst-redesign-kg8orh`. All runs below used test doubles for the language model and web search (no API keys were available in the build environment, and Tavily was blocked by its network policy). Everything else was real: FastAPI, SQLAlchemy, SQLite and Postgres 16, PDF parsing, the Python finance engine, ReportLab export, the Next.js production build and Chromium.

| Check | Result |
| --- | --- |
| Backend lint and format (`ruff check`, `ruff format --check`) | Pass |
| Backend tests on SQLite (`pytest`) | 46 passed ([log](2026-10-21-backend-tests-sqlite.txt)) |
| Backend tests on Postgres 16 (`TEST_DATABASE_URL=…`) | 46 passed |
| Alembic `upgrade head` then `downgrade base` on Postgres 16 | Pass |
| Web app typecheck, lint, production build | Pass |
| Browser journey (`npm run e2e`): sign in → accept terms → upload PDF → ask question → edit plan → run → dashboard → change assumption → save version → export PDF → evidence inspector → research workspace → data export → legal page | Pass, 3 of 3 consecutive runs ([JSON](2026-10-21-e2e-results.json)) |

Screens captured during the journey: [plan](screens/01-plan.png), [dashboard](screens/02-dashboard.png), [evidence](screens/03-evidence.png), [workspace](screens/04-workspace.png). [Sample PDF export](sample-report-test-fixture.pdf) (fixture data).

## Defects found by these tests and fixed

1. Passages were not hashable, so verification crashed on the first claim. The run failed cleanly with a message and no invented output, as designed; fixed.
2. A weakly contradicted claim fell through to "Unsupported" instead of "Partially supported"; rule fixed and covered.
3. The PDF listed assumptions as raw keys and fractions ("Cac", "0.6"); now labelled with units.
4. Account deletion removed the record of terms acceptance that the privacy notice promises to keep; now kept under a pseudonym, and the search-cache 7-day retention is enforced by the worker.
5. The same claim could be extracted by several tasks; now de-duplicated across the run.
6. Evidence filter showed a claim the filter had hidden; detail now follows the filter.
7. "Export my data" broke because the client parsed the download as JSON; downloads are now always treated as files.
8. Uploading a PDF straight after page load could be overwritten by the initial document-list fetch; the newest request now wins.

## Not yet demonstrated

A recorded run with **real** Tavily search and a **real** language model, and the verifier's measured precision on the evaluation set. Both need API keys. Run:

```bash
cd backend
TAVILY_API_KEY=... GEMINI_API_KEY=... python -m scripts.acceptance_run "Should <company> launch <product> in <market> in <year>?"
GEMINI_API_KEY=... python -m eval.run_eval
```

The first writes `docs/redesign/evidence/acceptance/<timestamp>/` (run JSON, PDF, summary); the second writes `backend/eval/results/` and fails if "supported" precision is below 0.90.

## Real-data attempts through GitHub Actions (21 October 2026)

The `Acceptance run (real data)` workflow ran with the repository's Tavily and Gemini secrets.

| Run | Reached | Stopped by | Fix |
| --- | --- | --- | --- |
| 1–2 | Planning | Gemini HTTP 404: `gemini-2.5-flash` no longer offered to new accounts | Default model changed to `gemini-3.8-flash`; provider errors now carry Google's reason |
| 3 | Planning (6 tasks), Tavily research, extraction | Gemini HTTP 503 overload after 3 retries | Longer backoff; one failed task or claim no longer fails the run |
| 4 | Planning | Gemini HTTP 503 overload; results not recorded because of a bad path in the commit step | Commit step fixed; planning failures recorded; fallback models supported |
| 5 | Planning, Tavily research, extraction, into verification | Gemini HTTP 429 `GenerateRequestsPerDayPerProjectPerModel-FreeTier`, limit 20 requests a day; retries stacked with the SDK's own retries until the 30-minute limit | SDK retries off; quota exhaustion now stops the run at once with the reason |

Real Tavily search worked in every run that reached it. The remaining blocker is the Gemini key's free-tier quota: a full run needs roughly 30–60 model calls. Enabling billing on the key's Google project removes the daily cap and is also what the privacy notice assumes (no training on customer content).
