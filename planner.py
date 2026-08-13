import json

class AIResearchPlanner:
    """Decomposes complex strategic and business questions into a structured research plan."""
    
    @staticmethod
    def generate_plan(query: str) -> dict:
        # Standardized strategic research plan breakdown
        plan = {
            "query": query,
            "objective": f"Comprehensive market viability and risk-reward analysis for: '{query}'",
            "research_tasks": [
                {"id": 1, "task": "Market Size, CAGR & Industry Growth Trends", "category": "Market"},
                {"id": 2, "task": "Consumer Demand, Behavior & Pain Points", "category": "Customer"},
                {"id": 3, "task": "Competitor Landscape, Positioning & Market Share", "category": "Competition"},
                {"id": 4, "task": "Pricing Strategies & Unit Economics Benchmarks", "category": "Financial"},
                {"id": 5, "task": "Barriers to Entry & Regulatory/Compliance Requirements", "category": "Legal/Risk"},
                {"id": 6, "task": "Supply Chain, Sourcing & Operational Feasibility", "category": "Operations"},
                {"id": 7, "task": "Financial Scenario Modelling (Base, Optimistic, Conservative)", "category": "Financial"}
            ],
            "evaluation_metrics": [
                "Market Attractiveness (0-100)",
                "Opportunity Score (0-100)",
                "Competitive Intensity (0-100)",
                "Execution Difficulty (0-100)",
                "Risk Score (0-100)",
                "Confidence Rating (0-100)"
            ]
        }
        return plan
