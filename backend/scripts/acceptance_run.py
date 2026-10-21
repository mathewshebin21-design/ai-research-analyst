"""Record a real acceptance run: real Tavily search, real language model, full pipeline.

Usage (from backend/):
    TAVILY_API_KEY=... GEMINI_API_KEY=... python -m scripts.acceptance_run \\
        "Should <company> launch <product> in <market> in <year>?"

Writes docs/redesign/evidence/acceptance/<timestamp>/ with the full run JSON, the exported PDF,
the verifier evaluation if requested, and a Markdown summary of what the run found.
"""

import json
import os
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Pass the market-entry question as the first argument.")
    if not (os.environ.get("TAVILY_API_KEY") and os.environ.get("GEMINI_API_KEY")):
        raise SystemExit("Set TAVILY_API_KEY and GEMINI_API_KEY; this script never uses fakes.")
    question = sys.argv[1]
    tmp = tempfile.mkdtemp(prefix="intel-acceptance-")
    os.environ.update(
        ENVIRONMENT="test",
        AUTH_MODE="dev",
        DATABASE_URL=f"sqlite:///{tmp}/run.db",
        STORAGE_DIR=f"{tmp}/storage",
        WORKER_IN_PROCESS="false",
    )

    from fastapi.testclient import TestClient

    from intel.db import Base, init_engine
    from intel.main import create_app
    from intel.worker import process_one

    Base.metadata.create_all(init_engine(os.environ["DATABASE_URL"]))
    out = ROOT / "docs" / "redesign" / "evidence" / "acceptance" / datetime.now(UTC).strftime("%Y-%m-%dT%H%M")
    out.mkdir(parents=True, exist_ok=True)
    with TestClient(create_app(start_worker=False)) as c:
        token = c.post("/dev/token", json={"email": "acceptance@example.com"}).json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        v = c.get("/legal/versions").json()
        c.post("/me/accept-terms", json={"terms_version": v["terms"], "privacy_version": v["privacy"]}, headers=h)
        ws = c.post("/workspaces", json={"name": "Acceptance"}, headers=h).json()
        r = c.post(f"/workspaces/{ws['id']}/runs", json={"question": question}, headers=h)
        if r.status_code != 201:
            reason = f"Planning failed ({r.status_code}): {r.json().get('detail')}"
            (out / "SUMMARY.md").write_text(
                f"# Acceptance run {out.name}: failed\n\n**Question:** {question}\n\n**Error:** {reason}\n"
            )
            raise SystemExit(reason)
        run = r.json()
        print(f"Plan: {len(run['tasks'])} tasks")
        c.post(f"/runs/{run['id']}/start", headers=h).raise_for_status()
        process_one()
        detail = c.get(f"/runs/{run['id']}", headers=h).json()
        (out / "run.json").write_text(json.dumps(detail, indent=2))
        if detail["status"] != "completed":
            (out / "SUMMARY.md").write_text(
                f"# Acceptance run {out.name}: failed\n\n**Question:** {question}\n\n"
                f"**Error:** {detail['error']}\n\n**Usage:** {detail['usage']}\n\nEvents:\n\n"
                + "\n".join(f"- {e['agent']}: {e['message']}" for e in detail["events"])
                + "\n"
            )
            raise SystemExit(f"Run failed: {detail['error']}")
        rep = c.post(f"/runs/{run['id']}/reports", headers=h).json()
        (out / "report.pdf").write_bytes(c.get(rep["download"], headers=h).content)

    counts: dict[str, int] = {}
    for cl in detail["claims"]:
        counts[cl["status"]] = counts.get(cl["status"], 0) + 1
    rec = detail["recommendation"] or {}
    lines = [
        f"# Acceptance run {out.name}",
        "",
        f"**Question:** {question}",
        "",
        f"- Model: {detail['settings'].get('llm_model')}; status rules {detail['settings'].get('status_rules')}",
        f"- Usage: {detail['usage']}",
        f"- Sources: {len(detail['sources'])} ({', '.join(sorted({s['tier'] for s in detail['sources']}))} tiers)",
        f"- Claims: {len(detail['claims'])} " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())),
        f"- Findings: {len(detail['findings'])} ({sum(f['severity'] == 'high' for f in detail['findings'])} high)",
        f"- Verdict: **{rec.get('verdict')}**, score {rec.get('overall')}, confidence {rec.get('confidence_label')}",
        "",
        "## Sources",
        "",
        *[
            f"- {s['key']} [{s['title']}]({s['url']}) · {s['publisher']} · tier {s['tier']}"
            for s in detail["sources"]
            if s["url"]
        ],
        "",
        "## Claims",
        "",
        *[f"- {cl['key']} **{cl['status']}**: {cl['text']}" for cl in detail["claims"]],
    ]
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    print(f"Recorded in {out}")


if __name__ == "__main__":
    main()
