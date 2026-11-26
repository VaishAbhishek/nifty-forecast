# F&O momentum data for 2026-11-26

Built 08:10 on the VM from Upstox. 218 stocks, 0 failed. Prices are the last completed session (2026-11-25).
Numbers here are measured. Reasons are not: this file cannot tell why a stock moved.

Notes: BSE filings not read (HTTP 403 for https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w: <); the report's web search is the fallback

## Market

- Nifty: close 25819.2, last day +1.85%, 5 days +1.70%. Regime: **drift** (10-day efficiency 0.34, against 20/50-day averages: up).
- India VIX: 17.67.
- Momentum crash risk: **normal** (Nifty +0.0% from its 20-day high, above its 50-day average; VIX 1.21 times its 60-day median).
- Expected index gap: +0.44% (GIFT Nifty 26050.0 against the Nifty futures close 25935.0; GIFT's own change +0.95%). An estimate, not the open.
- Overnight: brent +4.02%, nasdaq -0.36%, spx -0.07%, usdinr -0.74%.
- Flows (units as Upstox reports them): FII cash net +4479 (2026-11-25); DII cash net +4019 (2026-11-25); FII index futures 24% long; FII stock futures 57% long.
- Sector indices, last session and 5 sessions: Bank +1.8% / +2.3%, Financials +2.2% / +2.0%, IT +1.1% / +1.8%, Auto +1.2% / +3.8%, Pharma +2.4% / +2.9%, Metal -2.0% / -7.6%, FMCG +3.8% / +5.3%, Energy +0.0% / -1.4%, Realty +0.0% / +1.7%.

## What past gaps did next (all F&O stocks, about one year, 20420 gaps)

Kept going = closed beyond the open in the gap's direction. Filled = traded back to the previous close that day.

| Gap | Count | Kept going | Filled | Average open-to-close in the gap's direction |
|---|---|---|---|---|
| down 0.5-1% | 5033 | 50% | 64% | +0.02% |
| down 1-2% | 2604 | 52% | 41% | +0.16% |
| down 2-4% | 923 | 43% | 29% | -0.31% |
| down 4+% | 193 | 35% | 13% | -0.64% |
| up 0.5-1% | 7051 | 46% | 70% | -0.04% |
| up 1-2% | 3277 | 50% | 46% | +0.05% |
| up 2-4% | 1018 | 53% | 24% | +0.22% |
| up 4+% | 321 | 39% | 9% | -0.47% |

Futures open interest source: end-of-day snapshot of 2026-11-25.

## Swing candidates (rules v3)

Strong 6- and 12-month momentum adjusted for volatility (NSE's momentum-index method), within 15% of the
52-week high, in a tight base or an orderly pullback. Enter only on a close above the trigger; stop below
the base. Shorts (weak momentum near the 52-week low) need futures or puts.

| Stock | Dir | Momentum pct | Setup | Volume drying up | Close | Trigger | Stop | Target 2R | Risk (ATRs) | From 52w high | 5d | Options IV vs realised | Expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DIVISLAB | UP | 100 | tight base | no | 11716.5 | 11838.9 | 10954.0 | 13608.7 | 2.3 | -1% | +5.1% | 0.81 | 2026-12-29 |
| ATHERENERG | UP | 99 | tight base | yes | 1871.9 | 2028.5 | 1847.0 | 2391.4 | 2.6 | -7% | -1.9% | 1.13 | 2026-12-29 |
| ANANDRATHI | UP | 99 | tight base | yes | 2380.0 | 2413.3 | 2344.3 | 2551.4 | 2.1 | -1% | +0.2% | 1.50 | 2026-12-29 |
| SONACOMS | UP | 98 | tight base | yes | 883.1 | 937.1 | 879.9 | 1051.5 | 2.6 | -6% | -1.8% | 1.23 | 2026-12-29 |
| ACUTAAS | UP | 98 | tight base | yes | 3993.0 | 4144.9 | 3720.2 | 4994.4 | 2.8 | -3% | +1.3% | 1.01 | 2026-12-29 |
| AUROPHARMA | UP | 97 | tight base | no | 1843.0 | 1864.1 | 1778.0 | 2036.4 | 2.0 | -1% | +2.7% | 1.03 | 2026-12-29 |
| INDHOTEL | UP | 96 | tight base | yes | 903.9 | 928.1 | 865.4 | 1053.5 | 2.7 | -2% | +0.3% | 1.05 | 2026-12-29 |
| FEDERALBNK | UP | 96 | tight base | no | 356.2 | 377.1 | 344.0 | 443.4 | 3.5 | -5% | -2.6% | 0.90 | 2026-12-29 |
| NYKAA | UP | 95 | tight base | yes | 358.0 | 369.3 | 351.6 | 404.6 | 1.8 | -3% | +0.0% | 1.27 | 2026-12-29 |
| TVSMOTOR | UP | 94 | tight base | no | 4610.0 | 4647.7 | 4360.0 | 5223.1 | 2.5 | -1% | +3.2% | 0.87 | 2026-12-29 |
| BOSCHLTD | UP | 94 | tight base | no | 49130.0 | 51085.9 | 48370.0 | 56517.7 | 2.3 | -6% | +0.1% | 0.77 | 2026-12-29 |
| KALYANKJIL | UP | 94 | tight base | no | 636.4 | 733.2 | 617.0 | 965.5 | 3.0 | -13% | -6.8% | 0.82 | 2026-12-29 |
| MAZDOCK | DOWN | 3 | tight base | yes | 1799.0 | 1786.9 | 1927.3 | 1506.1 | 3.3 | -37% | -2.6% | 1.28 | 2026-12-29 |
| VMM | DOWN | 5 | tight base | yes | 94.8 | 89.0 | 97.8 | 71.5 | 3.2 | -32% | +1.9% | 0.91 | 2026-12-29 |
| TIINDIA | DOWN | 6 | tight base | no | 2217.7 | 2173.5 | 2349.0 | 1822.4 | 2.3 | -34% | -0.6% | 1.00 | 2026-12-29 |
| NBCC | DOWN | 6 | tight base | no | 75.9 | 75.3 | 82.8 | 60.3 | 2.9 | -40% | -3.3% | 0.74 | 2026-12-29 |
| GODFRYPHLP | DOWN | 11 | tight base | yes | 1761.5 | 1729.8 | 1890.4 | 1408.5 | 3.0 | -41% | -1.5% | 1.53 | 2026-12-29 |
| WAAREEENER | DOWN | 12 | tight base | yes | 2379.9 | 2356.5 | 2629.9 | 1809.6 | 3.2 | -33% | -2.5% | 0.96 | 2026-12-29 |

## Industry strength among F&O stocks (source: NSE Nifty 500 list)

Ranked by median 20-session strength against Nifty. Industries need 3+ F&O members.

| Rank | Industry | Members | Median last day | Median 5d | Median vs Nifty 20d | Share up 5d |
|---|---|---|---|---|---|---|
| 1 | Realty | 6 | +0.0% | +2.0% | +5.2% | 67% |
| 2 | Fast Moving Consumer Goods | 14 | +3.4% | +5.2% | +3.1% | 93% |
| 3 | Consumer Durables | 10 | +0.6% | +3.4% | +2.6% | 60% |
| 4 | Financial Services | 55 | +0.6% | +0.4% | +1.5% | 56% |
| 5 | Services | 5 | +0.4% | +0.5% | +1.2% | 60% |
| 6 | Automobile and Auto Components | 16 | +1.0% | +1.1% | -2.5% | 69% |
| 7 | Construction Materials | 4 | +0.8% | +2.5% | -2.8% | 100% |
| 8 | Oil Gas & Consumable Fuels | 9 | +1.0% | +0.3% | -3.0% | 56% |
| 9 | Healthcare | 17 | +2.4% | +2.8% | -4.9% | 94% |
| 10 | Chemicals | 7 | -0.5% | +0.5% | -5.7% | 57% |
| 11 | Consumer Services | 9 | +2.1% | +0.5% | -5.8% | 67% |
| 12 | Construction | 3 | -0.0% | -3.3% | -5.8% | 33% |
| 13 | Power | 8 | -1.2% | -2.9% | -7.9% | 25% |
| 14 | Metals & Mining | 10 | -1.2% | -4.8% | -12.0% | 0% |
| 15 | Information Technology | 13 | +0.9% | +2.2% | -13.9% | 69% |
| 16 | Telecommunication | 3 | -0.5% | -2.8% | -14.4% | 0% |
| 17 | Capital Goods | 27 | -0.4% | -2.1% | -15.6% | 33% |

## Industry and peers of focus and swing stocks

Peers = F&O stocks whose daily moves (market move removed) tracked this stock most closely over 60 sessions.
When a stock has news, check whether its peers have moved yet.

| Stock | Industry (rank) | Peers (correlation) | Peers' last day |
|---|---|---|---|
| APLAPOLLO | Capital Goods (17) | TATASTEEL 0.58 | TATASTEEL -2.3% |
| HINDUNILVR | Fast Moving Consumer Goods (2) | BRITANNIA 0.62, DABUR 0.62, GODREJCP 0.58, MARICO 0.46 | BRITANNIA +5.1%, DABUR +7.8%, GODREJCP +5.6%, MARICO +1.7% |
| DMART | Consumer Services (11) | NESTLEIND 0.47 | NESTLEIND +4.0% |
| DABUR | Fast Moving Consumer Goods (2) | HINDUNILVR 0.62, COLPAL 0.57, GODREJCP 0.56, BRITANNIA 0.54, PIIND 0.50 | HINDUNILVR +6.1%, COLPAL +4.0%, GODREJCP +5.6%, BRITANNIA +5.1%, PIIND +0.3% |
| GODREJCP | Fast Moving Consumer Goods (2) | HINDUNILVR 0.58, DABUR 0.56, BRITANNIA 0.48 | HINDUNILVR +6.1%, DABUR +7.8%, BRITANNIA +5.1% |
| BAJAJFINSV | Financial Services (4) | LTF 0.68, PRESTIGE 0.51, BAJFINANCE 0.49, SHRIRAMFIN 0.48, GODREJPROP 0.47 | LTF +3.6%, PRESTIGE -0.1%, BAJFINANCE +3.3%, SHRIRAMFIN -0.6%, GODREJPROP -0.2% |
| KAYNES | Capital Goods (17) | SAIL 0.50, JINDALSTEL 0.45 | SAIL -0.6%, JINDALSTEL -2.3% |
| POLICYBZR | Financial Services (4) | MFSL 0.58, LTF 0.50 | MFSL +0.8%, LTF +3.6% |
| TATACONSUM | Fast Moving Consumer Goods (2) | - | - |
| COLPAL | Fast Moving Consumer Goods (2) | BRITANNIA 0.59, DABUR 0.57, GODFRYPHLP 0.56, RECLTD 0.54, NESTLEIND 0.46 | BRITANNIA +5.1%, DABUR +7.8%, GODFRYPHLP +0.8%, RECLTD +2.1%, NESTLEIND +4.0% |
| HEROMOTOCO | Automobile and Auto Components (6) | EICHERMOT 0.53 | EICHERMOT +2.0% |
| OFSS | Information Technology (15) | ATHERENERG 0.47 | ATHERENERG -5.4% |
| ICICIBANK | Financial Services (4) | - | - |
| COFORGE | Information Technology (15) | PERSISTENT 0.66, MPHASIS 0.48, ATHERENERG 0.45 | PERSISTENT -2.6%, MPHASIS +2.6%, ATHERENERG -5.4% |
| KEI | Capital Goods (17) | POLYCAB 0.78, APARINDS 0.48, ENRIN 0.47, BHEL 0.46, HDFCAMC 0.46 | POLYCAB -0.7%, APARINDS +0.5%, ENRIN -0.2%, BHEL -0.5%, HDFCAMC -0.4% |
| LTF | Financial Services (4) | BAJAJFINSV 0.68, CHOLAFIN 0.65, SBICARD 0.62, ABCAPITAL 0.59, BAJFINANCE 0.54 | BAJAJFINSV +2.4%, CHOLAFIN +2.0%, SBICARD +2.4%, ABCAPITAL +1.5%, BAJFINANCE +3.3% |
| NATIONALUM | Metals & Mining (14) | HINDALCO 0.66, HINDZINC 0.57, JINDALSTEL 0.54, INOXWIND 0.53, JSWSTEEL 0.53 | HINDALCO -1.2%, HINDZINC -1.8%, JINDALSTEL -2.3%, INOXWIND -2.5%, JSWSTEEL -0.7% |
| EICHERMOT | Automobile and Auto Components (6) | HEROMOTOCO 0.53, MARUTI 0.51, TVSMOTOR 0.50, BAJAJ-AUTO 0.46 | HEROMOTOCO +3.9%, MARUTI +1.4%, TVSMOTOR +1.8%, BAJAJ-AUTO +2.1% |
| TATASTEEL | Metals & Mining (14) | APLAPOLLO 0.58, HINDALCO 0.49, JSWSTEEL 0.48, JINDALSTEL 0.46 | APLAPOLLO -11.6%, HINDALCO -1.2%, JSWSTEEL -0.7%, JINDALSTEL -2.3% |
| DIVISLAB | Healthcare (9) | LAURUSLABS 0.57, SUNPHARMA 0.53, AUROPHARMA 0.49 | LAURUSLABS +3.8%, SUNPHARMA +2.2%, AUROPHARMA +2.6% |
| ATHERENERG | Automobile and Auto Components (6) | POLYCAB 0.49, OFSS 0.47, COFORGE 0.45 | POLYCAB -0.7%, OFSS -4.1%, COFORGE -3.8% |
| ANANDRATHI | Financial Services (4) | - | - |
| SONACOMS | Automobile and Auto Components (6) | NAVINFLUOR 0.53, MOTHERSON 0.47, ACUTAAS 0.46, PGEL 0.46 | NAVINFLUOR -1.9%, MOTHERSON +0.3%, ACUTAAS +3.0%, PGEL -0.5% |
| ACUTAAS | Healthcare (9) | SONACOMS 0.46 | SONACOMS -0.3% |
| AUROPHARMA | Healthcare (9) | DIVISLAB 0.49 | DIVISLAB +4.6% |
| INDHOTEL | Consumer Services (11) | - | - |
| FEDERALBNK | Financial Services (4) | PNB 0.50, BANKBARODA 0.46, SBIN 0.46 | PNB -0.8%, BANKBARODA +0.3%, SBIN +0.5% |
| NYKAA | Consumer Services (11) | POLYCAB 0.55, GVT&D 0.50, CGPOWER 0.47, PREMIERENE 0.46 | POLYCAB -0.7%, GVT&D -3.0%, CGPOWER -1.5%, PREMIERENE +0.7% |
| TVSMOTOR | Automobile and Auto Components (6) | MOTHERSON 0.60, MARUTI 0.58, UPL 0.51, SUZLON 0.50, EICHERMOT 0.50 | MOTHERSON +0.3%, MARUTI +1.4%, UPL -0.6%, SUZLON +0.8%, EICHERMOT +2.0% |
| BOSCHLTD | Automobile and Auto Components (6) | MOTHERSON 0.63, HDFCAMC 0.49, TVSMOTOR 0.48, SUZLON 0.47, BHARATFORG 0.46 | MOTHERSON +0.3%, HDFCAMC -0.4%, TVSMOTOR +1.8%, SUZLON +0.8%, BHARATFORG +0.8% |
| KALYANKJIL | Consumer Durables (3) | - | - |
| MAZDOCK | Capital Goods (17) | BDL 0.71, WAAREEENER 0.57, RVNL 0.56, AMBUJACEM 0.48, HINDZINC 0.48 | BDL +0.8%, WAAREEENER -0.4%, RVNL -0.0%, AMBUJACEM +0.0%, HINDZINC -1.8% |
| VMM | Consumer Services (11) | DIXON 0.47 | DIXON -3.1% |
| TIINDIA | Automobile and Auto Components (6) | CGPOWER 0.65, ASTRAL 0.55, BHEL 0.53, MOTHERSON 0.52, NBCC 0.52 | CGPOWER -1.5%, ASTRAL +1.7%, BHEL -0.5%, MOTHERSON +0.3%, NBCC -2.2% |
| NBCC | Construction (12) | DIXON 0.64, DELHIVERY 0.61, JIOFIN 0.60, INOXWIND 0.60, GVT&D 0.59 | DIXON -3.1%, DELHIVERY +1.1%, JIOFIN +1.4%, INOXWIND -2.5%, GVT&D -3.0% |
| GODFRYPHLP | Fast Moving Consumer Goods (2) | LICI 0.63, RVNL 0.57, COLPAL 0.56, KFINTECH 0.56, UPL 0.54 | LICI +0.3%, RVNL -0.0%, COLPAL +4.0%, KFINTECH +0.5%, UPL -0.6% |
| WAAREEENER | Capital Goods (17) | MAZDOCK 0.57, RVNL 0.55, PREMIERENE 0.51, BHEL 0.45 | MAZDOCK -0.1%, RVNL -0.0%, PREMIERENE +0.7%, BHEL -0.5% |

## Focus list: stocks on two or more lists below

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1476.0 | -11.6% | -1.9 | 20.9x | 0.65 | -32.6% | -33.3% | 7.0% | +27% short build-up | +0.4% | 3.3% | -36% | down 20d-down |
| HINDUNILVR | 2141.8 | +6.1% | +2.7 | 3.1x | 1.00 | +6.6% | +17.8% | 2.1% | +7% long build-up | +0.5% | 1.4% | -14% | up 20d-up |
| DMART | 3592.0 | +5.5% | +3.1 | 2.6x | 1.00 | +3.5% | +12.2% | 1.7% | +2% | +0.3% | 1.5% | -23% | mixed 20d-up |
| DABUR | 430.0 | +7.8% | +2.9 | 8.4x | 0.89 | +11.9% | +20.2% | 2.5% | +7% long build-up | +0.3% | 1.8% | -19% | up 20d-up |
| GODREJCP | 963.0 | +5.6% | +2.1 | 2.5x | 1.00 | +7.7% | +16.2% | 2.5% | +3% | +0.3% | 1.5% | -24% | up 20d-up |
| BAJAJFINSV | 1925.0 | +2.4% | +0.9 | 4.7x | 0.41 | +2.9% | +14.8% | 2.6% | +8% long build-up | +0.5% | 1.6% | -9% | up 20d-up |
| KAYNES | 2698.0 | -4.0% | -0.8 | 1.3x | 0.08 | -5.6% | -19.5% | 5.4% | +14% short build-up | +0.2% | 3.2% | -55% | down 20d-down |
| POLICYBZR | 1123.8 | +3.2% | +0.7 | 2.9x | 0.17 | +6.8% | +11.4% | 4.6% | +7% long build-up | +0.7% | 3.2% | -43% | mixed 20d-up |
| TATACONSUM | 1185.8 | +4.7% | +2.2 | 1.9x | 1.00 | +6.6% | +18.6% | 2.0% | +4% long build-up | +0.3% | 4.6% | -8% | up 20d-up |
| COLPAL | 1825.0 | +4.0% | +1.7 | 2.2x | 1.00 | +6.1% | +13.8% | 2.2% | +3% long build-up | +0.4% | 1.7% | -21% | mixed 20d-up |
| HEROMOTOCO | 5751.5 | +3.9% | +1.6 | 1.8x | 1.00 | +7.9% | +10.2% | 2.4% | +8% long build-up | +0.4% | 1.8% | -10% | up 20d-up |
| OFSS | 9275.0 | -4.1% | -1.6 | 2.1x | 0.12 | -4.8% | -6.6% | 2.7% | +6% short build-up | +0.1% | 2.2% | -26% | down 20d-down |
| ICICIBANK | 1640.0 | +3.4% | +1.4 | 1.1x | 0.70 | +2.6% | +18.2% | 2.4% | +7% long build-up | +0.5% | 1.2% | -1% | up |
| COFORGE | 2060.0 | -3.8% | -1.2 | 1.4x | 0.10 | +0.9% | +3.1% | 3.4% | +12% short build-up | +0.2% | 2.2% | -6% | up |
| KEI | 3652.0 | -3.9% | -1.1 | 1.1x | 0.03 | -5.2% | -5.7% | 3.8% | +5% short build-up | +0.3% | 2.3% | -38% | down 20d-down |
| LTF | 283.9 | +3.6% | +1.1 | 4.1x | 0.39 | +1.3% | +17.9% | 3.3% | -2% | +0.6% | 2.2% | -16% | mixed 20d-up |
| NATIONALUM | 287.8 | -3.6% | -1.0 | 1.5x | 0.23 | -10.3% | -6.6% | 3.7% | +3% short build-up | +0.3% | 2.4% | -35% | down 20d-down |
| EICHERMOT | 8336.0 | +2.0% | +0.7 | 1.5x | 0.88 | +6.5% | +16.3% | 2.7% | +7% long build-up | +0.4% | 1.5% | -0% | up 20d-up |
| TATASTEEL | 159.3 | -2.3% | -0.6 | 4.3x | 0.32 | -12.2% | -7.1% | 4.0% | +2% | +0.4% | 2.1% | -29% | down 20d-down |

## Biggest up-moves last session (in units of the stock's normal daily range)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DMART | 3592.0 | +5.5% | +3.1 | 2.6x | 1.00 | +3.5% | +12.2% | 1.7% | +2% | +0.3% | 1.5% | -23% | mixed 20d-up |
| DABUR | 430.0 | +7.8% | +2.9 | 8.4x | 0.89 | +11.9% | +20.2% | 2.5% | +7% long build-up | +0.3% | 1.8% | -19% | up 20d-up |
| HINDUNILVR | 2141.8 | +6.1% | +2.7 | 3.1x | 1.00 | +6.6% | +17.8% | 2.1% | +7% long build-up | +0.5% | 1.4% | -14% | up 20d-up |
| TATACONSUM | 1185.8 | +4.7% | +2.2 | 1.9x | 1.00 | +6.6% | +18.6% | 2.0% | +4% long build-up | +0.3% | 4.6% | -8% | up 20d-up |
| GODREJCP | 963.0 | +5.6% | +2.1 | 2.5x | 1.00 | +7.7% | +16.2% | 2.5% | +3% | +0.3% | 1.5% | -24% | up 20d-up |
| BRITANNIA | 5076.2 | +5.1% | +1.9 | 2.1x | 1.00 | +8.0% | +11.3% | 2.5% | -0% | +0.3% | - | -19% | mixed |
| NESTLEIND | 1358.5 | +4.0% | +1.7 | 1.0x | 1.00 | +5.0% | +15.1% | 2.2% | +3% long build-up | +0.4% | - | -13% | mixed 20d-up |
| COLPAL | 1825.0 | +4.0% | +1.7 | 2.2x | 1.00 | +6.1% | +13.8% | 2.2% | +3% long build-up | +0.4% | 1.7% | -21% | mixed 20d-up |
| HEROMOTOCO | 5751.5 | +3.9% | +1.6 | 1.8x | 1.00 | +7.9% | +10.2% | 2.4% | +8% long build-up | +0.4% | 1.8% | -10% | up 20d-up |
| ZYDUSLIFE | 1236.0 | +3.0% | +1.5 | 0.8x | 1.00 | +2.6% | +5.4% | 1.9% | +5% long build-up | +0.2% | - | -2% | up |

## Biggest down-moves last session

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1476.0 | -11.6% | -1.9 | 20.9x | 0.65 | -32.6% | -33.3% | 7.0% | +27% short build-up | +0.4% | 3.3% | -36% | down 20d-down |
| OFSS | 9275.0 | -4.1% | -1.6 | 2.1x | 0.12 | -4.8% | -6.6% | 2.7% | +6% short build-up | +0.1% | 2.2% | -26% | down 20d-down |
| ATHERENERG | 1871.9 | -5.4% | -1.5 | 0.9x | 0.08 | -1.9% | +11.8% | 3.7% | +2% | +0.2% | 2.6% | -7% | up |
| JSWENERGY | 485.8 | -3.3% | -1.4 | 1.5x | 0.04 | -5.7% | +3.4% | 2.5% | +2% | +0.2% | - | -21% | mixed |
| ADANIENSOL | 1408.0 | -4.2% | -1.3 | 1.7x | 0.08 | -5.7% | +7.3% | 3.3% | +2% | +0.4% | - | -21% | mixed |
| COFORGE | 2060.0 | -3.8% | -1.2 | 1.4x | 0.10 | +0.9% | +3.1% | 3.4% | +12% short build-up | +0.2% | 2.2% | -6% | up |
| DIXON | 12978.0 | -3.1% | -1.1 | 1.4x | 0.22 | -0.8% | +15.5% | 3.0% | +2% | +0.4% | - | -18% | mixed |
| KEI | 3652.0 | -3.9% | -1.1 | 1.1x | 0.03 | -5.2% | -5.7% | 3.8% | +5% short build-up | +0.3% | 2.3% | -38% | down 20d-down |
| NATIONALUM | 287.8 | -3.6% | -1.0 | 1.5x | 0.23 | -10.3% | -6.6% | 3.7% | +3% short build-up | +0.3% | 2.4% | -35% | down 20d-down |
| PERSISTENT | 6120.0 | -2.6% | -1.0 | 0.8x | 0.00 | +3.5% | +4.9% | 2.7% | +2% | +0.2% | - | -7% | up |

## Unusual volume last session (against its own 20-day average)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1476.0 | -11.6% | -1.9 | 20.9x | 0.65 | -32.6% | -33.3% | 7.0% | +27% short build-up | +0.4% | 3.3% | -36% | down 20d-down |
| DABUR | 430.0 | +7.8% | +2.9 | 8.4x | 0.89 | +11.9% | +20.2% | 2.5% | +7% long build-up | +0.3% | 1.8% | -19% | up 20d-up |
| BAJAJFINSV | 1925.0 | +2.4% | +0.9 | 4.7x | 0.41 | +2.9% | +14.8% | 2.6% | +8% long build-up | +0.5% | 1.6% | -9% | up 20d-up |
| TATASTEEL | 159.3 | -2.3% | -0.6 | 4.3x | 0.32 | -12.2% | -7.1% | 4.0% | +2% | +0.4% | 2.1% | -29% | down 20d-down |
| LTF | 283.9 | +3.6% | +1.1 | 4.1x | 0.39 | +1.3% | +17.9% | 3.3% | -2% | +0.6% | 2.2% | -16% | mixed 20d-up |
| HINDUNILVR | 2141.8 | +6.1% | +2.7 | 3.1x | 1.00 | +6.6% | +17.8% | 2.1% | +7% long build-up | +0.5% | 1.4% | -14% | up 20d-up |
| POLICYBZR | 1123.8 | +3.2% | +0.7 | 2.9x | 0.17 | +6.8% | +11.4% | 4.6% | +7% long build-up | +0.7% | 3.2% | -43% | mixed 20d-up |
| HDFCLIFE | 601.3 | +4.6% | +1.5 | 2.9x | 0.71 | +1.1% | +17.1% | 3.0% | +0% | +0.6% | - | -24% | up |
| DMART | 3592.0 | +5.5% | +3.1 | 2.6x | 1.00 | +3.5% | +12.2% | 1.7% | +2% | +0.3% | 1.5% | -23% | mixed 20d-up |
| MFSL | 1444.0 | +0.8% | +0.2 | 2.6x | 0.00 | +0.9% | +17.3% | 3.4% | +6% long build-up | +0.5% | - | -24% | mixed |
| GODREJCP | 963.0 | +5.6% | +2.1 | 2.5x | 1.00 | +7.7% | +16.2% | 2.5% | +3% | +0.3% | 1.5% | -24% | up 20d-up |
| ADANIGREEN | 1364.5 | -1.9% | -0.6 | 2.4x | 0.15 | -4.6% | +5.9% | 3.1% | +3% short build-up | +0.5% | - | -16% | mixed |

## Closed above the 20-day high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DABUR | 430.0 | +7.8% | +2.9 | 8.4x | 0.89 | +11.9% | +20.2% | 2.5% | +7% long build-up | +0.3% | 1.8% | -19% | up 20d-up |
| BAJAJFINSV | 1925.0 | +2.4% | +0.9 | 4.7x | 0.41 | +2.9% | +14.8% | 2.6% | +8% long build-up | +0.5% | 1.6% | -9% | up 20d-up |
| LTF | 283.9 | +3.6% | +1.1 | 4.1x | 0.39 | +1.3% | +17.9% | 3.3% | -2% | +0.6% | 2.2% | -16% | mixed 20d-up |
| HINDUNILVR | 2141.8 | +6.1% | +2.7 | 3.1x | 1.00 | +6.6% | +17.8% | 2.1% | +7% long build-up | +0.5% | 1.4% | -14% | up 20d-up |
| POLICYBZR | 1123.8 | +3.2% | +0.7 | 2.9x | 0.17 | +6.8% | +11.4% | 4.6% | +7% long build-up | +0.7% | 3.2% | -43% | mixed 20d-up |
| DMART | 3592.0 | +5.5% | +3.1 | 2.6x | 1.00 | +3.5% | +12.2% | 1.7% | +2% | +0.3% | 1.5% | -23% | mixed 20d-up |
| GODREJCP | 963.0 | +5.6% | +2.1 | 2.5x | 1.00 | +7.7% | +16.2% | 2.5% | +3% | +0.3% | 1.5% | -24% | up 20d-up |
| COLPAL | 1825.0 | +4.0% | +1.7 | 2.2x | 1.00 | +6.1% | +13.8% | 2.2% | +3% long build-up | +0.4% | 1.7% | -21% | mixed 20d-up |
| TATACONSUM | 1185.8 | +4.7% | +2.2 | 1.9x | 1.00 | +6.6% | +18.6% | 2.0% | +4% long build-up | +0.3% | 4.6% | -8% | up 20d-up |
| TRENT | 3319.6 | +3.5% | +1.3 | 1.9x | 0.76 | +4.5% | +17.7% | 2.5% | +1% | +0.5% | - | -2% | up 20d-up |

## Closed below the 20-day low

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1476.0 | -11.6% | -1.9 | 20.9x | 0.65 | -32.6% | -33.3% | 7.0% | +27% short build-up | +0.4% | 3.3% | -36% | down 20d-down |
| TATASTEEL | 159.3 | -2.3% | -0.6 | 4.3x | 0.32 | -12.2% | -7.1% | 4.0% | +2% | +0.4% | 2.1% | -29% | down 20d-down |
| OFSS | 9275.0 | -4.1% | -1.6 | 2.1x | 0.12 | -4.8% | -6.6% | 2.7% | +6% short build-up | +0.1% | 2.2% | -26% | down 20d-down |
| TATAPOWER | 323.0 | -1.5% | -0.5 | 1.6x | 0.35 | -6.2% | -4.8% | 2.9% | +4% short build-up | +0.2% | - | -31% | down 20d-down |
| NATIONALUM | 287.8 | -3.6% | -1.0 | 1.5x | 0.23 | -10.3% | -6.6% | 3.7% | +3% short build-up | +0.3% | 2.4% | -35% | down 20d-down |
| KAYNES | 2698.0 | -4.0% | -0.8 | 1.3x | 0.08 | -5.6% | -19.5% | 5.4% | +14% short build-up | +0.2% | 3.2% | -55% | down 20d-down |
| COCHINSHIP | 1082.0 | -0.7% | -0.2 | 1.2x | 0.31 | -5.7% | -3.7% | 3.5% | -2% | +0.4% | - | -41% | down 20d-down |
| IDEA | 11.7 | -1.9% | -0.6 | 1.1x | 0.27 | -5.0% | -3.5% | 3.0% | -0% | +0.5% | - | -26% | down 20d-down |
| KEI | 3652.0 | -3.9% | -1.1 | 1.1x | 0.03 | -5.2% | -5.7% | 3.8% | +5% short build-up | +0.3% | 2.3% | -38% | down 20d-down |
| MANAPPURAM | 267.5 | -1.3% | -0.3 | 1.0x | 0.29 | -9.8% | -6.6% | 4.3% | -1% | +0.5% | - | -30% | down 20d-down |

## Futures: price up with open interest up (long build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CUB | 247.0 | +0.6% | +0.2 | 1.0x | 0.79 | +6.3% | +15.9% | 3.5% | +13% long build-up | +0.3% | - | -3% | up |
| BAJAJFINSV | 1925.0 | +2.4% | +0.9 | 4.7x | 0.41 | +2.9% | +14.8% | 2.6% | +8% long build-up | +0.5% | 1.6% | -9% | up 20d-up |
| HEROMOTOCO | 5751.5 | +3.9% | +1.6 | 1.8x | 1.00 | +7.9% | +10.2% | 2.4% | +8% long build-up | +0.4% | 1.8% | -10% | up 20d-up |
| GAIL | 187.5 | +1.0% | +0.5 | 1.1x | 0.69 | +0.3% | +13.2% | 1.9% | +8% long build-up | +0.3% | - | -2% | up |
| EICHERMOT | 8336.0 | +2.0% | +0.7 | 1.5x | 0.88 | +6.5% | +16.3% | 2.7% | +7% long build-up | +0.4% | 1.5% | -0% | up 20d-up |
| POLICYBZR | 1123.8 | +3.2% | +0.7 | 2.9x | 0.17 | +6.8% | +11.4% | 4.6% | +7% long build-up | +0.7% | 3.2% | -43% | mixed 20d-up |
| HINDUNILVR | 2141.8 | +6.1% | +2.7 | 3.1x | 1.00 | +6.6% | +17.8% | 2.1% | +7% long build-up | +0.5% | 1.4% | -14% | up 20d-up |
| ICICIBANK | 1640.0 | +3.4% | +1.4 | 1.1x | 0.70 | +2.6% | +18.2% | 2.4% | +7% long build-up | +0.5% | 1.2% | -1% | up |

## Futures: price down with open interest up (short build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1476.0 | -11.6% | -1.9 | 20.9x | 0.65 | -32.6% | -33.3% | 7.0% | +27% short build-up | +0.4% | 3.3% | -36% | down 20d-down |
| KARURVYSYA | 378.8 | -1.4% | -0.4 | 2.1x | 0.38 | -3.8% | +8.0% | 3.5% | +21% short build-up | +0.2% | - | -5% | up |
| KAYNES | 2698.0 | -4.0% | -0.8 | 1.3x | 0.08 | -5.6% | -19.5% | 5.4% | +14% short build-up | +0.2% | 3.2% | -55% | down 20d-down |
| COFORGE | 2060.0 | -3.8% | -1.2 | 1.4x | 0.10 | +0.9% | +3.1% | 3.4% | +12% short build-up | +0.2% | 2.2% | -6% | up |
| RBLBANK | 390.4 | -0.8% | -0.3 | 1.0x | 0.34 | +0.1% | +12.0% | 2.9% | +8% short build-up | +0.2% | - | -9% | mixed |
| CAMS | 717.5 | -0.6% | -0.2 | 0.8x | 0.42 | -3.6% | +5.9% | 3.5% | +8% short build-up | +0.5% | - | -15% | up |
| SHRIRAMFIN | 990.0 | -0.6% | -0.2 | 1.1x | 0.14 | +0.7% | +20.2% | 3.0% | +7% short build-up | +0.6% | - | -14% | mixed |
| LODHA | 1202.0 | -1.4% | -0.4 | 1.4x | 0.42 | -0.1% | +19.0% | 3.7% | +6% short build-up | +0.6% | - | -11% | up |

## Strongest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VOLTAS | 1232.4 | +1.1% | +0.3 | 0.9x | 0.33 | +7.3% | +30.2% | 3.8% | +2% | +0.5% | - | -22% | up |
| MAXHEALTH | 1076.3 | -1.2% | -0.5 | 1.4x | 0.25 | +4.4% | +27.4% | 2.7% | +1% | +0.3% | - | -9% | up |
| KALYANKJIL | 636.4 | -2.5% | -0.4 | 0.5x | 0.32 | -6.8% | +27.3% | 6.0% | +1% | +0.4% | 3.1% | -13% | up |
| CHOLAFIN | 1868.0 | +2.0% | +0.7 | 1.0x | 0.24 | -0.9% | +27.2% | 2.9% | +4% long build-up | +0.6% | - | -4% | up |
| MOTILALOFS | 1230.1 | -0.4% | -0.1 | 0.7x | 0.29 | -0.8% | +26.9% | 4.1% | +2% | +0.6% | - | -4% | up NR7 |
| UNOMINDA | 1375.0 | +1.3% | +0.4 | 0.5x | 0.69 | -0.9% | +26.7% | 3.5% | +1% | +0.6% | - | -2% | up |
| INDIGO | 5720.0 | +3.6% | +1.2 | 1.8x | 0.73 | +1.9% | +24.4% | 2.8% | -1% | +0.5% | - | -4% | up 20d-up |
| HDFCBANK | 846.2 | +3.5% | +1.3 | 1.2x | 0.77 | +3.8% | +24.4% | 2.6% | -2% | +0.6% | - | -17% | up |

## Weakest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1476.0 | -11.6% | -1.9 | 20.9x | 0.65 | -32.6% | -33.3% | 7.0% | +27% short build-up | +0.4% | 3.3% | -36% | down 20d-down |
| PIIND | 1576.0 | +0.3% | +0.1 | 0.4x | 0.30 | -5.7% | -24.4% | 4.4% | -0% | -0.1% | - | -55% | down NR7 |
| KAYNES | 2698.0 | -4.0% | -0.8 | 1.3x | 0.08 | -5.6% | -19.5% | 5.4% | +14% short build-up | +0.2% | 3.2% | -55% | down 20d-down |
| PAGEIND | 30805.0 | +2.3% | +0.6 | 1.1x | 0.74 | -1.0% | -11.0% | 4.0% | -1% | +0.3% | - | -30% | down |
| INOXWIND | 52.4 | -2.5% | -0.5 | 0.9x | 0.06 | -12.3% | -10.6% | 5.2% | +1% | +0.5% | - | -63% | down 20d-down |
| CUMMINSIND | 4067.0 | +0.3% | +0.1 | 0.4x | 0.39 | +0.1% | -10.3% | 4.2% | +1% | -0.1% | - | -33% | down |
| ASTRAL | 1246.2 | +1.7% | +0.6 | 0.6x | 0.76 | +0.3% | -9.4% | 3.0% | -1% | +0.1% | - | -30% | down |
| OIL | 425.0 | +0.6% | +0.2 | 0.7x | 0.86 | -2.0% | -7.1% | 2.6% | +5% long build-up | +0.0% | - | -20% | down |

## Within 2% of the 52-week high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MARICO | 935.2 | +1.7% | +1.0 | 0.8x | 1.00 | +1.2% | +20.5% | 1.8% | +1% | +0.4% | - | +0% | up 20d-up |
| EICHERMOT | 8336.0 | +2.0% | +0.7 | 1.5x | 0.88 | +6.5% | +16.3% | 2.7% | +7% long build-up | +0.4% | 1.5% | -0% | up 20d-up |
| DLF | 795.0 | +0.1% | +0.1 | 1.1x | 0.82 | +3.8% | +18.5% | 2.4% | +1% | +0.4% | - | -0% | up |
| TVSMOTOR | 4610.0 | +1.8% | +0.7 | 0.6x | 0.81 | +3.2% | +12.8% | 2.5% | +1% | +0.4% | 1.6% | -1% | up |
| ICICIBANK | 1640.0 | +3.4% | +1.4 | 1.1x | 0.70 | +2.6% | +18.2% | 2.4% | +7% long build-up | +0.5% | 1.2% | -1% | up |
| GLENMARK | 2719.0 | +2.3% | +0.7 | 0.9x | 0.77 | +4.0% | +20.0% | 3.1% | +1% | +0.4% | - | -1% | up 20d-up |
| MANKIND | 2685.0 | +2.7% | +1.1 | 0.5x | 0.89 | +2.9% | +7.3% | 2.3% | +2% | +0.1% | - | -1% | up |
| AUROPHARMA | 1843.0 | +2.6% | +1.1 | 1.2x | 0.93 | +2.7% | +13.2% | 2.3% | +0% | +0.3% | 1.5% | -1% | up |

## Reading the columns

- In ATRs: last day's move divided by the stock's average true range. Above 1.5 is an unusually large day.
- Close in range: 1.00 closed at the day's high, 0.00 at the low.
- Est. gap: the stock's beta times the expected index gap. It ignores stock news, which usually matters more.
- Options: 1-day move: the daily move implied by the nearest at-the-money straddle. Shown for focus and swing stocks.
- Options IV vs realised: at-the-money implied volatility divided by the stock's 20-day realised volatility.
  Above about 1.6 the options are expensive (often before results) and buying them needs a bigger move.
- Momentum pct: rank 0-100 across F&O stocks on volatility-adjusted 6- and 12-month returns.
- The full per-stock data is in momentum/latest.json.
