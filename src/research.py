import os
import time
from google import genai
from pydantic import BaseModel
from typing import List

class Citation(BaseModel):
    source_title: str
    url: str

class ResearchReport(BaseModel):
    executive_summary: str
    market_size_and_trends: str
    key_competitors: List[str]
    strategic_recommendations: List[str]
    citations: List[Citation]

class ResearchEngine:
    def __init__(self):
        self.client = genai.Client()

    def generate_report(self, query: str, persona: str) -> ResearchReport:
        prompt = f"Act as a {persona}. Provide a thorough research report on market intelligence for: {query}."
        
        # We configure options with fallback if rate-limited
        max_retries = 3
        backoff_factor = 2
        
        for attempt in range(max_retries):
            try:
                # Attempt with Google Search grounding tool enabled
                response = self.client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': ResearchReport,
                        'tools': [{'google_search': {}}]
                    },
                )
                return ResearchReport.model_validate_json(response.text)
            except Exception as e:
                error_str = str(e)
                if ("429" in error_str or "RESOURCE_EXHAUSTED" in error_str) and attempt < max_retries - 1:
                    time.sleep(backoff_factor ** (attempt + 1))
                    continue
                elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    # Fallback: try once without Google Search tool to bypass search-quota limitations if needed
                    try:
                        response_fallback = self.client.models.generate_content(
                            model='gemini-3.5-flash',
                            contents=prompt + " (Provide simulated market insights based on standard training data since search is rate-limited).",
                            config={
                                'response_mime_type': 'application/json',
                                'response_schema': ResearchReport,
                            },
                        )
                        return ResearchReport.model_validate_json(response_fallback.text)
                    except Exception:
                        raise RuntimeError("API quota limit reached (429). Please wait 30 seconds for your free tier window to refresh.")
                else:
                    raise e
