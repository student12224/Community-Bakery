
"""Advance customer orders for the Community Bakery simulation."""

from product import PRODUCTS


class Order:
    """Represent one customer's advance order."""

    VALID_STATUSES = {"pending", "fulfilled", "missed"}

    def __init__(self, id, product_id, quantity, collection_week):

        if not isinstance(id, str):
            raise ValueError("order ID must be a string")

        if not id or not id.strip():
            raise ValueError("order ID cannot be empty")

        if id != id.strip():
            raise ValueError("order ID cannot contain surrounding whitespace")

        if not isinstance(product_id, str):
            raise ValueError("product ID must be a string")

        if product_id not in PRODUCTS:
            raise ValueError("invalid product ID")

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            raise ValueError("quantity must be an integer")

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if isinstance(collection_week, bool) or not isinstance(collection_week, int):
            raise ValueError("collection week must be an integer")

        if collection_week < 1:
            raise ValueError("collection week must be at least 1")

        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.collection_week = collection_week
        self.status = "pending"

    def mark_fulfilled(self):
        """Mark a pending order as fulfilled."""

        if self.status != "pending":
            raise ValueError("only pending orders can be fulfilled")

        self.status = "fulfilled"

    def mark_missed(self):
        """Mark a pending order as missed."""

        if self.status != "pending":
            raise ValueError("only pending orders can be missed")

        self.status = "missed"

    def __repr__(self):
        return (
            f"Order(id={self.id!r}, "
            f"product_id={self.product_id!r}, "
            f"quantity={self.quantity}, "
            f"collection_week={self.collection_week}, "
            f"status={self.status!r})"
        )
