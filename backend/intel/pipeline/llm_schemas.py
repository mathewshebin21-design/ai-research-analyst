"""Structured outputs requested from the language model. Kept flat so every provider can honour them."""

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["Market", "Customer", "Competition", "Financial", "Legal / risk", "Operations", "Other"]


class PlannedTask(BaseModel):
    title: str = Field(description="Research question for this task, under 90 characters")
    category: Category
    rationale: str = Field(description="One sentence: why this matters for the decision")
    queries: list[str] = Field(description="2 or 3 specific web search queries")


class Plan(BaseModel):
    objective: str
    tasks: list[PlannedTask]


class ExtractedClaim(BaseModel):
    text: str = Field(description="One atomic, checkable statement relevant to the decision")
    kind: Literal["fact", "figure", "forecast"]
    passage_ids: list[str] = Field(description="IDs of the passages this claim is drawn from, e.g. P12")


class MissingItem(BaseModel):
    item: str = Field(description="A specific fact or figure the decision needs that the passages do not give")
    impact: Literal["High", "Medium", "Low"]
    plan: str = Field(description="How to obtain it")


class Extraction(BaseModel):
    claims: list[ExtractedClaim]
    missing: list[MissingItem]


class PassageVerdict(BaseModel):
    passage_id: str
    relation: Literal["supports", "contradicts", "neutral"]
    confidence: float = Field(ge=0, le=1, description="How strongly the passage entails or contradicts the claim")
    quote: str = Field(description="Exact words copied from the passage that decide the verdict; empty if neutral")
    scope_issue: str = Field(description="Mismatch in geography, segment, period or unit; empty if none")
    note: str = Field(description="One sentence explaining the verdict")


class Verification(BaseModel):
    verdicts: list[PassageVerdict]


class CitedItem(BaseModel):
    text: str
    claims: list[str] = Field(description="Claim keys such as C3 that this item rests on")


class Swot(BaseModel):
    strengths: list[CitedItem]
    weaknesses: list[CitedItem]
    opportunities: list[CitedItem]
    threats: list[CitedItem]


class PestleItem(BaseModel):
    factor: Literal["Political", "Economic", "Social", "Technological", "Legal", "Environmental"]
    rating: int = Field(ge=1, le=5, description="Impact on the decision, 1 low to 5 high")
    note: str
    claims: list[str]


class PorterForce(BaseModel):
    force: Literal["Rivalry", "New entrants", "Substitutes", "Buyer power", "Supplier power"]
    level: float = Field(ge=1, le=5)
    rationale: str
    claims: list[str]


class Competitor(BaseModel):
    name: str
    positioning: str
    price_note: str = Field(description="Price level or range if known from the claims, else empty")
    strengths: str
    weaknesses: str
    claims: list[str]


class FactorScore(BaseModel):
    key: Literal["attract", "demand", "compete", "econ", "exec"]
    score: int = Field(ge=0, le=100)
    rationale: str
    claims: list[str]


class AssumptionSuggestion(BaseModel):
    key: Literal[
        "price", "gross_margin", "return_rate", "cac", "marketing", "repeat_rate", "fixed_costs", "launch_cost"
    ]
    value: float
    claim: str = Field(description="Claim key that states this value, or empty if it is your estimate")
    note: str


class Analysis(BaseModel):
    competitors: list[Competitor]
    swot: Swot
    pestle: list[PestleItem]
    porter: list[PorterForce]
    factors: list[FactorScore]
    assumptions: list[AssumptionSuggestion]


class Narrative(BaseModel):
    headline: str = Field(description="The recommendation in one sentence, consistent with the given verdict")
    summary: str = Field(description="Three sentences. Cite claim keys in brackets, e.g. [C2]")
    conditions: list[str] = Field(description="2 to 4 measurable conditions to proceed")
    would_change: list[str] = Field(description="1 to 3 findings that would change the verdict")
