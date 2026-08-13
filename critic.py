from typing import Dict, Any, List

class StrategicCriticAgent:
    """Audits research outputs for unsupported claims and citation gaps."""

    @staticmethod
    def audit_report(claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        flagged_claims = []
        verified_count = 0
        
        for item in claims:
            if not item.get("verified", False):
                flagged_claims.append(item.get("claim", "Unknown claim"))
            else:
                verified_count += 1
                
        total = len(claims) if claims else 1
        grounding_score = (verified_count / total) * 100
        
        return {
            "total_claims_audited": len(claims),
            "verified_claims": verified_count,
            "grounding_score_pct": round(grounding_score, 2),
            "flagged_unsupported": flagged_claims,
            "status": "Passed QA audit" if grounding_score >= 50 else "Needs further evidence"
        }
