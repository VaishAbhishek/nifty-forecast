"""A fake internet for offline tests: answers Upstox, RSS, LLM and Telegram URLs
with synthetic data shaped like the documented responses. No real network use."""
import gzip
import json
import os
import random
from datetime import datetime, timedelta, time as dtime
from email.utils import format_datetime
from urllib.parse import unquote
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
HOLIDAYS = {"2026-11-10"}
sent_messages = []
llm_mode = {"mode": "ok"}  # ok | fail | garbage


def now():
    return datetime.fromisoformat(os.environ["NF_FAKE_NOW"]).astimezone(IST)


def _weekdays(start, end):
    d = start
    while d <= end:
        if d.weekday() < 5 and d.isoformat() not in HOLIDAYS:
            yield d
        d += timedelta(days=1)


def _build():
    rnd = random.Random(7)
    days, px = [], 19500.0
    for d in _weekdays(datetime(2023, 6, 1).date(), datetime(2026, 11, 20).date()):
        o = px + rnd.gauss(0, 60)
        c = o + rnd.gauss(4, 130)
        h, l = max(o, c) + abs(rnd.gauss(0, 70)), min(o, c) - abs(rnd.gauss(0, 70))
        days.append({"date": d.isoformat(), "o": round(o, 2), "h": round(h, 2), "l": round(l, 2), "c": round(c, 2)})
        px = c
    return days


DAYS = _build()
BY_DATE = {d["date"]: d for d in DAYS}


def minute_bars(day):
    """A 375-bar path that matches the day's open/high/low/close exactly."""
    d = BY_DATE[day]
    rnd = random.Random(day)
    n = 375
    hi_at, lo_at = sorted(rnd.sample(range(20, n - 20), 2))
    if rnd.random() < 0.5:
        hi_at, lo_at = lo_at, hi_at
    pts = sorted([(0, d["o"]), (hi_at, d["h"]), (lo_at, d["l"]), (n - 1, d["c"])])
    closes = []
    for (i0, p0), (i1, p1) in zip(pts, pts[1:]):
        for i in range(i0, i1):
            closes.append(p0 + (p1 - p0) * (i - i0) / (i1 - i0))
    closes.append(d["c"])
    base = datetime.fromisoformat(day).replace(hour=9, minute=15, tzinfo=IST)
    bars, prev = [], d["o"]
    for i, c in enumerate(closes):
        bars.append([(base + timedelta(minutes=i)).isoformat(), round(prev, 2), round(max(prev, c), 2),
                     round(min(prev, c), 2), round(c, 2), 0, 0])
        prev = c
    return bars


def _daily_rows(key, frm, to):
    today = now().date().isoformat()
    closed = now().time() >= dtime(15, 30)
    rows = []
    for d in DAYS:
        if not (frm <= d["date"] <= to) or d["date"] > today or (d["date"] == today and not closed):
            continue
        if "VIX" in key:
            v = 12 + (hash(d["date"]) % 600) / 100.0
            rows.append([d["date"] + "T00:00:00+05:30", v, v + 0.5, v - 0.5, v, 0, 0])
        elif key.startswith("GLOBAL"):
            scale = {"GLOBAL_INDICATOR|BZUSD": 0.003, "GLOBAL_INDICATOR|USDINR": 0.0036}.get(key, 0.25)
            rows.append([d["date"] + "T00:00:00+05:30", d["o"] * scale, d["h"] * scale, d["l"] * scale, d["c"] * scale, 0, 0])
        else:
            rows.append([d["date"] + "T00:00:00+05:30", d["o"], d["h"], d["l"], d["c"], 0, 0])
    rows.reverse()  # Upstox returns newest first
    return rows


def _rss(source):
    t = now()
    items = [("Sensex, Nifty likely to open lower as crude oil jumps 3% on Middle East tension", 40),
             ("Wall Street tumbles overnight as tariff worries return; Nasdaq drops 1.8%", 300),
             ("FIIs net sold shares worth Rs 3,263 crore; DIIs bought Rs 5,283.9 crore on Monday", 600),
             ("Rupee weakens past 88 against the dollar", 120),
             ("Infosys Q2 net profit rises 6%, beats estimates", 700),
             ("Bollywood star buys a sea-facing flat", 50),
             ("%s old story about markets" % source, 60 * 24 * 5)]
    if now().time() >= dtime(9, 30):
        items.append(("RBI governor signals rate cut may come sooner; markets rally", 5))
    xml = "".join("<item><title>%s</title><link>http://x/%d</link><pubDate>%s</pubDate></item>"
                  % (title.replace("&", "&amp;"), i, format_datetime(t - timedelta(minutes=age)))
                  for i, (title, age) in enumerate(items))
    return ('<?xml version="1.0"?><rss><channel><title>%s</title>%s</channel></rss>' % (source, xml)).encode()


def request(url, method="GET", headers=None, data=None, timeout=12, retries=1):
    today = now().date().isoformat()
    u = unquote(url)

    def ok(payload):
        return 200, json.dumps({"status": "success", "data": payload}).encode()

    if "api.upstox.com" in url:
        assert method == "GET", "the agent must only ever GET from Upstox"
        assert (headers or {}).get("Authorization", "").startswith("Bearer "), "missing token header"
        if "/historical-candle/intraday/" in u:
            bars = minute_bars(today) if today in BY_DATE else []
            cutoff = now().replace(second=0, microsecond=0)
            return ok({"candles": [b for b in reversed(bars) if datetime.fromisoformat(b[0]) < cutoff]})
        if "/v3/historical-candle/" in u:
            path = u.split("/v3/historical-candle/")[1].split("/")
            key, unit, interval, to, frm = path[0], path[1], path[2], path[3], path[4]
            if unit == "days":
                return ok({"candles": _daily_rows(key, frm, to)})
            rows = []
            for d in DAYS:
                if frm <= d["date"] <= to and d["date"] < today:
                    bars = minute_bars(d["date"])
                    for j in range(0, 375, 30):
                        chunk = bars[j:j + 30]
                        rows.append([chunk[0][0], chunk[0][1], max(b[2] for b in chunk), min(b[3] for b in chunk), chunk[-1][4], 0, 0])
            rows.reverse()
            return ok({"candles": rows})
        if "/v2/market/holidays/" in u:
            day = u.rsplit("/", 1)[1]
            return ok([{"date": day, "holiday_type": "TRADING_HOLIDAY", "closed_exchanges": ["NSE", "BSE"]}] if day in HOLIDAYS else [])
        if "/v3/market-quote/ltp" in u:
            out = {}
            for key in u.split("instrument_key=")[1].split(","):
                rows = _daily_rows(key, "2026-01-01", today)
                out[key.replace("|", ":")] = {"last_price": rows[0][4] * 1.004, "instrument_token": key, "cp": rows[0][4]}
            return ok(out)
        if "/v2/market-quote/ohlc" in u:
            bars = minute_bars(today)
            return ok({"NSE_INDEX:Nifty 50": {"ohlc": {"open": bars[0][1], "high": bars[0][2], "low": bars[0][3], "close": bars[0][4]},
                                              "last_price": bars[0][4], "instrument_token": "NSE_INDEX|Nifty 50"}})
        if "/v2/option/contract" in u:
            exp = (now().date() + timedelta(days=6)).isoformat()
            return ok([{"expiry": exp, "strike_price": 24000}, {"expiry": "2026-12-29", "strike_price": 24000}])
        if "/v2/option/chain" in u:
            spot = minute_bars(today)[0][1]
            atm = round(spot / 50) * 50
            return ok([{"strike_price": atm + k * 50,
                        "call_options": {"market_data": {"ltp": max(5, 120 - k * 30), "oi": 1000 + k}},
                        "put_options": {"market_data": {"ltp": max(5, 115 + k * 30), "oi": 1200 - k}}} for k in range(-3, 4)])
        raise AssertionError("unexpected Upstox URL " + u)
    if "assets.upstox.com" in url:
        rows = [{"instrument_key": "GLOBAL_INDEX|SGX NIFTY", "name": "GIFT NIFTY"},
                {"instrument_key": "GLOBAL_INDICATOR|BZUSD", "name": "Brent Crude"},
                {"instrument_key": "GLOBAL_INDICATOR|USDINR", "name": "USD INR"},
                {"instrument_key": "GLOBAL_INDEX|SPX", "name": "S&P 500"},
                {"instrument_key": "GLOBAL_INDEX|NDX", "name": "US Tech 100"}]
        return 200, gzip.compress(json.dumps(rows).encode())
    if "api.telegram.org" in url:
        assert "/sendMessage" in url, "only sendMessage is allowed, never getUpdates"
        assert len(data["text"]) <= 4096
        sent_messages.append(data["text"])
        return 200, b'{"ok": true}'
    if "api.anthropic.com" in url:
        if llm_mode["mode"] == "fail":
            from forecast.net import NetError
            raise NetError("HTTP 529 overloaded")
        if llm_mode["mode"] == "garbage":
            return 200, json.dumps({"content": [{"type": "text", "text": "Sorry, I cannot help."}]}).encode()
        prompt = data["messages"][0]["content"]
        n = sum(1 for line in prompt.split("Headlines:")[1].splitlines() if line.strip())
        items = [{"id": i, "relevant": True, "catalyst": "oil_geo", "direction": -1, "magnitude": 2} for i in range(n)]
        reply = {"items": items, "overall": {"summary": "Global cues are weak.", "key_risk": "A reversal if crude cools.",
                                             "binary_event_today": None, "fii_net_cr": -3263, "dii_net_cr": 5283.9}}
        return 200, json.dumps({"content": [{"type": "text", "text": "```json\n%s\n```" % json.dumps(reply)}]}).encode()
    # anything else is an RSS feed
    return 200, _rss(url.split("/")[2])
