"""JSONL prediction log and small JSON state files in the data directory."""
import json
import os

from .config import DATA_DIR, now_ist, redact

PRED = "predictions.jsonl"


def _path(name):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    p = DATA_DIR / name
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load(name=PRED):
    p = _path(name)
    if not p.exists():
        return []
    rows = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def append(rows, name=PRED):
    with open(_path(name), "a") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")


def rewrite(rows, name=PRED):
    p = _path(name)
    tmp = p.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    os.replace(tmp, p)


def write_json(name, obj):
    p = _path(name)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(redact(json.dumps(obj, indent=1, sort_keys=True, default=str)))
    os.replace(tmp, p)


def read_json(name, default=None):
    p = _path(name)
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def set_status(command, ok, checks, extra=None):
    """Health of the last run of each command. Pushed to the data branch."""
    from .config import git_sha
    st = read_json("status.json", {}) or {}
    st[command] = {"ts": now_ist().isoformat(timespec="seconds"), "ok": ok, "code": git_sha(),
                   "checks": checks, **(extra or {})}
    write_json("status.json", st)


def log(msg):
    line = "%s %s" % (now_ist().isoformat(timespec="seconds"), redact(msg))
    print(line, flush=True)
    try:
        with open(_path("log/%s.log" % now_ist().strftime("%Y-%m")), "a") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
