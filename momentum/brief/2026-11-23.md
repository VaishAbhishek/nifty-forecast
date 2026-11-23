# F&O momentum data for 2026-11-23

Built 08:10 on the VM from Upstox. 218 stocks, 0 failed. Prices are the last completed session (2026-11-20).
Numbers here are measured. Reasons are not: this file cannot tell why a stock moved.

## Market

- Nifty: close 25800.6, last day +1.12%, 5 days +2.61%. Regime: **trend_up** (10-day efficiency 0.52, against 20/50-day averages: up).
- India VIX: 17.32.
- Momentum crash risk: **normal** (Nifty +0.0% from its 20-day high, above its 50-day average; VIX 1.22 times its 60-day median).
- Expected index gap: +0.33% (GIFT Nifty 25838.0 against the Nifty futures close 25752.0; GIFT's own change +1.40%). An estimate, not the open.
- Overnight: brent -0.87%, nasdaq -3.96%, spx -2.52%, usdinr -0.66%.
- Flows (units as Upstox reports them): FII cash net +10308 (2026-11-20); DII cash net -4860 (2026-11-20); FII index futures 34% long; FII stock futures 58% long.
- Sector indices, last session and 5 sessions: Bank +2.5% / +5.9%, Financials +2.0% / +3.6%, IT +1.3% / -1.9%, Auto +0.7% / +3.1%, Pharma +0.1% / -0.5%, Metal -0.2% / -3.0%, FMCG -0.1% / +3.6%, Energy -0.2% / -0.2%, Realty +1.7% / +1.9%.

## What past gaps did next (all F&O stocks, about one year, 20242 gaps)

Kept going = closed beyond the open in the gap's direction. Filled = traded back to the previous close that day.

| Gap | Count | Kept going | Filled | Average open-to-close in the gap's direction |
|---|---|---|---|---|
| down 0.5-1% | 5054 | 50% | 64% | +0.02% |
| down 1-2% | 2607 | 52% | 41% | +0.17% |
| down 2-4% | 916 | 42% | 29% | -0.33% |
| down 4+% | 191 | 34% | 13% | -0.70% |
| up 0.5-1% | 6973 | 46% | 69% | -0.03% |
| up 1-2% | 3181 | 51% | 45% | +0.08% |
| up 2-4% | 1001 | 53% | 24% | +0.24% |
| up 4+% | 319 | 39% | 8% | -0.45% |

Futures open interest source: end-of-day snapshot of 2026-11-20.

## Swing candidates (rules v2)

Strong 6- and 12-month momentum adjusted for volatility (NSE's momentum-index method), within 15% of the
52-week high, in a tight base or an orderly pullback. Enter only on a close above the trigger; stop below
the base. Shorts (weak momentum near the 52-week low) need futures or puts.

| Stock | Dir | Momentum pct | Setup | Volume drying up | Close | Trigger | Stop | Target 2R | Risk (ATRs) | From 52w high | 5d | Options IV vs realised | Expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ATHERENERG | UP | 100 | tight base | yes | 1935.4 | 2028.1 | 1808.6 | 2467.2 | 3.3 | -4% | -0.5% | 0.49 | 2026-11-23 |
| DIVISLAB | UP | 99 | tight base | no | 11180.5 | 11859.6 | 10669.0 | 14240.9 | 3.3 | -5% | -2.3% | 0.48 | 2026-11-23 |
| ANANDRATHI | UP | 99 | tight base | yes | 2375.8 | 2413.2 | 2344.3 | 2550.9 | 2.2 | -1% | -0.2% | 1.10 | 2026-11-23 |
| SONACOMS | UP | 98 | tight base | yes | 892.5 | 937.1 | 882.5 | 1046.3 | 2.4 | -5% | -2.9% | 0.65 | 2026-11-23 |
| INDHOTEL | UP | 96 | tight base | yes | 912.0 | 915.3 | 865.4 | 1015.1 | 2.2 | -0% | +2.4% | 0.81 | 2026-11-23 |
| NYKAA | UP | 95 | tight base | yes | 364.0 | 369.3 | 346.1 | 415.6 | 2.4 | -1% | -0.3% | 0.96 | 2026-11-23 |
| TVSMOTOR | UP | 94 | tight base | no | 4590.0 | 4647.1 | 4360.0 | 5221.2 | 2.6 | -1% | +2.1% | 0.59 | 2026-11-23 |
| BOSCHLTD | UP | 94 | tight base | no | 49360.0 | 51471.8 | 48370.0 | 57675.5 | 2.4 | -6% | -0.1% | 0.51 | 2026-11-23 |
| AUROPHARMA | UP | 92 | tight base | no | 1799.0 | 1864.1 | 1778.0 | 2036.2 | 2.1 | -3% | -1.3% | 0.61 | 2026-11-23 |
| ETERNAL | UP | 91 | tight base | no | 364.0 | 378.9 | 356.5 | 423.7 | 2.5 | -4% | +0.1% | 0.90 | 2026-11-23 |
| PHOENIXLTD | UP | 90 | tight base | no | 2285.3 | 2309.7 | 2098.2 | 2732.8 | 3.0 | -1% | +1.3% | 1.22 | 2026-11-23 |
| KARURVYSYA | UP | 90 | tight base | no | 377.0 | 399.1 | 364.3 | 468.7 | 2.8 | -5% | -1.2% | 0.95 | 2026-11-23 |
| SWIGGY | DOWN | 2 | tight base | yes | 178.2 | 176.0 | 201.3 | 125.5 | 3.4 | -58% | -4.5% | 0.82 | 2026-11-23 |
| SUZLON | DOWN | 2 | tight base | yes | 37.0 | 35.7 | 39.6 | 27.9 | 3.5 | -39% | -3.4% | 0.73 | 2026-11-23 |
| VMM | DOWN | 3 | tight base | yes | 92.0 | 89.1 | 97.8 | 71.5 | 3.3 | -34% | -4.6% | 0.79 | 2026-11-23 |
| TMPV | DOWN | 3 | pullback | no | 266.4 | 250.5 | 280.4 | 190.9 | 3.1 | -35% | -7.3% | 0.56 | 2026-11-23 |
| MAZDOCK | DOWN | 4 | tight base | yes | 1841.5 | 1812.3 | 1927.3 | 1582.3 | 2.4 | -35% | -2.6% | 0.88 | 2026-11-23 |
| TIINDIA | DOWN | 5 | tight base | no | 2228.3 | 2112.6 | 2349.0 | 1639.8 | 2.8 | -33% | -1.3% | 0.97 | 2026-11-23 |

## Industry strength among F&O stocks (source: NSE Nifty 500 list)

Ranked by median 20-session strength against Nifty. Industries need 3+ F&O members.

| Rank | Industry | Members | Median last day | Median 5d | Median vs Nifty 20d | Share up 5d |
|---|---|---|---|---|---|---|
| 1 | Services | 5 | +0.5% | +0.7% | +7.4% | 80% |
| 2 | Realty | 6 | +2.0% | +2.2% | +7.2% | 83% |
| 3 | Consumer Durables | 10 | +0.6% | +3.2% | +3.2% | 70% |
| 4 | Construction | 3 | -0.1% | +0.8% | +1.2% | 67% |
| 5 | Financial Services | 57 | +0.8% | +1.4% | +1.1% | 65% |
| 6 | Automobile and Auto Components | 16 | -0.1% | +0.5% | +0.9% | 50% |
| 7 | Oil Gas & Consumable Fuels | 9 | -0.3% | +1.8% | +0.8% | 67% |
| 8 | Healthcare | 16 | +0.5% | +0.8% | -0.4% | 81% |
| 9 | Fast Moving Consumer Goods | 14 | +0.3% | +3.1% | -1.7% | 79% |
| 10 | Power | 8 | +0.6% | +1.6% | -2.1% | 75% |
| 11 | Construction Materials | 4 | +1.1% | +4.1% | -2.4% | 100% |
| 12 | Consumer Services | 9 | +0.8% | -0.3% | -3.6% | 44% |
| 13 | Chemicals | 7 | +0.0% | +1.6% | -5.3% | 71% |
| 14 | Telecommunication | 3 | +0.3% | -2.3% | -7.2% | 33% |
| 15 | Metals & Mining | 10 | -0.1% | -3.5% | -8.5% | 10% |
| 16 | Capital Goods | 26 | -0.3% | -3.4% | -11.9% | 12% |
| 17 | Information Technology | 13 | +1.4% | -1.4% | -16.3% | 31% |

## Industry and peers of focus and swing stocks

Peers = F&O stocks whose daily moves (market move removed) tracked this stock most closely over 60 sessions.
When a stock has news, check whether its peers have moved yet.

| Stock | Industry (rank) | Peers (correlation) | Peers' last day |
|---|---|---|---|
| AXISBANK | Financial Services (5) | INDUSINDBK 0.52 | INDUSINDBK +8.6% |
| INDUSINDBK | Financial Services (5) | AXISBANK 0.52, PRESTIGE 0.50, CAMS 0.47, SBICARD 0.46, IDFCFIRSTB 0.46 | AXISBANK +4.7%, PRESTIGE +1.5%, CAMS +1.5%, SBICARD +1.1%, IDFCFIRSTB +1.4% |
| APOLLOHOSP | Healthcare (8) | MAXHEALTH 0.59 | MAXHEALTH +3.9% |
| CUB | Financial Services (5) | BANKINDIA 0.51, INDIANB 0.45 | BANKINDIA +1.7%, INDIANB +0.3% |
| MAXHEALTH | Healthcare (8) | APOLLOHOSP 0.59, FORTIS 0.56 | APOLLOHOSP +5.3%, FORTIS +1.9% |
| UNIONBANK | Financial Services (5) | PNB 0.69, CANBK 0.66, INDIANB 0.64, BANKINDIA 0.58, BANKBARODA 0.52 | PNB +0.3%, CANBK +2.1%, INDIANB +0.3%, BANKINDIA +1.7%, BANKBARODA +0.4% |
| PERSISTENT | Information Technology (17) | COFORGE 0.62, LTM 0.60, MPHASIS 0.54 | COFORGE +2.2%, LTM +2.1%, MPHASIS +2.7% |
| ULTRACEMCO | Construction Materials (11) | SHREECEM 0.61, AMBUJACEM 0.46 | SHREECEM +1.4%, AMBUJACEM +0.8% |
| HDFCBANK | Financial Services (5) | - | - |
| MARUTI | Automobile and Auto Components (6) | TVSMOTOR 0.58, MOTHERSON 0.54, EICHERMOT 0.48, M&M 0.45 | TVSMOTOR -0.2%, MOTHERSON +0.7%, EICHERMOT +0.7%, M&M +1.0% |
| SHREECEM | Construction Materials (11) | ULTRACEMCO 0.61, GMRAIRPORT 0.56, AMBUJACEM 0.54 | ULTRACEMCO +3.0%, GMRAIRPORT +1.0%, AMBUJACEM +0.8% |
| PIIND | Chemicals (13) | CUMMINSIND 0.69, DABUR 0.57, BHARATFORG 0.49, GODFRYPHLP 0.45 | CUMMINSIND -1.0%, DABUR +0.6%, BHARATFORG +1.2%, GODFRYPHLP -0.3% |
| ATHERENERG | Automobile and Auto Components (6) | POLYCAB 0.48, APLAPOLLO 0.48, ABB 0.46 | POLYCAB +0.3%, APLAPOLLO -1.2%, ABB -0.2% |
| DIVISLAB | Healthcare (8) | LAURUSLABS 0.55, NMDC 0.51, MOTILALOFS 0.50, SUNPHARMA 0.48, AUROPHARMA 0.48 | LAURUSLABS -0.5%, NMDC +1.0%, MOTILALOFS -0.4%, SUNPHARMA -0.8%, AUROPHARMA -0.4% |
| ANANDRATHI | Financial Services (5) | - | - |
| SONACOMS | Automobile and Auto Components (6) | NAVINFLUOR 0.48, MOTHERSON 0.47, PGEL 0.46, APLAPOLLO 0.46, LAURUSLABS 0.46 | NAVINFLUOR -1.2%, MOTHERSON +0.7%, PGEL +1.8%, APLAPOLLO -1.2%, LAURUSLABS -0.5% |
| INDHOTEL | Consumer Services (12) | - | - |
| NYKAA | Consumer Services (12) | POLYCAB 0.54, GVT&D 0.50, AUROPHARMA 0.45 | POLYCAB +0.3%, GVT&D -2.6%, AUROPHARMA -0.4% |
| TVSMOTOR | Automobile and Auto Components (6) | MOTHERSON 0.59, MARUTI 0.58, UPL 0.52, IRFC 0.51, SUZLON 0.50 | MOTHERSON +0.7%, MARUTI +3.1%, UPL +0.4%, IRFC -0.6%, SUZLON +0.0% |
| BOSCHLTD | Automobile and Auto Components (6) | MOTHERSON 0.63, HDFCAMC 0.49, TVSMOTOR 0.48, SUZLON 0.48, INDIGO 0.46 | MOTHERSON +0.7%, HDFCAMC +0.3%, TVSMOTOR -0.2%, SUZLON +0.0%, INDIGO +2.1% |
| AUROPHARMA | Healthcare (8) | DIVISLAB 0.48, NYKAA 0.45 | DIVISLAB +0.0%, NYKAA +1.7% |
| ETERNAL | Consumer Services (12) | - | - |
| PHOENIXLTD | Realty (2) | DLF 0.58, OBEROIRLTY 0.55, PRESTIGE 0.50, GODREJPROP 0.50, BANDHANBNK 0.48 | DLF +2.2%, OBEROIRLTY +1.8%, PRESTIGE +1.5%, GODREJPROP +2.6%, BANDHANBNK +0.0% |
| KARURVYSYA | Financial Services (5) | MAHABANK 0.55, CONCOR 0.48 | MAHABANK +1.5%, CONCOR -1.3% |
| SWIGGY | Consumer Services (12) | - | - |
| SUZLON | Capital Goods (16) | INOXWIND 0.68, BHEL 0.59, IRFC 0.58, RVNL 0.57, UPL 0.52 | INOXWIND -2.6%, BHEL -0.3%, IRFC -0.6%, RVNL -2.0%, UPL +0.4% |
| VMM | Consumer Services (12) | - | - |
| TMPV | Automobile and Auto Components (6) | - | - |
| MAZDOCK | Capital Goods (16) | BDL 0.71, RVNL 0.56, WAAREEENER 0.56, AMBUJACEM 0.49, HINDZINC 0.48 | BDL +0.2%, RVNL -2.0%, WAAREEENER +1.1%, AMBUJACEM +0.8%, HINDZINC -1.4% |
| TIINDIA | Automobile and Auto Components (6) | CGPOWER 0.65, ASTRAL 0.57, BHEL 0.56, NBCC 0.53, MOTHERSON 0.52 | CGPOWER -2.6%, ASTRAL -0.1%, BHEL -0.3%, NBCC +0.1%, MOTHERSON +0.7% |

## Focus list: stocks on two or more lists below

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AXISBANK | 1446.0 | +4.7% | +2.0 | 3.5x | 0.95 | +8.6% | +18.8% | 2.3% | +38% long build-up | +0.4% | 2.5% | -0% | up 20d-up |
| INDUSINDBK | 1003.0 | +8.6% | +2.5 | 6.1x | 1.00 | +9.7% | +20.1% | 3.1% | +18% long build-up | +0.4% | 2.9% | -7% | mixed 20d-up |
| APOLLOHOSP | 9200.0 | +5.3% | +2.3 | 2.8x | 0.83 | +7.9% | +19.0% | 2.2% | +24% long build-up | +0.2% | 1.4% | -1% | up 20d-up |
| CUB | 248.8 | +6.2% | +1.8 | 5.4x | 0.89 | +7.1% | +12.1% | 3.2% | -48% short covering | +0.2% | 19.5% | -1% | mixed 20d-up |
| MAXHEALTH | 1081.0 | +3.9% | +1.4 | 2.4x | 0.77 | +14.1% | +32.6% | 2.7% | +5% long build-up | +0.2% | 2.2% | -9% | mixed 20d-up |
| UNIONBANK | 218.8 | +4.2% | +1.8 | 1.6x | 0.98 | +7.8% | +22.3% | 2.3% | +23% long build-up | +0.2% | 3.1% | -0% | up 20d-up |
| PERSISTENT | 6124.0 | +4.2% | +1.7 | 3.5x | 0.76 | +2.0% | +6.9% | 2.4% | -2% | +0.2% | 2.0% | -7% | up |
| ULTRACEMCO | 12939.0 | +3.0% | +1.4 | 2.0x | 1.00 | +6.9% | +17.1% | 2.1% | -18% short covering | +0.4% | 1.9% | -1% | up 20d-up |
| HDFCBANK | 846.0 | +2.9% | +1.2 | 2.0x | 0.88 | +5.2% | +22.1% | 2.4% | -7% short covering | +0.4% | 2.3% | -17% | up 20d-up |
| MARUTI | 14011.0 | +3.1% | +1.1 | 2.7x | 0.93 | +9.0% | +24.8% | 2.7% | +14% long build-up | +0.4% | 2.2% | -19% | up 20d-up |
| SHREECEM | 25475.0 | +1.4% | +0.7 | 4.0x | 0.94 | +3.3% | +12.1% | 2.1% | -16% short covering | +0.3% | 1.9% | -9% | up 20d-up |
| PIIND | 1597.4 | -2.0% | -0.5 | 0.5x | 0.06 | -6.8% | -22.1% | 4.5% | -14% long unwinding | -0.1% | 2.4% | -55% | down 20d-down |

## Biggest up-moves last session (in units of the stock's normal daily range)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INDUSINDBK | 1003.0 | +8.6% | +2.5 | 6.1x | 1.00 | +9.7% | +20.1% | 3.1% | +18% long build-up | +0.4% | 2.9% | -7% | mixed 20d-up |
| APOLLOHOSP | 9200.0 | +5.3% | +2.3 | 2.8x | 0.83 | +7.9% | +19.0% | 2.2% | +24% long build-up | +0.2% | 1.4% | -1% | up 20d-up |
| AXISBANK | 1446.0 | +4.7% | +2.0 | 3.5x | 0.95 | +8.6% | +18.8% | 2.3% | +38% long build-up | +0.4% | 2.5% | -0% | up 20d-up |
| CUB | 248.8 | +6.2% | +1.8 | 5.4x | 0.89 | +7.1% | +12.1% | 3.2% | -48% short covering | +0.2% | 19.5% | -1% | mixed 20d-up |
| UNIONBANK | 218.8 | +4.2% | +1.8 | 1.6x | 0.98 | +7.8% | +22.3% | 2.3% | +23% long build-up | +0.2% | 3.1% | -0% | up 20d-up |
| PERSISTENT | 6124.0 | +4.2% | +1.7 | 3.5x | 0.76 | +2.0% | +6.9% | 2.4% | -2% | +0.2% | 2.0% | -7% | up |
| MAXHEALTH | 1081.0 | +3.9% | +1.4 | 2.4x | 0.77 | +14.1% | +32.6% | 2.7% | +5% long build-up | +0.2% | 2.2% | -9% | mixed 20d-up |
| ULTRACEMCO | 12939.0 | +3.0% | +1.4 | 2.0x | 1.00 | +6.9% | +17.1% | 2.1% | -18% short covering | +0.4% | 1.9% | -1% | up 20d-up |
| HDFCBANK | 846.0 | +2.9% | +1.2 | 2.0x | 0.88 | +5.2% | +22.1% | 2.4% | -7% short covering | +0.4% | 2.3% | -17% | up 20d-up |
| PNBHOUSING | 1191.3 | +3.2% | +1.2 | 1.1x | 0.80 | +6.6% | +9.4% | 2.6% | +7% long build-up | +0.2% | - | -3% | mixed 20d-up |

## Unusual volume last session (against its own 20-day average)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INDUSINDBK | 1003.0 | +8.6% | +2.5 | 6.1x | 1.00 | +9.7% | +20.1% | 3.1% | +18% long build-up | +0.4% | 2.9% | -7% | mixed 20d-up |
| CUB | 248.8 | +6.2% | +1.8 | 5.4x | 0.89 | +7.1% | +12.1% | 3.2% | -48% short covering | +0.2% | 19.5% | -1% | mixed 20d-up |
| TATAELXSI | 3850.0 | +3.4% | +1.1 | 4.2x | 0.66 | +0.4% | +4.0% | 3.0% | -37% short covering | +0.3% | - | -35% | up |
| SHREECEM | 25475.0 | +1.4% | +0.7 | 4.0x | 0.94 | +3.3% | +12.1% | 2.1% | -16% short covering | +0.3% | 1.9% | -9% | up 20d-up |
| COFORGE | 2086.7 | +2.2% | +0.7 | 3.7x | 0.40 | +2.9% | +9.8% | 3.1% | -9% short covering | +0.2% | - | -4% | up |
| APLAPOLLO | 2121.6 | -1.2% | -0.5 | 3.5x | 0.90 | -5.8% | +4.3% | 2.6% | +0% | +0.2% | - | -8% | mixed |
| PRESTIGE | 1680.0 | +1.5% | +0.4 | 3.5x | 0.86 | +1.8% | +20.6% | 3.5% | -5% short covering | +0.4% | - | -6% | up |
| AXISBANK | 1446.0 | +4.7% | +2.0 | 3.5x | 0.95 | +8.6% | +18.8% | 2.3% | +38% long build-up | +0.4% | 2.5% | -0% | up 20d-up |
| PERSISTENT | 6124.0 | +4.2% | +1.7 | 3.5x | 0.76 | +2.0% | +6.9% | 2.4% | -2% | +0.2% | 2.0% | -7% | up |
| APOLLOHOSP | 9200.0 | +5.3% | +2.3 | 2.8x | 0.83 | +7.9% | +19.0% | 2.2% | +24% long build-up | +0.2% | 1.4% | -1% | up 20d-up |
| MARUTI | 14011.0 | +3.1% | +1.1 | 2.7x | 0.93 | +9.0% | +24.8% | 2.7% | +14% long build-up | +0.4% | 2.2% | -19% | up 20d-up |
| LTM | 4166.4 | +2.1% | +0.7 | 2.6x | 0.46 | -2.1% | +0.8% | 3.2% | -11% short covering | +0.3% | - | -35% | mixed |

## Closed above the 20-day high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INDUSINDBK | 1003.0 | +8.6% | +2.5 | 6.1x | 1.00 | +9.7% | +20.1% | 3.1% | +18% long build-up | +0.4% | 2.9% | -7% | mixed 20d-up |
| CUB | 248.8 | +6.2% | +1.8 | 5.4x | 0.89 | +7.1% | +12.1% | 3.2% | -48% short covering | +0.2% | 19.5% | -1% | mixed 20d-up |
| SHREECEM | 25475.0 | +1.4% | +0.7 | 4.0x | 0.94 | +3.3% | +12.1% | 2.1% | -16% short covering | +0.3% | 1.9% | -9% | up 20d-up |
| AXISBANK | 1446.0 | +4.7% | +2.0 | 3.5x | 0.95 | +8.6% | +18.8% | 2.3% | +38% long build-up | +0.4% | 2.5% | -0% | up 20d-up |
| APOLLOHOSP | 9200.0 | +5.3% | +2.3 | 2.8x | 0.83 | +7.9% | +19.0% | 2.2% | +24% long build-up | +0.2% | 1.4% | -1% | up 20d-up |
| MARUTI | 14011.0 | +3.1% | +1.1 | 2.7x | 0.93 | +9.0% | +24.8% | 2.7% | +14% long build-up | +0.4% | 2.2% | -19% | up 20d-up |
| MAXHEALTH | 1081.0 | +3.9% | +1.4 | 2.4x | 0.77 | +14.1% | +32.6% | 2.7% | +5% long build-up | +0.2% | 2.2% | -9% | mixed 20d-up |
| ULTRACEMCO | 12939.0 | +3.0% | +1.4 | 2.0x | 1.00 | +6.9% | +17.1% | 2.1% | -18% short covering | +0.4% | 1.9% | -1% | up 20d-up |
| HDFCBANK | 846.0 | +2.9% | +1.2 | 2.0x | 0.88 | +5.2% | +22.1% | 2.4% | -7% short covering | +0.4% | 2.3% | -17% | up 20d-up |
| BLUESTARCO | 1791.0 | +1.5% | +0.5 | 1.9x | 0.58 | +12.8% | +19.5% | 3.4% | -9% short covering | +0.3% | - | -12% | up 20d-up |

## Closed below the 20-day low

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PIIND | 1597.4 | -2.0% | -0.5 | 0.5x | 0.06 | -6.8% | -22.1% | 4.5% | -14% long unwinding | -0.1% | 2.4% | -55% | down 20d-down |

## Futures: price up with open interest up (long build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HDFCLIFE | 588.6 | +2.0% | +0.7 | 1.7x | 0.94 | -0.6% | +12.4% | 2.7% | +46% long build-up | +0.4% | - | -25% | up |
| BAJAJFINSV | 1892.0 | +0.4% | +0.1 | 1.5x | 0.62 | +1.4% | +14.3% | 2.6% | +43% long build-up | +0.4% | - | -11% | up |
| AXISBANK | 1446.0 | +4.7% | +2.0 | 3.5x | 0.95 | +8.6% | +18.8% | 2.3% | +38% long build-up | +0.4% | 2.5% | -0% | up 20d-up |
| M&M | 3545.0 | +1.0% | +0.4 | 1.2x | 0.72 | +6.4% | +23.9% | 2.9% | +27% long build-up | +0.5% | - | -8% | up 20d-up |
| SBILIFE | 1826.5 | +1.2% | +0.5 | 0.7x | 0.99 | +2.0% | +11.4% | 2.3% | +27% long build-up | +0.3% | - | -14% | up |
| DIVISLAB | 11180.5 | +0.0% | +0.0 | 0.5x | 0.90 | -2.3% | +24.9% | 3.2% | +27% long build-up | +0.1% | 1.9% | -5% | up NR7 |
| NYKAA | 364.0 | +1.7% | +0.6 | 0.7x | 0.86 | -0.3% | +14.0% | 2.7% | +26% long build-up | +0.2% | 2.1% | -1% | up |
| GODREJPROP | 1930.2 | +2.6% | +0.8 | 0.8x | 0.87 | +4.1% | +29.0% | 3.3% | +25% long build-up | +0.5% | - | -13% | up 20d-up |

## Futures: price down with open interest up (short build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CIPLA | 1415.0 | -0.2% | -0.1 | 0.9x | 0.51 | +1.7% | +5.8% | 1.6% | +31% short build-up | +0.1% | - | -8% | up |
| ZYDUSLIFE | 1200.0 | -0.2% | -0.1 | 0.5x | 0.43 | +0.8% | +6.2% | 2.4% | +18% short build-up | +0.1% | - | -5% | mixed NR7 |
| DRREDDY | 1390.2 | -0.8% | -0.5 | 0.4x | 0.36 | +0.7% | +13.1% | 1.6% | +17% short build-up | +0.1% | - | -2% | up NR7 |
| SUNPHARMA | 1884.9 | -0.8% | -0.3 | 0.8x | 0.07 | +0.3% | +7.8% | 2.3% | +14% short build-up | +0.2% | - | -8% | up |
| HINDUNILVR | 2052.5 | -1.1% | -0.5 | 1.0x | 0.52 | +3.0% | +13.1% | 1.9% | +14% short build-up | +0.3% | - | -18% | up |
| ADANIPORTS | 1917.0 | -0.0% | -0.0 | 0.9x | 0.52 | +0.7% | +12.6% | 2.2% | +11% short build-up | +0.2% | - | -3% | up |
| INDUSTOWER | 387.0 | -0.2% | -0.1 | 0.7x | 0.82 | -2.3% | +1.8% | 2.4% | +9% short build-up | +0.2% | - | -20% | up NR7 |
| TVSMOTOR | 4590.0 | -0.2% | -0.1 | 1.3x | 0.42 | +2.1% | +15.3% | 2.4% | +8% short build-up | +0.3% | 1.4% | -1% | up NR7 |

## Strongest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ATHERENERG | 1935.4 | +0.6% | +0.2 | 0.5x | 0.37 | -0.5% | +40.2% | 3.4% | -30% short covering | +0.3% | 2.6% | -4% | up |
| MAXHEALTH | 1081.0 | +3.9% | +1.4 | 2.4x | 0.77 | +14.1% | +32.6% | 2.7% | +5% long build-up | +0.2% | 2.2% | -9% | mixed 20d-up |
| MAHABANK | 99.5 | +1.5% | +0.5 | 1.4x | 0.96 | +8.4% | +32.0% | 2.8% | -13% short covering | +0.3% | - | -0% | up 20d-up |
| NAVINFLUOR | 10077.0 | -1.2% | -0.4 | 1.2x | 0.23 | +0.8% | +31.4% | 3.1% | -64% long unwinding | +0.0% | - | -3% | up |
| IREDA | 131.7 | +1.5% | +0.4 | 2.6x | 0.66 | +11.3% | +31.4% | 4.0% | -15% short covering | +0.4% | - | -14% | up |
| UNOMINDA | 1380.0 | -0.4% | -0.1 | 0.9x | 0.34 | -0.6% | +30.6% | 3.7% | +3% short build-up | +0.5% | - | -2% | up |
| MOTILALOFS | 1205.7 | -0.4% | -0.1 | 0.6x | 0.66 | -1.2% | +30.2% | 4.3% | -14% long unwinding | +0.5% | - | -6% | up NR7 |
| VOLTAS | 1235.0 | -0.2% | -0.0 | 1.2x | 0.19 | +9.0% | +30.0% | 3.7% | +8% short build-up | +0.4% | - | -22% | up |

## Weakest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PIIND | 1597.4 | -2.0% | -0.5 | 0.5x | 0.06 | -6.8% | -22.1% | 4.5% | -14% long unwinding | -0.1% | 2.4% | -55% | down 20d-down |
| KAYNES | 2910.0 | +0.7% | +0.1 | 0.5x | 0.78 | -15.2% | -8.7% | 4.7% | -19% short covering | +0.2% | - | -54% | down |
| PAGEIND | 31020.0 | -0.1% | -0.0 | 1.1x | 0.59 | -1.0% | -8.3% | 3.8% | -19% long unwinding | +0.2% | - | -29% | down |
| ASTRAL | 1252.6 | -0.1% | -0.1 | 0.6x | 1.00 | -0.1% | -7.7% | 3.2% | -20% long unwinding | +0.0% | - | -29% | down |
| TCS | 2376.2 | +1.4% | +0.6 | 0.9x | 0.61 | -1.3% | -6.1% | 2.5% | -10% short covering | +0.2% | - | -29% | mixed |
| INOXWIND | 55.5 | -2.6% | -0.5 | 1.6x | 0.21 | -13.9% | -5.9% | 5.1% | -26% long unwinding | +0.4% | - | -64% | down |
| CUMMINSIND | 4100.0 | -1.0% | -0.2 | 0.5x | 0.90 | -6.2% | -5.6% | 4.5% | -0% | -0.1% | - | -33% | down NR7 |
| HCLTECH | 1344.4 | +0.9% | +0.3 | 1.2x | 0.59 | -2.4% | -5.5% | 2.6% | -0% | +0.2% | - | -24% | mixed |

## Within 2% of the 52-week high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| INDHOTEL | 912.0 | +2.5% | +1.0 | 0.8x | 0.97 | +2.4% | +16.7% | 2.5% | -1% | +0.3% | 1.7% | -0% | up 20d-up |
| UNIONBANK | 218.8 | +4.2% | +1.8 | 1.6x | 0.98 | +7.8% | +22.3% | 2.3% | +23% long build-up | +0.2% | 3.1% | -0% | up 20d-up |
| KOTAKBANK | 515.8 | +2.5% | +1.2 | 0.9x | 0.95 | +5.6% | +19.8% | 2.1% | -6% short covering | +0.2% | - | -0% | up 20d-up |
| MAHABANK | 99.5 | +1.5% | +0.5 | 1.4x | 0.96 | +8.4% | +32.0% | 2.8% | -13% short covering | +0.3% | - | -0% | up 20d-up |
| FEDERALBNK | 373.5 | +2.5% | +1.1 | 1.4x | 0.94 | +3.5% | +9.6% | 2.3% | +3% | +0.1% | - | -0% | up 20d-up |
| AXISBANK | 1446.0 | +4.7% | +2.0 | 3.5x | 0.95 | +8.6% | +18.8% | 2.3% | +38% long build-up | +0.4% | 2.5% | -0% | up 20d-up |
| ICICIBANK | 1640.0 | +1.9% | +0.9 | 1.1x | 0.89 | +3.6% | +17.6% | 2.2% | +19% long build-up | +0.3% | - | -0% | up 20d-up |
| GAIL | 191.4 | -0.3% | -0.2 | 0.6x | 1.00 | +1.8% | +16.8% | 1.9% | -8% long unwinding | +0.2% | - | -0% | up |

## Reading the columns

- In ATRs: last day's move divided by the stock's average true range. Above 1.5 is an unusually large day.
- Close in range: 1.00 closed at the day's high, 0.00 at the low.
- Est. gap: the stock's beta times the expected index gap. It ignores stock news, which usually matters more.
- Options: 1-day move: the daily move implied by the nearest at-the-money straddle. Shown for focus and swing stocks.
- Options IV vs realised: at-the-money implied volatility divided by the stock's 20-day realised volatility.
  Above about 1.6 the options are expensive (often before results) and buying them needs a bigger move.
- Momentum pct: rank 0-100 across F&O stocks on volatility-adjusted 6- and 12-month returns.
- The full per-stock data is in momentum/latest.json.
