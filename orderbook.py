
"""Manage advance customer orders."""

from order import Order

class OrderBook:
    """Store and manage advance customer orders."""

    def __init__(self, duration=12):
        if (
            isinstance(duration, bool)
            or not isinstance(duration, int)
            or duration < 1
        ):
            raise ValueError("duration must be a positive integer")

        self.duration = duration
        self.orders = []

    def add_order(self, order):
        """Add an Order instance or dictionary."""

        if isinstance(order, dict):
            try:
                order = Order(
                    id=order["id"],
                    product_id=order["product_id"],
                    quantity=order["quantity"],
                    collection_week=order["collection_week"]
                )
            except KeyError as exc:
                raise ValueError(
                    f"missing order field: {exc.args[0]}"
                ) from exc

        if not isinstance(order, Order):
            raise ValueError("order must be an Order instance")

        if any(existing.id == order.id for existing in self.orders):
            raise ValueError("duplicate order ID")

        if order.collection_week > self.duration:
            raise ValueError(
                "collection week exceeds simulation duration"
            )

        self.orders.append(order)
        return order

    def get_order(self, order_id):
        """Find an order by ID."""

        for order in self.orders:
            if order.id == order_id:
                return order

        raise ValueError("order not found")

    def get_orders(self):
        """Return all orders in ascending ID order."""

        return sorted(self.orders, key=lambda order: order.id)

    def get_pending_orders(self, collection_week=None):
        """Return pending orders."""

        result = [
            order for order in self.orders
            if order.status == "pending"
            and (
                collection_week is None
                or order.collection_week == collection_week
            )
        ]

        return sorted(result, key=lambda order: order.id)

    def get_fulfilled_orders(self):
        """Return fulfilled orders."""

        return sorted(
            [
                order for order in self.orders
                if order.status == "fulfilled"
            ],
            key=lambda order: order.id
        )

    def get_missed_orders(self):
        """Return missed orders."""

        return sorted(
            [
                order for order in self.orders
                if order.status == "missed"
            ],
            key=lambda order: order.id
        )

    def fulfil_order(self, order_id):
        """Mark an order as fulfilled."""

        self.get_order(order_id).mark_fulfilled()

    def fulfill_order(self, order_id):
        """US spelling alias."""

        self.fulfil_order(order_id)

    def miss_order(self, order_id):
        """Mark an order as missed."""

        self.get_order(order_id).mark_missed()

    def process_week(self, week):
        """Return pending orders due in the specified week."""

        if (
            isinstance(week, bool)
            or not isinstance(week, int)
            or week < 1
            or week > self.duration
        ):
            raise ValueError("week is outside the simulation duration")

        return self.get_pending_orders(week)

    def __len__(self):
        return len(self.orders)

    def __repr__(self):
        return (
            f"OrderBook(duration={self.duration}, "
            f"orders={len(self.orders)})"
        )