from intel.pipeline.llm_schemas import Plan
from intel.providers.llm import LLM
from intel.providers.usage import Usage

SYSTEM = """You plan market-entry research for a strategy team.
Break the decision question into 5 to 8 research tasks that together let a board decide.
Cover market size and growth, customers and willingness to pay, competitors and pricing,
unit economics benchmarks, regulation, and operations, adapted to the question.
Queries must be specific enough for a web search engine and mention the geography and segment.
Do not answer the question. Do not invent facts."""


def make_plan(llm: LLM, question: str, context: dict, usage: Usage, max_queries: int) -> Plan:
    extra = "\n".join(f"{k}: {v}" for k, v in context.items() if v)
    prompt = f"Decision question:\n{question}\n\nContext from the user:\n{extra or 'none'}"
    plan = llm.generate(system=SYSTEM, prompt=prompt, schema=Plan, usage=usage)
    plan.tasks = [t for t in plan.tasks if t.title.strip() and t.queries][:8]
    budget = max_queries
    for t in plan.tasks:
        n = max(0, min(3, budget))
        t.queries = [q.strip() for q in t.queries if q.strip()][:n]
        budget -= len(t.queries)
    plan.tasks = [t for t in plan.tasks if t.queries]
    if not plan.tasks:
        raise ValueError("The planner returned no usable tasks.")
    return plan
