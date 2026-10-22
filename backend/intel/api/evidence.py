"""User-supplied evidence and disputes on individual claims."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from intel.api.deps import audit, expensive, rate_limited
from intel.api.readmodel import run_detail
from intel.config import Settings, get_settings
from intel.db import get_db
from intel.models import Claim, Run, User
from intel.providers import factory
from intel.providers.errors import ProviderError
from intel.security.auth import accepted_user, require_role
from intel.user_evidence import EvidenceRejected, add_evidence, clear_dispute, dispute

router = APIRouter(dependencies=[Depends(rate_limited)])


class EvidenceIn(BaseModel):
    url: str | None = Field(default=None, max_length=2000)
    text: str | None = Field(default=None, max_length=20000)
    title: str | None = Field(default=None, max_length=200)
    document_id: str | None = None

    @model_validator(mode="after")
    def one_kind(self):
        if sum(bool(v) for v in (self.url, self.text, self.document_id)) != 1:
            raise ValueError("Give exactly one of: a link, pasted text, or a document.")
        return self


class DisputeIn(BaseModel):
    note: str = Field(default="", max_length=1000)


def _claim(db: Session, user: User, run_id: str, claim_id: str) -> tuple[Run, Claim]:
    run = db.get(Run, run_id)
    claim = db.get(Claim, claim_id)
    if run is None or claim is None or claim.run_id != run.id:
        raise HTTPException(404, "Claim not found.")
    require_role(db, user, run.workspace_id, "editor")
    if run.status != "completed":
        raise HTTPException(409, "Evidence can be added once the run has completed.")
    return run, claim


@router.post("/runs/{run_id}/claims/{claim_id}/evidence", dependencies=[Depends(expensive)])
def add_claim_evidence(
    run_id: str,
    claim_id: str,
    body: EvidenceIn,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    run, claim = _claim(db, user, run_id, claim_id)
    try:
        llm = factory.get_providers(settings).llm
        result = add_evidence(
            db,
            run,
            claim,
            llm,
            settings,
            user.email or "a user",
            url=body.url,
            text=body.text,
            title=body.title,
            document_id=body.document_id,
        )
    except EvidenceRejected as exc:
        db.rollback()
        raise HTTPException(422, str(exc)) from exc
    except ProviderError as exc:
        db.rollback()
        raise HTTPException(503, str(exc)) from exc
    audit(
        db,
        "claim.evidence_added",
        user.id,
        run.workspace_id,
        run=run.id,
        claim=claim.key,
        kind=next(k for k in ("url", "text", "document_id") if getattr(body, k)),
    )
    db.commit()
    return {"result": result, "run": run_detail(db, run)}


@router.post("/runs/{run_id}/claims/{claim_id}/dispute")
def dispute_claim(
    run_id: str, claim_id: str, body: DisputeIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    run, claim = _claim(db, user, run_id, claim_id)
    dispute(db, run, claim, body.note, user.email or "a user")
    audit(db, "claim.disputed", user.id, run.workspace_id, run=run.id, claim=claim.key)
    db.commit()
    return run_detail(db, run)


@router.delete("/runs/{run_id}/claims/{claim_id}/dispute")
def undispute_claim(
    run_id: str, claim_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    run, claim = _claim(db, user, run_id, claim_id)
    clear_dispute(db, run, claim, user.email or "a user")
    audit(db, "claim.dispute_cleared", user.id, run.workspace_id, run=run.id, claim=claim.key)
    db.commit()
    return run_detail(db, run)
