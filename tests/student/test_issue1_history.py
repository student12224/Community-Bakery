
import unittest

from bakery import Bakery


class Issue1HistoryTests(unittest.TestCase):

    def test_two_bakeries_have_independent_stock(self):
        """Changing one bakery must not affect another."""

        bakery1 = Bakery()
        bakery2 = Bakery()

        bakery1.get_stock()["flour"] = 500

        self.assertEqual(
            bakery1.get_stock()["flour"], 500
        )

        self.assertEqual(
            bakery2.get_stock()["flour"], 1000
        )

    def test_previous_week_history_remains_unchanged(self):
        """A later week must not modify an earlier record."""

        bakery = Bakery(
            duration=2,
            initial_stock={
                "flour": 100,
                "butter": 20,
                "fruit": 20
            }
        )

        decision = {
            "workforce": 1,
            "sales": {
                "loaf": 1,
                "bun": 0,
                "slice": 0
            },
            "purchases": {
                "flour": 0,
                "butter": 0,
                "fruit": 0
            }
        }

        demand = {
            "loaf": 10,
            "bun": 10,
            "slice": 10
        }

        # Complete the first week.
        bakery.step(decision, demand)

        # Save the first week's historical record.
        first_history = bakery.get_history()
        first_closing_stock = first_history[0]["closing_stock"].copy()

        # Complete the second week.
        bakery.step(decision, demand)

        # Retrieve history again.
        updated_history = bakery.get_history()

        # Week 1 must retain its original closing stock.
        self.assertEqual(
            updated_history[0]["closing_stock"],
            first_closing_stock
        )


if __name__ == "__main__":
    unittest.main()
