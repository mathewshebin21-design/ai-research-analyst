"""Tavily web search with retries and a shared cache. Failures raise; they are never results."""

import hashlib
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy.orm import Session

from intel.models import SearchCache
from intel.providers.errors import ProviderError, ProviderNotConfigured

TAVILY_URL = "https://api.tavily.com/search"
CACHE_TTL = timedelta(days=7)


@dataclass
class SearchHit:
    url: str
    title: str
    content: str
    score: float | None
    published: str | None


class SearchClient:
    def search(self, query: str, *, max_results: int = 6) -> list[SearchHit]: ...


class TavilyClient(SearchClient):
    def __init__(self, api_key: str | None, *, timeout: float = 30.0, transport: httpx.BaseTransport | None = None):
        if not api_key:
            raise ProviderNotConfigured("TAVILY_API_KEY is not set, so web research cannot run.")
        self._key = api_key
        self._http = httpx.Client(timeout=timeout, transport=transport)

    def search(self, query: str, *, max_results: int = 6) -> list[SearchHit]:
        payload = {
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_raw_content": True,
            "include_answer": False,
        }
        headers = {"Authorization": f"Bearer {self._key}"}
        last = "no response"
        for attempt in range(3):
            try:
                r = self._http.post(TAVILY_URL, json=payload, headers=headers)
            except httpx.HTTPError as exc:
                last = type(exc).__name__
            else:
                if r.status_code == 200:
                    return [
                        SearchHit(
                            url=item.get("url") or "",
                            title=(item.get("title") or "").strip() or "Untitled",
                            content=(item.get("raw_content") or item.get("content") or "").strip(),
                            score=item.get("score"),
                            published=item.get("published_date"),
                        )
                        for item in r.json().get("results", [])
                        if item.get("url") and (item.get("raw_content") or item.get("content"))
                    ]
                last = f"HTTP {r.status_code}"
                if r.status_code in (400, 401, 403, 432, 433):  # bad request, auth, plan/credit limits
                    break
            time.sleep(1.0 * (2**attempt))
        raise ProviderError(f"Tavily search failed ({last}).")


def cache_key(query: str, max_results: int) -> str:
    return hashlib.sha256(f"tavily|advanced|{max_results}|{query.strip().lower()}".encode()).hexdigest()


def cached_search(db: Session, client: SearchClient, query: str, max_results: int = 6) -> tuple[list[SearchHit], bool]:
    key = cache_key(query, max_results)
    row = db.get(SearchCache, key)
    if row is not None:
        created = row.created_at if row.created_at.tzinfo else row.created_at.replace(tzinfo=UTC)
        if datetime.now(UTC) - created < CACHE_TTL:
            return [SearchHit(**h) for h in row.response], True
    hits = client.search(query, max_results=max_results)
    if row is None:
        db.add(SearchCache(key=key, response=[h.__dict__ for h in hits]))
    else:
        row.response = [h.__dict__ for h in hits]
        row.created_at = datetime.now(UTC)
    db.flush()
    return hits, False
