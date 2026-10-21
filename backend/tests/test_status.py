import pytest

from intel.pipeline.status import LinkView, derive_status


def L(relation, ent, tier="B", pub="a.example", scope=None):  # noqa: N802
    return LinkView(relation, ent, tier, pub, scope)


@pytest.mark.parametrize(
    ("links", "expected"),
    [
        ([], "missing"),
        ([L("related", 0.0)], "unsupported"),  # relevant but never stated: relevance is not support
        ([L("supports", 0.9, "A")], "supported"),  # one official source is enough
        ([L("supports", 0.9, "B", "a"), L("supports", 0.8, "B", "b")], "supported"),  # two independent publishers
        ([L("supports", 0.9, "B", "a"), L("supports", 0.8, "B", "a")], "partial"),  # same publisher twice is one source
        ([L("supports", 0.9, "B")], "partial"),  # single tier-B source
        ([L("supports", 0.95, "A", scope="France, not Germany")], "partial"),  # scope mismatch
        ([L("supports", 0.5, "A")], "partial"),  # weak support
        ([L("supports", 0.9, "B"), L("contradicts", 0.9, "A")], "contradicted"),
        (
            [L("supports", 0.9, "A"), L("contradicts", 0.9, "C")],
            "supported",
        ),  # lower tier disagreement noted, not decisive
        ([L("contradicts", 0.5, "A")], "partial"),
    ],
)
def test_derive_status(links, expected):
    assert derive_status(links)[0] == expected


def test_reason_explains_relevance_is_not_support():
    assert "Relevance is not support" in derive_status([L("related", 0.0)])[1]
