
"""Load JSON scenarios and replay decisions deterministically."""

import json
from pathlib import Path

from product import PRODUCTS
from validation import integer, quantities
from bakery import Bakery
from order import Order


def load_json(path):
    """Read a JSON value using UTF-8."""

    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def load_orders(order_data, duration):
    """Validate and create advance Order objects from JSON data."""

    if not isinstance(order_data, list):
        raise ValueError("orders must be a list")

    orders = []

    required_fields = {
        "id",
        "product_id",
        "quantity",
        "collection_week"
    }

    for item in order_data:

        if not isinstance(item, dict):
            raise ValueError("each order must be an object")

        if set(item) != required_fields:
            raise ValueError("invalid order fields")

        order = Order(
            id=item["id"],
            product_id=item["product_id"],
            quantity=item["quantity"],
            collection_week=item["collection_week"]
        )

        if order.collection_week > duration:
            raise ValueError(
                "collection week exceeds simulation duration"
            )

        orders.append(order)

    return orders


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

    required = {
        "duration",
        "demands"
    }

    if set(scenario) - allowed or not required <= set(scenario):
        raise ValueError("invalid scenario fields")

    # Validate simulation duration.
    duration = integer(
        scenario["duration"],
        "duration",
        1,
        12
    )

    # Validate weekly demands.
    demands = scenario["demands"]

    if (
        not isinstance(demands, list)
        or len(demands) != duration
    ):
        raise ValueError(
            "one demand object is required for each week"
        )

    demands = [
        quantities(demand, PRODUCTS, "demand", 200)
        for demand in demands
    ]

    # Load advance orders.
    # Legacy scenarios without an orders field remain supported.
    order_data = scenario.get("orders", [])

    orders = load_orders(order_data, duration)

    # Create a fresh bakery with its advance orders.
    bakery = Bakery(
        duration=duration,
        initial_cash=scenario.get("initial_cash", 100000),
        initial_stock=scenario.get("initial_stock"),
        orders=orders
    )

    return bakery, demands


def replay(scenario, decisions):
    """Return weekly records and ignore decisions after bankruptcy."""

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
