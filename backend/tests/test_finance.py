import pytest

from intel.finance import Assumptions, break_even_units, project, run_scenarios

BASE = {
    "price": 159,
    "gross_margin": 0.62,
    "return_rate": 0.35,
    "cac": 58,
    "marketing": 30000,
    "repeat_rate": 0.4,
    "fixed_costs": 15000,
    "launch_cost": 150000,
}


def test_golden_base_case():
    p = project(Assumptions.from_values(BASE))
    assert p.break_even_month == 21
    assert p.payback_month is None
    assert p.peak_funding == pytest.approx(-329_000, abs=1_000)
    assert p.cash_36 == pytest.approx(-210_000, abs=1_000)
    assert len(p.cumulative_cash) == 36


def test_scenarios_are_ordered_and_sensitivity_sorted():
    out = run_scenarios(BASE)
    s = out["scenarios"]
    assert s["conservative"]["cash_36"] < s["base"]["cash_36"] < s["optimistic"]["cash_36"]
    swings = [abs(r["high"] - r["low"]) for r in out["sensitivity"]]
    assert swings == sorted(swings, reverse=True)


def test_rejects_missing_and_out_of_range_assumptions():
    with pytest.raises(ValueError, match="Missing"):
        Assumptions.from_values({"price": 10})
    with pytest.raises(ValueError, match="Gross margin"):
        Assumptions.from_values({**BASE, "gross_margin": 1.5})


def test_break_even_units_kept_from_original_module():
    assert break_even_units(1000, 50, 30)["break_even_units"] == 50
    with pytest.raises(ValueError):
        break_even_units(1000, 30, 30)
