#!/usr/bin/env python3
"""Event-driven options bot: paper trading experiment only.

Two chains share every decision point:
  claude  real paper orders on Alpaca (limit at the ask, 2-minute fill window)
  shadow  random event, coin-flip direction, same strike rule, booked at the
          same quotes; never sends an order

Commands (all times ET, market days only)
  buy    3:15 p.m.  close anything still open, then bet on tonight's /
                    tomorrow morning's event if one qualifies
  sell   9:45 a.m.  sell half of an overnight position
  fed    1:45 p.m.  Fed decision days only: SPY same-day expiry, closed by buy
  probe             read-only: SPY + one watchlist stock quotes, expected move, strikes
  status            ledger balances and open bets; Alpaca account + positions
  report            trade table from the ledger
  refresh-earnings  re-download the earnings calendar (also automatic, weekly)

--dry-run on any command: every GET runs, no order is sent, no file is written.
The claude chain's pick can be given with --event / --direction / --reason;
otherwise the built-in rule decides and logs its one-line reason.
See README.md for the rules.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import secrets
import sys
from dataclasses import dataclass
from decimal import Decimal
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import alpaca  # noqa: E402
import chain as ch  # noqa: E402
import earnings  # noqa: E402
import net  # noqa: E402
import settings  # noqa: E402
from strikes import OptionQuote, expected_move, pick_strike  # noqa: E402
from timing import (Candidate, EarningsEvent, MarketCalendar, buy_run_candidates,  # noqa: E402
                    fed_candidate, in_window)

ET = ZoneInfo("America/New_York")
LEDGER_PATH = os.path.join(HERE, "ledger.json")
EARNINGS_PATH = os.path.join(HERE, "earnings.json")
LOG_PATH = os.path.join(HERE, "run.log")
RNG = secrets.SystemRandom()


# --------------------------------------------------------------------------
# Run context
# --------------------------------------------------------------------------
class Run:
    def __init__(self, args):
        self.args = args
        self.dry = bool(args.dry_run)
        net.DRY_RUN = self.dry
        self.cfg = settings.config()
        alpaca.MAX_QUOTE_AGE = dt.timedelta(minutes=self.cfg["quote_max_age_minutes"])
        self.rules: ch.Rules = self.cfg["rules"]
        self.now = self._now(args)
        self.today = self.now.date()
        self.ledger = self._load_ledger()
        self.summary: list[str] = []

    def _now(self, args) -> dt.datetime:
        if getattr(args, "at", None):
            if not args.dry_run:
                raise SystemExit("--at is only allowed with --dry-run")
            return dt.datetime.fromisoformat(args.at).replace(tzinfo=ET)
        return dt.datetime.now(ET)

    def _load_ledger(self) -> dict:
        if os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH) as f:
                return json.load(f)
        return ch.new_ledger(self.rules)

    def save(self) -> None:
        if self.dry:
            print("[dry-run] ledger.json not written")
            return
        tmp = LEDGER_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.ledger, f, indent=1)
            f.write("\n")
        os.replace(tmp, LEDGER_PATH)

    def log(self, msg: str) -> None:
        line = f"{dt.datetime.now(ET).isoformat(timespec='seconds')} {'[dry-run] ' if self.dry else ''}{msg}"
        print(line)
        if not self.dry:
            with open(LOG_PATH, "a") as f:
                f.write(line + "\n")

    def note(self, chain: str, msg: str) -> None:
        """Log and keep in ledger.json's log (committed with the ledger)."""
        self.log(f"[{chain}] {msg}")
        ch.note(self.ledger, self.now, chain, msg)
        self.summary.append(f"{chain}: {msg}")

    def market(self) -> MarketCalendar:
        first, last = self.today - dt.timedelta(days=10), self.today + dt.timedelta(days=20)
        return MarketCalendar.from_alpaca(alpaca.calendar(first, last), first, last)

    def check_window(self, name: str) -> None:
        start, end = self.cfg["windows"][name]
        if in_window(self.now.time(), start, end):
            return
        if self.dry or getattr(self.args, "force_time", False):
            self.log(f"outside the {name} window {start:%H:%M}-{end:%H:%M} ET (now {self.now:%H:%M}); "
                     "continuing because of --dry-run/--force-time")
            return
        raise SystemExit(f"Not the {name} window ({start:%H:%M}-{end:%H:%M} ET); now {self.now:%H:%M}. "
                         "Use --force-time to override.")


# --------------------------------------------------------------------------
# Pricing a candidate (one quote snapshot shared by both chains)
# --------------------------------------------------------------------------
@dataclass
class Priced:
    cand: Candidate
    spot: Decimal
    change_pct: Decimal | None
    expiry: dt.date
    atm: Decimal
    move: Decimal
    call: OptionQuote | None
    put: OptionQuote | None

    def leg(self, direction: str) -> OptionQuote | None:
        return self.call if direction == "call" else self.put

    @property
    def move_pct(self) -> Decimal:
        return self.move / self.spot * 100

    def describe(self) -> str:
        legs = "; ".join(f"{d} {q.strike} bid {q.bid} ask {q.ask}" if q else f"{d} none"
                         for d, q in (("call", self.call), ("put", self.put)))
        chg = f"{self.change_pct:+.2f}%" if self.change_pct is not None else "n/a"
        return (f"{self.cand.id} exp {self.expiry}: spot {self.spot} ({chg} today), ATM {self.atm}, "
                f"expected move ±{self.move:.2f} ({self.move_pct:.1f}%) -> {legs}")


def price(c: Candidate) -> Priced:
    spot, chg = alpaca.spot_and_change(c.ticker)
    if c.exact_expiry:
        expiry = c.expiry_on_or_after
    else:
        exps = alpaca.expiries(c.ticker, c.expiry_on_or_after)
        if not exps:
            raise RuntimeError(f"no {c.ticker} expiry on/after {c.expiry_on_or_after}")
        expiry = exps[0]
    quotes = alpaca.option_chain(c.ticker, expiry)
    if not quotes:
        raise RuntimeError(f"no fresh quotes (<= {alpaca.MAX_QUOTE_AGE}) for {c.ticker} options expiring {expiry}")
    em = expected_move(quotes, spot)
    if em is None:
        raise RuntimeError(f"no ATM call+put pair for {c.ticker} {expiry}")
    atm, move = em
    return Priced(c, spot, chg, expiry, atm, move,
                  pick_strike(quotes, spot, move, "call"), pick_strike(quotes, spot, move, "put"))


def can_afford(state: dict, ask: Decimal, r: ch.Rules) -> bool:
    """Would this chain get at least one contract (after a bust-restart if one is due)?"""
    bal = Decimal(state["balance"])
    if bal < ch.one_contract(ask, r) and bal < r.start:
        bal = r.start
    return ch.contracts_for(bal, ask, r) >= 1


def claude_choice(run: Run, priced: list[Priced]) -> tuple[Priced, str, str] | None:
    """Pick (event, direction, one-line reason) for the claude chain."""
    a = run.args
    if getattr(a, "event", None):
        hits = [p for p in priced if p.cand.id == a.event or p.cand.id.startswith(a.event + ":")
                or p.cand.ticker == a.event.upper() or p.cand.kind == a.event.lower()]
        if len(hits) != 1:
            raise SystemExit(f"--event {a.event!r} matched {len(hits)} candidates: "
                             + ", ".join(p.cand.id for p in priced))
        p = hits[0]
    if getattr(a, "direction", None):
        direction, reason = a.direction, a.reason
        if not getattr(a, "event", None):
            if len(priced) != 1:
                raise SystemExit("--direction needs --event when several events qualify: "
                                 + ", ".join(p.cand.id for p in priced))
            p = priced[0]
        return p, direction, reason
    # Built-in rule: momentum direction, biggest affordable implied move.
    state = run.ledger["chains"]["claude"]

    def dir_for(p: Priced) -> str:
        return "put" if (p.change_pct or 0) < 0 else "call"

    pool = [p] if getattr(a, "event", None) else priced
    ok = [x for x in pool if x.leg(dir_for(x)) and can_afford(state, x.leg(dir_for(x)).ask, run.rules)]
    if not ok:
        ok = [x for x in pool if x.leg(dir_for(x))]
    if not ok:
        return None
    best = max(ok, key=lambda x: x.move_pct)
    d = dir_for(best)
    chg = f"{best.change_pct:+.1f}%" if best.change_pct is not None else "flat"
    others = f" over {len(priced) - 1} other(s)" if len(priced) > 1 else ""
    reason = (f"{best.cand.label()}: largest implied move ({best.move_pct:.1f}%) that the chain can afford{others}; "
              f"{best.cand.ticker} {chg} today, so {d} (follow the day's momentum)")
    return best, d, reason


def shadow_choice(run: Run, priced: list[Priced]) -> tuple[Priced, str, str] | None:
    direction = RNG.choice(["call", "put"])
    state = run.ledger["chains"]["shadow"]
    pool = [p for p in priced if p.leg(direction) and can_afford(state, p.leg(direction).ask, run.rules)]
    pool = pool or [p for p in priced if p.leg(direction)]
    if not pool:
        return None
    p = RNG.choice(pool)
    return p, direction, f"random pick of {len(pool)} event(s), coin flip {direction}"


# --------------------------------------------------------------------------
# Entering and exiting
# --------------------------------------------------------------------------
def alpaca_option_positions() -> dict[str, int]:
    return {p["symbol"]: int(Decimal(p["qty"])) for p in alpaca.positions() if p.get("asset_class") == "us_option"}


def enter(run: Run, chain: str, pick: tuple[Priced, str, str], tag: str) -> None:
    p, direction, reason = pick
    q = p.leg(direction)
    if q is None:
        run.note(chain, f"skip {p.cand.label()}: no quoted {direction} strike beyond the expected move")
        return
    n, why = ch.size_bet(run.ledger, chain, q.ask, run.now, run.rules)
    if n == 0:
        run.note(chain, f"skip {p.cand.label()} {direction} {q.symbol} ask {q.ask}: {why}")
        return
    common = dict(event=p.cand.label(), event_id=p.cand.id, ticker=p.cand.ticker, direction=direction,
                  symbol=q.symbol, strike=q.strike, expiry=p.expiry, quote_ask=q.ask,
                  reasoning=reason, overnight=p.cand.overnight, exit_day=p.cand.exit_day, r=run.rules)
    run.log(f"[{chain}] {p.cand.label()}: {direction} {q.symbol} strike {q.strike} exp {p.expiry} "
            f"bid {q.bid} ask {q.ask} x{n} (stake ${ch.money(ch.stake(Decimal(run.ledger['chains'][chain]['balance']), run.rules))}) "
            f"| {reason}")
    if chain == "shadow":
        if run.dry:
            run.log(f"[shadow] would book {n} @ {q.ask} (no order, booked at the quote)")
            return
        t = ch.record_entry(run.ledger, chain, run.now, qty=n, price=q.ask, **common)
        run.note(chain, f"booked {n} {q.symbol} @ {q.ask} (no order), ledger cost ${t['entry_value']}, "
                        f"balance {run.ledger['chains'][chain]['balance']}, step {t['step']}")
        return
    cid = f"evt-claude-{run.today:%Y%m%d}-{tag}"
    if run.dry:
        run.log(f"[claude] DRY RUN: would send {cid}: buy {n} {q.symbol} limit {q.ask} day; "
                f"cancel after {run.cfg['fill_wait_seconds']}s if unfilled")
        return
    try:
        filled, avg, o = alpaca.limit_and_wait(q.symbol, n, "buy", q.ask, cid, run.cfg["fill_wait_seconds"], run.log)
    except net.ApiError as e:
        run.note(chain, f"buy {cid} REJECTED HTTP {e.status}: {e.body[:300]}")
        return
    if o["status"] == "rejected":
        run.note(chain, f"buy REJECTED: {json.dumps(o)}")
        return
    if filled == 0:
        run.note(chain, f"no fill: {cid} buy {n} {q.symbol} @ {q.ask} cancelled after "
                        f"{run.cfg['fill_wait_seconds']}s (status {o['status']})")
        return
    t = ch.record_entry(run.ledger, chain, run.now, qty=filled, price=avg, **common)
    part = f" (partial {filled}/{n}, rest cancelled)" if filled < n else ""
    run.note(chain, f"bought {filled} {q.symbol} @ {avg}{part}, ledger cost ${t['entry_value']}, "
                    f"balance {run.ledger['chains'][chain]['balance']}, step {t['step']}")


def sell(run: Run, chain: str, qty: int, step: str) -> None:
    """Sell `qty` of this chain's open bet: claude at the bid via limit orders, shadow booked at the bid."""
    t = ch.open_trade(run.ledger, chain)
    sym = t["symbol"]
    if dt.date.fromisoformat(t["expiry"]) < run.today:
        if not run.dry:
            ch.write_off(run.ledger, chain, run.now, f"expired {t['expiry']} before it was sold; "
                         "check Alpaca account activity", run.rules)
        run.note(chain, f"{sym} expired unsold; written off at $0")
        return
    try:
        bid, ask = alpaca.quote(sym)
    except alpaca.StaleQuote as e:
        run.note(chain, f"{step}: not sold, {e}; the next run tries again")
        return
    if chain == "shadow":
        if run.dry:
            run.log(f"[shadow] would book sale of {qty} {sym} @ bid {bid}")
            return
        ch.record_exit(run.ledger, chain, run.now, qty, bid, run.rules, how=f"{step} at bid (no order)")
        run.note(chain, f"{step}: booked sale of {qty} {sym} @ bid {bid} (no order); balance "
                        f"{run.ledger['chains'][chain]['balance']}")
        return
    held = alpaca_option_positions().get(sym, 0)
    if held < qty:
        run.note(chain, f"WARNING ledger has {t['remaining']} {sym} but Alpaca holds {held}; selling {held}")
        qty = held
    if qty <= 0:
        if not run.dry:
            ch.write_off(run.ledger, chain, run.now, "not held at Alpaca (check account activity)", run.rules)
        return
    left = qty
    for attempt in ("", "-r"):
        if left <= 0:
            break
        if attempt:
            try:
                bid, ask = alpaca.quote(sym)
            except alpaca.StaleQuote as e:
                run.note(chain, f"{step}: retry skipped, {e}")
                break
        if bid <= 0:
            run.note(chain, f"{step}: no bid for {sym}; {left} not sold (will retry next run)")
            return
        cid = f"evt-claude-{run.today:%Y%m%d}-{step}{attempt}"
        if run.dry:
            run.log(f"[claude] DRY RUN: would send {cid}: sell {left} {sym} limit {bid} (bid) day")
            return
        try:
            q, avg, o = alpaca.limit_and_wait(sym, left, "sell", bid, cid, run.cfg["fill_wait_seconds"], run.log)
        except net.ApiError as e:
            run.note(chain, f"{step}: {cid} REJECTED HTTP {e.status}: {e.body[:300]}")
            break
        if q:
            ch.record_exit(run.ledger, chain, run.now, q, avg, run.rules, how=step)
            run.note(chain, f"{step}: sold {q} {sym} @ {avg}; balance {run.ledger['chains'][chain]['balance']}")
            left -= q
        if left:
            run.note(chain, f"{step}: {cid} sell {left} {sym} @ {bid} not filled in "
                            f"{run.cfg['fill_wait_seconds']}s; cancelled (status {o['status']})")
    if left:
        run.note(chain, f"{step}: {left} {sym} still open; the next run tries again")


def close_open(run: Run) -> None:
    """3:15 p.m.: sell everything still open from earlier buys."""
    for chain in ch.CHAINS:
        t = ch.open_trade(run.ledger, chain)
        if t is None:
            continue
        if dt.date.fromisoformat(t["exit_day"]) > run.today:
            run.note(chain, f"open bet {t['id']} exits {t['exit_day']}, not today; leaving it")
            continue
        sell(run, chain, t["remaining"], "close")


def reconcile(run: Run) -> bool:
    """True if Alpaca's option positions match the claude chain's ledger."""
    t = ch.open_trade(run.ledger, "claude")
    held = alpaca_option_positions()
    expect = {t["symbol"]: t["remaining"]} if t else {}
    if held != expect:
        run.note("claude", f"WARNING Alpaca option positions {held} != ledger {expect}; no new claude bet")
        return False
    return True


def place_bets(run: Run, priced: list[Priced], tag: str) -> None:
    if not priced:
        run.note("-", "no event could be priced; no bet")
        return
    run.log(f"{len(priced)} priced candidate(s):")
    for p in priced:
        run.log("  " + p.describe())
    for chain, chooser in (("claude", claude_choice), ("shadow", shadow_choice)):
        if ch.open_trade(run.ledger, chain):
            run.note(chain, "skip: a bet is still open (one at a time)")
            continue
        if chain == "claude" and not reconcile(run):
            continue
        pick = chooser(run, priced)
        if pick is None:
            run.note(chain, "skip: no candidate has a strike beyond the expected move")
            continue
        enter(run, chain, pick, tag)


def price_all(run: Run, cands: list[Candidate]) -> list[Priced]:
    out = []
    for c in cands:
        try:
            out.append(price(c))
        except (RuntimeError, net.ApiError) as e:
            run.note("-", f"skip {c.label()}: {e}")
    return out


# --------------------------------------------------------------------------
# Earnings
# --------------------------------------------------------------------------
def earnings_events(run: Run) -> list[EarningsEvent]:
    watch = set(settings.watchlist())
    cache = earnings.load(EARNINGS_PATH)
    if earnings.is_stale(cache, run.today):
        try:
            cache = earnings.refresh(run.today, watch)
            run.log(f"earnings calendar refreshed: {len(cache['events'])} watchlist reports "
                    f"{cache['from']}..{cache['to']}")
            if not run.dry:
                earnings.save(EARNINGS_PATH, cache)
        except Exception as e:  # blocked host, 403, bad JSON: keep going without earnings
            run.note("-", f"earnings refresh failed ({type(e).__name__}: {str(e)[:200]}); "
                          + ("using the old cache" if cache else "no earnings events"))
    if not cache:
        return []
    return [EarningsEvent(e["ticker"], dt.date.fromisoformat(e["date"]), e["when"]) for e in cache["events"]]


def recheck_earnings(run: Run, cands: list[Candidate]) -> list[Candidate]:
    """Re-fetch each report date on the day of the trade; drop any that moved."""
    watch = set(settings.watchlist())
    fresh: dict[dt.date, list[dict] | Exception] = {}
    out = []
    for c in cands:
        if c.kind != "earnings":
            out.append(c)
            continue
        if c.event_date not in fresh:
            try:
                fresh[c.event_date] = earnings.fetch_day(c.event_date, watch)
            except Exception as e:
                fresh[c.event_date] = e
        f = fresh[c.event_date]
        why = f"could not re-check the date ({type(f).__name__})" if isinstance(f, Exception) \
            else earnings.still_scheduled(c.ticker, c.event_date, c.when, f)
        if why:
            run.note("-", f"skip {c.label()}: {why}")
        else:
            out.append(c)
    return out


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def cmd_buy(run: Run) -> None:
    alpaca.require_paper()
    run.check_window("buy")
    cal = run.market()
    if not cal.is_trading_day(run.today):
        run.note("-", f"buy: {run.today} is not a trading day")
        return
    close_open(run)
    macro, warn = settings.macro_events()
    for w in warn:
        run.log(w)
    cands, skipped = buy_run_candidates(run.today, cal, macro, earnings_events(run), run.cfg["macro_ticker"])
    for s in skipped:
        run.note("-", f"skip {s}")
    cands = recheck_earnings(run, cands)
    if not cands:
        run.note("-", "buy: no event qualifies tonight / tomorrow morning")
        return
    place_bets(run, price_all(run, cands), "buy")


def cmd_sell(run: Run) -> None:
    alpaca.require_paper()
    run.check_window("sell")
    for chain in ch.CHAINS:
        t = ch.open_trade(run.ledger, chain)
        if t is None or not t["overnight"] or t["half_done"]:
            continue
        if t["exit_day"] != run.today.isoformat():
            run.note(chain, f"open overnight bet {t['id']} exits {t['exit_day']}, not today; not selling")
            continue
        half = t["contracts"] // 2
        if half == 0:
            run.note(chain, f"{t['symbol']}: 1 contract, nothing to sell at 9:45; all of it goes at 3:15")
        else:
            sell(run, chain, min(half, t["remaining"]), "half")
        if not run.dry:
            t["half_done"] = True


def cmd_fed(run: Run) -> None:
    alpaca.require_paper()
    run.check_window("fed")
    macro, _ = settings.macro_events()
    c, why = fed_candidate(run.today, run.market(), macro, run.cfg["macro_ticker"])
    if c is None:
        run.note("-", f"fed: {why}")
        return
    place_bets(run, price_all(run, [c]), "fed")


def cmd_probe(run: Run) -> None:
    """Read-only: show that SPY options and one watchlist stock's options can be quoted."""
    acct = alpaca.require_paper()
    print(f"Alpaca paper account {acct['account_number']} ({acct['status']}), "
          f"options level {acct.get('options_trading_level')}")
    for ticker in [run.cfg["macro_ticker"], run.args.ticker or settings.watchlist()[0]]:
        exps = alpaca.expiries(ticker, run.today)
        if not exps:
            print(f"{ticker}: no expiries found")
            continue
        c = Candidate("probe", ticker, run.today, "-", run.today, run.today, exps[0], True)
        try:
            p = price(c)
        except RuntimeError as e:
            print(f"{ticker}: {e}")
            continue
        print(f"{ticker}: expiries {', '.join(map(str, exps[:5]))}")
        print("  " + p.describe())


def cmd_status(run: Run) -> None:
    for chain, s in run.ledger["chains"].items():
        t = ch.open_trade(run.ledger, chain)
        print(f"{chain:7} balance ${s['balance']} step {s['step']} restarts {s['restarts']} "
              f"busts {s['busts']} targets {s['targets_hit']} open: "
              + (f"{t['symbol']} x{t['remaining']} (exit {t['exit_day']})" if t else "none"))
    try:
        acct = alpaca.require_paper()
        print(f"Alpaca {acct['account_number']} cash {acct['cash']}; option positions {alpaca_option_positions()}")
    except Exception as e:
        print(f"Alpaca not reachable: {type(e).__name__}: {e}")


def cmd_report(run: Run) -> None:
    rows = run.ledger["trades"]
    if not rows:
        print("No trades yet.")
    for t in rows:
        exits = ", ".join(f"{x['qty']}@{x['price']}" for x in t["exits"]) or "-"
        print(f"{t['date']} {t['chain']:6} #{t['step']}/r{t['restarts']} {t['event']} | {t['direction']} "
              f"{t['ticker']} {t['strike']} exp {t['expiry']} x{t['contracts']} buy@{t['entry_price']} "
              f"sell {exits} | haircut value {t['haircut_value']} balance after {t['balance_after']} "
              f"| {t['reasoning']}")
    cmd_status_ledger_only(run)


def cmd_status_ledger_only(run: Run) -> None:
    for chain, s in run.ledger["chains"].items():
        print(f"{chain}: balance ${s['balance']} step {s['step']} restarts {s['restarts']} busts {s['busts']}")


def cmd_test_trade(run: Run) -> None:
    """Plumbing test: buy 1 cheap SPY option at the ask, then sell it at the bid.

    Real paper orders (tagged evt-test-...), but outside both chains: the
    ledger is not touched. Run while the market is open.
    """
    alpaca.require_paper()
    cal = run.market()
    if not cal.is_trading_day(run.today) or not (dt.time(9, 35) <= run.now.time() <= dt.time(15, 0)):
        if not (run.dry or run.args.force_time):
            raise SystemExit("test-trade runs 9:35 a.m.-3:00 p.m. ET on a market day (or use --force-time)")
    held = alpaca_option_positions()
    if held:
        raise SystemExit(f"REFUSED: option positions already open {held}; test-trade needs a flat account")
    spy = (run.args.ticker or run.cfg["macro_ticker"]).upper()
    exp = alpaca.expiries(spy, run.today)[0]
    quotes = [q for q in alpaca.option_chain(spy, exp)
              if q.kind == "call" and q.bid > 0 and Decimal("0.05") <= q.ask <= Decimal("0.50")]
    if not quotes:
        raise SystemExit(f"no {spy} {exp} call with a fresh quote between $0.05 and $0.50")
    q = min(quotes, key=lambda x: (abs(x.ask - Decimal("0.20")), x.ask - x.bid))
    wait = run.cfg["fill_wait_seconds"]
    tag = f"evt-test-{run.now:%Y%m%d-%H%M}"
    run.log(f"TEST: {q.symbol} bid {q.bid} ask {q.ask}; buy 1 at the ask, then sell at the bid")
    if run.dry:
        run.log(f"DRY RUN: would send {tag}-buy: buy 1 {q.symbol} limit {q.ask}, then {tag}-sell at the bid")
        return
    bq, bp, o = alpaca.limit_and_wait(q.symbol, 1, "buy", q.ask, f"{tag}-buy", wait, run.log)
    run.summary.append(f"test buy {q.symbol} limit {q.ask}: status {o['status']}, filled {bq} @ {bp}")
    if not bq:
        run.summary.append("no buy fill: order cancelled after the wait (the cancel path works)")
        return
    sold = 0
    for attempt in ("sell", "sell-r"):
        try:
            bid, ask = alpaca.quote(q.symbol)
        except alpaca.StaleQuote as e:
            run.summary.append(f"stale quote: {e}")
            continue
        if bid <= 0:
            run.summary.append(f"no bid for {q.symbol}")
            break
        sq, sp, o = alpaca.limit_and_wait(q.symbol, 1, "sell", bid, f"{tag}-{attempt}", wait, run.log)
        run.summary.append(f"test {attempt} limit {bid}: status {o['status']}, filled {sq} @ {sp}")
        if sq:
            sold = 1
            run.summary.append(f"round trip: bought @ {bp}, sold @ {sp}, P&L ${(sp - bp) * 100:.2f}")
            break
    left = alpaca_option_positions()
    run.summary.append(f"option positions after test: {left or 'none'}")
    if not sold:
        run.summary.append(f"WARNING {q.symbol} still held; sell it before tomorrow's runs "
                           "(the claude chain refuses to buy while it is open)")


def cmd_refresh(run: Run) -> None:
    cache = earnings.refresh(run.today, set(settings.watchlist()))
    print(f"{len(cache['events'])} watchlist reports {cache['from']}..{cache['to']}")
    for e in cache["events"]:
        print(f"  {e['date']} {e['ticker']} {e['when']}")
    if not run.dry:
        earnings.save(EARNINGS_PATH, cache)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("buy", "sell", "fed", "probe", "status", "report", "refresh-earnings", "test-trade"):
        sp = sub.add_parser(name)
        sp.add_argument("--dry-run", action="store_true", help="send no orders, write no files")
        sp.add_argument("--at", help="pretend it is this ET time, YYYY-MM-DDTHH:MM (dry-run only)")
        if name in ("buy", "sell", "fed", "test-trade"):
            sp.add_argument("--force-time", action="store_true", help="run outside the time window")
        if name in ("buy", "fed"):
            sp.add_argument("--event", help="claude chain: candidate id, ticker or kind to bet on")
            sp.add_argument("--direction", choices=["call", "put"], help="claude chain direction")
            sp.add_argument("--reason", help="one line of reasoning (required with --direction)")
        if name in ("probe", "test-trade"):
            sp.add_argument("--ticker", help="watchlist stock to quote (default: first on the list)")
    args = p.parse_args(argv)
    if getattr(args, "direction", None) and not getattr(args, "reason", None):
        p.error("--direction needs --reason")
    if getattr(args, "reason", None) and "\n" in args.reason:
        p.error("--reason must be one line")
    run = Run(args)
    cmds = {"buy": cmd_buy, "sell": cmd_sell, "fed": cmd_fed, "probe": cmd_probe, "status": cmd_status,
            "report": cmd_report, "refresh-earnings": cmd_refresh, "test-trade": cmd_test_trade}
    code = 0
    try:
        cmds[args.cmd](run)
    except net.AuthStop as e:
        print(f"STOP: HTTP {e.status} from {e.method} {e.url}\n{e.body}", file=sys.stderr)
        run.summary.append(f"STOP HTTP {e.status} {e.url}")
        code = 2
    except net.Unreachable as e:
        print(f"STOP: {e}", file=sys.stderr)
        run.summary.append(f"STOP {e}")
        code = 4
    finally:
        # Always save what was booked, even if a later step crashed: a real fill
        # must never be lost from the ledger.
        if args.cmd in ("buy", "sell", "fed", "test-trade"):
            run.save()
            print("\nSUMMARY\n" + ("\n".join(run.summary) or "nothing to do"))
    return code


if __name__ == "__main__":
    sys.exit(main())
