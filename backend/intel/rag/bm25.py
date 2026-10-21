"""Okapi BM25 over in-memory passages. Deterministic and dependency-free."""

import math
from collections import Counter

from intel.rag.text import tokens


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.4, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.docs = [Counter(tokens(d)) for d in docs]
        self.lengths = [sum(c.values()) for c in self.docs]
        self.avg = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        df: Counter[str] = Counter()
        for c in self.docs:
            df.update(c.keys())
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: str) -> list[float]:
        q = tokens(query)
        out = []
        for c, length in zip(self.docs, self.lengths, strict=True):
            s = 0.0
            for t in q:
                f = c.get(t)
                if not f:
                    continue
                s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * length / (self.avg or 1)))
            out.append(s)
        return out

    def top(self, query: str, k: int) -> list[tuple[int, float]]:
        ranked = sorted(enumerate(self.scores(query)), key=lambda x: x[1], reverse=True)
        return [(i, s) for i, s in ranked[:k] if s > 0]


def relevance(score: float, best: float) -> float:
    """Normalise a BM25 score into 0..1 relative to the best match for the same query."""
    return round(score / best, 3) if best > 0 else 0.0
