"""Account, consent and data-subject rights (UK GDPR access and erasure)."""

import hashlib
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from intel.api.deps import audit, expensive, rate_limited
from intel.api.readmodel import iso, run_detail
from intel.config import Settings, get_settings
from intel.db import get_db
from intel.models import AuditLog, Document, Membership, Report, Run, User, Workspace
from intel.rag.pdf import storage_path
from intel.security.auth import current_user, mint_dev_token

router = APIRouter(dependencies=[Depends(rate_limited)])


class AcceptTerms(BaseModel):
    terms_version: str
    privacy_version: str


@router.get("/me")
def me(user: User = Depends(current_user), settings: Settings = Depends(get_settings)) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "terms_version": user.terms_version,
        "terms_accepted_at": iso(user.terms_accepted_at),
        "current_terms_version": settings.terms_version,
        "current_privacy_version": settings.privacy_version,
        "needs_terms": user.terms_version != settings.terms_version or user.privacy_version != settings.privacy_version,
    }


@router.post("/me/accept-terms")
def accept_terms(
    body: AcceptTerms,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    if body.terms_version != settings.terms_version or body.privacy_version != settings.privacy_version:
        raise HTTPException(409, "The terms have changed. Reload the page and review the current version.")
    user.terms_version, user.privacy_version, user.terms_accepted_at = (
        body.terms_version,
        body.privacy_version,
        datetime.now(UTC),
    )
    db.merge(user)
    audit(db, "terms.accepted", user.id, terms=body.terms_version, privacy=body.privacy_version)
    db.commit()
    return {"ok": True}


@router.get("/me/export", dependencies=[Depends(expensive)])
def export_data(user: User = Depends(current_user), db: Session = Depends(get_db)) -> JSONResponse:
    """Everything stored about the user, as JSON (right of access / portability)."""
    workspace_ids = [m.workspace_id for m in db.query(Membership).filter_by(user_id=user.id)]
    payload = {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": iso(user.created_at),
            "terms_version": user.terms_version,
            "terms_accepted_at": iso(user.terms_accepted_at),
        },
        "workspaces": [],
        "activity": [
            {"at": iso(a.at), "action": a.action, "detail": a.detail}
            for a in db.query(AuditLog).filter_by(user_id=user.id).order_by(AuditLog.id)
        ],
    }
    for wid in workspace_ids:
        ws = db.get(Workspace, wid)
        if ws is None:
            continue
        payload["workspaces"].append(
            {
                "id": ws.id,
                "name": ws.name,
                "documents": [
                    {"id": d.id, "filename": d.filename, "pages": d.pages, "uploaded_at": iso(d.created_at)}
                    for d in db.query(Document).filter_by(workspace_id=wid, uploaded_by=user.id)
                ],
                "runs": [run_detail(db, r) for r in db.query(Run).filter_by(workspace_id=wid, created_by=user.id)],
            }
        )
    audit(db, "account.exported", user.id)
    db.commit()
    return JSONResponse(payload, headers={"Content-Disposition": 'attachment; filename="my-data.json"'})


@router.delete("/me")
def delete_account(
    user: User = Depends(current_user), db: Session = Depends(get_db), settings: Settings = Depends(get_settings)
) -> dict:
    """Erase the user, the workspaces they own and the files in them. Shared workspaces they only joined are kept."""
    owned = db.query(Workspace).filter_by(owner_id=user.id).all()
    files = []
    for ws in owned:
        files += [d.storage_key for d in db.query(Document).filter_by(workspace_id=ws.id)]
        run_ids = [r.id for r in db.query(Run).filter_by(workspace_id=ws.id)]
        files += [r.storage_key for r in db.query(Report).filter(Report.run_id.in_(run_ids))] if run_ids else []
    files += [d.storage_key for d in db.query(Document).filter_by(uploaded_by=user.id)]
    for ws in owned:
        db.delete(ws)
    db.flush()
    # Keep consent records (6 years, see privacy notice) under a pseudonym; drop all other activity.
    pseudonym = "deleted:" + hashlib.sha256(user.id.encode()).hexdigest()[:16]
    db.query(AuditLog).filter(AuditLog.user_id == user.id, AuditLog.action.like("terms.%")).update(
        {AuditLog.user_id: pseudonym}, synchronize_session=False
    )
    db.query(AuditLog).filter_by(user_id=user.id).delete()
    db.delete(db.merge(user))
    db.add(AuditLog(action="account.deleted", user_id=pseudonym, detail={"workspaces": len(owned)}))
    db.commit()
    for key in set(files):
        try:
            storage_path(settings.storage_dir, key).unlink(missing_ok=True)
        except ValueError:
            pass
    return {"deleted": True}


class DevLogin(BaseModel):
    email: EmailStr


@router.post("/dev/token")
def dev_token(body: DevLogin, settings: Settings = Depends(get_settings)) -> dict:
    """Local development sign-in. Disabled unless AUTH_MODE=dev outside production."""
    if settings.auth_mode != "dev" or settings.environment == "production":
        raise HTTPException(404, "Not found")
    user_id = "dev-" + body.email.lower().replace("@", "-at-")[:56]
    return {"access_token": mint_dev_token(user_id, body.email, settings), "token_type": "bearer"}
