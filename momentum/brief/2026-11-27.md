# F&O momentum data for 2026-11-27

Built 08:10 on the VM from Upstox. 218 stocks, 0 failed. Prices are the last completed session (2026-11-26).
Numbers here are measured. Reasons are not: this file cannot tell why a stock moved.

Notes: BSE filings not read (HTTP 403 for https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w: <); the report's web search is the fallback

## Market

- Nifty: close 25884.5, last day +0.25%, 5 days +2.60%. Regime: **drift** (10-day efficiency 0.29, against 20/50-day averages: up).
- India VIX: 16.84.
- Momentum crash risk: **normal** (Nifty +0.0% from its 20-day high, above its 50-day average; VIX 1.15 times its 60-day median).
- Expected index gap: -0.14% (GIFT Nifty 25995.5 against the Nifty futures close 26033.0; GIFT's own change -0.21%). An estimate, not the open.
- Overnight: brent -2.89%, nasdaq +0.23%, spx +0.16%, usdinr +0.23%.
- Flows (units as Upstox reports them): FII cash net +5843 (2026-11-26); DII cash net +5631 (2026-11-26); FII index futures 23% long; FII stock futures 57% long.
- Sector indices, last session and 5 sessions: Bank -0.3% / +2.4%, Financials -0.2% / +2.6%, IT +3.7% / +6.8%, Auto -0.7% / +4.5%, Pharma +0.5% / +3.2%, Metal +1.2% / -4.2%, FMCG -0.9% / +4.4%, Energy +0.6% / -0.3%, Realty +3.3% / +5.9%.

## What past gaps did next (all F&O stocks, about one year, 20461 gaps)

Kept going = closed beyond the open in the gap's direction. Filled = traded back to the previous close that day.

| Gap | Count | Kept going | Filled | Average open-to-close in the gap's direction |
|---|---|---|---|---|
| down 0.5-1% | 5023 | 50% | 64% | +0.02% |
| down 1-2% | 2605 | 52% | 41% | +0.16% |
| down 2-4% | 922 | 43% | 29% | -0.31% |
| down 4+% | 193 | 35% | 13% | -0.64% |
| up 0.5-1% | 7086 | 46% | 70% | -0.04% |
| up 1-2% | 3292 | 50% | 46% | +0.05% |
| up 2-4% | 1018 | 53% | 24% | +0.22% |
| up 4+% | 322 | 39% | 9% | -0.49% |

Futures open interest source: end-of-day snapshot of 2026-11-26.

## Swing candidates (rules v3)

Strong 6- and 12-month momentum adjusted for volatility (NSE's momentum-index method), within 15% of the
52-week high, in a tight base or an orderly pullback. Enter only on a close above the trigger; stop below
the base. Shorts (weak momentum near the 52-week low) need futures or puts.

| Stock | Dir | Momentum pct | Setup | Volume drying up | Close | Trigger | Stop | Target 2R | Risk (ATRs) | From 52w high | 5d | Options IV vs realised | Expiry |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DIVISLAB | UP | 100 | tight base | no | 11631.0 | 11821.4 | 10954.0 | 13556.0 | 2.3 | -2% | +5.3% | 0.77 | 2026-12-29 |
| ATHERENERG | UP | 99 | tight base | yes | 1906.0 | 2028.0 | 1861.0 | 2362.0 | 2.6 | -6% | +0.3% | 1.09 | 2026-12-29 |
| ANANDRATHI | UP | 99 | tight base | yes | 2410.0 | 2431.6 | 2344.3 | 2606.2 | 2.9 | -1% | +1.5% | 1.44 | 2026-12-29 |
| ACUTAAS | UP | 98 | tight base | yes | 4079.9 | 4145.1 | 3720.2 | 4995.0 | 2.8 | -1% | +2.2% | 0.90 | 2026-12-29 |
| NAVINFLUOR | UP | 97 | tight base | no | 10270.0 | 10393.7 | 9712.5 | 11756.0 | 2.0 | -1% | -0.1% | 0.91 | 2026-12-29 |
| AUROPHARMA | UP | 97 | tight base | no | 1811.0 | 1855.8 | 1778.0 | 2011.5 | 2.0 | -3% | +0.8% | 0.98 | 2026-12-29 |
| FEDERALBNK | UP | 96 | tight base | no | 356.9 | 377.1 | 353.6 | 424.1 | 2.6 | -5% | -1.0% | 0.87 | 2026-12-29 |
| MCX | UP | 95 | tight base | no | 3835.0 | 3879.1 | 3455.0 | 4727.4 | 3.0 | -1% | +6.0% | 0.76 | 2026-12-29 |
| INDHOTEL | UP | 95 | tight base | yes | 886.7 | 928.0 | 869.4 | 1045.3 | 2.6 | -4% | +1.3% | 1.01 | 2026-12-29 |
| NYKAA | UP | 94 | tight base | yes | 353.0 | 369.2 | 351.8 | 404.0 | 2.0 | -4% | +0.3% | 1.22 | 2026-12-29 |
| PAYTM | UP | 94 | pullback | no | 1768.9 | 1815.8 | 1664.3 | 2118.9 | 2.2 | -10% | -6.4% | 0.76 | 2026-12-29 |
| BOSCHLTD | UP | 94 | tight base | no | 48830.0 | 51078.2 | 48370.0 | 56494.8 | 2.5 | -7% | -0.7% | 0.86 | 2026-12-29 |
| SWIGGY | DOWN | 2 | tight base | no | 182.9 | 175.5 | 195.3 | 135.8 | 2.9 | -57% | +1.4% | 0.99 | 2026-12-29 |
| MAZDOCK | DOWN | 4 | tight base | yes | 1817.0 | 1786.9 | 1927.3 | 1506.2 | 3.4 | -36% | -0.3% | 1.30 | 2026-12-29 |
| TIINDIA | DOWN | 5 | tight base | no | 2212.2 | 2173.6 | 2349.0 | 1822.8 | 2.3 | -34% | +0.2% | 1.00 | 2026-12-29 |
| ONGC | DOWN | 8 | tight base | no | 222.9 | 219.2 | 227.8 | 202.1 | 2.2 | -28% | -0.9% | 0.78 | 2026-12-29 |
| GODFRYPHLP | DOWN | 11 | tight base | yes | 1764.9 | 1729.9 | 1890.4 | 1408.9 | 3.1 | -41% | +0.4% | 1.53 | 2026-12-29 |
| WAAREEENER | DOWN | 12 | tight base | yes | 2385.2 | 2356.6 | 2629.9 | 1810.1 | 3.3 | -33% | -0.3% | 0.95 | 2026-12-29 |

## Industry strength among F&O stocks (source: NSE Nifty 500 list)

Ranked by median 20-session strength against Nifty. Industries need 3+ F&O members.

| Rank | Industry | Members | Median last day | Median 5d | Median vs Nifty 20d | Share up 5d |
|---|---|---|---|---|---|---|
| 1 | Realty | 6 | +3.2% | +5.8% | +9.2% | 100% |
| 2 | Financial Services | 55 | -0.3% | +1.5% | +0.5% | 69% |
| 3 | Fast Moving Consumer Goods | 14 | -1.1% | +3.4% | +0.4% | 100% |
| 4 | Services | 5 | -1.1% | +0.5% | -1.2% | 60% |
| 5 | Consumer Durables | 10 | -1.7% | +3.8% | -2.7% | 70% |
| 6 | Oil Gas & Consumable Fuels | 9 | +0.3% | +0.2% | -3.1% | 56% |
| 7 | Construction Materials | 4 | +0.0% | +2.2% | -3.3% | 100% |
| 8 | Consumer Services | 9 | -1.1% | +1.4% | -4.8% | 100% |
| 9 | Healthcare | 17 | +0.1% | +2.3% | -5.0% | 82% |
| 10 | Construction | 3 | -0.6% | -1.0% | -5.9% | 0% |
| 11 | Automobile and Auto Components | 16 | -0.2% | +3.1% | -6.0% | 88% |
| 12 | Chemicals | 7 | +0.9% | -0.1% | -7.0% | 43% |
| 13 | Power | 8 | +0.1% | -2.0% | -8.2% | 38% |
| 14 | Information Technology | 13 | +1.6% | +5.9% | -9.6% | 85% |
| 15 | Metals & Mining | 10 | +1.1% | -1.2% | -11.8% | 20% |
| 16 | Telecommunication | 3 | -0.7% | -3.2% | -12.4% | 0% |
| 17 | Capital Goods | 27 | +0.4% | +0.3% | -16.2% | 52% |

## Industry and peers of focus and swing stocks

Peers = F&O stocks whose daily moves (market move removed) tracked this stock most closely over 60 sessions.
When a stock has news, check whether its peers have moved yet.

| Stock | Industry (rank) | Peers (correlation) | Peers' last day |
|---|---|---|---|
| PRESTIGE | Realty (1) | GODREJPROP 0.68, DLF 0.60, OBEROIRLTY 0.58, KFINTECH 0.56, CAMS 0.55 | GODREJPROP +4.4%, DLF +1.6%, OBEROIRLTY +2.0%, KFINTECH +6.5%, CAMS +4.0% |
| KFINTECH | Financial Services (2) | CAMS 0.67, GODREJPROP 0.57, PRESTIGE 0.56, HDFCAMC 0.54, GODFRYPHLP 0.53 | CAMS +4.0%, GODREJPROP +4.4%, PRESTIGE +8.7%, HDFCAMC +2.0%, GODFRYPHLP +0.2% |
| TCS | Information Technology (14) | WIPRO 0.77, TECHM 0.76, HCLTECH 0.71, INFY 0.68, LTM 0.56 | WIPRO +4.0%, TECHM +3.0%, HCLTECH +6.4%, INFY +4.7%, LTM +3.2% |
| TORNTPHARM | Healthcare (9) | MANKIND 0.53 | MANKIND +0.0% |
| LODHA | Realty (1) | OBEROIRLTY 0.66, GODREJPROP 0.65, DLF 0.58, MUTHOOTFIN 0.53, RADICO 0.52 | OBEROIRLTY +2.0%, GODREJPROP +4.4%, DLF +1.6%, MUTHOOTFIN +0.3%, RADICO -0.6% |
| BRITANNIA | Fast Moving Consumer Goods (3) | HINDUNILVR 0.60, COLPAL 0.57, ASTRAL 0.54, MARICO 0.52, DABUR 0.48 | HINDUNILVR -0.5%, COLPAL -1.4%, ASTRAL +1.0%, MARICO +0.4%, DABUR -2.7% |
| UJJIVANSFB | - | SHRIRAMFIN 0.66, AUBANK 0.52 | SHRIRAMFIN -2.8%, AUBANK -2.4% |
| MCX | Financial Services (2) | - | - |
| ZYDUSLIFE | Healthcare (9) | CIPLA 0.47 | CIPLA +1.2% |
| WIPRO | Information Technology (14) | TCS 0.77, TECHM 0.70, INFY 0.69, HCLTECH 0.59, LTM 0.57 | TCS +4.9%, TECHM +3.0%, INFY +4.7%, HCLTECH +6.4%, LTM +3.2% |
| MAHABANK | Financial Services (2) | BANKINDIA 0.60, KARURVYSYA 0.53, CANBK 0.51, PNB 0.47, UNIONBANK 0.46 | BANKINDIA +0.2%, KARURVYSYA -2.3%, CANBK -0.8%, PNB -0.8%, UNIONBANK -1.6% |
| GODREJPROP | Realty (1) | PRESTIGE 0.68, LODHA 0.65, OBEROIRLTY 0.63, DLF 0.61, KFINTECH 0.57 | PRESTIGE +8.7%, LODHA +4.9%, OBEROIRLTY +2.0%, DLF +1.6%, KFINTECH +6.5% |
| DABUR | Fast Moving Consumer Goods (3) | HINDUNILVR 0.62, COLPAL 0.58, GODREJCP 0.57, BRITANNIA 0.48, PIIND 0.47 | HINDUNILVR -0.5%, COLPAL -1.4%, GODREJCP -1.6%, BRITANNIA +2.1%, PIIND +1.0% |
| SHRIRAMFIN | Financial Services (2) | UJJIVANSFB 0.66, AUBANK 0.60, CHOLAFIN 0.57, SBICARD 0.56, DLF 0.51 | UJJIVANSFB -6.4%, AUBANK -2.4%, CHOLAFIN -1.3%, SBICARD -0.5%, DLF +1.6% |
| ANANDRATHI | Financial Services (2) | - | - |
| ENRIN | Capital Goods (17) | GVT&D 0.73, POWERINDIA 0.70, SIEMENS 0.67, CGPOWER 0.67, BHEL 0.62 | GVT&D +2.2%, POWERINDIA +1.9%, SIEMENS -0.1%, CGPOWER +0.4%, BHEL +1.3% |
| HDFCBANK | Financial Services (2) | - | - |
| DLF | Realty (1) | OBEROIRLTY 0.69, GODREJPROP 0.61, PRESTIGE 0.60, PHOENIXLTD 0.60, LODHA 0.58 | OBEROIRLTY +2.0%, GODREJPROP +4.4%, PRESTIGE +8.7%, PHOENIXLTD +0.2%, LODHA +4.9% |
| APARINDS | Capital Goods (17) | ENRIN 0.62, ASTRAL 0.60, BEL 0.55, CGPOWER 0.55, GVT&D 0.52 | ENRIN +3.0%, ASTRAL +1.0%, BEL +0.1%, CGPOWER +0.4%, GVT&D +2.2% |
| APLAPOLLO | Capital Goods (17) | TATASTEEL 0.58 | TATASTEEL +2.7% |
| DIVISLAB | Healthcare (9) | LAURUSLABS 0.56, SUNPHARMA 0.52, AUROPHARMA 0.50, MANKIND 0.46 | LAURUSLABS +1.8%, SUNPHARMA +0.8%, AUROPHARMA -1.7%, MANKIND +0.0% |
| ATHERENERG | Automobile and Auto Components (11) | POLYCAB 0.50, NAVINFLUOR 0.47 | POLYCAB -0.4%, NAVINFLUOR +3.1% |
| ACUTAAS | Healthcare (9) | SONACOMS 0.46, CONCOR 0.45 | SONACOMS -0.2%, CONCOR -1.1% |
| NAVINFLUOR | Chemicals (12) | FORCEMOT 0.52, SONACOMS 0.52, ATHERENERG 0.47, KFINTECH 0.46, CDSL 0.46 | FORCEMOT -0.1%, SONACOMS -0.2%, ATHERENERG +1.8%, KFINTECH +6.5%, CDSL +2.0% |
| AUROPHARMA | Healthcare (9) | DIVISLAB 0.50, NYKAA 0.45 | DIVISLAB -0.7%, NYKAA -1.4% |
| FEDERALBNK | Financial Services (2) | PNB 0.50, BANKBARODA 0.46, SBIN 0.46 | PNB -0.8%, BANKBARODA -0.7%, SBIN -0.1% |
| INDHOTEL | Consumer Services (8) | - | - |
| NYKAA | Consumer Services (8) | POLYCAB 0.56, PREMIERENE 0.48, GVT&D 0.48, CGPOWER 0.46, AUROPHARMA 0.45 | POLYCAB -0.4%, PREMIERENE -1.4%, GVT&D +2.2%, CGPOWER +0.4%, AUROPHARMA -1.7% |
| PAYTM | Financial Services (2) | - | - |
| BOSCHLTD | Automobile and Auto Components (11) | MOTHERSON 0.63, TVSMOTOR 0.49, HDFCAMC 0.48, SUZLON 0.47, BAJAJ-AUTO 0.46 | MOTHERSON -1.0%, TVSMOTOR -1.3%, HDFCAMC +2.0%, SUZLON +0.4%, BAJAJ-AUTO -0.2% |
| SWIGGY | Consumer Services (8) | KFINTECH 0.45, JIOFIN 0.45 | KFINTECH +6.5%, JIOFIN +1.9% |
| MAZDOCK | Capital Goods (17) | BDL 0.71, WAAREEENER 0.57, RVNL 0.56, HINDZINC 0.50, AMBUJACEM 0.48 | BDL +0.7%, WAAREEENER +0.2%, RVNL +1.1%, HINDZINC +1.3%, AMBUJACEM -0.3% |
| TIINDIA | Automobile and Auto Components (11) | CGPOWER 0.65, ASTRAL 0.55, BHEL 0.53, MOTHERSON 0.52, NBCC 0.52 | CGPOWER +0.4%, ASTRAL +1.0%, BHEL +1.3%, MOTHERSON -1.0%, NBCC -0.6% |
| ONGC | Oil Gas & Consumable Fuels (6) | OIL 0.61, RELIANCE 0.48, PAGEIND 0.45 | OIL +0.5%, RELIANCE +1.6%, PAGEIND +0.2% |
| GODFRYPHLP | Fast Moving Consumer Goods (3) | LICI 0.64, RVNL 0.57, CONCOR 0.57, COLPAL 0.56, UPL 0.54 | LICI +0.4%, RVNL +1.1%, CONCOR -1.1%, COLPAL -1.4%, UPL +1.9% |
| WAAREEENER | Capital Goods (17) | MAZDOCK 0.57, RVNL 0.55, PREMIERENE 0.51, BHEL 0.45, IRFC 0.45 | MAZDOCK +1.0%, RVNL +1.1%, PREMIERENE -1.4%, BHEL +1.3%, IRFC +1.5% |

## Focus list: stocks on two or more lists below

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRESTIGE | 1832.1 | +8.7% | +2.4 | 8.5x | 0.95 | +10.5% | +31.6% | 3.3% | +6% long build-up | -0.1% | 2.2% | -0% | up 20d-up |
| KFINTECH | 995.0 | +6.5% | +2.0 | 4.5x | 0.90 | +6.7% | +16.4% | 3.0% | +10% long build-up | -0.1% | 2.3% | -11% | up 20d-up |
| TCS | 2640.3 | +4.9% | +1.8 | 1.7x | 1.00 | +11.0% | +7.3% | 2.5% | +10% long build-up | -0.1% | 1.9% | -21% | up 20d-up |
| TORNTPHARM | 5019.1 | +2.5% | +1.3 | 5.0x | 0.91 | +8.9% | +10.1% | 1.9% | +4% long build-up | -0.1% | 1.4% | -4% | mixed 20d-up |
| LODHA | 1261.2 | +4.9% | +1.3 | 2.0x | 0.89 | +5.3% | +25.2% | 3.6% | +4% long build-up | -0.2% | 2.3% | -6% | up 20d-up |
| BRITANNIA | 5185.0 | +2.1% | +0.8 | 2.8x | 0.88 | +10.9% | +13.5% | 2.6% | +6% long build-up | -0.1% | 1.5% | -17% | up 20d-up |
| UJJIVANSFB | 56.9 | -6.4% | -1.9 | 1.3x | 0.07 | -7.2% | +4.3% | 3.5% | +9% short build-up | -0.1% | 2.8% | -23% | down |
| MCX | 3835.0 | +7.6% | +1.9 | 1.9x | 0.89 | +6.0% | +20.6% | 3.7% | +4% long build-up | -0.1% | 2.4% | -1% | up 20d-up |
| ZYDUSLIFE | 1194.2 | -3.4% | -1.6 | 1.6x | 0.09 | -0.7% | +1.6% | 2.2% | +15% short build-up | -0.1% | 1.8% | -6% | mixed |
| WIPRO | 196.5 | +4.0% | +1.6 | 1.9x | 0.87 | +6.2% | +6.5% | 2.5% | -0% | -0.1% | 1.9% | -28% | up |
| MAHABANK | 94.2 | -4.6% | -1.5 | 0.8x | 0.05 | -1.9% | +17.8% | 3.2% | +13% short build-up | -0.1% | 2.4% | -6% | up |
| GODREJPROP | 2004.3 | +4.4% | +1.3 | 1.4x | 0.87 | +6.8% | +26.3% | 3.2% | +2% | -0.2% | 1.9% | -8% | up 20d-up |
| DABUR | 418.5 | -2.7% | -1.1 | 1.4x | 0.25 | +10.3% | +16.2% | 2.5% | +12% short build-up | -0.1% | 1.7% | -22% | up |
| SHRIRAMFIN | 961.9 | -2.8% | -1.0 | 1.4x | 0.17 | -0.8% | +15.5% | 2.8% | +17% short build-up | -0.2% | 2.1% | -17% | mixed |
| ANANDRATHI | 2410.0 | +1.3% | +1.0 | 3.2x | 0.62 | +1.5% | +6.4% | 1.2% | +4% long build-up | -0.0% | 1.3% | -1% | up |
| ENRIN | 3058.0 | +3.0% | +0.8 | 6.1x | 0.01 | +3.1% | +7.7% | 3.8% | +20% long build-up | +0.0% | 2.6% | -23% | mixed |
| HDFCBANK | 862.0 | +1.9% | +0.7 | 1.8x | 0.65 | +6.7% | +25.8% | 2.6% | +3% long build-up | -0.2% | 1.6% | -15% | up 20d-up |
| DLF | 807.8 | +1.6% | +0.7 | 1.4x | 0.77 | +5.7% | +21.2% | 2.3% | +2% | -0.1% | 1.7% | -1% | up 20d-up |
| APARINDS | 14200.0 | -0.3% | -0.1 | 0.6x | 0.00 | +1.5% | -7.9% | 4.3% | +204% short build-up | +0.0% | 3.5% | -26% | down |
| APLAPOLLO | 1481.5 | +0.4% | +0.1 | 2.2x | 0.48 | -31.4% | -31.6% | 7.0% | -1% | -0.1% | 2.8% | -36% | down |

## Biggest up-moves last session (in units of the stock's normal daily range)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRESTIGE | 1832.1 | +8.7% | +2.4 | 8.5x | 0.95 | +10.5% | +31.6% | 3.3% | +6% long build-up | -0.1% | 2.2% | -0% | up 20d-up |
| HCLTECH | 1468.6 | +6.4% | +2.4 | 1.8x | 1.00 | +9.2% | +4.9% | 2.5% | +4% long build-up | -0.1% | - | -18% | up |
| KFINTECH | 995.0 | +6.5% | +2.0 | 4.5x | 0.90 | +6.7% | +16.4% | 3.0% | +10% long build-up | -0.1% | 2.3% | -11% | up 20d-up |
| MCX | 3835.0 | +7.6% | +1.9 | 1.9x | 0.89 | +6.0% | +20.6% | 3.7% | +4% long build-up | -0.1% | 2.4% | -1% | up 20d-up |
| BSE | 3990.4 | +5.7% | +1.9 | 1.8x | 0.96 | +6.2% | +14.5% | 2.9% | +4% long build-up | -0.1% | - | -10% | up |
| TCS | 2640.3 | +4.9% | +1.8 | 1.7x | 1.00 | +11.0% | +7.3% | 2.5% | +10% long build-up | -0.1% | 1.9% | -21% | up 20d-up |
| INFY | 1183.0 | +4.7% | +1.8 | 1.6x | 0.95 | +6.7% | +5.3% | 2.5% | +6% long build-up | -0.1% | - | -32% | up |
| WIPRO | 196.5 | +4.0% | +1.6 | 1.9x | 0.87 | +6.2% | +6.5% | 2.5% | -0% | -0.1% | 1.9% | -28% | up |
| GODREJPROP | 2004.3 | +4.4% | +1.3 | 1.4x | 0.87 | +6.8% | +26.3% | 3.2% | +2% | -0.2% | 1.9% | -8% | up 20d-up |
| TORNTPHARM | 5019.1 | +2.5% | +1.3 | 5.0x | 0.91 | +8.9% | +10.1% | 1.9% | +4% long build-up | -0.1% | 1.4% | -4% | mixed 20d-up |

## Biggest down-moves last session

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UJJIVANSFB | 56.9 | -6.4% | -1.9 | 1.3x | 0.07 | -7.2% | +4.3% | 3.5% | +9% short build-up | -0.1% | 2.8% | -23% | down |
| ZYDUSLIFE | 1194.2 | -3.4% | -1.6 | 1.6x | 0.09 | -0.7% | +1.6% | 2.2% | +15% short build-up | -0.1% | 1.8% | -6% | mixed |
| MAHABANK | 94.2 | -4.6% | -1.5 | 0.8x | 0.05 | -1.9% | +17.8% | 3.2% | +13% short build-up | -0.1% | 2.4% | -6% | up |
| ASIANPAINT | 2543.0 | -3.0% | -1.3 | 0.9x | 0.03 | -1.4% | +11.3% | 2.4% | +2% | -0.1% | - | -15% | up |
| NESTLEIND | 1320.3 | -2.8% | -1.2 | 1.2x | 0.01 | +3.0% | +13.0% | 2.4% | +6% short build-up | -0.1% | - | -15% | mixed |
| DABUR | 418.5 | -2.7% | -1.1 | 1.4x | 0.25 | +10.3% | +16.2% | 2.5% | +12% short build-up | -0.1% | 1.7% | -22% | up |
| BAJFINANCE | 1097.8 | -3.0% | -1.1 | 0.8x | 0.00 | +0.4% | +19.7% | 2.9% | +3% | -0.2% | - | -7% | up |
| SHRIRAMFIN | 961.9 | -2.8% | -1.0 | 1.4x | 0.17 | -0.8% | +15.5% | 2.8% | +17% short build-up | -0.2% | 2.1% | -17% | mixed |
| DMART | 3533.0 | -1.6% | -1.0 | 0.7x | 0.23 | +2.1% | +12.7% | 1.7% | +2% | -0.1% | - | -24% | mixed |
| IOC | 144.4 | -2.3% | -0.9 | 0.7x | 0.12 | +0.4% | +11.0% | 2.5% | +2% | -0.1% | - | -24% | up NR7 |

## Unusual volume last session (against its own 20-day average)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRESTIGE | 1832.1 | +8.7% | +2.4 | 8.5x | 0.95 | +10.5% | +31.6% | 3.3% | +6% long build-up | -0.1% | 2.2% | -0% | up 20d-up |
| ENRIN | 3058.0 | +3.0% | +0.8 | 6.1x | 0.01 | +3.1% | +7.7% | 3.8% | +20% long build-up | +0.0% | 2.6% | -23% | mixed |
| TORNTPHARM | 5019.1 | +2.5% | +1.3 | 5.0x | 0.91 | +8.9% | +10.1% | 1.9% | +4% long build-up | -0.1% | 1.4% | -4% | mixed 20d-up |
| KFINTECH | 995.0 | +6.5% | +2.0 | 4.5x | 0.90 | +6.7% | +16.4% | 3.0% | +10% long build-up | -0.1% | 2.3% | -11% | up 20d-up |
| CONCOR | 421.0 | -1.1% | -0.5 | 3.5x | 0.00 | -3.6% | +0.7% | 2.4% | +7% short build-up | -0.1% | - | -23% | down |
| ANANDRATHI | 2410.0 | +1.3% | +1.0 | 3.2x | 0.62 | +1.5% | +6.4% | 1.2% | +4% long build-up | -0.0% | 1.3% | -1% | up |
| BRITANNIA | 5185.0 | +2.1% | +0.8 | 2.8x | 0.88 | +10.9% | +13.5% | 2.6% | +6% long build-up | -0.1% | 1.5% | -17% | up 20d-up |
| COFORGE | 2000.0 | -2.9% | -0.8 | 2.7x | 0.31 | -2.4% | +1.9% | 3.9% | +7% short build-up | -0.1% | - | -8% | mixed |
| VMM | 96.0 | +1.3% | +0.5 | 2.5x | 0.51 | +6.5% | +9.2% | 2.8% | +2% | -0.1% | - | -31% | mixed |
| APLAPOLLO | 1481.5 | +0.4% | +0.1 | 2.2x | 0.48 | -31.4% | -31.6% | 7.0% | -1% | -0.1% | 2.8% | -36% | down |
| LODHA | 1261.2 | +4.9% | +1.3 | 2.0x | 0.89 | +5.3% | +25.2% | 3.6% | +4% long build-up | -0.2% | 2.3% | -6% | up 20d-up |
| WIPRO | 196.5 | +4.0% | +1.6 | 1.9x | 0.87 | +6.2% | +6.5% | 2.5% | -0% | -0.1% | 1.9% | -28% | up |

## Closed above the 20-day high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRESTIGE | 1832.1 | +8.7% | +2.4 | 8.5x | 0.95 | +10.5% | +31.6% | 3.3% | +6% long build-up | -0.1% | 2.2% | -0% | up 20d-up |
| TORNTPHARM | 5019.1 | +2.5% | +1.3 | 5.0x | 0.91 | +8.9% | +10.1% | 1.9% | +4% long build-up | -0.1% | 1.4% | -4% | mixed 20d-up |
| KFINTECH | 995.0 | +6.5% | +2.0 | 4.5x | 0.90 | +6.7% | +16.4% | 3.0% | +10% long build-up | -0.1% | 2.3% | -11% | up 20d-up |
| BRITANNIA | 5185.0 | +2.1% | +0.8 | 2.8x | 0.88 | +10.9% | +13.5% | 2.6% | +6% long build-up | -0.1% | 1.5% | -17% | up 20d-up |
| LODHA | 1261.2 | +4.9% | +1.3 | 2.0x | 0.89 | +5.3% | +25.2% | 3.6% | +4% long build-up | -0.2% | 2.3% | -6% | up 20d-up |
| MCX | 3835.0 | +7.6% | +1.9 | 1.9x | 0.89 | +6.0% | +20.6% | 3.7% | +4% long build-up | -0.1% | 2.4% | -1% | up 20d-up |
| HDFCBANK | 862.0 | +1.9% | +0.7 | 1.8x | 0.65 | +6.7% | +25.8% | 2.6% | +3% long build-up | -0.2% | 1.6% | -15% | up 20d-up |
| OBEROIRLTY | 1905.2 | +2.0% | +0.7 | 1.7x | 0.76 | +5.8% | +19.0% | 2.7% | +5% long build-up | -0.1% | - | -4% | up 20d-up |
| TCS | 2640.3 | +4.9% | +1.8 | 1.7x | 1.00 | +11.0% | +7.3% | 2.5% | +10% long build-up | -0.1% | 1.9% | -21% | up 20d-up |
| DLF | 807.8 | +1.6% | +0.7 | 1.4x | 0.77 | +5.7% | +21.2% | 2.3% | +2% | -0.1% | 1.7% | -1% | up 20d-up |

## Closed below the 20-day low

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KEI | 3646.0 | -0.2% | -0.0 | 1.9x | 0.07 | -2.1% | -5.5% | 3.9% | +7% short build-up | -0.1% | - | -38% | down 20d-down |
| PREMIERENE | 803.5 | -1.4% | -0.4 | 1.1x | 0.22 | -3.5% | -4.9% | 3.5% | +1% | -0.1% | - | -29% | down 20d-down |

## Futures: price up with open interest up (long build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ACUTAAS | 4079.9 | +2.2% | +0.6 | 0.8x | 0.69 | +2.2% | +10.0% | 3.7% | +235% long build-up | -0.1% | 2.3% | -1% | up |
| ENRIN | 3058.0 | +3.0% | +0.8 | 6.1x | 0.01 | +3.1% | +7.7% | 3.8% | +20% long build-up | +0.0% | 2.6% | -23% | mixed |
| TCS | 2640.3 | +4.9% | +1.8 | 1.7x | 1.00 | +11.0% | +7.3% | 2.5% | +10% long build-up | -0.1% | 1.9% | -21% | up 20d-up |
| KFINTECH | 995.0 | +6.5% | +2.0 | 4.5x | 0.90 | +6.7% | +16.4% | 3.0% | +10% long build-up | -0.1% | 2.3% | -11% | up 20d-up |
| COROMANDEL | 1942.3 | +0.1% | +0.0 | 0.9x | 0.21 | -0.8% | +14.0% | 3.2% | +9% long build-up | -0.1% | - | -22% | up |
| LICI | 410.0 | +0.4% | +0.2 | 1.4x | 0.31 | +2.5% | +4.7% | 2.0% | +8% long build-up | -0.1% | - | -11% | up |
| ANGELONE | 358.0 | +2.5% | +0.6 | 0.9x | 0.75 | +5.8% | +22.4% | 4.2% | +6% long build-up | -0.2% | - | -6% | up |
| BRITANNIA | 5185.0 | +2.1% | +0.8 | 2.8x | 0.88 | +10.9% | +13.5% | 2.6% | +6% long build-up | -0.1% | 1.5% | -17% | up 20d-up |

## Futures: price down with open interest up (short build-up)

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APARINDS | 14200.0 | -0.3% | -0.1 | 0.6x | 0.00 | +1.5% | -7.9% | 4.3% | +204% short build-up | +0.0% | 3.5% | -26% | down |
| SHRIRAMFIN | 961.9 | -2.8% | -1.0 | 1.4x | 0.17 | -0.8% | +15.5% | 2.8% | +17% short build-up | -0.2% | 2.1% | -17% | mixed |
| ZYDUSLIFE | 1194.2 | -3.4% | -1.6 | 1.6x | 0.09 | -0.7% | +1.6% | 2.2% | +15% short build-up | -0.1% | 1.8% | -6% | mixed |
| MAHABANK | 94.2 | -4.6% | -1.5 | 0.8x | 0.05 | -1.9% | +17.8% | 3.2% | +13% short build-up | -0.1% | 2.4% | -6% | up |
| CUB | 239.0 | -3.2% | -0.9 | 0.6x | 0.15 | +2.9% | +11.2% | 3.7% | +12% short build-up | -0.1% | - | -6% | up |
| DABUR | 418.5 | -2.7% | -1.1 | 1.4x | 0.25 | +10.3% | +16.2% | 2.5% | +12% short build-up | -0.1% | 1.7% | -22% | up |
| UJJIVANSFB | 56.9 | -6.4% | -1.9 | 1.3x | 0.07 | -7.2% | +4.3% | 3.5% | +9% short build-up | -0.1% | 2.8% | -23% | down |
| DIXON | 12718.0 | -2.0% | -0.7 | 1.1x | 0.16 | +0.8% | +11.6% | 3.1% | +8% short build-up | -0.1% | - | -18% | mixed |

## Strongest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRESTIGE | 1832.1 | +8.7% | +2.4 | 8.5x | 0.95 | +10.5% | +31.6% | 3.3% | +6% long build-up | -0.1% | 2.2% | -0% | up 20d-up |
| MAXHEALTH | 1081.2 | +0.5% | +0.2 | 0.5x | 0.71 | +5.7% | +27.0% | 2.6% | -1% | -0.1% | - | -9% | up |
| UNOMINDA | 1390.0 | +1.1% | +0.4 | 0.5x | 0.97 | +1.5% | +26.4% | 3.0% | +1% | -0.2% | - | -1% | up |
| GODREJPROP | 2004.3 | +4.4% | +1.3 | 1.4x | 0.87 | +6.8% | +26.3% | 3.2% | +2% | -0.2% | 1.9% | -8% | up 20d-up |
| HDFCBANK | 862.0 | +1.9% | +0.7 | 1.8x | 0.65 | +6.7% | +25.8% | 2.6% | +3% long build-up | -0.2% | 1.6% | -15% | up 20d-up |
| MOTILALOFS | 1215.2 | -1.2% | -0.3 | 0.6x | 0.00 | -1.1% | +25.5% | 3.9% | +8% short build-up | -0.2% | - | -5% | up |
| KALYANKJIL | 639.8 | +0.5% | +0.1 | 0.5x | 0.38 | -1.6% | +25.4% | 5.8% | +3% long build-up | -0.1% | - | -12% | up NR7 |
| LODHA | 1261.2 | +4.9% | +1.3 | 2.0x | 0.89 | +5.3% | +25.2% | 3.6% | +4% long build-up | -0.2% | 2.3% | -6% | up 20d-up |

## Weakest against Nifty over 20 sessions

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| APLAPOLLO | 1481.5 | +0.4% | +0.1 | 2.2x | 0.48 | -31.4% | -31.6% | 7.0% | -1% | -0.1% | 2.8% | -36% | down |
| PIIND | 1591.2 | +1.0% | +0.4 | 0.4x | 0.51 | -2.0% | -22.6% | 2.6% | +0% | +0.0% | - | -54% | down |
| KAYNES | 2703.3 | +0.2% | +0.0 | 0.6x | 0.58 | -6.2% | -13.9% | 5.3% | +4% long build-up | -0.1% | - | -55% | down NR7 |
| CUMMINSIND | 4100.9 | +0.8% | +0.3 | 0.6x | 0.25 | +2.4% | -11.2% | 3.1% | +1% | +0.0% | - | -33% | down |
| INOXWIND | 53.0 | +1.2% | +0.2 | 0.8x | 0.35 | -7.8% | -10.2% | 5.0% | +2% | -0.2% | - | -63% | down NR7 |
| NATIONALUM | 294.9 | +2.5% | +0.7 | 1.4x | 0.49 | -4.3% | -8.8% | 3.7% | +1% | -0.1% | - | -34% | down NR7 |
| PAGEIND | 30860.0 | +0.2% | +0.1 | 0.5x | 0.78 | +0.2% | -8.8% | 3.9% | +2% | -0.1% | - | -30% | down NR7 |
| APARINDS | 14200.0 | -0.3% | -0.1 | 0.6x | 0.00 | +1.5% | -7.9% | 4.3% | +204% short build-up | +0.0% | 3.5% | -26% | down |

## Within 2% of the 52-week high

| Stock | Close | Last day | In ATRs | Volume | Close in range | 5d | 20d | ATR | Futures OI | Est. gap | Options: 1-day move | From 52w high | Trend, flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MARICO | 939.1 | +0.4% | +0.2 | 0.8x | 1.00 | +3.6% | +22.0% | 1.8% | +3% | -0.1% | - | +0% | up 20d-up |
| TECHM | 1854.7 | +3.0% | +1.3 | 1.0x | 0.94 | +6.0% | +4.4% | 2.2% | +1% | -0.1% | - | -0% | up |
| PRESTIGE | 1832.1 | +8.7% | +2.4 | 8.5x | 0.95 | +10.5% | +31.6% | 3.3% | +6% long build-up | -0.1% | 2.2% | -0% | up 20d-up |
| LAURUSLABS | 2505.0 | +1.8% | +0.5 | 1.1x | 0.83 | +7.9% | +14.8% | 3.3% | +2% | -0.0% | - | -0% | up 20d-up |
| GLENMARK | 2740.2 | +0.8% | +0.3 | 0.5x | 0.72 | +3.6% | +19.1% | 3.0% | +2% | -0.1% | - | -0% | up 20d-up |
| DLF | 807.8 | +1.6% | +0.7 | 1.4x | 0.77 | +5.7% | +21.2% | 2.3% | +2% | -0.1% | 1.7% | -1% | up 20d-up |
| MANKIND | 2685.0 | +0.0% | +0.0 | 0.5x | 0.40 | +2.3% | +7.8% | 2.2% | +1% | -0.0% | - | -1% | up |
| ANANDRATHI | 2410.0 | +1.3% | +1.0 | 3.2x | 0.62 | +1.5% | +6.4% | 1.2% | +4% long build-up | -0.0% | 1.3% | -1% | up |

## Reading the columns

- In ATRs: last day's move divided by the stock's average true range. Above 1.5 is an unusually large day.
- Close in range: 1.00 closed at the day's high, 0.00 at the low.
- Est. gap: the stock's beta times the expected index gap. It ignores stock news, which usually matters more.
- Options: 1-day move: the daily move implied by the nearest at-the-money straddle. Shown for focus and swing stocks.
- Options IV vs realised: at-the-money implied volatility divided by the stock's 20-day realised volatility.
  Above about 1.6 the options are expensive (often before results) and buying them needs a bigger move.
- Momentum pct: rank 0-100 across F&O stocks on volatility-adjusted 6- and 12-month returns.
- The full per-stock data is in momentum/latest.json.
