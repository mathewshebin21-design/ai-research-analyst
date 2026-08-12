import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types
from src.analysis import StrategicAnalysis

load_dotenv(find_dotenv(), override=True)

class ResearchEngine:
    def __init__(self):
        raw_key = None
        if "GEMINI_API_KEY" in st.secrets:
            raw_key = st.secrets["GEMINI_API_KEY"]
        else:
            raw_key = os.getenv("GEMINI_API_KEY")
            
        if not raw_key:
            raise ValueError("GEMINI_API_KEY missing in Streamlit Secrets and environment variables.")

        api_key = str(raw_key).strip().strip('"').strip("'")
        self.client = genai.Client(api_key=api_key)
        
        all_models = [m.name.replace("models/", "") for m in self.client.models.list()]
        preferred = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]
        self.selected_model = None
        
        for model_name in preferred:
            if model_name in all_models:
                self.selected_model = model_name
                break
                
        if not self.selected_model:
            self.selected_model = all_models[0] if all_models else "gemini-3.6-flash"

    def analyze_question(self, query: str) -> StrategicAnalysis:
        system_prompt = (
            "You are an elite Senior Strategy Consultant and Market Intelligence Analyst. "
            "Analyze business opportunities with extreme rigor. "
            "CRITICAL: The 'recommendation' field MUST strictly be one of: "
            "'ENTER', 'DO NOT ENTER', or 'CONDUCT FURTHER RESEARCH'."
        )

        user_prompt = f"Conduct a full strategic market assessment for the following inquiry:\n\n'{query}'"

        response = self.client.models.generate_content(
            model=self.selected_model,
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StrategicAnalysis,
            ),
        )

        return StrategicAnalysis.model_validate_json(response.text)