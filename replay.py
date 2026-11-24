
"""Load JSON scenarios and replay decisions deterministically."""

import json
from pathlib import Path

from product import PRODUCTS
from validation import integer, quantities
from bakery import Bakery


def load_json(path):
    """Read a JSON value using UTF-8."""

    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def from_scenario(scenario):
    """Validate a scenario and return a fresh bakery and copied demands."""

    if not isinstance(scenario, dict):
        raise ValueError("scenario must be an object")

    allowed = {
        "duration",
        "demands",
        "initial_cash",
        "initial_stock",
        "orders"
    }

    required = {"duration", "demands"}

    if set(scenario) - allowed or not required.issubset(scenario):
        raise ValueError("invalid scenario fields")

    duration = integer(
        scenario["duration"],
        "duration",
        1,
        12
    )

    demands_input = scenario["demands"]

    if (
        not isinstance(demands_input, list)
        or len(demands_input) != duration
    ):
        raise ValueError(
            "one demand object is required for each week"
        )

    demands = [
        quantities(item, PRODUCTS, "demand", 200)
        for item in demands_input
    ]

    # An omitted orders field means an empty order list.
    # An explicitly supplied None is invalid.
    if "orders" in scenario:
        order_records = scenario["orders"]

        if not isinstance(order_records, list):
            raise ValueError("orders must be a list")
    else:
        order_records = []

    bakery = Bakery(
        duration=duration,
        initial_cash=scenario.get("initial_cash", 100000),
        initial_stock=scenario.get("initial_stock"),
        orders=order_records,
    )

    return bakery, demands


def replay(scenario, decisions):
    """Replay one decision per week; ignore decisions after bankruptcy."""

    bakery, demands = from_scenario(scenario)

    if (
        not isinstance(decisions, list)
        or len(decisions) != bakery.duration
    ):
        raise ValueError(
            "one decision object is required for each week"
        )

    for decision, demand in zip(decisions, demands):

        bakery.step(decision, demand)

        if bakery.is_stopped():
            break

    return bakery.get_history()
