"""Deterministic critique of a finished analysis. Findings are shown to the user, never silently fixed."""

import re
from dataclasses import dataclass

NUMBER = re.compile(r"(?<![\w.])[€$£]?\d[\d,]*(?:\.\d+)?\s?%?")


@dataclass
class ClaimView:
    id: str
    key: str
    kind: str
    status: str
    text: str
    tiers: list[str]
    scope_issues: list[str]
    supporting_publishers: int


@dataclass
class FindingOut:
    severity: str
    code: str
    text: str
    claim_id: str | None = None


def review_claims(claims: list[ClaimView], failed_searches: int, total_searches: int) -> list[FindingOut]:
    out: list[FindingOut] = []
    for c in claims:
        if c.status == "unsupported":
            sev = "high" if c.kind in ("figure", "forecast") else "medium"
            out.append(
                FindingOut(
                    sev, "unsupported", f"{c.key}: no retrieved source states this. Excluded from scoring.", c.id
                )
            )
        elif c.status == "contradicted":
            out.append(
                FindingOut("high", "contradicted", f"{c.key}: a source of equal or higher tier contradicts this.", c.id)
            )
        elif c.status == "partial":
            if c.scope_issues:
                out.append(
                    FindingOut(
                        "medium", "scope", f"{c.key}: evidence has a scope mismatch ({c.scope_issues[0]}).", c.id
                    )
                )
            elif c.supporting_publishers <= 1:
                out.append(
                    FindingOut("low", "single_source", f"{c.key}: rests on a single source; corroborate it.", c.id)
                )
        if c.status in ("supported", "partial") and c.tiers and set(c.tiers) == {"C"}:
            out.append(
                FindingOut("medium", "low_tier", f"{c.key}: only blog or user-generated sources support this.", c.id)
            )
    if failed_searches:
        out.append(
            FindingOut(
                "medium" if failed_searches * 3 >= total_searches else "low",
                "search_failures",
                f"{failed_searches} of {total_searches} searches failed; coverage may be incomplete.",
            )
        )
    return out


def numbers_in(text: str) -> set[str]:
    return {n.replace(",", "").replace(" ", "").rstrip(".") for n in NUMBER.findall(text)}


def unsourced_numbers(narrative: str, allowed_texts: list[str]) -> list[str]:
    """Numbers in the narrative that appear in no claim or assumption."""
    allowed: set[str] = set()
    for t in allowed_texts:
        allowed |= numbers_in(t)
    bare = {a.strip("€$£%") for a in allowed}
    found = []
    for n in sorted(numbers_in(narrative)):
        core = n.strip("€$£%")
        if re.fullmatch(r"C?\d", core) or core in bare:
            continue
        if re.fullmatch(r"(19|20)\d\d", core) or core in {"1", "2", "3", "4", "6", "12", "36"}:
            continue  # years and small counts are not data claims
        found.append(n)
    return found
