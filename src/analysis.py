from pydantic import BaseModel, Field
from typing import List, Literal

class OpportunityMatrix(BaseModel):
    market_attractiveness: int = Field(description="Score from 0-100 indicating market growth and size dynamics")
    customer_demand: int = Field(description="Score from 0-100 evaluating willingness to pay and demand trend")
    competitive_intensity: int = Field(description="Score from 0-100 (Higher means highly saturated/competitive)")
    pricing_opportunity: int = Field(description="Score from 0-100 reflecting margin potential and pricing power")
    entry_difficulty: int = Field(description="Score from 0-100 evaluating capital and regulatory barriers")
    overall_opportunity_score: int = Field(description="Calculated overall strategic suitability score from 0-100")

class StrategicAnalysis(BaseModel):
    executive_summary: str = Field(description="High-level briefing summarizing the core findings")
    recommendation: Literal["ENTER", "DO NOT ENTER", "CONDUCT FURTHER RESEARCH"] = Field(
        description="Clear strategic decision verdict"
    )
    strategic_opportunity: str = Field(description="Primary competitive gap or positioning sweet spot")
    key_risks: List[str] = Field(description="Top 3-5 operational, financial, or strategic risks")
    opportunities: List[str] = Field(description="Top 3-5 growth levers or market gaps")
    suggested_strategy: str = Field(description="Actionable go-to-market execution plan")
    matrix: OpportunityMatrix