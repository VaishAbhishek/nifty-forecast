"""Entry point.  python3 -m forecast.run {morning|recheck|score|selftest}

Advisory and read-only: fetches market data and news, sends Telegram
messages, writes files in the data directory. It places no orders and does
not touch the EMA bot in any way.
"""
import argparse
import json
import os
import sys
import traceback
from datetime import datetime, time as dtime, timedelta

from . import news, quant, report, score as scoring, sentiment, store, strategies, telegram, upstox
from .config import CONFIG_DIR, IST, git_sha, now_ist, redact
from .strategies import RULE_HASH, RULE_VERSION, WORD


def trading_day(now):
    """(is_trading_day, reason). Asks Upstox, falls back to the local list."""
    day = now.date().isoformat()
    if now.weekday() >= 5:
        return False, "weekend"
    try:
        if upstox.is_trading_holiday(day):
            return False, "NSE holiday (Upstox)"
        return True, "Upstox calendar"
    except Exception as e:
        try:
            local = json.loads((CONFIG_DIR / "holidays.json").read_text())["nse_trading_holidays"]
        except Exception:
            local = []
        if day in local:
            return False, "NSE holiday (local list)"
        return True, "local list (Upstox calendar failed: %s)" % str(e)[:80]


def history(today):
    """Completed daily sessions for Nifty and a date->close map for India VIX."""
    frm = (datetime.fromisoformat(today) - timedelta(days=1150)).date().isoformat()
    days = [d for d in upstox.daily(upstox.NIFTY, frm, today) if d["date"] < today]
    vix = {}
    try:
        vix = {d["date"]: d["c"] for d in upstox.daily(upstox.VIX, frm, today) if d["date"] < today}
    except Exception as e:
        store.log("VIX history failed: %s" % e)
    return days, vix


def base_record(today, kind, now, f):
    return {"date": today, "kind": kind, "run_ts": now.isoformat(timespec="seconds"), "rule_version": RULE_VERSION,
            "rule_hash": RULE_HASH, "code": git_sha(), "open_0915": f["open_0915"], "prev_close": f["prev_close"],
            "outcome": None}


def n_scored():
    return len({r["date"] for r in store.load() if r.get("outcome") and r.get("kind") in scoring.SCORED_KINDS
                and r.get("rule_version") == RULE_VERSION})


# ------------------------------------------------------------------ morning

def cmd_morning(args):
    now = now_ist()
    today = now.date().isoformat()
    ok, why = trading_day(now)
    if not ok:
        store.log("morning: skipped, %s" % why)
        store.set_status("morning", True, [], {"skipped": why})
        return 0
    in_window = dtime(9, 15) <= now.time() <= dtime(9, 40)
    if not in_window and not args.force:
        store.log("morning: outside 09:15-09:40 IST, not running (use --force for a manual run)")
        return 0
    kind = "morning" if in_window else "manual"
    if kind == "morning" and any(r["date"] == today and r["kind"] == "morning" for r in store.load()):
        store.log("morning: already logged for %s, not repeating" % today)
        return 0

    days, vix = history(today)
    if len(days) < 250:
        raise RuntimeError("Only %d daily candles from Upstox, need 250+" % len(days))
    try:
        open_px, open_src = upstox.wait_for_open()
    except Exception as e:
        telegram.send("<b>NIFTY MORNING CALL</b>\nNo opening price from Upstox, so there is no call today.\n<i>%s</i>"
                      % telegram.esc(str(e)[:200]), args.dry_run)
        raise
    f = quant.features(days, vix, open_px)
    outages = []
    if not f["vix_prev"]:
        outages.append("India VIX")
    if not f["range_model"]:
        outages.append("volatility model")

    ctx = {"open_source": open_src}
    try:
        ctx["vix_live"] = (upstox.ltp([upstox.VIX]).get(upstox.VIX) or {}).get("last")
    except Exception as e:
        store.log("live VIX failed: %s" % e)
    try:
        ctx["global"] = upstox.global_snapshot()
    except Exception as e:
        ctx["global"] = {}
        store.log("global snapshot failed: %s" % e)
    if not any(k in ctx["global"] for k in ("gift", "brent", "usdinr")):
        outages.append("Brent/USD-INR/GIFT")
    try:
        ctx["options"] = upstox.option_snapshot(open_px)
    except Exception as e:
        store.log("option snapshot failed: %s" % e)

    try:
        ctx["sectors"] = upstox.sector_snapshot(with_history=True)
    except Exception as e:
        store.log("sector snapshot failed: %s" % e)
    lv = quant.levels(days, open_px, (f["range_model"] or {}).get("expected_range"))

    since = datetime.fromisoformat(f["prev_date"]).replace(hour=15, minute=30, tzinfo=IST)
    headlines, feed_health = news.collect(since)
    if not headlines:
        outages.append("news")
    sent = sentiment.score(headlines, use_llm=not args.no_llm)
    flows = news.flows_from_headlines(headlines)
    for k in ("fii_net_cr", "dii_net_cr"):
        if flows[k] is None and sent.get(k) is not None:
            flows[k] = sent[k]
    ctx["flows"] = flows

    ens = strategies.ensemble(f, sent, outages)
    rm = f["range_model"] or {}
    base = base_record(today, kind, now, f)
    recs = [dict(base, strategy="S0_coin", verdict=WORD[strategies.coin(today)]),
            dict(base, strategy="S0_clim", p_range300=rm.get("clim60_range"), p_oc300=rm.get("clim60_oc")),
            dict(base, strategy="S1_vol", p_range300=rm.get("p_range"), p_oc300=rm.get("p_oc")),
            dict(base, strategy="S2_compress", p_range300=rm.get("p_range_cond"), compressed=rm.get("compressed"))]
    for k, d in ens["votes"].items():
        recs.append(dict(base, strategy=k, verdict=WORD[d["vote"]]))
    recs.append(dict(base, strategy="S9_ensemble", verdict=ens["verdict"], p_up=ens["p_up"],
                     p_range300=rm.get("p_range"), p_oc300=rm.get("p_oc"), net_votes=ens["net_votes"],
                     inputs={"gap_pct": f["gap_pct"], "vix_prev": f["vix_prev"], "news_score": sent["score"],
                             "news_method": sent["method"], "n_headlines": len(headlines),
                             "fii_net_cr": flows["fii_net_cr"], "dii_net_cr": flows["dii_net_cr"]},
                     data_flags=outages))

    label = now.strftime("%a %d %b %Y")
    msg = report.morning(label, f, ens, sent, headlines, ctx, outages, feed_health, n_scored(), lv, RULE_VERSION)
    store.append(recs)  # log first: the prediction must exist even if Telegram fails
    store.write_json("runs/%s_%s.json" % (today, kind), {
        "features": f, "levels": lv, "ensemble": ens, "context": ctx, "outages": outages, "feed_health": feed_health,
        "sentiment": {k: v for k, v in sent.items() if k != "labels"},
        "headlines": [{"title": h["title"], "source": h["source"], "ts": h["ts"].isoformat(), "also": h.get("also", 0),
                       "label": l} for h, l in zip(headlines, sent["labels"])]})
    sent_ok = True
    try:
        telegram.send(msg, args.dry_run)
    except Exception as e:
        sent_ok = False
        store.log("Telegram send failed: %s" % e)
    checks = [{"name": "upstox_history", "ok": True, "detail": "%d days to %s" % (len(days), f["prev_date"])},
              {"name": "open_price", "ok": True, "detail": "%s via %s" % (open_px, open_src)},
              {"name": "vix", "ok": bool(f["vix_prev"]), "detail": str(f["vix_prev"])},
              {"name": "global", "ok": bool(ctx["global"]), "detail": ",".join(sorted(ctx["global"]))},
              {"name": "options", "ok": "options" in ctx, "detail": str(ctx.get("options"))[:120]},
              {"name": "sectors", "ok": bool((ctx.get("sectors") or {}).get("sectors")) and not (ctx.get("sectors") or {}).get("missing"),
               "detail": "missing: %s" % ((ctx.get("sectors") or {}).get("missing") if ctx.get("sectors") else "all")},
              {"name": "news", "ok": bool(headlines), "detail": "%d headlines, %d drivers, %d sources"
               % (len(headlines), sent["n_relevant"], len({h["source"] for h in headlines}))},
              {"name": "llm", "ok": sent["method"] == "llm", "detail": sent["model"] or sent["llm_error"] or "off"},
              {"name": "telegram", "ok": sent_ok, "detail": ""}]
    store.set_status("morning", sent_ok, checks, {"verdict": ens["verdict"], "feeds": feed_health, "seconds":
                                                   round((now_ist() - now).total_seconds(), 1)})
    store.log("morning: %s logged (%s), net votes %+d, p_range300 %s" % (ens["verdict"], kind, ens["net_votes"], rm.get("p_range")))
    return 0 if sent_ok else 1


# ------------------------------------------------------------------ recheck

def first30_history(today):
    """date -> range of the 09:15-09:45 candle, for about the last year."""
    out = {}
    end = datetime.fromisoformat(today).date() - timedelta(days=1)
    for _ in range(4):
        start = end - timedelta(days=85)
        try:
            for c in upstox.hist_minutes(upstox.NIFTY, 30, start.isoformat(), end.isoformat()):
                if c["ts"].time() == dtime(9, 15):
                    out[c["date"]] = c["h"] - c["l"]
        except Exception as e:
            store.log("30-minute history chunk failed: %s" % e)
        end = start - timedelta(days=1)
    return out


def cmd_recheck(args):
    now = now_ist()
    today = now.date().isoformat()
    ok, why = trading_day(now)
    if not ok:
        store.log("recheck: skipped, %s" % why)
        return 0
    in_window = dtime(9, 40) <= now.time() <= dtime(10, 30)
    if not in_window and not args.force:
        store.log("recheck: outside 09:40-10:30 IST, not running")
        return 0
    kind = "recheck" if in_window else "manual"
    rows = store.load()
    if kind == "recheck" and any(r["date"] == today and r["kind"] == "recheck" for r in rows):
        store.log("recheck: already logged for %s" % today)
        return 0
    ens = next((r for r in rows if r["date"] == today and r["kind"] == "morning" and r["strategy"] == "S9_ensemble"), None)
    run = store.read_json("runs/%s_morning.json" % today, {}) or {}

    bars = [b for b in upstox.intraday(upstox.NIFTY, 1) if b["date"] == today]
    if not bars:
        raise RuntimeError("No intraday candles for today")
    f30 = [b for b in bars if b["ts"].time() < dtime(9, 45)]
    or15 = [b for b in bars if b["ts"].time() < dtime(9, 30)]
    open_px, last = bars[0]["o"], bars[-1]["c"]
    or_high, or_low = max(b["h"] for b in or15), min(b["l"] for b in or15)
    closes_5m = [b["c"] for b in bars if b["ts"].time() >= dtime(9, 30) and b["ts"].minute % 5 == 4]
    r = {"open": open_px, "last": last, "move_pts": last - open_px, "move_pct": (last - open_px) / open_px * 100,
         "f30_high": max(b["h"] for b in f30), "f30_low": min(b["l"] for b in f30),
         "or_high": or_high, "or_low": or_low, "orb": strategies.orb(closes_5m, or_high, or_low),
         "range_so_far": max(b["h"] for b in bars) - min(b["l"] for b in bars)}
    r["f30_range"] = r["f30_high"] - r["f30_low"]

    days, _ = history(today)
    model = quant.first30_model(first30_history(today), days, r["f30_range"], r["range_so_far"])
    r["p_range_new"] = model["p_range"] if model else None
    r["p_n"] = model["n"] if model else None
    r["p_range_morning"] = ens.get("p_range300") if ens else None
    r["vix_morning"] = (run.get("context") or {}).get("vix_live")
    try:
        r["vix_now"] = (upstox.ltp([upstox.VIX]).get(upstox.VIX) or {}).get("last")
    except Exception:
        r["vix_now"] = None

    seen = [news.story_words(h["title"]) for h in run.get("headlines", [])]
    since = datetime.fromisoformat(ens["run_ts"]) if ens else now - timedelta(minutes=35)
    fresh, _ = news.collect(since)
    fresh = [h for h in fresh if not any(news.same_story(news.story_words(h["title"]), w) for w in seen)]
    sent = sentiment.score(fresh, use_llm=not args.no_llm and bool(fresh))
    r.update(new_headlines=fresh, news_labels=sent["labels"], news_score=sent["score"], news_high_impact=sent["n_high_impact"],
             sent=sent, levels=quant.levels(days, open_px))
    try:
        r["sectors"] = upstox.sector_snapshot(with_history=False)
    except Exception as e:
        store.log("sector snapshot failed: %s" % e)
    news_vote = strategies.s8_news(sent)[0]

    verdict = ens["verdict"] if ens else None
    status, reason = strategies.recheck_status(verdict or "NO_TRADE", r["move_pct"], r["p_range_new"], r["range_so_far"],
                                               news_vote, sent["n_high_impact"])
    if not ens:
        status, reason = "NO MORNING CALL", "there was no 09:16 call to check, so this is a snapshot only"

    base = {"date": today, "kind": kind, "run_ts": now.isoformat(timespec="seconds"), "rule_version": RULE_VERSION,
            "rule_hash": RULE_HASH, "code": git_sha(), "open_0915": ens["open_0915"] if ens else open_px,
            "prev_close": ens["prev_close"] if ens else None, "outcome": None}
    recs = [dict(base, strategy="R1_first30", p_range300=r["p_range_new"]),
            dict(base, strategy="S6_orb", verdict=WORD[r["orb"]], ref_price=last),
            dict(base, strategy="R9_recheck", status=status, morning_verdict=verdict, move_pct=round(r["move_pct"], 3),
                 f30_range=round(r["f30_range"], 1), n_new_headlines=len(fresh))]
    store.append(recs)
    store.write_json("runs/%s_%s.json" % (today, "recheck" if in_window else "recheck_manual"), dict(
        {k: v for k, v in r.items() if k not in ("new_headlines", "news_labels", "sent")}, status=status, reason=reason,
        new_headlines=[{"title": h["title"], "source": h["source"], "label": l} for h, l in zip(fresh, sent["labels"])]))
    sent_ok = True
    try:
        telegram.send(report.recheck(now.strftime("%a %d %b %Y"), verdict, status, reason, r), args.dry_run)
    except Exception as e:
        sent_ok = False
        store.log("Telegram send failed: %s" % e)
    store.set_status("recheck", sent_ok, [{"name": "intraday", "ok": True, "detail": "%d bars" % len(bars)},
                                         {"name": "first30_model", "ok": model is not None, "detail": str(model)},
                                         {"name": "telegram", "ok": sent_ok, "detail": ""}], {"status": status})
    store.log("recheck: %s (%s)" % (status, reason))
    return 0 if sent_ok else 1


# -------------------------------------------------------------------- score

def cmd_score(args):
    now = now_ist()
    today = now.date().isoformat()
    rows = store.load()
    session_over = now.time() >= dtime(15, 35)
    pending = sorted({r["date"] for r in rows if not r.get("outcome") and (r["date"] < today or (r["date"] == today and session_over))})
    if not pending:
        store.log("score: nothing to score")
        return 0
    results = {}
    past = [d for d in pending if d < today]
    if past:
        for d in upstox.daily(upstox.NIFTY, past[0], past[-1]):
            results[d["date"]] = d
    if today in pending:
        bars = [b for b in upstox.intraday(upstox.NIFTY, 1) if b["date"] == today]
        if bars:
            results[today] = {"date": today, "o": bars[0]["o"], "h": max(b["h"] for b in bars),
                              "l": min(b["l"] for b in bars), "c": bars[-1]["c"]}
    filled = set()
    for r in rows:
        if not r.get("outcome") and r["date"] in results:
            scoring.fill_outcome(r, results[r["date"]])
            filled.add(r["date"])
    if not filled:
        store.log("score: no session data yet for %s" % ", ".join(pending))
        return 0
    store.rewrite(rows)
    st = scoring.stats(rows, RULE_VERSION)
    store.write_json("scores.json", st)
    last = max(filled)
    sent_ok = True
    try:
        telegram.send(scoring.message(last, [r for r in rows if r["date"] == last], st), args.dry_run)
    except Exception as e:
        sent_ok = False
        store.log("Telegram send failed: %s" % e)
    store.set_status("score", sent_ok, [{"name": "scored_dates", "ok": True, "detail": ",".join(sorted(filled))}],
                     {"sessions": st["sessions"]})
    store.log("score: filled %s, %d sessions in total" % (", ".join(sorted(filled)), st["sessions"]))
    return 0 if sent_ok else 1


# ----------------------------------------------------------------- selftest

def cmd_selftest(args):
    """Exercise every live dependency once and report honestly what worked."""
    now = now_ist()
    today = now.date().isoformat()
    checks = []

    def check(name, fn, required=True):
        try:
            detail = fn()
            checks.append({"name": name, "ok": True, "required": required, "detail": redact(str(detail))[:400]})
        except Exception as e:
            checks.append({"name": name, "ok": False, "required": required, "detail": redact("%s: %s" % (type(e).__name__, e))[:400]})

    frm = (now - timedelta(days=20)).date().isoformat()

    def nifty_daily():
        d = upstox.daily(upstox.NIFTY, frm, today)
        return "%d candles, last %s close %.1f" % (len(d), d[-1]["date"], d[-1]["c"])

    def vix_daily():
        d = upstox.daily(upstox.VIX, frm, today)
        return "%d candles, last %s close %.2f" % (len(d), d[-1]["date"], d[-1]["c"])

    def intraday_1m():
        b = upstox.intraday(upstox.NIFTY, 1)
        return "%d bars today%s" % (len(b), (", first %s open %.1f" % (b[0]["ts"].strftime("%H:%M"), b[0]["o"])) if b else " (normal outside market hours)")

    def thirty_min():
        d = upstox.hist_minutes(upstox.NIFTY, 30, frm, today)
        first = sorted({c["ts"].strftime("%H:%M") for c in d})[:2]
        return "%d candles, first bar times %s" % (len(d), first)

    def globals_():
        keys = upstox.global_keys()
        snap = upstox.global_snapshot()
        missing = [k for k in upstox.GLOBAL_WANTED if k not in snap]
        text = "; ".join("%s %.2f (%+.2f%%)" % (k, v["last"], v["pct"]) for k, v in snap.items())
        if missing:
            raise RuntimeError("no data for %s (unmatched: %s). got: %s" % (missing, [k for k in missing if k not in keys], text))
        return text

    def feeds():
        res = [news.fetch_feed(f)[1] for f in news.load_feeds()]
        store.write_json("feeds_health.json", res)
        bad = [r["name"] for r in res if not r["ok"]]
        text = "%d of %d feeds fresh" % (len(res) - len(bad), len(res))
        if len(bad) > len(res) / 2:
            raise RuntimeError(text + "; down: " + ", ".join(bad))
        return text + ("; down: " + ", ".join(bad) if bad else "")

    def llm():
        if not sentiment.provider():
            raise RuntimeError("no LLM key set; the keyword list will be used")
        sample = [{"title": "Sensex, Nifty set to open lower as crude jumps 4% on Middle East tension", "source": "test"},
                  {"title": "FIIs turn net buyers, pump Rs 2,100 crore into Indian equities", "source": "test"}]
        s = sentiment.score(sample)
        if s["method"] != "llm":
            raise RuntimeError(s["llm_error"])
        return "%s scored 2 test headlines: %s" % (s["model"], [l["direction"] for l in s["labels"]])

    def lexicon():
        s = sentiment.score([{"title": "Sensex crashes 900 points as crude spikes", "source": "test"}], use_llm=False)
        assert s["method"] == "lexicon" and s["score"] < 0
        return "fallback works (score %+.2f)" % s["score"]

    def isolation():
        home = os.path.expanduser("~")
        seen = [p for p in (home + "/nifty-bot", home + "/.nifty_bot_env") if os.access(p, os.R_OK)]
        under_systemd = bool(os.environ.get("INVOCATION_ID"))
        if seen and under_systemd:
            raise RuntimeError("sandbox is NOT hiding the EMA bot: can read %s" % seen)
        return "bot files hidden by the sandbox" if under_systemd else "not run by systemd, sandbox not tested (readable: %s)" % (seen or "none")

    def data_dir():
        store.write_json("cache/write_test.json", {"ts": now.isoformat()})
        return "writable"

    check("upstox_nifty_daily", nifty_daily)
    check("upstox_vix_daily", vix_daily)
    check("upstox_intraday", intraday_1m)
    check("upstox_30min_history", thirty_min, required=False)
    check("upstox_holiday_api", lambda: "today is a holiday: %s" % upstox.is_trading_holiday(today), required=False)
    check("upstox_quote_ohlc", lambda: upstox.day_ohlc(upstox.NIFTY), required=False)
    check("brent_usdinr_gift_us", globals_, required=False)
    check("upstox_option_chain", lambda: upstox.option_snapshot(upstox.day_ohlc(upstox.NIFTY)["last"]), required=False)

    def sectors():
        s = upstox.sector_snapshot(with_history=False)
        if s["missing"]:
            raise RuntimeError("no quote for %s" % s["missing"])
        return "%d sectors, %d heavyweights" % (len(s["sectors"]), len(s["heavy"]))
    check("sectors_and_heavyweights", sectors, required=False)
    check("rss_feeds", feeds)
    check("llm", llm, required=False)
    check("lexicon_fallback", lexicon)
    check("data_dir", data_dir)
    check("isolation_from_ema_bot", isolation)

    lines = ["%s %s: %s" % ("PASS" if c["ok"] else ("FAIL" if c["required"] else "WARN"), c["name"], c["detail"]) for c in checks]
    if not args.no_telegram:
        def tg():
            body = "\n".join(telegram.esc(l[:300]) for l in lines)
            telegram.send("<b>Nifty forecast self-test</b> (%s)\n<pre>%s</pre>" % (git_sha(), body), args.dry_run)
            return "test message sent"
        check("telegram_send", tg)
        lines.append("%s telegram_send: %s" % ("PASS" if checks[-1]["ok"] else "FAIL", checks[-1]["detail"]))
    ok = all(c["ok"] for c in checks if c["required"])
    try:
        store.set_status("selftest", ok, checks, {"tz_now": now.isoformat(timespec="seconds"), "python": sys.version.split()[0]})
    except Exception as e:
        lines.append("FAIL status_file: %s" % e)
    print("\n".join(lines))
    print("\nSELF-TEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="forecast.run", description=__doc__)
    ap.add_argument("command", choices=["morning", "recheck", "score", "selftest"])
    ap.add_argument("--dry-run", action="store_true", help="print Telegram messages instead of sending")
    ap.add_argument("--force", action="store_true", help="run outside the normal time window (logged as manual, not scored)")
    ap.add_argument("--no-llm", action="store_true", help="use the keyword list only")
    ap.add_argument("--no-telegram", action="store_true", help="selftest: skip the Telegram test message")
    args = ap.parse_args(argv)
    fn = {"morning": cmd_morning, "recheck": cmd_recheck, "score": cmd_score, "selftest": cmd_selftest}[args.command]
    try:
        return fn(args)
    except Exception as e:
        store.log("%s FAILED: %s\n%s" % (args.command, e, traceback.format_exc()[-1500:]))
        try:
            store.set_status(args.command, False, [{"name": "fatal", "ok": False, "detail": redact(str(e))[:300]}])
        except Exception:
            pass
        if args.command in ("morning", "recheck", "score"):
            try:  # tell the user the run broke, so silence never looks like "no call"
                telegram.send("<b>Nifty forecast: the %s run failed</b>\n<i>%s</i>" % (args.command, telegram.esc(redact(str(e))[:300])), args.dry_run)
            except Exception:
                pass
        return 1


if __name__ == "__main__":
    sys.exit(main())
