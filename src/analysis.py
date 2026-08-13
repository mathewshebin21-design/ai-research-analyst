from pydantic import BaseModel, Field
from typing import List

class SWOT(BaseModel):
    strengths: List[str] = Field(description="Internal strengths")
    weaknesses: List[str] = Field(description="Internal weaknesses")
    opportunities: List[str] = Field(description="External opportunities")
    threats: List[str] = Field(description="External threats")

class Competitor(BaseModel):
    name: str = Field(description="Name of the competitor")
    positioning: str = Field(description="Market positioning")
    pricing_tier: str = Field(description="Pricing tier")
    strengths: str = Field(description="Key strengths")
    weaknesses: str = Field(description="Key weaknesses")

class StrategicAnalysis(BaseModel):
    recommendation: str = Field(description="Strictly 'ENTER', 'DO NOT ENTER', or 'CONDUCT FURTHER RESEARCH'")
    executive_summary: str = Field(description="Executive summary")
    swot: SWOT = Field(description="Structured SWOT analysis") # Add this
    key_drivers: List[str] = Field(description="Key market growth drivers")
    key_risks: List[str] = Field(description="Key risks")
    action_plan: List[str] = Field(description="Execution steps")
    competitors: List[Competitor] = Field(description="List of top competitors")