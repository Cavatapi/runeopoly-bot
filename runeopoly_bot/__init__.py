"""Decision policy for computer-controlled Runeopoly seats."""

DIFFICULTIES = ("easy", "normal", "hard")

# Cash reserves apply to optional spending, never to required payments.
RESERVE = {"easy": 250, "normal": 200, "hard": 150}
BID_FRACTION = {"easy": 0.55, "normal": 0.85, "hard": 0.95}
BUILD_LIMIT = {"easy": 1, "normal": 3, "hard": 5}


def _value(tiles, tile, seat, difficulty):
    deed = tiles[tile]
    price = deed["price"]
    if difficulty == "easy":
        return price

    others = [d["owner"] for i, d in tiles.items() if i != tile and d["group"] == deed["group"]]
    owned = others.count(seat)
    if deed["group"] in ("railroad", "utility"):
        return price + owned * (20 if difficulty == "normal" else 35)

    if owned == len(others):
        return price + (90 if difficulty == "normal" else 160)
    if difficulty == "hard":
        rival = others[0]
        if rival is not None and rival != seat and all(owner == rival for owner in others):
            return price + 100
        if deed["group"] in ("orange", "red"):
            return price + 40 + owned * 35
    return price + owned * 35


def _trade_gain(tiles, offer, seat, difficulty):
    def value(tile):
        deed = tiles[tile]
        return _value(tiles, tile, seat, difficulty) - (deed["price"] // 2 if deed["mortgaged"] else 0)

    return (offer["give_gp"] - offer["take_gp"]
            + sum(value(t) for t in offer["give_tiles"]) - sum(value(t) for t in offer["take_tiles"])
            + 40 * (len(offer["give_cards"]) - len(offer["take_cards"])))


def choose_action(view, choices, difficulty):
    """Return one of the server's proposed {action, data} dictionaries, or None."""
    seat, gp, tiles = view["seat"], view["gp"], view["tiles"]
    reserve = RESERVE[difficulty]
    budget = gp - reserve
    fallback = None

    for choice in choices:
        action, data = choice["action"], choice["data"]
        tile = data.get("tile")
        if action == "buy":
            tile = view["landing"]
            price = tiles[tile]["price"]
            if difficulty == "easy" and price > 160:
                continue
            if budget >= price or (difficulty == "hard" and budget >= price - 80
                                   and _value(tiles, tile, seat, difficulty) >= price + 100):
                return choice
        elif action == "bid":
            tile = view["auction_tile"]
            amount = data["amount"]
            if amount <= min(budget, _value(tiles, tile, seat, difficulty) * BID_FRACTION[difficulty]):
                return choice
        elif action == "upgrade":
            deed = tiles[tile]
            if budget >= deed["upgrade_cost"] and deed["level"] < BUILD_LIMIT[difficulty]:
                return choice
        elif action == "unmortgage":
            deed = tiles[tile]
            value = deed["price"] // 2
            if difficulty != "easy" and budget >= (value * 110 + 99) // 100:
                return choice
        elif action == "pay_jail":
            if gp >= reserve + 50 and (difficulty == "easy" or view["owned_count"] < 5):
                return choice
        elif action == "accept_trade":
            offer = view["trade"]
            threshold = {"easy": 80, "normal": 35, "hard": 15}[difficulty]
            if gp + offer["give_gp"] - offer["take_gp"] >= reserve and _trade_gain(tiles, offer, seat, difficulty) >= threshold:
                return choice
        elif action == "resolve_mortgage" and data["unmortgage"]:
            if difficulty != "easy" and budget >= tiles[tile]["price"] // 2:
                return choice
        elif action == "mortgage":
            if fallback is None or (fallback["action"] == "mortgage"
                                    and _value(tiles, tile, seat, difficulty)
                                    < _value(tiles, fallback["data"]["tile"], seat, difficulty)):
                fallback = choice
        elif fallback is None:
            fallback = choice

    return fallback
