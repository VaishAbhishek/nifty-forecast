"""The pre-registered rules. Each one is logged and scored on its own.

DO NOT edit a threshold in place once the forward test has started. Change
RULE_VERSION when a rule changes, so the old and new versions are counted
separately. The rule hash is written on every logged prediction.
"""
import hashlib

# v2 (2026-11-11): the news vote counts only "driver" headlines. Headlines that merely
# restate where the index opened are excluded, because they repeat the gap. Sources
# take turns and reworded copies of one story are merged.
RULE_VERSION = "v2"
RULES = {
    "gap_fade_max_pct": 0.30,      # S3: gaps smaller than this are faded
    "gap_min_pct": 0.05,           # S3: below this there is no gap to speak of
    "rsi2_low": 10, "rsi2_high": 90, "streak_days": 3,  # S5
    "news_lean": 0.40,             # S8: |score| needed for a news vote
    "net_votes_for_lean": 2,       # S9
    "quiet_max_p_range": 0.25,     # S9: QUIET needs big-day odds below this
    "max_p_dir": 0.60, "p_dir_step": 0.03,  # stated direction odds: an assumption, capped
    "orb_minutes": 15,             # S6 (logged at the re-check)
    "recheck_confirm_pct": 0.10, "recheck_invalid_pct": 0.25,
    "big_move_pts": 300,
}
# Hash of this whole file, so any change to a threshold OR to the logic shows up in the log.
with open(__file__, "rb") as _fh:
    RULE_HASH = hashlib.sha256(_fh.read()).hexdigest()[:10]
WORD = {1: "UP", -1: "DOWN", 0: "NONE"}


def coin(day):
    """A fixed, reproducible coin flip for the date. The baseline to beat."""
    return 1 if int(hashlib.sha256(day.encode()).hexdigest(), 16) % 2 == 0 else -1


def s3_gap(f):
    g = f["gap_pct"]
    if abs(g) < RULES["gap_min_pct"]:
        return 0, "no real gap (%+.2f%%)" % g
    if abs(g) < RULES["gap_fade_max_pct"]:
        return (-1 if g > 0 else 1), "small gap %+.2f%%: small gaps have tended to fill" % g
    if abs(g) < 1.0:
        return 0, "mid-size gap %+.2f%%: no rule" % g
    return 0, "large gap %+.2f%%: past studies conflict, no vote" % g


def s4_trend(f):
    c, e20, e50, e200 = f["prev_close"], f["ema20"], f["ema50"], f["ema200"]
    if e200 is None:
        return 0, "not enough history for the 200-day average"
    if c > e20 > e50 and c > e200:
        return 1, "uptrend: close above the 20, 50 and 200-day averages"
    if c < e20 < e50 and c < e200:
        return -1, "downtrend: close below the 20, 50 and 200-day averages"
    return 0, "no clean trend"


def s5_meanrev(f):
    r2, st = f["rsi2"], f["streak"]
    if r2 is not None and (r2 < RULES["rsi2_low"] or st <= -RULES["streak_days"]):
        return 1, "oversold (RSI2 %.0f, streak %+d)" % (r2, st)
    if r2 is not None and (r2 > RULES["rsi2_high"] or st >= RULES["streak_days"]):
        return -1, "overbought (RSI2 %.0f, streak %+d)" % (r2, st)
    return 0, "not stretched (RSI2 %s, streak %+d)" % ("%.0f" % r2 if r2 is not None else "n/a", st)


def s8_news(sent):
    s = sent["score"]
    if sent["n_relevant"] == 0:
        return 0, "no driver headlines"
    if s >= RULES["news_lean"]:
        return 1, "driver news positive (%+.2f)" % s
    if s <= -RULES["news_lean"]:
        return -1, "driver news negative (%+.2f)" % s
    return 0, "driver news mixed (%+.2f)" % s


def ensemble(f, sent, outages):
    """The published verdict: UP / DOWN / QUIET / NO_TRADE, with reasons."""
    votes = {"S3_gap": s3_gap(f), "S4_trend": s4_trend(f), "S5_meanrev": s5_meanrev(f), "S8_news": s8_news(sent)}
    net_votes = sum(v for v, _ in votes.values())
    rm = f.get("range_model") or {}
    p_range = rm.get("p_range")
    need = RULES["net_votes_for_lean"]
    reasons = []
    news_vote = votes["S8_news"][0]
    if sent.get("binary_event_today"):
        verdict = "NO_TRADE"
        reasons.append("An event is decided during today's session: %s" % sent["binary_event_today"])
    elif len(outages) >= 2:
        verdict = "NO_TRADE"
        reasons.append("Too many inputs missing: %s" % ", ".join(outages))
    elif news_vote and any(votes[k][0] == -news_vote for k in ("S3_gap", "S4_trend", "S5_meanrev")):
        verdict = "NO_TRADE"
        reasons.append("News and price signals point in opposite directions")
    elif net_votes >= need and votes["S3_gap"][0] != -1:
        verdict = "UP"
    elif net_votes <= -need and votes["S3_gap"][0] != 1:
        verdict = "DOWN"
    elif abs(net_votes) >= need:
        verdict = "NO_TRADE"
        reasons.append("The opening gap points against the other price signals")
    elif p_range is not None and p_range < RULES["quiet_max_p_range"] and not sent.get("n_high_impact"):
        verdict = "QUIET"
        reasons.append("No directional agreement, low odds of a big day and no high-impact news")
    else:
        verdict = "NO_TRADE"
        reasons.append("Signals are weak or split (net vote %+d of 4)" % net_votes)
    p_up = 0.5
    if verdict in ("UP", "DOWN"):
        edge = min(RULES["max_p_dir"] - 0.5, RULES["p_dir_step"] * abs(net_votes))
        p_up = 0.5 + edge if verdict == "UP" else 0.5 - edge
    return {"verdict": verdict, "votes": {k: {"vote": v, "why": w} for k, (v, w) in votes.items()},
            "net_votes": net_votes, "reasons": reasons, "p_up": round(p_up, 3)}


def orb(bars_5m_closes, or_high, or_low):
    """S6: first 5-minute close outside the opening range. +1 up, -1 down, 0 none."""
    for c in bars_5m_closes:
        if c > or_high:
            return 1
        if c < or_low:
            return -1
    return 0


def recheck_status(verdict, move_pct, p_range_new, range_so_far, news_vote, new_high_impact):
    """Is the 09:16 call still standing 30 minutes later? Returns (status, reason)."""
    conf, inval = RULES["recheck_confirm_pct"], RULES["recheck_invalid_pct"]
    big = RULES["big_move_pts"]
    if verdict in ("UP", "DOWN"):
        signed = move_pct if verdict == "UP" else -move_pct
        if signed <= -inval:
            return "INVALIDATED", "price has moved %.2f%% against the call" % abs(move_pct)
        if news_vote and news_vote != (1 if verdict == "UP" else -1):
            return "WEAKENED", "new headlines lean the other way"
        if signed >= conf:
            return "STILL VALID", "price is moving with the call (%+.2f%% from the open)" % move_pct
        return "UNCONFIRMED", "price has not committed either way (%+.2f%% from the open)" % move_pct
    if verdict == "QUIET":
        if range_so_far >= big * 2 / 3 or (p_range_new is not None and p_range_new >= 0.5):
            return "INVALIDATED", "the first 30 minutes were too wide for a quiet day"
        if new_high_impact:
            return "WEAKENED", "new high-impact headlines since the open"
        if p_range_new is not None and p_range_new < RULES["quiet_max_p_range"]:
            return "STILL VALID", "narrow first 30 minutes, big-day odds still low"
        return "WEAKENED", "big-day odds have risen"
    return "STILL NO TRADE", "the morning call was to stand aside; this update is information only"
