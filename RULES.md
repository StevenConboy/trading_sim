# Experiment rules

Paper trading only. Never live.

## Instrument
- XSP index options that expire the same day (0DTE).

## Budget
- $100 per trade, fixed. Never more.

## Two trades each market day, both real paper orders
- **claude**: the direction (call or put) is passed in, with a one-line reason.
- **coin**: the direction comes from a random coin flip. This is the control.

## Entry (9:45 a.m. ET)
- Pick the strike whose ask is closest to $0.10.
- Contracts = floor(100 / (ask x 100)).
- Buy with a limit order at the ask.
- If it isn't filled within 2 minutes, cancel it and log "no fill".

## Exit 1
- Right after the fill, place a day limit sell for half the contracts
  (rounded down) at 5x the fill price. If there is only 1 contract, skip this.

## Exit 2
- The rest runs with no cap.

## Close (3:15 p.m. ET)
- Cancel open orders and sell everything left.
- Never hold to expiry.

## Market closed / early close
- If the market is closed or closes early, do nothing and log why.

## Same contract
- If both trades land on the same contract, split fills by quantity.

## Implementation notes (how trade.py applies the rules)
- Hosts: only `paper-api.alpaca.markets` and `data.alpaca.markets`. Any other
  host is refused. The code never holds or sends API keys; the environment's
  proxy adds them.
- A 401 or 403 from any call stops the script and prints the exact response,
  except a 403 on an order POST whose body has a numeric Alpaca `code`
  (e.g. 40310000 "no available quote ... reenter with a limit"). That is an
  order rejection, not an auth failure, and is handled as one.
- Quotes come from the `indicative` options feed. The `opra` feed returned
  403 ("OPRA agreement is not signed") on this account.
- Strike ties (same distance from $0.10) go to the cheaper ask, then the
  strike furthest out of the money.
- If the ask is above $1.00, floor(100 / (ask x 100)) is 0, so no trade is
  made and the row is logged.
- A partial fill after 2 minutes keeps the filled contracts and cancels the rest.
- The close runs at 3:15 p.m. ET (moved from 3:30) so it finishes before
  Alpaca's own same-day-expiry liquidation, which can start around 3:30.
- The entry is meant for 9:45 a.m. ET. A scheduled start that runs late may
  still buy until 10:15; the actual run time is written in `notes`.
- If a buy order is rejected, the exact response is logged and the run stops.
  It never switches to another instrument.
- The close sells with a day limit order at the bid ($0.01 if there is no
  bid), never a market order: Alpaca rejects market orders on options with
  no quote. If the sell hasn't filled after 60 seconds it is left working.
  A rejected close sell is logged and the other arm still sells.
- `check` records the proceeds if a close sell left working fills later.
- Each arm sells only its own quantity through its own tagged orders, so if
  both arms hold the same contract, their fills and sales stay separate.
- Orders are tagged with client_order_id `claude-YYYYMMDD-<step>` and
  `coin-YYYYMMDD-<step>`.
- `check` and `close` rebuild any of the day's rows that are missing from
  `trades.csv` out of the arm's tagged buy order on Alpaca. That way a failed
  push from the morning run can't stop the close from selling.
