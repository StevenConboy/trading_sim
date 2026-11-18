# Event bot (events/)

This is a paper trading experiment, and it never trades live. It buys far
out-of-the-money options just before scheduled market-moving events and
sells them the next day. Each chain starts at $100 and sizes every bet with
bold play to try to reach $600,000. The bot is separate from lottery-sim
(`../trade.py`) and shares no files or state with it.

## Two chains

| chain  | what it does |
|--------|--------------|
| claude | Sends real paper orders on the alpaca-chain Alpaca account. Claude (or the built-in rule) picks the event and direction and logs one line of reasoning. |
| shadow | The control. It picks a random event and flips a coin for direction, then uses the same strike rule and books the trade at the same quotes. It sends no orders. |

Both chains live in `ledger.json`: balances, step, restarts, busts, the one
open bet, every trade and a log of skips, no-fills and busts.

## Commands (times are ET, market days only)

```
python3 events/run.py buy    # 3:15 p.m.  close what's still open, then bet on tonight / tomorrow 8:30
python3 events/run.py sell   # 9:45 a.m.  sell half of an overnight bet
python3 events/run.py fed    # 1:45 p.m.  Fed decision days only (closed by the 3:15 buy run)
python3 events/run.py probe  # read-only: SPY + one watchlist stock quotes, expected move, strikes
python3 events/run.py status | report | refresh-earnings
```

`--dry-run` works on every command. It runs every read (GET) but sends no
order and writes no file. `--at 2026-12-09T15:16` sets the clock, but only
together with `--dry-run`. `--force-time` lets a real run go ahead outside
its time window.

You can set the claude chain's pick yourself:
`buy --event cpi --direction put --reason "one line"`. `--event` takes a
candidate id (`earnings:NVDA:2026-11-18`), a ticker or a kind. If you give
no pick, the built-in rule chooses. It takes the affordable event with the
largest implied move and follows that day's momentum (call if the stock is
up on the day, put if it's down). It logs that reason. A good way to run it
is a dry run first to see the candidates, then the real run with your own
pick.

After each real run, commit and push `events/ledger.json` and
`events/earnings.json`. lottery-sim persists its state the same way. Every
scheduled run starts from a fresh clone.

## Rules

**When to trade**
- **CPI / jobs (8:30 a.m.):** buy at 3:15 p.m. the day before, using SPY
  options that expire on the event day.
- **Earnings after the close:** buy at 3:15 p.m. that day, using the nearest
  expiry after the report.
- **Earnings before the open:** buy at 3:15 p.m. the day before, using the
  nearest expiry on or after the report day.
- **Fed decision days:** buy at 1:45 p.m. using SPY options that expire the
  same day, and close at 3:15 p.m.
- **Overnight bets:** sell half (rounded down) at 9:45 a.m. the next
  morning and the rest at 3:15 p.m. A 1-contract bet sells it all at 3:15.
- **Weekends and holidays:** a bet is skipped if it would be held over a
  weekend or holiday. Days that close early are skipped, both as entry days
  and as exit days. The market calendar comes from Alpaca.
- **One open bet per chain.** If several events qualify, each chain picks
  one. A Fed bet is skipped while an overnight bet is still open.

**Strike and orders**
- **Expected move:** the ATM call mid plus the ATM put mid for the expiry.
  The ATM strike is the one closest to spot.
- **Strike:** the first strike strictly beyond spot ± the expected move, in
  the chosen direction.
- **Buys** are limit orders at the ask. If an order isn't filled in 2
  minutes, it is cancelled and logged. A partial fill keeps what filled.
- **Sells** are limit orders at the current bid. An unfilled sell is
  cancelled after 2 minutes and retried once at a fresh bid. Anything still
  unsold is logged and retried on the next run. If the contract expires
  first, it is written off at $0.
- **Shadow** books its buys at the ask and its sells at the bid, from the
  same quotes the claude chain sees.

**Sizing and ledger**
- **Stake:** `min(balance, (target - balance) / (m - 1))`, rounded down to
  whole contracts. m is 5 by default.
- **Haircut:** 15% on every fill in the ledger. Buys cost 15% more than the
  fill price, and sells pay 15% less.
- **Bust:** if the balance can't buy one contract and is below the $100
  start, the bot logs a bust, counts it and restarts that chain at $100.
  It also busts right after a close that leaves less than the price of a
  $0.01 contract. A chain that is still at or above $100 but can't afford a
  bet just skips it.
- **Target:** reaching $600,000 is logged as a target hit, and that chain
  restarts at $100.
- Settings are in `config.yaml`: start, target, m, haircut, fill wait and
  run windows.

## Data

- **`calendar.yaml`:** CPI, jobs and Fed dates from BLS and the Federal
  Reserve. **The date lists are still TODO** (see the file).
- **`watchlist.yaml`:** 31 large US names. The file explains why each one is
  there.
- **`earnings.json`:** cached earnings calendar from Nasdaq's public JSON
  (`api.nasdaq.com`, no API key). It refreshes automatically once it is 7
  days old, covering the next 21 days. On the day of a trade, the bot
  fetches that date again and skips the bet if the report has moved or
  changed time. Reports with no before-open or after-close time are never
  traded.

## Safety

- **Hosts:** the bot talks only to `paper-api.alpaca.markets`,
  `data.alpaca.markets` and `api.nasdaq.com`. It refuses every other host,
  including the live trading host.
- **Keys:** no keys appear in code. The environment's network proxy adds
  the Alpaca headers.
- **Paper account check:** the account number must start with `PA`.
- **Errors:** a 401 or 403 from Alpaca stops the run.
- **Dry run:** in `--dry-run`, any request other than GET is refused at the
  HTTP layer.
- **Order tags:** orders are tagged `evt-claude-YYYYMMDD-{buy,fed,half,close}`.
- **Unexpected positions:** if Alpaca shows an option position that the
  ledger doesn't know about, the claude chain won't open a new bet.
- **Ledger safety:** the ledger is saved even if a run crashes partway, so a
  real fill is never lost.

## Tests

```
python3 -m pytest -q events/tests
```

These cover sizing, strike choice, calendar timing (weekends, holidays,
early closes, Fed days), bust and restart, ledger updates, earnings parsing
and re-checks, and full buy, sell and fed cycles against a fake Alpaca.
