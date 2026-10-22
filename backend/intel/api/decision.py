"""Decision workspace endpoints: weights, live verdict and the condition tracker."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from intel.api.deps import audit, rate_limited
from intel.db import get_db
from intel.decision import conditions, current_decision, save_weights, set_condition
from intel.models import Run, User
from intel.security.auth import accepted_user, require_role

router = APIRouter(dependencies=[Depends(rate_limited)])


class WeightsIn(BaseModel):
    weights: dict[str, float]
    save: bool = False


class ConditionIn(BaseModel):
    status: str = Field(pattern="^(open|met|not_met)$")
    note: str = Field(default="", max_length=1000)


def _completed_run(db: Session, user: User, run_id: str, role: str) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(404, "Run not found.")
    require_role(db, user, run.workspace_id, role)
    if run.status != "completed":
        raise HTTPException(409, "The decision workspace opens once the run has completed.")
    return run


@router.post("/runs/{run_id}/decision")
def decide_with_weights(
    run_id: str, body: WeightsIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    """Preview the verdict under different weights; with save=true, keep them for everyone in the workspace."""
    run = _completed_run(db, user, run_id, "editor" if body.save else "viewer")
    try:
        if body.save:
            save_weights(db, run, body.weights, user.id)
            audit(db, "decision.weights_saved", user.id, run.workspace_id, run=run.id)
            db.commit()
            return current_decision(db, run) or {}
        return current_decision(db, run, body.weights) or {}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.delete("/runs/{run_id}/decision/weights")
def reset_weights(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> dict:
    from intel.models import Analysis

    run = _completed_run(db, user, run_id, "editor")
    db.query(Analysis).filter_by(run_id=run.id, kind="weights").delete()
    db.commit()
    return current_decision(db, run) or {}


@router.put("/runs/{run_id}/conditions/{index}")
def update_condition(
    run_id: str, index: int, body: ConditionIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> list[dict]:
    run = _completed_run(db, user, run_id, "editor")
    try:
        items = set_condition(db, run, index, body.status, body.note, user.id)
    except IndexError as exc:
        raise HTTPException(404, "Condition not found.") from exc
    audit(db, "decision.condition_updated", user.id, run.workspace_id, run=run.id, index=index, status=body.status)
    db.commit()
    return items


@router.get("/runs/{run_id}/conditions")
def list_conditions(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> list[dict]:
    return conditions(db, _completed_run(db, user, run_id, "viewer"))
