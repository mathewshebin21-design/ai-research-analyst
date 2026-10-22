import httpx
import pytest

from intel.user_evidence import EvidenceRejected, fetch_url
from tests.conftest import login
from tests.test_api import _completed_run


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://10.0.0.5/",
        "http://169.254.169.254/latest/meta-data",
        "http://[::1]/",
        "file:///etc/passwd",
        "ftp://example.com/x",
    ],
)
def test_fetch_refuses_internal_and_non_http_addresses(url):
    with pytest.raises(EvidenceRejected):
        fetch_url(url)


def test_fetch_extracts_text_and_follows_safe_redirects():
    pages = {
        "https://a.example/old": httpx.Response(301, headers={"location": "/new"}),
        "https://a.example/new": httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text=(
                "<html><title>Panel note</title><script>x()</script>"
                "<p>Online footwear sales in the United Kingdom grew by 6.5% in 2025.</p></html>"
            ),
        ),
    }
    transport = httpx.MockTransport(lambda req: pages[str(req.url)])
    f = fetch_url("https://a.example/old", transport)
    assert f.url == "https://a.example/new" and f.title == "Panel note"
    assert "grew by 6.5%" in f.pages[0][1] and "x()" not in f.pages[0][1]


def test_fetch_rejects_oversized_and_non_text():
    big = httpx.MockTransport(
        lambda r: httpx.Response(200, headers={"content-type": "text/html"}, content=b"a" * (3 * 1024 * 1024 + 10))
    )
    with pytest.raises(EvidenceRejected, match="too large"):
        fetch_url("https://a.example/big", big)
    img = httpx.MockTransport(lambda r: httpx.Response(200, headers={"content-type": "image/png"}, content=b"\x89PNG"))
    with pytest.raises(EvidenceRejected, match="Only web pages"):
        fetch_url("https://a.example/x.png", img)


def test_pasted_evidence_upgrades_a_claim_and_the_decision(client):
    h = login(client)
    ws, d = _completed_run(client, h)
    partial = next(c for c in d["claims"] if c["status"] == "partial" and c["text"].startswith("Competitor Northfold"))
    r = client.post(
        f"/runs/{d['id']}/claims/{partial['id']}/evidence",
        json={
            "text": "Competitor Northfold prices its core trainer at £150 and sells direct, our store audit found.",
            "title": "Store audit",
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    res = r.json()["result"]
    assert res["previous_status"] == "partial" and res["status"] == "supported"  # second independent source
    claim = next(c for c in r.json()["run"]["claims"] if c["id"] == partial["id"])
    assert any(e["quote"] and "Northfold" in e["quote"] for e in claim["evidence"])
    src = next(s for s in r.json()["run"]["sources"] if s["key"] == res["source_key"])
    assert src["publisher"].startswith("Added by user") and src["tier"] == "B"


def test_unrelated_evidence_does_not_count_as_support(client):
    h = login(client)
    ws, d = _completed_run(client, h)
    target = next(c for c in d["claims"] if c["status"] == "unsupported")
    r = client.post(
        f"/runs/{d['id']}/claims/{target['id']}/evidence",
        json={"text": "Sustainable trainers are popular and brands talk about growth all the time in the UK market."},
        headers=h,
    ).json()
    assert r["result"]["status"] == "unsupported"


def test_evidence_input_validation_and_roles(client):
    ana, ben = login(client, "ana@example.com"), login(client, "ben@example.com")
    ws, d = _completed_run(client, ana)
    c = d["claims"][0]
    url = f"/runs/{d['id']}/claims/{c['id']}/evidence"
    assert client.post(url, json={}, headers=ana).status_code == 422
    assert client.post(url, json={"text": "short"}, headers=ana).status_code == 422
    assert client.post(url, json={"url": "http://127.0.0.1/"}, headers=ana).status_code == 422
    client.post(f"/workspaces/{ws['id']}/members", json={"email": "ben@example.com", "role": "viewer"}, headers=ana)
    assert client.post(url, json={"text": "x" * 50}, headers=ben).status_code == 403


def test_dispute_counts_claim_as_no_evidence_until_cleared(client):
    h = login(client)
    ws, d = _completed_run(client, h)
    supported = next(c for c in d["claims"] if c["status"] == "supported" and c["task"] == "T1")
    before = d["decision"]["overall"]
    after = client.post(
        f"/runs/{d['id']}/claims/{supported['id']}/dispute", json={"note": "Panel excludes marketplaces"}, headers=h
    ).json()
    claim = next(c for c in after["claims"] if c["id"] == supported["id"])
    assert claim["user_flag"] == "disputed" and claim["status"] == "supported"  # the evidence is unchanged...
    assert any(f["code"] == "disputed" for f in after["findings"])
    attract = next(f for f in after["decision"]["factors"] if f["key"] == "attract")
    assert attract["coverage"] < 1  # ...but it no longer counts towards the decision
    cleared = client.delete(f"/runs/{d['id']}/claims/{supported['id']}/dispute", headers=h).json()
    assert cleared["decision"]["overall"] == before and not any(f["code"] == "disputed" for f in cleared["findings"])
