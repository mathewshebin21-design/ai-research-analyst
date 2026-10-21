"""Runs a planned research job: search → extract → verify → critique → analyse → decide."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from intel.config import Settings
from intel.finance import ASSUMPTION_SPEC, run_scenarios
from intel.models import (
    Analysis,
    Chunk,
    Claim,
    Document,
    EvidenceLink,
    Finding,
    MissingData,
    Run,
    RunEvent,
    Scenario,
    Search,
    Source,
    Task,
)
from intel.pipeline import analyst, critic
from intel.pipeline.extract import extract_claims
from intel.pipeline.passages import Passage, PassageIndex
from intel.pipeline.planner import make_plan
from intel.pipeline.sources import canonical_url, content_hash, domain, tier_for
from intel.pipeline.status import LinkView, derive_status
from intel.pipeline.verify import verify_claim
from intel.providers.errors import ProviderError
from intel.providers.llm import LLM
from intel.providers.search import SearchClient, cached_search
from intel.providers.usage import Usage
from intel.rag.bm25 import relevance
from intel.rag.text import split_passages

log = logging.getLogger(__name__)
MAX_SOURCE_CHARS = 60_000


@dataclass
class Providers:
    llm: LLM
    search: SearchClient


class RunFailed(RuntimeError):
    pass


def emit(db: Session, run: Run, agent: str, message: str) -> None:
    db.add(RunEvent(run_id=run.id, agent=agent, message=message))
    db.commit()


def plan_run(db: Session, run: Run, llm: LLM, settings: Settings) -> None:
    usage = Usage()
    plan = make_plan(llm, run.question, run.context or {}, usage, settings.max_searches_per_run)
    for i, t in enumerate(plan.tasks, start=1):
        db.add(
            Task(
                run_id=run.id,
                key=f"T{i}",
                title=t.title,
                category=t.category,
                rationale=t.rationale,
                queries=t.queries,
                position=i,
            )
        )
    run.status = "planned"
    run.context = {**(run.context or {}), "objective": plan.objective}
    run.usage = _merge_usage(run.usage, usage)
    db.commit()
    emit(db, run, "Planner", f"Plan ready: {len(plan.tasks)} tasks, {sum(len(t.queries) for t in plan.tasks)} searches")


def _merge_usage(existing: dict | None, usage: Usage) -> dict:
    out = dict(existing or {})
    for k, v in usage.as_dict().items():
        if isinstance(v, dict):
            merged = dict(out.get(k) or {})
            for name, n in v.items():
                merged[name] = merged.get(name, 0) + n
            out[k] = merged
        else:
            out[k] = out.get(k, 0) + v
    return out


def execute_run(db: Session, run_id: str, providers: Providers, settings: Settings) -> None:
    run = db.get(Run, run_id)
    if run is None:
        raise RunFailed("Run not found.")
    usage = Usage()
    run.status, run.started_at, run.error = "running", datetime.now(UTC), None
    run.settings = {
        "support_threshold": settings.support_threshold,
        "partial_threshold": settings.partial_threshold,
        "llm_model": providers.llm.model,
        "status_rules": "v1",
    }
    db.commit()
    stage = "research"
    try:
        tasks = db.query(Task).filter_by(run_id=run.id).order_by(Task.position).all()
        run.stage = stage
        task_sources, failed, total = _collect(db, run, tasks, providers.search, settings, usage)
        doc_sources = _attach_documents(db, run)
        if not any(task_sources.values()) and not doc_sources:
            raise RunFailed("No sources could be collected. Check the search service and try again.")

        stage = "extract"
        run.stage = stage
        db.commit()
        index = _build_index(db, run)
        doc_ids = {s.id for s in doc_sources}
        claims, missing_items = _extract(db, run, tasks, index, task_sources, doc_ids, providers.llm, settings, usage)

        if not claims:
            raise RunFailed("No claims could be extracted from the sources. See the task notes for the reason.")

        stage = "verify"
        run.stage = stage
        db.commit()
        _verify(db, run, claims, index, providers.llm, settings, usage)

        stage = "critique"
        run.stage = stage
        db.commit()
        findings = _critique(db, run, claims, failed, total)
        for m in missing_items:
            db.add(MissingData(run_id=run.id, item=m.item, impact=m.impact, plan=m.plan))
        for c in claims:
            if c.status == "missing":
                db.add(
                    MissingData(
                        run_id=run.id,
                        item=c.text,
                        impact="Medium",
                        plan="No source found; research further or treat as an assumption.",
                        claim_id=c.id,
                    )
                )
        db.commit()

        stage = "analyse"
        run.stage = stage
        db.commit()
        _analyse(db, run, claims, findings, providers.llm, usage)

        run.status, run.stage, run.finished_at = "completed", None, datetime.now(UTC)
        run.usage = _merge_usage(run.usage, usage)
        db.commit()
        emit(db, run, "System", "Run complete")
    except (ProviderError, RunFailed, ValueError) as exc:
        db.rollback()
        _fail(db, run_id, str(exc), stage, usage)
    except Exception:
        db.rollback()
        log.exception("run crashed", extra={"run_id": run_id, "stage": stage})
        _fail(db, run_id, f"An internal error stopped the run during {stage}.", stage, usage)


def _fail(db: Session, run_id: str, message: str, stage: str, usage: Usage) -> None:
    run = db.get(Run, run_id)
    if run is None:
        return
    run.status, run.error, run.stage, run.finished_at = "failed", message, stage, datetime.now(UTC)
    run.usage = _merge_usage(run.usage, usage)
    db.commit()
    emit(db, run, "System", f"Run failed during {stage}: {message}")


def _collect(db, run, tasks, search, settings, usage):
    task_sources: dict[str, list[str]] = {t.id: [] for t in tasks}
    seen_urls: dict[str, str] = {}
    seen_hashes: dict[str, str] = {}
    n_sources = db.query(Source).filter_by(run_id=run.id).count()
    failed = total = 0
    for t in tasks:
        t.status = "running"
        db.commit()
        ok = 0
        for q in t.queries:
            if total >= settings.max_searches_per_run:
                t.note = "Search budget for this run was reached."
                break
            total += 1
            try:
                hits, cached = cached_search(db, search, q)
            except ProviderError as exc:
                failed += 1
                db.add(Search(run_id=run.id, task_id=t.id, query=q, status="failed", error=str(exc)))
                db.commit()
                emit(db, run, "Researcher", f"{t.key}: search failed ({exc})")
                continue
            ok += 1
            usage.cached_searches += int(cached)
            usage.searches += int(not cached)
            db.add(
                Search(
                    run_id=run.id, task_id=t.id, query=q, status="cached" if cached else "ok", result_count=len(hits)
                )
            )
            for h in hits:
                url = canonical_url(h.url)
                digest = content_hash(h.content)
                existing = seen_urls.get(url) or seen_hashes.get(digest)
                if existing:
                    if existing not in task_sources[t.id]:
                        task_sources[t.id].append(existing)
                    continue
                n_sources += 1
                src = Source(
                    run_id=run.id,
                    key=f"S{n_sources}",
                    kind="web",
                    url=h.url,
                    title=h.title[:500],
                    publisher=domain(h.url),
                    tier=tier_for(h.url),
                    published=h.published,
                    content=h.content[:MAX_SOURCE_CHARS],
                    content_hash=digest,
                    search_score=h.score,
                )
                db.add(src)
                db.flush()
                seen_urls[url], seen_hashes[digest] = src.id, src.id
                task_sources[t.id].append(src.id)
            db.commit()
        t.status = "done" if ok else "failed"
        if not ok and not t.note:
            t.note = "Every search for this task failed."
        db.commit()
        emit(db, run, "Researcher", f"{t.key}: {len(task_sources[t.id])} sources from {ok}/{len(t.queries)} searches")
    return task_sources, failed, total


def _attach_documents(db, run) -> list[Source]:
    out = []
    n = db.query(Source).filter_by(run_id=run.id).count()
    for doc_id in run.document_ids or []:
        doc = db.get(Document, doc_id)
        if doc is None or doc.workspace_id != run.workspace_id or doc.status != "ready":
            continue
        n += 1
        text = "\n".join(
            c.text for c in db.query(Chunk).filter_by(document_id=doc.id).order_by(Chunk.page, Chunk.ordinal)
        )
        src = Source(
            run_id=run.id,
            key=f"S{n}",
            kind="pdf",
            document_id=doc.id,
            title=doc.filename,
            publisher=f"Uploaded document: {doc.filename}",
            tier="B",
            content=text[:MAX_SOURCE_CHARS],
            content_hash=doc.sha256,
        )
        db.add(src)
        out.append(src)
    db.commit()
    if out:
        emit(db, run, "Researcher", f"Attached {len(out)} uploaded document(s)")
    return out


def _build_index(db, run) -> PassageIndex:
    passages: list[Passage] = []
    n = 0
    for s in db.query(Source).filter_by(run_id=run.id).order_by(Source.key).all():
        if s.kind == "pdf" and s.document_id:
            for c in db.query(Chunk).filter_by(document_id=s.document_id).order_by(Chunk.page, Chunk.ordinal):
                n += 1
                passages.append(Passage(f"P{n}", s.id, s.key, s.publisher, s.tier, c.text, c.page))
        else:
            for text in split_passages(s.content):
                n += 1
                passages.append(Passage(f"P{n}", s.id, s.key, s.publisher, s.tier, text, None))
    return PassageIndex(passages)


def _extract(db, run, tasks, index, task_sources, doc_ids, llm, settings, usage):
    claims: list[Claim] = []
    missing = []
    seen_claims: set[str] = set()
    per_task = max(3, settings.max_claims_per_run // max(1, len(tasks)))
    for t in tasks:
        if len(claims) >= settings.max_claims_per_run:
            break
        among = set(task_sources.get(t.id, [])) | doc_ids
        query = " ".join([t.title, *t.queries])
        candidates = [p for p, _ in index.search(query, 12, among=among)] if among else []
        if not candidates:
            t.note = (t.note + " " if t.note else "") + "No passages to extract from."
            db.commit()
            continue
        try:
            out = extract_claims(llm, run.question, t.title, candidates, usage, per_task)
        except ProviderError as exc:
            # One unavailable call should not sink the run; the gap is recorded on the task.
            t.note = (t.note + " " if t.note else "") + f"Claims could not be extracted: {exc}"
            db.commit()
            emit(db, run, "Extractor", f"{t.key}: extraction failed ({exc})")
            continue
        added = 0
        for c in out.claims:
            norm = " ".join(c.text.lower().rstrip(".;").split())
            if norm in seen_claims:
                continue  # the same statement found again by a later task
            seen_claims.add(norm)
            added += 1
            claim = Claim(run_id=run.id, task_id=t.id, key=f"C{len(claims) + 1}", text=c.text, kind=c.kind)
            claim._refs = c.passage_ids  # type: ignore[attr-defined]  # transient, used by _verify
            db.add(claim)
            claims.append(claim)
        missing.extend(out.missing)
        db.commit()
        emit(db, run, "Extractor", f"{t.key}: {added} new claims")
    seen, unique = set(), []
    for m in missing:
        if m.item.lower() not in seen:
            seen.add(m.item.lower())
            unique.append(m)
    return claims, unique[:12]


def _verify(db, run, claims, index, llm, settings, usage):
    sources = {s.id: s for s in db.query(Source).filter_by(run_id=run.id)}
    for claim in claims:
        scores = index.score(claim.text)
        refs = [index.by_id[p] for p in getattr(claim, "_refs", []) if p in index.by_id]
        extra = [p for p, _ in index.search(claim.text, 4)]
        chosen = list(dict.fromkeys([*refs, *extra]))[:6]
        best = max((scores.get(p.pid, 0.0) for p in chosen), default=0.0)
        candidates = [(p, relevance(scores.get(p.pid, 0.0), best)) for p in chosen]
        try:
            judged = verify_claim(llm, claim.text, candidates, usage)
        except ProviderError as exc:
            claim.status = "missing"
            claim.status_reason = f"Not checked: the verification service was unavailable ({exc}). Treat as unverified."
            db.add(
                Finding(
                    run_id=run.id,
                    claim_id=claim.id,
                    severity="high",
                    code="unverified",
                    text=f"{claim.key}: could not be checked against its sources; it is excluded from support.",
                )
            )
            db.commit()
            continue
        views = []
        for j in judged:
            if j.relation == "related" and j.relevance < 0.3:
                continue
            src = sources[j.passage.source_id]
            db.add(
                EvidenceLink(
                    claim_id=claim.id,
                    source_id=src.id,
                    passage=j.passage.text,
                    page=j.passage.page,
                    quote=j.quote,
                    quote_start=j.quote_span[0] if j.quote_span else None,
                    quote_end=j.quote_span[1] if j.quote_span else None,
                    relation=j.relation,
                    entailment=j.entailment,
                    relevance=j.relevance,
                    scope_issue=j.scope_issue,
                    verifier_note=j.note,
                    verifier_model=getattr(llm, "last_model", llm.model),
                )
            )
            views.append(LinkView(j.relation, j.entailment, src.tier, src.publisher, j.scope_issue))
        claim.status, claim.status_reason = derive_status(views, settings.support_threshold, settings.partial_threshold)
        db.commit()
    counts: dict[str, int] = {}
    for c in claims:
        counts[c.status] = counts.get(c.status, 0) + 1
    emit(db, run, "Verifier", ", ".join(f"{v} {k}" for k, v in sorted(counts.items())) or "No claims to verify")


def _critique(db, run, claims, failed, total) -> list[Finding]:
    views = []
    for c in claims:
        links = db.query(EvidenceLink).filter_by(claim_id=c.id).all()
        tiers = [db.get(Source, lk.source_id).tier for lk in links if lk.relation == "supports"]
        pubs = {db.get(Source, lk.source_id).publisher for lk in links if lk.relation == "supports"}
        views.append(
            critic.ClaimView(
                c.id,
                c.key,
                c.kind,
                c.status,
                c.text,
                tiers,
                [lk.scope_issue for lk in links if lk.scope_issue],
                len(pubs),
            )
        )
    rows = []
    for f in critic.review_claims(views, failed, total):
        row = Finding(run_id=run.id, claim_id=f.claim_id, severity=f.severity, code=f.code, text=f.text)
        db.add(row)
        rows.append(row)
    db.commit()
    emit(db, run, "Critic", f"{len(rows)} findings")
    return rows


def _analyse(db, run, claims, findings, llm, usage):
    refs = [analyst.ClaimRef(c.id, c.key, c.status, c.text) for c in claims]
    result = analyst.analyse(llm, run.question, refs, usage)
    high = sum(1 for f in findings if f.severity == "high")
    scores = analyst.score(result["factors"], high)
    decision = analyst.decide(scores, result["factors"])
    narrative = analyst.narrate(llm, run.question, decision, scores, refs, result["assumption_suggestions"], usage)

    allowed = [c.text for c in claims if c.status in ("supported", "partial", "contradicted")]
    allowed += [str(v["value"]) for v in result["assumption_suggestions"].values()]
    allowed += [str(scores["overall"])]
    loose = critic.unsourced_numbers(
        " ".join([narrative["headline"], narrative["summary"], *narrative["conditions"]]), allowed
    )
    if loose:
        db.add(
            Finding(
                run_id=run.id,
                severity="high",
                code="unsourced_number",
                text=f"The recommendation text uses figures not found in any claim or assumption: {', '.join(loose)}.",
            )
        )
    if narrative["unknown_citations"]:
        db.add(
            Finding(
                run_id=run.id,
                severity="medium",
                code="bad_citation",
                text="The recommendation cites claims that are not usable evidence: "
                + ", ".join(narrative["unknown_citations"])
                + ".",
            )
        )

    for kind in ("swot", "pestle", "porter", "competitors", "factors"):
        db.add(Analysis(run_id=run.id, kind=kind, data={"items": result[kind]}))
    db.add(Analysis(run_id=run.id, kind="recommendation", data={**decision, **scores, **narrative}))
    db.add(Analysis(run_id=run.id, kind="assumptions", data={"items": result["assumption_suggestions"]}))
    run.context = {**(run.context or {}), "verdict": decision["verdict"]}
    db.commit()

    suggestions = result["assumption_suggestions"]
    if all(k in suggestions for k in ASSUMPTION_SPEC):
        values = {k: suggestions[k]["value"] for k in ASSUMPTION_SPEC}
        try:
            results = run_scenarios(values)
        except ValueError as exc:
            emit(db, run, "Analyst", f"Suggested assumptions are out of range ({exc}); enter them manually.")
        else:
            db.add(
                Scenario(run_id=run.id, version=1, assumptions=suggestions, results=results, created_by=run.created_by)
            )
            db.commit()
    emit(
        db,
        run,
        "Analyst",
        f"Verdict: {decision['verdict']} (score {scores['overall']}, confidence {scores['confidence_label']})",
    )
