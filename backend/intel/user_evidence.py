"""Evidence the user brings: a link, pasted text or one of their PDFs, checked against one claim.

User sources go through the same quote-checked verifier and the same status rules as searched
sources. They are tier B, so on its own a user source can make a claim at most partially
supported; a second independent source or a tier-A source is still needed for "supported".
"""

import html
import ipaddress
import re
import socket
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpx
from sqlalchemy.orm import Session

from intel.config import Settings
from intel.models import Chunk, Claim, Document, EvidenceLink, Finding, Run, RunEvent, Source
from intel.pipeline import critic
from intel.pipeline.passages import Passage, PassageIndex
from intel.pipeline.sources import content_hash, domain
from intel.pipeline.status import LinkView, derive_status
from intel.pipeline.verify import verify_claim
from intel.providers.llm import LLM
from intel.providers.usage import Usage
from intel.rag.bm25 import relevance
from intel.rag.pdf import UploadRejected, chunk_pages, validate_pdf
from intel.rag.text import normalize, split_passages

MAX_FETCH_BYTES = 3 * 1024 * 1024
CLAIM_FINDING_CODES = ("unsupported", "contradicted", "scope", "single_source", "low_tier", "unverified")


class EvidenceRejected(ValueError):
    """Shown to the user: the evidence could not be used."""


@dataclass
class Fetched:
    url: str
    title: str
    pages: list[tuple[int | None, str]]  # (page or None, text)


def _public_host(host: str) -> None:
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise EvidenceRejected("That web address could not be found.") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global or ip.is_multicast:
            raise EvidenceRejected("Links to private or internal addresses are not allowed.")


def _html_to_text(raw: str) -> tuple[str, str]:
    title_m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    title = normalize(html.unescape(title_m.group(1))) if title_m else ""
    body = re.sub(r"<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>", " ", raw, flags=re.S | re.I)
    body = re.sub(r"<(br|p|div|li|h[1-6]|tr|section|article)\b[^>]*>", "\n\n", body, flags=re.I)
    body = re.sub(r"<[^>]+>", " ", body)
    return title, html.unescape(body)


def fetch_url(url: str, transport: httpx.BaseTransport | None = None) -> Fetched:
    """Fetch a public web page or PDF safely: http(s) only, public addresses only, size and redirect limits."""
    current = url.strip()
    with httpx.Client(
        timeout=15.0,
        follow_redirects=False,
        transport=transport,
        headers={"User-Agent": "StrategicIntelligenceHub/1.0 (evidence check)"},
    ) as client:
        for _ in range(4):
            parts = urlsplit(current)
            if parts.scheme not in ("http", "https") or not parts.hostname:
                raise EvidenceRejected("Use a full web address starting with http:// or https://.")
            if transport is None:  # tests inject a transport and never touch the network
                _public_host(parts.hostname)
            with client.stream("GET", current) as r:
                if r.is_redirect:
                    current = urljoin(current, r.headers.get("location", ""))
                    continue
                if r.status_code != 200:
                    raise EvidenceRejected(f"The page could not be fetched (HTTP {r.status_code}).")
                data = b""
                for chunk in r.iter_bytes():
                    data += chunk
                    if len(data) > MAX_FETCH_BYTES:
                        raise EvidenceRejected("The page is too large to check (over 3 MB).")
                ctype = r.headers.get("content-type", "").lower()
            break
        else:
            raise EvidenceRejected("The link redirects too many times.")
    if "pdf" in ctype or data[:5] == b"%PDF-":
        try:
            pages = validate_pdf(data, max_bytes=MAX_FETCH_BYTES, max_pages=200)
        except UploadRejected as exc:
            raise EvidenceRejected(str(exc)) from exc
        return Fetched(current, domain(current), [(p, t) for p, _, t in chunk_pages(pages)])
    if not any(t in ctype for t in ("html", "text/plain", "xml")) and ctype:
        raise EvidenceRejected("Only web pages, plain text and PDFs can be checked.")
    title, text = _html_to_text(data.decode(r.encoding or "utf-8", errors="replace"))
    passages = [(None, p) for p in split_passages(text) if len(normalize(p)) >= 40]
    if not passages:
        raise EvidenceRejected("No readable text was found on that page.")
    return Fetched(current, title or domain(current), passages)


def _claim_views(db: Session, claim: Claim) -> list[LinkView]:
    out = []
    for lk in db.query(EvidenceLink).filter_by(claim_id=claim.id):
        src = db.get(Source, lk.source_id)
        out.append(LinkView(lk.relation, lk.entailment, src.tier, src.publisher, lk.scope_issue))
    return out


def refresh_claim(db: Session, run: Run, claim: Claim, settings: Settings) -> None:
    """Re-derive one claim's status and its critic findings from all of its evidence."""
    claim.status, claim.status_reason = derive_status(
        _claim_views(db, claim), settings.support_threshold, settings.partial_threshold
    )
    db.query(Finding).filter(Finding.claim_id == claim.id, Finding.code.in_(CLAIM_FINDING_CODES)).delete(
        synchronize_session=False
    )
    links = db.query(EvidenceLink).filter_by(claim_id=claim.id).all()
    supporting = [db.get(Source, lk.source_id) for lk in links if lk.relation == "supports"]
    view = critic.ClaimView(
        claim.id,
        claim.key,
        claim.kind,
        claim.status,
        claim.text,
        [s.tier for s in supporting],
        [lk.scope_issue for lk in links if lk.scope_issue],
        len({s.publisher for s in supporting}),
    )
    for f in critic.review_claims([view], failed_searches=0, total_searches=1):
        db.add(Finding(run_id=run.id, claim_id=f.claim_id, severity=f.severity, code=f.code, text=f.text))


def add_evidence(
    db: Session,
    run: Run,
    claim: Claim,
    llm: LLM,
    settings: Settings,
    user_label: str,
    *,
    url: str | None = None,
    text: str | None = None,
    title: str | None = None,
    document_id: str | None = None,
    transport: httpx.BaseTransport | None = None,
) -> dict:
    if url:
        fetched = fetch_url(url, transport)
        kind, src_url, src_title, pages, publisher = (
            "user",
            fetched.url,
            fetched.title,
            fetched.pages,
            domain(fetched.url),
        )
        doc_id = None
    elif text:
        body = text.strip()
        if len(body) < 40:
            raise EvidenceRejected("Paste at least a sentence or two of the source text.")
        kind, src_url, src_title, doc_id = "user", None, (title or "Pasted text").strip()[:200], None
        pages = [(None, p) for p in split_passages(body)]
        publisher = src_title
    elif document_id:
        doc = db.get(Document, document_id)
        if doc is None or doc.workspace_id != run.workspace_id or doc.status != "ready":
            raise EvidenceRejected("That document is not in this workspace.")
        chunks = db.query(Chunk).filter_by(document_id=doc.id).order_by(Chunk.page, Chunk.ordinal).all()
        kind, src_url, src_title, doc_id = "pdf", None, doc.filename, doc.id
        pages = [(c.page, c.text) for c in chunks]
        publisher = f"Uploaded document: {doc.filename}"
    else:
        raise EvidenceRejected("Add a link, paste text or choose a document.")

    n = db.query(Source).filter_by(run_id=run.id).count() + 1
    joined = "\n\n".join(t for _, t in pages)
    source = Source(
        run_id=run.id,
        key=f"S{n}",
        kind=kind,
        url=src_url,
        document_id=doc_id,
        title=src_title or publisher,
        publisher=f"Added by user: {publisher}"[:255],
        tier="B",
        content=joined[:60_000],
        content_hash=content_hash(joined),
    )
    db.add(source)
    db.flush()

    passages = [
        Passage(f"P{i}", source.id, source.key, source.publisher, "B", t, page) for i, (page, t) in enumerate(pages, 1)
    ]
    index = PassageIndex(passages)
    ranked = index.search(claim.text, 5) or [(p, 0.0) for p in passages[:3]]
    best = max((s for _, s in ranked), default=0.0)
    usage = Usage()
    judged = verify_claim(llm, claim.text, [(p, relevance(s, best) if best else 0.5) for p, s in ranked], usage)
    added = 0
    for j in judged:
        db.add(
            EvidenceLink(
                claim_id=claim.id,
                source_id=source.id,
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
        added += 1
    db.flush()
    before = claim.status
    refresh_claim(db, run, claim, settings)
    run.usage = {
        **(run.usage or {}),
        "user_evidence_llm_calls": (run.usage or {}).get("user_evidence_llm_calls", 0) + usage.llm_calls,
    }
    db.add(
        RunEvent(
            run_id=run.id,
            agent="User",
            message=f"{user_label} added {source.key} to {claim.key}: {before} → {claim.status}",
        )
    )
    relations = [j.relation for j in judged]
    return {
        "source_key": source.key,
        "previous_status": before,
        "status": claim.status,
        "verdicts": {r: relations.count(r) for r in set(relations)},
        "passages_checked": added,
    }


def dispute(db: Session, run: Run, claim: Claim, note: str, user_label: str) -> None:
    claim.user_flag, claim.user_note = "disputed", note.strip()[:1000]
    db.query(Finding).filter_by(claim_id=claim.id, code="disputed").delete()
    db.add(
        Finding(
            run_id=run.id,
            claim_id=claim.id,
            severity="medium",
            code="disputed",
            text=f"{claim.key}: disputed by {user_label}: {claim.user_note or 'no reason given'}. "
            "Counted as no evidence.",
        )
    )
    db.add(RunEvent(run_id=run.id, agent="User", message=f"{user_label} disputed {claim.key}"))


def clear_dispute(db: Session, run: Run, claim: Claim, user_label: str) -> None:
    claim.user_flag, claim.user_note = None, None
    db.query(Finding).filter_by(claim_id=claim.id, code="disputed").delete()
    db.add(RunEvent(run_id=run.id, agent="User", message=f"{user_label} cleared the dispute on {claim.key}"))
