from src.decision_engine import evaluate_market_opportunity

if __name__ == "__main__":
    result = evaluate_market_opportunity("UK Sustainable Fashion Market")
    print("--- Strategic Decision Engine Test ---")
    print(f"Market: {result['market']}")
    print(f"Recommendation: {result['recommendation']} (Confidence: {result['confidence']})")
    print(f"Opportunity Score: {result['opportunity_score']}/100")
