"""Offline test of demon.py against a fake broker. No network, no files in the repo.

Run: python3 demon/sim_test.py   (prints ALL CHECKS PASSED)
Simulates the initial buy with a crash and retry, 10 weekly rebalances with
holidays, a distribution, a reverse split and a fee, and checks after every
run that the ledger matches the fake broker and no order is ever duplicated,
overspent or short."""
import datetime as dt
import os
import random
import shutil
import sys
import tempfile
from decimal import Decimal as D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import demon  # noqa: E402

ET = demon.ET
tmp = tempfile.mkdtemp()
demon.LEDGER_PATH = os.path.join(tmp, "ledger.json")
demon.TRADES_PATH = os.path.join(tmp, "trades.csv")
demon.EQUITY_PATH = os.path.join(tmp, "equity.csv")
demon.SUMMARY_DIR = os.path.join(tmp, "summaries")
demon.LOG_PATH = os.path.join(tmp, "demon.log")
demon.time.sleep = lambda s: None


class Broker:
    def __init__(self):
        self.cash = D("100000")
        self.pos = {}
        self.orders = {}
        self.prices = {"YINN": D("19.01"), "SOXL": D("32.44"), "LABU": D("235.78"),
                       "NAIL": D("34.63"), "TMF": D("29.52"), "SGOV": D("100.66")}
        self.now = None
        self.activities = []
        self.cas = []
        self.sent = []
        self.fail_after = None  # raise after N order POSTs

    def acct(self):
        eq = self.cash + sum(self.pos[s] * self.prices[s] for s in self.pos)
        return {"account_number": "PA123", "status": "ACTIVE", "currency": "USD",
                "cash": str(self.cash), "equity": str(eq)}

    def positions(self):
        return {s: {"symbol": s, "qty": str(q), "current_price": str(self.prices[s]),
                    "market_value": str(q * self.prices[s])} for s, q in self.pos.items() if q != 0}

    def post(self, body):
        if self.fail_after is not None and len(self.sent) >= self.fail_after:
            self.fail_after = None
            raise RuntimeError("simulated crash")
        coid = body["client_order_id"]
        assert coid not in self.orders, f"DUPLICATE order {coid}"
        q, sym = D(body["qty"]), body["symbol"]
        slip = D("1.001") if body["side"] == "buy" else D("0.999")
        px = (self.prices[sym] * slip).quantize(D("0.0001"))
        if body["side"] == "buy":
            assert self.cash >= q * px, f"OVERSPEND cash {self.cash} < {q * px}"
            self.cash -= q * px
            self.pos[sym] = self.pos.get(sym, D(0)) + q
        else:
            assert self.pos.get(sym, D(0)) >= q, f"SHORT {sym}"
            self.cash += q * px
            self.pos[sym] -= q
        self.cash = self.cash.quantize(D("0.01"))
        o = {"id": coid, "client_order_id": coid, "status": "filled", "filled_qty": str(q),
             "filled_avg_price": str(px), "symbol": sym, "side": body["side"], "qty": str(q),
             "created_at": self.now.isoformat()}
        self.orders[coid] = o
        self.sent.append(o)
        return o


B = Broker()


def fake_http(method, url, params=None, body=None):
    assert method == "POST" and url.endswith("/v2/orders"), (method, url)
    return B.post(body)


def cal(start, end):
    out, d = [], start
    while d <= end:
        if d.weekday() < 5 and d not in HOLIDAYS:
            out.append({"date": d.isoformat(), "open": "09:30", "close": "16:00"})
        d += dt.timedelta(days=1)
    return out


HOLIDAYS = {dt.date(2026, 12, 25), dt.date(2027, 1, 1), dt.date(2027, 1, 18)}
demon.http = fake_http
demon.account = B.acct
demon.positions = B.positions
demon.now_et = lambda: B.now
demon.calendar = cal
demon.clock = lambda: {"is_open": dt.time(9, 30) <= B.now.time() < dt.time(16, 0)}
demon.open_orders = lambda: []
demon.orders_since = lambda day: [o for o in B.orders.values() if o["created_at"][:10] >= day.isoformat()]
demon.order_by_coid = lambda c: B.orders.get(c)
demon.get_order = lambda i: B.orders[i]
demon.latest_prices = lambda: dict(B.prices)
demon.activities_since = lambda day: list(B.activities)
demon.corporate_actions = lambda s, e: list(B.cas)


def check(label):
    led = demon.load_ledger()
    for sym in demon.SYMBOLS:
        b = B.pos.get(sym, D(0))
        m = demon.real_total_shares(led, sym)
        assert abs(b - m) < D("0.00001"), f"{label}: {sym} broker {b} ledger {m}"
    lc = sum(demon.cash(led, s) for s in demon.REAL)
    assert abs(lc - B.cash) < D("0.02"), f"{label}: cash broker {B.cash} ledger {lc}"
    for s in demon.SLEEVES:
        assert demon.cash(led, s) > D("-1"), f"{label}: {s} cash {demon.cash(led, s)}"
    for s in demon.REAL:
        v = demon.sleeve_value(led, s, B.prices)
        w = {sym: demon.shares(led, s, sym) * B.prices[sym] / v for sym in demon.SLEEVES[s]["weights"]}
    return led


def run(cmd, when):
    B.now = when
    demon.SUMMARY = {"did": [], "fills": [], "errors": []}
    return demon.main.__wrapped__(cmd) if hasattr(demon.main, "__wrapped__") else _main(cmd)


def _main(cmd):
    sys.argv = ["demon.py", cmd]
    return demon.main()


random.seed(7)
# Week 1: Mon Nov 30 10:00 initial buy; simulate a crash after 3 orders, then a retry
B.fail_after = 3
code = run("rebalance", dt.datetime(2026, 11, 30, 10, 0, tzinfo=ET))
print("first attempt exit", code)
code = run("rebalance", dt.datetime(2026, 11, 30, 10, 5, tzinfo=ET))
print("retry exit", code)
assert code == 0
led = check("initial")
print({s: led["sleeves"][s] for s in "BDF"})
code = run("rebalance", dt.datetime(2026, 11, 30, 10, 7, tzinfo=ET))
assert code == 0 and "already" in demon.SUMMARY["did"][0]

day = dt.date(2026, 11, 30)
for week in range(10):
    for i in range(5):
        d = day + dt.timedelta(days=i)
        if d in HOLIDAYS:
            continue
        for s in B.prices:
            vol = D("0.0001") if s == "SGOV" else D(str(random.gauss(0, 0.04)))
            B.prices[s] = (B.prices[s] * (1 + vol)).quantize(D("0.0001"))
        if week == 2 and i == 1:  # SGOV distribution + a 1:5 reverse split on NAIL
            amt = (B.pos["SGOV"] * D("0.33")).quantize(D("0.01"))
            B.cash += amt
            B.activities.append({"id": "div1", "activity_type": "DIV", "symbol": "SGOV",
                                 "net_amount": str(amt), "date": d.isoformat()})
            B.cas.append({"id": "cd1", "kind": "cash_dividends", "symbol": "SGOV", "rate": 0.33,
                          "ex_date": d.isoformat(), "payable_date": d.isoformat()})
            B.pos["NAIL"] = (B.pos["NAIL"] / 5).quantize(D("0.000000001"))
            B.prices["NAIL"] *= 5
            B.cas.append({"id": "rs1", "kind": "reverse_splits", "symbol": "NAIL", "old_rate": 5,
                          "new_rate": 1, "ex_date": d.isoformat()})
            B.cash -= D("0.03")  # a fee
        run("snapshot", dt.datetime.combine(d, dt.time(16, 15), ET))
        check(f"snapshot {d}")
        if i == 0 or (d - dt.timedelta(days=1)) in HOLIDAYS and i == 1:
            pass
    # rebalance: run Mon..Fri at 10:00 — script decides
    day += dt.timedelta(days=7)
    for i in range(5):
        d = day + dt.timedelta(days=i)
        n0 = len(B.sent)
        run("rebalance", dt.datetime.combine(d, dt.time(10, 0), ET))
        if len(B.sent) > n0 or "weekly" in " ".join(demon.SUMMARY["did"]):
            print(d, "rebalanced, orders", len(B.sent) - n0, demon.SUMMARY["errors"])
        check(f"rebalance {d}")

led = demon.load_ledger()
print("rebalances", led["rebalances"])
print(open(os.path.join(demon.SUMMARY_DIR, sorted(os.listdir(demon.SUMMARY_DIR))[-1])).read())
print([e for e in led["events"] if e["type"] != "reconcile" or "cash" not in e["detail"]][:12])
print(open(demon.TRADES_PATH).read()[:1500])
shutil.rmtree(tmp)
print("ALL CHECKS PASSED")
