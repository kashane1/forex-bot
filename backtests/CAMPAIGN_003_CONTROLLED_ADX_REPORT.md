# CAMPAIGN 003 — Controlled ADX-Filtered Trend Following

> **Result: REJECT.** Real OANDA practice H4 data, frozen baseline +
> H4-only + 6-pair universe + ADX-14>25 gate. One controlled hypothesis,
> no optimizer, RiskEngine wired in. This campaign does **not** authorize
> paper-loop, demo-loop, or any order submission.

## Provenance

- **Git commit:** `6b32972f454928abc121cd23401c94afc102ed5f`
- **Working tree dirty at report time:** YES
- **Config:** [`configs/campaign_003_controlled_adx.yaml`](../configs/campaign_003_controlled_adx.yaml)
- **Config hash:** `a4f1eb90d749001b09fcc32fae8438ef48a588728709ddcc5a32e3fcc8a08262`
- **Strategy version:** `trend_following 0.2.0-c003`
- **Data source:** real OANDA practice, **reused** from
  `data/campaign_002.sqlite3` (no re-fetch, no synthetic data)
- **RiskEngine invoked:** YES — all 42 runs, `mode="backtest"`
- **Total runs:** 42 (24 baseline + 18 cost stress, H4 only)
- **Runner elapsed:** 333s

### Data provenance (reused CAMPAIGN_002 hashes)

CAMPAIGN_003 **reuses** the real OANDA practice H4 candles fetched for CAMPAIGN_002 (`data/campaign_002.sqlite3`). No re-fetch, no synthetic data. Provenance hashes below are the ones recorded at CAMPAIGN_002 fetch time and match the CAMPAIGN_002 report.

| instrument | gran | source | candles | first | last | raw_sha256 (16) | norm_sha256 (16) |
|---|---|---|---:|---|---|---|---|
| EUR_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `f56b30030f3abbd6` | `f5d1d1b193020976` |
| GBP_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `6ea9b168cf234d1d` | `2c751fec8b0e9f6d` |
| USD_JPY | H4 | oanda-practice | 9935 | 2020-01-01 | 2026-05-19 | `568f4c6104e1f73a` | `64836ea0f08e21c7` |
| AUD_USD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `710f6aed5875367a` | `7a19f3e957ea8ee5` |
| USD_CAD | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `9fe3b74d78c5cc5a` | `dc04b583759ec5c6` |
| USD_CHF | H4 | oanda-practice | 9934 | 2020-01-01 | 2026-05-19 | `46a0f6748c7dfc9c` | `11b0a134792a62a3` |

## Exact rule diff from CAMPAIGN_002

CAMPAIGN_003 = frozen `0.1.0-baseline-frozen` **plus exactly three
pre-committed changes**. Nothing else changed; the ADX threshold was
fixed at 25 before any run and was not swept.

| aspect | CAMPAIGN_002 | CAMPAIGN_003 (`0.2.0-c003`) |
|---|---|---|
| timeframes | H4 **and** H1 | **H4 only** |
| universe | 7 pairs (incl. NZD_USD) | **6 pairs — NZD_USD excluded** (cost structure) |
| entry gate | EMA50/200 + Donchian-20 breakout | same **+ ADX-14 > 25** |
| EMA filter | 50 / 200 | 50 / 200 (unchanged) |
| Donchian | 20, prior bars only | 20, prior bars only (unchanged) |
| stops | 2.0×ATR initial + trailing | 2.0×ATR initial + trailing (unchanged) |
| risk | 0.25% / trade, 1 position | 0.25% / trade, 1 position (unchanged) |
| RiskEngine | wired in | wired in (unchanged) |

## Assumptions

- Fills: bid for long exits / short entries, ask for the opposite;
  `fixed_slippage_pips` + `spread_slippage_multiplier` applied against
  the trade.
- PnL → USD: quote-currency PnL converted at the exit price for
  USD-base pairs (USD_JPY/CAD/CHF); USD-quote pairs already in USD.
- **Financing: NOT modeled in the engine PnL.** A conservative
  financing debit is applied as an after-the-fact overlay (see below).
  Financing remains a hard blocker for any live promotion.
- ADX-14 threshold 25 is the textbook "trend present" level,
  pre-committed, never swept.

## RiskEngine — approvals and rejections

Total rejection rows (one per signal × code) across all 42 runs: **2142**. The permanent per-signal export (`*_risk_rejections.csv`, Step 0) makes every breakdown below reproducible from disk.

**By rejection code:**

| code | count |
|---|---:|
| `SPREAD_TO_ATR` | 796 |
| `SPREAD_TOO_WIDE` | 724 |
| `SESSION_BLOCKED` | 555 |
| `DRAWDOWN_LIMIT` | 67 |

**By pair:**

| pair | rejections |
|---|---:|
| EUR_USD | 572 |
| GBP_USD | 185 |
| USD_JPY | 231 |
| AUD_USD | 222 |
| USD_CAD | 533 |
| USD_CHF | 399 |

**By split:**

| split | rejections |
|---|---:|
| train | 151 |
| validation | 145 |
| test_untouched | 104 |
| full | 1742 |

**By UTC hour:**

| hour | rejections |
|---:|---:|
| 01:00 | 81 |
| 02:00 | 37 |
| 05:00 | 215 |
| 06:00 | 61 |
| 09:00 | 149 |
| 10:00 | 104 |
| 13:00 | 182 |
| 14:00 | 55 |
| 17:00 | 390 |
| 18:00 | 189 |
| 21:00 | 441 |
| 22:00 | 238 |

**By day of week:**

| day | rejections |
|---|---:|
| Mon | 381 |
| Tue | 400 |
| Wed | 513 |
| Thu | 368 |
| Fri | 259 |
| Sun | 221 |

## Metrics by split (H4, base costs)

| split | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| train | 310 | 126 | -1.24% | -2.96% | 0.81 | -0.120 | 33.0% |
| validation | 203 | 127 | -1.34% | -2.00% | 0.69 | -0.111 | 35.2% |
| test_untouched | 101 | 84 | -0.63% | -1.16% | 0.77 | -0.071 | 35.2% |
| full | 628 | 346 | -3.42% | -4.89% | 0.71 | -0.121 | 33.6% |

## Metrics by pair — untouched test split (2025-01-01 → 2026-05-20)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 16 | 12 | -0.16% | -1.03% | 0.92 | -0.037 | 31.2% |
| EUR_USD | 9 | 24 | +0.58% | -0.59% | 1.67 | +0.257 | 44.4% |
| GBP_USD | 19 | 5 | -0.14% | -1.11% | 0.92 | -0.028 | 42.1% |
| USD_CAD | 22 | 28 | -1.21% | -1.21% | 0.31 | -0.159 | 36.4% |
| USD_CHF | 21 | 10 | -1.97% | -2.06% | 0.24 | -0.459 | 28.6% |
| USD_JPY | 14 | 5 | -0.88% | -0.98% | 0.54 | -0.002 | 28.6% |

## Metrics by pair — full window (2020-01-01 → 2026-05-20)

| pair | trades | rejected | return % | max-DD % | PF | expectancy R | win % |
|---|---:|---:|---:|---:|---:|---:|---:|
| AUD_USD | 104 | 38 | -5.24% | -6.43% | 0.57 | -0.204 | 32.7% |
| EUR_USD | 89 | 98 | -2.78% | -4.90% | 0.72 | -0.124 | 33.7% |
| GBP_USD | 106 | 29 | -1.44% | -3.01% | 0.87 | -0.052 | 36.8% |
| USD_CAD | 111 | 77 | -7.37% | -7.41% | 0.42 | -0.207 | 30.6% |
| USD_CHF | 97 | 60 | -3.04% | -4.00% | 0.72 | -0.140 | 33.0% |
| USD_JPY | 121 | 44 | -0.65% | -3.59% | 0.95 | -0.000 | 34.7% |

## Cost stress (full window)

| regime | trades | rejected | avg return % | avg max-DD % | avg PF | avg expectancy R |
|---|---:|---:|---:|---:|---:|---:|
| base | 628 | 346 | -3.42% | -4.89% | 0.71 | -0.121 |
| stress_15x | 628 | 346 | -4.06% | -5.41% | 0.66 | -0.138 |
| stress_2x | 616 | 386 | -4.32% | -5.61% | 0.64 | -0.150 |

## Financing stress overlay

Conservative financing debit (worst-of-long/short bp/day from `docs/financing_decision.md`) applied to the full-window baseline runs. Financing is **not** in the engine PnL — this is an after-the-fact stress overlay. 'Raw expectancy R' is the per-run summary metric, so it matches the Metrics-by-pair table exactly.

| pair | trades | total financing debit (USD) | mean debit/trade (R) | raw expectancy R | financing-stressed expectancy R |
|---|---:|---:|---:|---:|---:|
| EUR_USD | 89 | 2.65 | 0.024 | -0.124 | -0.147 |
| GBP_USD | 106 | 3.25 | 0.024 | -0.052 | -0.077 |
| USD_JPY | 121 | 6.05 | 0.039 | -0.000 | -0.039 |
| AUD_USD | 104 | 2.46 | 0.019 | -0.204 | -0.223 |
| USD_CAD | 111 | 2.60 | 0.019 | -0.207 | -0.226 |
| USD_CHF | 97 | 3.73 | 0.031 | -0.140 | -0.170 |

### Financing-stressed expectancy by split

Pair-averaged (consistent with Metrics-by-split). Each pair's raw expectancy is its per-run summary metric; the financing debit is the mean per-trade debit in R over that run.

| split | raw expectancy R | financing debit R | financing-stressed expectancy R |
|---|---:|---:|---:|
| train | -0.120 | 0.025 | -0.146 |
| validation | -0.111 | 0.027 | -0.139 |
| test_untouched | -0.071 | 0.027 | -0.099 |
| full | -0.121 | 0.026 | -0.147 |

## Trade diagnostics (full-window baseline)

Full-window baseline trades: **628**.

| metric | value |
|---|---:|
| win rate | 33.6% |
| mean R | -0.118 |
| median R | -0.151 |
| long trades | 317 (expR -0.083) |
| short trades | 311 (expR -0.154) |
| total PnL (USD) | -102.64 |

**Exit reasons:**

| exit reason | trades | total PnL (USD) | expectancy R | win % |
|---|---:|---:|---:|---:|
| trailing_stop | 508 | +47.32 | +0.031 | 41.5% |
| stop | 120 | -149.95 | -0.751 | 0.0% |

## Comparison vs CAMPAIGN_002 H4 baseline

Both campaigns on **real OANDA H4 data, identical 6-pair universe** (CAMPAIGN_002 numbers recomputed here over the same 6 pairs — NZD_USD excluded — so the comparison isolates the ADX filter).

| split | campaign | trades | return % | PF | expectancy R | win % |
|---|---|---:|---:|---:|---:|---:|
| train | CAMPAIGN_002 H4 (6-pair) | 570 | -2.83% | 0.74 | -0.126 | 32.8% |
| train | **CAMPAIGN_003 +ADX** | 310 | -1.24% | 0.81 | -0.120 | 33.0% |
| validation | CAMPAIGN_002 H4 (6-pair) | 368 | -2.55% | 0.66 | -0.151 | 32.2% |
| validation | **CAMPAIGN_003 +ADX** | 203 | -1.34% | 0.69 | -0.111 | 35.2% |
| test_untouched | CAMPAIGN_002 H4 (6-pair) | 204 | -1.02% | 0.75 | -0.085 | 35.1% |
| test_untouched | **CAMPAIGN_003 +ADX** | 101 | -0.63% | 0.77 | -0.071 | 35.2% |
| full | CAMPAIGN_002 H4 (6-pair) | 994 | -5.62% | 0.67 | -0.147 | 32.2% |
| full | **CAMPAIGN_003 +ADX** | 628 | -3.42% | 0.71 | -0.121 | 33.6% |

The ADX filter cut trade count and modestly improved expectancy, but
did **not** lift the untouched-test result across break-even.
Conditioning the Donchian breakout on trend strength reduces how often
it fires in chop; it does not change the fact that the breakout entry
itself has no positive edge on these pairs over 2020-2026.

## Artifact paths

- Per-run equity curves: `backtests/campaign_003_controlled_adx/runs/**/*_equity.csv`
- Per-run trade lists: `backtests/campaign_003_controlled_adx/runs/**/*_trades.csv`
- **Per-signal risk rejections:** `backtests/campaign_003_controlled_adx/runs/**/*_risk_rejections.csv`
- Per-run summaries (committed): `backtests/campaign_003_controlled_adx/runs/**/*_summary.json`
- Run index: `backtests/campaign_003_controlled_adx/runs/_index.json`

(Equity/trade/rejection CSVs are gitignored for size; regenerate with
`python scripts/run_campaign_003.py --clean`.)

## Known limitations

1. **Financing unmodeled in-engine** — overlay only; hard live blocker.
2. NZD_USD exclusion is partly returns-correlated (it was also the
   worst CAMPAIGN_002 pair); the structural spread/ATR rationale is
   sound but the residual leakage is acknowledged.
3. Backtest fills approximate broker behavior; no live dry-run.
4. ADX threshold 25 is a single pre-committed value; this campaign does
   not establish its sensitivity (deliberately — no sweep).

## Pass/fail decision

Pre-committed Task-5 gates. **REJECT.**

Untouched-test expectancy **-0.071 R**. Gate findings:

- untouched-test expectancy negative (-0.071 R)
- untouched-test PF 0.77 < 1.05
- only 1/6 pairs positive on test — not broad
- stress_2x expectancy negative (-0.150 R)
- financing-stressed test expectancy negative (-0.099 R)
- financing remains unmodeled in-engine — blocker for live promotion regardless of the above (docs/financing_decision.md)

**REJECT.** The controlled ADX hypothesis did not lift the frozen breakout entry to a positive untouched-test expectancy. Conditioning *when* the breakout fires is not sufficient — the next research step (per the hypothesis backlog) is a different *entry* (volatility-compression breakout, H-11, or pullback-continuation, H-04), not further conditioning of this one. Do not paper-trade, demo-trade, or live-trade `0.2.0-c003`.

_Live trading is not recommended and not in scope for CAMPAIGN_003._
