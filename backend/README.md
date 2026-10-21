# Research API

FastAPI service that runs evidence-checked market-entry research. It sits alongside the Streamlit app and does not change it.

## What happens in a run

1. **Plan.** The model drafts 5–8 research tasks with search queries. The user can edit the plan before anything is searched.
2. **Research.** Tavily searches (cached for 7 days, retried, de-duplicated by URL and content). Failed searches are recorded as failures, never as results. Uploaded PDFs join as sources with page numbers.
3. **Extract.** The model proposes atomic claims from the passages and lists data it could not find.
4. **Verify.** For each claim, the model judges each candidate passage and must copy the exact words it relied on. A quote that is not literally in the passage voids the verdict.
5. **Status.** Fixed rules (`intel/pipeline/status.py`) turn verdicts into Supported / Partially supported / Contradicted / Unsupported / Missing data. Retrieval relevance is stored but never counts as support.
6. **Critique.** Deterministic checks flag unsupported figures, contradictions, single-source and scope-mismatched claims, failed searches, and any number in the recommendation that appears in no claim or assumption.
7. **Analyse and decide.** The model drafts SWOT, PESTLE, Five Forces, competitors and factor scores, each citing claim keys. Citations are validated; uncited competitors are dropped; unevidenced factor scores are held at 50. The verdict comes from fixed thresholds; the model only words it.
8. **Finance.** `intel/finance.py` computes 36-month scenarios and sensitivity in Python. Every assumption is labelled as evidence (with claim key), model estimate, or user input.

## Run locally

```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env            # add TAVILY_API_KEY and GEMINI_API_KEY to run real research
uvicorn intel.main:app --reload # http://localhost:8000/docs
```

With Docker and Postgres: `docker compose up --build` from the repository root (create `backend/.env` first).

## Tests and evaluation

```bash
pytest -q                                   # unit + API tests with fake providers (SQLite)
TEST_DATABASE_URL=postgresql+psycopg://... pytest -q   # same suite on Postgres
GEMINI_API_KEY=... python -m eval.run_eval  # verifier accuracy on 36 hand-labelled pairs, real model
```

`eval/run_eval.py` fails if "supported" precision is below 0.90 and writes results to `eval/results/`.

## Security

- Auth: Supabase JWTs (HS256 secret or JWKS). `AUTH_MODE=dev` gives local sign-in and is refused when `ENVIRONMENT=production`.
- Users must accept the current terms and privacy notice; the version and time are stored.
- Workspace roles (owner, editor, viewer) on every request; other workspaces return 404.
- Per-user rate limits, a stricter limit on costly endpoints, and a monthly run cap per workspace.
- PDF uploads: size and page caps, magic-byte check, encrypted and image-only files rejected, random storage names.
- `GET /me/export` returns all of a user's data; `DELETE /me` erases it, including files on disk.
- JSON logs with request IDs; no document text, prompts or keys are logged.
