import os
from tavily_search import search_market_intelligence

if __name__ == "__main__":
    results = search_market_intelligence("Electric vehicle battery recycling trends 2026")
    for r in results:
        print(f"- {r.get('title')}: {r.get('url')}")
