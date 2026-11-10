"""Tiny HTTP helper on urllib with timeouts, one retry and secret redaction."""
import gzip
import json
import time
import urllib.error
import urllib.request

from .config import redact

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


class NetError(Exception):
    pass


def request(url, method="GET", headers=None, data=None, timeout=12, retries=1):
    """Return (status, body_bytes). Raises NetError with a redacted message."""
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    hdrs.update(headers or {})
    body = None
    if data is not None:
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
        hdrs.setdefault("Content-Type", "application/json")
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return r.status, raw
        except urllib.error.HTTPError as e:
            detail = ""
            try:
                detail = e.read()[:300].decode("utf-8", "replace")
            except Exception:
                pass
            last = NetError(redact("HTTP %s for %s: %s" % (e.code, url.split("?")[0], detail)))
            if e.code not in (429, 500, 502, 503, 504):
                break
        except Exception as e:  # timeouts, DNS, TLS, resets
            last = NetError(redact("%s for %s: %s" % (type(e).__name__, url.split("?")[0], e)))
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    raise last


def get_json(url, headers=None, timeout=12, retries=1):
    _, raw = request(url, headers=headers, timeout=timeout, retries=retries)
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        raise NetError(redact("Non-JSON response from %s" % url.split("?")[0]))


def post_json(url, payload, headers=None, timeout=30, retries=0):
    _, raw = request(url, method="POST", headers=headers, data=payload, timeout=timeout, retries=retries)
    try:
        return json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        raise NetError(redact("Non-JSON response from %s" % url.split("?")[0]))
