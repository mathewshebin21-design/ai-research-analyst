"""Decision workspace: the verdict recomputed from current evidence and the user's weights.

The model's original recommendation is kept as written. This module recalculates the score,
confidence and verdict deterministically whenever weights change or claims change status
(for example after the user adds evidence or disputes a claim), so the dashboard never shows a
verdict that the current evidence no longer supports.
"""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from intel.models import Analysis, Claim, Finding, Run
from intel.pipeline import analyst
from intel.pipeline.status import coverage_weight

CURRENCIES = {"GBP": "£", "EUR": "€", "USD": "$", "INR": "₹"}
DEFAULT_CURRENCY = "GBP"
CONDITION_STATES = ("open", "met", "not_met")


def currency_of(run: Run) -> str:
    code = (run.context or {}).get("currency") or "EUR"  # runs created before currencies were added used euros
    return code if code in CURRENCIES else DEFAULT_CURRENCY


def _analysis(db: Session, run_id: str, kind: str) -> Analysis | None:
    return db.query(Analysis).filter_by(run_id=run_id, kind=kind).one_or_none()


def _upsert(db: Session, run_id: str, kind: str, data: dict) -> None:
    row = _analysis(db, run_id, kind)
    if row is None:
        db.add(Analysis(run_id=run_id, kind=kind, data=data))
    else:
        row.data = data


def default_weights() -> dict[str, float]:
    return {k: w for k, (_, w) in analyst.FACTORS.items()}


def normalise(weights: dict[str, float]) -> dict[str, float]:
    clean = {k: max(0.0, float(weights.get(k, 0.0))) for k in analyst.FACTORS}
    total = sum(clean.values())
    if total <= 0:
        raise ValueError("At least one factor needs a weight above zero.")
    return {k: round(v / total, 4) for k, v in clean.items()}


def saved_weights(db: Session, run: Run) -> dict[str, float]:
    row = _analysis(db, run.id, "weights")
    return row.data["weights"] if row else default_weights()


def save_weights(db: Session, run: Run, weights: dict[str, float], user_id: str) -> dict[str, float]:
    w = normalise(weights)
    _upsert(db, run.id, "weights", {"weights": w, "updated_by": user_id, "updated_at": datetime.now(UTC).isoformat()})
    return w


def current_decision(db: Session, run: Run, weights: dict[str, float] | None = None) -> dict | None:
    factors_row = _analysis(db, run.id, "factors")
    rec_row = _analysis(db, run.id, "recommendation")
    if factors_row is None or rec_row is None:
        return None
    w = normalise(weights) if weights is not None else saved_weights(db, run)
    claims = {c.key: c for c in db.query(Claim).filter_by(run_id=run.id)}

    def effective(c: Claim) -> str:
        return "disputed" if c.user_flag == "disputed" else c.status

    factors = []
    for f in factors_row.data["items"]:
        cited = [claims[k] for k in f["claims"] if k in claims]
        statuses = [effective(c) for c in cited]
        coverage = round(sum(coverage_weight(s) for s in statuses) / len(statuses), 3) if statuses else 0.0
        evidenced = any(s in ("supported", "partial") for s in statuses)
        model_score = f.get("model_score")
        factors.append(
            {
                **f,
                "weight": w[f["key"]],
                "coverage": coverage,
                "score": model_score if evidenced and model_score is not None else 50,
                "basis": "evidenced" if evidenced else ("unsupported" if statuses else "no_evidence"),
            }
        )
    high = db.query(Finding).filter_by(run_id=run.id, severity="high").count()
    scores = analyst.score(factors, high)
    decision = analyst.decide(scores, factors)
    original = rec_row.data
    return {
        **scores,
        **decision,
        "weights": w,
        "factors": factors,
        "original_verdict": original.get("verdict"),
        "original_overall": original.get("overall"),
        "changed": decision["verdict"] != original.get("verdict") or scores["overall"] != original.get("overall"),
        "custom_weights": _analysis(db, run.id, "weights") is not None,
    }


def conditions(db: Session, run: Run) -> list[dict]:
    row = _analysis(db, run.id, "conditions")
    if row:
        return row.data["items"]
    rec = _analysis(db, run.id, "recommendation")
    texts = rec.data.get("conditions", []) if rec else []
    return [{"text": t, "status": "open", "note": "", "updated_at": None, "updated_by": None} for t in texts]


def set_condition(db: Session, run: Run, index: int, status: str, note: str, user_id: str) -> list[dict]:
    if status not in CONDITION_STATES:
        raise ValueError("Status must be open, met or not_met.")
    items = conditions(db, run)
    if not 0 <= index < len(items):
        raise IndexError("No such condition.")
    items = [dict(i) for i in items]
    items[index].update(
        status=status, note=note.strip()[:1000], updated_by=user_id, updated_at=datetime.now(UTC).isoformat()
    )
    _upsert(db, run.id, "conditions", {"items": items})
    return items
