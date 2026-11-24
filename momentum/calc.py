"""Pure calculations for the momentum jobs. No network, no clock, no files."""
import re
import math

GAP_BUCKETS = ((0.5, 1.0), (1.0, 2.0), (2.0, 4.0), (4.0, 1e9))
RULES_VERSION = 3   # bump when a threshold below changes, so the scorecard can keep versions apart


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
    rets = [pct(d["c"], p["c"]) for p, d in zip(days[-21:-1], days[-20:]) if p["c"]]
    rv20 = (sum((x - mean(rets)) ** 2 for x in rets) / (len(rets) - 1)) ** 0.5 * math.sqrt(252) if len(rets) > 2 else None
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
        "rv20": r2(rv20, 1), "sma20": r2(sma20), "sma50": r2(sma50),
    }
    f.update(swing_inputs(days, a))
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
    entry_i and exit_i are bar indices, so an option's price can be read at the same minutes.
    """
    up = direction == "UP"
    try:
        confirm, cancel = float(confirm), float(cancel)
        target = float(target) if target not in (None, "") else None
    except (TypeError, ValueError):
        return {"status": "no_levels"}
    if (up and confirm <= cancel) or (not up and confirm >= cancel) or not bars:
        return {"status": "bad_levels" if bars else "no_bars"}
    entry = entry_i = None
    for i, b in enumerate(bars):
        hit_cancel = b["l"] <= cancel if up else b["h"] >= cancel
        if entry is None:
            if hit_cancel:
                return {"status": "cancelled"}
            if (b["h"] >= confirm) if up else (b["l"] <= confirm):
                entry = max(confirm, b["o"]) if up else min(confirm, b["o"])  # a gap through fills at the open
                entry_i = i
                risk = abs(entry - cancel)
                if risk <= 0:
                    return {"status": "bad_levels"}
            continue
        if hit_cancel:
            return {"status": "stopped", "entry": r2(entry), "r": -1.0, "entry_i": entry_i, "exit_i": i}
        if target is not None and ((b["h"] >= target) if up else (b["l"] <= target)):
            return {"status": "target", "entry": r2(entry), "r": r2(abs(target - entry) / risk), "entry_i": entry_i, "exit_i": i}
    if entry is None:
        return {"status": "no_trigger"}
    return {"status": "closed", "entry": r2(entry), "r": r2((bars[-1]["c"] - entry) * (1 if up else -1) / risk),
            "entry_i": entry_i, "exit_i": len(bars) - 1}


def option_leg(trade, opt_bars, und_bars):
    """Premium return of an option bought at the trade's entry minute and sold at its exit minute."""
    if not trade or trade.get("entry_i") is None or not opt_bars:
        return None
    by_ts = {b["ts"]: b for b in opt_bars}

    def at(i):
        # the option's close in the same minute, or the last option print before it
        ts = und_bars[i]["ts"]
        if ts in by_ts:
            return by_ts[ts]["c"]
        earlier = [b for b in opt_bars if b["ts"] <= ts]
        return earlier[-1]["c"] if earlier else None

    p_in, p_out = at(trade["entry_i"]), at(trade["exit_i"])
    if not p_in or p_out is None:
        return None
    return {"premium_in": r2(p_in), "premium_out": r2(p_out), "premium_ret": r2(pct(p_out, p_in))}


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
    opt = [r["option"]["premium_ret"] for r in rows if (r.get("option") or {}).get("premium_ret") is not None]
    return {"n": n, "right": right, "hit": r2(right / n) if n else None, "needs_for_95": needed_for_95(n),
            "avg_ret": r2(mean([r.get("ret") for r in rows])), "avg_alpha": r2(mean([r.get("alpha") for r in rows])),
            "trades": len(trig), "avg_r": r2(mean(trig)), "total_r": r2(sum(trig)) if trig else None,
            "n_5d": sum(1 for r in rows if r.get("ret_5d") is not None),
            "avg_ret_5d": r2(mean([r.get("ret_5d") for r in rows])),
            "avg_alpha_5d": r2(mean([r.get("alpha_5d") for r in rows])),
            "n_10d": sum(1 for r in rows if r.get("ret_10d") is not None),
            "hit_10d": r2(mean([1.0 if r["ret_10d"] > 0 else 0.0 for r in rows if r.get("ret_10d") is not None])),
            "avg_ret_10d": r2(mean([r.get("ret_10d") for r in rows])),
            "avg_alpha_10d": r2(mean([r.get("alpha_10d") for r in rows])),
            "opt_trades": len(opt), "opt_win": r2(mean([1.0 if x > 0 else 0.0 for x in opt])),
            "opt_avg_ret": r2(mean(opt))}


def scorecard(rows):
    """Tallies overall and by tier, conviction, horizon, direction, evidence, market regime and gap verdict."""
    groups = {"all": {"all": rows}}
    for field in ("tier", "conviction", "horizon", "direction", "regime", "gap_verdict", "surprise"):
        g = {}
        for r in rows:
            v = surprise_bucket(r.get("surprise_pct")) if field == "surprise" else r.get(field)
            g.setdefault(str(v or "unknown").lower(), []).append(r)
        groups[field] = g
    ev = {}
    for r in rows:
        for e in r.get("evidence") or []:
            ev.setdefault(str(e).lower(), []).append(r)
    groups["evidence"] = ev
    return {name: {k: tally(v) for k, v in sorted(g.items())} for name, g in groups.items()}


# ------------------------------------------------------------------ swing (rules version 2)

def stdev(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 3:
        return None
    m = sum(xs) / len(xs)
    return (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5


def swing_inputs(days, a):
    """Momentum over 6 and 12 months adjusted for volatility (NSE's momentum-index method),
    plus the shape of the last few weeks: a tight base or an orderly pullback."""
    c = [d["c"] for d in days]
    out = {}
    rets = [pct(d["c"], p["c"]) for p, d in zip(days[-253:-1], days[-252:]) if p["c"]]
    sd = stdev(rets)
    ann = sd * math.sqrt(252) if sd else None
    for months, n in ((6, 126), (12, 252)):
        if len(c) > n and ann:
            out["mom%d" % months] = r2(pct(c[-1], c[-n - 1]) / ann, 3)
    if not a or len(days) < 60:
        return out
    last = days[-1]
    sma20 = mean(c[-20:])
    sma50 = mean(c[-50:])
    sma50_prev = mean(c[-70:-20]) if len(c) >= 70 else None
    hi10, lo10 = max(d["h"] for d in days[-10:]), min(d["l"] for d in days[-10:])
    hi5, lo5 = max(d["h"] for d in days[-5:]), min(d["l"] for d in days[-5:])
    vol50 = mean([d["v"] for d in days[-50:]])
    vol5 = mean([d["v"] for d in days[-5:]])
    out.update(base_atr=r2((hi10 - lo10) / a, 1), dryup=r2(vol5 / vol50) if vol50 else None,
               ext_atr=r2((last["c"] - sma20) / a, 1), sma50_rising=bool(sma50_prev and sma50 > sma50_prev),
               sma50_falling=bool(sma50_prev and sma50 < sma50_prev))
    out["setup_up"] = _setup(True, last["c"], sma20, sma50, out, hi10, lo10, hi5, lo5, a)
    out["setup_down"] = _setup(False, last["c"], sma20, sma50, out, hi10, lo10, hi5, lo5, a)
    return out


def _setup(up, close, sma20, sma50, f, hi10, lo10, hi5, lo5, a):
    """A tight base or an orderly pullback inside an established trend, with its trigger and stop."""
    s = 1 if up else -1
    trend = (close > sma50 and sma20 > sma50 and f["sma50_rising"]) if up else \
            (close < sma50 and sma20 < sma50 and f["sma50_falling"])
    if not trend or abs(f["ext_atr"]) > 3:
        return None
    quiet = f["dryup"] is not None and f["dryup"] < 0.85
    if f["base_atr"] <= 4.0:
        kind, trigger, stop = "tight base", (hi10 if up else lo10), (lo10 if up else hi10)
    elif -0.5 <= (close - sma20) * s / a <= 1.0 and ((hi10 - close) if up else (close - lo10)) >= 1.5 * a:
        kind, trigger = "pullback", (hi5 if up else lo5)
        stop = min(lo5, sma20 - 0.5 * a) if up else max(hi5, sma20 + 0.5 * a)
    else:
        return None
    trigger += 0.1 * a * s
    risk = (trigger - stop) * s
    if risk <= 0 or risk > 3.5 * a:
        return None
    return {"kind": kind, "quiet_volume": quiet, "trigger": r2(trigger), "stop": r2(stop),
            "target": r2(trigger + 2 * risk * s), "risk_atr": r2(risk / a, 1)}


def zscores(values):
    """{key: z} for a {key: value} dict; None values left out."""
    xs = {k: v for k, v in values.items() if v is not None}
    sd = stdev(list(xs.values()))
    if not sd:
        return {}
    m = mean(list(xs.values()))
    return {k: (v - m) / sd for k, v in xs.items()}


def panic_state(nifty_days, vix_days):
    """Momentum crashes cluster after market falls with high volatility (Daniel and Moskowitz 2016)."""
    if len(nifty_days) < 60 or len(vix_days) < 40:
        return {"panic": False, "why": "not enough history"}
    c = [d["c"] for d in nifty_days]
    dd20 = pct(c[-1], max(c[-20:]))
    below50 = c[-1] < mean(c[-50:])
    v = [d["c"] for d in vix_days]
    vix_ratio = v[-1] / median(v[-60:]) if median(v[-60:]) else None
    panic = bool(below50 and dd20 is not None and dd20 <= -5 and vix_ratio and vix_ratio >= 1.3)
    return {"panic": panic, "drawdown_20d": r2(dd20), "below_sma50": below50, "vix_vs_60d_median": r2(vix_ratio)}


# ------------------------------------------------------------------ options (rules version 2)

TARGET_DELTA = 0.55
MAX_SPREAD_PCT = 2.5
IV_RICH = 1.6
THETA_HEAVY_PCT = 4.0


def option_plan(chain, direction, lot, risk_per_share, rv20=None, expiry=None, sessions_left=None):
    """Contract to buy for a directional intraday idea, with its premium stop and target.

    Picks the strike whose delta is nearest 0.55 (at or slightly in the money), then
    translates the stock's stop and 2R target into premium using delta. Flags the
    things that make option buying lose even when the direction is right: a wide
    bid-ask spread, implied volatility far above the stock's recent realised
    volatility, and fast time decay.
    """
    side = "CE" if direction == "UP" else "PE"
    best = None
    for row in chain:
        o = row.get(side) or {}
        price = o.get("ltp") or o.get("close")
        d = abs(o.get("delta") or 0)
        if not price or not d or not o.get("key"):
            continue
        score = abs(d - TARGET_DELTA) + (0.15 if (o.get("oi") or 0) <= 0 else 0)
        if best is None or score < best[0]:
            best = (score, row["strike"], o, price, d)
    if not best:
        return None
    _, strike, o, price, d = best
    bid, ask = o.get("bid"), o.get("ask")
    spread = (ask - bid) / ((ask + bid) / 2) * 100 if bid and ask and ask >= bid else None
    try:
        risk = float(risk_per_share)
    except (TypeError, ValueError):
        risk = None
    plan = {"side": side, "strike": strike, "key": o["key"], "expiry": expiry, "sessions_left": sessions_left,
            "premium": r2(price), "bid": bid, "ask": ask, "spread_pct": r2(spread, 1), "delta": r2(d),
            "iv": o.get("iv"), "theta": o.get("theta"), "oi": o.get("oi"), "volume": o.get("volume"), "lot": lot}
    if lot:
        plan["cost_per_lot"] = round(price * lot)
    if risk and risk > 0:
        stop = max(0.05, price - d * risk * 1.15)   # 15% extra for spread and the delta moving against you
        plan.update(premium_stop=r2(stop), premium_target=r2(price + d * 2 * risk))
        if lot:
            plan["risk_per_lot"] = round((price - stop) * lot)
    flags = []
    if spread is None:
        flags.append("no live bid/ask")
    elif spread > MAX_SPREAD_PCT:
        flags.append("wide spread %.1f%%" % spread)
    if o.get("iv") and rv20:
        plan["iv_vs_rv"] = r2(o["iv"] / rv20)
        if o["iv"] / rv20 >= IV_RICH:
            flags.append("expensive: IV %.0f vs realised %.0f" % (o["iv"], rv20))
    if o.get("theta") and price:
        decay = abs(o["theta"]) / price * 100
        plan["theta_pct"] = r2(decay, 1)
        if decay >= THETA_HEAVY_PCT:
            flags.append("time decay %.0f%% a day" % decay)
    if (o.get("oi") or 0) <= 0:
        flags.append("no open interest")
    plan["flags"] = flags
    plan["grade"] = "ok" if not flags or flags == ["no live bid/ask"] else "caution"
    return plan


# ------------------------------------------------------------------ peers and sectors (rules version 2)

def correlation(a, b):
    n = len(a)
    if n < 20:
        return None
    ma, mb = sum(a) / n, sum(b) / n
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    if va <= 0 or vb <= 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) ** 0.5


def peer_map(returns, index_ret=None, n=60, top=5, min_corr=0.45):
    """Each stock's closest peers by correlation of daily returns over n sessions.

    The market's own move is taken out first (returns minus beta x index), so two
    stocks count as peers because they share an industry driver, not just because
    both follow Nifty.
    """
    dates = None
    for r in returns.values():
        ds = set(r)
        dates = ds if dates is None else dates & ds
    dates = sorted(dates or [])[-n:]
    if len(dates) < 30:
        return {}
    series = {}
    for sym, r in returns.items():
        xs = [r[d] for d in dates]
        if index_ret and all(d in index_ret for d in dates):
            ix = [index_ret[d] for d in dates]
            mi = sum(ix) / len(ix)
            vi = sum((v - mi) ** 2 for v in ix)
            if vi > 0:
                mx = sum(xs) / len(xs)
                b = sum((v - mi) * (x - mx) for v, x in zip(ix, xs)) / vi
                xs = [x - b * v for x, v in zip(xs, ix)]
        series[sym] = xs
    syms = sorted(series)
    best = {s: [] for s in syms}
    for i, a in enumerate(syms):
        for b in syms[i + 1:]:
            c = correlation(series[a], series[b])
            if c is not None and c >= min_corr:
                best[a].append((c, b))
                best[b].append((c, a))
    return {s: [[b, r2(c)] for c, b in sorted(v, reverse=True)[:top]] for s, v in best.items() if v}


def sector_table(stocks, industry_of, min_members=3):
    """Median move of the F&O stocks in each industry, ranked by 20-session strength against Nifty."""
    groups = {}
    for sym, f in stocks.items():
        ind = industry_of.get(sym)
        if ind:
            groups.setdefault(ind, []).append(f)
    rows = []
    for ind, fs in groups.items():
        if len(fs) < min_members:
            continue
        rows.append({"industry": ind, "members": len(fs), "chg1": r2(median([f.get("chg1") for f in fs])),
                     "chg5": r2(median([f.get("chg5") for f in fs])), "rs20": r2(median([f.get("rs20") for f in fs])),
                     "up_share": r2(sum(1 for f in fs if (f.get("chg5") or 0) > 0) / len(fs))})
    rows.sort(key=lambda r: -(r["rs20"] if r["rs20"] is not None else -99))
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


# ------------------------------------------------------------------ learning from the record

def wilson(k, n, z=1.645):
    """90% Wilson interval for a hit rate of k out of n."""
    if not n:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return r2(c - h), r2(c + h)


def surprise_bucket(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    if x >= 10:
        return "beat 10%+"
    if x >= 0:
        return "beat 0-10%"
    if x > -10:
        return "miss 0-10%"
    return "miss 10%+"


def outcome(r):
    """1 if the pick worked: for swing the 10-session result (or 5 if that is all there is), else open to close."""
    if r.get("horizon") == "swing":
        v = r.get("ret_10d") if r.get("ret_10d") is not None else r.get("ret_5d")
        return None if v is None else (1.0 if v > 0 else 0.0)
    return 1.0 if r.get("right") else 0.0


def features_of(r):
    names = ["tag:" + str(e).lower() for e in (r.get("evidence") or [])]
    names += ["horizon:" + str(r.get("horizon")), "direction:" + str(r.get("direction")),
              "regime:" + str(r.get("regime") or "unknown")]
    b = surprise_bucket(r.get("surprise_pct"))
    if b:
        names.append("surprise:" + b)
    return names


LEARN_MIN = 100


def learn(rows, min_rows=LEARN_MIN, steps=3000, lr=0.3, l2=1.0):
    """What the record says about each kind of evidence.

    Always: hit rate with a 90% interval for every tag, horizon, direction, regime and
    surprise bucket. Once there are min_rows finished picks: a logistic regression on
    the same features (standard library, gradient descent with a ridge penalty), so each
    piece of evidence gets a weight with the others held fixed. Positive weight = it
    has gone with picks that worked.
    """
    data = [(features_of(r), outcome(r)) for r in rows]
    data = [(f, y) for f, y in data if y is not None]
    groups = {}
    for f, y in data:
        for name in f:
            g = groups.setdefault(name, [0, 0])
            g[0] += 1
            g[1] += y
    table = []
    for name, (n, k) in sorted(groups.items()):
        lo, hi = wilson(k, n)
        table.append({"feature": name, "n": n, "hit": r2(k / n), "lo90": lo, "hi90": hi})
    out = {"n": len(data), "table": table, "model": None}
    if len(data) < min_rows or len({y for _, y in data}) < 2:
        out["note"] = "model starts at %d finished picks; %d so far" % (min_rows, len(data))
        return out
    names = sorted(n for n, (c, _) in groups.items() if c >= 10)
    idx = {n: i for i, n in enumerate(names)}
    w, b = [0.0] * len(names), 0.0
    X = [[idx[n] for n in f if n in idx] for f, _ in data]
    Y = [y for _, y in data]
    m = len(data)
    for _ in range(steps):
        gw, gb = [0.0] * len(names), 0.0
        for xs, y in zip(X, Y):
            z = b + sum(w[i] for i in xs)
            p = 1 / (1 + math.exp(-max(-30, min(30, z))))
            e = p - y
            gb += e
            for i in xs:
                gw[i] += e
        b -= lr * gb / m
        for i in range(len(w)):
            w[i] -= lr * (gw[i] / m + l2 * w[i] / m)
    out["model"] = {"intercept": r2(b, 3), "base_rate": r2(sum(Y) / m),
                    "weights": sorted(({"feature": n, "weight": r2(w[idx[n]], 3), "n": groups[n][0]} for n in names),
                                      key=lambda x: -x["weight"])}
    return out


# ------------------------------------------------------------------ 09:20 trade engine (rules version 3)
#
# Prepare before the open, decide after it. A stock becomes a trade only when the
# market shows its hand in the first five minutes: unusual volume, a clear
# direction that agrees with the gap (and the news, if any), a market that is not
# fighting it, room left to run, and an option that can be traded cheaply.

GATE_OR_MAX_ATR = 1.0     # opening range no wider than one day's normal range
GATE_GAP_MAX_ATR = 1.5    # the gap has not already used up the move
GATE_GAP_FLAT = 0.25      # gaps smaller than this (%) count as no gap
ENTRY_FROM = (9, 20)      # after the five-minute opening range
ENTRY_TILL = (10, 15)
HALF_AT_R = 2.0
DAILY_STOP_R = -3.0


def trade_gates(sym, q, atr_pct, relvol, rank, nifty, news=None, option=None):
    """Five gates for one in-play stock at 09:20. Returns {"pass", "direction", "gates", plan levels}.

    q: the stock's quote (open, high, low, last, prev). nifty: Nifty quote (open, last).
    news: watchlist item {"direction", "fresh"} or None. option: option_plan() result or None.
    """
    o, hi, lo, last, prev = q["open"], q["high"], q["low"], q["last"], q["prev"]
    direction = "UP" if last > o else "DOWN" if last < o else None
    atr = (atr_pct or 0) / 100 * prev if prev else 0
    gap = pct(o, prev) if prev else 0
    gates = []

    def gate(name, ok, why):
        gates.append({"gate": name, "ok": bool(ok), "why": why})

    gate("in play", relvol is not None and rank is not None,
         "%.1fx usual opening volume, #%s" % (relvol or 0, rank))
    gap_dir = "UP" if gap > GATE_GAP_FLAT else "DOWN" if gap < -GATE_GAP_FLAT else None
    agree = direction is not None and (gap_dir is None or gap_dir == direction)
    why = "first 5 min %s, gap %+.2f%%" % (direction or "flat", gap)
    if news and news.get("direction") in ("UP", "DOWN"):
        agree = agree and news["direction"] == direction
        why += ", news %s" % news["direction"]
    gate("direction", agree, why)
    if nifty and nifty.get("open") and nifty.get("last"):
        m = pct(nifty["last"], nifty["open"])
        ok = direction == "UP" and m >= 0 or direction == "DOWN" and m <= 0
        gate("market", ok, "Nifty %+.2f%% from its open" % m)
    else:
        gate("market", False, "no Nifty quote")
    if atr:
        or_atr, gap_atr = (hi - lo) / atr, abs(o - prev) / atr
        gate("room", or_atr <= GATE_OR_MAX_ATR and gap_atr <= GATE_GAP_MAX_ATR,
             "range %.2f ATR, gap %.2f ATR" % (or_atr, gap_atr))
    else:
        or_atr = gap_atr = None
        gate("room", False, "no ATR")
    if option is None:
        gate("tradeable", False, "no option contract found")
    else:
        gate("tradeable", option.get("grade") == "ok", ", ".join(option.get("flags") or []) or
             "spread %s%%" % option.get("spread_pct"))
    out = {"symbol": sym, "direction": direction, "gates": gates, "pass": all(g["ok"] for g in gates),
           "relvol": r2(relvol, 1), "rank": rank, "gap": r2(gap), "or_atr": r2(or_atr), "gap_atr": r2(gap_atr),
           "news": bool(news), "fresh": bool(news and news.get("fresh"))}
    if direction and hi > lo:
        up = direction == "UP"
        entry, stop = (hi, lo) if up else (lo, hi)
        risk = abs(entry - stop)
        out.update(entry=r2(entry), stop=r2(stop), risk=r2(risk),
                   half=r2(entry + HALF_AT_R * risk if up else entry - HALF_AT_R * risk))
    return out


def rank_trades(rows):
    """Fresh news first, then any news, then volume."""
    return sorted(rows, key=lambda r: (not r.get("fresh"), not r.get("news"), -(r.get("relvol") or 0)))


def one_per_theme(rows, theme_of):
    """Keep the best trade per (theme, direction): three bank stocks falling on one news item are one bet."""
    seen, keep, dropped = set(), [], []
    for r in rows:
        t = (theme_of(r["symbol"]) or r["symbol"], r["direction"])
        (dropped if t in seen else keep).append(r)
        seen.add(t)
    return keep, dropped


def _hm(t):
    return (t.hour, t.minute)


def trade_step(t, last, vwap, now_t, st):
    """Advance one engine trade from its latest price. Mutates st; returns alert texts.

    Stages: waiting -> entered -> half (half booked at 2R, rest trails VWAP) -> done.
    Before 09:20 nothing happens. A break of the stop side before entry cancels; no
    break by 10:15 expires. R results land in st["r"] for the daily stop.
    """
    out = []
    if last is None or _hm(now_t) < ENTRY_FROM:
        return out
    up = t["direction"] == "UP"
    entry, stop, risk = t["entry"], t["stop"], t["risk"]
    beyond = (lambda x: last >= x) if up else (lambda x: last <= x)
    before = (lambda x: last <= x) if up else (lambda x: last >= x)
    name = "%s %s" % (t["symbol"], t["direction"])
    stage = st.get("stage", "waiting")
    if stage == "waiting":
        if before(stop):
            st["stage"] = "done"
            st["result"] = "cancelled"
            out.append("CANCELLED %s: %.2f broke the other side of the range (%.2f) first. No trade." % (name, last, stop))
        elif beyond(entry):
            if st.get("blocked"):
                st["stage"] = "done"
                st["result"] = "skipped (daily stop)"
            elif _hm(now_t) > ENTRY_TILL:
                st["stage"] = "done"
                st["result"] = "expired"
            else:
                st["stage"] = "entered"
                st["entry_px"] = last
                st["entry_t"] = now_t.strftime("%H:%M")
                out.append("ENTRY %s: %.2f broke the opening range %.2f. Stop %.2f, book half at %.2f (2R)."
                           % (name, last, entry, stop, t["half"]))
        elif _hm(now_t) > ENTRY_TILL:
            st["stage"] = "done"
            st["result"] = "expired"
            out.append("EXPIRED %s: no break of %.2f by 10:15. No trade." % (name, entry))
        return out
    if stage == "entered":
        if before(stop):
            st.update(stage="done", result="stop", r=-1.0)
            out.append("STOP %s: %.2f hit the stop %.2f. Exit (-1R)." % (name, last, stop))
        elif beyond(t["half"]):
            st.update(stage="half", trail=entry)
            out.append("BOOK HALF %s: %.2f reached 2R (%.2f). Sell half; trail the rest along VWAP, never below entry %.2f."
                       % (name, last, t["half"], entry))
        elif _hm(now_t) >= (15, 0):
            r = (last - entry) / risk * (1 if up else -1)
            st.update(stage="done", result="15:00 exit", r=round(r, 2))
            out.append("15:00 EXIT %s: out at %.2f (%+.1fR)." % (name, last, r))
        return out
    if stage == "half":
        trail = st.get("trail", entry)
        if vwap:
            trail = max(trail, vwap) if up else min(trail, vwap)
        st["trail"] = trail
        if before(trail) or _hm(now_t) >= (15, 0):
            r_rest = (last - entry) / risk * (1 if up else -1)
            r = 0.5 * HALF_AT_R + 0.5 * r_rest
            st.update(stage="done", result="trail" if before(trail) else "15:00 exit", r=round(r, 2))
            out.append("%s %s: rest out at %.2f (%s). Trade %+.1fR."
                       % ("TRAIL EXIT" if before(trail) else "15:00 EXIT", name, last,
                          "crossed VWAP/entry %.2f" % trail if before(trail) else "end of day", r))
    return out


def size_lots(risk_per_lot, budget, cost_per_lot=None):
    """Whole lots whose stop-loss risk fits the rupee budget. 0 means even one lot risks more."""
    if not risk_per_lot or risk_per_lot <= 0 or not budget:
        return None
    lots = int(budget // risk_per_lot)
    out = {"lots": lots, "budget": budget, "risk_total": round(lots * risk_per_lot)}
    if cost_per_lot:
        out["cost_total"] = round(lots * cost_per_lot)
    return out


def day_r(states):
    return round(sum(s.get("r") or 0 for s in states.values()), 2)


# ------------------------------------------------------------------ filings (rules version 3)

_SUFFIX = re.compile(r"\b(limited|ltd|the|india|of|and|co|company|corporation|corp|industries|inds|enterprises)\b")


def norm_name(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower().replace("&", " and "))
    return " ".join(_SUFFIX.sub(" ", s).split())


def match_filings(items, universe):
    """Tag exchange announcements with the F&O symbol they belong to (by company name). Unmatched are dropped."""
    names = {}
    for sym, u in universe.items():
        for n in (u.get("name"), sym):
            k = norm_name(n)
            if k:
                names.setdefault(k, sym)
    out = []
    for it in items:
        sym = names.get(norm_name(it.get("company")))
        if sym:
            out.append(dict(it, symbol=sym))
    return out
