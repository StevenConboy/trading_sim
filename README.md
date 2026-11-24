# trading_sim

Paper-trading experiment: same-day XSP index options, a "claude" arm
(direction picked with a one-line reason) against a "coin" arm (random coin
flip). Paper only. Rules are in [RULES.md](RULES.md); results go to `trades.csv`.

```
python3 trade.py status
python3 trade.py buy --direction put --reason "one line"   # 9:45 a.m. ET
python3 trade.py check
python3 trade.py close                                      # 3:15 p.m. ET
python3 trade.py report
```

Add `--dry-run` to make no orders and write no files. Standard library only
(Python 3.9+). The script talks only to paper-api.alpaca.markets and
data.alpaca.markets and sends no keys: the environment's proxy adds auth.

## Shannon's Demon test (`demon/`)

A separate experiment in its own Alpaca paper account: weekly-rebalanced
leveraged ETF / SGOV sleeves against buy-and-hold. Rules and implementation
notes are in [demon/RULES.md](demon/RULES.md).

```
python3 demon/demon.py status
python3 demon/demon.py rebalance     # 10:00 a.m. ET, Mon-Fri; acts on the first trading day of the week
python3 demon/demon.py snapshot      # 4:15 p.m. ET, Mon-Fri
python3 demon/demon.py summary
python3 demon/sim_test.py            # offline test against a fake broker
```

Files: `demon/ledger.json`, `demon/trades.csv`, `demon/equity.csv`,
`demon/summaries/`. Add `--dry-run` to make no orders and write no files.
