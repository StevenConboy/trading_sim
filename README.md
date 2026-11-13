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
