# Redesign: AI Strategic Intelligence Platform

Status: **waiting for design approval.** Nothing in `main` or the Streamlit deployment has changed.

| Document | What it covers |
| --- | --- |
| [AUDIT.md](AUDIT.md) | What is real, simulated, broken or unused in the current app, with recorded evidence |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Target system: Next.js front end, FastAPI over the existing Python, evidence model, security |
| [COST_ESTIMATE.md](COST_ESTIMATE.md) | Per-run and monthly running costs, and build effort |
| [MILESTONES.md](MILESTONES.md) | Ordered, tested milestones after approval, with the rollback path |
| [../../frontend-preview](../../frontend-preview) | Working design previews (three directions, illustrative data) |
| [evidence/](evidence) | Logs and scripts behind the audit findings |

## Decision needed

Approve one direction (A Executive Intelligence, B Intelligence Command, C Minimal Intelligence), plus anything to carry over
from the others. Implementation starts at milestone M0 only after that.

## Change log

| Date | Change | Branch |
| --- | --- | --- |
| 2026-10-21 | Audit, architecture, cost estimate, milestones and three design previews added. No production code changed. | `claude/ai-research-analyst-redesign-kg8orh` |
