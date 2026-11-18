"""Momentum jobs on a fake internet: data -> pre-open -> checks -> end of day, plus the pure calculations.

Run:  python3 -m unittest discover -s tests -v
"""
import gzip
import json
import os
import random
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, time as dtime
from pathlib import Path
from urllib.parse import unquote_plus as unquote

import test_offline  # noqa: F401  sets the fake environment the forecast modules are imported under
import fake_net
from forecast import net, store, upstox as ux
from momentum import api, brief, calc, run

IST = fake_net.IST
N = 60
SYMS = ["STOCK%02d" % i for i in range(N)]
EQ = {s: "NSE_EQ|INE%04dA01" % i for i, s in enumerate(SYMS)}
FUT = {s: "NSE_FO|%d" % (50000 + i) for i, s in enumerate(SYMS)}
BY_KEY = dict([(v, k) for k, v in EQ.items()] + [(v, k) for k, v in FUT.items()])
NIFTY_FUT = "NSE_FO|49999"


def scale(sym):
    return 0.01 + 0.002 * SYMS.index(sym)


def vol(sym, day):
    r = random.Random(sym + day)
    return int(1e6 * (0.6 + r.random()) * (4 if r.random() < 0.05 else 1))


def stock_days(sym):
    s = scale(sym)
    return [{"date": d["date"], "o": d["o"] * s, "h": d["h"] * s, "l": d["l"] * s, "c": d["c"] * s, "v": vol(sym, d["date"])}
            for d in fake_net.DAYS]


def stock_bars(sym, day):
    s = scale(sym)
    return [[b[0], b[1] * s, b[2] * s, b[3] * s, b[4] * s, 1000 + (i % 7) * 100, 0] for i, b in enumerate(fake_net.minute_bars(day))]


def instruments_file():
    ms = lambda d: int(datetime.fromisoformat(d).replace(hour=15, tzinfo=IST).timestamp() * 1000)  # noqa: E731
    rows = [{"segment": "NSE_INDEX", "instrument_type": "INDEX", "instrument_key": "NSE_INDEX|Nifty 50", "name": "Nifty 50"}]
    for s in SYMS:
        rows.append({"segment": "NSE_EQ", "instrument_type": "EQ", "instrument_key": EQ[s], "trading_symbol": s, "name": s + " LTD"})
        for exp, key in (("2026-12-29", FUT[s] + "9"), ("2026-11-24", FUT[s]), ("2026-10-27", FUT[s] + "8")):
            rows.append({"segment": "NSE_FO", "instrument_type": "FUT", "instrument_key": key, "expiry": ms(exp), "lot_size": 500,
                         "underlying_key": EQ[s], "underlying_symbol": s, "underlying_type": "EQUITY", "name": s + " LTD"})
        rows.append({"segment": "NSE_FO", "instrument_type": "CE", "instrument_key": FUT[s] + "7", "expiry": ms("2026-11-24"),
                     "underlying_key": EQ[s], "underlying_symbol": s, "underlying_type": "EQUITY", "strike_price": 100.0})
    rows.append({"segment": "NSE_FO", "instrument_type": "FUT", "instrument_key": NIFTY_FUT, "expiry": ms("2026-11-24"),
                 "underlying_key": "NSE_INDEX|Nifty 50", "underlying_symbol": "NIFTY", "underlying_type": "INDEX"})
    return gzip.compress(json.dumps(rows).encode())


def quote_row(key, now):
    today = now.date().isoformat()
    sym = BY_KEY.get(key)
    s = scale(sym) if sym else 1.0
    past = [d for d in fake_net.DAYS if d["date"] < today]
    prev = past[-1]["c"] * s
    row = {"instrument_token": key, "symbol": sym or "NIFTY", "last_price": prev, "prev_close_price": prev, "volume": 0,
           "ohlc": {"open": past[-1]["o"] * s, "high": past[-1]["h"] * s, "low": past[-1]["l"] * s, "close": prev,
                    "ts": int(datetime.fromisoformat(past[-1]["date"]).replace(tzinfo=IST).timestamp() * 1000)},
           "last_trade_time": str(int(datetime.fromisoformat(past[-1]["date"]).replace(hour=15, tzinfo=IST).timestamp() * 1000)),
           "indicative_equilibrium_price": 0}
    if today in fake_net.BY_DATE and dtime(9, 0) <= now.time() < dtime(9, 15):
        row["indicative_equilibrium_price"] = fake_net.BY_DATE[today]["o"] * s
    if today in fake_net.BY_DATE and now.time() >= dtime(9, 15):
        bars = [b for b in fake_net.minute_bars(today) if datetime.fromisoformat(b[0]) < now.replace(second=0, microsecond=0)] \
            or fake_net.minute_bars(today)[:1]
        row.update(last_price=bars[-1][4] * s, volume=sum(1000 + (i % 7) * 100 for i in range(len(bars))) * (5 if sym == "STOCK07" else 1),
                   last_trade_time=str(int(now.timestamp() * 1000)),
                   ohlc={"open": bars[0][1] * s, "high": max(b[2] for b in bars) * s, "low": min(b[3] for b in bars) * s,
                         "close": bars[-1][4] * s, "ts": int(now.replace(hour=0, minute=0).timestamp() * 1000)})
    if key.startswith("NSE_FO|"):
        i = SYMS.index(sym) if sym else 0
        row.update(oi=100000 + i * 900, previous_oi=100000)
    return row


def request(url, method="GET", headers=None, data=None, timeout=12, retries=1):
    """Answers the momentum-specific URLs, and hands everything else to the forecast agent's fake internet."""
    u = unquote(url)
    now = fake_net.now()
    today = now.date().isoformat()

    def ok(payload):
        return 200, json.dumps({"status": "success", "data": payload}).encode()

    if url.endswith("/NSE.json.gz"):
        return 200, instruments_file()
    if "api.upstox.com" in url:
        assert method == "GET", "momentum must only ever GET from Upstox"
        assert (headers or {}).get("Authorization", "").startswith("Bearer ")
        if "/market-quote/quotes" in u:
            keys = u.split("instrument_key=")[1].split(",")
            assert len(keys) <= api.QUOTE_CHUNK
            return ok({k.replace("|", ":"): quote_row(k, now) for k in keys})
        if "/v2/market/fii" in u or "/v2/market/dii" in u:
            ts = int(now.timestamp() * 1000) - 86400000
            rec = {"time_stamp": ts, "buy_amount": 9000.5, "sell_amount": 11000.0, "total_long_contracts": 300, "total_short_contracts": 700}
            segs = [p.split("=")[1] for p in u.split("?")[1].split("&") if p.startswith("data_type=")]
            return ok({seg: [rec, dict(rec, time_stamp=ts - 86400000, buy_amount=1.0)] for seg in segs})
        if "/historical-candle/" in u:
            intr = "/historical-candle/intraday/" in u
            path = u.split("/historical-candle/intraday/" if intr else "/v3/historical-candle/")[1].split("/")
            sym = BY_KEY.get(path[0])
            if sym and intr:
                bars = stock_bars(sym, today)
                cutoff = now.replace(second=0, microsecond=0)
                return ok({"candles": [b for b in reversed(bars) if datetime.fromisoformat(b[0]) < cutoff]})
            if sym and path[1] == "days":
                to, frm = path[3], path[4]
                closed = now.time() >= dtime(15, 30)
                rows = [[d["date"] + "T00:00:00+05:30", d["o"], d["h"], d["l"], d["c"], d["v"], 0] for d in stock_days(sym)
                        if frm <= d["date"] <= to and (d["date"] < today or (d["date"] == today and closed))]
                return ok({"candles": rows[::-1]})
            if sym and path[1] == "minutes":
                to, frm = path[3], path[4]
                rows = []
                for d in fake_net.DAYS:
                    if frm <= d["date"] <= to and d["date"] < today:
                        bars = stock_bars(sym, d["date"])
                        for j in range(0, 375, 5):
                            c = bars[j:j + 5]
                            rows.append([c[0][0], c[0][1], max(b[2] for b in c), min(b[3] for b in c), c[-1][4], sum(b[5] for b in c), 0])
                return ok({"candles": rows[::-1]})
    status, body = fake_net.request(url, method=method, headers=headers, data=data, timeout=timeout, retries=retries)
    if "/v3/market-quote/ltp" in u and "SGX NIFTY" in u:
        js = json.loads(body)  # put GIFT Nifty on the index's own scale, 0.4% above the last close
        prev = [d for d in fake_net.DAYS if d["date"] < today][-1]["c"]
        js["data"]["GLOBAL_INDEX:SGX NIFTY"].update(last_price=prev * 1.004, cp=prev)
        body = json.dumps(js).encode()
    return status, body


def at(ts):
    os.environ["NF_FAKE_NOW"] = ts


class Calculations(unittest.TestCase):
    def bars(self, *closes):
        out, prev = [], closes[0]
        for c in closes:
            out.append({"o": prev, "h": max(prev, c), "l": min(prev, c), "c": c})
            prev = c
        return out

    def test_walk(self):
        b = self.bars(100, 101, 103, 106, 104)
        self.assertEqual(calc.walk(b, "UP", 102, 99.5, 105), {"status": "target", "entry": 102.0, "r": 1.2})
        self.assertEqual(calc.walk(b, "UP", 102, 99.5), {"status": "closed", "entry": 102.0, "r": 0.8})
        self.assertEqual(calc.walk(self.bars(100, 103, 100, 99), "UP", 102, 99.5), {"status": "stopped", "entry": 102.0, "r": -1.0})
        self.assertEqual(calc.walk(self.bars(100, 99, 103), "UP", 102, 99.5)["status"], "cancelled")
        self.assertEqual(calc.walk(self.bars(100, 100.5, 101), "UP", 102, 99)["status"], "no_trigger")
        self.assertEqual(calc.walk(b, "UP", 100, 102)["status"], "bad_levels")
        self.assertEqual(calc.walk(b, "UP", None, 99)["status"], "no_levels")
        self.assertEqual(calc.walk([], "UP", 102, 99)["status"], "no_bars")
        d = self.bars(100, 99, 97, 96)
        self.assertEqual(calc.walk(d, "DOWN", 98, 100.5, 96.5), {"status": "target", "entry": 98.0, "r": 0.6})
        self.assertEqual(calc.walk(d, "DOWN", 98, 99.5)["status"], "cancelled")
        # a gap through the confirm level is filled at the open, not at the level
        g = [{"o": 105, "h": 106, "l": 104.5, "c": 106}, {"o": 106, "h": 108, "l": 106, "c": 108}]
        r = calc.walk(g, "UP", 102, 100)
        self.assertEqual(r["entry"], 105.0)
        self.assertAlmostEqual(r["r"], 3 / 5, places=2)

    def test_small_helpers(self):
        self.assertEqual(calc.gap_verdict("DOWN", -2.4, 2.5), "mostly priced in")
        self.assertEqual(calc.gap_verdict("DOWN", -1.0, 2.5), "partly priced in")
        self.assertEqual(calc.gap_verdict("UP", -1.0, 2.5), "gapping against")
        self.assertEqual(calc.gap_verdict("UP", 0.2, 2.5), "valid")
        self.assertEqual(calc.gap_verdict("UP", None, 2.5), "unknown")
        self.assertEqual(calc.oi_class(1.2, 6.0), "long build-up")
        self.assertEqual(calc.oi_class(-1.2, 6.0), "short build-up")
        self.assertEqual(calc.oi_class(1.2, -6.0), "short covering")
        self.assertEqual(calc.oi_class(-1.2, -6.0), "long unwinding")
        self.assertIsNone(calc.oi_class(1.2, 1.0))
        self.assertEqual(calc.needed_for_95(25), 18)
        self.assertEqual(calc.needed_for_95(10), 9)
        self.assertIsNone(calc.needed_for_95(4))
        self.assertEqual(calc.bucket_of(1.5), "1-2")
        self.assertEqual(calc.bucket_of(7), "4+")
        self.assertIsNone(calc.bucket_of(0.2))

    def test_features_and_gaps(self):
        days = [{"date": "2026-01-%02d" % (i + 1), "o": 100 + i, "h": 102 + i, "l": 99 + i, "c": 101 + i, "v": 1000} for i in range(30)]
        days[-1].update(c=140, h=141, v=5000)
        f = calc.features(days)
        self.assertEqual(f["breakout"], "up")
        self.assertEqual(f["vol_ratio"], 5.0)
        self.assertGreater(f["move_atr"], 2.5)
        self.assertIsNone(calc.features(days[:10]))
        ev = calc.gap_events([{"o": 100, "h": 101, "l": 99, "c": 100}, {"o": 102, "h": 104, "l": 101.5, "c": 103.5},
                              {"o": 101, "h": 103.6, "l": 100, "c": 100.5}])
        self.assertEqual([(e[0], e[3]) for e in ev], [("up", False), ("down", True)])
        t = calc.gap_table(ev)
        self.assertEqual(t["up 2-4"]["cont"], 1.0)
        self.assertEqual(t["down 2-4"]["fill"], 1.0)

    def test_stream_parser(self):
        rows = [{"a": i, "t": "x{y}" * (i % 3), "n": {"k": [1, 2, {"z": i}]}} for i in range(200)]
        raw = json.dumps(rows).encode()
        for payload in (gzip.compress(raw), raw):
            for chunk in (7, 64, 100000):
                self.assertEqual(list(api.iter_objects(payload, chunk)), rows)

    def test_scorecard(self):
        rows = [{"tier": "best", "conviction": "high", "horizon": "intraday", "direction": "UP", "evidence": ["catalyst", "volume"],
                 "right": True, "ret": 1.0, "alpha": 0.5, "trade": {"status": "target", "r": 2.0}},
                {"tier": "list", "conviction": "low", "horizon": "swing", "direction": "DOWN", "evidence": ["volume"],
                 "right": False, "ret": -0.5, "alpha": -0.2, "trade": {"status": "no_trigger"}, "ret_5d": 3.0}]
        sc = calc.scorecard(rows)
        self.assertEqual(sc["all"]["all"]["n"], 2)
        self.assertEqual(sc["all"]["all"]["trades"], 1)
        self.assertEqual(sc["evidence"]["volume"]["n"], 2)
        self.assertEqual(sc["tier"]["best"]["hit"], 1.0)
        self.assertEqual(sc["horizon"]["swing"]["n_5d"], 1)
        self.assertIn("By evidence", brief.render_scorecard(sc, None, 1))


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="nf_mom_")
        cls.saved = (net.request, store.DATA_DIR, ux.DATA_DIR, api.DATA_DIR, os.environ.get("NF_FAKE_NOW"))
        net.request = request
        for mod in (store, ux, api):
            mod.DATA_DIR = Path(cls.tmp)
        fake_net.sent_messages.clear()

    @classmethod
    def tearDownClass(cls):
        net.request, store.DATA_DIR, ux.DATA_DIR, api.DATA_DIR, fake_now = cls.saved
        if fake_now:
            os.environ["NF_FAKE_NOW"] = fake_now
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def read(self, name):
        return json.loads((Path(self.tmp) / "momentum" / name).read_text())

    def day(self, day, first):
        sent = fake_net.sent_messages
        at(day + "T08:10:05+05:30")
        self.assertEqual(run.main(["data"]), 0)
        d = self.read("latest.json")
        self.assertEqual(d["date"], day)
        self.assertEqual(len(d["stocks"]), N)
        self.assertEqual(d["failed"], [])
        self.assertTrue(d["gap_table"])
        self.assertEqual(d["market"]["index_gap"]["nifty_fut"] > 0, True)
        self.assertEqual(d["oi_source"].startswith("pre-market" if first else "end-of-day"), True)
        text = (Path(self.tmp) / "momentum" / "brief" / ("%s.md" % day)).read_text()
        for needle in ("## Market", "Focus list", "What past gaps did next", "Regime"):
            self.assertIn(needle, text)
        some = d["stocks"]["STOCK07"]
        for k in ("chg1", "vol_ratio", "atr_pct", "move_atr", "beta", "est_gap", "oi_chg", "from_52w_high"):
            self.assertIsNotNone(some.get(k), k)

        # the morning report logs its picks; levels sit just beyond the open so both paths get exercised
        o = fake_net.BY_DATE[day]["o"]
        picks = {"date": day, "picks": [
            {"symbol": "stock07", "direction": "UP", "horizon": "intraday", "tier": "best", "conviction": "High",
             "evidence": ["catalyst", "volume"], "confirm": round(o * scale("STOCK07") * 1.001, 2), "cancel": round(o * scale("STOCK07") * 0.995, 2)},
            {"symbol": "STOCK11", "direction": "SHORT", "horizon": "swing", "tier": "list", "conviction": "Medium", "evidence": "oi"},
            {"symbol": "NOTREAL", "direction": "UP"}, {"symbol": "STOCK12", "direction": "sideways"}]}
        (Path(self.tmp) / "momentum" / "picks").mkdir(parents=True, exist_ok=True)
        (Path(self.tmp) / "momentum" / "picks" / ("%s.json" % day)).write_text(json.dumps(picks))

        n = len(sent)
        at(day + "T09:07:20+05:30")
        self.assertEqual(run.main(["preopen"]), 0)
        self.assertEqual(len(sent), n + 1)
        self.assertIn("Pre-open gaps", sent[-1])
        self.assertIn("indicative prices", sent[-1])
        self.assertIn("STOCK07", sent[-1])
        g = self.read("gaps/%s.json" % day)
        self.assertEqual(len(g["all"]), N)
        want = calc.pct(fake_net.BY_DATE[day]["o"], [x for x in fake_net.DAYS if x["date"] < day][-1]["c"])
        self.assertAlmostEqual(g["all"]["STOCK07"]["gap"], want, places=1)
        self.assertAlmostEqual(g["index_gap"], want, places=1)

        for label, clock in (("5", "09:20:15"), ("30", "09:47:00")):
            at(day + "T%s+05:30" % clock)
            self.assertEqual(run.main(["check" + label]), 0)
            self.assertIn("%s-minute check" % label, sent[-1])
            c = self.read("checks/%s_%s.json" % (day, label))
            self.assertEqual([p["symbol"] for p in c["picks"]], ["STOCK07", "STOCK11"])
            self.assertEqual(c["picks"][1]["direction"], "DOWN")
            self.assertEqual([r["symbol"] for r in c["in_play"]], ["STOCK07"])  # the one stock given five times its volume

        at(day + "T16:05:00+05:30")
        self.assertEqual(run.main(["eod"]), 0)
        self.assertIn("Momentum picks: results", sent[-1])
        rows = [r for r in store.load("momentum/scores.jsonl") if r["date"] == day]
        self.assertEqual(sorted(r["symbol"] for r in rows), ["STOCK07", "STOCK11"])
        a = next(r for r in rows if r["symbol"] == "STOCK07")
        self.assertIn(a["trade"]["status"], ("target", "stopped", "closed", "cancelled", "no_trigger"))
        self.assertEqual(a["right"], fake_net.BY_DATE[day]["c"] > fake_net.BY_DATE[day]["o"])
        self.assertAlmostEqual(a["alpha"], 0.0, places=1)  # the fake stocks are scaled copies of the index
        self.assertEqual(next(r for r in rows if r["symbol"] == "STOCK11")["trade"]["status"], "not_intraday")
        self.assertEqual(run.main(["eod"]), 0)  # a second run must not score twice
        self.assertEqual(len([r for r in store.load("momentum/scores.jsonl") if r["date"] == day]), 2)
        self.assertEqual(self.read("eod_latest.json")["date"], day)
        ip = [r for r in store.load("momentum/inplay.jsonl") if r["date"] == day]
        self.assertEqual(len(ip), 1)
        self.assertIsNotNone(ip[0]["trade"])

    def test_1_days(self):
        days = ["2026-11-11", "2026-11-12", "2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19"]
        for i, day in enumerate(days):
            self.day(day, first=(i == 0))
        rows = store.load("momentum/scores.jsonl")
        swing = [r for r in rows if r["symbol"] == "STOCK11"]
        self.assertEqual([r.get("ret_5d") is not None for r in swing], [True, True, True, False, False, False, False])
        sc = self.read("scorecard.json")
        self.assertEqual(sc["picks"]["all"]["all"]["n"], 14)
        self.assertEqual(sc["sessions"], 7)
        self.assertEqual(sc["picks"]["evidence"]["catalyst"]["n"], 7)
        self.assertEqual(sc["in_play"]["n"], 7)
        self.assertIn("In-play", (Path(self.tmp) / "momentum" / "scorecard.md").read_text())

    def test_2_skips_and_windows(self):
        n = len(fake_net.sent_messages)
        at("2026-11-14T08:10:05+05:30")  # Saturday
        self.assertEqual(run.main(["data"]), 0)
        at("2026-11-10T09:07:20+05:30")  # holiday
        self.assertEqual(run.main(["preopen"]), 0)
        at("2026-11-12T12:00:00+05:30")  # outside every window
        for cmd in ("data", "preopen", "check5", "check30", "eod"):
            self.assertEqual(run.main([cmd]), 0)
        self.assertEqual(len(fake_net.sent_messages), n)
        self.assertEqual(store.read_json("status.json")["momentum_preopen"]["skipped"], "NSE holiday (Upstox)")

    def test_3_no_secrets_and_selftest(self):
        at("2026-11-12T08:20:00+05:30")
        self.assertEqual(run.main(["selftest"]), 0)
        st = store.read_json("status.json")["momentum_selftest"]
        self.assertTrue(st["ok"], st)
        for p in Path(self.tmp).rglob("*"):
            if p.is_file():
                body = p.read_text(errors="replace")
                for secret in ("tok-SECRET-123456", "999:SECRET-BOT-TOKEN", "sk-SECRET-KEY-abcdef"):
                    self.assertNotIn(secret, body, p)
        for m in fake_net.sent_messages:
            self.assertNotIn("SECRET", m)

    def test_4_failure_is_reported(self):
        at("2026-11-12T09:07:20+05:30")
        n = len(fake_net.sent_messages)
        real = api.quotes
        api.quotes = lambda keys: (_ for _ in ()).throw(api.UpstoxError("HTTP 500 for quotes"))
        try:
            self.assertEqual(run.main(["preopen"]), 1)
        finally:
            api.quotes = real
        self.assertIn("preopen run failed", fake_net.sent_messages[-1])
        self.assertEqual(len(fake_net.sent_messages), n + 1)
        self.assertFalse(store.read_json("status.json")["momentum_preopen"]["ok"])


class Flows(unittest.TestCase):
    def test_single_day_from_walks_back(self):
        # The live API answers with only the day named in 'from'; the newest day with data is 2 weekdays back.
        days = list(api._flow_days())
        have = days[2]
        calls = []

        def fake_get(path, params=None, timeout=15):
            frm = dict(params)["from"]
            calls.append((path, frm))
            if frm != have:
                return {}
            ts = int(datetime.fromisoformat(have + "T00:00:00+05:30").timestamp() * 1000)
            rec = {"time_stamp": ts, "buy_amount": 10.0, "sell_amount": 4.0,
                   "total_long_contracts": 1, "total_short_contracts": 3}
            return {seg: [rec] for k, seg in params if k == "data_type"}

        old = api._get
        api._get = fake_get
        try:
            f = api.flows()
        finally:
            api._get = old
        for name in ("fii_cash", "fii_index_fut", "fii_stock_fut", "dii_cash"):
            self.assertEqual(f[name]["date"], have)
            self.assertEqual(f[name]["net"], 6.0)
        self.assertEqual(f["fii_index_fut"]["long_share"], 0.25)
        self.assertEqual(len(calls), 6)


if __name__ == "__main__":
    unittest.main()
