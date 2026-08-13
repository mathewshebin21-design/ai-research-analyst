import os
from google import genai
from pydantic import BaseModel
from typing import List, Optional

class Citation(BaseModel):
    source_title: str
    url: str

class ResearchReport(BaseModel):
    executive_summary: str
    market_size_and_trends: Optional[str] = None
    swot_strengths: Optional[List[str]] = None
    swot_weaknesses: Optional[List[str]] = None
    swot_opportunities: Optional[List[str]] = None
    swot_threats: Optional[List[str]] = None
    key_competitors: Optional[List[str]] = None
    financial_projections: Optional[str] = None
    strategic_recommendations: Optional[List[str]] = None
    citations: Optional[List[Citation]] = None

class ResearchEngine:
    def __init__(self):
        self.client = genai.Client()

    def generate_report(self, query: str, persona: str, sections: List[str]) -> ResearchReport:
        section_instructions = ", ".join(sections)
        prompt = f"Act as a {persona}. Provide a thorough market intelligence report on: {query}. Focus specifically on including these requested sections: {section_instructions}."
        
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': ResearchReport,
            },
        )
        return ResearchReport.model_validate_json(response.text)
