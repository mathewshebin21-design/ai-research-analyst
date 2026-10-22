"""Run allowance, refreshing a run, and what changed since the previous run.

Refreshing copies the reviewed plan into a new run linked by previous_run_id. The comparison is
deterministic: claims from the two runs are matched by word overlap, sources by address, and the
verdict, base case and competitor list are compared field by field.
"""

import re
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from intel.config import Settings
from intel.decision import current_decision
from intel.models import Analysis, Claim, Job, Run, RunEvent, Scenario, Source, Task

REFRESH_AFTER = timedelta(days=30)
CLAIM_MATCH = 0.5
_WORD = re.compile(r"[a-z0-9]+(?:\.[0-9]+)?%?")


# ---- allowance -----------------------------------------------------------------------------


def period(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now or datetime.now(UTC)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = (start + timedelta(days=32)).replace(day=1)
    return start, end


def usage(db: Session, workspace_id: str, settings: Settings) -> dict:
    start, end = period()
    used = (
        db.query(Run)
        .filter(Run.workspace_id == workspace_id, Run.started_at.is_not(None), Run.started_at >= start)
        .count()
    )
    limit = settings.runs_per_workspace_per_month
    return {
        "runs_used": used,
        "limit": limit,
        "remaining": max(0, limit - used),
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
    }


# ---- refresh -------------------------------------------------------------------------------


def refresh(db: Session, run: Run, user_id: str) -> Run:
    """A new run with the same question, context, documents and reviewed plan, ready to start."""
    context = dict(run.context or {})
    context.pop("verdict", None)
    new = Run(
        workspace_id=run.workspace_id,
        created_by=user_id,
        question=run.question,
        context=context,
        document_ids=list(run.document_ids or []),
        previous_run_id=run.id,
        status="planned",
    )
    db.add(new)
    db.flush()
    for t in db.query(Task).filter_by(run_id=run.id).order_by(Task.position):
        db.add(
            Task(
                run_id=new.id,
                key=t.key,
                title=t.title,
                category=t.category,
                rationale=t.rationale,
                queries=list(t.queries),
                position=t.position,
            )
        )
    # Saved decision weights carry over, so a change of verdict comes from the evidence, not the weights.
    weights = db.query(Analysis).filter_by(run_id=run.id, kind="weights").one_or_none()
    if weights is not None:
        db.add(Analysis(run_id=new.id, kind="weights", data=dict(weights.data)))
    # Only the newest run in a chain keeps the monthly schedule.
    if context.get("refresh_monthly"):
        run.context = {**(run.context or {}), "refresh_monthly": False}
    db.add(RunEvent(run_id=new.id, agent="System", message=f"Refresh of the run from {_day(run.finished_at)}"))
    return new


def set_monthly(run: Run, on: bool) -> None:
    run.context = {**(run.context or {}), "refresh_monthly": bool(on)}


def due_refreshes(db: Session, settings: Settings, now: datetime | None = None) -> list[str]:
    """Queue a refresh for each run that asked for one and is a month old. Returns the new run ids.

    Skips a workspace with no runs left this month; it is tried again on the next pass.
    """
    now = now or datetime.now(UTC)
    created = []
    for run in db.query(Run).filter(Run.status == "completed", Run.finished_at.is_not(None)):
        if not (run.context or {}).get("refresh_monthly"):
            continue
        finished = run.finished_at if run.finished_at.tzinfo else run.finished_at.replace(tzinfo=UTC)
        if now - finished < REFRESH_AFTER or db.query(Run).filter_by(previous_run_id=run.id).count():
            continue
        if usage(db, run.workspace_id, settings)["remaining"] <= 0:
            continue
        new = refresh(db, run, run.created_by)
        new.status, new.started_at = "queued", now
        db.add(Job(run_id=new.id))
        db.add(RunEvent(run_id=new.id, agent="System", message="Queued by the monthly refresh"))
        created.append(new.id)
    db.commit()
    return created


# ---- what changed --------------------------------------------------------------------------


def _day(dt: datetime | None) -> str:
    return dt.strftime("%d %b %Y") if dt else "an earlier date"


def _words(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def _similarity(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def _match_claims(old: list[Claim], new: list[Claim]) -> tuple[list[tuple[Claim, Claim]], list[Claim], list[Claim]]:
    pairs = sorted(
        ((_similarity(_words(o.text), _words(n.text)), i, j) for i, o in enumerate(old) for j, n in enumerate(new)),
        reverse=True,
    )
    used_old: set[int] = set()
    used_new: set[int] = set()
    matched = []
    for score, i, j in pairs:
        if score < CLAIM_MATCH:
            break
        if i in used_old or j in used_new:
            continue
        used_old.add(i)
        used_new.add(j)
        matched.append((old[i], new[j]))
    return (
        matched,
        [n for j, n in enumerate(new) if j not in used_new],
        [o for i, o in enumerate(old) if i not in used_old],
    )


def _base(db: Session, run_id: str) -> dict | None:
    """The base case the research itself produced (version 1), not later hand-edited versions."""
    s = db.query(Scenario).filter_by(run_id=run_id).order_by(Scenario.version).first()
    return s.results["scenarios"]["base"] if s else None


def _competitors(db: Session, run_id: str) -> set[str]:
    row = db.query(Analysis).filter_by(run_id=run_id, kind="competitors").one_or_none()
    return {c["name"] for c in (row.data["items"] if row else [])}


def _source_ids(db: Session, run_id: str) -> dict[str, Source]:
    return {(s.url or s.title or s.key): s for s in db.query(Source).filter_by(run_id=run_id) if s.kind != "user"}


def changes(db: Session, run: Run) -> dict | None:
    if not run.previous_run_id or run.status != "completed":
        return None
    prev = db.get(Run, run.previous_run_id)
    if prev is None or prev.status != "completed":
        return None
    by_key = lambda r: sorted(db.query(Claim).filter_by(run_id=r.id), key=lambda c: int(c.key[1:]))  # noqa: E731
    matched, added, dropped = _match_claims(by_key(prev), by_key(run))
    before, after = current_decision(db, prev), current_decision(db, run)
    old_src, new_src = _source_ids(db, prev.id), _source_ids(db, run.id)
    old_base, new_base = _base(db, prev.id), _base(db, run.id)
    old_comp, new_comp = _competitors(db, prev.id), _competitors(db, run.id)
    figures = []
    if old_base and new_base:
        for key, label in (
            ("break_even_month", "Break-even month"),
            ("peak_funding", "Peak funding need"),
            ("cash_36", "Cash at month 36"),
            ("revenue_36", "Revenue over 36 months"),
        ):
            if old_base.get(key) != new_base.get(key):
                figures.append({"key": key, "label": label, "before": old_base.get(key), "after": new_base.get(key)})
    claim_view = lambda c: {"key": c.key, "text": c.text, "status": c.status}  # noqa: E731
    return {
        "previous_run_id": prev.id,
        "previous_finished_at": prev.finished_at.isoformat() if prev.finished_at else None,
        "verdict": {
            "before": before and before["verdict"],
            "after": after and after["verdict"],
            "score_before": before and before["overall"],
            "score_after": after and after["overall"],
        },
        "claims_changed": [
            {"before": claim_view(o), "after": claim_view(n)} for o, n in matched if o.status != n.status
        ],
        "claims_unchanged": sum(1 for o, n in matched if o.status == n.status),
        "claims_new": [claim_view(c) for c in added],
        "claims_dropped": [claim_view(c) for c in dropped],
        "sources_new": [{"key": s.key, "title": s.title, "url": s.url} for k, s in new_src.items() if k not in old_src],
        "sources_dropped": [
            {"key": s.key, "title": s.title, "url": s.url} for k, s in old_src.items() if k not in new_src
        ],
        "figures": figures,
        "competitors_new": sorted(new_comp - old_comp),
        "competitors_dropped": sorted(old_comp - new_comp),
        "method": f"Claims are matched by word overlap of at least {int(CLAIM_MATCH * 100)}%; "
        "sources by web address. Evidence you added yourself is not compared. The base case is each run's "
        "first version, calculated from its own research.",
    }
