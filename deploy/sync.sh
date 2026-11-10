#!/usr/bin/env bash
# Pushes the agent's logs to the "data" branch and pulls code updates from "main".
# Touches only ~/nifty-forecast and ~/nifty-forecast-data. Never the EMA bot.
set -u
# Wrapped in a function so bash reads the whole file before running it
# (this script can update itself during the pull).
main() {
CODE="${NF_CODE_DIR:-$HOME/nifty-forecast}"
DATA="${NF_DATA_DIR:-$HOME/nifty-forecast-data}"
KEY="$HOME/.ssh/nifty_forecast_deploy"
if [ -z "${GIT_SSH_COMMAND:-}" ] && [ -f "$KEY" ]; then
  export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
fi
now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
pull="skipped"; push="ok"; reinstall="no"

# 1. code: fast-forward only, so a local edit is never overwritten
if [ -e "$HOME/.nifty_forecast_no_autopull" ]; then
  pull="disabled by ~/.nifty_forecast_no_autopull"
elif git -C "$CODE" fetch -q origin main 2>/dev/null; then
  before="$(git -C "$CODE" rev-parse --short HEAD)"
  if git -C "$CODE" merge -q --ff-only origin/main 2>/dev/null; then
    after="$(git -C "$CODE" rev-parse --short HEAD)"
    pull="ok $before -> $after"
  else
    pull="FAILED: local changes block a fast-forward (at $before)"
  fi
else
  pull="FAILED: could not reach GitHub"
fi

# 2. do the installed systemd files still match the repo?
want="$(cat "$CODE"/deploy/*.service "$CODE"/deploy/*.timer 2>/dev/null | sha256sum | cut -c1-16)"
have="$(cat "$DATA/cache/installed_units" 2>/dev/null || echo none)"
[ "$want" != "$have" ] && reinstall="YES: run ./deploy/install.sh again"

# 3. data: commit and push whatever the runs wrote
mkdir -p "$DATA"
printf '{"ts": "%s", "pull": "%s", "reinstall_needed": "%s", "code": "%s"}\n' \
  "$now" "$pull" "$reinstall" "$(git -C "$CODE" rev-parse --short HEAD 2>/dev/null)" > "$DATA/sync_status.json"
git -C "$DATA" add -A
git -C "$DATA" diff --cached --quiet || git -C "$DATA" commit -qm "data $now"
if ! git -C "$DATA" push -q origin HEAD:data 2>/dev/null; then
  # someone else pushed to the branch: replay our commits on top and retry once
  git -C "$DATA" pull -q --rebase origin data 2>/dev/null && git -C "$DATA" push -q origin HEAD:data 2>/dev/null || push="FAILED"
fi
echo "sync $now | pull: $pull | push: $push | reinstall needed: $reinstall"
[ "$push" = "ok" ]
}
main "$@"; exit $?
