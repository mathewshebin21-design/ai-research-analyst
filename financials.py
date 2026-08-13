import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialScenarioModeler:
    """Performs deterministic financial projections and multi-variable what-if scenario analysis."""

    @staticmethod
    def calculate_scenario(
        base_revenue: float,
        price_change_pct: float = 0.0,
        volume_change_pct: float = 0.0,
        cogs_pct: float = 0.40,
        opex: float = 50000.0
    ) -> Dict[str, Any]:
        adjusted_revenue = base_revenue * (1 + price_change_pct / 100.0) * (1 + volume_change_pct / 100.0)
        cogs = adjusted_revenue * cogs_pct
        gross_profit = adjusted_revenue - cogs
        gross_margin = (gross_profit / adjusted_revenue) if adjusted_revenue > 0 else 0.0
        ebitda = gross_profit - opex
        
        return {
            "adjusted_revenue": round(adjusted_revenue, 2),
            "cogs": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin * 100, 2),
            "ebitda": round(ebitda, 2),
            "status": "Successfully calculated scenario projection"
        }
