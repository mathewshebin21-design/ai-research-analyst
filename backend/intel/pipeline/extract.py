from intel.pipeline.llm_schemas import Extraction
from intel.pipeline.passages import Passage
from intel.providers.llm import LLM
from intel.providers.usage import Usage
from intel.rag.text import normalize

SYSTEM = """You extract claims for an evidence-checked market-entry analysis.
Work only from the numbered passages. Each claim must be a single checkable statement that a
passage states or that directly bears on the research task. Keep figures with their units,
geography and period. Never merge numbers from different passages into a new number.
List the passage IDs each claim comes from. Then list specific facts or figures the decision
needs that the passages do not provide."""


def render(passages: list[Passage]) -> str:
    return "\n\n".join(
        f"[{p.pid}] (source {p.source_key}, {p.publisher}{f', page {p.page}' if p.page else ''})\n{p.text}"
        for p in passages
    )


def extract_claims(
    llm: LLM, question: str, task_title: str, passages: list[Passage], usage: Usage, limit: int
) -> Extraction:
    prompt = (
        f"Decision question: {question}\nResearch task: {task_title}\n"
        f"Return at most {limit} claims.\n\nPassages:\n{render(passages)}"
    )
    out = llm.generate(system=SYSTEM, prompt=prompt, schema=Extraction, usage=usage)
    shown = {p.pid for p in passages}
    seen: set[str] = set()
    claims = []
    for c in out.claims:
        text = normalize(c.text)
        key = text.lower()
        if len(text) < 12 or key in seen:
            continue
        seen.add(key)
        c.text = text
        c.passage_ids = [pid for pid in c.passage_ids if pid in shown]
        claims.append(c)
    out.claims = claims[:limit]
    return out
