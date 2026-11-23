
import unittest

from bakery import Bakery


class Issue2ValidationTests(unittest.TestCase):

    def test_rejected_purchase_preserves_all_state(self):
        """Excessive purchases must not modify bakery state."""

        bakery = Bakery(
            duration=2,
            initial_cash=100000,
            initial_stock={
                "flour": 1000,
                "butter": 400,
                "fruit": 400
            }
        )

        original_stock = bakery.get_stock().copy()
        original_cash = bakery.get_cash()
        original_week = bakery.week
        original_history = bakery.get_history()
        original_bankrupt = bakery.bankrupt

        decision = {
            "workforce": 1,
            "sales": {
                "loaf": 1,
                "bun": 0,
                "slice": 0
            },
            "purchases": {
                "flour": 1000,
                "butter": 0,
                "fruit": 0
            }
        }

        demand = {
            "loaf": 10,
            "bun": 10,
            "slice": 10
        }

        # The purchase exceeds available flour capacity.
        with self.assertRaises(ValueError):
            bakery.step(decision, demand)

        # Verify that no simulation state has changed.
        self.assertEqual(
            bakery.get_stock(), original_stock
        )

        self.assertEqual(
            bakery.get_cash(), original_cash
        )

        self.assertEqual(
            bakery.week, original_week
        )

        self.assertEqual(
            bakery.get_history(), original_history
        )

        self.assertEqual(
            bakery.bankrupt, original_bankrupt
        )

    def test_unaffordable_purchase_is_rejected(self):
        """Purchases must not exceed available cash."""

        bakery = Bakery(
            duration=2,
            initial_cash=10000,
            initial_stock={
                "flour": 0,
                "butter": 0,
                "fruit": 0
            }
        )

        original_stock = bakery.get_stock().copy()
        original_cash = bakery.get_cash()

        decision = {
            "workforce": 1,
            "sales": {
                "loaf": 0,
                "bun": 0,
                "slice": 0
            },
            "purchases": {
                "flour": 600,
                "butter": 0,
                "fruit": 0
            }
        }

        demand = {
            "loaf": 10,
            "bun": 10,
            "slice": 10
        }

        # Flour costs 6000 pence, but only 5000
        # pence remains after weekly rent.
        with self.assertRaises(ValueError):
            bakery.step(decision, demand)

        self.assertEqual(
            bakery.get_stock(), original_stock
        )

        self.assertEqual(
            bakery.get_cash(), original_cash
        )

        self.assertEqual(bakery.week, 1)
        self.assertEqual(bakery.get_history(), [])


if __name__ == "__main__":
    unittest.main()
