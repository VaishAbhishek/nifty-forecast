"""Pure calculations for the momentum jobs. No network, no clock, no files."""
import math

GAP_BUCKETS = ((0.5, 1.0), (1.0, 2.0), (2.0, 4.0), (4.0, 1e9))
RULES_VERSION = 1   # bump when a threshold below changes, so the scorecard can keep versions apart


def pct(a, b):
    return (a / b - 1) * 100 if a is not None and b else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def r2(x, n=2):
    return round(x, n) if x is not None else None


def atr(days, n=14):
    trs, w = [], days[-(n + 1):]
    for prev, d in zip(w, w[1:]):
        trs.append(max(d["h"] - d["l"], abs(d["h"] - prev["c"]), abs(d["l"] - prev["c"])))
    return mean(trs)


def returns_by_date(days):
    return {d["date"]: pct(d["c"], p["c"]) for p, d in zip(days, days[1:]) if p["c"]}


def beta(stock_ret, index_ret, n=60):
    dates = sorted(set(stock_ret) & set(index_ret))[-n:]
    if len(dates) < 30:
        return None
    xs, ys = [index_ret[d] for d in dates], [stock_ret[d] for d in dates]
    mx, my = mean(xs), mean(ys)
    var = sum((x - mx) ** 2 for x in xs)
    if var <= 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var


def features(days, index_ret=None):
    """Features of one stock from completed daily sessions (oldest first). None if too little history."""
    if len(days) < 25:
        return None
    last, prev = days[-1], days[-2]
    if not last["c"] or not prev["c"]:
        return None
    a = atr(days)
    vol_base = mean([d["v"] for d in days[-21:-1]])
    hi20, lo20 = max(d["h"] for d in days[-21:-1]), min(d["l"] for d in days[-21:-1])
    year = days[-252:]
    closes = [d["c"] for d in days]
    sma20 = mean(closes[-20:])
    sma50 = mean(closes[-50:]) if len(closes) >= 50 else None
    trend = "mixed"
    if sma50:
        if last["c"] > sma20 > sma50:
            trend = "up"
        elif last["c"] < sma20 < sma50:
            trend = "down"
    streak = 0
    for p, d in zip(reversed(days[:-1]), reversed(days)):
        step = 1 if d["c"] > p["c"] else -1 if d["c"] < p["c"] else 0
        if step == 0 or (streak and (step > 0) != (streak > 0)):
            break
        streak += step
    ranges = [d["h"] - d["l"] for d in days[-7:]]
    f = {
        "date": last["date"], "close": r2(last["c"]), "prev_close": r2(prev["c"]),
        "chg1": r2(pct(last["c"], prev["c"])),
        "chg5": r2(pct(last["c"], days[-6]["c"])),
        "chg20": r2(pct(last["c"], days[-21]["c"])),
        "gap_last": r2(pct(last["o"], prev["c"])),
        "vol_ratio": r2(last["v"] / vol_base) if vol_base else None,
        "atr_pct": r2(a / last["c"] * 100) if a else None,
        "move_atr": r2((last["c"] - prev["c"]) / a) if a else None,
        "range_pos": r2((last["c"] - last["l"]) / (last["h"] - last["l"])) if last["h"] > last["l"] else 0.5,
        "breakout": "up" if last["c"] > hi20 else "down" if last["c"] < lo20 else None,
        "hi20": r2(hi20), "lo20": r2(lo20), "high": r2(last["h"]), "low": r2(last["l"]),
        "from_52w_high": r2(pct(last["c"], max(d["h"] for d in year))),
        "from_52w_low": r2(pct(last["c"], min(d["l"] for d in year))),
        "trend": trend, "streak": streak, "nr7": ranges[-1] <= min(ranges),
    }
    if index_ret is not None:
        f["beta"] = r2(beta(returns_by_date(days), index_ret))
    return f


def gap_events(days, n=250):
    """(direction, gap %, open-to-close % in the gap's direction, filled?) for each past gap of 0.5% or more."""
    out, w = [], days[-(n + 1):]
    for p, d in zip(w, w[1:]):
        g = pct(d["o"], p["c"])
        if g is None or abs(g) < GAP_BUCKETS[0][0] or not d["o"]:
            continue
        up = g > 0
        oc = pct(d["c"], d["o"]) * (1 if up else -1)
        filled = d["l"] <= p["c"] if up else d["h"] >= p["c"]
        out.append(("up" if up else "down", abs(g), oc, filled))
    return out


def bucket_of(gap_abs):
    for lo, hi in GAP_BUCKETS:
        if lo <= gap_abs < hi:
            return "%g-%g" % (lo, hi) if hi < 1e8 else "%g+" % lo
    return None


def gap_table(events):
    """Pooled gap behaviour: {"up 1-2": {"n", "cont", "fill", "avg_oc"}}. cont = share that kept going by the close."""
    acc = {}
    for direction, g, oc, filled in events:
        b = bucket_of(g)
        if not b:
            continue
        a = acc.setdefault("%s %s" % (direction, b), [0, 0, 0, 0.0])
        a[0] += 1
        a[1] += 1 if oc > 0 else 0
        a[2] += 1 if filled else 0
        a[3] += oc
    return {k: {"n": a[0], "cont": r2(a[1] / a[0]), "fill": r2(a[2] / a[0]), "avg_oc": r2(a[3] / a[0])}
            for k, a in sorted(acc.items())}


def oi_class(price_chg, oi_chg, min_oi=3.0):
    """The standard four-way reading of price change against open-interest change (both in %)."""
    if price_chg is None or oi_chg is None or abs(oi_chg) < min_oi:
        return None
    if oi_chg > 0:
        return "long build-up" if price_chg > 0 else "short build-up"
    return "short covering" if price_chg > 0 else "long unwinding"


def regime(days):
    """Trend-or-chop reading of the index from the last 10 sessions (Kaufman efficiency ratio)."""
    if len(days) < 51:
        return {"tag": "unknown"}
    c = [d["c"] for d in days]
    path = sum(abs(b - a) for a, b in zip(c[-11:-1], c[-10:]))
    er = abs(c[-1] - c[-11]) / path if path else 0.0
    sma20, sma50 = mean(c[-20:]), mean(c[-50:])
    side = "up" if c[-1] > sma20 > sma50 else "down" if c[-1] < sma20 < sma50 else "mixed"
    tag = "chop" if er < 0.25 else ("trend_%s" % side if er >= 0.45 and side != "mixed" else "drift")
    a = atr(days)
    return {"tag": tag, "efficiency_10d": r2(er), "vs_averages": side,
            "last_range_vs_atr": r2((days[-1]["h"] - days[-1]["l"]) / a) if a else None,
            "chg1": r2(pct(c[-1], c[-2])), "chg5": r2(pct(c[-1], c[-6])), "close": r2(c[-1])}


def gap_verdict(direction, gap_pct, atr_pct):
    """How much of a pick's expected move the opening gap has already used."""
    if gap_pct is None or not atr_pct:
        return "unknown"
    used = (gap_pct if direction == "UP" else -gap_pct) / atr_pct
    if used >= 0.8:
        return "mostly priced in"
    if used >= 0.3:
        return "partly priced in"
    if used <= -0.3:
        return "gapping against"
    return "valid"


def walk(bars, direction, confirm, cancel, target=None):
    """Follow a pick through the day's 1-minute bars.

    Entry when price reaches the confirm level, stop at the cancel level, exit at
    the target if one is given, otherwise at the close. The result is in R: multiples
    of the risk taken (entry to stop). Ties inside one bar are read against the pick.
    """
    up = direction == "UP"
    try:
        confirm, cancel = float(confirm), float(cancel)
        target = float(target) if target not in (None, "") else None
    except (TypeError, ValueError):
        return {"status": "no_levels"}
    if (up and confirm <= cancel) or (not up and confirm >= cancel) or not bars:
        return {"status": "bad_levels" if bars else "no_bars"}
    entry = None
    for b in bars:
        hit_cancel = b["l"] <= cancel if up else b["h"] >= cancel
        if entry is None:
            if hit_cancel:
                return {"status": "cancelled"}
            if (b["h"] >= confirm) if up else (b["l"] <= confirm):
                entry = max(confirm, b["o"]) if up else min(confirm, b["o"])  # a gap through fills at the open
                risk = abs(entry - cancel)
                if risk <= 0:
                    return {"status": "bad_levels"}
            continue
        if hit_cancel:
            return {"status": "stopped", "entry": r2(entry), "r": -1.0}
        if target is not None and ((b["h"] >= target) if up else (b["l"] <= target)):
            return {"status": "target", "entry": r2(entry), "r": r2(abs(target - entry) / risk)}
    if entry is None:
        return {"status": "no_trigger"}
    return {"status": "closed", "entry": r2(entry), "r": r2((bars[-1]["c"] - entry) * (1 if up else -1) / risk)}


def day_outcome(direction, o, h, l, c, idx_o=None, idx_c=None):
    """Open-to-close result of a direction call, with the index for comparison."""
    s = 1 if direction == "UP" else -1
    out = {"open": r2(o), "close": r2(c), "ret": r2(pct(c, o) * s), "right": pct(c, o) * s > 0,
           "best": r2(pct(h if s > 0 else l, o) * s), "worst": r2(pct(l if s > 0 else h, o) * s)}
    if idx_o and idx_c:
        out["index_ret"] = r2(pct(idx_c, idx_o))
        out["alpha"] = r2(out["ret"] - pct(idx_c, idx_o) * s)
    return out


def needed_for_95(n):
    """Smallest number of right calls out of n that a coin flip reaches less than 5% of the time."""
    if n <= 0:
        return None
    tail = 0.0
    for k in range(n, -1, -1):
        tail += math.comb(n, k) / 2.0 ** n
        if tail > 0.05:
            return k + 1 if k < n else None
    return 0


def tally(rows):
    """Summary of a group of scored picks."""
    n = len(rows)
    trig = [r["trade"]["r"] for r in rows if (r.get("trade") or {}).get("r") is not None]
    right = sum(1 for r in rows if r.get("right"))
    return {"n": n, "right": right, "hit": r2(right / n) if n else None, "needs_for_95": needed_for_95(n),
            "avg_ret": r2(mean([r.get("ret") for r in rows])), "avg_alpha": r2(mean([r.get("alpha") for r in rows])),
            "trades": len(trig), "avg_r": r2(mean(trig)), "total_r": r2(sum(trig)) if trig else None,
            "n_5d": sum(1 for r in rows if r.get("ret_5d") is not None),
            "avg_ret_5d": r2(mean([r.get("ret_5d") for r in rows])),
            "avg_alpha_5d": r2(mean([r.get("alpha_5d") for r in rows]))}


def scorecard(rows):
    """Tallies overall and by tier, conviction, horizon, direction, evidence, market regime and gap verdict."""
    groups = {"all": {"all": rows}}
    for field in ("tier", "conviction", "horizon", "direction", "regime", "gap_verdict"):
        g = {}
        for r in rows:
            g.setdefault(str(r.get(field) or "unknown").lower(), []).append(r)
        groups[field] = g
    ev = {}
    for r in rows:
        for e in r.get("evidence") or []:
            ev.setdefault(str(e).lower(), []).append(r)
    groups["evidence"] = ev
    return {name: {k: tally(v) for k, v in sorted(g.items())} for name, g in groups.items()}
