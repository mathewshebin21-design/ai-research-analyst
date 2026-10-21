"""Deterministic claim status. A model never asserts a status directly; these rules derive it."""

from dataclasses import dataclass

TIER_RANK = {"A": 3, "B": 2, "C": 1}


@dataclass(frozen=True)
class LinkView:
    relation: str  # supports | contradicts | related
    entailment: float
    tier: str
    publisher: str
    scope_issue: str | None


def derive_status(links: list[LinkView], support: float = 0.70, partial: float = 0.40) -> tuple[str, str]:
    if not links:
        return "missing", "No retrieved passage addresses this claim."

    strong = [lk for lk in links if lk.relation == "supports" and lk.entailment >= support and not lk.scope_issue]
    scoped = [lk for lk in links if lk.relation == "supports" and lk.entailment >= support and lk.scope_issue]
    weak = [lk for lk in links if lk.relation == "supports" and partial <= lk.entailment < support]
    against = [lk for lk in links if lk.relation == "contradicts" and lk.entailment >= support and not lk.scope_issue]

    best_for = max((TIER_RANK[lk.tier] for lk in strong), default=0)
    best_against = max((TIER_RANK[lk.tier] for lk in against), default=0)
    independent = {lk.publisher for lk in strong}

    if against and best_against >= best_for:
        return "contradicted", f"Contradicted by {len(against)} passage(s) of equal or higher source tier."
    if strong and (best_for == 3 or len(independent) >= 2):
        why = "a tier-A source" if best_for == 3 else f"{len(independent)} independent sources"
        extra = " A lower-tier source disagrees." if against else ""
        return "supported", f"Entailed by {why}.{extra}"
    if strong:
        return "partial", "Entailed by a single tier-B/C source; needs corroboration."
    if scoped:
        return "partial", "Supported only by a source with a scope mismatch: " + (scoped[0].scope_issue or "")
    if weak:
        return "partial", "Sources point the same way but do not state the claim outright."
    if any(lk.relation == "contradicts" and lk.entailment >= partial for lk in links):
        return "partial", "Sources weakly contradict this; treat with caution."
    return "unsupported", "Relevant passages were found, but none states this claim. Relevance is not support."


def coverage_weight(status: str) -> float:
    return {"supported": 1.0, "partial": 0.5}.get(status, 0.0)
