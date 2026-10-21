from dataclasses import dataclass, field


@dataclass
class Usage:
    """Per-run usage counters, stored on the run for cost reporting and budget caps."""

    searches: int = 0
    cached_searches: int = 0
    llm_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    embedding_calls: int = 0
    by_stage: dict[str, int] = field(default_factory=dict)
    models: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "searches": self.searches,
            "cached_searches": self.cached_searches,
            "llm_calls": self.llm_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "embedding_calls": self.embedding_calls,
            "models": dict(self.models),
        }
