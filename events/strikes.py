"""Expected move and strike choice. Pure functions."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OptionQuote:
    symbol: str
    kind: str          # call | put
    strike: Decimal
    expiry: dt.date
    bid: Decimal
    ask: Decimal

    @property
    def mid(self) -> Decimal:
        """Midpoint, or the ask when there is no bid."""
        return (self.bid + self.ask) / 2 if self.bid > 0 else self.ask


def parse_occ(symbol: str) -> tuple[str, dt.date, str, Decimal]:
    """'SPY261119C00600000' -> ('SPY', 2026-11-19, 'call', 600)."""
    tail = symbol[-15:]
    root = symbol[:-15]
    expiry = dt.date(2000 + int(tail[0:2]), int(tail[2:4]), int(tail[4:6]))
    kind = {"C": "call", "P": "put"}[tail[6]]
    return root, expiry, kind, Decimal(tail[7:]) / 1000


def expected_move(chain: list[OptionQuote], spot: Decimal) -> tuple[Decimal, Decimal] | None:
    """(at-the-money strike, expected move) for one expiry.

    ATM = the strike closest to spot that has both a quoted call and a quoted
    put (ties go to the lower strike). Expected move = call mid + put mid at
    that strike: the price of the ATM straddle.
    """
    calls = {q.strike: q for q in chain if q.kind == "call" and q.ask > 0}
    puts = {q.strike: q for q in chain if q.kind == "put" and q.ask > 0}
    both = sorted(set(calls) & set(puts))
    if not both:
        return None
    atm = min(both, key=lambda k: (abs(k - spot), k))
    return atm, calls[atm].mid + puts[atm].mid


def pick_strike(chain: list[OptionQuote], spot: Decimal, move: Decimal, direction: str) -> OptionQuote | None:
    """The first strike just beyond the expected move in `direction`.

    call: lowest strike strictly above spot + move.
    put:  highest strike strictly below spot - move.
    Strikes without an ask are passed over (they can't be bought at the ask).
    """
    if direction == "call":
        line = spot + move
        beyond = sorted((q for q in chain if q.kind == "call" and q.strike > line and q.ask > 0),
                        key=lambda q: q.strike)
    elif direction == "put":
        line = spot - move
        beyond = sorted((q for q in chain if q.kind == "put" and q.strike < line and q.ask > 0),
                        key=lambda q: -q.strike)
    else:
        raise ValueError(direction)
    return beyond[0] if beyond else None
