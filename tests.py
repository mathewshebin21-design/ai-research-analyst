import unittest
from financials import FinancialScenarioModeler
from recommendations import StrategicRecommendationEngine
from planner import AIResearchPlanner

class TestAIResearchHub(unittest.TestCase):
    
    def test_financial_scenarios(self):
        scenarios = FinancialScenarioModeler.calculate_scenarios(180000.0, 0.25, years=2)
        self.assertIn("Base", scenarios)
        self.assertIn("Optimistic", scenarios)
        self.assertIn("Conservative", scenarios)
        self.assertEqual(len(scenarios["Timeline"]), 3)
        self.assertEqual(scenarios["Base"][0], 180000.0)

    def test_recommendation_engine(self):
        rec_pass = StrategicRecommendationEngine.evaluate_recommendation(risk_score=30, attractiveness=85)
        self.assertEqual(rec_pass["verdict"], "ENTER (High Conviction)")
        
        rec_fail = StrategicRecommendationEngine.evaluate_recommendation(risk_score=80, attractiveness=50)
        self.assertEqual(rec_fail["verdict"], "DO NOT ENTER")

    def test_ai_planner(self):
        plan = AIResearchPlanner.generate_plan("D2C Apparel Expansion")
        self.assertIn("objective", plan)
        self.assertGreater(len(plan["research_tasks"]), 0)

if __name__ == "__main__":
    unittest.main()
