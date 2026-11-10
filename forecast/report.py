"""Builds the Telegram messages (HTML)."""
from .catalysts import CATALYSTS
from .telegram import esc

VERDICT_TEXT = {"UP": "UP-lean", "DOWN": "DOWN-lean", "QUIET": "QUIET", "NO_TRADE": "NO TRADE"}
ARROW = {1: "+", -1: "-", 0: "·"}
NAMES = {"S3_gap": "Gap", "S4_trend": "Trend", "S5_meanrev": "Stretch", "S8_news": "News"}


def n0(x):
    return "n/a" if x is None else "{:,.0f}".format(x)


def n2(x):
    return "n/a" if x is None else "{:,.2f}".format(x)


def pct(p):
    return "n/a" if p is None else "%d%%" % round(p * 100)


def morning(day_label, f, ens, sent, headlines, ctx, outages, feed_health, n_scored):
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
    L.append("<i>Advisory and paper only. Direction from the open is close to a coin flip. Sessions scored so far: %d.</i>" % n_scored)

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

    L.append("\n<b>Quant setup</b>")
    L.append("Prev close %s · Open %s · Gap %+.0f pts (%+.2f%%)" % (n0(f["prev_close"]), n0(f["open_0915"]), f["gap_pts"], f["gap_pct"]))
    L.append("Averages: 20d %s · 50d %s · 200d %s" % (n0(f["ema20"]), n0(f["ema50"]), n0(f["ema200"])))
    L.append("RSI14 %s · RSI2 %s · ATR14 %s pts · yesterday's range %s" % (n0(f["rsi14"]), n0(f["rsi2"]), n0(f["atr14"]), n0(f["prev_range"])))
    vix_line = "India VIX: prev close %s" % n2(f["vix_prev"])
    if ctx.get("vix_live"):
        vix_line += " · now %s" % n2(ctx["vix_live"])
    L.append(vix_line)
    if ctx.get("options"):
        o = ctx["options"]
        L.append("ATM straddle (%s, %s): %s pts · PCR %s" % (esc(o["expiry"]), n0(o["atm_strike"]), n0(o["straddle"]), n2(o["pcr"])))

    L.append("\n<b>Numbers</b>")
    g = ctx.get("global") or {}
    labels = (("gift", "GIFT Nifty"), ("brent", "Brent"), ("usdinr", "USD-INR"), ("spx", "S&amp;P 500"), ("nasdaq", "Nasdaq"))
    for key, label in labels:
        if key in g:
            L.append("%s: %s (%+.2f%%)" % (label, n2(g[key]["last"]), g[key]["pct"]))
        else:
            L.append("%s: n/a" % label)
    if "gift" in g and abs(g["gift"]["last"] / f["prev_close"] - 1) < 0.08:  # ignore an obviously wrong quote
        L.append("GIFT vs Nifty prev close: %+.0f pts" % (g["gift"]["last"] - f["prev_close"]))
    fl = ctx.get("flows") or {}
    if fl.get("fii_net_cr") is not None or fl.get("dii_net_cr") is not None:
        L.append("Yesterday's flows (from headlines, unverified): FII %s cr · DII %s cr"
                 % ("{:+,.0f}".format(fl["fii_net_cr"]) if fl.get("fii_net_cr") is not None else "n/a",
                    "{:+,.0f}".format(fl["dii_net_cr"]) if fl.get("dii_net_cr") is not None else "n/a"))
    else:
        L.append("Yesterday's FII/DII flows: n/a (no headline carried the figure)")

    L.append("\n<b>News</b> (%d headlines, scored by %s)" % (len(headlines), esc(sent["model"] or "keyword list")))
    L.append("Tone %+.2f on a -1 to +1 scale · %d positive, %d negative, %d high-impact"
             % (sent["score"], sent["n_pos"], sent["n_neg"], sent["n_high_impact"]))
    if sent.get("summary"):
        L.append(esc(sent["summary"]))
    ranked = sorted(zip(headlines, sent["labels"]), key=lambda x: (-x[1]["magnitude"] * (1 if x[1]["relevant"] else 0)))
    for h, l in ranked[:8]:
        if l["relevant"]:
            L.append("%s %s <i>(%s)</i>" % (ARROW[l["direction"]], esc(h["title"][:140]), esc(h["source"])))

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
    if r.get("vix_now") and r.get("vix_morning"):
        L.append("India VIX %s, was %s at the open (%+.1f%%)" % (n2(r["vix_now"]), n2(r["vix_morning"]),
                                                               (r["vix_now"] / r["vix_morning"] - 1) * 100))
    L.append("\n<b>Odds of a 300+ point range, updated</b>")
    if r.get("p_range_new") is not None:
        L.append("Now <b>%s</b>, was %s at 09:16%s" % (pct(r["p_range_new"]), pct(r.get("p_range_morning")),
                                                    " (from %d past sessions)" % r["p_n"] if r.get("p_n") else ""))
    else:
        L.append("Not available (was %s at 09:16)." % pct(r.get("p_range_morning")))
    L.append("\n<b>New headlines since 09:16</b> (%d)" % len(r["new_headlines"]))
    if r["new_headlines"]:
        L.append("Tone %+.2f · %d high-impact" % (r["news_score"], r["news_high_impact"]))
        for h, l in list(zip(r["new_headlines"], r["news_labels"]))[:5]:
            L.append("%s %s <i>(%s)</i>" % (ARROW[l["direction"]], esc(h["title"][:140]), esc(h["source"])))
    else:
        L.append("Nothing new that matters.")
    L.append("\n<i>Advisory and paper only. A NO TRADE call is never upgraded to a lean at the re-check.</i>")
    return "\n".join(L)
