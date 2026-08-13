class FinancialScenarioModeler:
    """Calculates financial projections under base, optimistic, and conservative growth scenarios."""
    
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
