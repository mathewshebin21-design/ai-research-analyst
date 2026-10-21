"""Measure the verifier against hand-labelled pairs with the real model.

Usage: GEMINI_API_KEY=... python -m eval.run_eval [--model gemini-3.8-flash]
Writes eval/results/<date>-<model>.json and .md. Re-run after any prompt or model change.
"""

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from intel.config import get_settings
from intel.pipeline.passages import Passage
from intel.pipeline.verify import verify_claim
from intel.providers.llm import GeminiLLM
from intel.providers.usage import Usage

HERE = Path(__file__).parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=get_settings().llm_model)
    args = ap.parse_args()
    st = get_settings()
    llm = GeminiLLM(st.gemini_api_key, args.model, st.llm_attempts, st.llm_fallback_models)
    usage = Usage()
    rows = [json.loads(line) for line in (HERE / "verifier_pairs.jsonl").read_text().splitlines()]
    results = []
    for r in rows:
        p = Passage("P1", "s", "S1", "eval", "B", r["passage"], None)
        judged = verify_claim(llm, r["claim"], [(p, 1.0)], usage)
        got = judged[0].relation if judged else "related"
        got = {"related": "neutral"}.get(got, got)
        results.append(
            {
                **r,
                "predicted": got,
                "entailment": judged[0].entailment if judged else 0.0,
                "quote": judged[0].quote if judged else None,
                "note_model": judged[0].note if judged else "",
            }
        )
    cm = Counter((x["label"], x["predicted"]) for x in results)
    labels = ["supports", "contradicts", "neutral"]

    def precision(lbl):
        tp = cm[(lbl, lbl)]
        pred = sum(cm[(t, lbl)] for t in labels)
        return tp / pred if pred else None

    def recall(lbl):
        tp = cm[(lbl, lbl)]
        actual = sum(cm[(lbl, p)] for p in labels)
        return tp / actual if actual else None

    neutral_total = sum(cm[("neutral", p)] for p in labels)
    metrics = {
        "model": args.model,
        "run_at": datetime.now(UTC).isoformat(),
        "n": len(results),
        "accuracy": sum(cm[(lbl, lbl)] for lbl in labels) / len(results),
        "supports_precision": precision("supports"),
        "supports_recall": recall("supports"),
        "contradicts_precision": precision("contradicts"),
        "contradicts_recall": recall("contradicts"),
        "false_support_rate_on_relevant_neutral": cm[("neutral", "supports")] / neutral_total
        if neutral_total
        else None,
        "confusion": {f"{t}->{p}": cm[(t, p)] for t in labels for p in labels},
        "usage": usage.as_dict(),
    }
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    stem = f"{datetime.now(UTC):%Y-%m-%d}-{args.model}"
    (out / f"{stem}.json").write_text(json.dumps({"metrics": metrics, "results": results}, indent=2))
    lines = [f"# Verifier evaluation: {args.model}", "", f"Run {metrics['run_at']}, {len(results)} pairs.", ""]
    for k in (
        "accuracy",
        "supports_precision",
        "supports_recall",
        "contradicts_precision",
        "contradicts_recall",
        "false_support_rate_on_relevant_neutral",
    ):
        v = metrics[k]
        lines.append(f"- **{k}**: {v:.2f}" if v is not None else f"- **{k}**: n/a")
    lines += ["", "| ID | Label | Predicted | Note |", "| --- | --- | --- | --- |"]
    lines += [
        f"| {x['id']} | {x['label']} | {x['predicted']} | {x['note']} |"
        for x in results
        if x["label"] != x["predicted"]
    ]
    (out / f"{stem}.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(metrics, indent=2))
    if (metrics["supports_precision"] or 0) < 0.9:
        raise SystemExit("supports precision below the 0.90 target")


if __name__ == "__main__":
    main()
