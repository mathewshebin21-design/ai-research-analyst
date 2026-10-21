import io

import httpx
import pytest
from reportlab.pdfgen import canvas

from intel.providers.errors import ProviderError, ProviderNotConfigured
from intel.providers.search import TavilyClient
from intel.rag.pdf import UploadRejected, chunk_pages, storage_path, validate_pdf


def test_tavily_requires_key():
    with pytest.raises(ProviderNotConfigured):
        TavilyClient(None)


def test_tavily_parses_results_and_sends_bearer(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers["authorization"]
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://a.example/x",
                        "title": "A",
                        "content": "short",
                        "raw_content": "full text",
                        "score": 0.7,
                    },
                    {"url": "https://b.example/y", "title": "B", "content": "", "raw_content": None},
                ]
            },
        )

    hits = TavilyClient("tvly-test", transport=httpx.MockTransport(handler)).search("q")
    assert seen["auth"] == "Bearer tvly-test"
    assert [h.content for h in hits] == ["full text"]  # empty results are dropped, raw content preferred


def test_tavily_errors_raise_instead_of_returning_fake_results(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        return httpx.Response(401 if "auth" in request.content.decode() else 503)

    with pytest.raises(ProviderError, match="HTTP 401"):
        TavilyClient("k", transport=httpx.MockTransport(handler)).search("auth problem")
    assert calls["n"] == 1  # auth errors are not retried
    calls["n"] = 0
    with pytest.raises(ProviderError, match="HTTP 503"):
        TavilyClient("k", transport=httpx.MockTransport(handler)).search("outage")
    assert calls["n"] == 3


def make_pdf(pages: list[str]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    for text in pages:
        y = 800
        for line in text.split("\n"):
            c.drawString(40, y, line)
            y -= 14
        c.showPage()
    c.save()
    return buf.getvalue()


def test_pdf_chunks_keep_page_numbers():
    data = make_pdf(
        ["Page one says the market grew by seven percent last year.", "Page two lists competitor prices in detail."]
    )
    pages = validate_pdf(data, max_bytes=10_000_000, max_pages=10)
    chunks = chunk_pages(pages)
    assert [c[0] for c in chunks] == [1, 2]
    assert "competitor prices" in chunks[1][2]


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"", "empty"),
        (b"MZ\x90\x00 not a pdf", "Only PDF"),
        (b"%PDF-1.4 garbage", "could not be read"),
    ],
)
def test_pdf_rejections(data, message):
    with pytest.raises(UploadRejected, match=message):
        validate_pdf(data, max_bytes=1000, max_pages=10)


def test_pdf_limits():
    data = make_pdf(["a" * 50] * 3)
    with pytest.raises(UploadRejected, match="larger than"):
        validate_pdf(data, max_bytes=10, max_pages=10)
    with pytest.raises(UploadRejected, match="3 pages"):
        validate_pdf(data, max_bytes=10_000_000, max_pages=2)


def test_storage_keys_cannot_escape_directory():
    for bad in ("../etc/passwd", "a/b.pdf", ".hidden"):
        with pytest.raises(ValueError):
            storage_path("storage", bad)
