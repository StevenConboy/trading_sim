"""Alpaca paper trading + market data. Only the two Alpaca hosts are allowed."""
from __future__ import annotations

import datetime as dt
import time
from decimal import Decimal

import net
from strikes import OptionQuote, parse_occ

TRADING = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
ALLOWED = frozenset({"paper-api.alpaca.markets", "data.alpaca.markets"})
OPTION_FEED = "indicative"   # "opra" returned 403 on the lottery-sim account (no OPRA agreement)
STOCK_FEED = "iex"
MAX_QUOTE_AGE = dt.timedelta(minutes=20)   # set from config.yaml by run.py
TERMINAL = {"filled", "canceled", "expired", "rejected", "done_for_day", "replaced"}


class StaleQuote(Exception):
    """The latest quote is older than MAX_QUOTE_AGE (e.g. yesterday's close)."""


def parse_ts(t: str) -> dt.datetime:
    """Alpaca timestamp ('2026-11-18T21:14:59.00163899Z', nanoseconds) -> aware UTC datetime."""
    t = t.strip().removesuffix("Z")
    if "." in t:
        head, frac = t.split(".", 1)
        t = f"{head}.{frac[:6]}"
    return dt.datetime.fromisoformat(t).replace(tzinfo=dt.timezone.utc)


def is_fresh(t: str | None, now: dt.datetime | None = None, max_age: dt.timedelta | None = None) -> bool:
    """True if an Alpaca quote timestamp is within max_age of now."""
    if not t:
        return False
    now = now or dt.datetime.now(dt.timezone.utc)
    return now - parse_ts(t) <= (max_age or MAX_QUOTE_AGE)


def get(base: str, path: str, **params):
    return net.request("GET", base + path, ALLOWED, params=params)


def account() -> dict:
    return get(TRADING, "/v2/account")


def require_paper() -> dict:
    acct = account()
    num = acct.get("account_number", "")
    if not num.startswith("PA"):
        raise SystemExit(f"REFUSED: account {num!r} does not look like a paper account (expected 'PA' prefix)")
    if acct.get("status") != "ACTIVE" or acct.get("trading_blocked") or acct.get("account_blocked"):
        raise SystemExit(f"REFUSED: account not tradable: status={acct.get('status')}")
    return acct


def calendar(start: dt.date, end: dt.date) -> list[dict]:
    return get(TRADING, "/v2/calendar", start=start.isoformat(), end=end.isoformat()) or []


def positions() -> list[dict]:
    return get(TRADING, "/v2/positions") or []


def stock_snapshot(symbol: str) -> dict:
    return get(DATA, "/v2/stocks/snapshots", symbols=symbol, feed=STOCK_FEED).get(symbol) or {}


def spot_and_change(symbol: str) -> tuple[Decimal, Decimal | None]:
    """(last price, % change vs previous close) from the IEX snapshot."""
    s = stock_snapshot(symbol)
    last = (s.get("latestTrade") or {}).get("p") or (s.get("dailyBar") or {}).get("c")
    if not last:
        raise RuntimeError(f"no stock price for {symbol}")
    prev = (s.get("prevDailyBar") or {}).get("c")
    last = Decimal(str(last))
    chg = (last / Decimal(str(prev)) - 1) * 100 if prev else None
    return last, chg


def expiries(underlying: str, on_or_after: dt.date, days: int = 21) -> list[dt.date]:
    """Expiry dates with active contracts in [on_or_after, on_or_after + days]."""
    seen, token = set(), None
    while True:
        page = get(TRADING, "/v2/options/contracts", underlying_symbols=underlying, status="active",
                   expiration_date_gte=on_or_after.isoformat(),
                   expiration_date_lte=(on_or_after + dt.timedelta(days=days)).isoformat(),
                   limit=10000, page_token=token)
        for c in page.get("option_contracts") or []:
            seen.add(dt.date.fromisoformat(c["expiration_date"]))
        token = page.get("next_page_token")
        if not token:
            return sorted(seen)


def tradable_symbols(underlying: str, expiry: dt.date) -> set[str]:
    out, token = set(), None
    while True:
        page = get(TRADING, "/v2/options/contracts", underlying_symbols=underlying, status="active",
                   expiration_date=expiry.isoformat(), limit=10000, page_token=token)
        out |= {c["symbol"] for c in page.get("option_contracts") or [] if c.get("tradable")}
        token = page.get("next_page_token")
        if not token:
            return out


def option_chain(underlying: str, expiry: dt.date) -> list[OptionQuote]:
    """Quoted, tradable contracts for one expiry (indicative feed)."""
    ok = tradable_symbols(underlying, expiry)
    out, token = [], None
    while True:
        page = get(DATA, f"/v1beta1/options/snapshots/{underlying}", feed=OPTION_FEED,
                   expiration_date=expiry.isoformat(), limit=1000, page_token=token)
        for sym, s in (page.get("snapshots") or {}).items():
            q = s.get("latestQuote") or {}
            if sym not in ok or not q.get("ap") or not is_fresh(q.get("t")):
                continue
            _, exp, kind, strike = parse_occ(sym)
            out.append(OptionQuote(sym, kind, strike, exp, Decimal(str(q.get("bp") or 0)),
                                   Decimal(str(q["ap"]))))
        token = page.get("next_page_token")
        if not token:
            return out


def quote(symbol: str) -> tuple[Decimal, Decimal]:
    """(bid, ask) for one option contract. Raises StaleQuote if the quote is too old."""
    q = get(DATA, "/v1beta1/options/quotes/latest", symbols=symbol, feed=OPTION_FEED).get("quotes", {}).get(symbol) or {}
    if not is_fresh(q.get("t")):
        raise StaleQuote(f"{symbol} latest quote is from {q.get('t')}, older than {MAX_QUOTE_AGE}")
    return Decimal(str(q.get("bp") or 0)), Decimal(str(q.get("ap") or 0))


def get_order(order_id: str) -> dict:
    return get(TRADING, f"/v2/orders/{order_id}")


def order_by_cid(cid: str) -> dict | None:
    try:
        return get(TRADING, "/v2/orders:by_client_order_id", client_order_id=cid)
    except net.ApiError as e:
        if e.status == 404:
            return None
        raise


def submit_limit(symbol: str, qty: int, side: str, price: Decimal, cid: str) -> dict:
    body = {"symbol": symbol, "qty": str(qty), "side": side, "type": "limit",
            "limit_price": str(price), "time_in_force": "day", "client_order_id": cid}
    return net.request("POST", TRADING + "/v2/orders", ALLOWED, body=body)


def cancel(order_id: str) -> None:
    try:
        net.request("DELETE", f"{TRADING}/v2/orders/{order_id}", ALLOWED)
    except net.ApiError as e:
        if e.status not in (404, 422):  # already filled / already cancelled
            raise


def limit_and_wait(symbol: str, qty: int, side: str, price: Decimal, cid: str, wait: float,
                   log) -> tuple[int, Decimal | None, dict]:
    """Place a day limit order, wait up to `wait` seconds, cancel the rest.

    Returns (filled qty, average fill price, final order).
    """
    log(f"ORDER {cid}: {side} {qty} {symbol} limit {price}")
    o = submit_limit(symbol, qty, side, price, cid)
    deadline = time.monotonic() + wait
    while o["status"] not in TERMINAL and time.monotonic() < deadline:
        time.sleep(2)
        o = get_order(o["id"])
    if o["status"] not in TERMINAL:
        log(f"{cid}: not filled within {int(wait)}s (filled {o.get('filled_qty')}/{qty}); cancelling")
        cancel(o["id"])
        end = time.monotonic() + 30
        while o["status"] not in TERMINAL and time.monotonic() < end:
            time.sleep(1)
            o = get_order(o["id"])
    q = int(Decimal(str(o.get("filled_qty") or 0)))
    p = Decimal(str(o["filled_avg_price"])) if q and o.get("filled_avg_price") else None
    return q, p, o
