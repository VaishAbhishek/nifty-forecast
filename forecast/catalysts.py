"""Catalyst types, how to spot them in a headline, and what history says.

The history notes come from published studies and news archives, most of them
small samples or non-peer-reviewed. They describe what happened before, not
what will happen today, and mostly say more about the SIZE of moves than the
direction.
"""
import re

CATALYSTS = {
    "oil_geo": {
        "label": "Oil / geopolitics",
        "pattern": r"crude|brent|opec|oil price|war\b|missile|strike on|attack|sanction|ceasefire|iran|israel|russia|ukraine|tension|border|red sea|hormuz|pakistan",
        "history": "No credible quantified Nifty study found. Oil spikes hurt India as an importer and "
                   "ceasefires tend to help, but sizes vary a lot. Treated as a volatility flag, not a direction rule.",
    },
    "rbi": {
        "label": "RBI policy",
        "pattern": r"\brbi\b|repo rate|monetary policy|\bmpc\b|reserve bank",
        "history": "One study of 72 RBI decisions (2014 to Apr 2025): Nifty averaged +0.21% on the day and rose on 62.5% of them, "
                   "typical swing about 0.9%. Recent days moved between -0.76% and +1.02%. Studies disagree on rate-cut days.",
    },
    "fed": {
        "label": "US Fed",
        "pattern": r"\bfed\b|fomc|powell|federal reserve|fed chair|us rate",
        "history": "The reaction lands in the NEXT Indian session and is mostly in the opening gap. One compilation shows a median "
                   "of about -0.2% the day after a decision. Small sample.",
    },
    "cpi": {
        "label": "Inflation data",
        "pattern": r"\bcpi\b|inflation|\bwpi\b|consumer price",
        "history": "No systematic Nifty study found for India or US CPI days. Evidence is anecdotal (for example a hot US print "
                   "in Oct 2026 was followed by about -0.7%).",
    },
    "election": {
        "label": "Elections",
        "pattern": r"election|exit poll|counting day|vote count|poll result|assembly poll|lok sabha",
        "history": "Extreme and rare. 4 Jun 2024 result day: -5.93%, recovered within three sessions; exit-poll day before: +3%. "
                   "No direction call is made on a counting day.",
    },
    "budget": {
        "label": "Union Budget",
        "pattern": r"\bbudget\b|finance minister|fiscal deficit|\bfm\b sitharaman",
        "history": "Budget days since 2010 averaged about +0.19%, and 12 of 14 closed within 2% either way. "
                   "The range matters more than the direction.",
    },
    "earnings": {
        "label": "Earnings",
        "pattern": r"\bq[1-4]\b|results|earnings|net profit|revenue|guidance|reliance|hdfc bank|\btcs\b|infosys|icici bank",
        "history": "No credible index-level study found for heavyweight results. Usually a stock-level driver that moves "
                   "the index only when several large names surprise the same way.",
    },
    "global_riskoff": {
        "label": "Global risk-off / risk-on",
        "pattern": r"wall street|dow jones|nasdaq|s&p 500|selloff|sell-off|rout|recession|tariff|trade war|asian (shares|markets)|"
                   r"global (cues|markets)|bond yield|treasury|dollar index|risk-off|plunge|crash",
        "history": "Mostly already in the opening gap by 09:15. Tail events are large (23 Mar 2020: -12.4%) but rare.",
    },
}

_COMPILED = {k: re.compile(v["pattern"], re.I) for k, v in CATALYSTS.items()}

# Things that are decided DURING today's session. No direction call on such days.
BINARY_TODAY = re.compile(
    r"(rbi|mpc|repo rate|monetary policy)[^.]{0,40}\btoday\b|\btoday\b[^.]{0,40}(rbi policy|mpc (decision|outcome)|repo rate)|"
    r"budget (day|today|2\d{3} live)|\btoday\b[^.]{0,30}\bbudget\b|"
    r"counting (day|begins|underway|of votes)|election results? (today|live)|results day",
    re.I)


def tag(title):
    """Catalyst keys that a headline matches."""
    return [k for k, rx in _COMPILED.items() if rx.search(title)]


def binary_event_today(headlines):
    for h in headlines:
        if BINARY_TODAY.search(h["title"]):
            return h["title"]
    return None
