
"""Weekly trading calculations, independent of terminal input and output."""

from copy import deepcopy

from ingredient import INGREDIENTS
from product import PRODUCTS
from validation import integer, validate_decision
from stock import Stock


class Bakery:
    """A bounded simulation with stock, cash and completed weekly records."""

    # Fixed operating rates, in pence.
    WEEKLY_RENT = 5000
    COST_PER_WORKER = 10000

    def __init__(self, duration=6, initial_cash=100000, initial_stock=None):
        self.duration = integer(duration, "duration", 1, 12)
        self._cash = integer(initial_cash, "initial_cash")
        self.stock = Stock(initial_stock)
        self.week = 1
        self.bankrupt = False
        self._history = []

    def get_stock(self):
        """Return the live stock dictionary; copy it to retain a snapshot."""
        return self.stock.quantities

    def get_cash(self):
        """Return the current cash balance in pence."""
        return self._cash

    def get_history(self):
        """Return independent record snapshots."""
        return deepcopy(self._history)

    def is_stopped(self):
        """Whether another trading week is forbidden."""
        return self.bankrupt or self.week > self.duration

    def step(self, decision, demand):
        """Validate and apply one complete week, returning a record dictionary."""

        # 1. Check whether the simulation can continue.
        if self.is_stopped():
            raise ValueError("simulation has stopped")

        # 2. Validate the decision before changing any state.
        workforce, sales, purchases = validate_decision(decision, demand)

        # 3. Capture opening stock.
        opening_stock = dict(self.stock.quantities)

        # 4. Calculate ingredient consumption.
        consumed = {
            k: sum(
                PRODUCTS[p].quantity_for(INGREDIENTS[k]) * sales[p]
                for p in PRODUCTS
            )
            for k in INGREDIENTS
        }

        # 5. Calculate labour requirements.
        minutes = sum(
            PRODUCTS[p].minutes * sales[p]
            for p in PRODUCTS
        )

        # 6. Validate ingredient availability.
        if any(
            PRODUCTS[p].quantity_for(INGREDIENTS[k]) * sales[p]
            > opening_stock[k]
            for p in PRODUCTS
            for k in INGREDIENTS
        ):
            raise ValueError("insufficient ingredients")

        # 7. Validate workforce capacity.
        if minutes > workforce * 600:
            raise ValueError("insufficient labour")

        # 8. Calculate remaining stock locally.
        # Do not update the actual stock yet.
        remaining = {
            k: opening_stock[k] - consumed[k]
            for k in INGREDIENTS
        }

        # 9. Calculate weekly financial results.
        revenue = sum(
            PRODUCTS[p].price * sales[p]
            for p in PRODUCTS
        )

        wages = (
            workforce * self.COST_PER_WORKER
            if revenue
            else 0
        )

        rent = self.WEEKLY_RENT

        cash_after_charges = (
            self._cash + revenue - wages - rent
        )

        # Exactly zero cash does not mean bankruptcy.
        bankrupt = cash_after_charges < 0

        # 10. Initialise weekly purchase and spoilage records.
        discarded = dict.fromkeys(INGREDIENTS, 0)
        purchased = dict.fromkeys(INGREDIENTS, 0)
        purchases_cost = 0

        # 11. Calculate spoilage and validate purchases
        # only if the bakery is not bankrupt.
        if not bankrupt:

            discarded = self.stock.discarded(remaining)

            remaining = {
                k: remaining[k] - discarded[k]
                for k in INGREDIENTS
            }

            # Validate storage capacity.
            if any(
                remaining[k] + purchases[k]
                > INGREDIENTS[k].capacity
                for k in INGREDIENTS
            ):
                raise ValueError("purchase exceeds capacity")

            # Calculate purchase costs.
            purchases_cost = sum(
                INGREDIENTS[k].price * purchases[k]
                for k in INGREDIENTS
            )

            # Validate available cash.
            if purchases_cost > cash_after_charges:
                raise ValueError("purchase is unaffordable")

            purchased = dict(purchases)

            # Calculate final stock locally.
            remaining = {
                k: remaining[k] + purchased[k]
                for k in INGREDIENTS
            }

        # 12. Commit all state changes only after validation succeeds.
        opening_cash = self._cash
        closing_cash = cash_after_charges - purchases_cost

        self.stock.update(remaining)
        self._cash = closing_cash
        self.bankrupt = bankrupt

        # 13. Create an independent weekly history record.
        record = {
            "week": self.week,
            "opening_cash": opening_cash,
            "closing_cash": self._cash,
            "workforce": workforce,
            "revenue": revenue,
            "wages": wages,
            "rent": rent,
            "purchases_cost": purchases_cost,
            "sales": dict(sales),
            "opening_stock": dict(opening_stock),
            "consumed": dict(consumed),
            "discarded": dict(discarded),
            "purchased": dict(purchased),
            "closing_stock": dict(self.stock.quantities),
            "minutes_used": minutes,
            "bankrupt": bankrupt,
        }

        # 14. Save history and advance the simulation.
        self._history.append(record)
        self.week += 1

        return deepcopy(record)
