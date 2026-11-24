
"""Validate, store and select advance customer orders."""

from order import Order


class OrderBook:
    """Own the complete, validated batch of orders for one simulation."""

    REQUIRED_FIELDS = {"id", "product_id", "quantity", "collection_week"}

    def __init__(self, records, duration):
        if type(duration) is not int or not 1 <= duration <= 12:
            raise ValueError("duration must be an integer from 1 to 12")

        if not isinstance(records, list):
            raise ValueError("orders must be a list")

        # Validate the complete batch before accepting any orders.
        validated_orders = []
        seen_ids = set()

        for record in records:
            if not isinstance(record, dict):
                raise ValueError("each order record must be an object")

            if set(record) != self.REQUIRED_FIELDS:
                raise ValueError(
                    "each order must contain exactly id, product_id, "
                    "quantity and collection_week"
                )

            order = Order(
                record["id"],
                record["product_id"],
                record["quantity"],
                record["collection_week"],
            )

            if order.collection_week > duration:
                raise ValueError(
                    "collection week exceeds simulation duration"
                )

            if order.id in seen_ids:
                raise ValueError("duplicate order ID")

            seen_ids.add(order.id)
            validated_orders.append(order)

        self.duration = duration
        self.orders = validated_orders

    def due_orders(self, week):
        """Return pending orders due this week in ascending ID order."""

        if type(week) is not int or not 1 <= week <= self.duration:
            raise ValueError("week is outside the simulation duration")

        return sorted(
            (
                order for order in self.orders
                if order.status == "pending"
                and order.collection_week == week
            ),
            key=lambda order: order.id,
        )

    def mark_fulfilled(self, order):
        """Mark an owned pending order as fulfilled."""

        if order not in self.orders:
            raise ValueError("order does not belong to this order book")

        order.mark_fulfilled()

    def mark_missed(self, order):
        """Mark an owned pending order as missed."""

        if order not in self.orders:
            raise ValueError("order does not belong to this order book")

        order.mark_missed()

    def get_order(self, order_id):
        """Return the order with the supplied ID."""

        for order in self.orders:
            if order.id == order_id:
                return order

        raise ValueError("order not found")

    def __len__(self):
        return len(self.orders)
