"""Test doubles for the language model and search. Fixture text is invented and marked as such."""

import re

from intel.pipeline import llm_schemas as S
from intel.providers.search import SearchClient, SearchHit
from intel.rag.text import tokens

CORPUS = [
    SearchHit(
        url="https://www.ons.gov.uk/fixture/footwear-sales",
        title="Fixture: footwear retail sales bulletin",
        content=(
            "Fixture text for tests. Online footwear sales in the United Kingdom grew by 6.5% in 2025.\n\n"
            "Premium trainers accounted for 22% of online footwear spending in 2025."
        ),
        score=0.91,
        published="2026-03-01",
    ),
    SearchHit(
        url="https://retail-analysts.example/fixture/uk-trainers",
        title="Fixture: UK trainer market note",
        content=(
            "Fixture text for tests. Online footwear sales in the United Kingdom grew by about 6.5% in 2025, "
            "according to our panel.\n\nCompetitor Northfold prices its core trainer at £150 and sells direct."
        ),
        score=0.84,
        published=None,
    ),
    SearchHit(
        url="https://lifestyle-blog.medium.com/fixture/eco-boom",
        title="Fixture: eco trainers are booming",
        content="Fixture text for tests. Eco trainers are booming and shoppers love sustainable brands.",
        score=0.77,
        published=None,
    ),
    SearchHit(
        url="https://survey-institute.example/fixture/premium",
        title="Fixture: willingness to pay survey",
        content=(
            "Fixture text for tests. The median acceptable premium for sustainable trainers was 10% among "
            "UK respondents; fewer than one in five accepted a premium above 20%."
        ),
        score=0.8,
        published=None,
    ),
]


class FakeSearch(SearchClient):
    def __init__(self, fail_on: str | None = None) -> None:
        self.calls: list[str] = []
        self.fail_on = fail_on

    def search(self, query: str, *, max_results: int = 6) -> list[SearchHit]:
        from intel.providers.errors import ProviderError

        self.calls.append(query)
        if self.fail_on is not None and self.fail_on in query:
            raise ProviderError("Tavily search failed (HTTP 500).")
        q = set(tokens(query))
        return [h for h in CORPUS if q & set(tokens(h.content))][:max_results]


PASSAGE = re.compile(r"\[(P\d+)\][^\n]*\n(.+?)(?=\n\n\[P\d+\]|\Z)", re.S)


class FakeLLM:
    """Deterministic stand-in. The verifier marks 'supports' when a passage sentence contains the
    claim's key numbers and most of its words, and it misquotes on purpose for claims containing 'misquote'."""

    model = "fake-llm"

    def __init__(self, fail_extract_on: str | None = None, fail_verify_on: str | None = None) -> None:
        self.fail_extract_on = fail_extract_on
        self.fail_verify_on = fail_verify_on

    def generate(self, *, system, prompt, schema, usage, temperature=0.2):
        from intel.providers.errors import ProviderError

        usage.llm_calls += 1
        if schema is S.Extraction and self.fail_extract_on and self.fail_extract_on in prompt:
            raise ProviderError("The language model failed for Extraction (HTTP 503 UNAVAILABLE: high demand)")
        if schema is S.Verification and self.fail_verify_on and self.fail_verify_on in prompt.split("\n", 1)[0]:
            raise ProviderError("The language model failed for Verification (HTTP 503 UNAVAILABLE: high demand)")
        if schema is S.Plan:
            return S.Plan(
                objective="Fixture objective",
                tasks=[
                    S.PlannedTask(
                        title="UK online footwear market growth",
                        category="Market",
                        rationale="Size",
                        queries=["uk online footwear sales growth"],
                    ),
                    S.PlannedTask(
                        title="Willingness to pay for sustainable trainers",
                        category="Customer",
                        rationale="Pricing",
                        queries=["sustainable trainers premium survey uk"],
                    ),
                    S.PlannedTask(
                        title="Competitor pricing",
                        category="Competition",
                        rationale="Positioning",
                        queries=["northfold trainer price"],
                    ),
                ],
            )
        if schema is S.Extraction:
            passages = PASSAGE.findall(prompt)
            claims = []
            for pid, text in passages:
                for sentence in re.split(r"(?<=[.;])\s+", text.strip()):
                    if "Fixture text" in sentence or len(sentence) < 25:
                        continue
                    claims.append(
                        S.ExtractedClaim(
                            text=sentence.rstrip("."),
                            kind="figure" if re.search(r"\d", sentence) else "fact",
                            passage_ids=[pid],
                        )
                    )
            if "Willingness" in prompt:
                claims[:0] = [
                    S.ExtractedClaim(
                        text="Customers will pay a premium of at least 20% for sustainable trainers",
                        kind="figure",
                        passage_ids=[],
                    ),
                    S.ExtractedClaim(
                        text="The UK sustainable trainer market will grow 12.4% a year to 2030",
                        kind="forecast",
                        passage_ids=[],
                    ),
                ]
            return S.Extraction(
                claims=claims[:6],
                missing=[
                    S.MissingItem(
                        item="Customer acquisition cost for UK trainers", impact="High", plan="Run a paid pilot"
                    )
                ],
            )
        if schema is S.Verification:
            claim = prompt.split("\n", 1)[0].removeprefix("Claim: ").strip()
            verdicts = []
            ctoks = set(tokens(claim))
            cnums = set(re.findall(r"\d+(?:\.\d+)?", claim))
            for pid, text in PASSAGE.findall(prompt.split("Passages:\n", 1)[1]):
                best, best_overlap = None, 0.0
                for sentence in re.split(r"(?<=[.;])\s+", text.strip()):
                    overlap = len(ctoks & set(tokens(sentence))) / max(1, len(ctoks))
                    if overlap > best_overlap:
                        best, best_overlap = sentence, overlap
                nums = set(re.findall(r"\d+(?:\.\d+)?", best or ""))
                if "at least 20%" in claim and "median acceptable premium" in text:
                    quote = "The median acceptable premium for sustainable trainers was 10%"
                    verdicts.append(
                        S.PassageVerdict(
                            passage_id=pid,
                            relation="contradicts",
                            confidence=0.9,
                            quote=quote,
                            scope_issue="",
                            note="Median is 10%.",
                        )
                    )
                elif best and best_overlap >= 0.7 and cnums <= nums:
                    quote = best if "misquote" not in claim else best + " (paraphrased)"
                    verdicts.append(
                        S.PassageVerdict(
                            passage_id=pid,
                            relation="supports",
                            confidence=0.88,
                            quote=quote,
                            scope_issue="",
                            note="States the claim.",
                        )
                    )
                else:
                    verdicts.append(
                        S.PassageVerdict(
                            passage_id=pid,
                            relation="neutral",
                            confidence=0.1,
                            quote="",
                            scope_issue="",
                            note="Topic only.",
                        )
                    )
            return S.Verification(verdicts=verdicts)
        if schema is S.Analysis:
            keys = re.findall(r"^(C\d+) \[(\w+)\]", prompt, re.M)
            supported = [k for k, st in keys if st in ("supported", "partial")] or ["C99"]
            item = lambda t: S.CitedItem(text=t, claims=supported[:1])  # noqa: E731
            return S.Analysis(
                competitors=[
                    S.Competitor(
                        name="Northfold",
                        positioning="Premium D2C",
                        price_note="£150",
                        strengths="Brand",
                        weaknesses="Price",
                        claims=supported[-1:],
                    ),
                    S.Competitor(
                        name="Invented Co", positioning="Unknown", price_note="", strengths="", weaknesses="", claims=[]
                    ),
                ],
                swot=S.Swot(
                    strengths=[item("Growing online channel")],
                    weaknesses=[S.CitedItem(text="No UK awareness", claims=[])],
                    opportunities=[item("Premium share")],
                    threats=[item("Price-sensitive buyers")],
                ),
                pestle=[S.PestleItem(factor="Economic", rating=3, note="Growth", claims=supported[:1])],
                porter=[S.PorterForce(force="Rivalry", level=3.5, rationale="Several brands", claims=supported[-1:])],
                factors=[
                    S.FactorScore(key="attract", score=70, rationale="Growth", claims=supported[:1]),
                    S.FactorScore(key="econ", score=90, rationale="Guess", claims=[]),
                ],
                assumptions=[
                    S.AssumptionSuggestion(key=k, value=v, claim="", note="estimate")
                    for k, v in {
                        "price": 150,
                        "gross_margin": 0.6,
                        "return_rate": 0.3,
                        "cac": 55,
                        "marketing": 30000,
                        "repeat_rate": 0.35,
                        "fixed_costs": 15000,
                        "launch_cost": 150000,
                    }.items()
                ],
            )
        if schema is S.Narrative:
            return S.Narrative(
                headline="Run a capped pilot before full entry",
                summary="Online growth is evidenced [C1]. Margins of 47% are assumed [C42].",
                conditions=["Measured CAC at or below the assumed 55 by month 4"],
                would_change=["A survey showing a lower premium"],
            )
        raise AssertionError(f"unexpected schema {schema}")
