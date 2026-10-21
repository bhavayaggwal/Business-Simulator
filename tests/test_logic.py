"""Automated tests T01–T14 from the Phase 1 test plan.

Run from the project folder with:  python -m unittest discover tests -v
"""
import random
import unittest
from decimal import Decimal as D

from data.memory_repository import MemoryRepository
from logic import algorithms, engine, validation
from logic.models import BusinessState, Decisions, MonthResult
from logic.services import MARKET_HIGH, MARKET_LOW, SimulatorService


def make_state(**overrides):
    """Shared engine test values from the test plan."""
    values = dict(business_id=1, month_no=0, cash=D("5000"), stock=300,
                  base_demand=400, reference_price=D("5"), unit_cost=D("2"),
                  fixed_cost=D("800"), price_sensitivity=D("1.5"),
                  max_marketing_boost=D("0.6"), marketing_k=D("500"))
    values.update(overrides)
    return BusinessState(**values)


def result(month, profit):
    """A minimal MonthResult for sorting/searching tests."""
    zero = D("0")
    return MonthResult(1, month, zero, zero, 0, zero, 1.0, 0, 0, 0, 0,
                       zero, zero, zero, zero, D(profit), zero, zero)


class EngineTests(unittest.TestCase):
    def test_T01_full_month(self):
        # Demand fixed at 450: base 450, price = typical price, no marketing boost.
        state = make_state(base_demand=450, max_marketing_boost=D("0"))
        r = engine.simulate_month(state, Decisions(D("5"), D("300"), 1000), 1.0)
        self.assertEqual(r.units_sold, 450)
        self.assertEqual(r.closing_stock, 850)
        self.assertEqual(r.revenue, D("2250.00"))
        self.assertEqual(r.cogs, D("900.00"))
        self.assertEqual(r.total_costs, D("2000.00"))
        self.assertEqual(r.profit, D("250.00"))
        self.assertEqual(r.closing_cash, D("4150.00"))

    def demand_for(self, price, spend):
        state = make_state()
        p = engine.price_effect(D(price), state.reference_price, state.price_sensitivity)
        m = engine.marketing_effect(D(spend), state.max_marketing_boost, state.marketing_k)
        return engine.calculate_demand(state.base_demand, p, m, 1.0)

    def test_T02_price_lowers_demand(self):
        self.assertEqual(self.demand_for("5", "0"), 400)
        self.assertEqual(self.demand_for("10", "0"), 141)

    def test_T03_marketing_diminishing_returns(self):
        d0, d500, d1000 = (self.demand_for("5", s) for s in ("0", "500", "1000"))
        self.assertEqual((d0, d500, d1000), (400, 551, 607))
        self.assertLess(d1000 - d500, d500 - d0)

    def test_T04_market_factor_in_range(self):
        service = SimulatorService(MemoryRepository(), rng=random.Random(1))
        for _ in range(1000):
            factor = service.rng.uniform(MARKET_LOW, MARKET_HIGH)
            self.assertTrue(0.90 <= factor <= 1.10)

    def test_T05_sales_capped_by_stock(self):
        state = make_state(base_demand=500, max_marketing_boost=D("0"))
        r = engine.simulate_month(state, Decisions(D("5"), D("0"), 0), 1.0)
        self.assertEqual((r.units_sold, r.closing_stock), (300, 0))

    def test_T06_demand_equals_stock(self):
        state = make_state(base_demand=300, max_marketing_boost=D("0"))
        r = engine.simulate_month(state, Decisions(D("5"), D("0"), 0), 1.0)
        self.assertEqual((r.units_sold, r.closing_stock), (300, 0))

    def test_T07_months_carry_over(self):
        repo = MemoryRepository()
        service = SimulatorService(repo, rng=random.Random(3))
        profile, _ = service.create_profile("tester")
        business, _ = service.create_business(profile.user_id, 1, {
            "name": "Test Cafe", "starting_capital": "5000", "price": "3.20",
            "initial_stock": "500", "marketing_budget": "100", "base_demand": "2000",
            "reference_price": "3.20", "unit_cost": "0.90", "fixed_cost": "2500",
            "price_sensitivity": "1.4"})
        first = service.run_month(business.business_id,
                                  Decisions(D("3.20"), D("100"), 1000)).result
        second = service.run_month(business.business_id,
                                   Decisions(D("3.20"), D("100"), 1000)).result
        self.assertEqual(second.opening_cash, first.closing_cash)
        self.assertEqual(second.opening_stock, first.closing_stock)


class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.history = [result(1, "250"), result(2, "-40"), result(3, "600"),
                        result(4, "250"), result(5, "10")]

    def test_T08_merge_sort_descending_and_stable(self):
        ordered = algorithms.merge_sort(self.history, "profit", descending=True)
        self.assertEqual([r.month_no for r in ordered], [3, 1, 4, 5, 2])

    def test_T08b_merge_sort_ascending(self):
        ordered = algorithms.merge_sort(self.history, "profit", descending=False)
        self.assertEqual([r.month_no for r in ordered], [2, 5, 1, 4, 3])

    def test_T09_merge_sort_edge_cases(self):
        self.assertEqual(algorithms.merge_sort([], "profit"), [])
        one = [result(1, "5")]
        self.assertEqual(algorithms.merge_sort(one, "profit"), one)

    def test_T10_binary_search(self):
        months = [result(m, "0") for m in range(1, 7)]
        for target in (4, 1, 6):
            self.assertEqual(algorithms.binary_search(months, target).month_no, target)
        self.assertIsNone(algorithms.binary_search(months, 7))

    def test_T11_linear_search(self):
        service = SimulatorService(MemoryRepository())
        profile, _ = service.create_profile("searcher")
        form = {"starting_capital": "5000", "price": "3", "initial_stock": "0",
                "marketing_budget": "0", "base_demand": "100", "reference_price": "3",
                "unit_cost": "1", "fixed_cost": "100", "price_sensitivity": "1"}
        service.create_business(profile.user_id, 1, dict(form, name="Morning Brew"))
        service.create_business(profile.user_id, 2, dict(form, name="Crumbs"))
        found = service.search_businesses(profile.user_id, "industry_name", "cof")
        self.assertEqual([b.name for b in found], ["Morning Brew"])
        self.assertEqual(service.search_businesses(profile.user_id, "name", "zzz"), [])


class ValidationTests(unittest.TestCase):
    def test_T12_price(self):
        self.assertEqual(validation.parse_money("0.01", "Price")[0], D("0.01"))
        for bad in ("0", "-5", "abc", "1.234"):
            self.assertIsNone(validation.parse_money(bad, "Price")[0], bad)

    def test_T13_units_to_buy(self):
        for bad in ("2.5", "-1", "abc"):
            value, error = validation.parse_whole(bad, "Units to buy", 0)
            self.assertIsNone(value)
            self.assertEqual(error, "Units to buy must be a whole number of 0 or more.")

    def test_T14_cash_check_boundary(self):
        ok, errors = validation.validate_decisions("3", "300", "350", D("1000"), D("2"))
        self.assertIsNotNone(ok)
        bad, errors = validation.validate_decisions("3", "300", "351", D("1000"), D("2"))
        self.assertIsNone(bad)
        self.assertIn("£1,002.00", errors[0])


if __name__ == "__main__":
    unittest.main()
