import os
import streamlit as st
from google import genai
from google.genai import types
from src.analysis import StrategicAnalysis

class ResearchEngine:
    def __init__(self):
        # Fallback across multiple key formats to guarantee pickup from Streamlit secrets
        api_key = (
            st.secrets.get("GEMINI_API_KEY") or 
            st.secrets.get("GOOGLE_API_KEY") or 
            os.environ.get("GEMINI_API_KEY") or 
            os.environ.get("GOOGLE_API_KEY")
        )
        if not api_key:
            raise ValueError("API Key not found in Streamlit secrets or environment variables.")
        
        # Explicitly initialize client with the developer API key
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
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )

        return response.parsed
