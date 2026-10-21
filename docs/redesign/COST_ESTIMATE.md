# Cost estimate

Prices are from public pricing pages and third-party summaries as of October 2026. Confirm them before budgeting.

> **Model change, 21 Oct 2026:** Google no longer offers `gemini-2.5-flash` to new API accounts, so the default model is now `gemini-3.8-flash`. The language-model line below was estimated at 2.5 Flash prices; check the 3.8 Flash price on Google's pricing page and the token counts recorded by the first real run (`usage` in the run JSON).

## Per research run

Assumes one market-entry question: about 7 tasks, 14 advanced searches, 10 page extracts, about 40 claims verified
against 2–3 passages each, and 200 pages of uploaded PDFs.

| Item | Basis | Low | High |
| --- | --- | --- | --- |
| Tavily | Advanced search = 2 credits; ≈38–55 credits at $0.005–0.008 per credit | $0.25 | $0.45 |
| Language model | ≈300k input / 30k output tokens. Gemini 2.5 Flash-class at $0.30 / $2.50 per million tokens ≈ $0.17; headroom for retries and a stronger verifier on hard claims | $0.15 | $0.60 |
| Embeddings and storage | ≈200 pages | $0.01 | $0.05 |
| **Total per run** | | **$0.41** | **$1.10** |

Using a frontier-class model for every verification step would raise the model line by roughly 3–10×.

## Fixed monthly

| Item | Basis | Low | High |
| --- | --- | --- | --- |
| Vercel | Hobby while in review; Pro for commercial use | $0 | $20 |
| Supabase | Free during build; Pro in production | $0 | $25 |
| API and worker containers | Two small instances, about 1 GB RAM each, on Render or Fly.io | $7 | $50 |
| Redis, Sentry, log retention | Free tiers cover this volume | $0 | $30 |
| **Total per month** | | **$7** | **$125** |

Embeddings come from a hosted API rather than a local `torch` model so the containers stay small.

## Examples

| Usage | Monthly total |
| --- | --- |
| 50 runs (personal or portfolio use) | about $30–$180 |
| 300 runs (small team) | about $130–$455 |

## Build effort

About 14.5 engineer-weeks across milestones M0–M8 (see MILESTONES.md). At typical contractor rates that is the dominant
cost; if you build it yourself with an AI coding assistant, budget the subscription plus your review time per milestone.

## Sources

- Tavily credit costs and plans: <https://docs.tavily.com/documentation/api-credits>, summarised at <https://coldiq.com/blog/tavily-pricing>
- Gemini 2.5 Flash token prices: <https://ai.google.dev/gemini-api/docs/pricing>, summarised at <https://anotherwrapper.com/llm-pricing/gemini-2.5-flash>
- Supabase plans: <https://supabase.com/pricing>, summarised at <https://makerkit.dev/blog/saas/supabase-pricing>
- Render and Vercel figures are from their pricing pages and were not re-checked for this estimate.
