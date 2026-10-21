"""Services: the bridge between the screens, the engine and the repository.

The UI only ever calls methods on SimulatorService. This class loads data from
the repository, runs the engine and algorithms, and saves the results.
"""
import random
from decimal import Decimal

from logic import algorithms, engine, validation
from logic.models import (Business, BusinessState, BusinessSummary, Decisions,
                          MonthReport)

MARKET_LOW = 0.90
MARKET_HIGH = 1.10


class SimulatorService:
    def __init__(self, repository, rng=None):
        self.repo = repository
        self.rng = rng or random.Random()

    # ---- profiles -------------------------------------------------------
    def list_profiles(self):
        return self.repo.get_profiles()

    def create_profile(self, username):
        existing = [p.username for p in self.repo.get_profiles()]
        name, error = validation.validate_username(username, existing)
        if error:
            return None, error
        return self.repo.add_profile(name), None

    # ---- industries and glossary ---------------------------------------
    def list_industries(self):
        return self.repo.get_industries()

    def get_industry(self, industry_id):
        return self.repo.get_industry(industry_id)

    def glossary(self):
        """Glossary terms keyed by term name, for info boxes and the help screen."""
        return {g.term: g for g in self.repo.get_glossary()}

    # ---- businesses -----------------------------------------------------
    def list_businesses(self, user_id):
        summaries = []
        for b in self.repo.get_businesses_for_user(user_id):
            industry = self.repo.get_industry(b.industry_id)
            summaries.append(BusinessSummary(b.business_id, b.name, industry.name,
                                             b.current_month, b.cash))
        return summaries

    def search_businesses(self, user_id, field, term):
        """field is 'name' or 'industry_name'. Uses linear search."""
        return algorithms.linear_search(self.list_businesses(user_id), field, term)

    def get_business(self, business_id):
        return self.repo.get_business(business_id)

    def create_business(self, user_id, industry_id, form):
        existing = [b.name for b in self.repo.get_businesses_for_user(user_id)]
        clean, errors = validation.validate_business_form(form, existing)
        if errors:
            return None, errors
        stock_cost = clean["initial_stock"] * clean["unit_cost"]
        business = Business(
            business_id=0, user_id=user_id, industry_id=industry_id,
            name=clean["name"], starting_capital=clean["starting_capital"],
            base_demand=clean["base_demand"], reference_price=clean["reference_price"],
            unit_cost=clean["unit_cost"], fixed_cost=clean["fixed_cost"],
            price_sensitivity=clean["price_sensitivity"],
            price=clean["price"], marketing_budget=clean["marketing_budget"],
            current_month=0,
            cash=engine.money(clean["starting_capital"] - stock_cost),
            stock=clean["initial_stock"],
        )
        return self.repo.add_business(business), {}

    def _state_for(self, business):
        industry = self.repo.get_industry(business.industry_id)
        return BusinessState(
            business_id=business.business_id, month_no=business.current_month,
            cash=business.cash, stock=business.stock,
            base_demand=business.base_demand, reference_price=business.reference_price,
            unit_cost=business.unit_cost, fixed_cost=business.fixed_cost,
            price_sensitivity=business.price_sensitivity,
            max_marketing_boost=industry.max_marketing_boost,
            marketing_k=industry.marketing_k,
        )

    # ---- running a month -----------------------------------------------
    def check_decisions(self, business_id, price_text, marketing_text, units_text):
        business = self.repo.get_business(business_id)
        return validation.validate_decisions(price_text, marketing_text, units_text,
                                             business.cash, business.unit_cost)

    def run_month(self, business_id, decisions: Decisions, market_factor=None):
        """Simulate the next month and save it. Returns a MonthReport."""
        business = self.repo.get_business(business_id)
        state = self._state_for(business)
        if market_factor is None:
            market_factor = self.rng.uniform(MARKET_LOW, MARKET_HIGH)

        result = engine.simulate_month(state, decisions, market_factor)

        # In the SQL version these two writes happen in one transaction.
        self.repo.add_result(result)
        business.current_month = result.month_no
        business.cash = result.closing_cash
        business.stock = result.closing_stock
        business.price = result.price
        business.marketing_budget = result.marketing_spend
        self.repo.update_business(business)

        return MonthReport(result, engine.explain_month(state, result))

    # ---- history --------------------------------------------------------
    def history(self, business_id):
        """All months in month order."""
        return self.repo.get_results(business_id)

    def sorted_history(self, business_id, key, descending):
        return algorithms.merge_sort(self.history(business_id), key, descending)

    def find_month(self, business_id, month_text):
        business = self.repo.get_business(business_id)
        month, error = validation.validate_month_number(month_text, business.current_month)
        if error:
            return None, error
        found = algorithms.binary_search(self.history(business_id), month)
        if found is None:
            return None, "Month not simulated yet."
        return found, None


def seed_demo(service):
    """Create a demo profile with one business and six months of history,
    so every screen has realistic data to show in the prototype."""
    profile, _ = service.create_profile("demo_student")
    coffee = next(i for i in service.list_industries() if i.name == "Coffee Shop")
    business, _ = service.create_business(profile.user_id, coffee.industry_id, {
        "name": "Bean There", "starting_capital": "10000", "price": "3.20",
        "initial_stock": "1500", "marketing_budget": "300",
        "base_demand": str(coffee.base_demand), "reference_price": str(coffee.reference_price),
        "unit_cost": str(coffee.unit_cost), "fixed_cost": str(coffee.fixed_cost),
        "price_sensitivity": str(coffee.price_sensitivity),
    })
    plan = [  # price, marketing, units to buy: a mix of good and bad months
        ("3.20", "300", "1200"),
        ("3.40", "400", "6000"),
        ("3.40", "600", "0"),
        ("4.80", "0", "0"),
        ("3.00", "200", "2600"),
        ("3.30", "500", "2400"),
    ]
    demo_rng = random.Random(7)
    for price, marketing, units in plan:
        decisions = Decisions(Decimal(price), Decimal(marketing), int(units))
        service.run_month(business.business_id, decisions,
                          market_factor=demo_rng.uniform(MARKET_LOW, MARKET_HIGH))
    return profile, business
