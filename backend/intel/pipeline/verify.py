"""Claim verification. The model must quote the passage; unquotable verdicts are discarded."""

from dataclasses import dataclass

from intel.pipeline.llm_schemas import Verification
from intel.pipeline.passages import Passage
from intel.providers.llm import LLM
from intel.providers.usage import Usage
from intel.rag.text import find_quote

SYSTEM = """You check whether passages support a claim. Be strict.
"supports" means a careful reader would accept the claim as stated from this passage alone:
same quantity, unit, geography, segment and period. A passage on the same topic that does not
state the claim is "neutral", however relevant it looks. "contradicts" means the passage states
something incompatible with the claim. Copy the deciding words exactly from the passage into
"quote". Report any geography, segment, period or unit mismatch in "scope_issue"."""


@dataclass
class Judged:
    passage: Passage
    relation: str  # supports | contradicts | related
    entailment: float
    relevance: float
    quote: str | None
    quote_span: tuple[int, int] | None
    scope_issue: str | None
    note: str


def verify_claim(llm: LLM, claim: str, candidates: list[tuple[Passage, float]], usage: Usage) -> list[Judged]:
    if not candidates:
        return []
    listing = "\n\n".join(f"[{p.pid}] ({p.publisher})\n{p.text}" for p, _ in candidates)
    prompt = f"Claim: {claim}\n\nPassages:\n{listing}\n\nReturn one verdict per passage."
    out = llm.generate(system=SYSTEM, prompt=prompt, schema=Verification, usage=usage, temperature=0.0)
    rel = dict((p.pid, r) for p, r in candidates)
    by_id = {p.pid: p for p, _ in candidates}
    judged: list[Judged] = []
    seen: set[str] = set()
    for v in out.verdicts:
        p = by_id.get(v.passage_id)
        if p is None or p.pid in seen:
            continue
        seen.add(p.pid)
        relation = {"supports": "supports", "contradicts": "contradicts"}.get(v.relation, "related")
        entailment = round(float(v.confidence), 3) if relation != "related" else 0.0
        span = find_quote(p.text, v.quote) if v.quote else None
        note = v.note.strip()
        if relation != "related" and span is None:
            relation, entailment = "related", 0.0
            note = "Verifier quote was not found in the passage, so its verdict was discarded. " + note
        judged.append(
            Judged(
                passage=p,
                relation=relation,
                entailment=entailment,
                relevance=rel[p.pid],
                quote=p.text[span[0] : span[1]] if span else None,
                quote_span=span,
                scope_issue=v.scope_issue.strip() or None,
                note=note,
            )
        )
    return judged
