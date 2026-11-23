
"""Weekly trading calculations, independent of terminal input and output."""

from copy import deepcopy

from ingredient import INGREDIENTS
from product import PRODUCTS
from validation import integer, validate_decision
from stock import Stock
from orderbook import OrderBook

class Bakery:
    """A bounded simulation with stock, cash, orders and weekly records."""

    WEEKLY_RENT = 5000
    COST_PER_WORKER = 10000
    MINUTES_PER_WORKER = 600

    def __init__(
        self,
        duration=6,
        initial_cash=100000,
        initial_stock=None,
        orders=None
    ):
        self.duration = integer(duration, "duration", 1, 12)
        self._cash = integer(initial_cash, "initial_cash")
        self.stock = Stock(initial_stock)

        self.order_book = OrderBook(self.duration)
        self.orderbook = self.order_book

        if orders is not None:
            for order in orders:
                self.order_book.add_order(order)

        self.week = 1
        self.bankrupt = False
        self._history = []

    def get_stock(self):
        return self.stock.quantities

    def get_cash(self):
        return self._cash

    def get_history(self):
        return deepcopy(self._history)

    def get_orderbook(self):
        return self.order_book

    def is_stopped(self):
        return self.bankrupt or self.week > self.duration

    def step(self, decision, demand):
        """Validate and apply one complete trading week."""

        if self.is_stopped():
            raise ValueError("simulation has stopped")

        workforce, sales, purchases = validate_decision(
            decision, demand
        )

        opening_stock = dict(self.stock.quantities)
        opening_cash = self._cash

        due_orders = self.order_book.process_week(self.week)

        fulfilled_orders = []
        missed_orders = []

        order_sales = dict.fromkeys(PRODUCTS, 0)

        # Walk-in ingredient consumption.
        walk_in_consumed = {
            ingredient: sum(
                PRODUCTS[product].quantity_for(
                    INGREDIENTS[ingredient]
                ) * sales[product]
                for product in PRODUCTS
            )
            for ingredient in INGREDIENTS
        }

        if any(
            walk_in_consumed[ingredient] > opening_stock[ingredient]
            for ingredient in INGREDIENTS
        ):
            raise ValueError("insufficient ingredients")

        remaining = {
            ingredient: (
                opening_stock[ingredient] - walk_in_consumed[ingredient]
            )
            for ingredient in INGREDIENTS
        }

        # Walk-in labour.
        walk_in_minutes = sum(
            PRODUCTS[product].minutes * sales[product]
            for product in PRODUCTS
        )

        labour_capacity = workforce * self.MINUTES_PER_WORKER

        if walk_in_minutes > labour_capacity:
            raise ValueError("insufficient labour")

        remaining_labour = labour_capacity - walk_in_minutes

        # Process advance orders in ascending ID order.
        for order in sorted(due_orders, key=lambda item: item.id):

            product = PRODUCTS[order.product_id]
            quantity = order.quantity

            required_minutes = product.minutes * quantity

            required_ingredients = {
                ingredient: (
                    product.quantity_for(INGREDIENTS[ingredient])
                    * quantity
                )
                for ingredient in INGREDIENTS
            }

            enough_stock = all(
                required_ingredients[ingredient] <= remaining[ingredient]
                for ingredient in INGREDIENTS
            )

            enough_labour = required_minutes <= remaining_labour

            if enough_stock and enough_labour:
                fulfilled_orders.append(order)
                order_sales[order.product_id] += quantity

                for ingredient in INGREDIENTS:
                    remaining[ingredient] -= (
                        required_ingredients[ingredient]
                    )

                remaining_labour -= required_minutes
            else:
                missed_orders.append(order)

        # Total production and consumption.
        total_sales = {
            product: sales[product] + order_sales[product]
            for product in PRODUCTS
        }

        consumed = {
            ingredient: (
                walk_in_consumed[ingredient]
                + sum(
                    PRODUCTS[product].quantity_for(
                        INGREDIENTS[ingredient]
                    ) * order_sales[product]
                    for product in PRODUCTS
                )
            )
            for ingredient in INGREDIENTS
        }

        minutes = (
            walk_in_minutes
            + sum(
                PRODUCTS[product].minutes * order_sales[product]
                for product in PRODUCTS
            )
        )

        # Separate revenue calculations.
        walk_in_revenue = sum(
            PRODUCTS[product].price * sales[product]
            for product in PRODUCTS
        )

        order_revenue = sum(
            PRODUCTS[product].price * order_sales[product]
            for product in PRODUCTS
        )

        revenue = walk_in_revenue + order_revenue

        wages = (
            workforce * self.COST_PER_WORKER
            if revenue
            else 0
        )

        rent = self.WEEKLY_RENT

        cash_after_charges = (
            opening_cash + revenue - wages - rent
        )

        bankrupt = cash_after_charges < 0

        # Spoilage and purchase calculations.
        discarded = dict.fromkeys(INGREDIENTS, 0)
        purchased = dict.fromkeys(INGREDIENTS, 0)
        purchases_cost = 0

        if not bankrupt:
            discarded = self.stock.discarded(remaining)

            remaining = {
                ingredient: (
                    remaining[ingredient] - discarded[ingredient]
                )
                for ingredient in INGREDIENTS
            }

            if any(
                remaining[ingredient] + purchases[ingredient]
                > INGREDIENTS[ingredient].capacity
                for ingredient in INGREDIENTS
            ):
                raise ValueError("purchase exceeds capacity")

            purchases_cost = sum(
                INGREDIENTS[ingredient].price * purchases[ingredient]
                for ingredient in INGREDIENTS
            )

            if purchases_cost > cash_after_charges:
                raise ValueError("purchase is unaffordable")

            purchased = dict(purchases)

            remaining = {
                ingredient: (
                    remaining[ingredient] + purchased[ingredient]
                )
                for ingredient in INGREDIENTS
            }

        closing_cash = cash_after_charges - purchases_cost

        # Commit state only after validation.
        self.stock.update(remaining)
        self._cash = closing_cash
        self.bankrupt = bankrupt

        for order in fulfilled_orders:
            self.order_book.fulfil_order(order.id)

        for order in missed_orders:
            self.order_book.miss_order(order.id)

        # History record.
        fulfilled_ids = [
            order.id for order in fulfilled_orders
        ]

        missed_ids = [
            order.id for order in missed_orders
        ]

        record = {
            "week": self.week,
            "opening_cash": opening_cash,
            "closing_cash": self._cash,
            "workforce": workforce,

            "revenue": revenue,
            "walk_in_revenue": walk_in_revenue,
            "order_revenue": order_revenue,

            "wages": wages,
            "rent": rent,
            "purchases_cost": purchases_cost,

            "sales": dict(sales),
            "order_sales": dict(order_sales),
            "total_sales": dict(total_sales),

            "opening_stock": dict(opening_stock),
            "consumed": dict(consumed),
            "discarded": dict(discarded),
            "purchased": dict(purchased),
            "closing_stock": dict(self.stock.quantities),

            "minutes_used": minutes,

            # Stage 2 order history fields.
            "fulfilled_order_ids": list(fulfilled_ids),
            "missed_order_ids": list(missed_ids),

            # Backward-compatible aliases.
            "fulfilled_orders": list(fulfilled_ids),
            "missed_orders": list(missed_ids),

            "bankrupt": bankrupt,
        }

        self._history.append(record)
        self.week += 1

        return deepcopy(record)