"""Read-only Upstox calls used by the momentum jobs. GET requests only.

Reuses the forecast agent's HTTP helper and token handling. Every function
here is best effort: callers wrap them and record failures in the output
files, so a changed API shape shows up in status.json instead of a crash.
"""
import codecs
import json
import time
import zlib
from datetime import datetime, timedelta
from urllib.parse import quote, urlencode

from forecast import net
from forecast import upstox as ux
from forecast.config import DATA_DIR, IST, now_ist

NSE_FILE = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
NIFTY = ux.NIFTY
VIX = ux.VIX
PACE_S = 0.3          # pause between per-stock calls, far below the documented limits
QUOTE_CHUNK = 100     # instrument keys per quote call (the documented limit is 500)

UpstoxError = ux.UpstoxError


def _get(path, params=None, timeout=15):
    url = ux.BASE + path
    if params:
        url += "?" + urlencode(params, doseq=True)
    try:
        js = net.get_json(url, headers=ux._headers(), timeout=timeout)
    except net.NetError as e:
        raise UpstoxError(str(e))
    if not isinstance(js, dict) or js.get("status") != "success":
        raise UpstoxError("Upstox error on %s: %s" % (path, str(js)[:200]))
    return js.get("data")


def _enc(key):
    return quote(key, safe="")


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _candles(data):
    """Upstox candle rows -> dicts with volume and open interest, oldest first."""
    out = []
    for row in (data or {}).get("candles") or []:
        try:
            ts = datetime.fromisoformat(row[0])
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=IST)
            ts = ts.astimezone(IST)
            out.append({"ts": ts, "date": ts.date().isoformat(), "o": float(row[1]), "h": float(row[2]),
                        "l": float(row[3]), "c": float(row[4]),
                        "v": float(row[5]) if len(row) > 5 and row[5] is not None else 0.0,
                        "oi": float(row[6]) if len(row) > 6 and row[6] is not None else 0.0})
        except (ValueError, TypeError, IndexError):
            continue
    out.sort(key=lambda r: r["ts"])
    return out


def daily(key, frm, to):
    try:
        return _candles(_get("/v3/historical-candle/%s/days/1/%s/%s" % (_enc(key), to, frm)))
    except UpstoxError:
        return _candles(_get("/v2/historical-candle/%s/day/%s/%s" % (_enc(key), to, frm)))


def minutes(key, interval, frm, to):
    return _candles(_get("/v3/historical-candle/%s/minutes/%d/%s/%s" % (_enc(key), interval, to, frm)))


def intraday(key, interval=1):
    return _candles(_get("/v3/historical-candle/intraday/%s/minutes/%d" % (_enc(key), interval)))


def _to_date(x):
    """Epoch (s or ms) or ISO text -> IST date string, or None."""
    if x in (None, "", 0, "0"):
        return None
    try:
        v = float(x)
        if v > 1e11:
            v /= 1000.0
        return datetime.fromtimestamp(v, IST).date().isoformat()
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(str(x)).astimezone(IST).date().isoformat()
        except ValueError:
            return str(x)[:10] or None


def _quote_row(row):
    o = row.get("ohlc") or {}
    last = _f(row.get("last_price"))
    prev = _f(row.get("prev_close_price"))
    if not prev and last is not None and _f(row.get("net_change")) is not None:
        prev = last - _f(row.get("net_change"))  # v2 has no previous close field
    return {"symbol": row.get("symbol"), "last": last, "prev": prev,
            "open": _f(o.get("open")), "high": _f(o.get("high")), "low": _f(o.get("low")),
            "ohlc_date": _to_date(o.get("ts")),
            "volume": _f(row.get("volume")), "oi": _f(row.get("oi")), "prev_oi": _f(row.get("previous_oi")),
            "iep": _f(row.get("indicative_equilibrium_price")),
            "traded_on": _to_date(row.get("last_trade_time")),
            "year_high": _f(row.get("year_high")), "year_low": _f(row.get("year_low"))}


def quotes(keys):
    """Full market quotes for many instruments. {instrument_key: row}. Missing keys are simply absent."""
    out, errors = {}, []
    keys = list(dict.fromkeys(keys))
    for i in range(0, len(keys), QUOTE_CHUNK):
        chunk = keys[i:i + QUOTE_CHUNK]
        data = None
        for path in ("/v3/market-quote/quotes", "/v2/market-quote/quotes"):
            try:
                data = _get(path, {"instrument_key": ",".join(chunk)})
                break
            except UpstoxError as e:
                errors.append(str(e)[:160])
        for name, row in (data or {}).items():
            if isinstance(row, dict):
                out[row.get("instrument_token") or name.replace(":", "|", 1)] = _quote_row(row)
        if i + QUOTE_CHUNK < len(keys):
            time.sleep(PACE_S)
    if not out and errors:
        raise UpstoxError(errors[-1])
    return out


def iter_objects(raw, chunk=65536):
    """Yield the objects of a (gzipped) JSON array without loading it whole.

    The NSE instruments file holds every option contract, so parsing it in one
    go would not fit in this service's memory cap on a small VM.
    """
    try:
        d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        first = d.decompress(raw[:chunk])
    except zlib.error:
        d, first = None, raw[:chunk]
    dec = codecs.getincrementaldecoder("utf-8")("replace")
    jd = json.JSONDecoder()
    buf = dec.decode(first)
    i = chunk
    while True:
        pos = 0
        while True:
            j = buf.find("{", pos)
            if j < 0:
                buf = ""
                break
            try:
                obj, end = jd.raw_decode(buf, j)
            except ValueError:
                buf = buf[j:]
                break
            yield obj
            pos = end
        if i >= len(raw):
            break
        piece = raw[i:i + chunk]
        i += chunk
        buf += dec.decode(d.decompress(piece) if d else piece)


def load_universe(force=False):
    """F&O stocks from the instruments file, cached per day.

    {"date", "nifty_fut", "stocks": {SYMBOL: {"eq", "fut", "lot", "name", "expiry"}}}
    """
    cache = DATA_DIR / "cache" / "momentum_universe.json"
    today = now_ist().date().isoformat()
    old = None
    try:
        old = json.loads(cache.read_text())
        if not force and old.get("date") == today and old.get("stocks"):
            return old
    except Exception:
        pass
    try:
        _, raw = net.request(NSE_FILE, timeout=60)
        stocks, nifty_fut = {}, None
        for r in iter_objects(raw):
            if r.get("instrument_type") != "FUT" or r.get("segment") != "NSE_FO":
                continue
            exp = _to_date(r.get("expiry"))
            if not exp or exp < today or not r.get("instrument_key"):
                continue
            ukey, sym = str(r.get("underlying_key") or ""), str(r.get("underlying_symbol") or "").upper()
            if r.get("underlying_type") == "INDEX":
                if ukey == NIFTY and (nifty_fut is None or exp < nifty_fut[0]):
                    nifty_fut = (exp, r["instrument_key"])
                continue
            if r.get("underlying_type") != "EQUITY" or not ukey.startswith("NSE_EQ|") or not sym:
                continue
            cur = stocks.get(sym)
            if cur is None or exp < cur["expiry"]:
                stocks[sym] = {"eq": ukey, "fut": r["instrument_key"], "lot": r.get("lot_size"),
                               "name": r.get("name") or sym, "expiry": exp}
        if len(stocks) < 50:
            raise UpstoxError("only %d F&O stocks found in the instruments file" % len(stocks))
        uni = {"date": today, "nifty_fut": nifty_fut[1] if nifty_fut else None, "stocks": stocks}
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(uni))
        return uni
    except Exception as e:
        if old and old.get("stocks"):
            old["stale"] = "instruments file failed (%s); using the list from %s" % (str(e)[:120], old.get("date"))
            return old
        raise UpstoxError("could not build the F&O universe: %s" % str(e)[:200])


FLOWS_LOOKBACK_DAYS = 10


def _flow_days():
    """Candidate 'from' dates, newest first, weekends skipped."""
    today = now_ist().date()
    for back in range(FLOWS_LOOKBACK_DAYS + 1):
        d = today - timedelta(days=back)
        if d.weekday() < 5:
            yield d.isoformat()


def _latest(rows):
    rows = sorted(rows or [], key=lambda r: _f(r.get("time_stamp")) or 0)
    return rows[-1] if rows else None


def flows():
    """Latest FII and DII figures. Best effort; returns {} parts that fail.

    Live runs showed /v2/market/fii and /dii answer with the single day named in
    'from' (a 'from' 12 days back always came back with that day's figures), so we
    walk back from today one weekday at a time and keep the newest day found for
    each segment. If the API instead returns a range, the first call already
    holds the newest day and the loop stops there.
    """
    out = {}
    fii_segs = (("NSE_EQ|CASH", "fii_cash"), ("NSE_FO|INDEX_FUTURES", "fii_index_fut"),
                ("NSE_FO|STOCK_FUTURES", "fii_stock_fut"))
    try:
        for frm in _flow_days():
            missing = [(seg, name) for seg, name in fii_segs if name not in out]
            if not missing:
                break
            data = _get("/v2/market/fii", [("data_type", seg) for seg, _ in missing]
                        + [("interval", "1D"), ("from", frm)]) or {}
            for seg, name in missing:
                r = _latest(data.get(seg))
                if not r:
                    continue
                item = {"date": _to_date(r.get("time_stamp")),
                        "net": round((_f(r.get("buy_amount")) or 0) - (_f(r.get("sell_amount")) or 0), 1)}
                lng, sht = _f(r.get("total_long_contracts")) or 0, _f(r.get("total_short_contracts")) or 0
                if lng + sht > 0:
                    item["long_share"] = round(lng / (lng + sht), 3)
                out[name] = item
    except UpstoxError as e:
        out["fii_error"] = str(e)[:160]
    try:
        for frm in _flow_days():
            data = _get("/v2/market/dii", [("data_type", "NSE_EQ|CASH"), ("interval", "1D"), ("from", frm)]) or {}
            r = _latest(data.get("NSE_EQ|CASH"))
            if r:
                out["dii_cash"] = {"date": _to_date(r.get("time_stamp")),
                                   "net": round((_f(r.get("buy_amount")) or 0) - (_f(r.get("sell_amount")) or 0), 1)}
                break
    except UpstoxError as e:
        out["dii_error"] = str(e)[:160]
    return out


def option_expiries(eq_key):
    """Upcoming option expiries for one stock, nearest first."""
    contracts = _get("/v2/option/contract", {"instrument_key": eq_key}) or []
    today = now_ist().date().isoformat()
    return sorted({str(c.get("expiry"))[:10] for c in contracts if str(c.get("expiry", ""))[:10] >= today})


def sessions_until(expiry):
    """Weekdays from today to expiry, both included (holidays not removed)."""
    d, n = now_ist().date(), 0
    while d.isoformat() <= expiry:
        n += 1 if d.weekday() < 5 else 0
        d += timedelta(days=1)
    return max(1, n)


def pick_expiry(expiries, min_sessions=5):
    """Nearest expiry with at least min_sessions left; otherwise the next one.

    Buying a stock option in its last few sessions means fast time decay and
    jumpy prices near settlement, so expiry week rolls to the next month.
    """
    for e in expiries:
        if sessions_until(e) >= min_sessions:
            return e
    return expiries[-1] if expiries else None


def _num(d, k):
    return _f((d or {}).get(k))


def option_chain(eq_key, expiry):
    """Rows of {strike, CE: {...}, PE: {...}} with price, bid/ask, OI, volume and greeks."""
    rows = []
    for row in _get("/v2/option/chain", {"instrument_key": eq_key, "expiry_date": expiry}) or []:
        strike = _f(row.get("strike_price"))
        if strike is None:
            continue
        item = {"strike": strike}
        for side, name in (("call_options", "CE"), ("put_options", "PE")):
            o = row.get(side) or {}
            md, gk = o.get("market_data") or {}, o.get("option_greeks") or {}
            item[name] = {"key": o.get("instrument_key"), "ltp": _num(md, "ltp"), "close": _num(md, "close_price"),
                          "bid": _num(md, "bid_price"), "ask": _num(md, "ask_price"), "oi": _num(md, "oi"),
                          "prev_oi": _num(md, "prev_oi"), "volume": _num(md, "volume"),
                          "iv": _num(gk, "iv"), "delta": _num(gk, "delta"), "theta": _num(gk, "theta")}
        rows.append(item)
    rows.sort(key=lambda r: r["strike"])
    return rows


def option_move(eq_key, spot, expiries=None):
    """At-the-money straddle on the nearest usable expiry: the move the options market is pricing."""
    expiries = expiries or option_expiries(eq_key)
    expiry = pick_expiry(expiries, min_sessions=1)
    if not expiry:
        raise UpstoxError("no option expiry")
    chain = option_chain(eq_key, expiry)
    best, put_oi, call_oi = None, 0.0, 0.0
    for row in chain:
        ce, pe = row["CE"], row["PE"]
        call_oi += ce["oi"] or 0
        put_oi += pe["oi"] or 0
        cp, pp = ce["ltp"] or ce["close"], pe["ltp"] or pe["close"]
        if not cp or not pp:
            continue
        if best is None or abs(row["strike"] - spot) < abs(best[0] - spot):
            best = (row["strike"], cp, pp, ce["iv"], pe["iv"])
    if not best or not spot:
        raise UpstoxError("no at-the-money strike with prices")
    n = sessions_until(expiry)
    straddle = best[1] + best[2]
    ivs = [x for x in best[3:] if x]
    return {"expiry": expiry, "sessions_left": n, "straddle_pct": round(straddle / spot * 100, 2),
            # a straddle is roughly 0.8 of the one-standard-deviation move to expiry
            "day_move_pct": round(straddle * 1.25 / (n ** 0.5) / spot * 100, 2),
            "atm_iv": round(sum(ivs) / len(ivs), 1) if ivs else None,
            "pcr": round(put_oi / call_oi, 2) if call_oi else None}
