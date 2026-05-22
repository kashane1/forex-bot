# Custom-engine CAMPAIGN_002 H4 parity reproduction

**Generated:** 2026-05-22T21:11:10.357883+00:00 · **Branch:** `infra-lean-parity-001`

> **DIAGNOSTIC / PARITY REPRODUCTION — NOT A NEW VERDICT.** This re-runs the **already-REJECTED** CAMPAIGN_002 H4 `trend_following` baseline on the bespoke engine for parity verification. `strategy_evidence: false`. It runs no new hypothesis, sweeps no parameter, and approves nothing. CAMPAIGN_002 stays **REJECT** regardless of the figures below.

## Run parameters

| field | value |
|---|---|
| strategy | `trend_following 0.1.0-baseline-frozen` |
| config | `configs/campaign_002_real_oanda.yaml` |
| config hash | `d536a9b06818197f…` |
| fill timing | `signal_bar_close` (CAMPAIGN_002's timing) |
| cost model | base regime — 0.2 pip slippage, 0.5× spread |
| risk engine | wired in (`mode=backtest`) — as CAMPAIGN_002 ran |
| window | 2020-01-01 → 2026-05-20 (full split) |
| data store | `data/oanda_h4_research.sqlite3` (gitignored) |

## Data provenance

| instrument | candles | first ts | last ts | data_request_hash |
|---|---|---|---|---|
| EUR_USD | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `ed353315b8ffd5a9` |
| GBP_USD | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `ca2a95816825492e` |
| USD_JPY | 9932 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `e1a6a5025f0cdc19` |
| AUD_USD | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `c36cbd0228ebffc4` |
| USD_CAD | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `40d80a3a240626a4` |
| USD_CHF | 9931 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `d907a301cc57e010` |
| NZD_USD | 9935 | 2020-01-01T22:00:00+00:00 | 2026-05-19T21:00:00+00:00 | `b62683f67f9fc916` |

## Reproduction results (bespoke engine)

| instrument | trades | expectancy R | return % | profit factor | win % | max DD % | rejected |
|---|---|---|---|---|---|---|---|
| EUR_USD | 132 | -0.218 | -7.04 | 0.55 | 29.5 | -8.05 | 274 |
| GBP_USD | 198 | -0.089 | -4.40 | 0.79 | 36.4 | -6.79 | 55 |
| USD_JPY | 217 | -0.000 | -0.54 | 0.98 | 38.2 | -3.57 | 84 |
| AUD_USD | 144 | -0.218 | -7.64 | 0.56 | 28.5 | -8.14 | 271 |
| USD_CAD | 122 | -0.185 | -7.19 | 0.51 | 29.5 | -8.03 | 373 |
| USD_CHF | 181 | -0.171 | -6.91 | 0.65 | 30.9 | -8.09 | 120 |
| NZD_USD | 38 | -0.203 | -1.95 | 0.53 | 36.8 | -1.99 | 576 |

**Total trades across the seven pairs: 1032.**

## Comparison to the committed CAMPAIGN_002 report

Reference numbers are the CAMPAIGN_002 H4 full-split, base-cost per-pair figures from `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`. A small delta is expected (the store was independently re-fetched); a large delta would itself be a finding to investigate — never tuned away.

| instrument | trades (repro / ref / Δ) | expectancy R (repro / ref / Δ) |
|---|---|---|
| EUR_USD | 132 / 132 / +0 | -0.218 / -0.218 / +0.000 |
| GBP_USD | 198 / 198 / +0 | -0.089 / -0.089 / +0.000 |
| USD_JPY | 217 / 217 / +0 | -0.000 / -0.000 / -0.000 |
| AUD_USD | 144 / 144 / +0 | -0.218 / -0.218 / +0.000 |
| USD_CAD | 122 / 122 / +0 | -0.185 / -0.185 / -0.000 |
| USD_CHF | 181 / 181 / +0 | -0.171 / -0.171 / -0.000 |
| NZD_USD | 38 / 38 / +0 | -0.203 / -0.203 / -0.000 |

Reproduction total trades **1032** vs committed **1032** (Δ +0).

## What this establishes

- The bespoke engine's CAMPAIGN_002 H4 baseline is **reproducible** from the committed config and the local real-OANDA H4 store — the custom-engine side of the Lean parity comparison is hash-pinned and re-runnable.
- It does **not** establish, measure, or imply any strategy edge. CAMPAIGN_002 was REJECT and stays REJECT. This is parity reproduction infrastructure, not strategy evidence, and approves nothing.
