"""Read-only share links and the slide-deck export."""

import hashlib
import secrets
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from intel.api.deps import audit, expensive, limiter, rate_limited
from intel.api.readmodel import iso, run_detail
from intel.db import get_db
from intel.models import Run, ShareLink, User
from intel.report_pptx import build_deck
from intel.security.auth import accepted_user, require_role

router = APIRouter(dependencies=[Depends(rate_limited)])
public = APIRouter()


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _run(db: Session, user: User, run_id: str, role: str) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(404, "Run not found.")
    require_role(db, user, run.workspace_id, role)
    if run.status != "completed":
        raise HTTPException(409, "Only completed runs can be shared or exported.")
    return run


def public_view(db: Session, run: Run) -> dict:
    """What a link holder sees: the report, without usage, activity, members or internal settings."""
    d = run_detail(db, run)
    searches = (d.get("usage") or {}).get("searches", 0)
    for key in ("events", "usage", "document_ids", "context", "error", "stage", "workspace_id"):
        d.pop(key, None)
    d["usage"] = {"searches": searches}  # only the count the research tab shows; no costs or tokens
    d["conditions"] = [{k: v for k, v in c.items() if k != "updated_by"} for c in d.get("conditions", [])]
    d["shared"] = True
    return d


@router.post("/runs/{run_id}/shares", status_code=201)
def create_share(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> dict:
    run = _run(db, user, run_id, "editor")
    token = secrets.token_urlsafe(24)
    link = ShareLink(run_id=run.id, token_hash=_hash(token), created_by=user.id)
    db.add(link)
    audit(db, "run.shared", user.id, run.workspace_id, run=run.id, share=link.id)
    db.commit()
    # The token is shown once; only its hash is stored.
    return {"id": link.id, "token": token, "created_at": iso(link.created_at)}


@router.get("/runs/{run_id}/shares")
def list_shares(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> list[dict]:
    run = _run(db, user, run_id, "viewer")
    rows = db.query(ShareLink).filter_by(run_id=run.id, revoked_at=None).order_by(ShareLink.created_at)
    return [{"id": s.id, "created_at": iso(s.created_at)} for s in rows]


@router.delete("/runs/{run_id}/shares/{share_id}")
def revoke_share(
    run_id: str, share_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    run = _run(db, user, run_id, "editor")
    link = db.get(ShareLink, share_id)
    if link is None or link.run_id != run.id:
        raise HTTPException(404, "Link not found.")
    link.revoked_at = datetime.now(UTC)
    audit(db, "run.share_revoked", user.id, run.workspace_id, run=run.id, share=link.id)
    db.commit()
    return {"revoked": True}


@public.get("/shared/{token}")
def view_shared(token: str, request: Request, db: Session = Depends(get_db)) -> dict:
    limiter("public", 30).check(request)
    link = db.query(ShareLink).filter_by(token_hash=_hash(token)).one_or_none()
    if link is None or link.revoked_at is not None:
        raise HTTPException(404, "This link is not valid or has been turned off.")
    run = db.get(Run, link.run_id)
    if run is None or run.status != "completed":
        raise HTTPException(404, "This link is not valid or has been turned off.")
    return public_view(db, run)


@router.post("/runs/{run_id}/slides", dependencies=[Depends(expensive)])
def export_slides(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> Response:
    run = _run(db, user, run_id, "viewer")
    deck = build_deck(run_detail(db, run))
    audit(db, "report.slides_exported", user.id, run.workspace_id, run=run.id)
    db.commit()
    return Response(
        deck,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="market-entry-{run.id[:8]}.pptx"'},
    )
