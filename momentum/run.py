"""Entry point.  python3 -m momentum.run {data|preopen|check5|check30|eod|selftest}

data     08:10  numbers for every F&O stock -> momentum/latest.json and momentum/brief/<date>.md
preopen  09:07  indicative opening prices -> Telegram: the real gaps, and each pick against its gap
check5   09:20  stocks trading at twice their usual volume, and where each pick stands
check30  09:47  the same after 30 minutes
eod      16:05  scores the day's picks, updates the scorecard, saves futures open interest

Advisory and read-only. It places no orders and does not touch the EMA bot or the forecast rules.
"""
import argparse
import json
import sys
import time
import traceback
from datetime import datetime, time as dtime, timedelta

from forecast import store, telegram
from forecast import upstox as ux
from forecast.config import CONFIG_DIR, git_sha, now_ist, redact

from . import api, brief, calc

D = "momentum/"
OPENVOL = "cache/momentum_openvol.json"
WINDOWS = {"data": (dtime(7, 30), dtime(9, 0)), "preopen": (dtime(9, 0), dtime(9, 14)),
           "check5": (dtime(9, 18), dtime(9, 35)), "check30": (dtime(9, 40), dtime(10, 20)),
           "eod": (dtime(15, 45), dtime(23, 30))}
IN_PLAY_RELVOL = 2.0
ORB_STOP_ATR = 0.10


def trading_day(now):
    day = now.date().isoformat()
    if now.weekday() >= 5:
        return False, "weekend"
    try:
        return (False, "NSE holiday (Upstox)") if ux.is_trading_holiday(day) else (True, "Upstox calendar")
    except Exception as e:
        try:
            local = json.loads((CONFIG_DIR / "holidays.json").read_text())["nse_trading_holidays"]
        except Exception:
            local = []
        return (False, "NSE holiday (local list)") if day in local else (True, "local list (%s)" % str(e)[:60])


def write_compact(name, obj):
    p = store._path(name)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(redact(json.dumps(obj, separators=(",", ":"), sort_keys=True, default=str)))
    tmp.replace(p)


def write_text(name, text):
    p = store._path(name)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(redact(text))
    tmp.replace(p)


def load_picks(today):
    """Picks the morning report logged for today: momentum/picks/<date>.json. Tolerant of loose input."""
    raw = store.read_json(D + "picks/%s.json" % today)
    rows = raw.get("picks") if isinstance(raw, dict) else raw
    out, seen = [], set()
    for p in rows or []:
        if not isinstance(p, dict):
            continue
        sym = str(p.get("symbol") or "").upper().strip().replace("NSE:", "")
        direction = str(p.get("direction") or "").upper().strip()
        direction = {"LONG": "UP", "BUY": "UP", "SHORT": "DOWN", "SELL": "DOWN"}.get(direction, direction)
        horizon = str(p.get("horizon") or "intraday").lower().strip()
        if not sym or direction not in ("UP", "DOWN") or (sym, horizon) in seen:
            continue
        seen.add((sym, horizon))
        ev = p.get("evidence") or []
        out.append({"symbol": sym, "direction": direction, "horizon": horizon,
                    "tier": str(p.get("tier") or "list").lower(), "conviction": str(p.get("conviction") or "unknown").lower(),
                    "evidence": [str(e).lower() for e in (ev if isinstance(ev, list) else [ev])],
                    "confirm": p.get("confirm"), "cancel": p.get("cancel"), "target": p.get("target")})
    return out


def stage(cmd, args, now):
    """Common gate: trading day and time window. Returns None to proceed, or an exit code."""
    ok, why = trading_day(now)
    if not ok:
        store.log("momentum %s: skipped, %s" % (cmd, why))
        store.set_status("momentum_" + cmd, True, [], {"skipped": why})
        return 0
    lo, hi = WINDOWS[cmd]
    if not (lo <= now.time() <= hi) and not args.force:
        store.log("momentum %s: outside %s-%s IST, not running (use --force)" % (cmd, lo.strftime("%H:%M"), hi.strftime("%H:%M")))
        return 0
    return None


# ------------------------------------------------------------------ data

def top(stocks, key, n, reverse=True, cond=None):
    rows = [(s, f[key]) for s, f in stocks.items() if f.get(key) is not None and (cond is None or cond(f))]
    rows.sort(key=lambda x: x[1], reverse=reverse)
    return [s for s, _ in rows[:n]]


def build_lists(stocks, index_chg20):
    for f in stocks.values():
        f["rs20"] = calc.r2(f["chg20"] - index_chg20) if f.get("chg20") is not None and index_chg20 is not None else None
    lists = {
        "gainers": top(stocks, "move_atr", 10, cond=lambda f: f["move_atr"] > 0.8),
        "losers": top(stocks, "move_atr", 10, reverse=False, cond=lambda f: f["move_atr"] < -0.8),
        "volume": top(stocks, "vol_ratio", 12, cond=lambda f: f["vol_ratio"] >= 1.5),
        "breakouts": top(stocks, "vol_ratio", 10, cond=lambda f: f.get("breakout") == "up"),
        "breakdowns": top(stocks, "vol_ratio", 10, cond=lambda f: f.get("breakout") == "down"),
        "oi_long": top(stocks, "oi_chg", 8, cond=lambda f: f.get("oi_class") == "long build-up"),
        "oi_short": top(stocks, "oi_chg", 8, cond=lambda f: f.get("oi_class") == "short build-up"),
        "rs_lead": top(stocks, "rs20", 8),
        "rs_lag": top(stocks, "rs20", 8, reverse=False),
        "near_high": top(stocks, "from_52w_high", 8, cond=lambda f: f["from_52w_high"] >= -2),
    }
    # focus = on two or more lists, at least one of them about last session's activity
    # (the slow lists alone, strength and nearness to the high, change little from day to day)
    fresh = set()
    for name in ("gainers", "losers", "volume", "breakouts", "breakdowns", "oi_long", "oi_short"):
        fresh.update(lists[name])
    count = {}
    for name, syms in lists.items():
        for s in syms:
            count[s] = count.get(s, 0) + 1
    focus = [s for s, c in count.items() if c >= 2 and s in fresh]
    focus.sort(key=lambda s: (-count[s], -abs(stocks[s].get("move_atr") or 0)))
    lists["focus"] = focus[:25]
    return lists


def backfill_openvol(stocks, today, limit=110):
    """Usual volume in the first 5 and 30 minutes, from 5-minute history, for stocks that lack a baseline."""
    hist = store.read_json(OPENVOL, {}) or {}
    h5, h30 = hist.setdefault("5", {}), hist.setdefault("30", {})
    have = {}
    for day, row in h5.items():
        for s in row:
            have[s] = have.get(s, 0) + 1
    need = [s for s in sorted(stocks) if have.get(s, 0) < 8][:limit]
    frm, to = (datetime.fromisoformat(today) - timedelta(days=24)).date().isoformat(), today
    done = 0
    for sym in need:
        try:
            by_day = {}
            for b in api.minutes(stocks[sym]["eq"], 5, frm, to):
                if b["date"] < today:
                    by_day.setdefault(b["date"], []).append(b)
            for day, bars in by_day.items():
                bars.sort(key=lambda b: b["ts"])
                if bars[0]["ts"].time() > dtime(9, 20):
                    continue
                h5.setdefault(day, {}).setdefault(sym, bars[0]["v"])
                h30.setdefault(day, {}).setdefault(sym, sum(b["v"] for b in bars[:6]))
            done += 1
        except Exception:
            pass
        time.sleep(api.PACE_S)
    for h in (h5, h30):
        for day in sorted(h)[:-20]:
            del h[day]
    if need:
        write_compact(OPENVOL, hist)
    return len(need), done


def cmd_data(args):
    now = now_ist()
    today = now.date().isoformat()
    gate = stage("data", args, now)
    if gate is not None:
        return gate
    checks, notes = [], []
    uni = api.load_universe()
    universe = uni["stocks"]
    if uni.get("stale"):
        notes.append(uni["stale"])
    checks.append({"name": "universe", "ok": True, "detail": "%d F&O stocks" % len(universe)})
    frm = (now.date() - timedelta(days=400)).isoformat()
    nifty_days = [d for d in api.daily(api.NIFTY, frm, today) if d["date"] < today]
    if len(nifty_days) < 60:
        raise RuntimeError("only %d Nifty sessions returned" % len(nifty_days))
    session = nifty_days[-1]["date"]
    index_ret = calc.returns_by_date(nifty_days)
    index_chg20 = calc.pct(nifty_days[-1]["c"], nifty_days[-21]["c"])

    stocks, failed, events = {}, [], []
    for sym in sorted(universe):
        try:
            days = [d for d in api.daily(universe[sym]["eq"], frm, today) if d["date"] < today]
            f = calc.features(days, index_ret)
            if f is None:
                failed.append("%s: short history" % sym)
            else:
                if f["date"] != session:
                    f["stale"] = True
                stocks[sym] = f
                events += calc.gap_events(days)
        except Exception as e:
            failed.append("%s: %s" % (sym, redact(str(e))[:70]))
        time.sleep(api.PACE_S)
    ok = len(stocks) >= 0.7 * len(universe)
    checks.append({"name": "daily_candles", "ok": ok, "detail": "%d ok, %d failed, session %s" % (len(stocks), len(failed), session)})

    # futures open interest: last evening's snapshot if we have it, else whatever the quote shows now
    oi_source = "none"
    eod = store.read_json(D + "eod_latest.json") or {}
    if eod.get("date") == session:
        for sym, f in stocks.items():
            f["oi_chg"] = (eod.get("stocks", {}).get(sym) or {}).get("oi_chg")
        oi_source = "end-of-day snapshot of %s" % session
    else:
        try:
            q = api.quotes([universe[s]["fut"] for s in stocks])
            for sym, f in stocks.items():
                row = q.get(universe[sym]["fut"]) or {}
                f["oi_chg"] = calc.r2(calc.pct(row.get("oi"), row.get("prev_oi")), 1) if row.get("oi") and row.get("prev_oi") else None
            oi_source = "pre-market quote (unverified until the evening snapshot exists)"
        except Exception as e:
            notes.append("futures open interest unavailable: %s" % redact(str(e))[:80])
    for f in stocks.values():
        f["oi_class"] = calc.oi_class(f.get("chg1"), f.get("oi_chg"))

    market = {"nifty": calc.regime(nifty_days)}
    try:
        vix = [d for d in api.daily(api.VIX, (now.date() - timedelta(days=10)).isoformat(), today) if d["date"] < today]
        market["vix"] = vix[-1]["c"] if vix else None
    except Exception as e:
        notes.append("VIX failed: %s" % redact(str(e))[:60])
    try:
        g = ux.global_snapshot()
        market["global"] = {k: {"last": v["last"], "pct": v["pct"]} for k, v in g.items()}
        gap = {"gift": g["gift"]["last"], "gift_change": g["gift"]["pct"]} if "gift" in g else {}
        if gap and uni.get("nifty_fut"):
            fut = (api.quotes([uni["nifty_fut"]]).get(uni["nifty_fut"]) or {}).get("last")
            if fut:
                gap.update(nifty_fut=fut, gift_vs_fut=calc.r2(calc.pct(gap["gift"], fut)))
        market["index_gap"] = gap
    except Exception as e:
        notes.append("global cues failed: %s" % redact(str(e))[:60])
    index_gap = (market.get("index_gap") or {}).get("gift_vs_fut")
    if index_gap is not None and abs(index_gap) > 4:
        notes.append("index gap estimate %.1f%% looks wrong and was ignored" % index_gap)
        index_gap = None
    for f in stocks.values():
        f["est_gap"] = calc.r2(f["beta"] * index_gap) if f.get("beta") is not None and index_gap is not None else None
    try:
        market["flows"] = api.flows()
    except Exception as e:
        notes.append("flows failed: %s" % redact(str(e))[:60])
    try:
        market["sectors"] = [{"name": s["name"], "yday": s.get("yday"), "d5": s.get("d5")} for s in ux.sector_snapshot()["sectors"]]
    except Exception as e:
        notes.append("sectors failed: %s" % redact(str(e))[:60])

    lists = build_lists(stocks, index_chg20)
    opt_ok = 0
    for sym in lists["focus"][:20]:
        try:
            stocks[sym]["opt"] = api.option_move(universe[sym]["eq"], stocks[sym]["close"])
            opt_ok += 1
        except Exception:
            pass
        time.sleep(api.PACE_S)
    checks.append({"name": "options", "ok": True, "detail": "%d of %d focus stocks" % (opt_ok, len(lists["focus"][:20]))})
    try:
        need, done = backfill_openvol(universe, today)
        checks.append({"name": "opening_volume_baseline", "ok": True, "detail": "backfilled %d of %d" % (done, need)})
    except Exception as e:
        notes.append("opening-volume baseline failed: %s" % redact(str(e))[:60])

    out = {"date": today, "session": session, "generated": now.isoformat(timespec="seconds"), "code": git_sha(),
           "rules_version": calc.RULES_VERSION, "failed": failed, "notes": notes, "market": market,
           "gap_table": calc.gap_table(events), "oi_source": oi_source, "lists": lists, "stocks": stocks}
    write_compact(D + "latest.json", out)
    text = brief.render_brief(out)
    write_text(D + "brief/%s.md" % today, text)
    write_text(D + "brief/latest.md", text)
    store.set_status("momentum_data", ok, checks, {"notes": notes, "failed": failed[:15]})
    store.log("momentum data: %d stocks, %d failed, focus %d" % (len(stocks), len(failed), len(lists["focus"])))
    if args.dry_run:
        print(text[:3000])
    return 0 if ok else 1


# ------------------------------------------------------------------ pre-open

def cmd_preopen(args):
    now = now_ist()
    today = now.date().isoformat()
    gate = stage("preopen", args, now)
    if gate is not None:
        return gate
    uni = api.load_universe()
    universe = uni["stocks"]
    by_key = {s["eq"]: sym for sym, s in universe.items()}
    keys = list(by_key) + ([uni["nifty_fut"]] if uni.get("nifty_fut") else [])
    latest = store.read_json(D + "latest.json") or {}
    feats = latest.get("stocks") or {}

    def snapshot():
        q = api.quotes(keys)
        iep = {k: r for k, r in q.items() if r.get("iep") and r.get("prev")}
        return q, iep

    q, iep, source = {}, {}, "indicative"
    for attempt in range(4):
        try:
            q2, iep2 = snapshot()
            if len(iep2) >= len(iep):
                q, iep = q2, iep2
        except Exception as e:
            store.log("momentum preopen: quote attempt %d failed: %s" % (attempt + 1, e))
        if attempt < 3:
            time.sleep(25)
    price = {k: r["iep"] for k, r in iep.items()}
    if len(price) < 0.5 * len(by_key):
        # no indicative prices in the quote: wait for the auction to match and read the opening trade
        time.sleep(50)
        q = api.quotes(keys)
        price = {k: r["last"] for k, r in q.items() if r.get("traded_on") == today and r.get("last") and r.get("prev")}
        source = "opening trade"
        if len(price) < 0.5 * len(by_key):
            price = {k: r["open"] for k, r in q.items() if r.get("ohlc_date") == today and r.get("open") and r.get("prev")}
            source = "opening price"
    if len(price) < 0.3 * len(by_key):
        raise RuntimeError("no pre-open prices in the quotes (%d of %d). Fields seen: %s"
                           % (len(price), len(by_key), sorted(k for k, v in (next(iter(q.values()), {}) or {}).items() if v is not None)))
    gaps = {}
    for k, px in price.items():
        sym = by_key.get(k)
        if not sym:
            continue
        g = calc.pct(px, q[k]["prev"])
        f = feats.get(sym) or {}
        gaps[sym] = {"symbol": sym, "gap": calc.r2(g), "price": px, "prev": q[k]["prev"], "chg1": f.get("chg1"),
                     "gap_atr": calc.r2(abs(g) / f["atr_pct"], 1) if f.get("atr_pct") else None}
    rows = sorted(gaps.values(), key=lambda r: r["gap"])
    index_gap = None
    if uni.get("nifty_fut") in price:
        index_gap = calc.r2(calc.pct(price[uni["nifty_fut"]], q[uni["nifty_fut"]]["prev"]))
    table = latest.get("gap_table") or {}
    picks = []
    for p in load_picks(today):
        g = (gaps.get(p["symbol"]) or {}).get("gap")
        row = dict(p, gap=g, verdict=calc.gap_verdict(p["direction"], g, (feats.get(p["symbol"]) or {}).get("atr_pct")))
        b = calc.bucket_of(abs(g)) if g is not None else None
        t = table.get("%s %s" % ("up" if (g or 0) > 0 else "down", b)) if b else None
        if t:
            row.update(cont=t["cont"], cont_n=t["n"])
        picks.append(row)
    out = {"date": today, "time": now_ist().strftime("%d %b %H:%M"), "source": source,
           "source_label": {"indicative": "indicative prices", "opening trade": "opening auction trades",
                            "opening price": "opening prices"}[source],
           "index_gap": index_gap, "coverage": "%d of %d" % (len(gaps), len(by_key)),
           "up": [r for r in reversed(rows) if r["gap"] >= 0.5][:8], "down": [r for r in rows if r["gap"] <= -0.5][:8],
           "picks": picks, "picks_note": None if picks else "No picks file for today yet, so this is the gap list only."}
    write_compact(D + "gaps/%s.json" % today, dict(out, all=gaps))
    telegram.send(brief.preopen_message(out), args.dry_run)
    store.set_status("momentum_preopen", True, [{"name": "prices", "ok": True, "detail": "%s, %s" % (source, out["coverage"])}])
    store.log("momentum preopen: %s, %s, %d picks" % (source, out["coverage"], len(picks)))
    return 0


# ------------------------------------------------------------------ opening checks

def touch_status(p, row):
    """Where a pick stands against its confirm and cancel levels, from the day's high and low so far."""
    up = p["direction"] == "UP"
    try:
        confirm, cancel = float(p["confirm"]), float(p["cancel"])
    except (TypeError, ValueError):
        return "no levels"
    hit_c = row["high"] >= confirm if up else row["low"] <= confirm
    hit_x = row["low"] <= cancel if up else row["high"] >= cancel
    if hit_c and hit_x:
        return "touched both levels"
    if hit_c:
        return "CONFIRMED (%s)" % ("above" if up else "below") + " %g" % confirm
    if hit_x:
        return "CANCELLED at %g" % cancel
    return "waiting (%g confirms)" % confirm


def cmd_check(args, label):
    cmd = "check" + label
    now = now_ist()
    today = now.date().isoformat()
    gate = stage(cmd, args, now)
    if gate is not None:
        return gate
    uni = api.load_universe()
    universe = uni["stocks"]
    by_key = {s["eq"]: sym for sym, s in universe.items()}
    q = api.quotes(list(by_key))
    rows = {}
    for k, r in q.items():
        sym = by_key.get(k)
        if sym and r.get("last") and r.get("prev") and r.get("open") and r.get("high") and r.get("low"):
            rows[sym] = r
    if len(rows) < 0.5 * len(by_key):
        raise RuntimeError("quotes for only %d of %d stocks" % (len(rows), len(by_key)))
    hist = store.read_json(OPENVOL, {}) or {}
    h = hist.setdefault(label, {})
    in_play, relvol = [], {}
    for sym, r in rows.items():
        base = calc.median([h[d].get(sym) for d in h if d < today])
        n = sum(1 for d in h if d < today and h[d].get(sym))
        if base and n >= 5 and r.get("volume"):
            relvol[sym] = r["volume"] / base
    if (now.time() <= WINDOWS[cmd][1]) and not args.force:
        h[today] = {sym: r["volume"] for sym, r in rows.items() if r.get("volume")}
        for day in sorted(h)[:-20]:
            del h[day]
        write_compact(OPENVOL, hist)
    for sym, rv in sorted(relvol.items(), key=lambda x: -x[1]):
        if rv < IN_PLAY_RELVOL:
            break
        r = rows[sym]
        in_play.append({"symbol": sym, "relvol": calc.r2(rv, 1), "chg": calc.r2(calc.pct(r["last"], r["prev"])),
                        "from_open": calc.r2(calc.pct(r["last"], r["open"])), "high": r["high"], "low": r["low"],
                        "open": r["open"], "last": r["last"]})
    picks = []
    for p in load_picks(today):
        r = rows.get(p["symbol"])
        if r:
            picks.append(dict(p, from_open=calc.r2(calc.pct(r["last"], r["open"])), status=touch_status(p, r),
                              relvol=calc.r2(relvol.get(p["symbol"]), 1)))
    out = {"date": today, "label": label, "time": now.strftime("%d %b %H:%M"), "in_play": in_play[:8], "picks": picks,
           "in_play_note": None if relvol else "Usual opening volume is still being measured; the in-play list starts once it is."}
    write_compact(D + "checks/%s_%s.json" % (today, label), out)
    if label == "5" and in_play:
        feats = (store.read_json(D + "latest.json") or {}).get("stocks") or {}
        logged = {(r["date"], r["symbol"]) for r in store.load(D + "inplay.jsonl")}
        new = []
        for r in in_play[:8]:
            atr_pct = (feats.get(r["symbol"]) or {}).get("atr_pct")
            if (today, r["symbol"]) in logged or not atr_pct or r["last"] == r["open"]:
                continue
            new.append({"date": today, "symbol": r["symbol"], "direction": "UP" if r["last"] > r["open"] else "DOWN",
                        "or_high": r["high"], "or_low": r["low"], "relvol": r["relvol"],
                        "atr": calc.r2(atr_pct / 100 * r["last"]), "rules_version": calc.RULES_VERSION, "trade": None})
        store.append(new, D + "inplay.jsonl")
    telegram.send(brief.check_message(out), args.dry_run)
    store.set_status("momentum_" + cmd, True, [{"name": "quotes", "ok": True, "detail": "%d stocks, %d with a volume baseline, %d in play"
                                                % (len(rows), len(relvol), len(in_play))}])
    store.log("momentum %s: %d in play, %d picks" % (cmd, len(in_play), len(picks)))
    return 0


# ------------------------------------------------------------------ end of day

def session_bars(key, today, after=None):
    bars = [b for b in api.intraday(key, 1) if b["date"] == today and b["ts"].time() >= dtime(9, 15)]
    return [b for b in bars if b["ts"].time() >= after] if after else bars


def fill_swing(rows, universe, today):
    """Five-session result for swing picks whose window has closed."""
    todo = [r for r in rows if r.get("horizon") in ("swing", "both") and r.get("ret_5d") is None
            and r.get("open") and r["date"] < today and r["symbol"] in universe]
    if not todo:
        return 0
    start = min(r["date"] for r in todo)
    idx = [d for d in api.daily(api.NIFTY, start, today) if d["date"] <= today]
    done = 0
    for r in todo:
        try:
            days = [d for d in api.daily(universe[r["symbol"]]["eq"], r["date"], today) if d["date"] >= r["date"]]
            if len(days) < 5:
                continue
            end = days[4]
            s = 1 if r["direction"] == "UP" else -1
            r["ret_5d"] = calc.r2(calc.pct(end["c"], r["open"]) * s)
            i0 = next((d for d in idx if d["date"] == r["date"]), None)
            i1 = next((d for d in idx if d["date"] == end["date"]), None)
            if i0 and i1:
                r["alpha_5d"] = calc.r2(r["ret_5d"] - calc.pct(i1["c"], i0["o"]) * s)
            done += 1
        except Exception:
            pass
        time.sleep(api.PACE_S)
    return done


def cmd_eod(args):
    now = now_ist()
    today = now.date().isoformat()
    gate = stage("eod", args, now)
    if gate is not None:
        return gate
    checks = []
    uni = api.load_universe()
    universe = uni["stocks"]
    latest = store.read_json(D + "latest.json") or {}

    # 1. futures open interest for tomorrow's data file
    try:
        q = api.quotes([s["eq"] for s in universe.values()] + [s["fut"] for s in universe.values()])
        snap = {}
        for sym, s in universe.items():
            e, f = q.get(s["eq"]) or {}, q.get(s["fut"]) or {}
            chg = calc.pct(e.get("last"), e.get("prev")) if e.get("last") and e.get("prev") else None
            oi_chg = calc.pct(f.get("oi"), f.get("prev_oi")) if f.get("oi") and f.get("prev_oi") else None
            snap[sym] = {"close": e.get("last"), "chg": calc.r2(chg), "oi": f.get("oi"), "oi_chg": calc.r2(oi_chg, 1)}
        with_oi = sum(1 for v in snap.values() if v["oi_chg"] is not None)
        write_compact(D + "eod_latest.json", {"date": today, "generated": now.isoformat(timespec="seconds"), "stocks": snap})
        checks.append({"name": "open_interest", "ok": with_oi > 0.5 * len(snap), "detail": "%d of %d futures" % (with_oi, len(snap))})
    except Exception as e:
        checks.append({"name": "open_interest", "ok": False, "detail": redact(str(e))[:120]})

    # 2. score today's picks
    rows = store.load(D + "scores.jsonl")
    have = {(r["date"], r["symbol"], r["horizon"]) for r in rows}
    picks = [p for p in load_picks(today) if (today, p["symbol"], p["horizon"]) not in have and p["symbol"] in universe]
    gaps = (store.read_json(D + "gaps/%s.json" % today) or {}).get("all") or {}
    feats = latest.get("stocks") or {}
    regime = ((latest.get("market") or {}).get("nifty") or {}).get("tag") if latest.get("date") == today else None
    todays, errors = [], 0
    if picks:
        idx = session_bars(api.NIFTY, today)
        for p in picks:
            try:
                bars = session_bars(universe[p["symbol"]]["eq"], today)
                if len(bars) < 30:
                    raise RuntimeError("only %d bars" % len(bars))
                res = calc.day_outcome(p["direction"], bars[0]["o"], max(b["h"] for b in bars), min(b["l"] for b in bars),
                                       bars[-1]["c"], idx[0]["o"] if idx else None, idx[-1]["c"] if idx else None)
                g = (gaps.get(p["symbol"]) or {}).get("gap")
                row = dict(p, date=today, regime=regime, gap=g, rules_version=calc.RULES_VERSION, code=git_sha(),
                           gap_verdict=calc.gap_verdict(p["direction"], g, (feats.get(p["symbol"]) or {}).get("atr_pct")), **res)
                row["trade"] = calc.walk(bars, p["direction"], p["confirm"], p["cancel"], p["target"]) \
                    if p["horizon"] in ("intraday", "both") else {"status": "not_intraday"}
                todays.append(row)
            except Exception as e:
                errors += 1
                store.log("momentum eod: could not score %s: %s" % (p["symbol"], e))
            time.sleep(api.PACE_S)
        rows += todays
    checks.append({"name": "picks", "ok": errors == 0, "detail": "%d scored, %d failed" % (len(todays), errors)})
    try:
        n5 = fill_swing(rows, universe, today)
        checks.append({"name": "swing_followup", "ok": True, "detail": "%d filled" % n5})
    except Exception as e:
        checks.append({"name": "swing_followup", "ok": False, "detail": redact(str(e))[:120]})
    store.rewrite(rows, D + "scores.jsonl")

    # 3. the in-play breakout forward test
    inplay = store.load(D + "inplay.jsonl")
    for r in inplay:
        if r["date"] != today or r.get("trade") or r["symbol"] not in universe:
            continue
        try:
            bars = session_bars(universe[r["symbol"]]["eq"], today, after=dtime(9, 20))
            up = r["direction"] == "UP"
            level = r["or_high"] if up else r["or_low"]
            stop = level - ORB_STOP_ATR * r["atr"] if up else level + ORB_STOP_ATR * r["atr"]
            r["trade"] = calc.walk(bars, r["direction"], level, stop)
        except Exception as e:
            store.log("momentum eod: in-play %s failed: %s" % (r["symbol"], e))
        time.sleep(api.PACE_S)
    store.rewrite(inplay, D + "inplay.jsonl")
    ip_tally = calc.tally([dict(r, right=False) for r in inplay if r.get("trade")]) if inplay else None

    sc = calc.scorecard(rows)
    n_days = len({r["date"] for r in rows})
    store.write_json(D + "scorecard.json", {"updated": now.isoformat(timespec="seconds"), "sessions": n_days,
                                            "rules_version": calc.RULES_VERSION, "picks": sc, "in_play": ip_tally})
    write_text(D + "scorecard.md", brief.render_scorecard(sc, ip_tally, n_days))
    msg = {"date": now.strftime("%d %b"), "today": todays, "scorecard": sc, "inplay": ip_tally if ip_tally and ip_tally["n"] else None,
           "note": None if todays else ("Today's picks were already scored." if load_picks(today) else "No picks file was logged today.")}
    telegram.send(brief.eod_message(msg), args.dry_run)
    ok = all(c["ok"] for c in checks)
    store.set_status("momentum_eod", ok, checks)
    store.log("momentum eod: %d picks scored, %d total" % (len(todays), len(rows)))
    return 0


# ------------------------------------------------------------------ self-test

def cmd_selftest(args):
    now = now_ist()
    today = now.date().isoformat()
    checks = []

    def check(name, fn, required=True):
        try:
            checks.append({"name": name, "ok": True, "required": required, "detail": redact(str(fn()))[:240]})
        except Exception as e:
            checks.append({"name": name, "ok": False, "required": required, "detail": redact("%s: %s" % (type(e).__name__, e))[:240]})

    state = {}

    def universe():
        state["uni"] = api.load_universe(force=True)
        s = state["uni"]["stocks"]
        return "%d F&O stocks, Nifty future %s, e.g. %s" % (len(s), state["uni"].get("nifty_fut"), sorted(s)[:3])

    def one():
        sym = "RELIANCE" if "RELIANCE" in state["uni"]["stocks"] else sorted(state["uni"]["stocks"])[0]
        return sym, state["uni"]["stocks"][sym]

    def quote_fields():
        sym, s = one()
        q = api.quotes([s["eq"], s["fut"]])
        e, f = q[s["eq"]], q[s["fut"]]
        return "%s last %s prev %s volume %s iep %s traded_on %s | future oi %s prev_oi %s" % (
            sym, e["last"], e["prev"], e["volume"], e["iep"], e["traded_on"], f["oi"], f["prev_oi"])

    def candles():
        sym, s = one()
        d = api.daily(s["eq"], (now.date() - timedelta(days=40)).isoformat(), today)
        m = api.minutes(s["eq"], 5, (now.date() - timedelta(days=6)).isoformat(), today)
        if not d or not d[-1]["v"]:
            raise RuntimeError("daily candles carry no volume")
        return "%s: %d daily (last volume %.0f), %d five-minute bars" % (sym, len(d), d[-1]["v"], len(m))

    def options():
        sym, s = one()
        spot = api.quotes([s["eq"]])[s["eq"]]["last"]
        return "%s %s" % (sym, api.option_move(s["eq"], spot))

    def flows():
        f = api.flows()
        if "fii_cash" not in f and "dii_cash" not in f:
            raise RuntimeError(str(f))
        return f

    def data_dir():
        write_compact(D + "write_test.json", {"ts": now.isoformat()})
        return "writable"

    check("fo_universe", universe)
    if state.get("uni"):
        check("quote_fields", quote_fields)
        check("candles_with_volume", candles)
        check("stock_option_chain", options, required=False)
    check("fii_dii", flows, required=False)
    check("data_dir", data_dir)
    lines = ["%s %s: %s" % ("PASS" if c["ok"] else ("FAIL" if c["required"] else "WARN"), c["name"], c["detail"]) for c in checks]
    if not args.no_telegram:
        def tg():
            telegram.send("<b>Momentum self-test</b> (%s)\n<pre>%s</pre>" % (git_sha(), "\n".join(telegram.esc(l[:300]) for l in lines)), args.dry_run)
            return "test message sent"
        check("telegram_send", tg)
        lines.append("%s telegram_send: %s" % ("PASS" if checks[-1]["ok"] else "FAIL", checks[-1]["detail"]))
    ok = all(c["ok"] for c in checks if c["required"])
    store.set_status("momentum_selftest", ok, checks)
    print("\n".join(lines))
    print("\nMOMENTUM SELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="momentum.run", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["data", "preopen", "check5", "check30", "eod", "selftest"])
    ap.add_argument("--dry-run", action="store_true", help="print Telegram messages instead of sending")
    ap.add_argument("--force", action="store_true", help="run outside the normal time window")
    ap.add_argument("--no-telegram", action="store_true", help="selftest: skip the Telegram test message")
    args = ap.parse_args(argv)
    fn = {"data": cmd_data, "preopen": cmd_preopen, "check5": lambda a: cmd_check(a, "5"),
          "check30": lambda a: cmd_check(a, "30"), "eod": cmd_eod, "selftest": cmd_selftest}[args.command]
    try:
        return fn(args)
    except Exception as e:
        store.log("momentum %s FAILED: %s\n%s" % (args.command, e, traceback.format_exc()[-1500:]))
        try:
            store.set_status("momentum_" + args.command, False, [{"name": "fatal", "ok": False, "detail": redact(str(e))[:300]}])
        except Exception:
            pass
        if args.command in ("preopen", "check5", "check30", "eod"):
            try:
                telegram.send("<b>Momentum: the %s run failed</b>\n<i>%s</i>" % (args.command, telegram.esc(redact(str(e))[:300])), args.dry_run)
            except Exception:
                pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
