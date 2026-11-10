"""Read-only Upstox market data with the Analytics Token. GET requests only.

Nothing in this module can place, modify or cancel an order.
"""
import gzip
import json
import time
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode

from . import net
from .config import DATA_DIR, IST, env, now_ist

BASE = "https://api.upstox.com"
NIFTY = "NSE_INDEX|Nifty 50"
VIX = "NSE_INDEX|India VIX"
GLOBAL_FILE = "https://assets.upstox.com/market-quote/instruments/exchange/global.json.gz"

# What to look for in the global instruments file. First match wins.
GLOBAL_WANTED = {
    "gift": ["gift nifty", "sgx nifty"],
    "brent": ["bzusd", "brent"],
    "usdinr": ["usdinr", "usd inr", "usd/inr"],
    "spx": ["s&p 500", "s&p500", "s&p", "sp500", "sp 500", "us 500", "us500", "gspc", "spx"],
    "nasdaq": ["us tech 100", "nasdaq 100", "nasdaq"],
}
GLOBAL_DEFAULTS = {"gift": "GLOBAL_INDEX|SGX NIFTY", "brent": "GLOBAL_INDICATOR|BZUSD"}


class UpstoxError(Exception):
    pass


def _headers():
    tok = env("UPSTOX_ANALYTICS_TOKEN")
    if not tok:
        raise UpstoxError("UPSTOX_ANALYTICS_TOKEN is not set")
    return {"Authorization": "Bearer " + tok, "Accept": "application/json"}


def _get(path, params=None, timeout=12):
    url = BASE + path
    if params:
        url += "?" + urlencode(params)
    try:
        js = net.get_json(url, headers=_headers(), timeout=timeout)
    except net.NetError as e:
        raise UpstoxError(str(e))
    if not isinstance(js, dict) or js.get("status") != "success":
        raise UpstoxError("Upstox error on %s: %s" % (path.split("?")[0], str(js)[:200]))
    return js.get("data")


def _enc(key):
    return quote(key, safe="")


def _candles(data):
    """Upstox candle rows -> list of dicts sorted oldest first."""
    out = []
    for row in (data or {}).get("candles") or []:
        try:
            ts = datetime.fromisoformat(row[0])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=IST)
            out.append({"ts": ts.astimezone(IST), "date": ts.astimezone(IST).date().isoformat(),
                        "o": float(row[1]), "h": float(row[2]), "l": float(row[3]), "c": float(row[4])})
        except (ValueError, TypeError, IndexError):
            continue
    out.sort(key=lambda r: r["ts"])
    return out


def daily(key, frm, to):
    """Daily candles between two ISO dates (inclusive). v3 first, v2 as fallback."""
    try:
        return _candles(_get("/v3/historical-candle/%s/days/1/%s/%s" % (_enc(key), to, frm)))
    except UpstoxError:
        return _candles(_get("/v2/historical-candle/%s/day/%s/%s" % (_enc(key), to, frm)))


def hist_minutes(key, interval, frm, to):
    return _candles(_get("/v3/historical-candle/%s/minutes/%d/%s/%s" % (_enc(key), interval, to, frm)))


def intraday(key, interval=1):
    """Today's candles so far."""
    return _candles(_get("/v3/historical-candle/intraday/%s/minutes/%d" % (_enc(key), interval)))


def ltp(keys):
    """Last price and previous close for several instruments. {key: {last, prev}}"""
    data = _get("/v3/market-quote/ltp", {"instrument_key": ",".join(keys)}) or {}
    out = {}
    for name, row in data.items():
        if not isinstance(row, dict):
            continue
        k = row.get("instrument_token") or name.replace(":", "|", 1)
        last, prev = row.get("last_price"), row.get("cp")
        if last:
            out[k] = {"last": float(last), "prev": float(prev) if prev else None}
    return out


def day_ohlc(key):
    """Live day open/high/low/close from the quote API (used if candles lag)."""
    data = _get("/v2/market-quote/ohlc", {"instrument_key": key, "interval": "1d"}) or {}
    for row in data.values():
        o = (row or {}).get("ohlc") or {}
        if o.get("open"):
            return {"o": float(o["open"]), "h": float(o["high"]), "l": float(o["low"]),
                    "c": float(o.get("close") or row.get("last_price") or 0),
                    "last": float(row.get("last_price") or 0)}
    raise UpstoxError("No OHLC quote for %s" % key)


def is_trading_holiday(day):
    """True/False from Upstox, or None if the API gave no usable answer."""
    data = _get("/v2/market/holidays/%s" % day)
    if not data:
        return False
    for h in data if isinstance(data, list) else [data]:
        if not isinstance(h, dict):
            continue
        if str(h.get("date", ""))[:10] not in ("", day):
            continue
        closed = [str(x).upper() for x in (h.get("closed_exchanges") or [])]
        kind = str(h.get("holiday_type", "")).upper()
        if "NSE" in closed or (kind == "TRADING_HOLIDAY" and not closed):
            return True
    return False


def wait_for_open(max_wait_s=75):
    """The 09:15 open. Tries the 1-minute candle, then the live quote."""
    deadline = time.time() + max_wait_s
    last_err = "no candle yet"
    today = now_ist().date().isoformat()
    while True:
        try:
            bars = [b for b in intraday(NIFTY, 1) if b["date"] == today]
            if bars:
                return bars[0]["o"], "candle"
        except UpstoxError as e:
            last_err = str(e)
        try:
            q = day_ohlc(NIFTY)
            if q["o"] > 0:
                return q["o"], "quote"
        except UpstoxError as e:
            last_err = str(e)
        if time.time() >= deadline:
            raise UpstoxError("Could not get today's open: %s" % last_err)
        time.sleep(8)


def global_keys():
    """Instrument keys for GIFT Nifty, Brent, USD-INR, S&P 500 and Nasdaq.

    Read from Upstox's global instruments file and cached for a day.
    """
    cache = DATA_DIR / "cache" / "global_keys.json"
    try:
        if cache.exists() and time.time() - cache.stat().st_mtime < 86400:
            cached = json.loads(cache.read_text())
            if all(k in cached for k in GLOBAL_WANTED):  # refetch while something is still unmatched
                return cached
    except Exception:
        pass
    found = dict(GLOBAL_DEFAULTS)
    try:
        _, raw = net.request(GLOBAL_FILE, timeout=20)
        try:
            raw = gzip.decompress(raw)
        except OSError:
            pass
        rows = json.loads(raw.decode("utf-8", "replace"))
        for name, needles in GLOBAL_WANTED.items():
            hit = None
            for needle in needles:
                for r in rows:
                    hay = " ".join(str(r.get(f, "")) for f in ("name", "trading_symbol", "instrument_key", "short_name")).lower()
                    if needle in hay and r.get("instrument_key"):
                        hit = r["instrument_key"]
                        break
                if hit:
                    break
            if hit:
                found[name] = hit
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(found))
        # keep the list of available names next to the logs, so a missed match can be fixed remotely
        listing = [{f: r.get(f) for f in ("instrument_key", "name", "trading_symbol", "short_name") if r.get(f)} for r in rows]
        (DATA_DIR / "global_instruments.json").write_text(json.dumps({"matched": found, "available": listing}, indent=1))
    except Exception:
        pass  # defaults still let GIFT and Brent work
    return found


def global_snapshot():
    """{name: {key, last, prev, pct}} for the global instruments, best effort."""
    keys = global_keys()
    out, quotes = {}, {}
    try:
        quotes = ltp(list(keys.values()))
    except UpstoxError:
        pass
    today = now_ist().date()
    for name, key in keys.items():
        last = prev = None
        q = quotes.get(key)
        if q:
            last, prev = q["last"], q["prev"]
        if last is None or prev is None:
            try:
                d = daily(key, (today - timedelta(days=12)).isoformat(), today.isoformat())
                if len(d) >= 2:
                    if last is None:
                        # no live quote: latest daily close against the one before it
                        last, prev = d[-1]["c"], d[-2]["c"]
                    else:
                        # live quote but no previous close: last completed day
                        prev = d[-1]["c"] if d[-1]["date"] < today.isoformat() else d[-2]["c"]
            except UpstoxError:
                pass
        if last and prev:
            out[name] = {"key": key, "last": last, "prev": prev, "pct": round((last - prev) / prev * 100, 2)}
    return out


def option_snapshot(spot):
    """Nearest-expiry ATM straddle and put/call ratio. A feature only, never a vote."""
    contracts = _get("/v2/option/contract", {"instrument_key": NIFTY}) or []
    today = now_ist().date().isoformat()
    expiries = sorted({str(c.get("expiry"))[:10] for c in contracts if str(c.get("expiry", ""))[:10] >= today})
    if not expiries:
        raise UpstoxError("No option expiry found")
    expiry = expiries[0]
    chain = _get("/v2/option/chain", {"instrument_key": NIFTY, "expiry_date": expiry}) or []
    best, put_oi, call_oi = None, 0.0, 0.0
    for row in chain:
        strike = row.get("strike_price")
        ce = ((row.get("call_options") or {}).get("market_data") or {})
        pe = ((row.get("put_options") or {}).get("market_data") or {})
        call_oi += float(ce.get("oi") or 0)
        put_oi += float(pe.get("oi") or 0)
        if strike is None or not ce.get("ltp") or not pe.get("ltp"):
            continue
        if best is None or abs(strike - spot) < abs(best[0] - spot):
            best = (float(strike), float(ce["ltp"]), float(pe["ltp"]))
    if not best:
        raise UpstoxError("No ATM strike with prices")
    return {"expiry": expiry, "atm_strike": best[0], "straddle": round(best[1] + best[2], 1),
            "pcr": round(put_oi / call_oi, 2) if call_oi else None}
