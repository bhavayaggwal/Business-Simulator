"""Data classes used across the simulator.

These mirror the database tables in the Phase 1 design. The engine only ever
works with these objects, never with the database or the UI directly.
"""
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class UserProfile:
    user_id: int
    username: str


@dataclass
class Industry:
    industry_id: int
    name: str
    base_demand: int
    reference_price: Decimal
    unit_cost: Decimal
    fixed_cost: Decimal
    price_sensitivity: Decimal
    max_marketing_boost: Decimal
    marketing_k: Decimal


@dataclass
class Business:
    business_id: int
    user_id: int
    industry_id: int
    name: str
    starting_capital: Decimal
    # Starting values this business actually runs on (industry defaults,
    # possibly edited by the user when the business was created).
    base_demand: int
    reference_price: Decimal
    unit_cost: Decimal
    fixed_cost: Decimal
    price_sensitivity: Decimal
    # Current position, updated after every simulated month.
    price: Decimal
    marketing_budget: Decimal
    current_month: int
    cash: Decimal
    stock: int


@dataclass
class BusinessSummary:
    """A business as shown in the dashboard list and searched by name/industry."""
    business_id: int
    name: str
    industry_name: str
    current_month: int
    cash: Decimal


@dataclass
class BusinessState:
    """Everything the engine needs to simulate the next month."""
    business_id: int
    month_no: int            # months simulated so far
    cash: Decimal
    stock: int
    base_demand: int
    reference_price: Decimal
    unit_cost: Decimal
    fixed_cost: Decimal
    price_sensitivity: Decimal
    max_marketing_boost: Decimal
    marketing_k: Decimal


@dataclass
class Decisions:
    price: Decimal
    marketing_spend: Decimal
    units_to_buy: int


@dataclass
class MonthResult:
    business_id: int
    month_no: int
    price: Decimal
    marketing_spend: Decimal
    units_purchased: int
    stock_purchase_cost: Decimal
    market_factor: float
    demand: int
    units_sold: int
    opening_stock: int
    closing_stock: int
    revenue: Decimal
    cogs: Decimal
    fixed_cost: Decimal
    total_costs: Decimal
    profit: Decimal
    opening_cash: Decimal
    closing_cash: Decimal


@dataclass
class GlossaryTerm:
    term: str
    definition: str
    example: str = ""


@dataclass
class MonthReport:
    """What the results screen receives after a month is simulated."""
    result: MonthResult
    explanations: list = field(default_factory=list)
