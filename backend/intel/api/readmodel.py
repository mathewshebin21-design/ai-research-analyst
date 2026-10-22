"""Read models returned to the UI and used for exports."""

from sqlalchemy.orm import Session

from intel.decision import CURRENCIES, conditions, currency_of, current_decision
from intel.growth import changes
from intel.models import (
    Analysis,
    Claim,
    EvidenceLink,
    Finding,
    MissingData,
    Run,
    RunEvent,
    Scenario,
    Search,
    Source,
    Task,
    Workspace,
)


def iso(dt) -> str | None:
    return dt.isoformat() if dt else None


def run_summary(run: Run) -> dict:
    rec = run.context.get("verdict") if run.context else None
    return {
        "id": run.id,
        "workspace_id": run.workspace_id,
        "question": run.question,
        "status": run.status,
        "stage": run.stage,
        "error": run.error,
        "verdict": rec,
        "created_at": iso(run.created_at),
        "finished_at": iso(run.finished_at),
    }


def scenario_out(s: Scenario) -> dict:
    return {
        "id": s.id,
        "version": s.version,
        "assumptions": s.assumptions,
        "results": s.results,
        "created_at": iso(s.created_at),
    }


def run_detail(db: Session, run: Run, events_after: int = 0) -> dict:
    tasks = db.query(Task).filter_by(run_id=run.id).order_by(Task.position).all()
    searches = db.query(Search).filter_by(run_id=run.id).all()
    sources = db.query(Source).filter_by(run_id=run.id).order_by(Source.key).all()
    claims = db.query(Claim).filter_by(run_id=run.id).all()
    claims.sort(key=lambda c: int(c.key[1:]))
    links = db.query(EvidenceLink).filter(EvidenceLink.claim_id.in_([c.id for c in claims])).all() if claims else []
    analyses = {a.kind: a.data for a in db.query(Analysis).filter_by(run_id=run.id)}
    scenarios = db.query(Scenario).filter_by(run_id=run.id).order_by(Scenario.version).all()
    workspace = db.get(Workspace, run.workspace_id)
    task_keys = {t.id: t.key for t in tasks}
    links_by_claim: dict[str, list[EvidenceLink]] = {}
    for lk in links:
        links_by_claim.setdefault(lk.claim_id, []).append(lk)

    def task_out(t: Task) -> dict:
        own = [s for s in searches if s.task_id == t.id]
        task_claims = [c for c in claims if c.task_id == t.id]
        return {
            "id": t.id,
            "key": t.key,
            "title": t.title,
            "category": t.category,
            "rationale": t.rationale,
            "queries": t.queries,
            "status": t.status,
            "note": t.note,
            "searches": [
                {"query": s.query, "status": s.status, "error": s.error, "results": s.result_count} for s in own
            ],
            "claims": len(task_claims),
            "supported": sum(1 for c in task_claims if c.status == "supported"),
        }

    def claim_out(c: Claim) -> dict:
        ev = sorted(links_by_claim.get(c.id, []), key=lambda e: (e.relation == "related", -e.entailment))
        return {
            "id": c.id,
            "key": c.key,
            "task": task_keys.get(c.task_id),
            "text": c.text,
            "kind": c.kind,
            "status": c.status,
            "status_reason": c.status_reason,
            "user_flag": c.user_flag,
            "user_note": c.user_note,
            "evidence": [
                {
                    "source_id": e.source_id,
                    "passage": e.passage,
                    "page": e.page,
                    "quote": e.quote,
                    "quote_start": e.quote_start,
                    "quote_end": e.quote_end,
                    "relation": e.relation,
                    "entailment": e.entailment,
                    "relevance": e.relevance,
                    "scope_issue": e.scope_issue,
                    "note": e.verifier_note,
                    "model": e.verifier_model,
                }
                for e in ev
            ],
        }

    rec = analyses.get("recommendation")
    return {
        **run_summary(run),
        "workspace_name": workspace.name if workspace else "",
        "objective": (run.context or {}).get("objective"),
        "context": {
            k: v for k, v in (run.context or {}).items() if k not in ("objective", "verdict", "refresh_monthly")
        },
        "currency": currency_of(run),
        "currency_symbol": CURRENCIES[currency_of(run)],
        "decision": current_decision(db, run) if run.status == "completed" else None,
        "conditions": conditions(db, run) if run.status == "completed" else [],
        "previous_run_id": run.previous_run_id,
        "refresh_monthly": bool((run.context or {}).get("refresh_monthly")),
        "changes": changes(db, run),
        "settings": run.settings,
        "usage": run.usage,
        "document_ids": run.document_ids,
        "started_at": iso(run.started_at),
        "tasks": [task_out(t) for t in tasks],
        "sources": [
            {
                "id": s.id,
                "key": s.key,
                "kind": s.kind,
                "url": s.url,
                "title": s.title,
                "publisher": s.publisher,
                "tier": s.tier,
                "published": s.published,
                "retrieved_at": iso(s.retrieved_at),
                "document_id": s.document_id,
            }
            for s in sources
        ],
        "claims": [claim_out(c) for c in claims],
        "findings": [
            {"id": f.id, "severity": f.severity, "code": f.code, "text": f.text, "claim_id": f.claim_id}
            for f in sorted(
                db.query(Finding).filter_by(run_id=run.id), key=lambda f: {"high": 0, "medium": 1, "low": 2}[f.severity]
            )
        ],
        "missing": [
            {"item": m.item, "impact": m.impact, "plan": m.plan} for m in db.query(MissingData).filter_by(run_id=run.id)
        ],
        "recommendation": rec,
        "factors": (analyses.get("factors") or {}).get("items", []),
        "swot": (analyses.get("swot") or {}).get("items"),
        "pestle": (analyses.get("pestle") or {}).get("items", []),
        "porter": (analyses.get("porter") or {}).get("items", []),
        "competitors": (analyses.get("competitors") or {}).get("items", []),
        "assumption_suggestions": (analyses.get("assumptions") or {}).get("items", {}),
        "scenario": scenario_out(scenarios[-1]) if scenarios else None,
        "scenario_versions": [{"id": s.id, "version": s.version, "created_at": iso(s.created_at)} for s in scenarios],
        "events": [
            {"id": e.id, "at": iso(e.at), "agent": e.agent, "message": e.message}
            for e in db.query(RunEvent)
            .filter(RunEvent.run_id == run.id, RunEvent.id > events_after)
            .order_by(RunEvent.id)
        ],
    }
