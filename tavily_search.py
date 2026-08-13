import os
import requests
from typing import List, Dict, Any

class TavilySearchEngine:
    """Performs live web research using the official Tavily API."""

    @staticmethod
    def search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return [{
                "title": "API Key Missing",
                "url": "https://tavily.com",
                "content": "TAVILY_API_KEY environment variable is not set.",
                "score": 0.0
            }]

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "content": item.get("content"),
                        "score": item.get("score", 1.0)
                    })
                return results
            else:
                return [{
                    "title": "Search Error",
                    "url": "#",
                    "content": f"Tavily API returned status code {response.status_code}",
                    "score": 0.0
                }]
        except Exception as e:
            return [{
                "title": "Connection Exception",
                "url": "#",
                "content": str(e),
                "score": 0.0
            }]

    @staticmethod
    def search_market_data(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        return TavilySearchEngine.search(query, max_results)

# Alias for test compatibility
WebSearchModule = TavilySearchEngine
