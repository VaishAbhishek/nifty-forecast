"""Headline sentiment: an LLM when a key is set, a keyword lexicon otherwise.

Both paths return the same shape, and the final score is always computed
here from the per-headline labels (not taken on trust from the model).
"""
import json
import re

from . import catalysts, net
from .config import env

POSITIVE = {
    2: ["record high", "all-time high", "surge", "soar", "rally", "rate cut", "ceasefire", "stimulus", "upgrade",
        "beats estimates", "net buyers", "strong inflow", "truce", "peace deal", "gst cut", "tariff cut", "trade deal"],
    1: ["gain", "rise", "rose", "jump", "climb", "rebound", "recover", "higher", "positive", "optimism", "optimistic", "inflow",
        "fiis buy", "fiis bought", "crude falls", "oil falls", "oil slips", "rupee gains", "rupee strengthens",
        "cools", "eases", "beat", "boost", "bullish", "green", "firm"],
}
NEGATIVE = {
    2: ["crash", "plunge", "tumble", "rout", "selloff", "sell-off", "rate hike", "war", "missile", "attack", "sanction",
        "downgrade", "recession", "default", "record low", "tariff hike", "net sellers", "crisis", "bloodbath", "panic"],
    1: ["fall", "fell", "drop", "slip", "slide", "decline", "lower", "weak", "loss", "negative", "outflow", "fiis sell",
        "fiis sold", "crude jumps", "crude spikes", "oil jumps", "oil surges", "rupee falls", "rupee weakens", "miss",
        "probe", "ban", "bearish", "red", "pressure", "worry", "worries", "fear", "tension", "hawkish", "hot inflation"],
}
NEGATORS = re.compile(r"\b(not|no|despite|fails? to|unlikely|pare[sd]?|erase[sd]?|off (day'?s )?(low|high)s?)\b", re.I)
LABELS = list(catalysts.CATALYSTS) + ["other"]


def _has(text, phrase):
    # whole word, allowing common endings (gain -> gains, gained, gaining)
    return re.search(r"(?<![a-z])" + re.escape(phrase) + r"(?:s|es|ed|d|ing|ped|ping)?(?![a-z])", text) is not None


def lexicon_label(title):
    t = title.lower()
    pos = sum(w for w, words in POSITIVE.items() for p in words if _has(t, p))
    neg = sum(w for w, words in NEGATIVE.items() for p in words if _has(t, p))
    # "crude/oil rises" is bad for India; "crude/oil falls" is good
    if re.search(r"(crude|oil|brent)[^,;]{0,25}(surge|soar|jump|rise|climb|spike|rally)", t):
        pos, neg = 0, max(neg, 2)
    if re.search(r"(crude|oil|brent)[^,;]{0,25}(fall|drop|slip|slide|plunge|tumble|decline)", t):
        pos, neg = max(pos, 2), 0
    net_score = pos - neg
    if NEGATORS.search(t):
        net_score /= 2.0
    direction = 1 if net_score >= 1 else -1 if net_score <= -1 else 0
    cats = catalysts.tag(title)
    return {"relevant": bool(cats) or direction != 0, "catalyst": cats[0] if cats else "other",
            "direction": direction, "magnitude": min(3, max(1, int(abs(net_score)))) if direction else (1 if cats else 0)}


def aggregate(labels):
    """Magnitude-weighted net direction in [-1, 1], shrunk when evidence is thin."""
    rel = [l for l in labels if l.get("relevant") and l.get("magnitude", 0) > 0]
    weight = sum(l["magnitude"] for l in rel)
    score = sum(l["direction"] * l["magnitude"] for l in rel) / (weight + 3.0) if rel else 0.0
    return {"score": round(max(-1.0, min(1.0, score)), 3), "n_relevant": len(rel),
            "n_high_impact": sum(1 for l in rel if l["magnitude"] >= 3),
            "n_pos": sum(1 for l in rel if l["direction"] > 0), "n_neg": sum(1 for l in rel if l["direction"] < 0)}


PROMPT = """You are an analyst of the Indian equity index Nifty 50. Below are news headlines published since the last market close, numbered from 0.

For EACH headline give:
- "id": its number
- "relevant": true if it could plausibly move the Nifty 50 index today, else false
- "catalyst": one of %s
- "direction": 1 if positive for the Nifty today, -1 if negative, 0 if neutral or unclear
- "magnitude": 0 (none), 1 (minor), 2 (meaningful), 3 (major, could drive a 1%%+ index move)

Remember India imports oil, so higher crude is negative. Do not guess beyond what a headline says. Most headlines are minor.

Then give "overall":
- "summary": two plain sentences on what the headlines mean for the Nifty today
- "key_risk": the single biggest risk to any directional view today, one sentence
- "binary_event_today": name of any scheduled event decided DURING today's Indian session (RBI policy, Union Budget, election counting), else null
- "fii_net_cr": yesterday's FII net cash figure in Rs crore if a headline states it (negative = sold), else null
- "dii_net_cr": same for DIIs, else null

Reply with one JSON object only, exactly: {"items": [...], "overall": {...}}

Headlines:
%s"""

DEFAULT_MODELS = {"anthropic": "claude-haiku-5-5", "openai": "gpt-5-mini", "gemini": "gemini-2.5-flash"}


def provider():
    p = env("LLM_PROVIDER").lower()
    if p in DEFAULT_MODELS:
        return p
    for name, key in (("anthropic", "ANTHROPIC_API_KEY"), ("openai", "OPENAI_API_KEY"), ("gemini", "GEMINI_API_KEY")):
        if env(key):
            return name
    return None


def _call_llm(prompt):
    p = provider()
    if not p:
        raise RuntimeError("no LLM key set")
    model = env("LLM_MODEL") or DEFAULT_MODELS[p]
    if p == "anthropic":
        js = net.post_json("https://api.anthropic.com/v1/messages",
                           {"model": model, "max_tokens": 4000, "messages": [{"role": "user", "content": prompt}]},
                           headers={"x-api-key": env("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"}, timeout=45)
        return "".join(b.get("text", "") for b in js.get("content", []) if b.get("type") == "text"), p, model
    if p == "openai":
        js = net.post_json("https://api.openai.com/v1/chat/completions",
                           {"model": model, "messages": [{"role": "user", "content": prompt}],
                            "response_format": {"type": "json_object"}},
                           headers={"Authorization": "Bearer " + env("OPENAI_API_KEY")}, timeout=45)
        return js["choices"][0]["message"]["content"], p, model
    js = net.post_json("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % model,
                       {"contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"responseMimeType": "application/json", "temperature": 0}},
                       headers={"x-goog-api-key": env("GEMINI_API_KEY")}, timeout=45)
    return js["candidates"][0]["content"]["parts"][0]["text"], p, model


def _parse(text, n):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object in reply")
    js = json.loads(text[start:end + 1])
    labels = [None] * n
    for it in js.get("items", []):
        i = it.get("id")
        if not isinstance(i, int) or not 0 <= i < n:
            continue
        d, m = int(it.get("direction", 0)), int(it.get("magnitude", 0))
        if d not in (-1, 0, 1) or not 0 <= m <= 3:
            continue
        cat = it.get("catalyst") if it.get("catalyst") in LABELS else "other"
        labels[i] = {"relevant": bool(it.get("relevant")), "catalyst": cat, "direction": d, "magnitude": m}
    if sum(1 for l in labels if l) < max(1, n // 2):
        raise ValueError("reply labelled fewer than half the headlines")
    return labels, js.get("overall") or {}


def _num(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def score(headlines, use_llm=True):
    """Label every headline and return the combined view. Never raises."""
    lex = [lexicon_label(h["title"]) for h in headlines]
    out = {"method": "lexicon", "model": None, "llm_error": None, "summary": None, "key_risk": None,
           "binary_event_today": catalysts.binary_event_today(headlines), "fii_net_cr": None, "dii_net_cr": None,
           "labels": lex}
    if use_llm and headlines and provider():
        try:
            listing = "\n".join("%d. [%s] %s" % (i, h["source"], h["title"]) for i, h in enumerate(headlines))
            text, p, model = _call_llm(PROMPT % (", ".join(LABELS), listing))
            labels, overall = _parse(text, len(headlines))
            out.update(method="llm", model="%s/%s" % (p, model),
                       labels=[l or lex[i] for i, l in enumerate(labels)],
                       summary=str(overall.get("summary") or "")[:500] or None,
                       key_risk=str(overall.get("key_risk") or "")[:300] or None,
                       fii_net_cr=_num(overall.get("fii_net_cr")), dii_net_cr=_num(overall.get("dii_net_cr")))
            ev = overall.get("binary_event_today")
            if ev and str(ev).lower() not in ("null", "none", "false"):
                out["binary_event_today"] = str(ev)[:120]
        except Exception as e:  # any failure falls back to the lexicon
            out["llm_error"] = str(e)[:200]
    elif use_llm and not provider():
        out["llm_error"] = "no LLM key set"
    out.update(aggregate(out["labels"]))
    out["lexicon_score"] = aggregate(lex)["score"]
    cats = {}
    for h, l in zip(headlines, out["labels"]):
        if l["relevant"] and l["catalyst"] != "other":
            cats.setdefault(l["catalyst"], []).append(h["title"])
    out["catalysts"] = cats
    return out
