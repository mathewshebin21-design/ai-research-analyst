from pydantic import BaseModel, Field
from typing import List

class Competitor(BaseModel):
    name: str = Field(description="Name of the competitor brand or company")
    positioning: str = Field(description="Market positioning or core focus")
    pricing_tier: str = Field(description="Price tier (e.g., Budget, Mid-range, Premium, Luxury)")
    strengths: str = Field(description="Key strengths of this competitor")
    weaknesses: str = Field(description="Vulnerabilities or gaps in their offering")

class StrategicAnalysis(BaseModel):
    recommendation: str = Field(description="Strictly 'ENTER', 'DO NOT ENTER', or 'CONDUCT FURTHER RESEARCH'")
    executive_summary: str = Field(description="Summary of the strategic opportunity")
    key_drivers: List[str] = Field(description="Key market growth drivers")
    key_risks: List[str] = Field(description="Key risks and challenges")
    action_plan: List[str] = Field(description="Recommended execution steps")
    competitors: List[Competitor] = Field(description="List of top 3-4 active competitors in this market segment")