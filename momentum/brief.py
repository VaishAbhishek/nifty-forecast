"""Text output: the morning brief (markdown, read by the report's agents) and Telegram messages."""
from forecast.telegram import esc

LISTS = (("gainers", "Biggest up-moves last session (in units of the stock's normal daily range)"),
         ("losers", "Biggest down-moves last session"),
         ("volume", "Unusual volume last session (against its own 20-day average)"),
         ("breakouts", "Closed above the 20-day high"),
         ("breakdowns", "Closed below the 20-day low"),
         ("oi_long", "Futures: price up with open interest up (long build-up)"),
         ("oi_short", "Futures: price down with open interest up (short build-up)"),
         ("rs_lead", "Strongest against Nifty over 20 sessions"),
         ("rs_lag", "Weakest against Nifty over 20 sessions"),
         ("near_high", "Within 2% of the 52-week high"))


def num(x, fmt="%+.1f", none="-"):
    return fmt % x if x is not None else none


def _row(sym, s):
    oi = "%s %s" % (num(s.get("oi_chg"), "%+.0f%%"), s.get("oi_class") or "") if s.get("oi_chg") is not None else "-"
    opt = s.get("opt") or {}
    flags = [x for x in (("20d-" + s["breakout"]) if s.get("breakout") else None,
                         "NR7" if s.get("nr7") else None,
                         "stale" if s.get("stale") else None) if x]
    return "| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        sym, num(s.get("close"), "%.1f"), num(s.get("chg1"), "%+.1f%%"), num(s.get("move_atr"), "%+.1f"),
        num(s.get("vol_ratio"), "%.1fx"), num(s.get("range_pos"), "%.2f"), num(s.get("chg5"), "%+.1f%%"),
        num(s.get("chg20"), "%+.1f%%"), num(s.get("atr_pct"), "%.1f%%"), oi.strip(),
        num(s.get("est_gap"), "%+.1f%%"), num(opt.get("day_move_pct"), "%.1f%%"),
        num(s.get("from_52w_high"), "%+.0f%%"), " ".join([s.get("trend") or "-"] + flags))


HEAD = ("| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap "
        "| Options: 1-day move | From 52w high | Trend, flags |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def render_brief(d):
    m = d["market"]
    n = m.get("nifty") or {}
    out = ["# F&O momentum data for %s" % d["date"],
           "",
           "Built %s on the VM from Upstox. %d stocks, %d failed. Prices are the last completed session (%s)."
           % (d["generated"][11:16], len(d["stocks"]), len(d.get("failed") or []), d.get("session")),
           "Numbers here are measured. Reasons are not: this file cannot tell why a stock moved.",
           ""]
    if d.get("notes"):
        out += ["Notes: " + "; ".join(d["notes"]), ""]
    out += ["## Market", ""]
    out.append("- Nifty: close %s, last day %s, 5 days %s. Regime: **%s** (10-day efficiency %s, against 20/50-day averages: %s)."
               % (num(n.get("close"), "%.1f"), num(n.get("chg1"), "%+.2f%%"), num(n.get("chg5"), "%+.2f%%"),
                  n.get("tag"), num(n.get("efficiency_10d"), "%.2f"), n.get("vs_averages")))
    if m.get("vix") is not None:
        out.append("- India VIX: %.2f." % m["vix"])
    g = m.get("index_gap") or {}
    if g:
        out.append("- Expected index gap: %s (GIFT Nifty %s against the Nifty futures close %s; GIFT's own change %s). An estimate, not the open."
                   % (num(g.get("gift_vs_fut"), "%+.2f%%"), num(g.get("gift"), "%.1f"), num(g.get("nifty_fut"), "%.1f"),
                      num(g.get("gift_change"), "%+.2f%%")))
    gl = m.get("global") or {}
    if gl:
        out.append("- Overnight: " + ", ".join("%s %s" % (k, num(v.get("pct"), "%+.2f%%")) for k, v in sorted(gl.items()) if k != "gift") + ".")
    fl = m.get("flows") or {}
    parts = []
    for key, label in (("fii_cash", "FII cash"), ("dii_cash", "DII cash")):
        if fl.get(key):
            parts.append("%s net %s (%s)" % (label, num(fl[key].get("net"), "%+.0f"), fl[key].get("date")))
    for key, label in (("fii_index_fut", "FII index futures"), ("fii_stock_fut", "FII stock futures")):
        if fl.get(key) and fl[key].get("long_share") is not None:
            parts.append("%s %.0f%% long" % (label, fl[key]["long_share"] * 100))
    if parts:
        out.append("- Flows (units as Upstox reports them): " + "; ".join(parts) + ".")
    if m.get("sectors"):
        out.append("- Sector indices, last session and 5 sessions: "
                   + ", ".join("%s %s / %s" % (s["name"], num(s.get("yday"), "%+.1f%%"), num(s.get("d5"), "%+.1f%%")) for s in m["sectors"]) + ".")
    out += ["", "## What past gaps did next (all F&O stocks, about one year, %d gaps)" % sum(v["n"] for v in d["gap_table"].values()), "",
            "Kept going = closed beyond the open in the gap's direction. Filled = traded back to the previous close that day.",
            "", "| Gap | Count | Kept going | Filled | Average open-to-close in the gap's direction |", "|---|---|---|---|---|"]
    for k, v in d["gap_table"].items():
        out.append("| %s%% | %d | %.0f%% | %.0f%% | %+.2f%% |" % (k, v["n"], v["cont"] * 100, v["fill"] * 100, v["avg_oc"]))
    out += ["", "Futures open interest source: %s." % d.get("oi_source"), ""]
    st = d["stocks"]
    out += ["## Focus list: stocks on two or more lists below", "", HEAD]
    out += [_row(s, st[s]) for s in d["lists"].get("focus", [])] or ["| none | | | | | | | | | | | | | |"]
    for key, title in LISTS:
        syms = d["lists"].get(key) or []
        if not syms:
            continue
        out += ["", "## %s" % title, "", HEAD] + [_row(s, st[s]) for s in syms]
    out += ["", "## Reading the columns", "",
            "- In ATRs: last day's move divided by the stock's average true range. Above 1.5 is an unusually large day.",
            "- Close in range: 1.00 closed at the day's high, 0.00 at the low.",
            "- Est. gap: the stock's beta times the expected index gap. It ignores stock news, which usually matters more.",
            "- Options: 1-day move: the daily move implied by the nearest at-the-money straddle. Shown for the focus list only.",
            "- The full per-stock data is in momentum/latest.json."]
    return "\n".join(out) + "\n"


def _pre(lines):
    return "<pre>%s</pre>" % esc("\n".join(lines))


def preopen_message(d):
    lines = ["<b>Pre-open gaps</b> %s (%s)" % (d["time"], esc(d["source_label"]))]
    if d.get("index_gap") is not None:
        lines.append("Nifty futures: %+.2f%%" % d["index_gap"])
    tbl = []
    for title, rows in (("GAP UP", d["up"]), ("GAP DOWN", d["down"])):
        tbl.append("%-12s %6s %5s %6s" % (title, "gap", "ATRs", "yday"))
        tbl += ["%-12s %+5.1f%% %5s %6s" % (r["symbol"][:12], r["gap"], num(r.get("gap_atr"), "%.1f"), num(r.get("chg1"), "%+.1f%%")) for r in rows] or ["(none over 0.5%)"]
    lines.append(_pre(tbl))
    if d.get("picks"):
        ptbl = ["%-11s %-4s %+5.1f%%  %s%s" % (p["symbol"][:11], p["direction"], p["gap"] if p.get("gap") is not None else 0.0,
                                               p["verdict"], (", such gaps kept going %.0f%% of %d" % (p["cont"] * 100, p["cont_n"])) if p.get("cont") is not None else "")
                for p in d["picks"]]
        lines += ["<b>Today's picks against the gap</b>", _pre(ptbl)]
    elif d.get("picks_note"):
        lines.append("<i>%s</i>" % esc(d["picks_note"]))
    lines.append("<i>Advisory only. The gap is already in the opening price.</i>")
    return "\n".join(lines)


def check_message(d):
    lines = ["<b>%s-minute check</b> %s" % (d["label"], d["time"])]
    if d.get("in_play"):
        tbl = ["%-11s %5s %6s %6s  %s" % ("IN PLAY", "vol", "day", "v.open", "range")]
        tbl += ["%-11s %4.1fx %+5.1f%% %+5.1f%%  %s-%s" % (r["symbol"][:11], r["relvol"], r["chg"], r["from_open"],
                                                           num(r.get("low"), "%.1f"), num(r.get("high"), "%.1f")) for r in d["in_play"]]
        lines.append(_pre(tbl))
    else:
        lines.append("<i>%s</i>" % esc(d.get("in_play_note") or "No stock is trading at twice its usual volume."))
    if d.get("picks"):
        ptbl = ["%-11s %-4s %+5.1f%%  %s%s" % (p["symbol"][:11], p["direction"], p["from_open"], p["status"],
                                               ("  vol %.1fx" % p["relvol"]) if p.get("relvol") else "") for p in d["picks"]]
        lines += ["<b>Today's picks</b> (move since the open)", _pre(ptbl)]
    lines.append("<i>Advisory only.</i>")
    return "\n".join(lines)


def _tally_line(name, t):
    return "%-14s %3d  %4s  %6s  %6s  %s" % (name[:14], t["n"], ("%.0f%%" % (t["hit"] * 100)) if t["hit"] is not None else "-",
                                               num(t["avg_ret"], "%+.2f%%"), num(t["avg_alpha"], "%+.2f%%"),
                                               ("%d trades, %s R each" % (t["trades"], num(t["avg_r"], "%+.2f"))) if t["trades"] else "")


def eod_message(d):
    lines = ["<b>Momentum picks: results</b> %s" % d["date"]]
    if d["today"]:
        tbl = ["%-11s %-4s %6s %6s  %s" % ("", "", "o-c", "v.Nifty", "trade")]
        for r in d["today"]:
            t = r.get("trade") or {}
            trade = t.get("status", "") + (" %+.1fR" % t["r"] if t.get("r") is not None else "")
            tbl.append("%-11s %-4s %+5.1f%% %6s  %s" % ((("*" if r.get("tier") == "best" else " ") + r["symbol"])[:11], r["direction"],
                                                        r["ret"], num(r.get("alpha"), "%+.1f%%"), trade))
        lines += [_pre(tbl), "* = best 3. o-c is open to close in the pick's direction."]
    else:
        lines.append("<i>%s</i>" % esc(d.get("note") or "No picks were logged today."))
    sc = d.get("scorecard") or {}
    if sc.get("all", {}).get("all", {}).get("n"):
        tbl = ["%-14s %3s  %4s  %6s  %6s" % ("RUNNING", "n", "hit", "o-c", "alpha")]
        tbl.append(_tally_line("all picks", sc["all"]["all"]))
        for group in ("tier", "conviction"):
            tbl += [_tally_line(k, t) for k, t in sc.get(group, {}).items()]
        lines.append(_pre(tbl))
        a = sc["all"]["all"]
        if a["needs_for_95"]:
            lines.append("<i>%d of %d right would be needed to rule out a coin flip; so far %d.</i>" % (a["needs_for_95"], a["n"], a["right"]))
    if d.get("inplay"):
        t = d["inplay"]
        lines.append("In-play breakout test (logged only): %d signals, %d trades, %s R each." % (t["n"], t["trades"], num(t["avg_r"], "%+.2f")))
    return "\n".join(lines)


def render_scorecard(sc, inplay, n_days):
    out = ["# Momentum picks scorecard", "",
           "%d picks over %d sessions. Hit = closed beyond the open in the pick's direction. Alpha = that move minus the index's."
           % (sc["all"]["all"]["n"], n_days),
           "R = result of the confirm/cancel trade in multiples of the risk taken. Costs are not included.",
           "Do not read much into any row with fewer than about 30 picks.", ""]
    for group, tallies in sc.items():
        out += ["## By %s" % group.replace("_", " "), "",
                "| Group | Picks | Hit | Needed for 95% | Avg open-to-close | Avg alpha | Trades | Avg R | Total R | 5-day picks | Avg 5-day | Avg 5-day alpha |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for k, t in tallies.items():
            out.append("| %s | %d | %s | %s | %s | %s | %d | %s | %s | %d | %s | %s |" % (
                k, t["n"], ("%.0f%%" % (t["hit"] * 100)) if t["hit"] is not None else "-", t["needs_for_95"] or "-",
                num(t["avg_ret"], "%+.2f%%"), num(t["avg_alpha"], "%+.2f%%"), t["trades"], num(t["avg_r"], "%+.2f"),
                num(t["total_r"], "%+.1f"), t["n_5d"], num(t["avg_ret_5d"], "%+.2f%%"), num(t["avg_alpha_5d"], "%+.2f%%")))
        out.append("")
    if inplay:
        out += ["## In-play opening-range breakout (forward test, logged only)", "",
                "Stocks at twice their usual volume five minutes after the open; entry on a break of the first five minutes' range",
                "in the direction of the first move, stop 10% of ATR away, exit at the close.", "",
                "%d signals, %d trades, average %s R, total %s R." % (inplay["n"], inplay["trades"], num(inplay["avg_r"], "%+.2f"), num(inplay["total_r"], "%+.1f")), ""]
    return "\n".join(out)
