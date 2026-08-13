import os
from google import genai
from pydantic import BaseModel
from typing import List

class Citation(BaseModel):
    source_title: str
    url: str

class ResearchReport(BaseModel):
    executive_summary: str
    market_size_and_trends: str
    swot_strengths: List[str]
    swot_weaknesses: List[str]
    swot_opportunities: List[str]
    swot_threats: List[str]
    key_competitors: List[str]
    strategic_recommendations: List[str]
    citations: List[Citation]

class ResearchEngine:
    def __init__(self):
        self.client = genai.Client()

    def generate_report(self, query: str, persona: str) -> ResearchReport:
        prompt = f"Act as a {persona}. Provide a comprehensive market intelligence report including SWOT analysis and key trends on: {query}."
        
        response = self.client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': ResearchReport,
            },
        )
        return ResearchReport.model_validate_json(response.text)
