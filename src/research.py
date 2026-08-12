import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types
from src.analysis import StrategicAnalysis

load_dotenv(find_dotenv(), override=True)

class ResearchEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        self.client = genai.Client(api_key=api_key)

    def analyze_question(self, query: str) -> StrategicAnalysis:
        system_prompt = (
            "You are an elite Senior Strategy Consultant and Market Intelligence Analyst. "
            "Your job is to analyze business opportunities with extreme rigor, providing structured, "
            "data-informed, and objective recommendations. "
            "CRITICAL: The 'recommendation' field in your JSON output MUST strictly be one of these exact strings: "
            "'ENTER', 'DO NOT ENTER', or 'CONDUCT FURTHER RESEARCH'."
        )

        user_prompt = f"Conduct a full strategic market assessment for the following inquiry:\n\n'{query}'"

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StrategicAnalysis,
            ),
        )

        return StrategicAnalysis.model_validate_json(response.text)