class FinancialScenarioModeler:
    """Calculates deterministic financial projections and break-even points without relying on LLM math."""

    @staticmethod
    def calculate_scenarios(initial_capital: float, growth_rate: float, years: int = 3) -> dict:
        scenarios = {"Base": [], "Optimistic": [], "Conservative": [], "Timeline": []}
        
        base_val = initial_capital
        opt_val = initial_capital
        cons_val = initial_capital

        for yr in range(years + 1):
            scenarios["Timeline"].append(f"Year {yr}")
            if yr == 0:
                scenarios["Base"].append(initial_capital)
                scenarios["Optimistic"].append(initial_capital)
                scenarios["Conservative"].append(initial_capital)
            else:
                base_val *= (1 + growth_rate)
                opt_val *= (1 + growth_rate * 1.5)
                cons_val *= (1 + growth_rate * 0.5)

                scenarios["Base"].append(round(base_val, 2))
                scenarios["Optimistic"].append(round(opt_val, 2))
                scenarios["Conservative"].append(round(cons_val, 2))

        return scenarios

    @staticmethod
    def calculate_break_even(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> dict:
        if price_per_unit <= variable_cost_per_unit:
            return {"error": "Price per unit must exceed variable cost per unit."}
        
        contribution_margin = price_per_unit - variable_cost_per_unit
        break_even_units = fixed_costs / contribution_margin
        break_even_revenue = break_even_units * price_per_unit

        return {
            "break_even_units": round(break_even_units, 2),
            "break_even_revenue": round(break_even_revenue, 2),
            "contribution_margin": round(contribution_margin, 2)
        }
