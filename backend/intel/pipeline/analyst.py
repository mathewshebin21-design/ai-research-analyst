"""Frameworks, explainable scoring and the recommendation.

The model drafts framework entries and factor scores, each citing claim keys. Citations are
validated here, evidence coverage is computed from claim statuses, and the verdict is chosen by
fixed rules. The model only writes the wording of the recommendation, after the verdict is set.
"""

import re
from dataclasses import dataclass

from intel.pipeline.llm_schemas import Analysis, CitedItem, Narrative
from intel.pipeline.status import coverage_weight
from intel.providers.llm import LLM
from intel.providers.usage import Usage

FACTORS = {
    "attract": ("Market attractiveness", 0.25),
    "demand": ("Customer demand", 0.20),
    "compete": ("Competitive room", 0.15),
    "econ": ("Unit economics", 0.25),
    "exec": ("Execution and compliance", 0.15),
}

ANALYST_SYSTEM = """You are a strategy analyst. Build the requested frameworks only from the numbered
claims. Every item lists the claim keys it rests on. Prefer claims marked supported or partial.
You may cite a contradicted or unsupported claim only to describe a risk or a gap, and must say so.
Score each factor 0-100 where 50 is neutral; a factor with little evidence stays near 50.
For the financial assumptions, use a value stated in a claim when one exists and give its key;
otherwise give your best estimate with an empty claim key. Do not invent competitors."""

NARRATIVE_SYSTEM = """You write the recommendation for a board paper. The verdict is already decided
and you must not change it. Cite claim keys in square brackets. Use only numbers that appear in
the claims or assumptions provided. Conditions must be measurable. Plain, direct sentences."""


@dataclass
class ClaimRef:
    id: str
    key: str
    status: str
    text: str


def _claims_block(claims: list[ClaimRef]) -> str:
    return "\n".join(f"{c.key} [{c.status}] {c.text}" for c in claims)


def _validate(keys: list[str], index: dict[str, ClaimRef]) -> tuple[list[str], str, float]:
    valid = [k for k in dict.fromkeys(k.strip().upper() for k in keys) if k in index]
    if not valid:
        return [], "no_evidence", 0.0
    cov = sum(coverage_weight(index[k].status) for k in valid) / len(valid)
    basis = "evidenced" if any(index[k].status in ("supported", "partial") for k in valid) else "unsupported"
    return valid, basis, round(cov, 3)


def _cited(item: CitedItem, index: dict[str, ClaimRef]) -> dict:
    keys, basis, cov = _validate(item.claims, index)
    return {"text": item.text, "claims": keys, "basis": basis, "coverage": cov}


def analyse(llm: LLM, question: str, claims: list[ClaimRef], usage: Usage) -> dict:
    index = {c.key: c for c in claims}
    prompt = f"Decision question: {question}\n\nClaims:\n{_claims_block(claims)}"
    a: Analysis = llm.generate(system=ANALYST_SYSTEM, prompt=prompt, schema=Analysis, usage=usage)

    swot = {
        k: [_cited(i, index) for i in getattr(a.swot, k)]
        for k in ("strengths", "weaknesses", "opportunities", "threats")
    }
    pestle = []
    for p in a.pestle:
        keys, basis, cov = _validate(p.claims, index)
        pestle.append(
            {"factor": p.factor, "rating": p.rating, "note": p.note, "claims": keys, "basis": basis, "coverage": cov}
        )
    porter = []
    for f in a.porter:
        keys, basis, cov = _validate(f.claims, index)
        porter.append(
            {"force": f.force, "level": round(f.level, 1), "rationale": f.rationale, "claims": keys, "basis": basis}
        )
    competitors = []
    for c in a.competitors:
        keys, basis, _ = _validate(c.claims, index)
        if basis == "no_evidence":
            continue  # a competitor no claim mentions is not reported
        competitors.append(
            {
                "name": c.name,
                "positioning": c.positioning,
                "price_note": c.price_note,
                "strengths": c.strengths,
                "weaknesses": c.weaknesses,
                "claims": keys,
                "basis": basis,
            }
        )

    factors = []
    by_key = {f.key: f for f in a.factors}
    for key, (label, weight) in FACTORS.items():
        f = by_key.get(key)
        keys, basis, cov = _validate(f.claims if f else [], index)
        # Without evidence a factor is held at neutral rather than trusting an unsupported score.
        score = f.score if f and basis == "evidenced" else 50
        factors.append(
            {
                "key": key,
                "label": label,
                "weight": weight,
                "score": score,
                "model_score": f.score if f else None,
                "coverage": cov,
                "claims": keys,
                "rationale": f.rationale if f else "The analyst gave no assessment.",
                "basis": basis,
            }
        )

    assumptions = {}
    for s in a.assumptions:
        key = s.claim.strip().upper()
        evidenced = key in index and index[key].status in ("supported", "partial")
        assumptions[s.key] = {
            "value": s.value,
            "origin": "evidence" if evidenced else "estimate",
            "claim": key if evidenced else None,
            "note": s.note,
        }

    return {
        "swot": swot,
        "pestle": pestle,
        "porter": porter,
        "competitors": competitors,
        "factors": factors,
        "assumption_suggestions": assumptions,
    }


def score(factors: list[dict], high_findings: int) -> dict:
    overall = round(sum(f["weight"] * f["score"] for f in factors), 1)
    coverage = round(sum(f["weight"] * f["coverage"] for f in factors), 3)
    penalty = max(0.5, 1 - 0.05 * high_findings)
    confidence = round(coverage * penalty, 3)
    label = "Low" if confidence < 0.4 else "Moderate" if confidence < 0.7 else "High"
    return {
        "overall": overall,
        "coverage": coverage,
        "confidence": confidence,
        "confidence_label": label,
        "confidence_method": (
            f"Weighted evidence coverage {coverage:.2f} × penalty {penalty:.2f} "
            f"for {high_findings} high-severity findings"
        ),
    }


def decide(scores: dict, factors: list[dict]) -> dict:
    econ = next(f for f in factors if f["key"] == "econ")
    reasons = []
    if scores["confidence"] < 0.35:
        verdict = "Insufficient evidence"
        reasons.append("Less than 35% of the weighted case rests on evidence.")
    elif scores["overall"] >= 70 and econ["coverage"] >= 0.34:
        verdict = "Go"
        reasons.append("Weighted score at least 70 with evidenced unit economics.")
    elif scores["overall"] >= 50:
        verdict = "Conditional go"
        reasons.append("Weighted score between 50 and 70, or unit economics not yet evidenced.")
    else:
        verdict = "No-go"
        reasons.append("Weighted score below 50.")
    return {"verdict": verdict, "rule": " ".join(reasons)}


CITE = re.compile(r"\[(C\d+)\]")


def narrate(
    llm: LLM, question: str, decision: dict, scores: dict, claims: list[ClaimRef], assumptions: dict, usage: Usage
) -> dict:
    usable = [c for c in claims if c.status in ("supported", "partial", "contradicted")]
    assumption_lines = "\n".join(f"{k}: {v['value']} ({v['origin']})" for k, v in assumptions.items())
    prompt = (
        f"Decision question: {question}\nVerdict (fixed): {decision['verdict']}\n"
        f"Weighted score: {scores['overall']} / 100. Confidence: {scores['confidence_label']}.\n\n"
        f"Claims:\n{_claims_block(usable)}\n\nAssumptions:\n{assumption_lines or 'none'}"
    )
    n: Narrative = llm.generate(system=NARRATIVE_SYSTEM, prompt=prompt, schema=Narrative, usage=usage, temperature=0.3)
    known = {c.key for c in usable}
    cited = sorted({k for k in CITE.findall(n.summary)})
    return {
        "headline": n.headline.strip(),
        "summary": n.summary.strip(),
        "conditions": [c.strip() for c in n.conditions if c.strip()][:4],
        "would_change": [c.strip() for c in n.would_change if c.strip()][:3],
        "cited": [k for k in cited if k in known],
        "unknown_citations": [k for k in cited if k not in known],
    }
