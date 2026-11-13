#!/usr/bin/env python3
"""Paper-trading experiment: same-day XSP options, "claude" arm vs "coin" control.

PAPER ONLY. The script talks to exactly two hosts:
  https://paper-api.alpaca.markets   (trading)
  https://data.alpaca.markets        (market data)
and refuses any other host. It sends no auth headers of its own: this
environment's network proxy adds them. No keys appear in code, files or logs.

Commands
  status                       account, clock, today's calendar, open orders, positions
  buy --direction call|put --reason "..."   9:45 a.m. ET entry for both arms
  check                        order states, half-exit fills, live marks
  close                        3:15 p.m. ET: cancel open orders, sell what's left
  report                       totals per arm from trades.csv

Add --dry-run to any command to make no orders (only GET requests are sent,
and trades.csv is not written).

See RULES.md for the rules.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from zoneinfo import ZoneInfo

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
TRADING = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
ALLOWED_HOSTS = frozenset({"paper-api.alpaca.markets", "data.alpaca.markets"})

UNDERLYING = "XSP"
BUDGET = Decimal("100")          # dollars per trade, fixed
TARGET_ASK = Decimal("0.10")     # pick the strike whose ask is closest to this
MULTIPLIER = 100
FILL_WAIT_SECONDS = 120          # cancel the entry if not filled within 2 minutes
HALF_EXIT_MULT = Decimal("5")    # half-exit limit = 5x fill price
FEED = "indicative"              # "opra" returns 403 on this account (no OPRA agreement)
ARMS = ("claude", "coin")
ET = ZoneInfo("America/New_York")
ENTRY_TIME = dt.time(9, 45)
ENTRY_LATEST = dt.time(10, 15)   # scheduled starts can run late; actual entry time is logged
CLOSE_TIME = dt.time(15, 15)
NORMAL_CLOSE = "16:00"

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "trades.csv")
LOG_PATH = os.path.join(HERE, "trade.log")
CSV_COLUMNS = [
    "date", "arm", "direction", "reason", "symbol", "strike", "contracts",
    "entry_price", "cost", "half_exit_price", "close_price", "proceeds",
    "profit", "notes",
]

DRY_RUN = False
SUMMARY = {"did": [], "fills": [], "errors": []}


def summary(kind: str, text: str) -> None:
    SUMMARY[kind].append(text)


def print_summary() -> None:
    print("\nSUMMARY")
    print("did:    " + ("; ".join(SUMMARY["did"]) or "nothing"))
    print("fills:  " + ("; ".join(SUMMARY["fills"]) or "none"))
    print("errors: " + ("; ".join(SUMMARY["errors"]) or "none"))


# --------------------------------------------------------------------------
# Errors and logging
# --------------------------------------------------------------------------
class AuthStop(Exception):
    """A 401 or 403 came back. The script stops and prints the exact response."""

    def __init__(self, method: str, url: str, status: int, body: str):
        super().__init__(f"HTTP {status} from {method} {url}")
        self.method, self.url, self.status, self.body = method, url, status, body


class OrderRejected(Exception):
    """An order was rejected. Exact response is already logged; stop."""


class ApiError(Exception):
    def __init__(self, method: str, url: str, status: int, body: str):
        super().__init__(f"HTTP {status} from {method} {url}: {body}")
        self.status, self.body = status, body


def now_et() -> dt.datetime:
    return dt.datetime.now(ET)


def log(msg: str) -> None:
    line = f"{now_et().isoformat(timespec='seconds')} {'[dry-run] ' if DRY_RUN else ''}{msg}"
    print(line)
    if not DRY_RUN:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")


# --------------------------------------------------------------------------
# HTTP: host allow-list, no auth headers, no redirects, stop on 401/403
# --------------------------------------------------------------------------
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        raise ApiError(req.get_method(), req.full_url, code,
                       f"redirect to {newurl} refused")


_OPENER = urllib.request.build_opener(_NoRedirect())


def check_host(url: str) -> None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.port not in (None, 443):
        raise SystemExit(f"REFUSED: {url} is not one of the allowed hosts {sorted(ALLOWED_HOSTS)}")


def http(method: str, url: str, params: dict | None = None, body: dict | None = None):
    check_host(url)
    if DRY_RUN and method != "GET":
        raise SystemExit(f"REFUSED in --dry-run: {method} {url}")
    if params:
        url = url + "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json", "User-Agent": "trading-sim/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with _OPENER.open(req, timeout=30) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        if e.code in (401, 403):
            raise AuthStop(method, url, e.code, raw) from None
        raise ApiError(method, url, e.code, raw) from None
    return json.loads(raw) if raw.strip() else None


def get(base: str, path: str, **params):
    return http("GET", base + path, params=params)


# --------------------------------------------------------------------------
# Alpaca calls
# --------------------------------------------------------------------------
def account() -> dict:
    return get(TRADING, "/v2/account")


def clock() -> dict:
    return get(TRADING, "/v2/clock")


def calendar_day(day: dt.date) -> dict | None:
    days = get(TRADING, "/v2/calendar", start=day.isoformat(), end=day.isoformat())
    for d in days or []:
        if d.get("date") == day.isoformat():
            return d
    return None


def next_trading_day(after: dt.date) -> dict | None:
    days = get(TRADING, "/v2/calendar", start=(after + dt.timedelta(days=1)).isoformat(),
               end=(after + dt.timedelta(days=10)).isoformat())
    return days[0] if days else None


def option_contracts(expiry: dt.date, kind: str | None = None) -> list[dict]:
    out, token = [], None
    while True:
        page = get(TRADING, "/v2/options/contracts", underlying_symbols=UNDERLYING,
                   expiration_date=expiry.isoformat(), type=kind, status="active",
                   limit=10000, page_token=token)
        out += page.get("option_contracts") or []
        token = page.get("next_page_token")
        if not token:
            return out


def option_snapshots(expiry: dt.date, kind: str | None = None) -> dict:
    out, token = {}, None
    while True:
        page = get(DATA, f"/v1beta1/options/snapshots/{UNDERLYING}", feed=FEED,
                   expiration_date=expiry.isoformat(), type=kind, limit=1000, page_token=token)
        out.update(page.get("snapshots") or {})
        token = page.get("next_page_token")
        if not token:
            return out


def latest_quotes(symbols: list[str]) -> dict:
    if not symbols:
        return {}
    return get(DATA, "/v1beta1/options/quotes/latest", symbols=",".join(symbols), feed=FEED).get("quotes", {})


def order_by_cid(cid: str) -> dict | None:
    try:
        return get(TRADING, "/v2/orders:by_client_order_id", client_order_id=cid)
    except ApiError as e:
        if e.status == 404:
            return None
        raise


def get_order(order_id: str) -> dict:
    return get(TRADING, f"/v2/orders/{order_id}")


def submit_order(symbol: str, qty: int, side: str, cid: str,
                 limit_price: Decimal | None = None) -> dict:
    body = {"symbol": symbol, "qty": str(qty), "side": side,
            "type": "limit" if limit_price is not None else "market",
            "time_in_force": "day", "client_order_id": cid}
    if limit_price is not None:
        body["limit_price"] = str(limit_price)
    log(f"ORDER {cid}: {side} {qty} {symbol} {body['type']}"
        + (f" @ {limit_price}" if limit_price is not None else ""))
    return http("POST", TRADING + "/v2/orders", body=body)


def cancel_order(order_id: str) -> None:
    try:
        http("DELETE", f"{TRADING}/v2/orders/{order_id}")
    except ApiError as e:
        if e.status not in (404, 422):  # already filled / already cancelled
            raise


def open_tagged_orders() -> list[dict]:
    orders = get(TRADING, "/v2/orders", status="open", limit=500)
    return [o for o in orders if (o.get("client_order_id") or "").startswith(tuple(a + "-" for a in ARMS))]


TERMINAL = {"filled", "canceled", "expired", "rejected", "done_for_day", "replaced"}


def wait_terminal(order_id: str, seconds: float = 30) -> dict:
    deadline = time.monotonic() + seconds
    while True:
        o = get_order(order_id)
        if o["status"] in TERMINAL or time.monotonic() > deadline:
            return o
        time.sleep(1)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def D(x) -> Decimal:
    return Decimal(str(x))


def money(x: Decimal) -> str:
    return str(x.quantize(Decimal("0.01")))


def tick_for(price: Decimal) -> Decimal:
    # XSP quotes in pennies under $3.00; use $0.05 above that.
    return Decimal("0.01") if price < 3 else Decimal("0.05")


def round_up_to_tick(price: Decimal) -> Decimal:
    t = tick_for(price)
    return (price / t).to_integral_value(rounding=ROUND_CEILING) * t


def cid_for(arm: str, day: dt.date, step: str) -> str:
    return f"{arm}-{day.strftime('%Y%m%d')}-{step}"


def contracts_for(ask: Decimal) -> int:
    """floor(100 / (ask x 100)) -- never more than the $100 budget."""
    if ask <= 0:
        return 0
    return int((BUDGET / (ask * MULTIPLIER)).to_integral_value(rounding=ROUND_FLOOR))


def require_paper() -> dict:
    acct = account()
    num = acct.get("account_number", "")
    if not num.startswith("PA"):
        raise SystemExit(f"REFUSED: account {num!r} does not look like a paper account (expected 'PA' prefix)")
    if acct.get("status") != "ACTIVE" or acct.get("trading_blocked") or acct.get("account_blocked"):
        raise SystemExit(f"REFUSED: account not tradable: status={acct.get('status')} "
                         f"trading_blocked={acct.get('trading_blocked')}")
    return acct


def market_check(day: dt.date) -> tuple[bool, str, dict]:
    """(ok, why-not, calendar row). Normal sessions only; early closes are skipped."""
    cal = calendar_day(day)
    if cal is None:
        return False, f"market closed: no session on {day} ({day.strftime('%A')})", {}
    if cal.get("close") != NORMAL_CLOSE:
        return False, f"early close at {cal.get('close')} ET on {day}: rules say do nothing", cal
    return True, "", cal


# --------------------------------------------------------------------------
# trades.csv
# --------------------------------------------------------------------------
def load_rows() -> list[dict]:
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))


def save_rows(rows: list[dict]) -> None:
    if DRY_RUN:
        return
    tmp = CSV_PATH + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_COLUMNS})
    os.replace(tmp, CSV_PATH)


def upsert(rows: list[dict], row: dict) -> None:
    for i, r in enumerate(rows):
        if r["date"] == row["date"] and r["arm"] == row["arm"]:
            rows[i] = {**r, **row}
            return
    rows.append(row)


def add_note(row: dict, note: str) -> None:
    row["notes"] = "; ".join(x for x in [row.get("notes", ""), note] if x)


# --------------------------------------------------------------------------
# Contract selection
# --------------------------------------------------------------------------
def pick_contract(expiry: dt.date, kind: str) -> dict | None:
    tradable = {c["symbol"]: c for c in option_contracts(expiry, kind) if c.get("tradable")}
    snaps = option_snapshots(expiry, kind)
    cands = []
    for sym, s in snaps.items():
        q = s.get("latestQuote") or {}
        if sym not in tradable or not q.get("ap"):
            continue
        ask = D(q["ap"])
        if ask <= 0:
            continue
        strike = D(tradable[sym]["strike_price"])
        otm = strike if kind == "call" else -strike  # larger = further out of the money
        cands.append(((abs(ask - TARGET_ASK), ask, -otm), {
            "symbol": sym, "strike": strike, "ask": ask, "bid": D(q.get("bp") or 0),
            "quote_time": q.get("t"), "candidates": 0}))
    if not cands:
        return None
    cands.sort(key=lambda c: c[0])
    best = cands[0][1]
    best["candidates"] = len(cands)
    return best


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def cmd_status(args) -> None:
    acct = require_paper()
    print(f"Account {acct['account_number']} status={acct['status']} (paper, {TRADING})")
    print(f"  cash={acct['cash']} equity={acct['equity']} buying_power={acct['buying_power']} "
          f"options_level={acct.get('options_trading_level')}")
    c = clock()
    print(f"Clock: now={c['timestamp']} is_open={c['is_open']} next_open={c['next_open']} next_close={c['next_close']}")
    today = now_et().date()
    ok, why, cal = market_check(today)
    print(f"Today {today}: " + (f"normal session {cal['open']}-{cal['close']} ET" if ok else why))
    nxt = next_trading_day(today)
    if nxt:
        print(f"Next trading day: {nxt['date']} {nxt['open']}-{nxt['close']} ET")
    orders = open_tagged_orders()
    print(f"Open tagged orders: {len(orders)}")
    for o in orders:
        print(f"  {o['client_order_id']}: {o['side']} {o['qty']} {o['symbol']} {o['type']} "
              f"limit={o.get('limit_price')} status={o['status']} filled={o['filled_qty']}")
    pos = get(TRADING, "/v2/positions")
    print(f"Positions: {len(pos)}")
    for p in pos:
        print(f"  {p['symbol']} qty={p['qty']} avg={p['avg_entry_price']} mark={p.get('current_price')} "
              f"upl={p.get('unrealized_pl')}")
    rows = [r for r in load_rows() if r["date"] == today.isoformat()]
    for r in rows:
        print(f"  csv {r['arm']}: {r['direction']} {r['symbol']} x{r['contracts']} entry={r['entry_price']} "
              f"notes={r['notes']}")


def cmd_buy(args) -> None:
    require_paper()
    now = now_et()
    today = now.date()
    rows = load_rows()

    def skip_all(why: str) -> None:
        log(f"BUY skipped: {why}")
        summary("did", f"buy skipped: {why}")
        for arm in ARMS:
            upsert(rows, {"date": today.isoformat(), "arm": arm, "notes": why})
        save_rows(rows)

    ok, why, _ = market_check(today)
    if not ok:
        return skip_all(why)
    if not clock()["is_open"]:
        return skip_all("market closed right now (clock.is_open=false)")
    if not (ENTRY_TIME <= now.time() <= ENTRY_LATEST) and not (args.dry_run or args.force_time):
        raise SystemExit(f"Not the entry window ({ENTRY_TIME}-{ENTRY_LATEST} ET); now {now.time():%H:%M}. "
                         "Use --force-time to override.")
    if not args.dry_run:
        for arm in ARMS:
            if order_by_cid(cid_for(arm, today, "buy")):
                raise SystemExit(f"{arm} already has a buy order today ({cid_for(arm, today, 'buy')}); refusing to buy twice.")

    coin = secrets.choice(["call", "put"])
    plan = {
        "claude": (args.direction, args.reason),
        "coin": (coin, "coin flip"),
    }
    log(f"BUY {today} at {now:%H:%M} ET: claude={args.direction} ({args.reason!r}); coin flip={coin}")
    summary("did", f"buy at {now:%H:%M} ET: claude {args.direction}, coin {coin}")

    picks: dict[str, dict] = {}
    cache: dict[str, dict | None] = {}
    for arm in ARMS:
        direction, reason = plan[arm]
        row = {"date": today.isoformat(), "arm": arm, "direction": direction, "reason": reason,
               "notes": f"entry run {now:%H:%M} ET"}
        if direction not in cache:
            cache[direction] = pick_contract(today, direction)
        pick = cache[direction]
        if pick is None:
            add_note(row, f"no quoted same-day {UNDERLYING} {direction}s")
            log(f"{arm}: {row['notes']}")
            upsert(rows, row)
            continue
        qty = contracts_for(pick["ask"])
        row.update(symbol=pick["symbol"], strike=str(pick["strike"]), contracts=str(qty))
        log(f"{arm}: {direction} {pick['symbol']} strike={pick['strike']} bid={pick['bid']} ask={pick['ask']} "
            f"quote_t={pick['quote_time']} (best of {pick['candidates']}) -> {qty} contracts, "
            f"max cost ${money(qty * pick['ask'] * MULTIPLIER)}")
        if qty == 0:
            add_note(row, f"ask {pick['ask']} > $1.00: 0 contracts within $100")
            upsert(rows, row)
            continue
        picks[arm] = {**pick, "qty": qty, "row": row}
        upsert(rows, row)

    if args.dry_run:
        print("\nDRY RUN: would place these orders (none sent):")
        for arm, p in picks.items():
            print(f"  {cid_for(arm, today, 'buy')}: buy {p['qty']} {p['symbol']} limit {p['ask']} day")
            half = p["qty"] // 2
            if half >= 1:
                print(f"    then {cid_for(arm, today, 'half')}: sell {half} {p['symbol']} limit "
                      f"{round_up_to_tick(p['ask'] * HALF_EXIT_MULT)} day (5x fill; uses actual fill price)")
            else:
                print("    then no half-exit (only 1 contract)")
        if len(picks) == 2 and picks["claude"]["symbol"] == picks["coin"]["symbol"]:
            print("  Both arms on the same contract: separate tagged orders, fills split by each arm's quantity.")
        return

    # Place both entries, then wait up to 2 minutes for each.
    placed: dict[str, dict] = {}
    rejected = False
    for arm, p in picks.items():
        if rejected:
            add_note(p["row"], "not placed: stopped after an earlier rejection")
            continue
        try:
            placed[arm] = submit_order(p["symbol"], p["qty"], "buy", cid_for(arm, today, "buy"), p["ask"])
        except ApiError as e:
            # Rules: log the exact rejection and stop. Never switch instruments.
            rejected = True
            add_note(p["row"], f"buy rejected HTTP {e.status}: {e.body}")
            log(f"{arm}: buy REJECTED HTTP {e.status}: {e.body}")
            summary("errors", f"{arm} buy rejected HTTP {e.status}: {e.body}")
    deadline = time.monotonic() + FILL_WAIT_SECONDS
    pending = set(placed)
    while pending and time.monotonic() < deadline:
        time.sleep(2)
        for arm in list(pending):
            placed[arm] = get_order(placed[arm]["id"])
            if placed[arm]["status"] in TERMINAL:
                pending.discard(arm)
    for arm in pending:
        log(f"{arm}: not filled in {FILL_WAIT_SECONDS}s, cancelling")
        cancel_order(placed[arm]["id"])
        placed[arm] = wait_terminal(placed[arm]["id"])

    for arm, o in placed.items():
        row = picks[arm]["row"]
        filled = int(D(o.get("filled_qty") or 0))
        if filled == 0:
            if o["status"] == "rejected":
                rejected = True
                add_note(row, "buy rejected after submit (status rejected)")
                summary("errors", f"{arm} buy order status rejected: {json.dumps(o)}")
            else:
                add_note(row, "no fill")
                summary("fills", f"{arm} no fill")
            row["contracts"] = "0"
            log(f"{arm}: no fill (status {o['status']})")
            continue
        price = D(o["filled_avg_price"])
        row.update(contracts=str(filled), entry_price=str(price), cost=money(filled * price * MULTIPLIER))
        if filled < picks[arm]["qty"]:
            add_note(row, f"partial fill {filled}/{picks[arm]['qty']}, rest cancelled")
        log(f"{arm}: filled {filled} @ {price}, cost ${row['cost']}")
        summary("fills", f"{arm} bought {filled} {o['symbol']} @ {price} (${row['cost']})")
        half = filled // 2
        if half < 1:
            add_note(row, "1 contract: no half-exit")
            continue
        limit = round_up_to_tick(price * HALF_EXIT_MULT)
        try:
            submit_order(o["symbol"], half, "sell", cid_for(arm, today, "half"), limit)
            add_note(row, f"half-exit {half} @ {limit} placed")
        except ApiError as e:
            add_note(row, f"half-exit rejected HTTP {e.status}: {e.body}")
            log(f"{arm}: half-exit REJECTED HTTP {e.status}: {e.body}")
            summary("errors", f"{arm} half-exit rejected HTTP {e.status}: {e.body}")
    save_rows(rows)
    if rejected:
        raise OrderRejected()


def arm_fills(arm: str, day: dt.date) -> dict:
    """Read this arm's buy / half / close orders back from Alpaca."""
    out = {}
    for step in ("buy", "half", "close"):
        o = order_by_cid(cid_for(arm, day, step))
        out[step] = o
    return out


def filled(o: dict | None) -> tuple[int, Decimal | None]:
    if not o:
        return 0, None
    q = int(D(o.get("filled_qty") or 0))
    return q, (D(o["filled_avg_price"]) if q and o.get("filled_avg_price") else None)


def cmd_check(args) -> None:
    require_paper()
    day = dt.date.fromisoformat(args.date) if args.date else now_et().date()
    rows = load_rows()
    todays = [r for r in rows if r["date"] == day.isoformat() and r.get("symbol")]
    if not todays:
        print(f"No trades recorded for {day}.")
        return
    quotes = latest_quotes(sorted({r["symbol"] for r in todays}))
    for r in todays:
        f = arm_fills(r["arm"], day)
        bq, bp = filled(f["buy"])
        hq, hp = filled(f["half"])
        cq, cp = filled(f["close"])
        if hq and hp is not None:
            r["half_exit_price"] = str(hp)
        left = bq - hq - cq
        q = quotes.get(r["symbol"], {})
        mark = D(q.get("bp") or 0)
        print(f"{r['arm']}: {r['direction']} {r['symbol']} bought {bq}@{bp} | half "
              f"{(f['half'] or {}).get('status', '-')} {hq}@{hp} | close {(f['close'] or {}).get('status', '-')} "
              f"{cq}@{cp} | left {left}, bid {mark} ask {q.get('ap')} -> marked value ${money(left * mark * MULTIPLIER)}")
    save_rows(rows)


def cmd_close(args) -> None:
    require_paper()
    now = now_et()
    day = now.date()
    if now.time() < CLOSE_TIME and not (args.dry_run or args.force_time):
        raise SystemExit(f"Too early: close runs at {CLOSE_TIME} ET; now {now.time():%H:%M}. Use --force-time to override.")
    rows = load_rows()

    # 1. Cancel every open tagged order.
    for o in open_tagged_orders():
        log(f"cancel {o['client_order_id']} ({o['side']} {o['qty']} {o['symbol']} status {o['status']})")
        summary("did", f"cancel {o['client_order_id']}")
        if not args.dry_run:
            cancel_order(o["id"])
            wait_terminal(o["id"])

    # 2. Sell what each arm still holds, using each arm's own quantity.
    todays = [r for r in rows if r["date"] == day.isoformat() and r.get("symbol")]
    if not todays:
        summary("did", f"close: no trades recorded for {day}")
    for r in todays:
        arm = r["arm"]
        f = arm_fills(arm, day)
        bq, bp = filled(f["buy"])
        hq, hp = filled(f["half"])
        cq, _ = filled(f["close"])
        if hq and hp is not None:
            r["half_exit_price"] = str(hp)
        left = bq - hq - cq
        if bq == 0:
            continue
        if left > 0:
            if args.dry_run:
                print(f"DRY RUN: would sell {left} {r['symbol']} at market ({cid_for(arm, day, 'close')})")
                continue
            try:
                o = submit_order(r["symbol"], left, "sell", cid_for(arm, day, "close"))
                o = wait_terminal(o["id"], 60)
                if o["status"] != "filled":
                    add_note(r, f"close order {o['status']}, filled {o.get('filled_qty')}/{left}")
                    summary("errors", f"{arm} close order {o['status']}, filled {o.get('filled_qty')}/{left}")
            except ApiError as e:
                add_note(r, f"close rejected HTTP {e.status}: {e.body}")
                log(f"{arm}: close REJECTED HTTP {e.status}: {e.body}")
                summary("errors", f"{arm} close rejected HTTP {e.status}: {e.body}")
        f = arm_fills(arm, day)
        cq, cp = filled(f["close"])
        if cp is not None:
            r["close_price"] = str(cp)
        proceeds = (hq * (hp or 0) + cq * (cp or 0)) * MULTIPLIER
        r["proceeds"] = money(D(proceeds))
        if r.get("cost"):
            r["profit"] = money(D(proceeds) - D(r["cost"]))
        still = bq - hq - cq
        if still > 0:
            add_note(r, f"WARNING {still} contracts still open after close")
            summary("errors", f"{arm}: {still} contracts still open after close")
        summary("did", f"{arm} close: sold {cq} @ {cp}, half-exit {hq} @ {hp}")
        summary("fills", f"{arm} proceeds ${r['proceeds']} profit ${r.get('profit')}")
        log(f"{arm}: half {hq}@{hp} close {cq}@{cp} proceeds ${r['proceeds']} profit ${r.get('profit')}")
    save_rows(rows)


def cmd_report(args) -> None:
    rows = load_rows()
    if not rows:
        print("trades.csv is empty.")
        return
    print(f"{'arm':8}{'days':>6}{'filled':>8}{'no-fill':>9}{'cost':>11}{'proceeds':>11}{'profit':>11}{'wins':>6}")
    for arm in ARMS:
        rs = [r for r in rows if r["arm"] == arm]
        traded = [r for r in rs if r.get("cost")]
        nofill = [r for r in rs if "no fill" in (r.get("notes") or "")]
        cost = sum(D(r["cost"]) for r in traded)
        proc = sum(D(r["proceeds"]) for r in traded if r.get("proceeds"))
        prof = sum(D(r["profit"]) for r in traded if r.get("profit"))
        wins = sum(1 for r in traded if r.get("profit") and D(r["profit"]) > 0)
        print(f"{arm:8}{len(rs):>6}{len(traded):>8}{len(nofill):>9}{money(D(cost)):>11}"
              f"{money(D(proc)):>11}{money(D(prof)):>11}{wins:>6}")
    open_rows = [r for r in rows if r.get("cost") and not r.get("profit")]
    if open_rows:
        print(f"\n{len(open_rows)} trade(s) without a close yet: "
              + ", ".join(f"{r['date']} {r['arm']}" for r in open_rows))


def main(argv=None) -> int:
    global DRY_RUN
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dry-run", action="store_true", help="make no orders and write no files")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    b = sub.add_parser("buy")
    b.add_argument("--direction", required=True, choices=["call", "put"], help="claude arm's direction")
    b.add_argument("--reason", required=True, help="one-line reason for the claude direction")
    b.add_argument("--force-time", action="store_true", help="allow buying outside 9:45-10:00 ET")
    c = sub.add_parser("check")
    c.add_argument("--date", help="YYYY-MM-DD (default today ET)")
    cl = sub.add_parser("close")
    cl.add_argument("--force-time", action="store_true", help="allow closing before 3:15 ET")
    sub.add_parser("report")
    for sp in sub.choices.values():  # accept --dry-run after the command too
        sp.add_argument("--dry-run", action="store_true", default=argparse.SUPPRESS)
    args = p.parse_args(argv)
    DRY_RUN = bool(getattr(args, "dry_run", False))
    if args.cmd == "buy" and "\n" in args.reason:
        p.error("--reason must be one line")
    try:
        {"status": cmd_status, "buy": cmd_buy, "check": cmd_check,
         "close": cmd_close, "report": cmd_report}[args.cmd](args)
    except AuthStop as e:
        msg = f"STOP: HTTP {e.status} from {e.method} {e.url}\n{e.body}"
        print(msg, file=sys.stderr)
        summary("errors", msg.replace("\n", " "))
        code = 2
    except OrderRejected:
        print("STOP: order rejected (exact response logged above). Not switching instruments.", file=sys.stderr)
        code = 3
    else:
        code = 0
    if args.cmd in ("buy", "close"):
        print_summary()
    return code


if __name__ == "__main__":
    sys.exit(main())
