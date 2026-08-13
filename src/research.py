import os
import streamlit as st
import google.generativeai as genai
from src.analysis import StrategicAnalysis

class ResearchEngine:
    def __init__(self):
        api_key = (
            st.secrets.get("GEMINI_API_KEY") or 
            st.secrets.get("GOOGLE_API_KEY") or 
            os.environ.get("GEMINI_API_KEY") or 
            os.environ.get("GOOGLE_API_KEY")
        )
        if not api_key:
            raise ValueError("API Key not found in Streamlit secrets or environment variables.")
        
        genai.configure(api_key=api_key)
        # Using the standard developer model configuration
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_question(self, query: str, persona: str = "Senior Strategy Consultant") -> StrategicAnalysis:
        prompt = f"""
        You are acting as an expert {persona}.
        Perform a comprehensive strategic analysis and market assessment for the following business question:
        
        "{query}"

        Provide a structured, rigorous assessment including an executive summary, clear recommendation, key market drivers, key risks, a detailed action plan, a 4-year market size trend projection, a SWOT analysis, and a competitive landscape matrix.
        """

        response = self.model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": StrategicAnalysis,
                "temperature": 0.2,
            }
        )

        return StrategicAnalysis.model_validate_json(response.text)
