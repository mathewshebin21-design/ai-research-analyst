from typing import List, Dict, Any

class CompetitorIntelligenceModule:
    """Analyzes competitors and constructs comparative intelligence matrices."""

    @staticmethod
    def analyze_competitors(industry: str, competitors_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        matrix = []
        for comp in competitors_data:
            matrix.append({
                "company": comp.get("company", "Unknown Competitor"),
                "positioning": comp.get("positioning", "Standard Market"),
                "target_customer": comp.get("target_customer", "General Audience"),
                "pricing": comp.get("pricing", "Mid-Market"),
                "strengths": comp.get("strengths", []),
                "weaknesses": comp.get("weaknesses", []),
                "differentiation": comp.get("differentiation", "Standard Offering")
            })
        
        return {
            "industry": industry,
            "total_competitors_analyzed": len(matrix),
            "competitor_matrix": matrix,
            "market_gaps": [
                "Underserved premium segment seeking high durability",
                "Lack of transparent direct-to-consumer pricing models"
            ]
        }
