import os
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from tavily import TavilyClient

# --- Pydantic Schema with Citations ---
class Citation(BaseModel):
    source_title: str = Field(description="Title of the source webpage or publisher.")
    url: str = Field(description="Exact URL supporting the data point.")

class MarketReport(BaseModel):
    executive_summary: str = Field(description="High-level synthesis based on real-time data.")
    market_size_and_trends: str = Field(description="Current market size, valuation, and key growth metrics.")
    key_competitors: list[str] = Field(description="Top players operating in this space.")
    strategic_recommendations: list[str] = Field(description="Actionable steps for market entry or growth.")
    citations: list[Citation] = Field(description="List of verified URLs used to ground this report.")

def generate_research_report(query: str, persona: str) -> MarketReport:
    # 1. Retrieve API Keys safely from Streamlit Secrets or Environment
    gemini_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    tavily_key = st.secrets.get("TAVILY_API_KEY") or os.environ.get("TAVILY_API_KEY")

    if not gemini_key:
        raise ValueError("GEMINI_API_KEY is missing from secrets.")
    
    # Initialize Google GenAI Client
    client = genai.Client(api_key=gemini_key)

    # 2. Fetch Real-Time Web Search Context (Fallback gracefully if Tavily key is absent)
    search_context = "No live web data available (operating on parametric memory)."
    if tavily_key:
        try:
            tavily = TavilyClient(api_key=tavily_key)
            # Fetch contextual markdown search string optimized for RAG/LLMs
            search_context = tavily.get_search_context(query=query, max_results=5)
        except Exception as e:
            print(f"Web search failed: {e}")

    # 3. Construct Prompt with Real-Time Grounding
    prompt = f"""
    You are an expert AI Research Analyst adopting the persona: {persona}.
    
    Analyze the following research query: "{query}"

    Here is real-time web intelligence retrieved for this topic:
    <web_search_context>
    {search_context}
    </web_search_context>

    Instructions:
    - Base your statistics, market valuations, and findings strictly on the provided web search context where applicable.
    - Explicitly provide valid URLs from the context inside the citations schema.
    - Avoid making up generic statistics; ground every core data point.
    """

    # 4. Generate Structured Output using Gemini 2.5 Flash & Pydantic
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MarketReport,
            temperature=0.2, # Low temperature for factual consistency
        ),
    )

    # Parse response text back into the Pydantic model
    return MarketReport.model_validate_json(response.text)
