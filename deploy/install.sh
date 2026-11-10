#!/usr/bin/env bash
# One-time installer for the Nifty forecast agent. Safe to run again after updates.
#
# It creates files only under ~/nifty-forecast, ~/nifty-forecast-data, ~/.nifty_forecast_env
# and /etc/systemd/system/nifty-forecast*. It never edits, restarts, stops or signals
# nifty_bot.service; it only reads that service's state to prove it was left alone.
set -euo pipefail

USER_NAME="$(id -un)"
HOME_DIR="$HOME"
CODE="$HOME_DIR/nifty-forecast"
DATA="$HOME_DIR/nifty-forecast-data"
ENVF="$HOME_DIR/.nifty_forecast_env"
KEY="$HOME_DIR/.ssh/nifty_forecast_deploy"
BOT_UNIT="nifty_bot.service"
say() { printf '\n== %s\n' "$*"; }
bot_state() { systemctl show "$BOT_UNIT" -p ActiveState -p MainPID -p NRestarts -p ActiveEnterTimestamp 2>/dev/null | tr '\n' ' '; }

[ "$(cd "$(dirname "$0")/.." && pwd)" = "$CODE" ] || { echo "Clone this repo to $CODE first (it is at $(cd "$(dirname "$0")/.." && pwd))."; exit 1; }
[ -f "$KEY" ] && export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"

say "EMA bot state before install (read-only check)"
BEFORE="$(bot_state)"; echo "${BEFORE:-$BOT_UNIT not found}"

say "Checking Python and systemd"
python3 -c 'import sys, zoneinfo; assert sys.version_info >= (3, 9), "Python 3.9+ needed"; zoneinfo.ZoneInfo("Asia/Kolkata"); print("python", sys.version.split()[0])'
systemd-analyze calendar "Mon..Fri *-*-* 09:16:00 Asia/Kolkata" | sed -n '1,4p'

say "Data folder (the 'data' branch of the same repo)"
if [ ! -d "$DATA/.git" ]; then
  git clone -q --branch data --single-branch "$(git -C "$CODE" remote get-url origin)" "$DATA"
fi
git -C "$DATA" config user.name "nifty-forecast-vm"
git -C "$DATA" config user.email "nifty-forecast-vm@users.noreply.github.com"
mkdir -p "$DATA/cache"
echo "ok: $DATA"

say "Credentials file"
if [ ! -f "$ENVF" ]; then
  install -m 600 "$CODE/deploy/env.example" "$ENVF"
  echo "Created $ENVF. Fill in the values:   nano $ENVF"
  echo "Then run this installer again:        $CODE/deploy/install.sh"
  exit 0
fi
chmod 600 "$ENVF"
if grep -qE '^\s*export\s' "$ENVF"; then echo "Remove the word 'export' from $ENVF (systemd rejects it)."; exit 1; fi
for k in UPSTOX_ANALYTICS_TOKEN TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID; do
  grep -qE "^$k=.+" "$ENVF" || { echo "$k is empty in $ENVF. Fill it in and run this again."; exit 1; }
done
if [ -f "$HOME_DIR/.nifty_bot_env" ]; then
  a="$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENVF" | cut -d= -f2-)"
  b="$(grep -E '^(TELEGRAM_BOT_TOKEN|TELEGRAM_TOKEN|BOT_TOKEN)=' "$HOME_DIR/.nifty_bot_env" | head -1 | cut -d= -f2- || true)"
  [ -n "$b" ] && [ "$a" = "$b" ] && echo "NOTE: this is the SAME Telegram bot token as the EMA bot. It works, but a separate bot is safer."
fi
echo "ok: keys present, permissions 600"

say "Offline tests (no network, no credentials used)"
( cd "$CODE" && python3 -m unittest discover -s tests 2>&1 | tail -3 )

say "Installing systemd units (needs sudo)"
tmp="$(mktemp -d)"
for f in "$CODE"/deploy/*.service "$CODE"/deploy/*.timer; do
  sed -e "s|__USER__|$USER_NAME|g" -e "s|__HOME__|$HOME_DIR|g" "$f" > "$tmp/$(basename "$f")"
done
sudo install -m 644 "$tmp"/* /etc/systemd/system/
rm -rf "$tmp"
sudo systemctl daemon-reload
sudo systemctl enable --now nifty-forecast-morning.timer nifty-forecast-recheck.timer nifty-forecast-score.timer nifty-forecast-sync.timer
cat "$CODE"/deploy/*.service "$CODE"/deploy/*.timer | sha256sum | cut -c1-16 > "$DATA/cache/installed_units"

say "Live self-test, run through systemd so the sandbox is tested too"
sudo systemctl start nifty-forecast@selftest.service || true
journalctl -u nifty-forecast@selftest.service --no-pager -o cat -n 25

say "First sync with GitHub (sends the self-test result so it can be reviewed remotely)"
sudo systemctl start nifty-forecast-sync.service || true
journalctl -u nifty-forecast-sync.service --no-pager -o cat -n 3

say "Timers"
systemctl list-timers 'nifty-forecast*' --no-pager

say "EMA bot state after install"
AFTER="$(bot_state)"; echo "${AFTER:-$BOT_UNIT not found}"
if [ "$BEFORE" = "$AFTER" ]; then echo "UNCHANGED: same state, same process id, same restart count."; else echo "DIFFERENT from before: check 'systemctl status $BOT_UNIT'. This installer does not touch it, so look for another cause."; fi
