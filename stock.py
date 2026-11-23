
"""Ingredient stock and weekly losses."""

from math import ceil

from ingredient import INGREDIENTS
from validation import quantities


class Stock:
    """Store one bakery's ingredient quantities."""

    def __init__(self, initial=None):
        # Create default stock independently for every Stock object.
        values = (
            {k: item.capacity for k, item in INGREDIENTS.items()}
            if initial is None
            else initial
        )

        # Validate quantities and create an independent dictionary.
        self.quantities = quantities(
            values,
            INGREDIENTS,
            "stock"
        )

        # Ensure that initial stock does not exceed capacity.
        if any(
            self.quantities[k] > INGREDIENTS[k].capacity
            for k in INGREDIENTS
        ):
            raise ValueError("initial stock exceeds capacity")

    def update(self, remaining):
        """Update the existing stock quantities from a dictionary."""

        for ingredient in remaining:
            self.quantities[ingredient] = remaining[ingredient]

    def discarded(self, remaining):
        """Return the whole units lost, rounded upwards."""

        discarded = {}

        for ingredient in INGREDIENTS:
            loss = (
                remaining[ingredient]
                * INGREDIENTS[ingredient].loss_percentage
                / 100
            )

            discarded[ingredient] = ceil(loss)

        return discarded
