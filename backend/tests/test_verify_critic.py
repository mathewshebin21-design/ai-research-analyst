from intel.pipeline import critic
from intel.pipeline.passages import Passage
from intel.pipeline.verify import verify_claim
from intel.providers.usage import Usage
from tests.fakes import FakeLLM

P = Passage(
    "P1", "s1", "S1", "ons.gov.uk", "A", "Online footwear sales in the United Kingdom grew by 6.5% in 2025.", None
)


def test_supported_verdict_keeps_exact_quote_span():
    [j] = verify_claim(
        FakeLLM(), "Online footwear sales in the United Kingdom grew by 6.5% in 2025", [(P, 1.0)], Usage()
    )
    assert j.relation == "supports"
    assert P.text[j.quote_span[0] : j.quote_span[1]] == j.quote


def test_unquotable_verdict_is_discarded():
    [j] = verify_claim(
        FakeLLM(), "misquote Online footwear sales in the United Kingdom grew by 6.5% in 2025", [(P, 1.0)], Usage()
    )
    assert j.relation == "related" and j.entailment == 0.0
    assert "discarded" in j.note


def test_topic_match_without_statement_is_related_only():
    [j] = verify_claim(FakeLLM(), "UK sustainable trainers will grow 12.4% a year", [(P, 0.9)], Usage())
    assert j.relation == "related"
    assert j.relevance == 0.9 and j.entailment == 0.0


def test_unsourced_numbers_flags_new_figures_only():
    allowed = ["Online sales grew by 6.5% in 2025", "55"]
    assert critic.unsourced_numbers("Growth of 6.5% since 2025 and CAC of 55 [C1]", allowed) == []
    assert critic.unsourced_numbers("Margins of 47% are assumed", allowed) == ["47%"]


def test_review_claims_severity():
    views = [
        critic.ClaimView("1", "C1", "forecast", "unsupported", "x", [], [], 0),
        critic.ClaimView("2", "C2", "fact", "contradicted", "x", ["A"], [], 1),
        critic.ClaimView("3", "C3", "fact", "partial", "x", ["B"], [], 1),
        critic.ClaimView("4", "C4", "fact", "supported", "x", ["C", "C"], [], 2),
    ]
    out = {f.code: f.severity for f in critic.review_claims(views, failed_searches=1, total_searches=10)}
    assert out == {
        "unsupported": "high",
        "contradicted": "high",
        "single_source": "low",
        "low_tier": "medium",
        "search_failures": "low",
    }
