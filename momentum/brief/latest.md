# F&O momentum data for 2026-11-25

Built 08:10 on the VM from Upstox. 218 stocks, 0 failed. Prices are the last completed session (2026-11-23).
Numbers here are measured. Reasons are not: this file cannot tell why a stock moved.

Notes: BSE filings not read (HTTP 403 for https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w: <); the report's web search is the fallback

## Market

- Nifty: close 25349.7, last day -1.75%, 5 days +0.23%. Regime: **chop** (10-day efficiency 0.19, against 20/50-day averages: up).
- India VIX: 17.70.
- Momentum crash risk: **normal** (Nifty -1.8% from its 20-day high, above its 50-day average; VIX 1.23 times its 60-day median).
- Expected index gap: +1.08% (GIFT Nifty 25806.0 against the Nifty futures close 25530.0; GIFT's own change +1.28%). An estimate, not the open.
- Overnight: brent +1.83%, nasdaq -1.97%, spx -0.89%, usdinr +0.01%.
- Flows (units as Upstox reports them): FII cash net +5673 (2026-11-23); DII cash net -2760 (2026-11-23); FII index futures 20% long; FII stock futures 57% long.
- Sector indices, last session and 5 sessions: Bank -3.2% / +1.6%, Financials -2.5% / +0.5%, IT +1.7% / -0.3%, Auto -1.0% / +3.3%, Pharma -0.3% / +0.7%, Metal -3.7% / -5.1%, FMCG -0.5% / +1.3%, Energy -1.8% / -1.7%, Realty +0.3% / +3.6%.

## What past gaps did next (all F&O stocks, about one year, 20344 gaps)

Kept going = closed beyond the open in the gap's direction. Filled = traded back to the previous close that day.

| Gap | Count | Kept going | Filled | Average open-to-close in the gap's direction |
|---|---|---|---|---|
| down 0.5-1% | 5034 | 50% | 64% | +0.02% |
| down 1-2% | 2601 | 52% | 41% | +0.16% |
| down 2-4% | 923 | 43% | 29% | -0.31% |
| down 4+% | 192 | 34% | 14% | -0.65% |
| up 0.5-1% | 7043 | 46% | 70% | -0.05% |
| up 1-2% | 3222 | 51% | 46% | +0.07% |
| up 2-4% | 1009 | 53% | 24% | +0.22% |
| up 4+% | 320 | 39% | 9% | -0.46% |

Futures open interest source: end-of-day snapshot of 2026-11-23.

## Swing candidates (rules v3)

Strong 6- and 12-month momentum adjusted for volatility (NSE's momentum-index method), within 15% of the
52-week high, in a tight base or an orderly pullback. Enter only on a close above the trigger; stop below
the base. Shorts (weak momentum near the 52-week low) need futures or puts.

| Stock | Dir | Momentum pct | Setup | Volume drying up | Close | Trigger | Stop | Target 2R | Risk (ATRs) | From 52w high | 5d | Options IV vs realised | Expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ATHERENERG | UP | 100 | tight base | yes | 1979.2 | 2028.1 | 1808.6 | 2467.1 | 3.3 | -2% | +2.0% | 1.12 | 2026-12-29 |
| DIVISLAB | UP | 99 | tight base | no | 11203.0 | 11859.6 | 10954.0 | 13670.8 | 2.5 | -5% | +1.1% | 0.79 | 2026-12-29 |
| ANANDRATHI | UP | 99 | tight base | yes | 2355.9 | 2413.3 | 2344.3 | 2551.2 | 2.1 | -2% | -1.3% | 1.87 | 2026-12-29 |
| SONACOMS | UP | 98 | tight base | yes | 886.0 | 937.1 | 879.9 | 1051.8 | 2.5 | -5% | -1.4% | 0.76 | 2026-12-29 |
| ACUTAAS | UP | 98 | tight base | yes | 3875.0 | 4145.0 | 3720.2 | 4994.6 | 2.8 | -6% | -1.8% | - | - |
| INDHOTEL | UP | 96 | tight base | yes | 906.0 | 920.2 | 865.4 | 1029.7 | 2.4 | -1% | +2.3% | 1.04 | 2026-12-29 |
| AUROPHARMA | UP | 95 | tight base | no | 1796.5 | 1864.0 | 1778.0 | 2036.1 | 2.1 | -3% | +0.1% | 1.02 | 2026-12-29 |
| NYKAA | UP | 94 | tight base | yes | 357.0 | 369.3 | 346.1 | 415.7 | 2.3 | -3% | -1.1% | 1.17 | 2026-12-29 |
| TVSMOTOR | UP | 93 | tight base | no | 4528.2 | 4647.1 | 4360.0 | 5221.4 | 2.6 | -2% | +1.7% | 0.86 | 2026-12-29 |
| KARURVYSYA | UP | 93 | tight base | no | 384.1 | 399.1 | 364.3 | 468.9 | 2.7 | -3% | -1.6% | 1.05 | 2026-12-29 |
| BOSCHLTD | UP | 92 | tight base | yes | 48800.0 | 51161.7 | 48370.0 | 56745.1 | 2.3 | -7% | +0.0% | 0.79 | 2026-12-29 |
| ETERNAL | UP | 91 | tight base | no | 362.1 | 378.9 | 356.5 | 423.7 | 2.5 | -4% | -2.4% | 1.06 | 2026-12-29 |
| SUZLON | DOWN | 2 | tight base | yes | 35.9 | 35.7 | 39.6 | 27.9 | 3.4 | -41% | -4.2% | 0.94 | 2026-12-29 |
| SWIGGY | DOWN | 2 | tight base | yes | 177.0 | 175.7 | 201.3 | 124.5 | 3.4 | -58% | -7.2% | 0.98 | 2026-12-29 |
| MAZDOCK | DOWN | 3 | tight base | yes | 1801.0 | 1796.0 | 1927.3 | 1533.4 | 2.9 | -37% | -3.8% | 0.95 | 2026-12-29 |
| VMM | DOWN | 6 | tight base | yes | 94.5 | 89.0 | 97.8 | 71.5 | 3.3 | -32% | -0.4% | 0.89 | 2026-12-29 |
| TIINDIA | DOWN | 6 | tight base | no | 2210.0 | 2112.4 | 2349.0 | 1639.3 | 2.8 | -34% | -1.2% | 1.02 | 2026-12-29 |
| BDL | DOWN | 7 | tight base | yes | 1020.0 | 1001.3 | 1132.7 | 738.6 | 3.4 | -36% | -1.3% | 0.93 | 2026-12-29 |

## Industry strength among F&O stocks (source: NSE Nifty 500 list)

Ranked by median 20-session strength against Nifty. Industries need 3+ F&O members.

| Rank | Industry | Members | Median last day | Median 5d | Median vs Nifty 20d | Share up 5d |
|---|---|---|---|---|---|---|
| 1 | Realty | 6 | +0.2% | +3.9% | +9.1% | 100% |
| 2 | Consumer Durables | 10 | -0.3% | +3.4% | +6.5% | 80% |
| 3 | Services | 5 | -1.2% | +0.5% | +2.4% | 60% |
| 4 | Financial Services | 55 | -1.4% | +0.2% | +2.2% | 56% |
| 5 | Automobile and Auto Components | 16 | -1.0% | +1.7% | +1.9% | 75% |
| 6 | Construction | 3 | -2.6% | -1.0% | -0.0% | 0% |
| 7 | Fast Moving Consumer Goods | 14 | -0.4% | +1.5% | -0.4% | 79% |
| 8 | Oil Gas & Consumable Fuels | 9 | -2.2% | -0.5% | -1.1% | 44% |
| 9 | Healthcare | 17 | -0.1% | +0.4% | -1.3% | 65% |
| 10 | Power | 8 | -1.9% | -0.3% | -2.1% | 50% |
| 11 | Consumer Services | 9 | -0.7% | -1.1% | -3.3% | 33% |
| 12 | Chemicals | 7 | -1.6% | +0.2% | -3.5% | 57% |
| 13 | Construction Materials | 4 | -1.6% | +1.9% | -4.7% | 75% |
| 14 | Metals & Mining | 10 | -1.4% | -3.2% | -8.8% | 10% |
| 15 | Telecommunication | 3 | -1.7% | -4.0% | -11.7% | 0% |
| 16 | Information Technology | 13 | +1.5% | +0.4% | -12.4% | 62% |
| 17 | Capital Goods | 27 | -1.6% | -3.4% | -13.9% | 7% |

## Industry and peers of focus and swing stocks

Peers = F&O stocks whose daily moves (market move removed) tracked this stock most closely over 60 sessions.
When a stock has news, check whether its peers have moved yet.

| Stock | Industry (rank) | Peers (correlation) | Peers' last day |
|---|---|---|---|
| APLAPOLLO | Capital Goods (17) | TATASTEEL 0.53 | TATASTEEL -8.4% |
| TATASTEEL | Metals & Mining (14) | APLAPOLLO 0.53 | APLAPOLLO -21.3% |
| PERSISTENT | Information Technology (16) | COFORGE 0.64, LTM 0.62, MPHASIS 0.55, HCLTECH 0.45 | COFORGE +2.7%, LTM +1.2%, MPHASIS +2.0%, HCLTECH +1.5% |
| EICHERMOT | Automobile and Auto Components (5) | HEROMOTOCO 0.53, MARUTI 0.51, TVSMOTOR 0.48, BAJAJ-AUTO 0.47 | HEROMOTOCO -0.0%, MARUTI -0.0%, TVSMOTOR -1.4%, BAJAJ-AUTO -1.1% |
| FEDERALBNK | Financial Services (4) | PNB 0.49, UNIONBANK 0.45 | PNB -3.6%, UNIONBANK -4.9% |
| POLICYBZR | Financial Services (4) | MFSL 0.58, LTF 0.50 | MFSL -0.2%, LTF +0.7% |
| TCS | Information Technology (16) | WIPRO 0.76, TECHM 0.76, HCLTECH 0.68, INFY 0.66, MPHASIS 0.60 | WIPRO +0.9%, TECHM +1.8%, HCLTECH +1.5%, INFY +0.5%, MPHASIS +2.0% |
| VMM | Consumer Services (11) | DIXON 0.46 | DIXON +2.1% |
| COFORGE | Information Technology (16) | PERSISTENT 0.64, MPHASIS 0.55, LTM 0.45 | PERSISTENT +2.6%, MPHASIS +2.0%, LTM +1.2% |
| OIL | Oil Gas & Consumable Fuels (8) | ONGC 0.60 | ONGC -0.3% |
| PAGEIND | Textiles (-) | ONGC 0.45 | ONGC -0.3% |
| INOXWIND | Capital Goods (17) | SUZLON 0.68, RVNL 0.62, JIOFIN 0.60, NBCC 0.58, COCHINSHIP 0.57 | SUZLON -3.0%, RVNL -3.1%, JIOFIN -2.3%, NBCC -2.5%, COCHINSHIP -3.1% |
| DLF | Realty (1) | OBEROIRLTY 0.68, PRESTIGE 0.62, GODREJPROP 0.59, PHOENIXLTD 0.59, LODHA 0.55 | OBEROIRLTY +0.9%, PRESTIGE +0.4%, GODREJPROP -0.4%, PHOENIXLTD -0.4%, LODHA +0.0% |
| PIIND | Chemicals (12) | CUMMINSIND 0.69, DABUR 0.54, BHARATFORG 0.49, GODFRYPHLP 0.46, NTPC 0.45 | CUMMINSIND -1.1%, DABUR +1.5%, BHARATFORG -1.6%, GODFRYPHLP -2.1%, NTPC -1.9% |
| APOLLOHOSP | Healthcare (9) | MAXHEALTH 0.60 | MAXHEALTH +0.8% |
| ATHERENERG | Automobile and Auto Components (5) | POLYCAB 0.48, ABB 0.46 | POLYCAB -1.9%, ABB -0.9% |
| DIVISLAB | Healthcare (9) | LAURUSLABS 0.55, SUNPHARMA 0.51, AUROPHARMA 0.48, NMDC 0.48, MOTILALOFS 0.47 | LAURUSLABS +3.3%, SUNPHARMA -1.3%, AUROPHARMA -0.1%, NMDC -2.2%, MOTILALOFS +2.4% |
| ANANDRATHI | Financial Services (4) | - | - |
| SONACOMS | Automobile and Auto Components (5) | NAVINFLUOR 0.51, ACUTAAS 0.48, MOTHERSON 0.47, PGEL 0.46, UNOMINDA 0.46 | NAVINFLUOR +0.8%, ACUTAAS +1.1%, MOTHERSON -0.5%, PGEL -0.3%, UNOMINDA -1.7% |
| ACUTAAS | Healthcare (9) | SONACOMS 0.48 | SONACOMS -0.7% |
| INDHOTEL | Consumer Services (11) | - | - |
| AUROPHARMA | Healthcare (9) | DIVISLAB 0.48 | DIVISLAB +0.2% |
| NYKAA | Consumer Services (11) | POLYCAB 0.55, GVT&D 0.49, PREMIERENE 0.47 | POLYCAB -1.9%, GVT&D -0.9%, PREMIERENE -3.0% |
| TVSMOTOR | Automobile and Auto Components (5) | MOTHERSON 0.59, MARUTI 0.58, UPL 0.52, IRFC 0.50, SUZLON 0.50 | MOTHERSON -0.5%, MARUTI -0.0%, UPL -2.5%, IRFC -3.5%, SUZLON -3.0% |
| KARURVYSYA | Financial Services (4) | MAHABANK 0.51, CONCOR 0.45 | MAHABANK -1.9%, CONCOR -2.5% |
| BOSCHLTD | Automobile and Auto Components (5) | MOTHERSON 0.63, TVSMOTOR 0.48, HDFCAMC 0.48, SUZLON 0.47, BAJAJ-AUTO 0.46 | MOTHERSON -0.5%, TVSMOTOR -1.4%, HDFCAMC -0.6%, SUZLON -3.0%, BAJAJ-AUTO -1.1% |
| ETERNAL | Consumer Services (11) | - | - |
| SUZLON | Capital Goods (17) | INOXWIND 0.68, BHEL 0.59, IRFC 0.58, RVNL 0.56, CGPOWER 0.53 | INOXWIND -3.2%, BHEL -4.1%, IRFC -3.5%, RVNL -3.1%, CGPOWER -0.2% |
| SWIGGY | Consumer Services (11) | MOTILALOFS 0.45 | MOTILALOFS +2.4% |
| MAZDOCK | Capital Goods (17) | BDL 0.71, WAAREEENER 0.56, RVNL 0.55, RECLTD 0.48, AMBUJACEM 0.47 | BDL -1.4%, WAAREEENER -2.9%, RVNL -3.1%, RECLTD -1.7%, AMBUJACEM -2.0% |
| TIINDIA | Automobile and Auto Components (5) | CGPOWER 0.65, ASTRAL 0.56, BHEL 0.53, NBCC 0.53, MOTHERSON 0.52 | CGPOWER -0.2%, ASTRAL -2.2%, BHEL -4.1%, NBCC -2.5%, MOTHERSON -0.5% |
| BDL | Capital Goods (17) | MAZDOCK 0.71, RVNL 0.68, HAL 0.59, LICI 0.56, IRFC 0.54 | MAZDOCK -2.2%, RVNL -3.1%, HAL -0.6%, LICI -0.8%, IRFC -3.5% |

## Focus list: stocks on two or more lists below

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1670.0 | -21.3% | -5.3 | 29.1x | 0.06 | -25.8% | -19.6% | 5.1% | -33% long unwinding | +1.5% | 8.2% | -28% | mixed 20d-down |
| TATASTEEL | 163.0 | -8.4% | -2.5 | 7.1x | 0.19 | -10.6% | -4.1% | 3.8% | -18% long unwinding | +1.2% | 2.2% | -27% | down 20d-down |
| PERSISTENT | 6282.5 | +2.6% | +1.0 | 2.3x | 0.72 | +5.1% | +7.4% | 2.5% | -31% short covering | +0.5% | 1.9% | -5% | up 20d-up |
| EICHERMOT | 8172.5 | +0.7% | +0.3 | 1.4x | 0.31 | +7.5% | +15.1% | 2.7% | +5% long build-up | +1.0% | 1.6% | -1% | up 20d-up |
| FEDERALBNK | 359.8 | -3.7% | -1.5 | 2.5x | 0.01 | -0.6% | +4.5% | 2.5% | -45% long unwinding | +0.4% | 1.7% | -4% | up |
| POLICYBZR | 1089.1 | +6.5% | +1.3 | 3.1x | 0.72 | +0.7% | +6.5% | 4.5% | -13% short covering | +1.7% | 3.5% | -45% | mixed |
| TCS | 2460.0 | +3.5% | +1.3 | 2.3x | 0.58 | +2.3% | -3.0% | 2.6% | -26% short covering | +0.5% | 1.9% | -27% | up |
| VMM | 94.5 | +2.7% | +0.9 | 2.2x | 0.70 | -0.4% | +6.5% | 2.9% | -66% short covering | +1.0% | 2.0% | -32% | mixed |
| COFORGE | 2142.3 | +2.7% | +0.9 | 1.6x | 0.75 | +6.6% | +7.5% | 3.0% | -11% short covering | +0.7% | 2.1% | -2% | up |
| OIL | 422.5 | -2.2% | -0.9 | 1.3x | 0.12 | -4.3% | -7.1% | 2.6% | -12% long unwinding | +0.1% | 1.7% | -20% | down 20d-down |
| PAGEIND | 30100.0 | -3.0% | -0.8 | 1.7x | 0.20 | -4.3% | -11.2% | 4.0% | -53% long unwinding | +0.7% | 1.9% | -31% | down 20d-down |
| INOXWIND | 53.7 | -3.2% | -0.6 | 1.1x | 0.05 | -9.8% | -8.1% | 5.5% | -6% long unwinding | +1.4% | 3.2% | -63% | down 20d-down |
| DLF | 794.1 | +1.2% | +0.5 | 1.1x | 0.83 | +5.2% | +19.9% | 2.4% | -17% short covering | +1.1% | 1.7% | -0% | up 20d-up |
| PIIND | 1571.0 | -1.6% | -0.4 | 0.7x | 0.02 | -6.5% | -22.2% | 4.6% | -33% long unwinding | -0.3% | 2.2% | -56% | down 20d-down |
| APOLLOHOSP | 9257.0 | +0.6% | +0.3 | 1.4x | 0.10 | +5.5% | +18.0% | 2.2% | +11% long build-up | +0.7% | 1.7% | -2% | up |

## Biggest up-moves last session (in units of the stock's normal daily range)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| POLICYBZR | 1089.1 | +6.5% | +1.3 | 3.1x | 0.72 | +0.7% | +6.5% | 4.5% | -13% short covering | +1.7% | 3.5% | -45% | mixed |
| TCS | 2460.0 | +3.5% | +1.3 | 2.3x | 0.58 | +2.3% | -3.0% | 2.6% | -26% short covering | +0.5% | 1.9% | -27% | up |
| PERSISTENT | 6282.5 | +2.6% | +1.0 | 2.3x | 0.72 | +5.1% | +7.4% | 2.5% | -31% short covering | +0.5% | 1.9% | -5% | up 20d-up |
| LAURUSLABS | 2370.7 | +3.3% | +1.0 | 0.6x | 0.88 | +6.8% | +15.1% | 3.4% | -40% short covering | +0.1% | - | -5% | up |
| VMM | 94.5 | +2.7% | +0.9 | 2.2x | 0.70 | -0.4% | +6.5% | 2.9% | -66% short covering | +1.0% | 2.0% | -32% | mixed |
| COFORGE | 2142.3 | +2.7% | +0.9 | 1.6x | 0.75 | +6.6% | +7.5% | 3.0% | -11% short covering | +0.7% | 2.1% | -2% | up |
| TORNTPHARM | 4763.7 | +1.6% | +0.8 | 1.8x | 0.39 | +1.6% | +4.7% | 1.9% | -41% short covering | +0.4% | - | -9% | mixed |
| SHRIRAMFIN | 995.9 | +2.5% | +0.8 | 1.6x | 0.35 | +1.8% | +20.7% | 2.9% | -1% | +1.5% | - | -14% | mixed |

## Biggest down-moves last session

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1670.0 | -21.3% | -5.3 | 29.1x | 0.06 | -25.8% | -19.6% | 5.1% | -33% long unwinding | +1.5% | 8.2% | -28% | mixed 20d-down |
| TATASTEEL | 163.0 | -8.4% | -2.5 | 7.1x | 0.19 | -10.6% | -4.1% | 3.8% | -18% long unwinding | +1.2% | 2.2% | -27% | down 20d-down |
| UNIONBANK | 208.2 | -4.9% | -1.9 | 1.3x | 0.04 | +1.3% | +14.9% | 2.7% | -22% long unwinding | +0.7% | - | -5% | up |
| AXISBANK | 1388.6 | -4.0% | -1.6 | 1.6x | 0.00 | +3.4% | +13.8% | 2.6% | -4% long unwinding | +1.4% | - | -5% | up |
| GAIL | 185.6 | -3.0% | -1.6 | 0.4x | 0.00 | -0.8% | +10.3% | 2.0% | -37% long unwinding | +0.7% | - | -3% | up |
| DMART | 3405.4 | -2.4% | -1.6 | 0.7x | 0.05 | -1.5% | +8.1% | 1.6% | -18% long unwinding | +0.5% | - | -27% | mixed |
| BANKBARODA | 275.6 | -4.0% | -1.5 | 1.1x | 0.07 | +2.0% | +18.8% | 2.7% | -15% long unwinding | +1.0% | - | -15% | up |
| FEDERALBNK | 359.8 | -3.7% | -1.5 | 2.5x | 0.01 | -0.6% | +4.5% | 2.5% | -45% long unwinding | +0.4% | 1.7% | -4% | up |
| ICICIBANK | 1585.5 | -3.3% | -1.5 | 1.4x | 0.00 | +0.0% | +13.0% | 2.3% | -7% long unwinding | +1.2% | - | -4% | up |
| IOC | 145.0 | -3.6% | -1.4 | 1.0x | 0.00 | +0.7% | +10.8% | 2.6% | -19% long unwinding | +1.2% | - | -23% | up |

## Unusual volume last session (against its own 20-day average)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1670.0 | -21.3% | -5.3 | 29.1x | 0.06 | -25.8% | -19.6% | 5.1% | -33% long unwinding | +1.5% | 8.2% | -28% | mixed 20d-down |
| TATASTEEL | 163.0 | -8.4% | -2.5 | 7.1x | 0.19 | -10.6% | -4.1% | 3.8% | -18% long unwinding | +1.2% | 2.2% | -27% | down 20d-down |
| DABUR | 399.0 | +1.5% | +0.7 | 3.8x | 0.56 | +4.5% | +11.1% | 2.3% | -29% short covering | +0.6% | - | -25% | mixed |
| PRESTIGE | 1687.0 | +0.4% | +0.1 | 3.5x | 0.72 | +2.9% | +20.8% | 3.3% | -28% short covering | +1.2% | - | -4% | up |
| POLICYBZR | 1089.1 | +6.5% | +1.3 | 3.1x | 0.72 | +0.7% | +6.5% | 4.5% | -13% short covering | +1.7% | 3.5% | -45% | mixed |
| FEDERALBNK | 359.8 | -3.7% | -1.5 | 2.5x | 0.01 | -0.6% | +4.5% | 2.5% | -45% long unwinding | +0.4% | 1.7% | -4% | up |
| TCS | 2460.0 | +3.5% | +1.3 | 2.3x | 0.58 | +2.3% | -3.0% | 2.6% | -26% short covering | +0.5% | 1.9% | -27% | up |
| PERSISTENT | 6282.5 | +2.6% | +1.0 | 2.3x | 0.72 | +5.1% | +7.4% | 2.5% | -31% short covering | +0.5% | 1.9% | -5% | up 20d-up |
| VMM | 94.5 | +2.7% | +0.9 | 2.2x | 0.70 | -0.4% | +6.5% | 2.9% | -66% short covering | +1.0% | 2.0% | -32% | mixed |
| ADANIENSOL | 1470.0 | -1.5% | -0.5 | 2.2x | 0.03 | +1.2% | +16.9% | 3.0% | -27% long unwinding | +1.1% | - | -18% | up |
| MANAPPURAM | 271.0 | -3.4% | -0.8 | 2.1x | 0.12 | -10.8% | -5.7% | 4.5% | -47% long unwinding | +1.5% | - | -29% | down |
| ADANIPOWER | 207.9 | -1.9% | -0.8 | 2.1x | 0.10 | +1.3% | +11.4% | 2.4% | -41% long unwinding | +1.2% | - | -18% | up |

## Closed above the 20-day high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PERSISTENT | 6282.5 | +2.6% | +1.0 | 2.3x | 0.72 | +5.1% | +7.4% | 2.5% | -31% short covering | +0.5% | 1.9% | -5% | up 20d-up |
| ICICIGI | 1742.6 | +0.4% | +0.2 | 1.9x | 0.39 | +1.9% | +10.3% | 2.2% | -7% short covering | +0.5% | - | -15% | up 20d-up |
| EICHERMOT | 8172.5 | +0.7% | +0.3 | 1.4x | 0.31 | +7.5% | +15.1% | 2.7% | +5% long build-up | +1.0% | 1.6% | -1% | up 20d-up |
| DIXON | 13390.0 | +2.1% | +0.8 | 1.4x | 0.65 | +3.9% | +20.0% | 2.5% | -33% short covering | +1.0% | - | -15% | mixed 20d-up |
| OBEROIRLTY | 1860.0 | +0.9% | +0.3 | 1.3x | 0.85 | +4.9% | +17.6% | 2.8% | -26% short covering | +1.0% | - | -6% | up 20d-up NR7 |
| DLF | 794.1 | +1.2% | +0.5 | 1.1x | 0.83 | +5.2% | +19.9% | 2.4% | -17% short covering | +1.1% | 1.7% | -0% | up 20d-up |

## Closed below the 20-day low

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1670.0 | -21.3% | -5.3 | 29.1x | 0.06 | -25.8% | -19.6% | 5.1% | -33% long unwinding | +1.5% | 8.2% | -28% | mixed 20d-down |
| TATASTEEL | 163.0 | -8.4% | -2.5 | 7.1x | 0.19 | -10.6% | -4.1% | 3.8% | -18% long unwinding | +1.2% | 2.2% | -27% | down 20d-down |
| PAGEIND | 30100.0 | -3.0% | -0.8 | 1.7x | 0.20 | -4.3% | -11.2% | 4.0% | -53% long unwinding | +0.7% | 1.9% | -31% | down 20d-down |
| OIL | 422.5 | -2.2% | -0.9 | 1.3x | 0.12 | -4.3% | -7.1% | 2.6% | -12% long unwinding | +0.1% | 1.7% | -20% | down 20d-down |
| COCHINSHIP | 1090.0 | -3.1% | -0.9 | 1.3x | 0.06 | -5.9% | -3.9% | 3.5% | -60% long unwinding | +1.1% | - | -41% | down 20d-down |
| INOXWIND | 53.7 | -3.2% | -0.6 | 1.1x | 0.05 | -9.8% | -8.1% | 5.5% | -6% long unwinding | +1.4% | 3.2% | -63% | down 20d-down |
| TATAPOWER | 328.0 | -3.4% | -1.3 | 1.0x | 0.04 | -5.1% | -3.1% | 2.8% | -43% long unwinding | +0.6% | - | -29% | down 20d-down |
| PREMIERENE | 809.9 | -3.0% | -0.8 | 1.0x | 0.10 | -1.5% | -3.7% | 3.7% | -63% long unwinding | +0.4% | - | -29% | down 20d-down |
| PIIND | 1571.0 | -1.6% | -0.4 | 0.7x | 0.02 | -6.5% | -22.2% | 4.6% | -33% long unwinding | -0.3% | 2.2% | -56% | down 20d-down |

## Futures: price up with open interest up (long build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| POWERINDIA | 30240.0 | +0.3% | +0.1 | 0.6x | 0.86 | -2.1% | +12.6% | 4.4% | +20% long build-up | -0.4% | - | -22% | mixed |
| APOLLOHOSP | 9257.0 | +0.6% | +0.3 | 1.4x | 0.10 | +5.5% | +18.0% | 2.2% | +11% long build-up | +0.7% | 1.7% | -2% | up |
| EICHERMOT | 8172.5 | +0.7% | +0.3 | 1.4x | 0.31 | +7.5% | +15.1% | 2.7% | +5% long build-up | +1.0% | 1.6% | -1% | up 20d-up |

## Futures: price down with open interest up (short build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HDFCLIFE | 575.0 | -2.3% | -0.8 | 0.8x | 0.03 | -4.9% | +10.8% | 2.9% | +27% short build-up | +1.3% | - | -27% | up |
| SUNPHARMA | 1860.0 | -1.3% | -0.6 | 0.7x | 0.17 | -0.4% | +6.9% | 2.4% | +26% short build-up | +0.6% | - | -9% | up |
| GODREJCP | 912.3 | -0.8% | -0.3 | 0.3x | 0.05 | +2.2% | +9.5% | 2.5% | +18% short build-up | +0.6% | - | -28% | up |
| MUTHOOTFIN | 2543.3 | -0.3% | -0.1 | 1.2x | 0.15 | -8.4% | +6.2% | 4.0% | +18% short build-up | +1.4% | - | -39% | down |
| MANKIND | 2615.1 | -1.9% | -0.8 | 0.2x | 0.19 | -0.4% | +13.1% | 2.3% | +15% short build-up | +0.2% | - | -3% | up |
| ASIANPAINT | 2580.4 | -1.1% | -0.4 | 0.5x | 0.26 | +0.3% | +11.1% | 2.5% | +12% short build-up | +1.1% | - | -14% | up |
| SBILIFE | 1804.9 | -1.2% | -0.5 | 0.6x | 0.22 | -1.2% | +9.8% | 2.4% | +12% short build-up | +0.9% | - | -15% | up |
| ABCAPITAL | 415.8 | -1.7% | -0.6 | 0.7x | 0.06 | +1.8% | +17.8% | 2.7% | +6% short build-up | +1.3% | - | -3% | up |

## Strongest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NAVINFLUOR | 10154.0 | +0.8% | +0.2 | 0.7x | 0.49 | +2.7% | +32.5% | 3.1% | -9% short covering | +0.2% | - | -2% | up |
| MOTILALOFS | 1235.0 | +2.4% | +0.6 | 1.0x | 0.80 | +1.5% | +32.3% | 4.1% | -39% short covering | +1.6% | - | -3% | up |
| MAXHEALTH | 1089.5 | +0.8% | +0.3 | 0.9x | 0.46 | +7.9% | +30.5% | 2.7% | -16% short covering | +0.7% | - | -8% | up |
| KALYANKJIL | 652.9 | +2.2% | +0.4 | 1.3x | 0.42 | -7.8% | +29.3% | 5.8% | -10% short covering | +1.0% | - | -10% | up |
| VOLTAS | 1218.5 | -1.3% | -0.3 | 0.5x | 0.18 | +5.7% | +28.6% | 3.9% | -15% long unwinding | +1.2% | - | -23% | up |
| MAHABANK | 97.6 | -1.9% | -0.7 | 1.6x | 0.17 | +6.0% | +28.2% | 3.0% | -21% long unwinding | +1.1% | - | -3% | up |
| UNOMINDA | 1356.9 | -1.7% | -0.4 | 0.3x | 0.00 | +0.7% | +26.9% | 3.8% | -30% long unwinding | +1.6% | - | -4% | up |
| CHOLAFIN | 1831.0 | -2.3% | -0.9 | 1.0x | 0.11 | -1.0% | +26.5% | 2.8% | -14% long unwinding | +1.5% | - | -6% | up |

## Weakest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PIIND | 1571.0 | -1.6% | -0.4 | 0.7x | 0.02 | -6.5% | -22.2% | 4.6% | -33% long unwinding | -0.3% | 2.2% | -56% | down 20d-down |
| APLAPOLLO | 1670.0 | -21.3% | -5.3 | 29.1x | 0.06 | -25.8% | -19.6% | 5.1% | -33% long unwinding | +1.5% | 8.2% | -28% | mixed 20d-down |
| KAYNES | 2809.0 | -3.5% | -0.7 | 1.1x | 0.05 | -5.7% | -15.1% | 5.1% | -59% long unwinding | +0.8% | - | -55% | down |
| PAGEIND | 30100.0 | -3.0% | -0.8 | 1.7x | 0.20 | -4.3% | -11.2% | 4.0% | -53% long unwinding | +0.7% | 1.9% | -31% | down 20d-down |
| ASTRAL | 1225.0 | -2.2% | -0.7 | 0.5x | 0.00 | -2.5% | -9.2% | 3.2% | -27% long unwinding | +0.2% | - | -31% | down |
| INOXWIND | 53.7 | -3.2% | -0.6 | 1.1x | 0.05 | -9.8% | -8.1% | 5.5% | -6% long unwinding | +1.4% | 3.2% | -63% | down 20d-down |
| CUMMINSIND | 4052.8 | -1.1% | -0.3 | 0.5x | 0.22 | -4.3% | -7.6% | 4.5% | -4% long unwinding | -0.2% | - | -34% | down |
| OIL | 422.5 | -2.2% | -0.9 | 1.3x | 0.12 | -4.3% | -7.1% | 2.6% | -12% long unwinding | +0.1% | 1.7% | -20% | down 20d-down |

## Within 2% of the 52-week high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DLF | 794.1 | +1.2% | +0.5 | 1.1x | 0.83 | +5.2% | +19.9% | 2.4% | -17% short covering | +1.1% | 1.7% | -0% | up 20d-up |
| MARICO | 919.5 | +0.3% | +0.1 | 0.8x | 0.76 | +0.6% | +18.6% | 1.9% | -19% short covering | +0.9% | - | -1% | up |
| EICHERMOT | 8172.5 | +0.7% | +0.3 | 1.4x | 0.31 | +7.5% | +15.1% | 2.7% | +5% long build-up | +1.0% | 1.6% | -1% | up 20d-up |
| INDHOTEL | 906.0 | -0.7% | -0.3 | 0.7x | 0.21 | +2.3% | +13.9% | 2.6% | -12% long unwinding | +1.0% | 1.6% | -1% | up |
| APOLLOHOSP | 9257.0 | +0.6% | +0.3 | 1.4x | 0.10 | +5.5% | +18.0% | 2.2% | +11% long build-up | +0.7% | 1.7% | -2% | up |
| COFORGE | 2142.3 | +2.7% | +0.9 | 1.6x | 0.75 | +6.6% | +7.5% | 3.0% | -11% short covering | +0.7% | 2.1% | -2% | up |
| NAVINFLUOR | 10154.0 | +0.8% | +0.2 | 0.7x | 0.49 | +2.7% | +32.5% | 3.1% | -9% short covering | +0.2% | - | -2% | up |

## Reading the columns

- In ATRs: last day's move divided by the stock's average true range. Above 1.5 is an unusually large day.
- Close in range: 1.00 closed at the day's high, 0.00 at the low.
- Est. gap: the stock's beta times the expected index gap. It ignores stock news, which usually matters more.
- Options: 1-day move: the daily move implied by the nearest at-the-money straddle. Shown for focus and swing stocks.
- Options IV vs realised: at-the-money implied volatility divided by the stock's 20-day realised volatility.
  Above about 1.6 the options are expensive (often before results) and buying them needs a bigger move.
- Momentum pct: rank 0-100 across F&O stocks on volatility-adjusted 6- and 12-month returns.
- The full per-stock data is in momentum/latest.json.
