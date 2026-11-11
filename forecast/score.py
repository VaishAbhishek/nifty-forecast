"""Forward-test scorer: fills in what actually happened and keeps the running tally."""
from .config import BIG_MOVE_PTS
from .quant import binom_p_one_sided, wilson
from .telegram import esc

DIRECTION = ("S9_ensemble", "S0_coin", "S3_gap", "S4_trend", "S5_meanrev", "S8_news", "S6_orb")
PROBABILITY = ("S1_vol", "S0_clim", "S2_compress", "R1_first30")
SCORED_KINDS = ("morning", "recheck")


def fill_outcome(rec, day):
    """Attach the session result to one logged prediction."""
    ref = rec.get("ref_price") or rec.get("open_0915") or day["o"]
    rng = day["h"] - day["l"]
    oc = day["c"] - (rec.get("open_0915") or day["o"])
    out = {"open": day["o"], "high": day["h"], "low": day["l"], "close": day["c"],
           "range_pts": round(rng, 1), "oc_pts": round(oc, 1),
           "big_range": rng >= BIG_MOVE_PTS, "big_oc": abs(oc) >= BIG_MOVE_PTS,
           "dir_hit": None, "quiet_hit": None, "brier_range": None, "brier_oc": None}
    v = rec.get("verdict")
    if v in ("UP", "DOWN"):
        move = day["c"] - ref
        out["move_from_ref"] = round(move, 1)
        if move != 0:
            out["dir_hit"] = (move > 0) == (v == "UP")
    elif v == "QUIET":
        out["quiet_hit"] = rng < BIG_MOVE_PTS
    if rec.get("p_range300") is not None:
        out["brier_range"] = round((rec["p_range300"] - (1.0 if out["big_range"] else 0.0)) ** 2, 4)
    if rec.get("p_oc300") is not None:
        out["brier_oc"] = round((rec["p_oc300"] - (1.0 if out["big_oc"] else 0.0)) ** 2, 4)
    rec["outcome"] = out
    return rec


def stats(rows, version=None):
    """Running tally per strategy for one rule version. Manual runs are excluded."""
    done = [r for r in rows if r.get("outcome") and r.get("kind") in SCORED_KINDS
            and (version is None or r.get("rule_version") == version)]
    sessions = sorted({r["date"] for r in done})
    res = {"rule_version": version, "sessions": len(sessions), "first": sessions[0] if sessions else None,
           "last": sessions[-1] if sessions else None, "direction": {}, "probability": {}, "ensemble": {}}
    for s in DIRECTION:
        mine = [r for r in done if r["strategy"] == s]
        calls = [r for r in mine if r["outcome"]["dir_hit"] is not None]
        hits = sum(1 for r in calls if r["outcome"]["dir_hit"])
        lo, hi = wilson(hits, len(calls))
        days = len({r["date"] for r in mine})
        res["direction"][s] = {"calls": len(calls), "hits": hits,
                               "hit_rate": round(hits / len(calls), 3) if calls else None,
                               "ci95": [round(lo, 3), round(hi, 3)], "p_vs_coin": round(binom_p_one_sided(hits, len(calls)), 4),
                               "coverage": round(len(calls) / days, 3) if days else None, "days": days}
    base = {r["date"]: r["outcome"]["brier_range"] for r in done if r["strategy"] == "S0_clim"
            and r["outcome"]["brier_range"] is not None}
    for s in PROBABILITY:
        mine = [r for r in done if r["strategy"] == s and r["outcome"]["brier_range"] is not None and r["date"] in base]
        if not mine:
            res["probability"][s] = {"n": 0, "brier": None, "skill": None}
            continue
        b = sum(r["outcome"]["brier_range"] for r in mine) / len(mine)
        bb = sum(base[r["date"]] for r in mine) / len(mine)
        res["probability"][s] = {"n": len(mine), "brier": round(b, 4), "baseline_brier": round(bb, 4),
                                 "skill": round(1 - b / bb, 3) if bb > 0 else None}
    ens = [r for r in done if r["strategy"] == "S9_ensemble"]
    quiet = [r for r in ens if r["verdict"] == "QUIET"]
    res["ensemble"] = {"days": len(ens), "no_trade": sum(1 for r in ens if r["verdict"] == "NO_TRADE"),
                       "quiet_calls": len(quiet), "quiet_hits": sum(1 for r in quiet if r["outcome"]["quiet_hit"]),
                       "big_days": sum(1 for r in ens if r["outcome"]["big_range"])}
    return res


def message(day, today_rows, st):
    """Telegram scorecard for one finished session plus the running tally."""
    L = ["<b>NIFTY SCORECARD · %s</b>" % esc(day)]
    ens = next((r for r in today_rows if r["strategy"] == "S9_ensemble" and r.get("outcome")), None)
    any_row = ens or next((r for r in today_rows if r.get("outcome")), None)
    if any_row:
        o = any_row["outcome"]
        L.append("Open {:,.0f} → close {:,.0f} ({:+,.0f} pts) · range {:,.0f} pts · 300+ day: {}".format(
            any_row.get("open_0915") or o["open"], o["close"], o["oc_pts"], o["range_pts"], "YES" if o["big_range"] else "no"))
    if ens:
        v, o = ens["verdict"], ens["outcome"]
        if v in ("UP", "DOWN"):
            res = "n/a" if o["dir_hit"] is None else ("RIGHT" if o["dir_hit"] else "WRONG")
        elif v == "QUIET":
            res = "RIGHT" if o["quiet_hit"] else "WRONG"
        else:
            res = "stood aside"
        L.append("Morning call: <b>%s</b> → %s (it gave %d%% odds of a 300+ range)"
                 % (v.replace("_", " "), res, round((ens.get("p_range300") or 0) * 100)))
    rc = next((r for r in today_rows if r["strategy"] == "R9_recheck"), None)
    if rc:
        L.append("09:46 re-check said: %s" % esc(rc.get("status", "n/a")))

    n = st["sessions"]
    L.append("\n<b>Running tally: %d session%s</b> (rules %s)" % (n, "" if n == 1 else "s", st.get("rule_version") or ""))
    rows = ["%-15s %5s %5s %9s" % ("Direction", "hits", "rate", "95% range")]
    for s, d in st["direction"].items():
        if d["days"] == 0:
            continue
        if d["calls"]:
            rows.append("%-15s %5s %4d%% %4d-%d%%" % (_short(s), "%d/%d" % (d["hits"], d["calls"]), round(d["hit_rate"] * 100),
                                                    round(d["ci95"][0] * 100), round(d["ci95"][1] * 100)))
        else:
            rows.append("%-15s %5s" % (_short(s), "0/0"))
    L.append("<pre>%s</pre>" % esc("\n".join(rows)))
    e = st["ensemble"]
    L.append("Published call: stood aside on %d of %d days; QUIET right %d of %d. Days with a 300+ range: %d of %d."
             % (e["no_trade"], e["days"], e["quiet_hits"], e["quiet_calls"], e["big_days"], e["days"]))
    prows = ["%-15s %3s %6s %7s" % ("Big-day odds", "n", "error", "vs base")]
    for s, d in st["probability"].items():
        if d["n"]:
            prows.append("%-15s %3d %6.3f %7s" % (_short(s), d["n"], d["brier"],
                                                 "%+d%%" % round(d["skill"] * 100) if d["skill"] is not None else "n/a"))
    if len(prows) > 1:
        L.append("<pre>%s</pre>" % esc("\n".join(prows)))
        L.append("Error is the Brier score (lower is better). \"vs base\" above 0% means it beat simply quoting the recent base rate.")
    if n < 25:
        L.append("\n<i>Too early to judge: %d of the 25-30 sessions needed. A direction rule needs about 18 of 25 right "
                 "before it means anything, and with several rules running, one will look good by luck.</i>" % n)
    else:
        L.append("\n<i>With several rules side by side, one can look good by luck. Only a rule far above the coin counts.</i>")
    return "\n".join(L)


def _short(s):
    return {"S9_ensemble": "Published", "S0_coin": "Coin flip", "S3_gap": "Gap", "S4_trend": "Trend",
            "S5_meanrev": "Stretch", "S8_news": "News", "S6_orb": "Breakout 09:46", "S1_vol": "Vol model",
            "S0_clim": "Base rate", "S2_compress": "Coiled model", "R1_first30": "After 30 min"}.get(s, s)
