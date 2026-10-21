import json
from collections import Counter
from pathlib import Path

ROWS = [json.loads(x) for x in (Path(__file__).parents[1] / "eval" / "verifier_pairs.jsonl").read_text().splitlines()]


def test_dataset_is_well_formed_and_balanced():
    assert len({r["id"] for r in ROWS}) == len(ROWS) >= 30
    counts = Counter(r["label"] for r in ROWS)
    assert set(counts) == {"supports", "contradicts", "neutral"}
    assert counts["neutral"] >= counts["supports"], "relevant-but-unsupported cases must be well represented"
