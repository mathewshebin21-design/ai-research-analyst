from datetime import UTC, datetime, timedelta

from intel import growth
from intel.config import get_settings
from intel.db import session_factory
from intel.models import Claim, Job, Run
from tests.conftest import login
from tests.test_api import _completed_run


def test_usage_meter_counts_started_runs(client):
    h = login(client)
    ws, d = _completed_run(client, h)
    u = client.get(f"/workspaces/{ws['id']}/usage", headers=h).json()
    assert u["runs_used"] == 1 and u["remaining"] == u["limit"] - 1
    assert u["period_end"] > u["period_start"]
    assert (
        client.get(f"/workspaces/{ws['id']}/usage", headers=login(client, "eve@example.com")).status_code == 404
    )  # not a member


def test_refresh_copies_plan_and_reports_what_changed(client):
    from intel.worker import process_one

    h = login(client)
    ws, d = _completed_run(client, h)
    weights = {"attract": 1, "demand": 1, "compete": 0, "econ": 0, "exec": 0}
    client.post(f"/runs/{d['id']}/decision", json={"weights": weights, "save": True}, headers=h)
    r = client.post(f"/runs/{d['id']}/refresh", headers=h)
    assert r.status_code == 201
    new = r.json()
    assert new["status"] == "planned" and new["previous_run_id"] == d["id"] and new["changes"] is None
    assert [t["queries"] for t in new["tasks"]] == [t["queries"] for t in d["tasks"]]

    # Make the earlier run differ: one claim had a different status, one claim was not found then.
    with session_factory()() as db:
        old_claims = db.query(Claim).filter_by(run_id=d["id"]).all()
        old_claims[0].status = "unsupported"
        db.delete(old_claims[1])
        db.commit()

    client.post(f"/runs/{new['id']}/start", headers=h)
    process_one()
    after = client.get(f"/runs/{new['id']}", headers=h).json()
    ch = after["changes"]
    assert ch["previous_run_id"] == d["id"]
    assert after["decision"]["custom_weights"] is True and after["decision"]["weights"]["compete"] == 0
    assert ch["verdict"]["after"] == after["decision"]["verdict"]
    assert any(c["before"]["status"] == "unsupported" for c in ch["claims_changed"])
    assert len(ch["claims_new"]) == 1 and ch["claims_dropped"] == []
    assert ch["sources_new"] == [] and ch["sources_dropped"] == []  # same fixtures both times
    assert client.get(f"/workspaces/{ws['id']}/usage", headers=h).json()["runs_used"] == 2


def test_refresh_needs_editor_and_completed_run(client):
    h = login(client)
    ws, d = _completed_run(client, h)
    viewer = login(client, "vic@example.com")
    client.post(f"/workspaces/{ws['id']}/members", json={"email": "vic@example.com", "role": "viewer"}, headers=h)
    assert client.post(f"/runs/{d['id']}/refresh", headers=viewer).status_code == 403
    planned = client.post(f"/runs/{d['id']}/refresh", headers=h).json()
    assert client.post(f"/runs/{planned['id']}/refresh", headers=h).status_code == 409


def test_monthly_refresh_is_opt_in_and_queues_once(client):
    h = login(client)
    ws, d = _completed_run(client, h)
    settings = get_settings()
    later = datetime.now(UTC) + timedelta(days=31)
    with session_factory()() as db:
        assert growth.due_refreshes(db, settings, later) == []  # not asked for
    assert client.put(f"/runs/{d['id']}/refresh-schedule", json={"monthly": True}, headers=h).json() == {
        "refresh_monthly": True
    }
    assert client.get(f"/runs/{d['id']}", headers=h).json()["refresh_monthly"] is True
    with session_factory()() as db:
        assert growth.due_refreshes(db, settings, datetime.now(UTC)) == []  # not a month old yet
        queued = growth.due_refreshes(db, settings, later)
        assert len(queued) == 1
        new = db.get(Run, queued[0])
        assert new.status == "queued" and new.previous_run_id == d["id"]
        assert new.context["refresh_monthly"] is True and db.get(Run, d["id"]).context["refresh_monthly"] is False
        assert db.query(Job).filter_by(run_id=new.id).count() == 1
        assert growth.due_refreshes(db, settings, later) == []  # only once


def test_sample_report_is_public_and_labelled(client, tmp_path, monkeypatch):
    from intel import export_sample

    monkeypatch.setattr(growth, "SAMPLE_PATH", tmp_path / "sample.json")
    monkeypatch.setattr(export_sample, "SAMPLE_PATH", tmp_path / "sample.json")
    assert client.get("/sample").status_code == 404
    h = login(client)
    ws, d = _completed_run(client, h)
    export_sample.export(d["id"], "Illustrative sample.")
    body = client.get("/sample").json()
    assert body["sample"] is True and body["shared"] is True and body["sample_note"] == "Illustrative sample."
    assert body["workspace_name"] == "Sample" and "events" not in body and "dev-" not in str(body)
