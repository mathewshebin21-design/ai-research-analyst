"""Deterministic scenario model. No language model touches these numbers.

Extends the original financials.py from compounding capital to a unit-economics cash model.
"""

from dataclasses import asdict, dataclass

MONTHS = 36
FULFILMENT_PER_ORDER = 8.0
RETURN_HANDLING_PER_RETURN = 9.0

ASSUMPTION_SPEC: dict[str, dict] = {
    "price": {"label": "Price per unit", "unit": "€", "min": 1, "max": 100000},
    "gross_margin": {"label": "Gross margin", "unit": "share", "min": 0, "max": 0.95},
    "return_rate": {"label": "Return rate", "unit": "share", "min": 0, "max": 0.9},
    "cac": {"label": "Acquisition cost per customer", "unit": "€", "min": 0.01, "max": 100000},
    "marketing": {"label": "Marketing per month", "unit": "€", "min": 0, "max": 10_000_000},
    "repeat_rate": {"label": "Repeat purchase rate (12 months)", "unit": "share", "min": 0, "max": 1},
    "fixed_costs": {"label": "Fixed costs per month", "unit": "€", "min": 0, "max": 10_000_000},
    "launch_cost": {"label": "One-off launch cost", "unit": "€", "min": 0, "max": 100_000_000},
}

SCENARIO_SHIFTS = {
    "conservative": {"cac": 1.25, "repeat_rate": 0.8, "return_rate": 1.1},
    "base": {"cac": 1.0, "repeat_rate": 1.0, "return_rate": 1.0},
    "optimistic": {"cac": 0.8, "repeat_rate": 1.2, "return_rate": 0.9},
}


@dataclass(frozen=True)
class Assumptions:
    price: float
    gross_margin: float
    return_rate: float
    cac: float
    marketing: float
    repeat_rate: float
    fixed_costs: float
    launch_cost: float

    @classmethod
    def from_values(cls, values: dict[str, float]) -> "Assumptions":
        missing = [k for k in ASSUMPTION_SPEC if k not in values]
        if missing:
            raise ValueError(f"Missing assumptions: {', '.join(missing)}")
        for k, spec in ASSUMPTION_SPEC.items():
            v = float(values[k])
            if not spec["min"] <= v <= spec["max"]:
                raise ValueError(f"{spec['label']} must be between {spec['min']} and {spec['max']}.")
        return cls(**{k: float(values[k]) for k in ASSUMPTION_SPEC})


@dataclass
class Projection:
    revenue: list[float]
    ebitda: list[float]
    cumulative_cash: list[float]
    break_even_month: int | None
    payback_month: int | None
    peak_funding: float
    revenue_36: float
    cash_36: float


def project(a: Assumptions) -> Projection:
    revenue: list[float] = []
    ebitda: list[float] = []
    cash_curve: list[float] = []
    customers = 0.0
    cash = -a.launch_cost
    peak = cash
    break_even = payback = None
    for m in range(1, MONTHS + 1):
        new = a.marketing / a.cac
        repeat = customers * (a.repeat_rate / 12)
        customers += new
        orders = new + repeat
        net_revenue = orders * (1 - a.return_rate) * a.price
        gross = (
            net_revenue * a.gross_margin
            - orders * FULFILMENT_PER_ORDER
            - orders * a.return_rate * RETURN_HANDLING_PER_RETURN
        )
        month = gross - a.marketing - a.fixed_costs
        cash += month
        revenue.append(round(net_revenue, 2))
        ebitda.append(round(month, 2))
        cash_curve.append(round(cash, 2))
        peak = min(peak, cash)
        if break_even is None and month >= 0:
            break_even = m
        if payback is None and cash >= 0:
            payback = m
    return Projection(
        revenue=revenue,
        ebitda=ebitda,
        cumulative_cash=cash_curve,
        break_even_month=break_even,
        payback_month=payback,
        peak_funding=round(peak, 2),
        revenue_36=round(sum(revenue), 2),
        cash_36=round(cash, 2),
    )


def shifted(a: Assumptions, scenario: str) -> Assumptions:
    s = SCENARIO_SHIFTS[scenario]
    values = asdict(a)
    values["cac"] = a.cac * s["cac"]
    values["repeat_rate"] = min(1.0, a.repeat_rate * s["repeat_rate"])
    values["return_rate"] = min(0.9, a.return_rate * s["return_rate"])
    return Assumptions(**values)


SENSITIVITY_KEYS = ["cac", "repeat_rate", "return_rate", "gross_margin", "price", "fixed_costs"]


def sensitivity(a: Assumptions, swing: float = 0.2) -> list[dict]:
    base = project(a).cash_36
    rows = []
    for key in SENSITIVITY_KEYS:
        values = asdict(a)
        lo, hi = dict(values), dict(values)
        lo[key] = values[key] * (1 - swing)
        hi[key] = values[key] * (1 + swing)
        if key in ("gross_margin", "return_rate", "repeat_rate"):
            hi[key] = min(hi[key], ASSUMPTION_SPEC[key]["max"])
        rows.append(
            {
                "key": key,
                "label": ASSUMPTION_SPEC[key]["label"],
                "low": round(project(Assumptions(**lo)).cash_36 - base, 2),
                "high": round(project(Assumptions(**hi)).cash_36 - base, 2),
            }
        )
    rows.sort(key=lambda r: abs(r["high"] - r["low"]), reverse=True)
    return rows


def run_scenarios(values: dict[str, float]) -> dict:
    a = Assumptions.from_values(values)
    return {
        "scenarios": {name: asdict(project(shifted(a, name))) for name in SCENARIO_SHIFTS},
        "sensitivity": sensitivity(a),
        "constants": {"fulfilment_per_order": FULFILMENT_PER_ORDER, "return_handling": RETURN_HANDLING_PER_RETURN},
        "months": MONTHS,
    }


def break_even_units(fixed_costs: float, price: float, variable_cost: float) -> dict:
    """Kept from the original financials.py."""
    if price <= variable_cost:
        raise ValueError("Price per unit must exceed variable cost per unit.")
    margin = price - variable_cost
    units = fixed_costs / margin
    return {
        "break_even_units": round(units, 2),
        "break_even_revenue": round(units * price, 2),
        "contribution_margin": margin,
    }
