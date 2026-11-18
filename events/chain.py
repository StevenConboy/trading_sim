"""The two chains: bold-play sizing, haircut, bust/restart, and the ledger.

The ledger is a plain dict (saved as ledger.json). All money is kept as
strings of Decimals so the JSON round-trips exactly.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal

MULTIPLIER = 100
CHAINS = ("claude", "shadow")
MIN_TICK = Decimal("0.01")


@dataclass(frozen=True)
class Rules:
    start: Decimal = Decimal("100")
    target: Decimal = Decimal("600000")
    win_multiple: Decimal = Decimal("5")
    slippage: Decimal = Decimal("0.15")


def D(x) -> Decimal:
    return Decimal(str(x))


def money(x: Decimal) -> str:
    return str(D(x).quantize(Decimal("0.01")))


# --------------------------------------------------------------------------
# Sizing and haircut
# --------------------------------------------------------------------------
def stake(balance: Decimal, r: Rules) -> Decimal:
    """Bold play: min(balance, (target - balance) / (m - 1))."""
    if balance >= r.target:
        return Decimal(0)
    return min(balance, (r.target - balance) / (r.win_multiple - 1))


def buy_value(qty: int, price: Decimal, r: Rules) -> Decimal:
    """Ledger cost of a buy fill: the fill is worth 15% less to us, so we pay 15% more."""
    return qty * price * MULTIPLIER * (1 + r.slippage)


def sell_value(qty: int, price: Decimal, r: Rules) -> Decimal:
    """Ledger proceeds of a sell fill: 15% less than the fill price."""
    return qty * price * MULTIPLIER * (1 - r.slippage)


def one_contract(ask: Decimal, r: Rules) -> Decimal:
    return buy_value(1, ask, r)


def contracts_for(balance: Decimal, ask: Decimal, r: Rules) -> int:
    """Whole contracts the bold-play stake buys at `ask`, after the haircut."""
    if ask <= 0:
        return 0
    return int((stake(balance, r) / one_contract(ask, r)).to_integral_value(rounding=ROUND_FLOOR))


# --------------------------------------------------------------------------
# Ledger
# --------------------------------------------------------------------------
def new_chain(r: Rules) -> dict:
    return {"balance": money(r.start), "step": 0, "restarts": 0, "busts": 0,
            "targets_hit": 0, "open": None}


def new_ledger(r: Rules) -> dict:
    return {"version": 1, "chains": {c: new_chain(r) for c in CHAINS}, "trades": [], "log": []}


def note(ledger: dict, when: dt.datetime, chain: str, msg: str) -> None:
    ledger["log"].append({"time": when.isoformat(timespec="seconds"), "chain": chain, "msg": msg})


def open_trade(ledger: dict, chain: str) -> dict | None:
    tid = ledger["chains"][chain]["open"]
    if tid is None:
        return None
    return next(t for t in ledger["trades"] if t["id"] == tid)


def bust(ledger: dict, chain: str, when: dt.datetime, why: str, r: Rules) -> None:
    c = ledger["chains"][chain]
    note(ledger, when, chain, f"BUST #{c['busts'] + 1}: {why}; balance {c['balance']} -> restart at {money(r.start)}")
    c["busts"] += 1
    c["restarts"] += 1
    c["balance"] = money(r.start)
    c["step"] = 0


def size_bet(ledger: dict, chain: str, ask: Decimal, when: dt.datetime, r: Rules) -> tuple[int, str | None]:
    """Contracts to buy for this chain at `ask`, busting and restarting first if needed.

    Returns (contracts, reason-if-0). A bust happens when the balance can't
    buy one contract and is below the start balance (a chain that is at or
    above the start just can't afford this bet; that is a skip, not a bust).
    """
    c = ledger["chains"][chain]
    bal = D(c["balance"])
    cost1 = one_contract(ask, r)
    if bal < cost1 and bal < r.start:
        bust(ledger, chain, when, f"balance {money(bal)} can't buy one contract at ${money(cost1)}", r)
        bal = D(c["balance"])
    n = contracts_for(bal, ask, r)
    if n == 0:
        return 0, (f"can't afford one contract: ${money(cost1)} with haircut, "
                   f"stake ${money(stake(bal, r))} of balance ${money(bal)}")
    return n, None


def record_entry(ledger: dict, chain: str, when: dt.datetime, *, event: str, event_id: str, ticker: str,
                 direction: str, symbol: str, strike: Decimal, expiry: dt.date, qty: int, price: Decimal,
                 quote_ask: Decimal, reasoning: str, overnight: bool, exit_day: dt.date, r: Rules) -> dict:
    """Book a filled buy: debit the haircut cost, step + 1, open the position."""
    c = ledger["chains"][chain]
    if c["open"] is not None:
        raise RuntimeError(f"{chain} already has an open bet ({c['open']}); one at a time")
    cost = buy_value(qty, price, r)
    c["balance"] = money(D(c["balance"]) - cost)
    c["step"] += 1
    tid = f"{chain}-{when:%Y%m%d-%H%M}"
    t = {
        "id": tid, "chain": chain, "date": when.date().isoformat(), "time": when.strftime("%H:%M"),
        "event": event, "event_id": event_id, "ticker": ticker, "direction": direction,
        "symbol": symbol, "strike": str(strike), "expiry": expiry.isoformat(),
        "contracts": qty, "remaining": qty, "quote_ask": str(quote_ask),
        "entry_price": str(price), "entry_value": money(cost),
        "exits": [], "exit_value": "0.00", "haircut_value": None,
        "balance_after": None, "step": c["step"], "restarts": c["restarts"],
        "overnight": overnight, "exit_day": exit_day.isoformat(), "half_done": not overnight,
        "status": "open", "reasoning": reasoning,
    }
    ledger["trades"].append(t)
    c["open"] = tid
    return t


def record_exit(ledger: dict, chain: str, when: dt.datetime, qty: int, price: Decimal, r: Rules,
                how: str = "") -> dict:
    """Book a sell fill. Closes the bet when nothing is left, then checks bust / target."""
    t = open_trade(ledger, chain)
    if t is None:
        raise RuntimeError(f"{chain} has no open bet")
    if qty > t["remaining"]:
        raise ValueError(f"selling {qty} but only {t['remaining']} left")
    c = ledger["chains"][chain]
    value = sell_value(qty, price, r)
    c["balance"] = money(D(c["balance"]) + value)
    t["remaining"] -= qty
    t["exits"].append({"time": when.isoformat(timespec="minutes"), "qty": qty, "price": str(price),
                       "value": money(value), **({"how": how} if how else {})})
    t["exit_value"] = money(D(t["exit_value"]) + value)
    if t["remaining"] == 0:
        close_out(ledger, chain, when, r)
    return t


def close_out(ledger: dict, chain: str, when: dt.datetime, r: Rules) -> None:
    t = open_trade(ledger, chain)
    c = ledger["chains"][chain]
    t["status"] = "closed"
    t["haircut_value"] = t["exit_value"]
    t["balance_after"] = c["balance"]
    t["profit"] = money(D(t["exit_value"]) - D(t["entry_value"]))
    c["open"] = None
    bal = D(c["balance"])
    if bal >= r.target:
        note(ledger, when, chain, f"TARGET HIT: balance {money(bal)} >= {money(r.target)} at step {c['step']}; "
             f"restart at {money(r.start)}")
        c["targets_hit"] += 1
        c["restarts"] += 1
        c["balance"] = money(r.start)
        c["step"] = 0
    elif bal < one_contract(MIN_TICK, r):
        bust(ledger, chain, when, f"balance {money(bal)} can't buy even a $0.01 contract", r)


def write_off(ledger: dict, chain: str, when: dt.datetime, why: str, r: Rules) -> None:
    """Close what's left at $0 (e.g. the contract expired before it could be sold)."""
    t = open_trade(ledger, chain)
    left = t["remaining"]
    t["remaining"] = 0
    t["exits"].append({"time": when.isoformat(timespec="minutes"), "qty": left, "price": "0",
                       "value": "0.00", "how": f"written off: {why}"})
    note(ledger, when, chain, f"{t['symbol']}: {left} contracts written off at $0 ({why})")
    close_out(ledger, chain, when, r)
