from typing import Dict, Any, List

class EvidenceClassifier:
    """Classifies research extractions into strict epistemic categories."""

    @staticmethod
    def classify_claim(claim: str, source_url: str = None) -> Dict[str, Any]:
        source_type = "FACT" if source_url and "example.com" not in source_url else "INFERENCE"
        if not source_url:
            source_type = "ASSUMPTION"
            
        return {
            "claim": claim,
            "classification": source_type,
            "source_url": source_url or "No direct URL provided",
            "confidence": 0.95 if source_type == "FACT" else 0.70,
            "verified": source_type == "FACT"
        }
