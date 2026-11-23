
import unittest

from bakery import Bakery
from stock import Stock


class Issue3CalculationTests(unittest.TestCase):

    def test_spoilage_rounds_up(self):
        """Partial ingredient losses must round upwards."""

        stock = Stock({
            "flour": 3,
            "butter": 3,
            "fruit": 3
        })

        remaining = {
            "flour": 3,
            "butter": 3,
            "fruit": 3
        }

        discarded = stock.discarded(remaining)

        self.assertEqual(discarded["flour"], 0)
        self.assertEqual(discarded["butter"], 1)
        self.assertEqual(discarded["fruit"], 1)

    def test_zero_stock_has_zero_spoilage(self):
        """No remaining stock must produce zero losses."""

        stock = Stock({
            "flour": 0,
            "butter": 0,
            "fruit": 0
        })

        discarded = stock.discarded({
            "flour": 0,
            "butter": 0,
            "fruit": 0
        })

        self.assertEqual(
            discarded,
            {
                "flour": 0,
                "butter": 0,
                "fruit": 0
            }
        )

    def test_zero_cash_is_not_bankruptcy(self):
        """Cash equal to zero must not trigger bankruptcy."""

        bakery = Bakery(
            duration=1,
            initial_cash=14650,
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

        record = bakery.step(decision, demand)

        # 14650 + 350 - 10000 - 5000 = 0
        self.assertEqual(record["closing_cash"], 0)

        self.assertFalse(record["bankrupt"])
        self.assertFalse(bakery.bankrupt)

    def test_negative_cash_triggers_bankruptcy(self):
        """Negative closing cash must trigger bankruptcy."""

        bakery = Bakery(
            duration=1,
            initial_cash=14649,
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

        record = bakery.step(decision, demand)

        # 14649 + 350 - 10000 - 5000 = -1
        self.assertEqual(record["closing_cash"], -1)

        self.assertTrue(record["bankrupt"])
        self.assertTrue(bakery.bankrupt)


if __name__ == "__main__":
    unittest.main()
