# Repository audit

Audited commit: `00e6826` ("Fix indentation and finalize Tavily search and evidence tracking modules"), 21 Oct 2026.

Method: every file was read; the existing tests were run; the Streamlit app was executed headlessly with
`streamlit.testing.v1.AppTest` and the main button was clicked. The deployed Streamlit URL could not be reached from the
build environment (outbound host blocked), so all findings come from the code and the local run, not from the live site.

## Summary

The app looks like a multi-agent research platform, but almost every number on screen is a constant. The only working
research-adjacent features are the uploaded-PDF similarity search and the deterministic financial calculation. The main
"Generate Custom Intelligence Report" flow crashes before it renders the report.

## Recorded evidence

| Check | Result | Log |
| --- | --- | --- |
| `pytest tests.py test_tavily.py` | 4 passed. `test_tavily` passes without a `TAVILY_API_KEY` because the missing-key error is returned as a search result. | [evidence/2026-10-21-existing-tests.log](evidence/2026-10-21-existing-tests.log) |
| Headless run, click **Generate Custom Intelligence Report** | `AttributeError: type object 'AdvancedRAGPipeline' has no attribute 'query_evidence_sources'` at `app.py:148` | [evidence/2026-10-21-apptest-generate-click.log](evidence/2026-10-21-apptest-generate-click.log) |
| Live EUR/INR widget with Yahoo unreachable | Shows `₹90.50` labelled "Live EUR/INR Exchange Rate" (hard-coded fallback in `api_integration.py`) | same log (yfinance errors) |

Reproduce: `python docs/redesign/evidence/apptest_generate_click.py .` with `streamlit pandas reportlab yfinance` installed.

## Actual versus simulated

| Area | Files | Status | Finding |
| --- | --- | --- | --- |
| Main report flow | `app.py` | Broken | Crashes on click (above). Even past the crash, `rec` is undefined when the "Strategic Recommendations" module is unticked, and the PDF step would raise `NameError`. |
| Research planner | `planner.py` | Simulated | Same seven tasks for every question; only the question text is interpolated. |
| Tavily search | `tavily_search.py` | Real client, unused | `app.py` imports `WebSearchModule` but never calls it. Errors and a missing key are returned as fake results (`"title": "API Key Missing"`). |
| Evidence classifier | `evidence.py` | Misleading | Any result whose URL is not `#` or `example` is labelled `VERIFIED_FACT`. Relevance score defaults to 0.85 when absent. |
| RAG attribution | `rag.py` | Simulated | `attribution_score` is always 0.96 and `verified_source` always `True`. No retrieval happens. |
| Strategic scores | `scoring.py` | Simulated | Returns 84, 78, 65, 58, 42, 89 for any query. |
| Recommendation and guardrails | `recommendations.py` | Simulated | Verdict is a rule over the constant scores. "PASSED (No ungrounded claims detected)", faithfulness 0.96 and relevance 0.94 are literals. |
| Market, competitors, SWOT | `app.py` | Simulated | Static strings, including "12.4% CAGR" and two competitors with market shares that have no source. |
| MBA decision hub | `app.py` | Simulated | Static page. "AI Guardrail Groundedness 0.98 (Verified)" is a literal. |
| Financial scenarios | `financials.py` | Real | Deterministic. Compounds starting capital by a growth rate; it is not a revenue/cost model. `calculate_break_even` is correct but unused. |
| Uploaded PDF RAG | `app.py` tab 3 | Partly real | PyPDF → 500-char chunks → MiniLM → FAISS similarity search works in principle. No page numbers are shown, the index lives only in the browser session, uploads are written to a shared `data/` folder under the client's filename, and `sentence-transformers` (needed by `HuggingFaceEmbeddings`) is not in `requirements.txt`. Not executed here because `torch` is too large for the audit environment. |
| Live market data | `api_integration.py` | Partly real | Real yfinance call. Failure silently returns 90.5 while the UI still says "Live". |
| PDF export | `pdf_export.py` | Partly real | ReportLab output works, but always prints "AI Guardrail Audit: Passed (… 0.96 faithfulness score)". Writes a fixed filename in the working directory, so concurrent users overwrite each other's reports. |
| Gemini research report | `src/research.py` | Unused | Structured-output call exists but is not wired in. On any exception it returns a mock report with an invented 14.2% CAGR. Model id `gemini-3.5-flash` should be verified. |
| Gemini document Q&A | `src/rag.py` | Unused | Truncates the document to 15,000 characters; no citations. |
| History store | `src/database.py` | Unused | Supabase insert/select for a `history` table. |
| Authentication | `auth.py`, `src/auth.py` | Unused | Supabase email/password form, never called. The app is fully public. |
| Critic, evaluation, score explainer | `critic.py`, `evaluation.py`, `scoring_guardrails.py` | Unused | Arithmetic is fine, but they consume the meaningless `verified` flag from `evidence.py`. |
| Dependencies | `requirements.txt` | Incomplete | Missing `supabase`, `google-genai`, `pypdf`, `pydantic`, `python-dotenv`, `sentence-transformers`, `requests` (transitive today). |
| CI | `.github/workflows/streamlit-ci.yml` | Weak | Runs `py_compile app.py` only, so the crash above passes CI. |
| Secrets | `.streamlit/secrets.toml` | OK for now | Committed with a placeholder value only. Should be git-ignored before real keys exist. |

## Claims the product must stop making

1. "Verified", "VERIFIED_FACT", "Passed QA audit" or "No ungrounded claims detected" where no verification ran.
2. Faithfulness, relevance and groundedness scores that are constants.
3. "Live" data that is a fallback constant.
4. Market figures (12.4% CAGR, 14.2% CAGR, competitor shares) with no source.

## Preserve and extend

- `financials.py`: keep the deterministic approach; extend into a revenue, cost and cash model (see ARCHITECTURE.md).
- `tavily_search.py`: keep the client; failures become typed errors, never results.
- PDF ingestion: keep PyPDF/FAISS ideas; rebuild with page-level chunks stored in Postgres/pgvector.
- `src/analysis.py`: Pydantic models as the seed of the API contracts.
- `src/pdf_generator.py`: ReportLab styling as the base of the boardroom export.
- Supabase auth and history: extend with workspaces and row-level security.
