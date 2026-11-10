"""Telegram delivery. sendMessage only. This module never calls getUpdates."""
import html

from . import net
from .config import env

LIMIT = 3800  # Telegram's hard limit is 4096 characters


def esc(text):
    return html.escape(str(text), quote=False)


def split(text, limit=LIMIT):
    parts, cur = [], ""
    for block in text.split("\n\n"):
        while len(block) > limit:  # a single very long block: cut on lines
            cut = block.rfind("\n", 0, limit)
            cut = cut if cut > 0 else limit
            if cur:
                parts.append(cur)
                cur = ""
            parts.append(block[:cut])
            block = block[cut:].lstrip("\n")
        if cur and len(cur) + 2 + len(block) > limit:
            parts.append(cur)
            cur = block
        else:
            cur = (cur + "\n\n" + block) if cur else block
    if cur:
        parts.append(cur)
    return parts


def send(text, dry_run=False):
    """Send an HTML message, split if long. Returns the number of parts sent."""
    parts = split(text)
    if dry_run or env("NF_DRY_RUN") == "1":
        print("\n----- TELEGRAM (dry run, %d part(s)) -----\n%s\n-----" % (len(parts), "\n\n[next part]\n\n".join(parts)))
        return len(parts)
    token, chat = env("TELEGRAM_BOT_TOKEN"), env("TELEGRAM_CHAT_ID")
    if not token or not chat:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set")
    for part in parts:
        js = net.post_json("https://api.telegram.org/bot%s/sendMessage" % token,
                           {"chat_id": chat, "text": part, "parse_mode": "HTML", "disable_web_page_preview": True},
                           timeout=20, retries=1)
        if not js.get("ok"):
            raise RuntimeError("Telegram refused the message: %s" % str(js)[:200])
    return len(parts)
