import asyncio
import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from intel.api.deps import audit, expensive, rate_limited
from intel.api.readmodel import run_detail, run_summary, scenario_out
from intel.config import Settings, get_settings
from intel.db import get_db, session_factory
from intel.finance import ASSUMPTION_SPEC, run_scenarios
from intel.models import Document, Job, Report, Run, RunEvent, Scenario, Task, User
from intel.pipeline.orchestrator import emit, plan_run
from intel.providers import factory
from intel.providers.errors import ProviderError
from intel.rag.pdf import storage_path, store_bytes
from intel.report_pdf import build_report
from intel.security.auth import accepted_user, require_role

router = APIRouter(dependencies=[Depends(rate_limited)])


class RunIn(BaseModel):
    question: str = Field(min_length=15, max_length=1000)
    company: str | None = Field(default=None, max_length=200)
    geography: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    document_ids: list[str] = Field(default_factory=list, max_length=10)
    currency: str = Field(default="GBP", pattern="^(GBP|EUR|USD|INR)$")


class TaskIn(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    category: str = Field(max_length=40)
    queries: list[str] = Field(min_length=1, max_length=3)


class PlanIn(BaseModel):
    tasks: list[TaskIn] = Field(min_length=1, max_length=10)


class AssumptionIn(BaseModel):
    value: float
    origin: str = Field(pattern="^(evidence|estimate|user)$")
    claim: str | None = None
    note: str = ""


class ScenarioIn(BaseModel):
    assumptions: dict[str, AssumptionIn]


def _load(db: Session, user: User, run_id: str, role: str) -> Run:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(404, "Run not found.")
    require_role(db, user, run.workspace_id, role)
    return run


@router.get("/workspaces/{workspace_id}/runs")
def list_runs(workspace_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> list[dict]:
    require_role(db, user, workspace_id, "viewer")
    return [run_summary(r) for r in db.query(Run).filter_by(workspace_id=workspace_id).order_by(Run.created_at.desc())]


@router.post("/workspaces/{workspace_id}/runs", status_code=201, dependencies=[Depends(expensive)])
def create_run(
    workspace_id: str,
    body: RunIn,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Create a run and draft its research plan for the user to review before anything is searched."""
    require_role(db, user, workspace_id, "editor")
    for doc_id in body.document_ids:
        doc = db.get(Document, doc_id)
        if doc is None or doc.workspace_id != workspace_id:
            raise HTTPException(422, "One of the selected documents is not in this workspace.")
    run = Run(
        workspace_id=workspace_id,
        created_by=user.id,
        question=body.question.strip(),
        context={"company": body.company, "geography": body.geography, "notes": body.notes, "currency": body.currency},
        document_ids=body.document_ids,
    )
    db.add(run)
    db.commit()
    try:
        providers = factory.get_providers(settings)
        plan_run(db, run, providers.llm, settings)
    except (ProviderError, ValueError) as exc:
        run.status, run.error = "failed", str(exc)
        db.commit()
        raise HTTPException(503, str(exc)) from exc
    audit(db, "run.created", user.id, workspace_id, run=run.id)
    db.commit()
    return run_detail(db, run)


@router.put("/runs/{run_id}/plan")
def edit_plan(
    run_id: str,
    body: PlanIn,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    run = _load(db, user, run_id, "editor")
    if run.status != "planned":
        raise HTTPException(409, "The plan can only be edited before the run starts.")
    if sum(len(t.queries) for t in body.tasks) > settings.max_searches_per_run:
        raise HTTPException(422, f"A run can use at most {settings.max_searches_per_run} searches.")
    db.query(Task).filter_by(run_id=run.id).delete()
    for i, t in enumerate(body.tasks, start=1):
        db.add(
            Task(
                run_id=run.id,
                key=f"T{i}",
                title=t.title.strip(),
                category=t.category,
                queries=[q.strip() for q in t.queries if q.strip()],
                position=i,
            )
        )
    audit(db, "run.plan_edited", user.id, run.workspace_id, run=run.id)
    db.commit()
    return run_detail(db, run)


@router.post("/runs/{run_id}/start")
def start_run(
    run_id: str,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    run = _load(db, user, run_id, "editor")
    if run.status not in ("planned", "failed"):
        raise HTTPException(409, f"This run is already {run.status}.")
    month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    used = (
        db.query(Run)
        .filter(Run.workspace_id == run.workspace_id, Run.started_at.is_not(None), Run.started_at >= month_start)
        .count()
    )
    if used >= settings.runs_per_workspace_per_month:
        raise HTTPException(
            429, f"This workspace has used its {settings.runs_per_workspace_per_month} runs for this month."
        )
    if run.status == "failed":
        _reset(db, run)
    run.status, run.error = "queued", None
    db.add(Job(run_id=run.id))
    audit(db, "run.started", user.id, run.workspace_id, run=run.id)
    db.commit()
    emit(db, run, "System", "Queued")
    return run_summary(run)


def _reset(db: Session, run: Run) -> None:
    """Retry from scratch, keeping the plan."""
    from intel.models import Analysis, Claim, Finding, MissingData, Search, Source

    for model in (Claim, Finding, MissingData, Analysis, Search, Source, Scenario):
        db.query(model).filter_by(run_id=run.id).delete()
    for t in db.query(Task).filter_by(run_id=run.id):
        t.status, t.note = "queued", None


@router.get("/runs/{run_id}")
def get_run(run_id: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> dict:
    return run_detail(db, _load(db, user, run_id, "viewer"))


@router.delete("/runs/{run_id}")
def delete_run(
    run_id: str,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    run = _load(db, user, run_id, "editor")
    if run.status in ("queued", "running"):
        raise HTTPException(409, "Wait for the run to finish before deleting it.")
    keys = [r.storage_key for r in db.query(Report).filter_by(run_id=run.id)]
    audit(db, "run.deleted", user.id, run.workspace_id, run=run.id)
    db.delete(run)
    db.commit()
    for k in keys:
        storage_path(settings.storage_dir, k).unlink(missing_ok=True)
    return {"deleted": True}


@router.get("/runs/{run_id}/events")
async def stream_events(
    run_id: str, request: Request, after: int = 0, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> StreamingResponse:
    """Server-sent events with run progress until the run finishes."""
    _load(db, user, run_id, "viewer")

    async def gen():
        last = after
        for _ in range(900):  # about 15 minutes
            if await request.is_disconnected():
                return
            s = session_factory()()
            try:
                events = (
                    s.query(RunEvent).filter(RunEvent.run_id == run_id, RunEvent.id > last).order_by(RunEvent.id).all()
                )
                run = s.get(Run, run_id)
                for e in events:
                    last = e.id
                    payload = json.dumps({"agent": e.agent, "message": e.message, "at": e.at.isoformat()})
                    yield f"id: {e.id}\ndata: {payload}\n\n"
                if run is None or run.status in ("completed", "failed"):
                    yield f"event: done\ndata: {json.dumps({'status': run.status if run else 'deleted'})}\n\n"
                    return
            finally:
                s.close()
            yield ": keep-alive\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.post("/runs/{run_id}/scenarios", status_code=201)
def create_scenario(
    run_id: str, body: ScenarioIn, user: User = Depends(accepted_user), db: Session = Depends(get_db)
) -> dict:
    run = _load(db, user, run_id, "editor")
    missing = [k for k in ASSUMPTION_SPEC if k not in body.assumptions]
    if missing:
        raise HTTPException(422, f"Missing assumptions: {', '.join(missing)}")
    values = {k: body.assumptions[k].value for k in ASSUMPTION_SPEC}
    try:
        results = run_scenarios(values)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    version = (db.query(Scenario).filter_by(run_id=run.id).count()) + 1
    s = Scenario(
        run_id=run.id,
        version=version,
        assumptions={k: body.assumptions[k].model_dump() for k in ASSUMPTION_SPEC},
        results=results,
        created_by=user.id,
    )
    db.add(s)
    db.commit()
    return scenario_out(s)


@router.get("/finance/spec")
def finance_spec() -> dict:
    return ASSUMPTION_SPEC


class CalculateIn(BaseModel):
    values: dict[str, float]


@router.post("/finance/calculate")
def calculate(body: CalculateIn, user: User = Depends(accepted_user)) -> dict:
    """Compute scenarios without saving, for live assumption controls."""
    try:
        return run_scenarios(body.values)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/runs/{run_id}/reports", status_code=201, dependencies=[Depends(expensive)])
def create_report(
    run_id: str,
    scenario_id: str | None = None,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    run = _load(db, user, run_id, "viewer")
    if run.status != "completed":
        raise HTTPException(409, "Reports can be exported once the run has completed.")
    data = run_detail(db, run)
    if scenario_id:
        s = db.get(Scenario, scenario_id)
        if s is None or s.run_id != run.id:
            raise HTTPException(404, "Scenario not found.")
        data["scenario"] = scenario_out(s)
    pdf = build_report(data)
    key, _ = store_bytes(settings.storage_dir, pdf, ".pdf")
    report = Report(run_id=run.id, scenario_id=(data["scenario"] or {}).get("id"), storage_key=key, created_by=user.id)
    db.add(report)
    audit(db, "report.exported", user.id, run.workspace_id, run=run.id)
    db.commit()
    return {"id": report.id, "download": f"/reports/{report.id}/download"}


@router.get("/reports/{report_id}/download")
def download_report(
    report_id: str,
    user: User = Depends(accepted_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    report = db.get(Report, report_id)
    if report is None:
        raise HTTPException(404, "Report not found.")
    _load(db, user, report.run_id, "viewer")
    path = storage_path(settings.storage_dir, report.storage_key)
    if not path.exists():
        raise HTTPException(410, "This report file is no longer available. Export it again.")
    return Response(
        path.read_bytes(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="market-entry-{report.run_id[:8]}.pdf"'},
    )


@router.get("/compare")
def compare(a: str, b: str, user: User = Depends(accepted_user), db: Session = Depends(get_db)) -> dict:
    out = []
    for run_id in (a, b):
        d = run_detail(db, _load(db, user, run_id, "viewer"))
        counts: dict[str, int] = {}
        for c in d["claims"]:
            counts[c["status"]] = counts.get(c["status"], 0) + 1
        base = (d["scenario"] or {}).get("results", {}).get("scenarios", {}).get("base", {})
        out.append(
            {
                "id": d["id"],
                "question": d["question"],
                "finished_at": d["finished_at"],
                "verdict": (d["recommendation"] or {}).get("verdict"),
                "overall": (d["recommendation"] or {}).get("overall"),
                "confidence": (d["recommendation"] or {}).get("confidence"),
                "claims": counts,
                "sources": len(d["sources"]),
                "factors": {f["key"]: f["score"] for f in d["factors"]},
                "currency_symbol": d["currency_symbol"],
                "break_even_month": base.get("break_even_month"),
                "peak_funding": base.get("peak_funding"),
            }
        )
    return {"runs": out}
