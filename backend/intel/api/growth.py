"""Run allowance and refreshes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from intel import growth
from intel.api.deps import audit, expensive, rate_limited
from intel.api.readmodel import run_detail
from intel.config import Settings, get_settings
from intel.db import get_db
from intel.models import Run, User
from intel.security.auth import accepted_user, require_role

router = APIRouter(dependencies=[Depends(rate_limited)])


class ScheduleIn(BaseModel):
    monthly: bool


def _completed(db: Session, user: User, run_id: str) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(404, "Run not found.")
    require_role(db, user, run.workspace_id, "editor")
    if run.status != "completed":
        raise HTTPException(409, "Only a completed run can be refreshed.")
    return run


@router.get("/workspaces/{workspace_id}/usage")
def workspace_usage(
    workspace_id: str,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    require_role(db, user, workspace_id, "viewer")
    return growth.usage(db, workspace_id, settings)


@router.post("/runs/{run_id}/refresh", status_code=201, dependencies=[Depends(expensive)])
def refresh_run(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> dict:
    """Copy the run's question and reviewed plan into a new run. Starting it uses one run."""
    run = _completed(db, user, run_id)
    new = growth.refresh(db, run, user.id)
    audit(db, "run.refreshed", user.id, run.workspace_id, run=new.id, previous=run.id)
    db.commit()
    return run_detail(db, new)


@router.put("/runs/{run_id}/refresh-schedule")
def refresh_schedule(
    run_id: str, body: ScheduleIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    run = _completed(db, user, run_id)
    growth.set_monthly(run, body.monthly)
    audit(db, "run.refresh_schedule", user.id, run.workspace_id, run=run.id, monthly=body.monthly)
    db.commit()
    return {"refresh_monthly": body.monthly}
