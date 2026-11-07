# Runeopoly Bot

A Python decision policy for computer-controlled players in [Runeopoly](https://github.com/Cavatapi/Runeopoly). Install it in the Python environment that runs the Runeopoly server.

```sh
python -m pip install "runeopoly-bot @ git+https://github.com/Cavatapi/runeopoly-bot.git"
```

Restart the server after installing. In a Runeopoly lobby, the banker can add a bot to each open seat and pick its difficulty and an available NPC token.

| Difficulty | Behavior |
| --- | --- |
| Easy | Focuses on cheap deeds, bids low, and builds slowly. |
| Normal | Values sets and railroads, maintains a cash reserve, and develops useful groups. |
| Hard | Pays more to complete sets or deny them to rivals, favors orange and red properties, and develops more aggressively. |

Bots can roll, buy, bid, pay rent, resolve cards and jail, manage property and debt, and respond to trade offers. The strategy uses the board and economy only. It runs in the Runeopoly server process without network access or a RuneLite login.

## Policy interface

`choose_action(view, choices, difficulty)` receives an economy-only view, a list of proposed `{"action": ..., "data": {...}}` dictionaries, and a member of `DIFFICULTIES`. It returns one of those dictionaries or `None`. The server owns the game state and validates the selected command.

The view has `seat`, `gp`, `landing`, `owned_count`, `auction_tile`, `trade`, and `tiles`. The tile map uses integer board positions with price, group, owner, mortgaged status, planned building level, and optional upgrade cost. Trade data is relative to the sender. Mandatory actions and passes are available in the choices.

Run the policy tests with `python -m unittest discover -s tests`.
