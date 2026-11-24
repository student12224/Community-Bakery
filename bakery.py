
"""Weekly trading calculations, independent of terminal input and output."""

from copy import deepcopy

from ingredient import INGREDIENTS
from product import PRODUCTS
from validation import integer, validate_decision
from stock import Stock
from orderbook import OrderBook


class Bakery:
    """A bounded simulation with stock, cash, advance orders and weekly records."""

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

        order_records = [] if orders is None else orders
        self.order_book = OrderBook(order_records, self.duration)

        self.week = 1
        self.bankrupt = False
        self._history = []

    def get_stock(self):
        """Return the live stock dictionary."""
        return self.stock.quantities

    def get_cash(self):
        """Return the current cash balance in pence."""
        return self._cash

    def get_history(self):
        """Return independent snapshots of completed weekly records."""
        return deepcopy(self._history)

    def is_stopped(self):
        """Return whether bankruptcy or duration stopped trading."""
        return self.bankrupt or self.week > self.duration

    def step(self, decision, demand):
        """Validate and commit one complete week, including due advance orders."""

        if self.is_stopped():
            raise ValueError("simulation has stopped")

        # Validate the entire walk-in decision before changing state.
        workforce, sales, purchases = validate_decision(decision, demand)

        opening_stock = dict(self.stock.quantities)
        opening_cash = self._cash
        labour_available = workforce * self.MINUTES_PER_WORKER

        # Keep all order outcomes provisional until the complete
        # weekly decision, including purchases, has been validated.
        fulfilled_orders = []
        missed_orders = []
        order_sales = dict.fromkeys(PRODUCTS, 0)
        remaining_stock = dict(opening_stock)

        # Advance orders have priority over walk-in sales.
        for order in self.order_book.due_orders(self.week):

            product = PRODUCTS[order.product_id]
            needed_minutes = product.minutes * order.quantity

            needed_ingredients = {
                ingredient: (
                    product.quantity_for(INGREDIENTS[ingredient])
                    * order.quantity
                )
                for ingredient in INGREDIENTS
            }

            can_make = (
                needed_minutes <= labour_available
                and all(
                    needed_ingredients[name] <= remaining_stock[name]
                    for name in INGREDIENTS
                )
            )

            if can_make:
                fulfilled_orders.append(order)
                order_sales[order.product_id] += order.quantity
                labour_available -= needed_minutes

                for name in INGREDIENTS:
                    remaining_stock[name] -= needed_ingredients[name]

            else:
                # A missed order consumes no resources.
                missed_orders.append(order)

        # Validate all walk-in production against resources remaining
        # after advance orders have been considered.
        walk_in_minutes = sum(
            PRODUCTS[product_id].minutes * sales[product_id]
            for product_id in PRODUCTS
        )

        if walk_in_minutes > labour_available:
            raise ValueError("insufficient labour")

        walk_in_consumed = {
            ingredient: sum(
                PRODUCTS[product_id].quantity_for(
                    INGREDIENTS[ingredient]
                ) * sales[product_id]
                for product_id in PRODUCTS
            )
            for ingredient in INGREDIENTS
        }

        if any(
            walk_in_consumed[name] > remaining_stock[name]
            for name in INGREDIENTS
        ):
            raise ValueError("insufficient ingredients")

        for name in INGREDIENTS:
            remaining_stock[name] -= walk_in_consumed[name]

        # Calculate total ingredient consumption.
        order_consumed = {
            ingredient: sum(
                PRODUCTS[product_id].quantity_for(
                    INGREDIENTS[ingredient]
                ) * order_sales[product_id]
                for product_id in PRODUCTS
            )
            for ingredient in INGREDIENTS
        }

        consumed = {
            ingredient: (
                order_consumed[ingredient] + walk_in_consumed[ingredient]
            )
            for ingredient in INGREDIENTS
        }

        # Calculate total production minutes.
        order_minutes = sum(
            PRODUCTS[product_id].minutes * order_sales[product_id]
            for product_id in PRODUCTS
        )

        minutes_used = order_minutes + walk_in_minutes

        # Calculate separate revenue streams.
        order_revenue = sum(
            PRODUCTS[product_id].price * order_sales[product_id]
            for product_id in PRODUCTS
        )

        walk_in_revenue = sum(
            PRODUCTS[product_id].price * sales[product_id]
            for product_id in PRODUCTS
        )

        revenue = order_revenue + walk_in_revenue

        # The full workforce is paid even when there are no sales.
        wages = workforce * self.COST_PER_WORKER
        rent = self.WEEKLY_RENT

        cash_after_charges = opening_cash + revenue - wages - rent
        bankrupt = cash_after_charges < 0

        discarded = dict.fromkeys(INGREDIENTS, 0)
        purchased = dict.fromkeys(INGREDIENTS, 0)
        purchases_cost = 0

        if not bankrupt:

            # Apply weekly spoilage after production.
            discarded = self.stock.discarded(remaining_stock)

            after_loss = {
                name: remaining_stock[name] - discarded[name]
                for name in INGREDIENTS
            }

            # Purchases arrive at the end of the week.
            if any(
                after_loss[name] + purchases[name]
                > INGREDIENTS[name].capacity
                for name in INGREDIENTS
            ):
                raise ValueError("purchase exceeds capacity")

            purchases_cost = sum(
                INGREDIENTS[name].price * purchases[name]
                for name in INGREDIENTS
            )

            if purchases_cost > cash_after_charges:
                raise ValueError("purchase is unaffordable")

            purchased = dict(purchases)

            closing_stock = {
                name: after_loss[name] + purchased[name]
                for name in INGREDIENTS
            }

        else:
            # Bankruptcy skips spoilage and purchases.
            # Purchase quantities have already passed type validation.
            closing_stock = remaining_stock

        closing_cash = cash_after_charges - purchases_cost

        # Commit all state only after every rejection condition is checked.
        self.stock.update(closing_stock)
        self._cash = closing_cash
        self.bankrupt = bankrupt

        for order in fulfilled_orders:
            self.order_book.mark_fulfilled(order)

        for order in missed_orders:
            self.order_book.mark_missed(order)

        fulfilled_ids = [order.id for order in fulfilled_orders]
        missed_ids = [order.id for order in missed_orders]

        record = {
            "week": self.week,
            "workforce": workforce,
            "opening_cash": opening_cash,
            "closing_cash": self._cash,

            "revenue": revenue,
            "walk_in_revenue": walk_in_revenue,
            "order_revenue": order_revenue,

            "wages": wages,
            "rent": rent,
            "purchases_cost": purchases_cost,

            # Sales records walk-in quantities only.
            "sales": dict(sales),

            "opening_stock": dict(opening_stock),
            "consumed": dict(consumed),
            "discarded": dict(discarded),
            "purchased": dict(purchased),
            "closing_stock": dict(self.stock.quantities),

            "minutes_used": minutes_used,
            "bankrupt": bankrupt,

            "fulfilled_order_ids": fulfilled_ids,
            "missed_order_ids": missed_ids,
        }

        self._history.append(record)
        self.week += 1

        return deepcopy(record)
