import os
from tavily import TavilyClient

def search_market_intelligence(query: str):
    """
    Performs real-time web search for market intelligence using Tavily API.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return [{"title": "API Key Missing", "content": "Please set TAVILY_API_KEY in your environment variables to enable live web intelligence."}]
    
    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, search_depth="advanced", max_results=5)
        return response.get("results", [])
    except Exception as e:
        return [{"title": "Search Error", "content": str(e)}]
