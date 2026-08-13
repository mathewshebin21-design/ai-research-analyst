from tavily_search import WebSearchModule

def test_search():
    results = WebSearchModule.search_market_data("AI Market")
    assert isinstance(results, list)
    assert len(results) > 0
    assert "title" in results[0]

def test_market_intelligence():
    results = WebSearchModule.search_market_data("AI Market")
    assert isinstance(results, list)
