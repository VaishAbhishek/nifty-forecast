"""Entry point.  python3 -m momentum.run {data|preopen|check5|check30|eod|selftest}

data     08:10  numbers for every F&O stock -> momentum/latest.json and momentum/brief/<date>.md
preopen  09:07  indicative opening prices -> Telegram: the real gaps, and each pick against its gap
check5   09:20  in-play stocks (3x usual volume) through the five trade gates -> TRADE alerts
check30  09:47  the same after 30 minutes
watch    every minute 09:16-15:16: alerts on engine trades (entry 09:20-10:15, half at 2R,
         VWAP trail, out by 15:00, daily stop at -3R) and on swing picks
eod      16:05  scores the day's picks, updates the scorecard, saves futures open interest

Advisory and read-only. It places no orders and does not touch the EMA bot or the forecast rules.
"""
import argparse
import json
import os
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
IN_PLAY_RELVOL = 3.0   # rules v2: at least 3x usual opening volume, and only the top IN_PLAY_TOP
IN_PLAY_TOP = 10
SWING_TOP = 12
RISK_PER_TRADE = int(os.environ.get("NF_RISK_PER_TRADE", "20000"))   # rupees lost if a trade hits its stop
OPTION_SCAN = 40       # stocks whose options are checked in the 08:10 data job


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
                    "confirm": p.get("confirm"), "cancel": p.get("cancel"), "target": p.get("target"),
                    "surprise_pct": p.get("surprise_pct"),
                    # rules v3 watchlist fields: news freshness and size, theme for one-trade-per-theme
                    "fresh": bool(p.get("fresh")), "materiality": p.get("materiality"),
                    "theme": p.get("theme"), "news": str(p.get("news") or "")[:300]})
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


def build_swing(stocks):
    """Swing candidates: strongest (or weakest) 6- and 12-month momentum, adjusted for volatility,
    close to the 52-week high (or low), in a tight base or orderly pullback.

    Rules version 2. Evidence: momentum over 3-12 months persists in Indian stocks while
    1-4 week moves tend to reverse; nearness to the 52-week high predicts returns
    (George and Hwang 2004); NSE's momentum indices rank on volatility-adjusted
    6- and 12-month returns.
    """
    z6 = calc.zscores({s: f.get("mom6") for s, f in stocks.items()})
    z12 = calc.zscores({s: f.get("mom12") for s, f in stocks.items()})
    score = {}
    for sym in stocks:
        parts = [z for z in (z6.get(sym), z12.get(sym)) if z is not None]
        if parts:
            score[sym] = sum(parts) / len(parts)
    ranked = sorted(score, key=score.get)
    n = len(ranked)
    for i, sym in enumerate(ranked):
        stocks[sym]["mom_score"] = calc.r2(score[sym])
        stocks[sym]["mom_pct"] = round(100 * i / max(1, n - 1))
    up = [s for s in ranked[::-1] if stocks[s]["mom_pct"] >= 70 and stocks[s].get("setup_up")
          and (stocks[s].get("from_52w_high") or -99) >= -15]
    down = [s for s in ranked if stocks[s]["mom_pct"] <= 30 and stocks[s].get("setup_down")
            and (stocks[s].get("from_52w_low") or 99) <= 15]
    return {"swing_up": up[:SWING_TOP], "swing_down": down[:SWING_TOP // 2]}


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

    stocks, failed, events, rets = {}, [], [], {}
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
                rets[sym] = dict(list(calc.returns_by_date(days).items())[-61:])
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
        vix = [d for d in api.daily(api.VIX, (now.date() - timedelta(days=130)).isoformat(), today) if d["date"] < today]
        market["vix"] = vix[-1]["c"] if vix else None
        market["panic"] = calc.panic_state(nifty_days, vix)
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
    # peers by co-movement, industries from NSE's list, and industry strength among F&O stocks
    try:
        peers = calc.peer_map(rets, index_ret)
        for sym, pr in peers.items():
            stocks[sym]["peers"] = pr
        checks.append({"name": "peers", "ok": True, "detail": "%d stocks with peers" % len(peers)})
    except Exception as e:
        notes.append("peer map failed: %s" % redact(str(e))[:60])
    ind, ind_source = api.industries()
    for sym, f in stocks.items():
        if ind.get(sym):
            f["industry"] = ind[sym]
    sectors = calc.sector_table(stocks, ind) if ind else []
    rank = {r["industry"]: r["rank"] for r in sectors}
    for f in stocks.values():
        if f.get("industry") in rank:
            f["industry_rank"] = rank[f["industry"]]
    market["industries"] = {"source": ind_source, "count": len(sectors), "table": sectors}
    if not ind:
        notes.append("no industry list: NSE download failed and config/stock_industries.csv is missing")
    swing = build_swing(stocks)
    lists.update(swing)
    scan = list(dict.fromkeys(lists["focus"] + swing["swing_up"] + swing["swing_down"]))[:OPTION_SCAN]
    opt_ok = 0
    for sym in scan:
        try:
            o = api.option_move(universe[sym]["eq"], stocks[sym]["close"])
            if o.get("atm_iv") and stocks[sym].get("rv20"):
                o["iv_vs_rv"] = calc.r2(o["atm_iv"] / stocks[sym]["rv20"])
            stocks[sym]["opt"] = o
            opt_ok += 1
        except Exception:
            pass
        time.sleep(api.PACE_S)
    checks.append({"name": "options", "ok": True, "detail": "%d of %d focus and swing stocks" % (opt_ok, len(scan))})
    try:
        need, done = backfill_openvol(universe, today)
        checks.append({"name": "opening_volume_baseline", "ok": True, "detail": "backfilled %d of %d" % (done, need)})
    except Exception as e:
        notes.append("opening-volume baseline failed: %s" % redact(str(e))[:60])

    try:
        n = capture_filings(universe, session, now)
        checks.append({"name": "filings", "ok": True, "detail": "%d F&O filings since the last close" % n})
    except Exception as e:
        notes.append("BSE filings not read (%s); the report's web search is the fallback" % redact(str(e))[:80])

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


def capture_filings(universe, session, now):
    """Exchange filings for F&O stocks since the last session's close -> momentum/news/<date>.json.

    Fresh = published after 15:30 on the last session, so the market has not traded it yet.
    The morning report reads this file first, before any web search.
    """
    today = now.date().isoformat()
    items = api.bse_announcements(session, today)
    cutoff = session + "T15:30"
    rows = []
    for it in calc.match_filings(items, universe):
        t = str(it.get("time") or "")
        rows.append(dict(it, fresh=t[:16].replace(" ", "T") >= cutoff if t else None))
    rows.sort(key=lambda r: str(r.get("time") or ""), reverse=True)
    write_compact(D + "news/%s.json" % today, {"date": today, "since": cutoff, "source": "BSE announcements",
                                              "seen": len(items), "fo": len(rows), "items": rows})
    return len(rows)


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
    imbalance = {}
    for k, r in q.items():
        b, s_ = r.get("buy_qty"), r.get("sell_qty")
        if by_key.get(k) and b is not None and s_ is not None and b + s_ > 0:
            imbalance[by_key[k]] = calc.r2((b - s_) / (b + s_))
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
           "picks": picks, "picks_note": None if picks else "WARNING: no picks file arrived from the morning report, so today's picks will not be checked or scored."}
    try:
        out["auction"] = auction_read(by_key, keys, today, now, imbalance, gaps, args)
    except Exception as e:
        out["auction"] = {"error": redact(str(e))[:120]}
    write_compact(D + "gaps/%s.json" % today, dict(out, all=gaps))
    telegram.send(brief.preopen_message(out), args.dry_run)
    store.set_status("momentum_preopen", True, [{"name": "prices", "ok": True, "detail": "%s, %s" % (source, out["coverage"])}])
    store.log("momentum preopen: %s, %s, %d picks" % (source, out["coverage"], len(picks)))
    return 0


AUCTION_RELVOL = 3.0
AUCTION_REREADS = 2        # plumbing: extra quote reads after the match (not a rule threshold)
AUCTION_REREAD_WAIT = 20   # seconds between them


def auction_read(by_key, keys, today, now, imbalance, gaps, args):
    """Opening-auction volume against its usual level, read after the 09:08 match.

    A stock with several times its usual auction volume is in play before 09:15.
    Imbalance is (buy - sell) / (buy + sell) of the unmatched orders seen earlier.
    """
    wait = (datetime.combine(now.date(), dtime(9, 8, 30), now.tzinfo) - now_ist()).total_seconds()
    if 0 < wait < 180:
        time.sleep(wait)
    q = api.quotes(keys)
    # Upstox updates the auction trade a few seconds to a minute after the 09:08 match, and not for every
    # stock at once (26 Nov: 114 of 218 dated today at 09:08:40). Re-read while under 90% have today's trade.
    for _ in range(AUCTION_REREADS):
        today_n = sum(1 for k, r in q.items() if by_key.get(k) and r.get("traded_on") == today)
        if today_n >= 0.9 * len(by_key) or args.dry_run:
            break
        time.sleep(AUCTION_REREAD_WAIT)
        try:
            q2 = api.quotes(keys)
        except Exception as e:
            store.log("momentum preopen: auction re-read failed: %s" % e)
            break
        if sum(1 for k, r in q2.items() if by_key.get(k) and r.get("traded_on") == today) >= today_n:
            q = q2
    vol = {by_key[k]: r["volume"] for k, r in q.items() if by_key.get(k) and r.get("volume") and r.get("traded_on") == today}
    # diagnostics for when no auction volume is seen: is the field empty, or is the trade date not today?
    seen = [r for k, r in q.items() if by_key.get(k)]
    with_vol = [r for r in seen if r.get("volume")]
    dates = {}
    for r in with_vol:
        d = str(r.get("traded_on"))
        dates[d] = dates.get(d, 0) + 1
    hist = store.read_json(OPENVOL, {}) or {}
    h = hist.setdefault("pre", {})
    rel = {}
    for sym, v in vol.items():
        prior = [h[d].get(sym) for d in h if d < today]
        base = calc.median(prior)
        if base and sum(1 for x in prior if x) >= 5:
            rel[sym] = v / base
    if vol and not args.force:
        h[today] = vol
        for day in sorted(h)[:-20]:
            del h[day]
        write_compact(OPENVOL, hist)
    top_ = []
    for sym, rv in sorted(rel.items(), key=lambda x: -x[1]):
        if rv < AUCTION_RELVOL or len(top_) >= 10:
            break
        top_.append({"symbol": sym, "relvol": calc.r2(rv, 1), "gap": (gaps.get(sym) or {}).get("gap"),
                     "imbalance": imbalance.get(sym)})
    return {"stocks_with_volume": len(vol), "with_baseline": len(rel), "in_play": top_,
            "imbalance": imbalance, "quotes_read": len(seen), "quotes_with_volume": len(with_vol), "volume_trade_dates": dates,
            "read_at": now_ist().strftime("%H:%M:%S"),
            "note": None if rel else ("No auction volume for today in the quotes at %s (%d of %d quotes carry a volume; trade dates %s)."
                                      % (now_ist().strftime("%H:%M:%S"), len(with_vol), len(seen), dates or "none")
                                      if not vol else "Usual auction volume is still being measured (needs 5 sessions).")}


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


def plan_option(p, universe, feats):
    """Live contract for an intraday pick: expiry with at least five sessions left, delta near 0.55."""
    u = universe.get(p["symbol"])
    if not u:
        return None
    f = feats.get(p["symbol"]) or {}
    try:
        risk = abs(float(p["confirm"]) - float(p["cancel"]))
    except (TypeError, ValueError):
        risk = (f.get("atr_pct") or 0) / 100 * (f.get("close") or 0) * 0.5 or None
    expiry = api.pick_expiry(api.option_expiries(u["eq"]))
    if not expiry:
        return None
    plan = calc.option_plan(api.option_chain(u["eq"], expiry), p["direction"], u.get("lot"), risk,
                            rv20=f.get("rv20"), expiry=expiry, sessions_left=api.sessions_until(expiry))
    if plan:
        plan["risk_per_share"] = calc.r2(risk)
        sz = calc.size_lots(plan.get("risk_per_lot"), RISK_PER_TRADE, plan.get("cost_per_lot"))
        if sz:
            plan["size"] = sz
    return plan


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
    q = api.quotes(list(by_key) + [api.NIFTY])
    nifty_q = q.get(api.NIFTY) or {}
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
        if rv < IN_PLAY_RELVOL or len(in_play) >= IN_PLAY_TOP:
            break
        r = rows[sym]
        in_play.append({"symbol": sym, "relvol": calc.r2(rv, 1), "chg": calc.r2(calc.pct(r["last"], r["prev"])),
                        "from_open": calc.r2(calc.pct(r["last"], r["open"])), "high": r["high"], "low": r["low"],
                        "open": r["open"], "last": r["last"]})
    picks = []
    feats = (store.read_json(D + "latest.json") or {}).get("stocks") or {}
    earlier = {}
    if label == "30":
        earlier = {(x["symbol"], x["horizon"]): x.get("option") for x in
                   (store.read_json(D + "checks/%s_5.json" % today) or {}).get("picks") or []}
    for p in load_picks(today):
        r = rows.get(p["symbol"])
        if not r:
            continue
        row = dict(p, from_open=calc.r2(calc.pct(r["last"], r["open"])), status=touch_status(p, r),
                   relvol=calc.r2(relvol.get(p["symbol"]), 1))
        if p["horizon"] in ("intraday", "both"):
            opt = earlier.get((p["symbol"], p["horizon"]))
            try:
                if not opt:
                    opt = plan_option(p, universe, feats)
                    time.sleep(api.PACE_S)
                elif opt.get("key"):
                    opt = dict(opt, now=(api.quotes([opt["key"]]).get(opt["key"]) or {}).get("last"))
            except Exception as e:
                opt = {"error": redact(str(e))[:100]}
            row["option"] = opt
        picks.append(row)
    out = {"date": today, "label": label, "time": now.strftime("%d %b %H:%M"), "in_play": in_play, "picks": picks,
           "in_play_note": None if relvol else "Usual opening volume is still being measured; the in-play list starts once it is."}
    if label == "5":
        try:
            out["engine"] = run_engine(today, now, in_play, relvol, rows, nifty_q, universe, feats, args)
        except Exception as e:
            out["engine"] = {"error": redact(str(e))[:160]}
            store.log("momentum engine failed: %s\n%s" % (e, traceback.format_exc()[-800:]))
    write_compact(D + "checks/%s_%s.json" % (today, label), out)
    if label == "5" and in_play:
        feats = (store.read_json(D + "latest.json") or {}).get("stocks") or {}
        logged = {(r["date"], r["symbol"]) for r in store.load(D + "inplay.jsonl")}
        new = []
        for r in in_play:
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


def run_engine(today, now, in_play, relvol, rows, nifty_q, universe, feats, args):
    """Rules v3, 09:20: every in-play stock through the five gates; passes become TRADE alerts."""
    watch = {p["symbol"]: p for p in load_picks(today) if p["horizon"] in ("intraday", "both") and p["symbol"] in universe}
    evaluated = []
    for rank, r in enumerate(in_play, 1):
        sym = r["symbol"]
        f = feats.get(sym) or {}
        q = rows[sym]
        news = watch.get(sym)
        pre = calc.trade_gates(sym, q, f.get("atr_pct"), r["relvol"], rank, nifty_q, news, option={"grade": "ok"})
        opt = None
        tried = False
        if pre["direction"] and all(g["ok"] for g in pre["gates"][:4]) and pre.get("risk"):
            tried = True
            try:
                opt = plan_option({"symbol": sym, "direction": pre["direction"], "confirm": pre["entry"],
                                   "cancel": pre["stop"]}, universe, feats)
                time.sleep(api.PACE_S)
            except Exception as e:
                opt = None
                store.log("momentum engine: option for %s failed: %s" % (sym, e))
        res = calc.trade_gates(sym, q, f.get("atr_pct"), r["relvol"], rank, nifty_q, news, option=opt)
        if not tried:
            # the option is only looked up once the first four gates pass; say so instead of "no option contract found"
            for g in res["gates"]:
                if g["gate"] == "tradeable" and not g["ok"]:
                    g["why"] = "not checked (an earlier gate failed)"
        res.update(option=opt, industry=f.get("industry"), theme=(news or {}).get("theme") or f.get("industry"),
                   news_text=(news or {}).get("news"), rules_version=calc.RULES_VERSION)
        evaluated.append(res)
    passed = calc.rank_trades([e for e in evaluated if e["pass"]])
    trades, same_theme = calc.one_per_theme(passed, lambda s: next((e["theme"] for e in evaluated if e["symbol"] == s), None))
    for d in same_theme:
        d["pass"] = False
        d["gates"].append({"gate": "theme", "ok": False, "why": "same theme as a higher-ranked trade"})
    watch_only = [p for s, p in watch.items() if s not in {e["symbol"] for e in evaluated}]
    eng = {"date": today, "time": now.strftime("%H:%M"), "rules_version": calc.RULES_VERSION, "risk_per_trade": RISK_PER_TRADE,
           "nifty_from_open": calc.r2(calc.pct(nifty_q["last"], nifty_q["open"])) if nifty_q.get("open") and nifty_q.get("last") else None,
           "trades": trades, "rejected": [e for e in evaluated if not e["pass"]],
           "watchlist_not_in_play": [{"symbol": p["symbol"], "direction": p["direction"],
                                      "relvol": calc.r2(relvol.get(p["symbol"]), 1)} for p in watch_only]}
    write_compact(D + "trades/%s.json" % today, eng)
    telegram.send(brief.engine_message(eng), args.dry_run)
    return {"trades": len(trades), "rejected": len(eng["rejected"])}


# ------------------------------------------------------------------ live watch

WATCH_FROM, WATCH_TO = dtime(9, 16), dtime(15, 16)
ENTRY_FROM = dtime(9, 20)    # rules v3: never before the five-minute opening range is complete
ENTRY_UNTIL = dtime(10, 15)
EXIT_BY = dtime(15, 0)


def trading_day_cached(now):
    """trading_day() once per date; the watcher runs every minute."""
    path = "cache/tradingday.json"
    c = store.read_json(path, {}) or {}
    day = now.date().isoformat()
    if c.get("date") != day:
        ok, why = trading_day(now)
        c = {"date": day, "ok": ok, "why": why}
        write_compact(path, c)
    return c["ok"], c["why"]


def watch_events(p, last, state, now):
    """New alerts for one pick from its latest price. Mutates state; returns alert texts."""
    out = []
    up = p["direction"] == "UP"
    try:
        confirm, cancel = float(p["confirm"]), float(p["cancel"])
    except (TypeError, ValueError):
        return out
    target = p.get("target")
    beyond = (lambda x: last >= x) if up else (lambda x: last <= x)
    before = (lambda x: last <= x) if up else (lambda x: last >= x)
    st = state.get("stage", "waiting")
    if p["horizon"] == "swing":
        if st == "waiting" and now.time() >= dtime(15, 5) and beyond(confirm):
            state["stage"] = "flagged"
            out.append("SWING %s %s: at %.2f, beyond its trigger %.2f. Enters only if it CLOSES there; stop %.2f."
                       % (p["symbol"], p["direction"], last, confirm, cancel))
        return out
    if st == "waiting":
        if now.time() < ENTRY_FROM:
            return out
        if before(cancel):
            state["stage"] = "done"
            out.append("CANCELLED %s %s: %.2f hit the cancel level %.2f before confirming. No trade."
                       % (p["symbol"], p["direction"], last, cancel))
        elif beyond(confirm):
            state["stage"] = "entered" if now.time() <= ENTRY_UNTIL else "late"
            if state["stage"] == "entered":
                out.append("ENTRY %s %s: %.2f traded through confirm %.2f. Stop %.2f%s."
                           % (p["symbol"], p["direction"], last, confirm, cancel,
                              (", target %.2f" % float(target)) if target not in (None, "") else ""))
            else:
                out.append("LATE %s %s: confirmed at %.2f after 10:15, outside the entry window. Skip by the rules."
                           % (p["symbol"], p["direction"], last))
    elif st == "entered":
        if before(cancel):
            state["stage"] = "done"
            out.append("STOP %s %s: %.2f hit the stop %.2f. Exit." % (p["symbol"], p["direction"], last, cancel))
        elif target not in (None, "") and beyond(float(target)):
            state["stage"] = "done"
            out.append("TARGET %s %s: %.2f reached the target %.2f." % (p["symbol"], p["direction"], last, float(target)))
        elif now.time() >= EXIT_BY and not state.get("exit_sent"):
            state["exit_sent"] = True
            out.append("15:00 EXIT %s %s: still open at %.2f. The plan is to be out now." % (p["symbol"], p["direction"], last))
    return out


def option_events(opt, price, state):
    out = []
    if price is None or not opt or opt.get("premium_stop") is None or state.get("opt_done"):
        return out
    name = "%s %g %s" % (opt.get("symbol", ""), opt["strike"], opt["side"])
    if price <= opt["premium_stop"]:
        state["opt_done"] = True
        out.append("OPTION STOP %s: premium %.2f at or below the stop %.2f." % (name, price, opt["premium_stop"]))
    elif opt.get("premium_target") is not None and price >= opt["premium_target"]:
        state["opt_done"] = True
        out.append("OPTION TARGET %s: premium %.2f reached %.2f." % (name, price, opt["premium_target"]))
    return out


def cmd_watch(args):
    """Every minute from 09:16 to 15:16: check each pick (and its option) twice, alert on any level hit."""
    now = now_ist()
    if not args.force and not (WATCH_FROM <= now.time() <= WATCH_TO):
        return 0
    if now.weekday() >= 5:
        return 0
    ok, _ = trading_day_cached(now)
    if not ok:
        return 0
    today = now.date().isoformat()
    picks = [p for p in load_picks(today) if p.get("confirm") not in (None, "") or p["horizon"] == "swing"]
    trades = (store.read_json(D + "trades/%s.json" % today) or {}).get("trades") or []
    if not picks and not trades:
        return 0
    uni = api.load_universe()["stocks"]
    plans = {(x["symbol"], x["horizon"]): x.get("option") for x in
             (store.read_json(D + "checks/%s_5.json" % today) or {}).get("picks") or []}
    path = D + "watch/%s.json" % today
    state = store.read_json(path, {}) or {}
    alerts = []
    for poll in range(1 if args.force else 2):
        if poll:
            time.sleep(28)
            now = now_ist()
        keys = [uni[p["symbol"]]["eq"] for p in picks if p["symbol"] in uni]
        keys += [o["key"] for o in plans.values() if o and o.get("key")]
        keys += [uni[t["symbol"]]["eq"] for t in trades if t["symbol"] in uni]
        try:
            q = api.quotes(keys)
        except Exception as e:
            store.log("momentum watch: quotes failed: %s" % e)
            break
        for p in picks:
            if p["symbol"] not in uni:
                continue
            k = "%s|%s" % (p["symbol"], p["horizon"])
            st = state.setdefault(k, {})
            last = (q.get(uni[p["symbol"]]["eq"]) or {}).get("last")
            if last:
                alerts += watch_events(p, last, st, now)
            opt = plans.get((p["symbol"], p["horizon"]))
            if opt and opt.get("key") and st.get("stage") == "entered":
                alerts += option_events(dict(opt, symbol=p["symbol"]), (q.get(opt["key"]) or {}).get("last"), st)
        eng = state.setdefault("engine", {})
        for t in trades:
            if t["symbol"] not in uni:
                continue
            st = eng.setdefault(t["symbol"], {})
            if calc.day_r(eng) <= calc.DAILY_STOP_R and st.get("stage", "waiting") == "waiting":
                st["blocked"] = True
            r = q.get(uni[t["symbol"]]["eq"]) or {}
            alerts += calc.trade_step(t, r.get("last"), r.get("vwap"), now.time(), st)
        if trades and calc.day_r(eng) <= calc.DAILY_STOP_R and not state.get("daily_stop_sent"):
            state["daily_stop_sent"] = True
            alerts.append("DAILY STOP: today's trades are at %+.1fR. No new entries today." % calc.day_r(eng))
    write_compact(path, state)
    if alerts:
        telegram.send("<b>Pick alert</b> %s\n%s\n<i>Advisory only.</i>" % (now.strftime("%H:%M"),
                      "\n".join(telegram.esc(a) for a in alerts)), args.dry_run)
        store.log("momentum watch: " + " | ".join(alerts))
    return 0


# ------------------------------------------------------------------ end of day

def session_bars(key, today, after=None):
    bars = [b for b in api.intraday(key, 1) if b["date"] == today and b["ts"].time() >= dtime(9, 15)]
    return [b for b in bars if b["ts"].time() >= after] if after else bars


def fill_swing(rows, universe, today):
    """Five- and ten-session results for swing picks whose window has closed."""
    todo = [r for r in rows if r.get("horizon") in ("swing", "both") and r.get("open") and r["date"] < today
            and r["symbol"] in universe and (r.get("ret_5d") is None or r.get("ret_10d") is None)]
    if not todo:
        return 0
    start = min(r["date"] for r in todo)
    idx = {d["date"]: d for d in api.daily(api.NIFTY, start, today) if d["date"] <= today}
    done = 0
    for r in todo:
        try:
            days = [d for d in api.daily(universe[r["symbol"]]["eq"], r["date"], today) if d["date"] >= r["date"]]
            s = 1 if r["direction"] == "UP" else -1
            i0 = idx.get(r["date"])
            for n in (5, 10):
                key = "ret_%dd" % n
                if r.get(key) is not None or len(days) < n:
                    continue
                end = days[n - 1]
                r[key] = calc.r2(calc.pct(end["c"], r["open"]) * s)
                i1 = idx.get(end["date"])
                if i0 and i1:
                    r["alpha_%dd" % n] = calc.r2(r[key] - calc.pct(i1["c"], i0["o"]) * s)
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
    plans = {(x["symbol"], x["horizon"]): x.get("option") for x in
             (store.read_json(D + "checks/%s_5.json" % today) or {}).get("picks") or []}
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
                opt = plans.get((p["symbol"], p["horizon"])) or {}
                if opt.get("key"):
                    row["option"] = {k: opt.get(k) for k in ("side", "strike", "expiry", "premium", "spread_pct", "iv_vs_rv", "grade")}
                    try:
                        leg = calc.option_leg(row["trade"], session_bars(opt["key"], today), bars)
                        if leg:
                            row["option"].update(leg)
                    except Exception as e:
                        row["option"]["error"] = redact(str(e))[:100]
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
            if r.get("rules_version", 1) >= 2:
                # v2: classic opening-range breakout, stop at the other side of the range
                level, stop = (r["or_high"], r["or_low"]) if up else (r["or_low"], r["or_high"])
            else:
                level = r["or_high"] if up else r["or_low"]
                stop = level - 0.10 * r["atr"] if up else level + 0.10 * r["atr"]
            r["trade"] = calc.walk(bars, r["direction"], level, stop)
        except Exception as e:
            store.log("momentum eod: in-play %s failed: %s" % (r["symbol"], e))
        time.sleep(api.PACE_S)
    store.rewrite(inplay, D + "inplay.jsonl")
    ip_tally = calc.tally([dict(r, right=False) for r in inplay if r.get("trade")]) if inplay else None

    # 4. the 09:20 engine's trades as the watcher managed them (proper re-scoring comes with step 2)
    try:
        eng = store.read_json(D + "trades/%s.json" % today) or {}
        wst = ((store.read_json(D + "watch/%s.json" % today) or {}).get("engine")) or {}
        tl = store.load(D + "trades.jsonl")
        done = {(r["date"], r["symbol"]) for r in tl}
        new = [{"date": today, "symbol": t["symbol"], "direction": t["direction"], "entry": t["entry"], "stop": t["stop"],
                "risk": t["risk"], "relvol": t["relvol"], "news": t.get("news"), "fresh": t.get("fresh"),
                "theme": t.get("theme"), "rules_version": t.get("rules_version"),
                "result": (wst.get(t["symbol"]) or {}).get("result") or (wst.get(t["symbol"]) or {}).get("stage", "not watched"),
                "r": (wst.get(t["symbol"]) or {}).get("r")}
               for t in eng.get("trades") or [] if (today, t["symbol"]) not in done]
        store.append(new, D + "trades.jsonl")
        checks.append({"name": "engine_trades", "ok": True, "detail": "%d logged, day %+.1fR" % (len(new), calc.day_r(wst))})
    except Exception as e:
        checks.append({"name": "engine_trades", "ok": False, "detail": redact(str(e))[:120]})

    sc = calc.scorecard(rows)
    learned = calc.learn(rows)
    n_days = len({r["date"] for r in rows})
    store.write_json(D + "scorecard.json", {"updated": now.isoformat(timespec="seconds"), "sessions": n_days,
                                            "rules_version": calc.RULES_VERSION, "picks": sc, "in_play": ip_tally,
                                            "learned": learned})
    write_text(D + "scorecard.md", brief.render_scorecard(sc, ip_tally, n_days) + brief.render_engine(store.load(D + "trades.jsonl"))
               + brief.render_learned(learned))
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

    def filings():
        d = now.date()
        items = api.bse_announcements((d - timedelta(days=3)).isoformat(), d.isoformat(), max_pages=1)
        m = calc.match_filings(items, state["uni"]["stocks"]) if state.get("uni") else []
        return "%d announcements on page 1, %d matched to F&O stocks, e.g. %s" % (
            len(items), len(m), (m[0]["symbol"] + ": " + m[0]["headline"][:60]) if m else "-")

    check("bse_filings", filings, required=False)
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
    ap.add_argument("command", choices=["data", "preopen", "check5", "check30", "watch", "eod", "selftest"])
    ap.add_argument("--dry-run", action="store_true", help="print Telegram messages instead of sending")
    ap.add_argument("--force", action="store_true", help="run outside the normal time window")
    ap.add_argument("--no-telegram", action="store_true", help="selftest: skip the Telegram test message")
    args = ap.parse_args(argv)
    fn = {"data": cmd_data, "preopen": cmd_preopen, "check5": lambda a: cmd_check(a, "5"),
          "check30": lambda a: cmd_check(a, "30"), "watch": cmd_watch, "eod": cmd_eod, "selftest": cmd_selftest}[args.command]
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
