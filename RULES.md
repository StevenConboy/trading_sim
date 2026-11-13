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

## Close (3:30 p.m. ET)
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
- A 401 or 403 from any call stops the script and prints the exact response.
- Quotes come from the `indicative` options feed. The `opra` feed returned
  403 ("OPRA agreement is not signed") on this account.
- Strike ties (same distance from $0.10) go to the cheaper ask, then the
  strike furthest out of the money.
- If the ask is above $1.00, floor(100 / (ask x 100)) is 0, so no trade is
  made and the row is logged.
- A partial fill after 2 minutes keeps the filled contracts and cancels the rest.
- Each arm sells only its own quantity through its own tagged orders, so if
  both arms hold the same contract, their fills and sales stay separate.
- Orders are tagged with client_order_id `claude-YYYYMMDD-<step>` and
  `coin-YYYYMMDD-<step>`.
