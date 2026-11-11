"""Builds the Telegram messages (HTML)."""
from .catalysts import CATALYSTS
from .telegram import esc

VERDICT_TEXT = {"UP": "UP-lean", "DOWN": "DOWN-lean", "QUIET": "QUIET", "NO_TRADE": "NO TRADE"}
ARROW = {1: "+", -1: "-", 0: "·"}
NAMES = {"S3_gap": "Gap", "S4_trend": "Trend", "S5_meanrev": "Stretch", "S8_news": "News"}
LEAN = {1: "bullish", -1: "bearish", 0: "neutral"}


def n0(x):
    return "n/a" if x is None else "{:,.0f}".format(x)


def n2(x):
    return "n/a" if x is None else "{:,.2f}".format(x)


def pct(p):
    return "n/a" if p is None else "%d%%" % round(p * 100)


def sg(x, digits=1):
    return "n/a" if x is None else ("%+." + str(digits) + "f") % x


# ------------------------------------------------------------------ sections

def news_block(headlines, sent, title="News: what is driving the market"):
    """Driver headlines only. Market reports and analyst views are counted, not scored."""
    pairs = list(zip(headlines, sent["labels"]))
    drivers = [(h, l) for h, l in pairs if l.get("kind") == "driver"]
    sources = len({h["source"] for h in headlines})
    L = ["\n<b>%s</b>" % title,
         "%d driver headline%s out of %d collected from %d source%s, scored by %s"
         % (len(drivers), "" if len(drivers) == 1 else "s", len(headlines), sources, "" if sources == 1 else "s",
            esc(sent["model"] or "keyword list")),
         "Tone <b>%+.2f</b> on a -1 to +1 scale · %d positive, %d negative, %d high-impact"
         % (sent["score"], sent["n_pos"], sent["n_neg"], sent["n_high_impact"])]
    if sent.get("summary"):
        L.append(esc(sent["summary"]))
    themes = {}
    for h, l in drivers:
        t = themes.setdefault(l["catalyst"], [0, 0, 0])
        t[0 if l["direction"] > 0 else 1 if l["direction"] < 0 else 2] += 1
    if themes:
        L.append("By theme:")
        for key, (p, n, z) in sorted(themes.items(), key=lambda kv: -sum(kv[1])):
            label = CATALYSTS[key]["label"] if key in CATALYSTS else "Other drivers"
            L.append("  %s: %d positive, %d negative%s" % (label, p, n, ", %d neutral" % z if z else ""))
    top = sorted(drivers, key=lambda x: (-x[1]["magnitude"], -x[0].get("also", 0)))[:7]
    if top:
        L.append("Main headlines:")
        for h, l in top:
            more = " <i>+%d similar</i>" % h["also"] if h.get("also") else ""
            L.append("%s %s <i>(%s)</i>%s" % (ARROW[l["direction"]], esc(h["title"][:140]), esc(h["source"]), more))
    if sent.get("events_today"):
        L.append("Due today: " + esc("; ".join(sent["events_today"])))
    L.append("<i>Not counted in the tone: %d market reports that only restate the index move, %d analyst views.</i>"
             % (sent.get("n_reports", 0), sent.get("n_views", 0)))
    return L


def sentiment_rows(f, ctx, sent):
    """(label, text, lean) rows. Context only: these are not votes."""
    rows = []
    g = ctx.get("global") or {}
    vp, vl = f.get("vix_prev"), ctx.get("vix_live")
    if vp and vl:
        ch = (vl / vp - 1) * 100
        rows.append(("India VIX", "%s, %+.1f%% vs prev close (%s)" % (n2(vl), ch, "fear rising" if ch > 3 else "fear easing" if ch < -3 else "steady"),
                     -1 if ch > 3 else 1 if ch < -3 else 0))
    elif vp:
        rows.append(("India VIX", "%s at prev close" % n2(vp), 0))
    o = ctx.get("options") or {}
    if o.get("pcr") is not None:
        rows.append(("Put/call ratio", "%s (above 1.2 is read as supportive, below 0.8 as heavy)" % n2(o["pcr"]),
                     1 if o["pcr"] >= 1.2 else -1 if o["pcr"] <= 0.8 else 0))
    if "gift" in g and abs(g["gift"]["last"] / f["prev_close"] - 1) < 0.08:
        prem = (g["gift"]["last"] / f["prev_close"] - 1) * 100
        rows.append(("GIFT Nifty", "%s, %+.2f%% vs Nifty prev close" % (n0(g["gift"]["last"]), prem), 1 if prem > 0.3 else -1 if prem < -0.3 else 0))
    us = [g[k]["pct"] for k in ("spx", "nasdaq") if k in g]
    if us:
        avg = sum(us) / len(us)
        rows.append(("US overnight", " · ".join("%s %+.2f%%" % (n, g[k]["pct"]) for k, n in (("spx", "S&amp;P 500"), ("nasdaq", "Nasdaq")) if k in g),
                     1 if avg > 0.5 else -1 if avg < -0.5 else 0))
    if "brent" in g:
        b = g["brent"]["pct"]
        rows.append(("Brent crude", "$%s, %+.2f%% (cheaper oil helps India)" % (n2(g["brent"]["last"]), b), 1 if b < -1 else -1 if b > 1 else 0))
    if "usdinr" in g:
        u = g["usdinr"]
        if u["pct"] == 0:
            rows.append(("USD-INR", "%s, no change reported (quote may be stale)" % n2(u["last"]), 0))
        else:
            rows.append(("USD-INR", "%s, %+.2f%% (a rising dollar is a headwind)" % (n2(u["last"]), u["pct"]), -1 if u["pct"] > 0.2 else 1 if u["pct"] < -0.2 else 0))
    fl = ctx.get("flows") or {}
    if fl.get("fii_net_cr") is not None:
        rows.append(("FII cash, yesterday", "%s cr (from headlines, unverified)" % "{:+,.0f}".format(fl["fii_net_cr"]),
                     1 if fl["fii_net_cr"] > 500 else -1 if fl["fii_net_cr"] < -500 else 0))
    else:
        rows.append(("FII cash, yesterday", "n/a (no headline carried the figure)", None))
    if fl.get("dii_net_cr") is not None:
        rows.append(("DII cash, yesterday", "%s cr (from headlines, unverified)" % "{:+,.0f}".format(fl["dii_net_cr"]),
                     1 if fl["dii_net_cr"] > 500 else -1 if fl["dii_net_cr"] < -500 else 0))
    rows.append(("Driver news tone", "%+.2f" % sent["score"], 1 if sent["score"] >= 0.4 else -1 if sent["score"] <= -0.4 else 0))
    return rows


def sentiment_block(f, ctx, sent):
    rows = sentiment_rows(f, ctx, sent)
    L = ["\n<b>Sentiment</b> (context, not votes)"]
    for name, text, lean in rows:
        L.append("%s %s: %s%s" % (ARROW.get(lean, "·"), name, text, " → <b>%s</b>" % LEAN[lean] if lean is not None else ""))
    counted = [l for _, _, l in rows if l is not None]
    L.append("Overall: %d bullish · %d bearish · %d neutral" % (counted.count(1), counted.count(-1), counted.count(0)))
    return L


def technical_block(f, lv, ctx):
    L = ["\n<b>Technicals</b>"]
    c, e20, e50, e200 = f["prev_close"], f["ema20"], f["ema50"], f["ema200"]
    L.append("Trend: prev close %s vs averages 20d %s · 50d %s · 200d %s" % (n0(c), n0(e20), n0(e50), n0(e200)))
    d = lv["dist20_pct"]
    L.append("Distance from the 20-day average: %+.1f%%%s" % (d, " (stretched)" if abs(d) >= 4 else ""))
    r14 = f["rsi14"]
    zone = "" if r14 is None else " (overbought above 70)" if r14 >= 70 else " (oversold below 30)" if r14 <= 30 else " (mid-range)"
    L.append("Momentum: RSI14 %s%s · RSI2 %s · %s" % (n0(r14), zone, n0(f["rsi2"]),
             "%d up closes in a row" % f["streak"] if f["streak"] > 0 else "%d down closes in a row" % -f["streak"] if f["streak"] < 0 else "no streak"))
    L.append("Volatility: ATR14 %s pts · yesterday's range %s pts%s" % (n0(f["atr14"]), n0(f["prev_range"]), " · narrowest of 7 days" if f["nr7"] else ""))
    o = ctx.get("options") or {}
    op = f["open_0915"]
    above = [("yesterday's high", lv["pdh"]), ("R1", lv["r1"]), ("R2", lv["r2"]), ("5-day high", lv["hi5"])]
    below = [("yesterday's low", lv["pdl"]), ("S1", lv["s1"]), ("S2", lv["s2"]), ("5-day low", lv["lo5"])]
    if o.get("call_wall"):
        above.append(("heaviest call OI", o["call_wall"]))
    if o.get("put_wall"):
        below.append(("heaviest put OI", o["put_wall"]))
    up = sorted([x for x in above + below + [("pivot", lv["pivot"])] if x[1] > op], key=lambda x: x[1])[:4]
    dn = sorted([x for x in above + below + [("pivot", lv["pivot"])] if x[1] <= op], key=lambda x: -x[1])[:4]
    L.append("Open: %s" % n0(op))
    L.append("Levels above: " + (" · ".join("%s %s" % (n0(v), k) for k, v in up) if up else "none nearby (open is above all of them)"))
    L.append("Levels below: " + (" · ".join("%s %s" % (n0(v), k) for k, v in dn) if dn else "none nearby"))
    if o.get("max_pain"):
        L.append("Options (%s expiry): max pain %s · ATM straddle %s pts, pricing roughly ±%s pts a day"
                 % (esc(o["expiry"]), n0(o["max_pain"]), n0(o["straddle"]), n0(o.get("implied_day_move"))))
    elif o:
        L.append("Options (%s expiry): ATM straddle %s pts, pricing roughly ±%s pts a day" % (esc(o["expiry"]), n0(o["straddle"]), n0(o.get("implied_day_move"))))
    if lv.get("band_lo"):
        L.append("If today's expected range sits around the open: %s to %s" % (n0(lv["band_lo"]), n0(lv["band_hi"])))
    return L


def sector_block(sec, when="at the open", history=True):
    L = ["\n<b>Sectors</b> (%% vs previous close, %s)" % when]
    if not sec or not sec.get("sectors"):
        L.append("Not available.")
        return L
    rows = sorted(sec["sectors"], key=lambda r: -r["pct"])
    if history:
        table = ["%-11s %6s %6s %6s" % ("", "now", "yday", "5-day")]
        table += ["%-11s %6s %6s %6s" % (r["name"], sg(r["pct"]), sg(r.get("yday")), sg(r.get("d5"))) for r in rows]
    else:
        table = ["%-11s %6s" % (r["name"], sg(r["pct"])) for r in rows]
    L.append("<pre>%s</pre>" % esc("\n".join(table)))
    up = sum(1 for r in rows if r["pct"] > 0)
    L.append("%d of %d sectors up · strongest %s %s · weakest %s %s"
             % (up, len(rows), rows[0]["name"], sg(rows[0]["pct"]) + "%", rows[-1]["name"], sg(rows[-1]["pct"]) + "%"))
    hv = sorted(sec.get("heavy") or [], key=lambda r: -r["pct"])
    if hv:
        L.append("Heavyweights (%d of %d up): %s" % (sum(1 for r in hv if r["pct"] > 0), len(hv),
                                                     " · ".join("%s %s" % (esc(r["name"]), sg(r["pct"])) for r in hv)))
    if sec.get("missing"):
        L.append("<i>No quote for: %s</i>" % esc(", ".join(sec["missing"])))
    return L


# ------------------------------------------------------------------ messages

def morning(day_label, f, ens, sent, headlines, ctx, outages, feed_health, n_scored, lv=None, rule_version=""):
    rm = f.get("range_model") or {}
    v = ens["verdict"]
    L = ["<b>NIFTY MORNING CALL · %s</b>" % esc(day_label),
         "<b>Verdict: %s</b>" % VERDICT_TEXT[v]]
    if v in ("UP", "DOWN"):
        p = ens["p_up"] if v == "UP" else 1 - ens["p_up"]
        L.append("Assumed odds of closing %s the open: about %s. This is an untested assumption, not a measured edge."
                 % ("above" if v == "UP" else "below", pct(p)))
    for r in ens["reasons"]:
        L.append(esc(r) + ".")
    L.append("<i>Advisory and paper only. Direction from the open is close to a coin flip. Sessions scored so far (rules %s): %d.</i>"
             % (esc(rule_version), n_scored))

    L.append("\n<b>Odds of a 300+ point day</b>")
    if rm:
        p_oc = rm["p_oc"]
        L.append("High-low range of 300+: <b>%s</b> (last 60 sessions: %s)" % (pct(rm["p_range"]), pct(rm["clim60_range"])))
        L.append("Open-to-close move of 300+: <b>%s</b> (up about %s, down about %s)"
                 % (pct(p_oc), pct(p_oc * ens["p_up"]), pct(p_oc * (1 - ens["p_up"]))))
        L.append("Expected range today: about %s points. Based on %d past sessions." % (n0(rm["expected_range"]), rm["n"]))
        if rm.get("p_range_cond") is not None:
            L.append("Market was %s yesterday; on similar days the 300+ range odds were %s (%d sessions)."
                     % ("coiled (narrow)" if rm["compressed"] else "not coiled", pct(rm["p_range_cond"]), rm["n_cond"]))
    else:
        L.append("Not available today.")

    L.append("\n<b>How the signals voted</b> (net %+d of 4)" % ens["net_votes"])
    for k, d in ens["votes"].items():
        L.append("%s %s: %s" % (ARROW[d["vote"]], NAMES[k], esc(d["why"])))
    L.append("Gap: prev close %s → open %s (%+.0f pts, %+.2f%%)" % (n0(f["prev_close"]), n0(f["open_0915"]), f["gap_pts"], f["gap_pct"]))

    L += news_block(headlines, sent)
    L += sentiment_block(f, ctx, sent)
    if lv:
        L += technical_block(f, lv, ctx)
    L += sector_block(ctx.get("sectors"), "at the open")

    if sent.get("catalysts"):
        L.append("\n<b>Catalysts and what history shows</b>")
        for key, titles in sorted(sent["catalysts"].items(), key=lambda kv: -len(kv[1]))[:4]:
            L.append("<b>%s</b> (%d headline%s): %s" % (CATALYSTS[key]["label"], len(titles), "" if len(titles) == 1 else "s",
                                                      esc(CATALYSTS[key]["history"])))

    L.append("\n<b>Key risk</b>")
    L.append(esc(sent.get("key_risk") or default_risk(f, rm, sent)))

    dead = [h["name"] for h in feed_health if not h["ok"]]
    notes = []
    if outages:
        notes.append("missing: " + ", ".join(outages))
    if dead:
        notes.append("feeds down: " + ", ".join(dead))
    if sent.get("llm_error") and sent["method"] == "lexicon":
        notes.append("LLM unavailable, used keyword list")
    L.append("\n<i>Data health: %s. Re-check at 09:46.</i>" % (esc("; ".join(notes)) if notes else "all inputs present"))
    return "\n".join(L)


def default_risk(f, rm, sent):
    if sent.get("n_high_impact"):
        return "High-impact headlines are in play, so a sharp move either way is more likely than usual."
    if rm and rm.get("p_range", 0) >= 0.5:
        return "Volatility is high: a 300+ point range is about as likely as not, and it can come in either direction."
    if abs(f["gap_pct"]) >= 0.5:
        return "A sizeable opening gap: the first hour can extend it or reverse it, and past data does not favour either."
    return "No single dominant risk. The main one is treating a weak lean as a strong one."


def recheck(day_label, morning_verdict, status, reason, r):
    L = ["<b>NIFTY 30-MIN RE-CHECK · %s</b>" % esc(day_label),
         "Morning call: <b>%s</b>" % VERDICT_TEXT.get(morning_verdict, "none (no morning call was logged)"),
         "<b>Status: %s</b>" % status, esc(reason[:1].upper() + reason[1:]) + "."]
    L.append("\n<b>What happened since the open</b>")
    L.append("Open %s · Now %s (%+.0f pts, %+.2f%%)" % (n0(r["open"]), n0(r["last"]), r["move_pts"], r["move_pct"]))
    L.append("First 30 min: high %s · low %s · range %s pts" % (n0(r["f30_high"]), n0(r["f30_low"]), n0(r["f30_range"])))
    orb_txt = {1: "broke ABOVE the first 15-minute range", -1: "broke BELOW the first 15-minute range",
               0: "is still inside the first 15-minute range"}[r["orb"]]
    L.append("Price %s (%s to %s). Breakouts like this have a weak record after costs; logged for scoring only."
             % (orb_txt, n0(r["or_low"]), n0(r["or_high"])))
    lv = r.get("levels") or {}
    if lv:
        marks = [("yesterday's high", lv["pdh"]), ("yesterday's low", lv["pdl"]), ("pivot", lv["pivot"]), ("R1", lv["r1"]), ("S1", lv["s1"])]
        up = sorted([m for m in marks if m[1] > r["last"]], key=lambda m: m[1])[:1]
        dn = sorted([m for m in marks if m[1] <= r["last"]], key=lambda m: -m[1])[:1]
        L.append("Nearest levels: %s above · %s below"
                 % ("%s %s" % (n0(up[0][1]), up[0][0]) if up else "none", "%s %s" % (n0(dn[0][1]), dn[0][0]) if dn else "none"))
    if r.get("vix_now") and r.get("vix_morning"):
        L.append("India VIX %s, was %s at the open (%+.1f%%)" % (n2(r["vix_now"]), n2(r["vix_morning"]),
                                                               (r["vix_now"] / r["vix_morning"] - 1) * 100))
    L.append("\n<b>Odds of a 300+ point range, updated</b>")
    if r.get("p_range_new") is not None:
        L.append("Now <b>%s</b>, was %s at 09:16%s" % (pct(r["p_range_new"]), pct(r.get("p_range_morning")),
                                                    " (from %d past sessions)" % r["p_n"] if r.get("p_n") else ""))
    else:
        L.append("Not available (was %s at 09:16)." % pct(r.get("p_range_morning")))
    L += sector_block(r.get("sectors"), "after 30 minutes", history=False)
    if r["new_headlines"]:
        L += news_block(r["new_headlines"], r["sent"], "New headlines since 09:16")
    else:
        L.append("\n<b>New headlines since 09:16</b>\nNothing new that matters.")
    L.append("\n<i>Advisory and paper only. A NO TRADE call is never upgraded to a lean at the re-check.</i>")
    return "\n".join(L)
