# Redesign: AI Strategic Intelligence Platform

Status: **design A approved; product built and tested on this branch; not yet deployed.** Nothing in `main` or the Streamlit deployment has changed.

| Document | What it covers |
| --- | --- |
| [AUDIT.md](AUDIT.md) | What is real, simulated, broken or unused in the current app, with recorded evidence |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Target system: Next.js front end, FastAPI over the existing Python, evidence model, security |
| [COST_ESTIMATE.md](COST_ESTIMATE.md) | Per-run and monthly running costs, and build effort |
| [MILESTONES.md](MILESTONES.md) | Ordered, tested milestones after approval, with the rollback path |
| [../../frontend-preview](../../frontend-preview) | Working design previews (three directions, illustrative data) |
| [DEPLOY.md](DEPLOY.md) | Hosting, environment variables, rollback |
| [evidence/](evidence) | Audit logs, build test results, screenshots, sample export |
| [../../backend](../../backend) | Research API (FastAPI) |
| [../../frontend](../../frontend) | Product web app (design A) and the legal documents |

## Decisions

- 21 Oct 2026: design **A, Executive Intelligence** approved. Legal documents written for a **UK** business.
- Payments are deliberately not built yet; they come after the legal checklist is complete.

## Change log

| Date | Change | Branch |
| --- | --- | --- |
| 2026-10-21 | Audit, architecture, cost estimate, milestones and three design previews added. No production code changed. | `claude/ai-research-analyst-redesign-kg8orh` |
| 2026-10-21 | M0–M7: research API (pipeline, verification, critique, finance, PDF export, auth, roles, limits, consent, data export and erasure), product web app in design A, UK legal pack, CI, deployment guide. 46 backend tests on SQLite and Postgres; browser journey passing. | same |
