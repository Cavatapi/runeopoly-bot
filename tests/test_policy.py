import unittest

from runeopoly_bot import choose_action


def choice(action, **data):
    return {"action": action, "data": data}


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.view = {
            "seat": 2, "gp": 400, "landing": 18, "auction_tile": 18, "owned_count": 2,
            "tiles": {16: {"group": "orange", "price": 180, "owner": 2},
                      18: {"group": "orange", "price": 180, "owner": None},
                      19: {"group": "orange", "price": 200, "owner": 2}},
        }

    def test_easy_declines_expensive_property(self):
        self.view["gp"] = 1000
        options = [choice("buy"), choice("auction")]
        self.assertEqual(choose_action(self.view, options, "easy"), options[1])
        self.assertEqual(choose_action(self.view, options, "normal"), options[0])

    def test_hard_bids_to_complete_a_set(self):
        self.view["gp"] = 600
        options = [choice("bid", amount=250), choice("pass")]
        self.assertEqual(choose_action(self.view, options, "normal"), options[1])
        self.assertEqual(choose_action(self.view, options, "hard"), options[0])

    def test_hard_keeps_cash_for_future_turns(self):
        self.view["gp"] = 180
        options = [choice("bid", amount=100), choice("pass")]
        self.assertEqual(choose_action(self.view, options, "hard"), options[1])

    def test_required_payment_is_not_subject_to_cash_reserve(self):
        payment = choice("pay_rent", tile=18, amount=300, to=1)
        self.assertEqual(choose_action(self.view, [payment], "normal"), payment)

    def test_rejects_trade_that_costs_more_than_it_returns(self):
        self.view["trade"] = {"give_gp": 25, "take_gp": 100,
                              "give_tiles": [], "take_tiles": [], "give_cards": [], "take_cards": []}
        options = [choice("accept_trade", trade_id="x"), choice("cancel_trade", trade_id="x")]
        self.assertEqual(choose_action(self.view, options, "hard"), options[1])
