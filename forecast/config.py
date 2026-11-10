"""Paths, environment and small shared helpers. Standard library only."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
CODE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("NF_DATA_DIR") or (CODE_DIR.parent / "nifty-forecast-data"))
CONFIG_DIR = CODE_DIR / "config"

BIG_MOVE_PTS = 300  # the "big day" threshold the user asked about

# Names of env values that must never appear in logs, status files or Telegram.
SECRET_KEYS = (
    "UPSTOX_ANALYTICS_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
)


def env(name, default=""):
    return (os.environ.get(name) or default).strip()


def now_ist():
    """Current time in IST. NF_FAKE_NOW (ISO timestamp) overrides it for tests only."""
    fake = os.environ.get("NF_FAKE_NOW")
    if fake:
        return datetime.fromisoformat(fake).astimezone(IST)
    return datetime.now(IST)


def redact(text):
    """Remove any secret value from a string before it is logged or pushed."""
    s = str(text)
    for k in SECRET_KEYS:
        v = env(k)
        if v and len(v) >= 6:
            s = s.replace(v, "<%s>" % k)
    return s


def git_sha():
    """Short commit id of the code that is running, read without calling git."""
    try:
        head = (CODE_DIR / ".git" / "HEAD").read_text().strip()
        if head.startswith("ref:"):
            ref = CODE_DIR / ".git" / head.split(" ", 1)[1]
            if ref.exists():
                return ref.read_text().strip()[:10]
            packed = CODE_DIR / ".git" / "packed-refs"
            if packed.exists():
                for line in packed.read_text().splitlines():
                    if line.endswith(head.split(" ", 1)[1]):
                        return line.split(" ")[0][:10]
            return "unknown"
        return head[:10]
    except Exception:
        return "unknown"
