"""Price-only indicators and the big-day probability model.

Everything here uses prices that were known before the prediction time,
so it is safe to compute on history (no lookahead).
"""
import math

from .config import BIG_MOVE_PTS


def ema(values, n):
    if not values:
        return None
    k = 2.0 / (n + 1)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e


def rsi(closes, n):
    """Wilder RSI. None if there is not enough history."""
    if len(closes) < n + 1:
        return None
    gains = losses = 0.0
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        gains += max(d, 0)
        losses += max(-d, 0)
    ag, al = gains / n, losses / n
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        ag = (ag * (n - 1) + max(d, 0)) / n
        al = (al * (n - 1) + max(-d, 0)) / n
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def true_ranges(days):
    out = []
    for i, d in enumerate(days):
        if i == 0:
            out.append(d["h"] - d["l"])
        else:
            pc = days[i - 1]["c"]
            out.append(max(d["h"] - d["l"], abs(d["h"] - pc), abs(d["l"] - pc)))
    return out


def streak(closes):
    """+n for n consecutive up closes, -n for down closes."""
    s = 0
    for i in range(len(closes) - 1, 0, -1):
        d = closes[i] - closes[i - 1]
        if d > 0 and s >= 0:
            s += 1
        elif d < 0 and s <= 0:
            s -= 1
        else:
            break
    return s


def _compressed(days, tr, i):
    """Was the market 'coiled' going into day i (uses data up to i-1 only)?"""
    if i < 21:
        return False
    ranges = [days[j]["h"] - days[j]["l"] for j in range(i - 7, i)]
    nr7 = ranges[-1] <= min(ranges)
    a5 = sum(tr[i - 5:i]) / 5
    a20 = sum(tr[i - 20:i]) / 20
    return nr7 or (a20 > 0 and a5 / a20 < 0.75)


def _expected_range(days, tr, vix_by_date, i):
    """Expected high-low range for day i from data up to i-1."""
    atr10 = sum(tr[i - 10:i]) / 10
    parts = [atr10]
    v = vix_by_date.get(days[i - 1]["date"])
    if v:
        # 1-sd daily move implied by VIX, times ~1.6 to go from close-to-close to high-low
        parts.append(days[i - 1]["c"] * v / 100 / math.sqrt(252) * 1.6)
    return sum(parts) / len(parts)


def range_model(days, vix_by_date, threshold=BIG_MOVE_PTS, lookback=500):
    """Chance that today's range (and open-to-close move) reaches `threshold` points.

    Method: take an expected range from recent ATR and India VIX, then look at
    how actual ranges compared with that same expectation on each past day.
    The probability is simply the share of past days whose ratio, applied to
    today's expectation, would have reached the threshold.
    """
    n = len(days)
    if n < 60:
        return None
    tr = true_ranges(days)
    samples = []
    for i in range(max(21, n - lookback), n):
        pred = _expected_range(days, tr, vix_by_date, i)
        if pred <= 0:
            continue
        d = days[i]
        samples.append(((d["h"] - d["l"]) / pred, abs(d["c"] - d["o"]) / pred, _compressed(days, tr, i)))
    # "day n" is today: build its expectation from all completed days
    ext = days + [days[-1]]
    tr_ext = tr + [tr[-1]]
    pred_today = _expected_range(ext, tr_ext, vix_by_date, n)
    comp_today = _compressed(ext, tr_ext, n)
    if not samples or pred_today <= 0:
        return None
    need = threshold / pred_today
    p_range = sum(1 for r, _, _ in samples if r >= need) / len(samples)
    p_oc = sum(1 for _, o, _ in samples if o >= need) / len(samples)
    cond = [s for s in samples if s[2] == comp_today]
    last60 = days[-60:]
    return {
        "expected_range": round(pred_today, 1),
        "p_range": round(p_range, 3),
        "p_oc": round(p_oc, 3),
        "n": len(samples),
        "compressed": comp_today,
        "p_range_cond": round(sum(1 for r, _, _ in cond if r >= need) / len(cond), 3) if len(cond) >= 40 else None,
        "n_cond": len(cond),
        "clim60_range": round(sum(1 for d in last60 if d["h"] - d["l"] >= threshold) / len(last60), 3),
        "clim60_oc": round(sum(1 for d in last60 if abs(d["c"] - d["o"]) >= threshold) / len(last60), 3),
    }


def first30_model(first30_by_date, days, first30_today, range_so_far, threshold=BIG_MOVE_PTS):
    """Updated chance of a `threshold` range given the first 30 minutes.

    Uses how the full-day range compared with the first-30-minute range on
    past days. Returns None if there is too little history.
    """
    if range_so_far >= threshold:
        return {"p_range": 1.0, "n": 0, "note": "range already reached"}
    by_date = {d["date"]: d for d in days}
    ratios = []
    for dt, f30 in first30_by_date.items():
        d = by_date.get(dt)
        if d and f30 > 0:
            ratios.append((d["h"] - d["l"]) / f30)
    if len(ratios) < 60 or first30_today <= 0:
        return None
    need = threshold / first30_today
    return {"p_range": round(sum(1 for r in ratios if r >= need) / len(ratios), 3), "n": len(ratios)}


def features(days, vix_by_date, open_px):
    """All quant inputs for the morning call. `days` are completed sessions only."""
    closes = [d["c"] for d in days]
    prev = days[-1]
    tr = true_ranges(days)
    ranges7 = [d["h"] - d["l"] for d in days[-7:]]
    f = {
        "prev_date": prev["date"],
        "prev_close": prev["c"],
        "open_0915": open_px,
        "gap_pts": round(open_px - prev["c"], 1),
        "gap_pct": round((open_px - prev["c"]) / prev["c"] * 100, 3),
        "ema20": round(ema(closes[-200:], 20), 1),
        "ema50": round(ema(closes[-300:], 50), 1),
        "ema200": round(ema(closes, 200), 1) if len(closes) >= 200 else None,
        "rsi14": round(rsi(closes[-250:], 14), 1) if rsi(closes[-250:], 14) is not None else None,
        "rsi2": round(rsi(closes[-250:], 2), 1) if rsi(closes[-250:], 2) is not None else None,
        "atr14": round(sum(tr[-14:]) / 14, 1),
        "streak": streak(closes[-15:]),
        "nr7": ranges7[-1] <= min(ranges7),
        "prev_range": round(prev["h"] - prev["l"], 1),
        "vix_prev": vix_by_date.get(prev["date"]),
    }
    f["range_model"] = range_model(days, vix_by_date)
    return f


def wilson(hits, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    p = hits / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def binom_p_one_sided(hits, n, p0=0.5):
    """Chance of at least `hits` successes in n tries if the true rate were p0."""
    if n == 0:
        return 1.0
    return sum(math.comb(n, k) * p0 ** k * (1 - p0) ** (n - k) for k in range(hits, n + 1))
