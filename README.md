# nifty-forecast

A morning forecast agent for the Nifty 50. It is **advisory, read-only and paper only**: it reads market data and news, sends Telegram messages and writes log files. It cannot place an order, and it does not import, signal, restart or share anything with `nifty_bot.service`.

## What it sends each trading day

| Time (IST) | Message | What it does |
|---|---|---|
| 09:16 | Morning call | One verdict (UP-lean / DOWN-lean / QUIET / NO TRADE), odds of a 300+ point day, how each signal voted, quant setup, Brent / USD-INR / GIFT / US closes, FII/DII if a headline carries it, scored headlines, matched catalysts with their history, key risk |
| 09:46 | 30-minute re-check | Whether the 09:16 call is STILL VALID / UNCONFIRMED / WEAKENED / INVALIDATED, the first-30-minute range, updated 300+ odds, new headlines since the open |
| 15:45 | Scorecard | What actually happened, whether the call was right, and the running hit rate of every rule against a coin flip |

Weekends and NSE holidays are skipped (Upstox holiday API first, `config/holidays.json` as fallback).

## Read this before trusting it

- Direction from the open is close to a coin flip. The stated direction odds are capped at 60% and are an assumption until the forward test says otherwise.
- The more predictable part is quiet day versus big day, so the 300+ odds are the output most worth judging.
- NO TRADE is the default. It is returned when news and price signals disagree, when signals are weak, when two or more inputs are missing, or when an event (RBI policy, Budget, election counting) is decided during the session.
- Nothing is backtested on news. Every call is logged before the outcome is known and scored afterwards.
- Do not judge any rule before 25 to 30 sessions. Even then a rule needs roughly 18 of 25 right to mean anything, and with several rules running side by side one will look good by luck.

## The rules being forward-tested

All of them are logged separately every day in `predictions.jsonl`, with a hash of the rules file.

| Id | Rule | Votes in the verdict? |
|---|---|---|
| S0_coin | A fixed coin flip per date: the baseline to beat | no |
| S0_clim | 300+ odds = share of the last 60 sessions with a 300+ range: the baseline for odds | no |
| S1_vol | 300+ odds from recent ATR and India VIX, calibrated on about 500 past sessions | sets the odds |
| S2_compress | Same, using only past days that were similarly "coiled" (NR7 or ATR squeeze) | no |
| S3_gap | Gaps under 0.30% tend to fill: lean against the gap. No vote on larger gaps | yes |
| S4_trend | Close above (below) the 20, 50 and 200-day averages | yes |
| S5_meanrev | RSI(2) under 10 or three down closes: up. Over 90 or three up closes: down | yes |
| S8_news | Headline tone at or beyond 0.40 either way | yes |
| S9_ensemble | **The published verdict.** Needs a net of 2 votes, no opposing gap, and no conflict between news and price | |
| S6_orb | 09:46: first 5-minute close outside the first 15-minute range | no, logged only |
| R1_first30 | 09:46: 300+ odds given the first 30 minutes | no, logged only |

To change a rule, bump `RULE_VERSION` in `forecast/strategies.py`. Old and new versions are then counted separately. Editing a threshold in place would spoil the test.

## Setup (once, on the VM)

**1. Deploy key, so the VM can pull code and push its logs for this one repo only**

```bash
ssh-keygen -t ed25519 -N "" -C nifty-forecast-vm -f ~/.ssh/nifty_forecast_deploy
cat ~/.ssh/nifty_forecast_deploy.pub
```

Paste the printed line at GitHub → this repo → Settings → Deploy keys → Add deploy key, and tick **Allow write access**.

**2. Clone and run the installer**

```bash
GIT_SSH_COMMAND="ssh -i ~/.ssh/nifty_forecast_deploy -o IdentitiesOnly=yes" \
  git clone git@github.com:VaishAbhishek/nifty-forecast.git ~/nifty-forecast
~/nifty-forecast/deploy/install.sh
```

The first run creates `~/.nifty_forecast_env` and stops.

**3. Fill in the keys, then run the installer again**

```bash
nano ~/.nifty_forecast_env
~/nifty-forecast/deploy/install.sh
```

The second run installs the timers, runs a live self-test inside the sandbox, sends a test message to Telegram, pushes the result to GitHub, and prints the EMA bot's state before and after so you can see it was not touched.

## Env keys (`~/.nifty_forecast_env`)

Plain `KEY=VALUE`, no `export`, no quotes.

| Key | Needed | Notes |
|---|---|---|
| `UPSTOX_ANALYTICS_TOKEN` | yes | Copy the value the EMA bot uses. Do not generate a new token: that revokes the bot's |
| `TELEGRAM_BOT_TOKEN` | yes | A new bot from @BotFather. Press Start on it once |
| `TELEGRAM_CHAT_ID` | yes | Your chat id, the same number the EMA bot uses |
| `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` or `GEMINI_API_KEY` | no | One is enough. With none, headlines are scored by the keyword list |
| `LLM_PROVIDER`, `LLM_MODEL` | no | Override the provider or model id. Model ids change, so set `LLM_MODEL` if the self-test reports the default is not found |

## Run and monitor

```bash
systemctl list-timers 'nifty-forecast*'                      # next run times
journalctl -u 'nifty-forecast@*' --since today -o cat        # today's output
cat ~/nifty-forecast-data/status.json                        # health of the last run of each job
sudo systemctl start nifty-forecast@selftest.service         # test every live dependency now
cd ~/nifty-forecast && set -a && source ~/.nifty_forecast_env && set +a \
  && NF_DATA_DIR=~/nifty-forecast-data python3 -m forecast.run morning --force --dry-run   # manual run, prints instead of sending
python3 -m unittest discover -s tests                        # offline tests, no network
```

A `--force` run outside the normal window is logged as `manual` and never counted in the score, because it would know more than a 09:16 call.

If a run breaks, you get a short "run failed" Telegram message, so silence never passes for "no call".

## Files

- `~/nifty-forecast/`: this repo (`main` branch). Standard-library Python only, nothing to `pip install`.
- `~/nifty-forecast-data/`: the `data` branch. `predictions.jsonl` (every prediction and outcome), `scores.json` (running tally), `status.json`, `runs/` (full research per day), `log/`.
- `config/feeds.json`: RSS sources. `config/holidays.json`: fallback holiday list.

## Hands-off updates

`nifty-forecast-sync.timer` runs four times a day: it pushes the data folder to the `data` branch and fast-forwards the code from `main`. To stop automatic code updates: `touch ~/.nifty_forecast_no_autopull`. Changes to the systemd files are never applied automatically; `sync_status.json` says when `install.sh` needs to be run again.

## Isolation from the EMA bot

- Separate folder, separate credentials file, separate Telegram bot, separate systemd units.
- The agent's services run with `ProtectSystem=strict`, a read-only home, write access to its data folder only, and `InaccessiblePaths` on `~/nifty-bot`, `~/.nifty_bot_env` and `~/.ssh`.
- Low CPU priority and a 300 MB memory cap, so it cannot starve the bot on a small VM.
- Upstox is called with GET requests only. Telegram is called with `sendMessage` only, never `getUpdates`.

## Uninstall

```bash
sudo systemctl disable --now nifty-forecast-morning.timer nifty-forecast-recheck.timer nifty-forecast-score.timer nifty-forecast-sync.timer
sudo rm /etc/systemd/system/nifty-forecast*; sudo systemctl daemon-reload
```
