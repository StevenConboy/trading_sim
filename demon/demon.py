#!/usr/bin/env python3
"""Shannon's Demon paper test: weekly-rebalanced leveraged ETF / T-bill sleeves
against buy-and-hold of the same ETFs.

PAPER ONLY. The script talks to exactly two hosts:
  https://paper-api.alpaca.markets   (trading)
  https://data.alpaca.markets        (market data, corporate actions)
and refuses any other host. It sends no auth headers of its own: this
environment's network proxy adds them. No keys appear in code, files or logs.

Commands
  status        safety check, account, sleeves, broker vs ledger
  rebalance     weekly rebalance (first trading day of the week, 10:00 a.m. ET)
  snapshot      daily snapshot after the close (about 4:15 p.m. ET)
  summary       rewrite the latest weekly summary from the files

Add --dry-run to make no orders and write no files (only GET requests).

Exit codes: 0 ok or nothing to do, 1 error, 2 STOP (safety check failed or
401/403), 3 order rejected or not fully filled, 4 orders already exist for
today without a saved plan (nothing placed; see the message).

See RULES.md for the rules.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import ROUND_DOWN, Decimal
from zoneinfo import ZoneInfo

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
TRADING = "https://paper-api.alpaca.markets"
DATA = "https://data.alpaca.markets"
ALLOWED_HOSTS = frozenset({"paper-api.alpaca.markets", "data.alpaca.markets"})
FEED = "iex"  # "sip" returns 403 on this account

ET = ZoneInfo("America/New_York")
REBALANCE_TIME = dt.time(10, 0)
REBALANCE_EARLY_WAIT = dt.timedelta(minutes=20)  # a start this early sleeps until 10:00
REBALANCE_CUTOFF = dt.timedelta(minutes=15)       # no new rebalance this close to the close

MIN_TRADE = Decimal("200")     # skip any single sleeve trade under $200
MIN_ORDER = Decimal("1")       # Alpaca's fractional minimum; smaller nets are crossed internally
BUY_BUFFER = Decimal("0.995")  # size buys at 99.5% so a price move can't overspend cash
QTY_STEP = Decimal("0.000001")
CASH_STEP = Decimal("0.000001")
FILL_TIMEOUT = 300             # seconds to wait for a market order to fill

SYMBOLS = ("YINN", "SOXL", "LABU", "NAIL", "TMF", "SGOV")
SLEEVES = {
    "A": {"kind": "real", "weights": {"YINN": "0.5", "SGOV": "0.5"}},
    "B": {"kind": "virtual", "mirror": "A", "weights": {"YINN": "1"}},
    "C": {"kind": "real", "weights": {"SOXL": "0.5", "SGOV": "0.5"}},
    "D": {"kind": "virtual", "mirror": "C", "weights": {"SOXL": "1"}},
    "E": {"kind": "real", "weights": {"YINN": "0.125", "LABU": "0.125", "NAIL": "0.125",
                                      "TMF": "0.125", "SGOV": "0.5"}},
    "F": {"kind": "virtual", "mirror": "E", "weights": {"YINN": "0.25", "LABU": "0.25",
                                                        "NAIL": "0.25", "TMF": "0.25"}},
}
REAL = ("A", "C", "E")
VIRTUAL = ("B", "D", "F")
PAIRS = (("A", "B"), ("C", "D"), ("E", "F"))

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(HERE, "ledger.json")
TRADES_PATH = os.path.join(HERE, "trades.csv")
EQUITY_PATH = os.path.join(HERE, "equity.csv")
SUMMARY_DIR = os.path.join(HERE, "summaries")
LOG_PATH = os.path.join(HERE, "demon.log")
TRADES_COLUMNS = ["timestamp", "sleeve", "symbol", "side", "quantity", "fill_price", "reason"]
EQUITY_COLUMNS = ["date", "time_et", "A", "B", "C", "D", "E", "F",
                  "broker_equity", "ledger_real_total", "note"]

DRY_RUN = False
SUMMARY = {"did": [], "fills": [], "errors": []}


class Stop(Exception):
    """Safety check failed, or a 401/403 came back. Nothing more is done."""


class NeedsAttention(Exception):
    """Orders exist for today but the saved plan is gone. Nothing is placed."""


class ApiError(Exception):
    def __init__(self, method: str, url: str, status: int, body: str):
        super().__init__(f"HTTP {status} from {method} {url}: {body}")
        self.status, self.body = status, body


def D(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def q_qty(x: Decimal) -> Decimal:
    return x.quantize(QTY_STEP, rounding=ROUND_DOWN)


def q_cash(x: Decimal) -> Decimal:
    return x.quantize(CASH_STEP)


def money(x) -> str:
    return f"${D(x):,.2f}"


def now_et() -> dt.datetime:
    return dt.datetime.now(ET)


def log(msg: str) -> None:
    line = f"{now_et().isoformat(timespec='seconds')} {'[dry-run] ' if DRY_RUN else ''}{msg}"
    print(line, flush=True)
    if not DRY_RUN:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")


def note(kind: str, text: str) -> None:
    SUMMARY[kind].append(text)


# --------------------------------------------------------------------------
# HTTP: host allow-list, no auth headers, no redirects, stop on 401/403
# --------------------------------------------------------------------------
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        raise ApiError(req.get_method(), req.full_url, code, f"redirect to {newurl} refused")


_OPENER = urllib.request.build_opener(_NoRedirect())


def check_host(url: str) -> None:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in ALLOWED_HOSTS or parts.port not in (None, 443):
        raise Stop(f"{url} is not one of the allowed hosts {sorted(ALLOWED_HOSTS)}")


def is_order_rejection(method: str, url: str, raw: str) -> bool:
    """Alpaca answers 403 with a numeric "code" when it rejects an order (for
    example not enough buying power). That is a rejection, not an auth failure."""
    if method != "POST" or urllib.parse.urlsplit(url).path != "/v2/orders":
        return False
    try:
        return isinstance(json.loads(raw).get("code"), int)
    except (ValueError, AttributeError):
        return False


def http(method: str, url: str, params: dict | None = None, body: dict | None = None):
    check_host(url)
    if DRY_RUN and method != "GET":
        raise Stop(f"refused in --dry-run: {method} {url}")
    if params:
        url = url + "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Accept": "application/json", "User-Agent": "trading-sim-demon/1.0"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    last = None
    for attempt in range(3):  # network errors and 5xx only; never for order POSTs
        try:
            with _OPENER.open(req, timeout=30) as resp:
                raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else None
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            if e.code == 403 and is_order_rejection(method, url, raw):
                raise ApiError(method, url, e.code, raw) from None
            if e.code in (401, 403):
                raise Stop(f"HTTP {e.code} from {method} {url}: {raw}") from None
            if e.code < 500 or method == "POST":
                raise ApiError(method, url, e.code, raw) from None
            last = ApiError(method, url, e.code, raw)
        except (urllib.error.URLError, TimeoutError) as e:
            if method == "POST":
                raise
            last = e
        time.sleep(2 * (attempt + 1))
    raise last  # type: ignore[misc]


def get(base: str, path: str, **params):
    return http("GET", base + path, params=params)


# --------------------------------------------------------------------------
# Alpaca calls
# --------------------------------------------------------------------------
def account() -> dict:
    return get(TRADING, "/v2/account")


def clock() -> dict:
    return get(TRADING, "/v2/clock")


def calendar(start: dt.date, end: dt.date) -> list[dict]:
    return get(TRADING, "/v2/calendar", start=start.isoformat(), end=end.isoformat()) or []


def positions() -> dict[str, dict]:
    return {p["symbol"]: p for p in get(TRADING, "/v2/positions") or []}


def open_orders() -> list[dict]:
    return get(TRADING, "/v2/orders", status="open", limit=500) or []


def orders_since(day: dt.date) -> list[dict]:
    after = dt.datetime.combine(day, dt.time(0, 0), ET).astimezone(dt.timezone.utc)
    return get(TRADING, "/v2/orders", status="all", after=after.isoformat().replace("+00:00", "Z"),
               limit=500, direction="asc") or []


def order_by_coid(coid: str) -> dict | None:
    try:
        return get(TRADING, "/v2/orders:by_client_order_id", client_order_id=coid)
    except ApiError as e:
        if e.status == 404:
            return None
        raise


def get_order(order_id: str) -> dict:
    return get(TRADING, f"/v2/orders/{order_id}")


def latest_prices() -> dict[str, Decimal]:
    """Alpaca's position price for held symbols (what broker equity uses),
    else the latest IEX trade."""
    snap = get(DATA, "/v2/stocks/snapshots", symbols=",".join(SYMBOLS), feed=FEED) or {}
    prices = {s: D(snap[s]["latestTrade"]["p"]) for s in SYMBOLS if snap.get(s, {}).get("latestTrade")}
    for s, p in positions().items():
        if s in SYMBOLS and p.get("current_price"):
            prices[s] = D(p["current_price"])
    missing = [s for s in SYMBOLS if s not in prices or prices[s] <= 0]
    if missing:
        raise RuntimeError(f"no price for {missing}")
    return prices


def activities_since(day: dt.date) -> list[dict]:
    """Non-trade activities (distributions, fees, cash in lieu, splits)."""
    out, token = [], None
    while True:
        page = get(TRADING, "/v2/account/activities",
                   activity_types="DIV,DIVCGL,DIVCGS,DIVFEE,DIVFT,DIVNRA,DIVROC,DIVTW,DIVTXEX,CIL",
                   after=day.isoformat(), direction="asc", page_size=100, page_token=token) or []
        out.extend(page)
        if len(page) < 100:
            return out
        token = page[-1]["id"]


def corporate_actions(start: dt.date, end: dt.date) -> list[dict]:
    res = get(DATA, "/v1/corporate-actions", symbols=",".join(SYMBOLS),
              types="forward_split,reverse_split,cash_dividend",
              start=start.isoformat(), end=end.isoformat(), limit=1000) or {}
    out = []
    for kind, items in (res.get("corporate_actions") or {}).items():
        for it in items:
            out.append({**it, "kind": kind})
    return out


# --------------------------------------------------------------------------
# Safety check
# --------------------------------------------------------------------------
def preflight() -> dict:
    """Stop unless everything points at a paper account that is safe to use."""
    if urllib.parse.urlsplit(TRADING).hostname != "paper-api.alpaca.markets":
        raise Stop(f"trading base URL is {TRADING}, not the paper endpoint")
    acct = account()
    problems = []
    if not str(acct.get("account_number", "")).startswith("PA"):
        problems.append("account number does not look like a paper account (expected PA...)")
    if acct.get("status") != "ACTIVE":
        problems.append(f"account status is {acct.get('status')}")
    if acct.get("account_blocked") or acct.get("trading_blocked"):
        problems.append("account or trading is blocked")
    if acct.get("currency") != "USD":
        problems.append(f"currency is {acct.get('currency')}")
    if D(acct.get("cash", "0")) < 0:
        problems.append(f"cash is negative ({acct.get('cash')}): margin is in use")
    others = [s for s in positions() if s not in SYMBOLS]
    if others:
        problems.append(f"account holds symbols outside this test: {others}")
    for p in positions().values():
        if D(p["qty"]) < 0:
            problems.append(f"short position in {p['symbol']}")
    if problems:
        raise Stop("; ".join(problems))
    return acct


# --------------------------------------------------------------------------
# Ledger
# --------------------------------------------------------------------------
def empty_ledger() -> dict:
    return {
        "version": 1,
        "started": None,
        "start_values": {},
        "sleeves": {s: {"cash": "0", "shares": {}} for s in SLEEVES},
        "rebalances": [],
        "processed_activities": [],
        "processed_corporate_actions": [],
        "pending": None,
        "events": [],
    }


def load_ledger() -> dict | None:
    if not os.path.exists(LEDGER_PATH):
        return None
    with open(LEDGER_PATH) as f:
        return json.load(f)


def save_ledger(ledger: dict) -> None:
    if DRY_RUN:
        return
    tmp = LEDGER_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(ledger, f, indent=1, sort_keys=False)
        f.write("\n")
    os.replace(tmp, LEDGER_PATH)


def event(ledger: dict, kind: str, detail: str) -> None:
    ledger["events"].append({"ts": now_et().isoformat(timespec="seconds"), "type": kind, "detail": detail})
    log(f"ledger {kind}: {detail}")


def shares(ledger: dict, sleeve: str, sym: str) -> Decimal:
    return D(ledger["sleeves"][sleeve]["shares"].get(sym, "0"))


def set_shares(ledger: dict, sleeve: str, sym: str, qty: Decimal) -> None:
    ledger["sleeves"][sleeve]["shares"][sym] = str(qty)


def cash(ledger: dict, sleeve: str) -> Decimal:
    return D(ledger["sleeves"][sleeve]["cash"])


def set_cash(ledger: dict, sleeve: str, amount: Decimal) -> None:
    ledger["sleeves"][sleeve]["cash"] = str(q_cash(amount))


def sleeve_value(ledger: dict, sleeve: str, prices: dict[str, Decimal]) -> Decimal:
    return cash(ledger, sleeve) + sum((shares(ledger, sleeve, s) * prices[s]
                                       for s in ledger["sleeves"][sleeve]["shares"]), Decimal(0))


def real_total_shares(ledger: dict, sym: str) -> Decimal:
    return sum((shares(ledger, s, sym) for s in REAL), Decimal(0))


def holders(ledger: dict, sym: str, group=REAL) -> list[str]:
    return [s for s in group if shares(ledger, s, sym) > 0]


# --------------------------------------------------------------------------
# Distributions, splits, reconciliation
# --------------------------------------------------------------------------
def process_activities(ledger: dict) -> None:
    """Broker cash from distributions (and cash in lieu): split among the real
    sleeves holding that symbol, by share count."""
    seen = set(ledger["processed_activities"])
    for a in activities_since(dt.date.fromisoformat(ledger["started"]) - dt.timedelta(days=1)):
        if a["id"] in seen:
            continue
        sym, amount = a.get("symbol"), D(a.get("net_amount", "0"))
        who = holders(ledger, sym) if sym in SYMBOLS else []
        if not who or amount == 0:
            event(ledger, "activity_unallocated",
                  f"{a.get('activity_type')} {sym} {amount} on {a.get('date')}: no sleeve holds it; "
                  "left for cash reconciliation")
        else:
            total = sum((shares(ledger, s, sym) for s in who), Decimal(0))
            parts = []
            for s in who:
                part = amount * shares(ledger, s, sym) / total
                set_cash(ledger, s, cash(ledger, s) + part)
                parts.append(f"{s} {part:.2f}")
            event(ledger, "distribution",
                  f"{a.get('activity_type')} {sym} {money(amount)} on {a.get('date')} -> " + ", ".join(parts))
        ledger["processed_activities"].append(a["id"])


def process_corporate_actions(ledger: dict) -> None:
    """Virtual sleeves only: splits change share counts; cash dividends are
    credited at rate x shares once the payable date has passed. Real sleeves
    get splits from broker reconciliation and distributions from activities."""
    start = dt.date.fromisoformat(ledger["started"])
    today = now_et().date()
    seen = set(ledger["processed_corporate_actions"])
    actions = sorted(corporate_actions(start, today + dt.timedelta(days=1)), key=lambda a: a.get("ex_date", ""))
    for a in actions:
        if a["id"] in seen or a.get("symbol") not in SYMBOLS:
            continue
        ex = dt.date.fromisoformat(a["ex_date"])
        if ex <= start:  # the virtual sleeves were bought after this ex-date
            ledger["processed_corporate_actions"].append(a["id"])
            continue
        sym = a["symbol"]
        if a["kind"] in ("forward_splits", "reverse_splits"):
            if ex > today:
                continue
            ratio = D(a["new_rate"]) / D(a["old_rate"])
            for s in VIRTUAL:
                old = shares(ledger, s, sym)
                if old > 0:
                    set_shares(ledger, s, sym, (old * ratio).quantize(Decimal("0.000000001")))
                    event(ledger, "split_virtual", f"{s} {sym} {a['old_rate']}->{a['new_rate']} "
                                                   f"ex {a['ex_date']}: {old} -> {old * ratio}")
        elif a["kind"] == "cash_dividends":
            pay = dt.date.fromisoformat(a.get("payable_date") or a["ex_date"])
            if pay > today:
                continue
            for s in VIRTUAL:
                qty = shares(ledger, s, sym)
                if qty > 0:
                    amt = qty * D(a["rate"])
                    set_cash(ledger, s, cash(ledger, s) + amt)
                    event(ledger, "distribution_virtual",
                          f"{s} {sym} {a['rate']}/share x {qty} = {money(amt)} (ex {a['ex_date']}, paid {pay})")
        ledger["processed_corporate_actions"].append(a["id"])


def reconcile(ledger: dict, acct: dict) -> list[str]:
    """Make the real sleeves add up to the broker. Shares: scale each sleeve's
    holding by broker/ledger (this is exactly a split ratio after a split).
    Cash: spread any difference (fees, unallocated cash) by sleeve value."""
    changes = []
    pos = positions()
    for sym in SYMBOLS:
        broker = D(pos[sym]["qty"]) if sym in pos else Decimal(0)
        mine = real_total_shares(ledger, sym)
        if abs(broker - mine) <= Decimal("0.000002"):
            continue
        targeting = [s for s in REAL if sym in SLEEVES[s]["weights"]]
        if mine > 0:
            for s in REAL:
                old = shares(ledger, s, sym)
                if old > 0:
                    set_shares(ledger, s, sym, q_qty(broker * old / mine) if broker > 0 else Decimal(0))
        elif broker > 0 and targeting:
            for s in targeting:
                set_shares(ledger, s, sym, q_qty(broker / len(targeting)))
        # put any rounding residue on the largest holder
        residue = broker - real_total_shares(ledger, sym)
        if residue != 0 and (holders(ledger, sym) or targeting):
            big = max(holders(ledger, sym) or targeting, key=lambda s: shares(ledger, s, sym))
            set_shares(ledger, big, sym, shares(ledger, big, sym) + residue)
        changes.append(f"{sym}: ledger {mine} -> broker {broker}")
    broker_cash = D(acct["cash"])
    ledger_cash = sum((cash(ledger, s) for s in REAL), Decimal(0))
    diff = broker_cash - ledger_cash
    if abs(diff) >= Decimal("0.005"):
        prices = latest_prices()
        vals = {s: max(sleeve_value(ledger, s, prices), Decimal(0)) for s in REAL}
        tot = sum(vals.values(), Decimal(0)) or Decimal(1)
        for s in REAL:
            set_cash(ledger, s, cash(ledger, s) + diff * vals[s] / tot)
        changes.append(f"cash: ledger {money(ledger_cash)} -> broker {money(broker_cash)} "
                       f"(diff {diff:+.4f} spread by sleeve value)")
    elif diff != 0:
        set_cash(ledger, "A", cash(ledger, "A") + diff)  # sub-cent rounding
    for c in changes:
        event(ledger, "reconcile", c)
    return changes


# --------------------------------------------------------------------------
# CSV files
# --------------------------------------------------------------------------
def append_trades(rows: list[dict]) -> None:
    if DRY_RUN or not rows:
        return
    new = not os.path.exists(TRADES_PATH)
    with open(TRADES_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=TRADES_COLUMNS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerows(rows)


def read_equity() -> list[dict]:
    if not os.path.exists(EQUITY_PATH):
        return []
    with open(EQUITY_PATH, newline="") as f:
        return list(csv.DictReader(f))


def write_equity_row(row: dict) -> None:
    rows = [r for r in read_equity() if r["date"] != row["date"]] + [row]
    rows.sort(key=lambda r: r["date"])
    if DRY_RUN:
        return
    with open(EQUITY_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=EQUITY_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------------------------
# Orders
# --------------------------------------------------------------------------
def submit_or_find(coid: str, sym: str, side: str, qty: Decimal) -> dict:
    """Never sends the same order twice: an order with this client_order_id
    on Alpaca is reused instead."""
    existing = order_by_coid(coid)
    if existing:
        log(f"order {coid} already exists ({existing['status']}); not sending again")
        return existing
    body = {"symbol": sym, "qty": str(qty), "side": side, "type": "market",
            "time_in_force": "day", "extended_hours": False, "client_order_id": coid}
    try:
        o = http("POST", TRADING + "/v2/orders", body=body)
        log(f"sent {coid}: {side} {qty} {sym} market day -> {o['status']}")
        return o
    except ApiError as e:
        if e.status == 422 and "client_order_id" in e.body:
            existing = order_by_coid(coid)
            if existing:
                return existing
        log(f"REJECTED {coid}: HTTP {e.status} {e.body}")
        return {"id": None, "status": "rejected", "filled_qty": "0", "filled_avg_price": None,
                "reject": f"HTTP {e.status} {e.body}"}


def wait_fill(o: dict) -> dict:
    if not o.get("id"):
        return o
    deadline = time.time() + FILL_TIMEOUT
    terminal = {"filled", "canceled", "expired", "rejected", "done_for_day"}
    while o["status"] not in terminal and time.time() < deadline:
        time.sleep(2)
        o = get_order(o["id"])
    if o["status"] not in terminal:
        log(f"order {o['client_order_id']} still {o['status']} after {FILL_TIMEOUT}s; cancelling the rest")
        try:
            http("DELETE", f"{TRADING}/v2/orders/{o['id']}")
        except ApiError as e:
            log(f"cancel failed: {e}")
        for _ in range(30):
            time.sleep(2)
            o = get_order(o["id"])
            if o["status"] in terminal:
                break
    return o


# --------------------------------------------------------------------------
# Rebalance planning
# --------------------------------------------------------------------------
def plan_deltas(ledger: dict, prices: dict[str, Decimal]) -> dict[str, dict[str, Decimal]]:
    """Per sleeve, per symbol: signed share change to reach target weights.
    Trades under $200 are dropped. Buys are sized at 99.5% so the sleeve keeps
    a little cash for price moves; sells never exceed what the sleeve holds."""
    out: dict[str, dict[str, Decimal]] = {}
    for s in REAL:
        value = sleeve_value(ledger, s, prices)
        out[s] = {}
        for sym, w in SLEEVES[s]["weights"].items():
            have = shares(ledger, s, sym)
            delta_usd = value * D(w) - have * prices[sym]
            if abs(delta_usd) < MIN_TRADE:
                if delta_usd != 0:
                    log(f"plan {s} {sym}: {money(delta_usd)} is under {money(MIN_TRADE)}, skipped")
                continue
            if delta_usd > 0:
                qty = q_qty(delta_usd * BUY_BUFFER / prices[sym])
            else:
                qty = -min(q_qty(-delta_usd / prices[sym]), have)
            if qty != 0:
                out[s][sym] = qty
    return out


def fit_buys_to_cash(ledger: dict, deltas: dict, prices: dict[str, Decimal], phase_syms: list[str]) -> None:
    """Scale a sleeve's buys in phase_syms down if its cash (after its sells)
    would not cover them at 0.5% above the latest price."""
    for s in REAL:
        need = sum((deltas[s][sym] * prices[sym] * Decimal("1.005")
                    for sym in phase_syms if deltas[s].get(sym, 0) > 0), Decimal(0))
        have = cash(ledger, s) - sum((-deltas[s][sym] * prices[sym]
                                      for sym in phase_syms if deltas[s].get(sym, 0) < 0), Decimal(0))
        if need > 0 and need > have:
            f = max(have, Decimal(0)) / need
            for sym in phase_syms:
                if deltas[s].get(sym, 0) > 0:
                    deltas[s][sym] = q_qty(deltas[s][sym] * f)
            log(f"{s}: buys scaled to {f:.4f} to fit cash {money(have)}")


def make_orders(date_tag: str, phase: str, deltas: dict, syms: list[str], prices: dict) -> list[dict]:
    orders = []
    for sym in syms:
        alloc = {s: str(deltas[s][sym]) for s in REAL if deltas[s].get(sym, 0) != 0}
        if not alloc:
            continue
        net = sum((D(v) for v in alloc.values()), Decimal(0))
        side = "buy" if net > 0 else "sell"
        cross = abs(net) * prices[sym] < MIN_ORDER
        if cross and net != 0:
            # Too small to send: trim the largest sleeve's part so the sleeves
            # trade only with each other and the broker position is unchanged.
            big = max(alloc, key=lambda s: abs(D(alloc[s])))
            alloc[big] = str(D(alloc[big]) - net)
            alloc = {s: v for s, v in alloc.items() if D(v) != 0}
            net = Decimal(0)
            if not alloc:
                continue
        orders.append({
            "coid": f"demon-{date_tag}-{phase}-{sym}-{side}",
            "symbol": sym, "side": side, "qty": str(abs(net)), "alloc": alloc,
            "ref_price": str(prices[sym]), "internal": cross,
            "status": "planned", "filled_qty": None, "fill_price": None,
        })
    return orders


def apply_fill(ledger: dict, o: dict, filled: Decimal, price: Decimal, reason: str) -> list[dict]:
    """Book each sleeve's share of a net order at the order's fill price.
    A partial fill scales every sleeve's part by the same fraction, so the
    sleeves still add up to the broker."""
    qty = D(o["qty"])
    frac = Decimal(1) if o["internal"] or qty == 0 else filled / qty
    ts = now_et().isoformat(timespec="seconds")
    rows = []
    for s, d in o["alloc"].items():
        part = q_qty(abs(D(d)) * frac)
        if part == 0:
            continue
        sign = 1 if D(d) > 0 else -1
        set_shares(ledger, s, o["symbol"], shares(ledger, s, o["symbol"]) + sign * part)
        set_cash(ledger, s, cash(ledger, s) - sign * part * price)
        rows.append({"timestamp": ts, "sleeve": s, "symbol": o["symbol"],
                     "side": "buy" if sign > 0 else "sell", "quantity": str(part),
                     "fill_price": str(price), "reason": reason})
    # rounding residue from scaling goes to the largest part so sleeves sum to the fill
    if not o["internal"] and o["alloc"]:
        booked = sum((D(r["quantity"]) * (1 if r["side"] == "buy" else -1) for r in rows), Decimal(0))
        net_signed = filled if o["side"] == "buy" else -filled
        residue = net_signed - booked
        if residue != 0:
            big = max(o["alloc"], key=lambda s: abs(D(o["alloc"][s])))
            set_shares(ledger, big, o["symbol"], shares(ledger, big, o["symbol"]) + residue)
            set_cash(ledger, big, cash(ledger, big) - residue * price)
    return rows


def execute_phase(ledger: dict, orders: list[dict], first: bool) -> None:
    """Send each order (skipping internal crosses), wait for the fill, book it."""
    for o in orders:
        if o["status"] in ("booked",):
            continue
        reason = "initial buy" if first else "weekly rebalance"
        if o["internal"]:
            price = D(o["ref_price"])
            rows = apply_fill(ledger, o, D(o["qty"]), price,
                              f"{reason}; netted between sleeves, no order (latest price)")
            o.update(status="booked", filled_qty="0", fill_price=str(price))
            append_trades(rows)
            save_ledger(ledger)
            note("fills", f"{o['symbol']} netted internally")
            continue
        if DRY_RUN:
            log(f"would send {o['coid']}: {o['side']} {o['qty']} {o['symbol']} "
                f"(alloc {o['alloc']}, ref {o['ref_price']})")
            continue
        if o["side"] == "sell" and o["status"] == "planned":  # never sell more than the broker holds
            held = D(positions().get(o["symbol"], {}).get("qty", "0"))
            if D(o["qty"]) > held:
                log(f"{o['coid']}: sell {o['qty']} capped at held {held}")
                o["qty"] = str(q_qty(held))
        o["status"] = "sent"
        save_ledger(ledger)
        res = wait_fill(submit_or_find(o["coid"], o["symbol"], o["side"], D(o["qty"])))
        filled = D(res.get("filled_qty") or "0")
        price = D(res["filled_avg_price"]) if res.get("filled_avg_price") else D(o["ref_price"])
        if filled < D(o["qty"]):
            msg = (f"{o['coid']} {res['status']}: filled {filled} of {o['qty']}"
                   + (f" ({res['reject']})" if res.get("reject") else ""))
            note("errors", msg)
            log(msg)
        rows = apply_fill(ledger, o, filled, price, f"{reason}; net order {o['coid']}") if filled > 0 else []
        o.update(status="booked", filled_qty=str(filled), fill_price=str(price), order_status=res["status"])
        append_trades(rows)
        save_ledger(ledger)
        note("fills", f"{o['side']} {filled} {o['symbol']} @ {price}")


def seed_virtual(ledger: dict) -> None:
    """B, D, F get the same dollars as A, C, E at their first fill prices."""
    fills: dict[str, Decimal] = {}
    for phase in ("p1", "p2"):
        for o in ledger["pending"].get(phase) or []:
            if o.get("fill_price") and not o["internal"]:
                fills[o["symbol"]] = D(o["fill_price"])
            elif o.get("fill_price"):
                fills.setdefault(o["symbol"], D(o["fill_price"]))
    ts = now_et().isoformat(timespec="seconds")
    rows = []
    for v in VIRTUAL:
        start = D(ledger["start_values"][SLEEVES[v]["mirror"]])
        for sym, w in SLEEVES[v]["weights"].items():
            if sym not in fills:
                raise RuntimeError(f"no first fill price for {sym}; cannot seed {v}")
            qty = (start * D(w) / fills[sym]).quantize(Decimal("0.000000001"))
            set_shares(ledger, v, sym, qty)
            rows.append({"timestamp": ts, "sleeve": v, "symbol": sym, "side": "buy",
                         "quantity": f"{qty:.6f}", "fill_price": str(fills[sym]),
                         "reason": f"virtual buy-and-hold at {SLEEVES[v]['mirror']}'s first fill price"})
        set_cash(ledger, v, Decimal(0))
        ledger["start_values"][v] = str(start)
    append_trades(rows)
    event(ledger, "seed_virtual", ", ".join(f"{r['sleeve']} {r['symbol']} {r['quantity']} @ {r['fill_price']}"
                                           for r in rows))


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def first_trading_day_of_week(today: dt.date) -> tuple[bool, str]:
    monday = today - dt.timedelta(days=today.weekday())
    days = calendar(monday, today)
    if not days or days[-1]["date"] != today.isoformat():
        return False, f"{today} is not a trading day"
    if days[0]["date"] != today.isoformat():
        return False, f"{today} is not the first trading day of the week (that was {days[0]['date']})"
    return True, ""


def cmd_rebalance(args) -> int:
    acct = preflight()
    now = now_et()
    today = now.date()
    ok, why = first_trading_day_of_week(today)
    if not ok:
        log(f"no rebalance: {why}")
        note("did", f"nothing ({why})")
        return 0
    cal = calendar(today, today)[0]
    close = dt.datetime.combine(today, dt.time.fromisoformat(cal["close"]), ET)
    target = dt.datetime.combine(today, REBALANCE_TIME, ET)
    if now < target:
        if target - now > REBALANCE_EARLY_WAIT:
            log(f"too early ({now:%H:%M} ET); the rebalance runs at 10:00 ET")
            note("did", "nothing (too early)")
            return 0
        if not DRY_RUN:
            log(f"waiting until 10:00 ET ({int((target - now).total_seconds())}s)")
            time.sleep((target - now).total_seconds() + 1)
    if now_et() > close - REBALANCE_CUTOFF:
        log(f"no rebalance: too close to the {cal['close']} close")
        note("errors", f"run started too late ({now_et():%H:%M} ET); this week's rebalance skipped")
        return 1
    if not clock().get("is_open"):
        log("no rebalance: market is not open")
        note("errors", "market not open at run time")
        return 1

    ledger = load_ledger()
    date_tag = today.strftime("%Y%m%d")
    if ledger and today.isoformat() in ledger["rebalances"]:
        log(f"already rebalanced today ({today})")
        note("did", "nothing (already rebalanced today)")
        return 0

    pending = ledger.get("pending") if ledger else None
    if pending and pending.get("date") != today.isoformat():
        event(ledger, "stale_plan", f"dropping unfinished plan from {pending.get('date')}; reconciling from broker")
        ledger["pending"] = pending = None
    first = pending["first"] if pending else (ledger is None or not ledger.get("started"))

    # Orders for today already on Alpaca but no plan to resume: never add more.
    mine_today = [o for o in orders_since(today) if o.get("client_order_id", "").startswith(f"demon-{date_tag}")]
    if mine_today and not pending:
        raise NeedsAttention(
            f"{len(mine_today)} demon-{date_tag} orders already exist on Alpaca but the saved plan is "
            "gone. Nothing was placed. The next run reconciles the ledger from broker positions.")
    stray = [o for o in open_orders() if not o.get("client_order_id", "").startswith(f"demon-{date_tag}")]
    if stray:
        raise Stop(f"open orders not from today's rebalance: "
                   f"{[(o['symbol'], o['side'], o['qty'], o['client_order_id']) for o in stray]}")

    if pending:
        log(f"resuming today's unfinished plan (orders are matched by client_order_id, never re-sent)")
    elif first:
        if positions():
            raise Stop("first run but the account already holds positions; it must start flat")
        equity = D(acct["equity"])
        if D(acct["cash"]) != equity:
            raise Stop(f"first run but cash {acct['cash']} != equity {acct['equity']}")
        third = (equity / 3).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        ledger = ledger or empty_ledger()
        ledger["started"] = today.isoformat()
        for s in REAL:
            start = third + (equity - 3 * third if s == "A" else 0)  # leftover cents go to A
            set_cash(ledger, s, start)
            ledger["start_values"][s] = str(start)
        event(ledger, "start", f"equity {money(equity)}; A {money(ledger['start_values']['A'])}, "
                               f"C {money(third)}, E {money(third)}")
    else:
        process_activities(ledger)
        process_corporate_actions(ledger)
        reconcile(ledger, acct)
    save_ledger(ledger)

    if not pending:
        prices = latest_prices()
        deltas = plan_deltas(ledger, prices)
        nets = {sym: sum((deltas[s].get(sym, Decimal(0)) for s in REAL), Decimal(0)) for sym in SYMBOLS}
        sells = [sym for sym in SYMBOLS if nets[sym] < 0]
        rest = [sym for sym in SYMBOLS if nets[sym] >= 0]
        fit_buys_to_cash(ledger, deltas, prices, sells)
        pending = {"date": today.isoformat(), "first": first,
                   "prices": {k: str(v) for k, v in prices.items()},
                   "deltas": {s: {k: str(v) for k, v in d.items()} for s, d in deltas.items()},
                   "p1": make_orders(date_tag, "p1", deltas, sells, prices), "p2": None}
        ledger["pending"] = pending
        for s in REAL:
            log(f"plan {s} (value {money(sleeve_value(ledger, s, prices))}): "
                + (", ".join(f"{sym} {q:+}" for sym, q in deltas[s].items()) or "no trades"))
        save_ledger(ledger)

    # Phase 1: net sells (and sleeve buys netted inside them)
    execute_phase(ledger, pending["p1"], first)

    # Phase 2: net buys, sized against the cash each sleeve now has
    if pending["p2"] is None:
        prices = latest_prices()
        deltas = {s: {k: D(v) for k, v in d.items()} for s, d in pending["deltas"].items()}
        p1_syms = [o["symbol"] for o in pending["p1"]]
        p2_syms = [sym for sym in SYMBOLS if sym not in p1_syms]
        fit_buys_to_cash(ledger, deltas, prices, p2_syms)
        broker_cash = D(account()["cash"]) if not DRY_RUN else sum((cash(ledger, s) for s in REAL), Decimal(0))
        p2 = make_orders(date_tag, "p2", deltas, p2_syms, prices)
        need = sum((D(o["qty"]) * prices[o["symbol"]] * Decimal("1.005")
                    for o in p2 if o["side"] == "buy" and not o["internal"]), Decimal(0))
        if need > broker_cash:
            f = max(broker_cash, Decimal(0)) / need
            log(f"net buys {money(need)} exceed broker cash {money(broker_cash)}; scaling to {f:.4f}")
            note("errors", f"buys scaled to {f:.4f} to fit broker cash")
            for s in REAL:
                for sym in p2_syms:
                    if deltas[s].get(sym, 0) > 0:
                        deltas[s][sym] = q_qty(deltas[s][sym] * f)
            p2 = make_orders(date_tag, "p2", deltas, p2_syms, prices)
        pending["p2"] = p2
        save_ledger(ledger)
    execute_phase(ledger, pending["p2"], first)

    if DRY_RUN:
        note("did", "dry run: plan printed, nothing sent")
        return 0

    if first:
        seed_virtual(ledger)
    reconcile(ledger, account())
    ledger["rebalances"].append(today.isoformat())
    ledger["last_run"] = {"date": today.isoformat(),
                          "orders": [{k: o.get(k) for k in ("coid", "symbol", "side", "qty", "filled_qty",
                                                            "fill_price", "internal", "order_status")}
                                     for o in pending["p1"] + pending["p2"]]}
    ledger["pending"] = None
    save_ledger(ledger)
    path = write_summary(ledger)
    note("did", f"{'initial buy' if first else 'weekly rebalance'} #{len(ledger['rebalances'])}; summary {path}")
    return 3 if SUMMARY["errors"] else 0


def current_values(ledger: dict, prices: dict[str, Decimal]) -> dict[str, Decimal]:
    return {s: sleeve_value(ledger, s, prices) for s in SLEEVES}


def cmd_snapshot(args) -> int:
    acct = preflight()
    today = now_et().date()
    ledger = load_ledger()
    if not ledger or not ledger.get("started"):
        log("no snapshot: the test has not started")
        note("did", "nothing (not started)")
        return 0
    if not calendar(today, today) or calendar(today, today)[0]["date"] != today.isoformat():
        log(f"no snapshot: {today} is not a trading day")
        note("did", "nothing (not a trading day)")
        return 0
    if clock().get("is_open"):
        log("no snapshot: market is still open")
        note("errors", "snapshot ran while the market was open")
        return 1
    if ledger.get("pending"):
        note("errors", f"unfinished rebalance plan from {ledger['pending'].get('date')} in the ledger")
    else:
        process_activities(ledger)
        process_corporate_actions(ledger)
        reconcile(ledger, acct)
    save_ledger(ledger)
    prices = latest_prices()
    vals = current_values(ledger, prices)
    real_total = sum((vals[s] for s in REAL), Decimal(0))
    broker_eq = D(account()["equity"])
    row = {"date": today.isoformat(), "time_et": now_et().strftime("%H:%M"),
           **{s: f"{vals[s]:.2f}" for s in SLEEVES},
           "broker_equity": f"{broker_eq:.2f}", "ledger_real_total": f"{real_total:.2f}",
           "note": "" if abs(broker_eq - real_total) < 1 else f"A+C+E differs from broker equity by "
                                                               f"{real_total - broker_eq:+.2f}"}
    write_equity_row(row)
    log("snapshot " + ", ".join(f"{s} {money(vals[s])}" for s in SLEEVES) + f"; broker {money(broker_eq)}")
    note("did", f"snapshot {today}: " + ", ".join(f"{s} {money(vals[s])}" for s in SLEEVES))
    return 0


def max_drawdown(series: list[Decimal]) -> Decimal:
    peak, mdd = None, Decimal(0)
    for v in series:
        peak = v if peak is None or v > peak else peak
        if peak > 0:
            mdd = min(mdd, v / peak - 1)
    return mdd


def write_summary(ledger: dict) -> str:
    prices = latest_prices()
    vals = current_values(ledger, prices)
    rows = read_equity()
    today = now_et().date().isoformat()
    lines = [f"# Shannon's Demon: week of {today}", "",
             f"Started {ledger['started']}. Rebalances so far: {len(ledger['rebalances'])} "
             f"(including the initial buy). Values at {now_et():%Y-%m-%d %H:%M} ET.", "",
             "| Sleeve | What | Start | Now | Return | Max drawdown |",
             "|---|---|---:|---:|---:|---:|"]
    desc = {"A": "50% YINN / 50% SGOV, weekly", "B": "100% YINN, hold (virtual)",
            "C": "50% SOXL / 50% SGOV, weekly", "D": "100% SOXL, hold (virtual)",
            "E": "4 x 12.5% + 50% SGOV, weekly", "F": "4 x 25%, never rebalanced (virtual)"}
    ret = {}
    for s in SLEEVES:
        start = D(ledger["start_values"].get(s, "0"))
        series = [start] + [D(r[s]) for r in rows if r.get(s)] + [vals[s]]
        ret[s] = (vals[s] / start - 1) * 100 if start else Decimal(0)
        lines.append(f"| {s} | {desc[s]} | {money(start)} | {money(vals[s])} | {ret[s]:+.2f}% | "
                     f"{max_drawdown(series) * 100:.2f}% |")
    lines += ["", "| Comparison | Rebalanced minus buy-and-hold |", "|---|---:|"]
    for a, b in PAIRS:
        lines.append(f"| {a} vs {b} | {ret[a] - ret[b]:+.2f} pp |")
    last = ledger.get("last_run") or {}
    if last.get("orders"):
        lines += ["", f"Orders on {last['date']}:", ""]
        for o in last["orders"]:
            kind = "netted internally" if o["internal"] else f"{o.get('order_status')}"
            lines.append(f"- {o['side']} {o['qty']} {o['symbol']}: filled {o.get('filled_qty')} "
                         f"@ {o.get('fill_price')} ({kind})")
    lines += ["", "Max drawdown uses the daily snapshots in equity.csv plus the start and current value. "
              "Virtual sleeves B, D, F include distributions from Alpaca's corporate-actions data.", ""]
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    path = os.path.join(SUMMARY_DIR, f"{today}.md")
    if not DRY_RUN:
        with open(path, "w") as f:
            f.write("\n".join(lines))
    print("\n".join(lines))
    return os.path.relpath(path, HERE)


def cmd_summary(args) -> int:
    preflight()
    ledger = load_ledger()
    if not ledger or not ledger.get("started"):
        log("no summary: the test has not started")
        return 0
    write_summary(ledger)
    return 0


def cmd_status(args) -> int:
    acct = preflight()
    print(f"paper account OK: status {acct['status']}, equity {money(acct['equity'])}, cash {money(acct['cash'])}")
    c = clock()
    print(f"clock: open={c['is_open']} next_open={c['next_open']} next_close={c['next_close']}")
    pos = positions()
    print("positions: " + (", ".join(f"{s} {p['qty']} ({money(p['market_value'])})" for s, p in pos.items()) or "none"))
    oo = open_orders()
    print("open orders: " + (", ".join(f"{o['side']} {o['qty']} {o['symbol']} {o['client_order_id']}"
                                       for o in oo) or "none"))
    ledger = load_ledger()
    if not ledger or not ledger.get("started"):
        print("ledger: test not started")
        return 0
    prices = latest_prices()
    for s in SLEEVES:
        hold = ", ".join(f"{k} {D(v):.4f}" for k, v in ledger["sleeves"][s]["shares"].items() if D(v))
        print(f"  {s}: value {money(sleeve_value(ledger, s, prices))} cash {money(cash(ledger, s))} | {hold}")
    for sym in SYMBOLS:
        b = D(pos[sym]["qty"]) if sym in pos else Decimal(0)
        m = real_total_shares(ledger, sym)
        print(f"  {sym}: broker {b} ledger A+C+E {m} {'OK' if abs(b - m) <= Decimal('0.000002') else 'MISMATCH'}")
    lc = sum((cash(ledger, s) for s in REAL), Decimal(0))
    print(f"  cash: broker {money(acct['cash'])} ledger A+C+E {money(lc)}")
    if ledger.get("pending"):
        print(f"  unfinished plan from {ledger['pending']['date']}")
    return 0


def main() -> int:
    global DRY_RUN
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["status", "rebalance", "snapshot", "summary"])
    ap.add_argument("--dry-run", action="store_true", help="no orders, no files written")
    args = ap.parse_args()
    DRY_RUN = args.dry_run
    fn = {"status": cmd_status, "rebalance": cmd_rebalance, "snapshot": cmd_snapshot, "summary": cmd_summary}
    code = 0
    try:
        code = fn[args.command](args)
    except Stop as e:
        log(f"STOP: {e}")
        note("errors", f"STOP: {e}")
        code = 2
    except NeedsAttention as e:
        log(f"ATTENTION: {e}")
        note("errors", str(e))
        code = 4
    except Exception as e:  # noqa: BLE001
        log(f"ERROR: {type(e).__name__}: {e}")
        note("errors", f"{type(e).__name__}: {e}")
        code = 1
    if args.command != "status":
        print("\nSUMMARY")
        for k in ("did", "fills", "errors"):
            print(f"{k + ':':7} " + ("; ".join(SUMMARY[k]) or ("none" if k != "did" else "nothing")))
    return code


if __name__ == "__main__":
    sys.exit(main())
