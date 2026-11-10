"""Headline collection from RSS. No NSE scraping."""
import html
import json
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from . import net
from .config import CONFIG_DIR, IST, now_ist

MARKET_WORDS = re.compile(
    r"nifty|sensex|market|stock|share|equit|fii|fpi|dii|rupee|rbi|repo|inflation|cpi|gdp|fed\b|fomc|"
    r"crude|oil|brent|opec|tariff|budget|election|earnings|results|q[1-4]\b|profit|bank|sebi|ipo|"
    r"wall street|dow|nasdaq|s&p|gift|yield|dollar|war|sanction|ceasefire|recession|rate cut|rate hike|gold",
    re.I)
TAGS = re.compile(r"<[^>]+>")


def load_feeds():
    return json.loads((CONFIG_DIR / "feeds.json").read_text())["feeds"]


def _text(el, names):
    for child in el:
        if child.tag.split("}")[-1].lower() in names and (child.text or child.attrib.get("href")):
            return (child.text or child.attrib.get("href") or "").strip()
    return ""


def _when(raw):
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST)


def parse_feed(raw, source):
    """RSS or Atom bytes -> list of {title, source, ts, link}."""
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        # some feeds ship stray bytes before the XML declaration
        start = raw.find(b"<")
        root = ET.fromstring(raw[start:])
    items = []
    for el in root.iter():
        if el.tag.split("}")[-1].lower() not in ("item", "entry"):
            continue
        title = html.unescape(TAGS.sub("", _text(el, ("title",)))).strip()
        ts = _when(_text(el, ("pubdate", "published", "updated", "date")))
        if title and ts:
            items.append({"title": re.sub(r"\s+", " ", title), "source": source, "ts": ts,
                          "link": _text(el, ("link",))})
    return items


def fetch_feed(feed):
    """Returns (items, health dict). Never raises."""
    health = {"name": feed["name"], "ok": False, "items": 0, "newest_h": None, "error": None}
    try:
        _, raw = net.request(feed["url"], timeout=10, retries=0,
                             headers={"Accept": "application/rss+xml, application/xml, text/xml, */*"})
        items = parse_feed(raw, feed["name"])
        health["items"] = len(items)
        if items:
            newest = max(i["ts"] for i in items)
            health["newest_h"] = round((now_ist() - newest).total_seconds() / 3600, 1)
            health["ok"] = health["newest_h"] <= 48  # older than two days = treat as dead
            if not health["ok"]:
                health["error"] = "stale feed"
        else:
            health["error"] = "no dated items"
        return items, health
    except Exception as e:  # network, parse
        health["error"] = str(e)[:160]
        return [], health


def norm(title):
    return re.sub(r"[^a-z0-9 ]", "", title.lower())[:80].strip()


def collect(since, limit=40, feeds=None):
    """Market headlines published after `since`, newest first, de-duplicated."""
    feeds = feeds or load_feeds()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch_feed, feeds))
    health = [h for _, h in results]
    seen, out = set(), []
    for items, _ in results:
        for it in items:
            if it["ts"] < since or it["ts"] > now_ist():
                continue
            title = re.sub(r"\s+-\s+[^-]{2,40}$", "", it["title"]) if it["source"].startswith("Google") else it["title"]
            key = norm(title)
            if not key or key in seen or not MARKET_WORDS.search(title):
                continue
            seen.add(key)
            out.append(dict(it, title=title))
    out.sort(key=lambda i: i["ts"], reverse=True)
    return out[:limit], health


FLOW = re.compile(
    r"\b(FIIs?|FPIs?|foreign (?:institutional |portfolio )?investors|DIIs?|domestic (?:institutional )?investors)\b"
    r"[^.;]{0,60}?\b(net )?(sold|sell|offload\w*|dump\w*|pull\w* out|withdr\w+|bought|buy|purchas\w+|pump\w*|invest\w*|infus\w*)\b"
    r"[^.;]{0,50}?(?:Rs\.?|₹|INR)\s?([\d,]+(?:\.\d+)?)\s*(lakh crore|crore|cr\b)", re.I)


def flows_from_headlines(headlines):
    """Best-effort FII/DII net cash figures (Rs crore) mentioned in headlines."""
    out = {"fii_net_cr": None, "dii_net_cr": None, "source": None}
    for h in headlines:
        for m in FLOW.finditer(h["title"]):
            who = "fii" if m.group(1).lower()[0] == "f" else "dii"
            amt = float(m.group(4).replace(",", ""))
            if "lakh" in m.group(5).lower():
                amt *= 100000
            verb = m.group(3).lower()
            sign = -1 if re.match(r"sold|sell|offload|dump|pull|withdr", verb) else 1
            if out[who + "_net_cr"] is None and amt < 100000:  # daily figures only
                out[who + "_net_cr"] = sign * amt
                out["source"] = h["source"]
    return out
