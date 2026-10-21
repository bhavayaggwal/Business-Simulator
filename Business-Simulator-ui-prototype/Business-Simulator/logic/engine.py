"""Simulation engine.

Every function here is "pure": the same inputs always give the same output,
and nothing touches the database or the screen. The random market factor is
created by the services layer and passed in, so tests can fix it at 1.00.
"""
import math
from decimal import Decimal, ROUND_HALF_UP

from logic.models import BusinessState, Decisions, MonthResult

PENNY = Decimal("0.01")


def money(value) -> Decimal:
    """Round any number to pounds and pence."""
    return Decimal(str(value)).quantize(PENNY, rounding=ROUND_HALF_UP)


def price_effect(price, reference_price, sensitivity) -> float:
    """Above the typical price demand falls; below it demand rises."""
    return (float(reference_price) / float(price)) ** float(sensitivity)


def marketing_effect(spend, max_boost, k) -> float:
    """Diminishing returns: each extra pound of marketing helps less."""
    return 1 + float(max_boost) * (1 - math.exp(-float(spend) / float(k)))


def calculate_demand(base, price_eff, marketing_eff, market_factor) -> int:
    """Whole units customers want this month (a fraction of a product can't be sold)."""
    return max(0, math.floor(base * price_eff * marketing_eff * market_factor))


def units_sold(demand: int, available: int) -> int:
    """Sales can never exceed the stock available."""
    return min(demand, available)


def closing_stock(opening: int, purchased: int, sold: int) -> int:
    return opening + purchased - sold


def revenue(price, sold: int) -> Decimal:
    return money(Decimal(price) * sold)


def cogs(sold: int, unit_cost) -> Decimal:
    """Cost of goods sold: what the units that were sold cost to buy."""
    return money(Decimal(unit_cost) * sold)


def total_costs(goods_cost, marketing, fixed) -> Decimal:
    return money(Decimal(goods_cost) + Decimal(marketing) + Decimal(fixed))


def closing_cash(opening, sales_revenue, purchase_cost, marketing, fixed) -> Decimal:
    """Cash moves when stock is BOUGHT, not when it is sold."""
    return money(Decimal(opening) + Decimal(sales_revenue) - Decimal(purchase_cost)
                 - Decimal(marketing) - Decimal(fixed))


def simulate_month(state: BusinessState, decisions: Decisions,
                   market_factor: float) -> MonthResult:
    """Run one month in the order set out in the design."""
    purchase_cost = money(Decimal(decisions.units_to_buy) * state.unit_cost)
    available = state.stock + decisions.units_to_buy

    p_eff = price_effect(decisions.price, state.reference_price, state.price_sensitivity)
    m_eff = marketing_effect(decisions.marketing_spend, state.max_marketing_boost,
                             state.marketing_k)
    demand = calculate_demand(state.base_demand, p_eff, m_eff, market_factor)

    sold = units_sold(demand, available)
    stock_after = closing_stock(state.stock, decisions.units_to_buy, sold)
    sales_revenue = revenue(decisions.price, sold)
    goods_cost = cogs(sold, state.unit_cost)
    costs = total_costs(goods_cost, decisions.marketing_spend, state.fixed_cost)
    profit = money(sales_revenue - costs)
    cash_after = closing_cash(state.cash, sales_revenue, purchase_cost,
                              decisions.marketing_spend, state.fixed_cost)

    return MonthResult(
        business_id=state.business_id,
        month_no=state.month_no + 1,
        price=money(decisions.price),
        marketing_spend=money(decisions.marketing_spend),
        units_purchased=decisions.units_to_buy,
        stock_purchase_cost=purchase_cost,
        market_factor=round(market_factor, 3),
        demand=demand,
        units_sold=sold,
        opening_stock=state.stock,
        closing_stock=stock_after,
        revenue=sales_revenue,
        cogs=goods_cost,
        fixed_cost=money(state.fixed_cost),
        total_costs=costs,
        profit=profit,
        opening_cash=money(state.cash),
        closing_cash=cash_after,
    )


def explain_month(state: BusinessState, result: MonthResult) -> list:
    """Plain-English reasons shown on the results screen."""
    reasons = []
    if result.price > state.reference_price:
        reasons.append("Your price is higher than the typical price in this industry, "
                       "which lowered demand.")
    elif result.price < state.reference_price:
        reasons.append("Your price is lower than the typical price in this industry, "
                       "which raised demand, but each sale earns less.")

    available = result.opening_stock + result.units_purchased
    if result.demand > available:
        reasons.append(f"You ran out of stock: {result.demand} customers wanted to buy "
                       f"but you only had {available} units.")

    cash_change = result.closing_cash - result.opening_cash
    if result.profit > 0 and cash_change < 0:
        reasons.append("You made a profit, but cash fell because you spent more on new "
                       "stock than the stock you sold cost.")
    elif result.profit < 0 and cash_change > 0:
        reasons.append("You made a loss, but cash rose because you sold stock you had "
                       "already paid for in earlier months.")

    if result.market_factor < 0.97:
        reasons.append("The market was weaker than usual this month.")
    elif result.market_factor > 1.03:
        reasons.append("The market was stronger than usual this month.")

    if result.marketing_spend == 0:
        reasons.append("You spent nothing on marketing, so demand got no boost from it.")

    if not reasons:
        reasons.append("A steady month: your price and stock were close to what the "
                       "market wanted.")
    return reasons
