"""Default data used to seed the database.

The industry figures are PLACEHOLDERS for the prototype: they produce sensible
results but should be reviewed (e.g. with a business teacher) before final use.
Users can change them when they create a business.
"""
from decimal import Decimal as D

# name, base_demand, reference_price, unit_cost, fixed_cost,
# price_sensitivity, max_marketing_boost, marketing_k
INDUSTRIES = [
    ("Coffee Shop",   2000, D("3.20"),  D("0.90"),  D("2500.00"), D("1.40"), D("0.50"), D("400")),
    ("Bakery",        1500, D("2.50"),  D("0.80"),  D("2000.00"), D("1.30"), D("0.40"), D("300")),
    ("Clothing Shop",  300, D("25.00"), D("10.00"), D("3000.00"), D("1.60"), D("0.70"), D("800")),
    ("Gym",            150, D("35.00"), D("10.00"), D("4000.00"), D("1.20"), D("0.60"), D("600")),
]

# term, definition, example
GLOSSARY = [
    ("Demand",
     "The number of units customers are willing and able to buy at a given price "
     "over a period of time.",
     "At £5, customers want 450 units this month."),
    ("Units sold",
     "How many products were actually sold. It can't be more than the stock you had.",
     "Demand 500, stock 300 → 300 sold."),
    ("Revenue",
     "All the money received from sales.",
     "Price × units sold = £5 × 450 = £2,250."),
    ("Cost of goods sold (COGS)",
     "What the products you sold cost you to buy.",
     "450 units × £2 = £900."),
    ("Fixed costs",
     "Costs that stay the same however much you sell, such as rent and wages.",
     "£800 every month."),
    ("Marketing spend",
     "Money spent advertising to increase demand. Each extra pound has a smaller effect.",
     "£300 this month."),
    ("Profit / loss",
     "Revenue minus total costs. A negative number is a loss.",
     "£2,250 − £2,000 = £250 profit."),
    ("Cash balance",
     "The money the business actually has available right now.",
     "£4,150 at the end of the month."),
    ("Cash flow",
     "Money coming in minus money going out over the month. It can differ from profit.",
     "Profit +£250, but cash −£850."),
    ("Stock / inventory",
     "Products the business holds, ready to sell.",
     "850 units in the warehouse."),
]
