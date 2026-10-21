from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from intel.api.deps import audit, rate_limited
from intel.db import get_db
from intel.models import Membership, User, Workspace
from intel.security.auth import accepted_user, require_role

router = APIRouter(prefix="/workspaces", dependencies=[Depends(rate_limited)])


class WorkspaceIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class MemberIn(BaseModel):
    email: str
    role: str = Field(pattern="^(viewer|editor|owner)$")


@router.get("")
def list_workspaces(user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> list[dict]:
    rows = (
        db.query(Workspace, Membership.role)
        .join(Membership)
        .filter(Membership.user_id == user.id)
        .order_by(Workspace.created_at)
    )
    return [{"id": w.id, "name": w.name, "role": role} for w, role in rows]


@router.post("", status_code=201)
def create_workspace(body: WorkspaceIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> dict:
    ws = Workspace(name=body.name.strip(), owner_id=user.id)
    db.add(ws)
    db.flush()
    db.add(Membership(workspace_id=ws.id, user_id=user.id, role="owner"))
    audit(db, "workspace.created", user.id, ws.id)
    db.commit()
    return {"id": ws.id, "name": ws.name, "role": "owner"}


@router.get("/{workspace_id}/members")
def members(workspace_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> list[dict]:
    require_role(db, user, workspace_id, "viewer")
    rows = (
        db.query(Membership, User)
        .join(User, User.id == Membership.user_id)
        .filter(Membership.workspace_id == workspace_id)
    )
    return [{"user_id": u.id, "email": u.email, "role": m.role} for m, u in rows]


@router.post("/{workspace_id}/members", status_code=201)
def add_member(
    workspace_id: str, body: MemberIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    require_role(db, user, workspace_id, "owner")
    target = db.query(User).filter(User.email == body.email.strip().lower()).one_or_none()
    if target is None:
        raise HTTPException(404, "That person needs to sign in once before they can be added.")
    m = db.query(Membership).filter_by(workspace_id=workspace_id, user_id=target.id).one_or_none()
    if m:
        m.role = body.role
    else:
        db.add(Membership(workspace_id=workspace_id, user_id=target.id, role=body.role))
    audit(db, "workspace.member_set", user.id, workspace_id, member=target.id, role=body.role)
    db.commit()
    return {"user_id": target.id, "role": body.role}
