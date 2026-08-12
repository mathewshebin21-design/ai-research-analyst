import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types
from src.analysis import StrategicAnalysis

load_dotenv(find_dotenv(), override=True)

class ResearchEngine:
    def __init__(self):
        # Read key from Streamlit Cloud Secrets first, fallback to .env
        raw_key = None
        if "GEMINI_API_KEY" in st.secrets:
            raw_key = st.secrets["GEMINI_API_KEY"]
        else:
            raw_key = os.getenv("GEMINI_API_KEY")
            
        if not raw_key:
            raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets and environment variables.")

        # Clean hidden spaces, newlines, and quotes
        api_key = str(raw_key).strip().strip('"').strip("'")
            
        self.client = genai.Client(api_key=api_key)

    def analyze_question(self, query: str) -> StrategicAnalysis:
        system_prompt = (
            "You are an elite Senior Strategy Consultant and Market Intelligence Analyst. "
            "Analyze business opportunities with extreme rigor. "
            "CRITICAL: The 'recommendation' field MUST strictly be one of: "
            "'ENTER', 'DO NOT ENTER', or 'CONDUCT FURTHER RESEARCH'."
        )

        user_prompt = f"Conduct a full strategic market assessment for the following inquiry:\n\n'{query}'"

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StrategicAnalysis,
            ),
        )

        return StrategicAnalysis.model_validate_json(response.text)