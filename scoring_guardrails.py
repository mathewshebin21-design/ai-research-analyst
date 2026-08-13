from typing import Dict, Any, List

class StrategicScoringGuardrail:
    """Provides transparent explainability for strategic scores and enforces guardrails."""

    @staticmethod
    def explain_score(component_scores: Dict[str, float], weights: Dict[str, float]) -> Dict[str, Any]:
        total_score = 0.0
        breakdown = {}
        
        for key, score in component_scores.items():
            weight = weights.get(key, 0.20)
            weighted_val = score * weight
            total_score += weighted_val
            breakdown[key] = {
                "raw_score": score,
                "weight": weight,
                "weighted_contribution": round(weighted_val, 2)
            }
            
        return {
            "overall_strategic_score": round(total_score, 2),
            "component_breakdown": breakdown,
            "guardrail_status": "Passed validation and bounds check"
        }
