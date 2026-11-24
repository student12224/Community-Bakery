
"""Advance customer orders for the Community Bakery simulation."""

from product import PRODUCTS


class Order:
    """Represent one customer's advance order and its current status."""

    VALID_STATUSES = {"pending", "fulfilled", "missed"}

    def __init__(self, id, product_id, quantity, collection_week):
        if not isinstance(id, str) or not id or not id.strip():
            raise ValueError("order ID must be a non-empty string")

        if id != id.strip():
            raise ValueError("order ID must not have surrounding whitespace")

        if not isinstance(product_id, str) or product_id not in PRODUCTS:
            raise ValueError("invalid product ID")

        if type(quantity) is not int or quantity <= 0:
            raise ValueError("quantity must be a positive integer")

        if type(collection_week) is not int or not 1 <= collection_week <= 12:
            raise ValueError("collection week must be an integer from 1 to 12")

        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.collection_week = collection_week
        self.status = "pending"

    def mark_fulfilled(self):
        """Change a pending order to fulfilled."""
        if self.status != "pending":
            raise ValueError("only pending orders can be fulfilled")
        self.status = "fulfilled"

    def mark_missed(self):
        """Change a pending order to missed."""
        if self.status != "pending":
            raise ValueError("only pending orders can be marked missed")
        self.status = "missed"

    def __repr__(self):
        return (
            f"Order(id={self.id!r}, product_id={self.product_id!r}, "
            f"quantity={self.quantity}, collection_week={self.collection_week}, "
            f"status={self.status!r})"
        )
