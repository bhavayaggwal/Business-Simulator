"""Input validation.

Every check returns (value, None) when the input is valid, or (None, message)
when it isn't, so each screen can show exactly what needs fixing.
"""
import re
from decimal import Decimal, InvalidOperation

from logic.models import Decisions

MAX_CAPITAL = Decimal("10000000")   # keeps totals inside DECIMAL(12,2)
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,30}$")


def parse_money(text, label, allow_zero=False):
    """A number of pounds with at most 2 decimal places."""
    cleaned = str(text).strip().replace("£", "").replace(",", "")
    if cleaned == "":
        return None, f"Enter a value for {label.lower()}."
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None, f"{label} must be a number."
    if not value.is_finite():
        return None, f"{label} must be a number."
    if value.as_tuple().exponent < -2:
        return None, f"{label} can have at most 2 decimal places."
    if allow_zero and value < 0:
        return None, f"{label} can't be negative."
    if not allow_zero and value <= 0:
        return None, f"{label} must be more than £0."
    return value, None


def parse_whole(text, label, minimum=0):
    """A whole number of at least `minimum`."""
    cleaned = str(text).strip().replace(",", "")
    if cleaned == "":
        return None, f"Enter a value for {label.lower()}."
    if not re.fullmatch(r"-?\d+", cleaned):
        return None, f"{label} must be a whole number of {minimum} or more."
    value = int(cleaned)
    if value < minimum:
        return None, f"{label} must be a whole number of {minimum} or more."
    return value, None


def parse_positive_decimal(text, label):
    """A plain number above 0 (used for price sensitivity)."""
    cleaned = str(text).strip()
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None, f"{label} must be a number."
    if not value.is_finite() or value <= 0:
        return None, f"{label} must be more than 0."
    return value, None


def validate_username(name, existing_names):
    name = name.strip()
    if not USERNAME_PATTERN.fullmatch(name):
        return None, "Username must be 3–30 letters, numbers or underscores."
    if name.lower() in (n.lower() for n in existing_names):
        return None, "That username is already taken."
    return name, None


def validate_business_form(form, existing_names):
    """Check the create-business form.

    `form` is a dict of the raw text from each field. Returns (clean_dict, errors)
    where errors maps field name -> message. clean_dict is None if any field fails.
    """
    errors = {}
    clean = {}

    name = form.get("name", "").strip()
    if not name:
        errors["name"] = "Enter a business name."
    elif len(name) > 60:
        errors["name"] = "Business name must be 60 characters or fewer."
    elif name.lower() in (n.lower() for n in existing_names):
        errors["name"] = "You already have a business with that name."
    clean["name"] = name

    def check(key, value_error):
        value, error = value_error
        if error:
            errors[key] = error
        clean[key] = value

    check("starting_capital", parse_money(form.get("starting_capital", ""), "Starting capital"))
    if clean["starting_capital"] is not None and clean["starting_capital"] >= MAX_CAPITAL:
        errors["starting_capital"] = "Starting capital must be below £10,000,000."
    check("price", parse_money(form.get("price", ""), "Price"))
    check("initial_stock", parse_whole(form.get("initial_stock", ""), "Initial stock", 0))
    check("marketing_budget", parse_money(form.get("marketing_budget", ""),
                                          "Marketing budget", allow_zero=True))
    check("base_demand", parse_whole(form.get("base_demand", ""), "Base demand", 1))
    check("reference_price", parse_money(form.get("reference_price", ""), "Typical price"))
    check("unit_cost", parse_money(form.get("unit_cost", ""), "Unit cost"))
    check("fixed_cost", parse_money(form.get("fixed_cost", ""), "Fixed costs", allow_zero=True))
    check("price_sensitivity", parse_positive_decimal(form.get("price_sensitivity", ""),
                                                      "Price sensitivity"))

    # Affordability checks only make sense once the numbers themselves are valid.
    capital = clean.get("starting_capital")
    stock = clean.get("initial_stock")
    unit_cost = clean.get("unit_cost")
    marketing = clean.get("marketing_budget")
    if None not in (capital, stock, unit_cost) and "starting_capital" not in errors:
        stock_cost = stock * unit_cost
        if stock_cost > capital:
            errors["initial_stock"] = ("You can't afford that much stock with your "
                                       "starting capital.")
        elif marketing is not None and marketing > capital - stock_cost:
            errors["marketing_budget"] = ("Marketing budget is more than the cash you "
                                          "have left.")

    if errors:
        return None, errors
    return clean, {}


def validate_decisions(price_text, marketing_text, units_text, cash, unit_cost):
    """Check one month's decisions. Returns (Decisions or None, list of messages)."""
    errors = []
    price, error = parse_money(price_text, "Price")
    if error:
        errors.append(error)
    marketing, error = parse_money(marketing_text, "Marketing spend", allow_zero=True)
    if error:
        errors.append(error)
    units, error = parse_whole(units_text, "Units to buy", 0)
    if error:
        errors.append(error)

    if not errors:
        plan_cost = units * Decimal(unit_cost) + marketing
        if plan_cost > cash:
            errors.append(f"You don't have enough cash: this plan costs £{plan_cost:,.2f} "
                          f"but you have £{Decimal(cash):,.2f}.")

    if errors:
        return None, errors
    return Decisions(price=price, marketing_spend=marketing, units_to_buy=units), []


def validate_month_number(text, current_month):
    value, error = parse_whole(text, "Month", 1)
    if error or value > current_month:
        return None, "Month not simulated yet."
    return value, None
