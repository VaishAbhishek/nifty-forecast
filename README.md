# nifty-forecast

A morning forecast agent for the Nifty 50. It is **advisory, read-only and paper only**: it reads market data and news, sends Telegram messages and writes log files. It cannot place an order, and it does not import, signal, restart or share anything with `nifty_bot.service`.

## What it sends each trading day

| Time (IST) | Message | What it does |
|---|---|---|
| 09:16 | Morning call | One verdict (UP-lean / DOWN-lean / QUIET / NO TRADE), odds of a 300+ point day, how each signal voted, then four context sections: News, Sentiment, Technicals, Sectors. Ends with matched catalysts and the key risk |
| 09:46 | 30-minute re-check | Whether the 09:16 call is STILL VALID / UNCONFIRMED / WEAKENED / INVALIDATED, the first-30-minute range, nearest levels, updated 300+ odds, sector and heavyweight moves, new driver headlines |
| 15:45 | Scorecard | What actually happened, whether the call was right, and the running hit rate of every rule against a coin flip |

Weekends and NSE holidays are skipped (Upstox holiday API first, `config/holidays.json` as fallback).

### The four context sections

- **News: what is driving the market.** Every headline is sorted into driver (a cause: crude, rupee, Fed, RBI, flows, results, geopolitics), market report (only restates where the index is or will open), analyst view, or irrelevant. **Only drivers count toward the tone.** Sources take turns so no feed dominates, and reworded copies of one story are merged.
- **Sentiment.** India VIX, put/call ratio, GIFT Nifty, US overnight, Brent, USD-INR, FII/DII (when a headline carries the figure) and the driver news tone, each marked bullish, bearish or neutral.
- **Technicals.** Trend against the 20/50/200-day averages, RSI, ATR, the nearest levels above and below the open (yesterday's high and low, pivot, R1/R2, S1/S2, 5-day high and low, the strikes with the heaviest call and put open interest), max pain, and the range the options market is pricing.
- **Sectors.** Nine sector indices and nine index heavyweights (`config/sectors.json`): move since the previous close, yesterday's move and the 5-session move.

Sentiment, Technicals and Sectors are context. They are shown and logged but they do not vote.

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
| S8_news | Tone of driver headlines at or beyond 0.40 either way | yes |
| S9_ensemble | **The published verdict.** Needs a net of 2 votes, no opposing gap, and no conflict between news and price | |
| S6_orb | 09:46: first 5-minute close outside the first 15-minute range | no, logged only |
| R1_first30 | 09:46: 300+ odds given the first 30 minutes | no, logged only |

To change a rule, bump `RULE_VERSION` in `forecast/strategies.py`. Old and new versions are then counted separately, and the scorecard shows the current version only. Editing a threshold in place would spoil the test.

Rule history:
- **v1** (11 Nov 2026, 1 session): first version. The news tone counted headlines that merely restated the opening gap.
- **v2** (from 12 Nov 2026): news tone counts driver headlines only; sources take turns; duplicate stories merged. Count restarted.

## Momentum jobs (F&O stocks)

A second set of jobs in `momentum/`, separate from the Nifty forecast above and with no effect on its rules or its forward test. They are **advisory and read-only** in the same way. They give the daily stock report (a scheduled Claude task, not part of this repo) measured numbers to work from, tell you what the open actually looks like, and keep score.

| Time (IST) | Job | What it does |
|---|---|---|
| 08:10 | `data` | For every F&O stock: last session's move in units of its normal range, volume against its 20-day average, 20-day breakouts, futures open-interest change, strength against Nifty, beta, expected gap, and for the busiest names the move the options market is pricing. Also the index regime (trend or chop), GIFT Nifty, FII/DII, sectors, and a table of what past gaps did next. Written to `momentum/latest.json` and `momentum/brief/<date>.md`. No Telegram message |
| 09:07 | `preopen` | Reads the indicative opening prices from the pre-open auction and sends the real gaps, plus each of the day's picks marked valid, partly priced in, mostly priced in or gapping against |
| 09:20 | `check5` | Stocks trading at twice their usual volume for this time of day ("in play"), and whether each pick has reached its confirm or cancel level |
| 09:47 | `check30` | The same after 30 minutes |
| 16:05 | `eod` | Scores every pick from the open (direction, against Nifty, and the confirm/cancel trade in R), follows swing picks for five sessions, updates `momentum/scorecard.md`, and saves futures open interest for the next morning |

The report's picks arrive as `momentum/picks/<date>.json` on the `data` branch. Without that file the jobs still run and send the gap and in-play lists.

### Rules version 3 (from 25 Nov 2026): prepare before the open, decide after it

- **08:10 filings**: BSE corporate announcements since the last close, matched to F&O stocks, saved to `momentum/news/<date>.json` with a `fresh` flag (published after 15:30). The morning report reads this first. If BSE refuses the VM, the report's web search is the fallback.
- **08:40 report = ranked watchlist**: fresh, material news with a direction and what the open must show. No pre-set entry levels for intraday names.
- **09:07–09:09 auction**: buy/sell imbalance of unmatched orders, and auction volume against its 20-day usual (needs 5 sessions of history) -> "In play before the open" in the pre-open message.
- **09:20 engine** (`check5`): each in-play stock (3x usual opening volume, top 10) must pass five gates: in play; first 5 minutes agree with the gap and any news; Nifty not against it; opening range <= 1 ATR and gap <= 1.5 ATR; option spread/IV/OI ok. Ranked fresh news > news > volume, one trade per theme. Saved to `momentum/trades/<date>.json`, sent as **09:20 TRADE CALLS**.
- **Watcher**: entry on a break of the 5-minute range between 09:20 and 10:15, stop at the other side, half at 2R, rest trails VWAP (never below entry), out by 15:00, no new entries after -3R in a day. Morning-report picks with levels also wait for 09:20 now.
- **Size**: lots = Rs 20,000 (env `NF_RISK_PER_TRADE`) divided by the option's stop-loss risk per lot, rounded down; 0 lots means skip.
- **EOD**: engine trades and their R appended to `momentum/trades.jsonl`. Proper re-scoring of all three versions (report ideas, pure in-play breakout, in-play + news) with costs comes next.

### Rules version 2 (from 23 Nov 2026)

- **Swing list** in the 08:10 data file: F&O stocks in the top 30% on volatility-adjusted 6- and 12-month momentum (NSE's momentum-index method), within 15% of the 52-week high, in a tight base (10-day range of 4 ATRs or less) or an orderly pullback to the 20-day average. Each has a trigger, stop and 2R target. Weak-momentum shorts near the 52-week low are listed separately and need futures or puts.
- **Momentum crash gate**: flagged when Nifty is below its 50-day average, 5% or more below its 20-day high, and India VIX is at least 1.3 times its 60-day median.
- **Options for intraday picks** at 09:20: the expiry with at least five sessions left, the strike with delta nearest 0.55, the premium stop and 2R target translated by delta, cost and risk per lot, and warnings for a spread above 2.5%, implied volatility 1.6 times realised or more, and time decay of 4% a day or more. At 09:47 the current premium is shown. At the close the option is scored at the same minutes as the stock trade.
- **In play**: the top 10 stocks at three times their usual opening volume (was every stock at twice).
- **Opening-range test**: stop at the other side of the opening range (the v1 stop sat inside the range, so most signals were cancelled before entry).
- **Swing picks** are scored at 5 and 10 sessions.

### Added 22 Nov 2026

- **Live watch** (`watch`, every minute 09:16-15:16): checks each of the day's picks twice a minute and sends a Telegram alert the moment one confirms (ENTRY, only until 09:50; LATE after that), cancels, hits its stop or target, or its option premium hits the premium stop or target; a 15:00 exit reminder for open intraday picks; and for swing picks, a 15:05 note when price is beyond the trigger (entry still needs the close). Needs `deploy/install.sh` run once more for the new timer.
- **Industries and peers** in the data file: NSE's Nifty 500 list gives each stock's industry (downloaded weekly; if the VM cannot reach NSE, put a copy of `ind_nifty500list.csv` at `config/stock_industries.csv`). Industries are ranked by median 20-session strength of their F&O members. Peers come from correlation of daily returns with the market's move removed (60 sessions), so they need no outside data.
- **Learning from the record**: `scorecard.md` now shows, for every evidence tag, horizon, direction, regime and earnings-surprise bucket, how often picks with it worked and a 90% range. From 100 finished picks a logistic regression gives each feature a weight with the others held fixed.
- **Earnings surprise**: picks may carry `surprise_pct` (actual profit against the analyst poll); the scorecard groups by surprise size.

### Read this before trusting it

- A gap is already in the opening price. The pre-open message tells you how much of a pick's expected move is gone, not that there is money in the gap.
- The gap table and the scorecard are the only numbers here that are measured on outcomes. Everything else describes yesterday.
- The in-play opening-range breakout is logged and scored as a forward test only. It comes from a study of US stocks and has not been shown to work here.
- R results ignore brokerage, taxes and slippage.
- Judge nothing before about 30 scored picks in a group. `scorecard.md` shows how many right calls a coin flip would need.
- To change a threshold, bump `RULES_VERSION` in `momentum/calc.py`; every scored row records the version it was made under.

### Run and monitor

```bash
systemctl list-timers 'nifty-momentum*'
journalctl -u 'nifty-momentum@*' --since today -o cat
sudo systemctl start nifty-momentum@selftest.service          # checks every Upstox call the jobs depend on
cd ~/nifty-forecast && set -a && source ~/.nifty_forecast_env && set +a \
  && NF_DATA_DIR=~/nifty-forecast-data python3 -m momentum.run data --force --dry-run
```

The jobs use the same credentials file and the same Telegram bot as the forecast agent, and the same sandbox. Upstox use is about 300 GET requests before the open and a handful during the day.

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

After a code update that adds or changes timers (the sync job's `sync_status.json` says so), run `~/nifty-forecast/deploy/install.sh` once more.

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
- `config/feeds.json`: RSS sources. `config/sectors.json`: sector and heavyweight instrument keys. `config/holidays.json`: fallback holiday list.

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
sudo systemctl disable --now nifty-momentum-data.timer nifty-momentum-preopen.timer nifty-momentum-check5.timer nifty-momentum-check30.timer nifty-momentum-watch.timer nifty-momentum-eod.timer nifty-momentum-sync.timer
sudo rm /etc/systemd/system/nifty-forecast* /etc/systemd/system/nifty-momentum*; sudo systemctl daemon-reload
```
