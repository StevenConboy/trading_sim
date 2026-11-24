# Shannon's Demon paper test: rules

Paper trading only. Never live.

## Goal
Test whether weekly rebalancing between volatile leveraged ETFs and T-bills
beats buy-and-hold of the same ETFs. Three versions side by side:
- a trendless asset (YINN)
- a trending asset (SOXL)
- a basket of wild assets that mostly move independently

## Hard rules
- Paper trading only, on the Alpaca paper endpoint (paper-api.alpaca.markets).
  Every run checks the base URL and account status first and stops if
  anything points to a live account.
- No keys in code, files or logs.
- No margin, no shorting, no options. Never spend more than available cash.
- Don't change the rules mid-test. If a change is truly needed, log the date
  and reason in CHANGELOG.md.

## Sleeves
Starting account equity is split into thirds.

| Sleeve | What | How |
|---|---|---|
| A | 50% YINN / 50% SGOV, rebalanced weekly | Real orders |
| B | 100% YINN buy-and-hold | Virtual |
| C | 50% SOXL / 50% SGOV, rebalanced weekly | Real orders |
| D | 100% SOXL buy-and-hold | Virtual |
| E | 12.5% each YINN, LABU, NAIL, TMF / 50% SGOV, rebalanced weekly | Real orders |
| F | 25% each YINN, LABU, NAIL, TMF, never rebalanced | Virtual |

- A, C and E each start with one third of equity.
- B starts with the same dollars as A, bought at A's first YINN fill.
- D starts with the same dollars as C, bought at C's first SOXL fill.
- F starts with the same dollars as E, 25% per fund at E's first fill prices.
- Virtual sleeves live in the ledger only and never trade.

## Ledger
- `ledger.json` holds each sleeve's shares and cash.
- Broker positions must equal the sum across real sleeves:
  YINN = A + E, SOXL = C, LABU/NAIL/TMF = E, SGOV = A + C + E.
- Reconcile against the broker before every rebalance. If they don't match
  (for example after a reverse split), fix the ledger from broker data and log
  what changed.
- SGOV distributions: split among A, C and E by their SGOV share counts;
  reinvested at the next rebalance. Other distributions: credited to the
  sleeves holding that fund, by share count.
- Virtual sleeves: adjusted for splits; distributions added from Alpaca's data.

## Rebalance (A, C and E only)
- First trading day of each week, 10:00 a.m. ET (Alpaca calendar; holidays skipped).
- Bring every holding back to its target weight.
- Skip any single trade under $200.
- Net orders across sleeves before sending; record each sleeve's share of the fill.
- Sell first, then buy with the proceeds.
- Fractional orders (all six funds are fractionable on Alpaca).
- Market orders, regular hours only. Record actual fill prices.

## Logging
- `trades.csv`: timestamp, sleeve, symbol, side, quantity, fill price, reason.
- `equity.csv`: daily snapshot after the close (about 4:15 p.m. ET) of every sleeve.
- `summaries/YYYY-MM-DD.md` after each rebalance: return and max drawdown per
  sleeve, A vs B, C vs D, E vs F in percentage points, number of rebalances.

## Test length
At least 6 months before drawing conclusions. No manual intervention.

## Implementation notes (how demon.py applies the rules)
- **Account.** This test has its own Alpaca paper account, used for nothing
  else. A run stops if the account holds any symbol outside the six funds, any
  short position, negative cash, or open orders that aren't from today's
  rebalance. The first run requires the account to be flat (cash = equity).
- **Keys.** The code never holds or sends API keys. The cloud environment's
  network proxy adds them to requests to `paper-api.alpaca.markets` and
  `data.alpaca.markets`; any other host is refused. A 401/403 stops the run.
- **Start.** First rebalance Monday 2026-11-30 at 10:00 ET is the initial buy.
  Equity is split into thirds rounded down to the cent; the leftover cent(s)
  go to A.
- **Cash only.** Buys are sized at 99.5% of the target dollars and checked
  against the sleeve's cash (after its sells) and the broker's cash at 0.5%
  above the latest price. Buying power and margin are never used. The few
  dollars left over stay in the sleeve as cash and count in its value.
- **$200 rule.** Applied per sleeve and per fund, before netting.
- **Netting.** Sleeve trades in the same fund are summed into one net order.
  Each sleeve's part is booked at that order's average fill price (a partial
  fill scales every part by the same fraction). A fund whose net is under $1
  (Alpaca's fractional minimum) is not sent: the sleeves trade with each other
  at the latest price.
- **Order of trades.** Phase 1 sends every fund whose net is a sell and waits
  for the fills. Phase 2 resizes the buys to the cash each sleeve now has,
  then sends the net buys. Sells are capped at what the broker holds.
- **Prices.** Valuation and sizing use Alpaca's position price for held funds,
  else the latest IEX trade (the SIP feed returns 403 on this account).
- **Reconciliation.** Shares: each sleeve's holding is scaled by
  broker/ledger, which is exactly the split ratio after a split. Cash: any
  difference from the broker (regulatory fees, cash in lieu, rounding) is
  spread across A, C, E by sleeve value. Every change is logged in the
  ledger's `events`. Reconciliation also runs at each daily snapshot.
- **Distributions.** Real sleeves: Alpaca account activities (DIV and related
  types, net of withholding), split by share count at the time they are
  processed. Virtual sleeves: Alpaca corporate-actions cash dividends,
  rate x shares, credited once the payable date has passed; splits applied
  on the ex-date. Virtual distributions stay as cash in B, D, F (never reinvested,
  since those sleeves never trade).
- **No duplicate orders.** Every order has a fixed client_order_id
  `demon-YYYYMMDD-<phase>-<SYMBOL>-<side>`. The plan is saved in the ledger
  before anything is sent; a retry resumes it and reuses any order Alpaca
  already has with that ID. If orders for today exist but the saved plan is
  gone, nothing is placed (exit 4) and the next run reconciles from the broker.
- **Timing.** The rebalance job runs at 10:00 ET Monday to Friday; the script
  acts only on the first trading day of the week and does nothing on other days.
  A start up to 20 minutes early waits for 10:00. A start later than 15 minutes
  before the close skips that week's rebalance (logged). Market orders are
  `day`, regular hours only. An order not filled within 5 minutes is cancelled
  and its partial fill is booked.
- **Max drawdown** uses the daily values in `equity.csv` plus the start and
  current value.
