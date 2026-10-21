from dataclasses import dataclass

from intel.rag.bm25 import BM25


@dataclass(frozen=True)
class Passage:
    pid: str
    source_id: str
    source_key: str
    publisher: str
    tier: str
    text: str
    page: int | None


class PassageIndex:
    def __init__(self, passages: list[Passage]) -> None:
        self.passages = passages
        self.by_id = {p.pid: p for p in passages}
        self._bm25 = BM25([p.text for p in passages])

    def search(self, query: str, k: int, among: set[str] | None = None) -> list[tuple[Passage, float]]:
        scores = self._bm25.scores(query)
        ranked = sorted(
            (
                (p, s)
                for p, s in zip(self.passages, scores, strict=True)
                if s > 0 and (among is None or p.source_id in among)
            ),
            key=lambda x: x[1],
            reverse=True,
        )
        return ranked[:k]

    def score(self, query: str) -> dict[str, float]:
        return {p.pid: s for p, s in zip(self.passages, self._bm25.scores(query), strict=True)}
