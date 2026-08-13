import os
from google import genai
from google.genai import types
from src.analysis import StrategicAnalysis

class ResearchEngine:
    def __init__(self):
        # Initialize the Gemini client using the environment API key
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def analyze_question(self, query: str, persona: str = "Senior Strategy Consultant") -> StrategicAnalysis:
        prompt = f"""
        You are acting as an expert {persona}.
        Perform a comprehensive strategic analysis and market assessment for the following business question:
        
        "{query}"

        Provide a structured, rigorous assessment including an executive summary, clear recommendation, key market drivers, key risks, a detailed action plan, a 4-year market size trend projection, a SWOT analysis, and a competitive landscape matrix.
        """

        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StrategicAnalysis,
                temperature=0.2,
            ),
        )

        return response.parsed