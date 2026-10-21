import io

from tests.conftest import login
from tests.test_search_pdf import make_pdf


def test_health_and_auth_required(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/workspaces").status_code == 401
    assert client.get("/workspaces", headers={"Authorization": "Bearer nonsense"}).status_code == 401
    r = client.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["x-request-id"]


def test_terms_must_be_accepted_first(client):
    h = login(client, accept=False)
    r = client.get("/workspaces", headers=h)
    assert r.status_code == 403 and r.json()["detail"]["code"] == "terms_required"
    assert (
        client.post("/me/accept-terms", json={"terms_version": "old", "privacy_version": "old"}, headers=h).status_code
        == 409
    )
    assert client.get("/me", headers=h).json()["needs_terms"] is True


def test_workspace_isolation_and_roles(client):
    ana, ben = login(client, "ana@example.com"), login(client, "ben@example.com")
    ws = client.post("/workspaces", json={"name": "Ana"}, headers=ana).json()
    assert client.get(f"/workspaces/{ws['id']}/runs", headers=ben).status_code == 404  # not even existence leaks
    assert (
        client.post(
            f"/workspaces/{ws['id']}/members", json={"email": "ben@example.com", "role": "viewer"}, headers=ana
        ).status_code
        == 201
    )
    assert client.get(f"/workspaces/{ws['id']}/runs", headers=ben).status_code == 200
    r = client.post(
        f"/workspaces/{ws['id']}/runs", json={"question": "Should we enter the UK trainer market?"}, headers=ben
    )
    assert r.status_code == 403  # viewers cannot spend the workspace's budget


def test_rate_limit_returns_429(client, monkeypatch):
    from intel.api import deps

    h = login(client)
    deps._limiters.clear()
    monkeypatch.setattr(
        deps,
        "limiter",
        lambda name, per_minute: deps.TokenBucketLimiter(2) if name not in deps._limiters else deps._limiters[name],
    )
    deps._limiters["default"] = deps.TokenBucketLimiter(2)
    codes = [client.get("/workspaces", headers=h).status_code for _ in range(4)]
    assert codes[:2] == [200, 200] and 429 in codes[2:]


def test_dev_tokens_refused_in_production(settings_env, monkeypatch):
    import pytest

    from intel.config import get_settings
    from intel.main import create_app

    monkeypatch.setenv("ENVIRONMENT", "production")
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="not allowed in production"):
        create_app(start_worker=False)


def test_full_research_journey(client, fake_providers, settings_env):
    from intel.worker import process_one

    h = login(client)
    ws = client.post("/workspaces", json={"name": "Market entry"}, headers=h).json()

    pdf = make_pdf(["Internal memo. Online footwear sales in the United Kingdom grew by 6.5% in 2025."])
    doc = client.post(
        f"/workspaces/{ws['id']}/documents",
        files={"file": ("../../memo.pdf", io.BytesIO(pdf), "application/pdf")},
        headers=h,
    )
    assert doc.status_code == 201, doc.text
    assert doc.json()["filename"] == "memo.pdf"
    bad = client.post(
        f"/workspaces/{ws['id']}/documents",
        files={"file": ("x.pdf", io.BytesIO(b"hello"), "application/pdf")},
        headers=h,
    )
    assert bad.status_code == 422

    run = client.post(
        f"/workspaces/{ws['id']}/runs",
        json={
            "question": "Should we launch sustainable trainers online in the UK in 2027?",
            "document_ids": [doc.json()["id"]],
        },
        headers=h,
    ).json()
    assert run["status"] == "planned" and len(run["tasks"]) == 3

    plan = [{"title": t["title"], "category": t["category"], "queries": t["queries"]} for t in run["tasks"]]
    plan[2]["queries"] = ["northfold trainer price uk"]
    assert client.put(f"/runs/{run['id']}/plan", json={"tasks": plan}, headers=h).status_code == 200
    assert client.post(f"/runs/{run['id']}/start", headers=h).json()["status"] == "queued"
    assert process_one() is True

    d = client.get(f"/runs/{run['id']}", headers=h).json()
    assert d["status"] == "completed", d["error"]
    by_text = {c["text"]: c for c in d["claims"]}

    growth = by_text["Online footwear sales in the United Kingdom grew by 6.5% in 2025"]
    assert growth["status"] == "supported"
    quote = growth["evidence"][0]
    assert quote["quote"] and quote["quote"] in quote["passage"]
    assert by_text["Customers will pay a premium of at least 20% for sustainable trainers"]["status"] == "contradicted"
    forecast = by_text["The UK sustainable trainer market will grow 12.4% a year to 2030"]
    assert forecast["status"] in ("unsupported", "missing")
    assert any(e["page"] == 1 for c in d["claims"] for e in c["evidence"]), "uploaded PDF evidence carries page numbers"

    codes = {f["code"] for f in d["findings"]}
    assert {"contradicted", "unsourced_number"} <= codes  # the narrative's invented 47% is caught
    assert any(m["item"].startswith("Customer acquisition cost") for m in d["missing"])

    names = [c["name"] for c in d["competitors"]]
    assert "Northfold" in names and "Invented Co" not in names  # uncited competitors are dropped
    econ = next(f for f in d["factors"] if f["key"] == "econ")
    assert econ["score"] == 50 and econ["model_score"] == 90  # unevidenced score held at neutral
    assert d["recommendation"]["verdict"] in ("Go", "Conditional go", "No-go", "Insufficient evidence")
    assert d["scenario"]["version"] == 1 and all(
        v["origin"] == "estimate" for v in d["scenario"]["assumptions"].values()
    )
    assert d["usage"]["searches"] == 3 and d["usage"]["llm_calls"] > 0

    changed = {k: {**v, "origin": "user"} for k, v in d["scenario"]["assumptions"].items()}
    changed["cac"]["value"] = 80
    s2 = client.post(f"/runs/{run['id']}/scenarios", json={"assumptions": changed}, headers=h).json()
    assert s2["version"] == 2
    assert s2["results"]["scenarios"]["base"]["cash_36"] < d["scenario"]["results"]["scenarios"]["base"]["cash_36"]

    rep = client.post(f"/runs/{run['id']}/reports", params={"scenario_id": s2["id"]}, headers=h).json()
    pdf_bytes = client.get(rep["download"], headers=h)
    assert pdf_bytes.status_code == 200 and pdf_bytes.content.startswith(b"%PDF")

    cmp = client.get("/compare", params={"a": run["id"], "b": run["id"]}, headers=h).json()
    assert cmp["runs"][0]["claims"]["supported"] >= 1

    export = client.get("/me/export", headers=h).json()
    assert export["workspaces"][0]["runs"][0]["id"] == run["id"]

    storage = settings_env / "storage"
    assert any(storage.iterdir())
    assert client.delete("/me", headers=h).json() == {"deleted": True}
    assert not any(storage.iterdir()), "uploaded documents and reports are erased with the account"


def test_failed_search_service_fails_run_with_message(client, fake_providers):
    from intel.worker import process_one

    fake_providers.fail_on = ""  # every query fails
    h = login(client)
    ws = client.post("/workspaces", json={"name": "W"}, headers=h).json()
    run = client.post(
        f"/workspaces/{ws['id']}/runs", json={"question": "Should we launch trainers in the UK?"}, headers=h
    ).json()
    client.post(f"/runs/{run['id']}/start", headers=h)
    process_one()
    d = client.get(f"/runs/{run['id']}", headers=h).json()
    assert d["status"] == "failed"
    assert "No sources could be collected" in d["error"]
    assert d["claims"] == []  # nothing is invented when research fails


def test_monthly_run_cap(client, monkeypatch):
    from intel.config import get_settings

    monkeypatch.setenv("RUNS_PER_WORKSPACE_PER_MONTH", "1")
    get_settings.cache_clear()
    h = login(client)
    ws = client.post("/workspaces", json={"name": "W"}, headers=h).json()
    ids = [
        client.post(
            f"/workspaces/{ws['id']}/runs", json={"question": f"Should we enter market number {i}?"}, headers=h
        ).json()["id"]
        for i in range(2)
    ]
    assert client.post(f"/runs/{ids[0]}/start", headers=h).status_code == 200
    from intel.db import session_factory
    from intel.models import Run

    with session_factory()() as s:
        from datetime import UTC, datetime

        s.get(Run, ids[0]).started_at = datetime.now(UTC)
        s.commit()
    assert client.post(f"/runs/{ids[1]}/start", headers=h).status_code == 429
