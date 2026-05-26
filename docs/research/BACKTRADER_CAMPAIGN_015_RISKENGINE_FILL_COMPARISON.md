# Backtrader vs Bespoke Fold-Window Comparison — RiskEngine & Fill Parity

> **SUPERSEDED / STALE DUE TO DUPLICATE-CANDLE CONTAMINATION** — see
> [`BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md).

**Date:** 2026-05-26
**Branch:** `infra-backtrader-campaign-015-riskengine-and-fill-parity-001`

> Diagnostic-only. Does **not** approve any strategy.

## Headline

| metric | prior BT fold-window | parity BT | bespoke rehydrate |
|---|---:|---:|---:|
| Total trades | 532 | **416** | **164** |
| Classification | SIGNAL_RULE_MISMATCH | **SIGNAL_RULE_MISMATCH** | — |
| Gap vs bespoke | +368 | **+252** | — |

Gap shrank by **116 trades** (−31.5% of prior excess).

## Parity flags used

- `entry_bar_stop_policy = bespoke_current_no_entry_bar_stop`
- `risk_engine_parity = true`

## Trade count by fold

| fold | BT (parity) | bespoke | delta |
|---:|---:|---:|---:|
| 0 | 44 | 18 | +26 |
| 1 | 54 | 26 | +28 |
| 2 | 57 | 26 | +31 |
| 3 | 61 | 28 | +33 |
| 4 | 54 | 24 | +30 |
| 5 | 42 | 14 | +28 |
| 6 | 52 | 14 | +38 |
| 7 | 52 | 14 | +38 |

## Trade count by pair

| pair | BT (parity) | bespoke | delta |
|---|---:|---:|---:|
| AUD_USD | 88 | 24 | +64 |
| EUR_USD | 46 | 27 | +19 |
| GBP_USD | 83 | 41 | +42 |
| NZD_USD | 46 | 5 | +41 |
| USD_CAD | 59 | 23 | +36 |
| USD_CHF | 52 | 27 | +25 |
| USD_JPY | 42 | 17 | +25 |

## Side distribution

| side | BT (parity) | bespoke |
|---|---:|---:|
| long | 224 | 85 |
| short | 192 | 79 |

## RiskEngine rejection counts

| reason | BT (parity, CSV lane) | bespoke (sqlite rehydrate) |
|---|---:|---:|
| SPREAD_TOO_WIDE | 55 | 22 |
| SPREAD_TO_ATR | 63 | 78 |
| SESSION_BLOCKED | 27 | 10 |
| MARGIN_BUFFER | 0 | 9 |
| **Total** | **145** | **119** |

BT parity lane now rejects signals, but totals and mix differ from bespoke —
likely spread-source mismatch (CSV export vs sqlite rehydrate) plus portfolio
state tracking differences across fold resets.

## PnL / return (BT parity lane only)

- Total PnL (account): **+79.05 USD** (416 trades, not comparable to bespoke evidence)
- Starting equity per fold×pair: 500 USD

## Classification

**`SIGNAL_RULE_MISMATCH`** — trade-count delta +153.7% still far above ±10% PASS band.

Residual divergence is not primarily TIMESTAMP_MISMATCH (windows aligned) or
entry-bar same-stop rejection (addressed). Remaining gap likely combines:

1. CSV vs sqlite spread / session gate timing differences
2. Position-state / re-entry sequencing drift
3. Sizing path differences (RiskEngine plan.units vs legacy manual sizing on bespoke when risk passes)

## First divergence (signal-diff cell)

Prior first divergence at fold 0 / EUR_USD `2021-11-04T13:00` was
`FILL_TIMING_MISMATCH` / `same_bar_adverse_stop`. With
`bespoke_current_no_entry_bar_stop`, that specific rejection path is removed;
**expected resolved** (not re-traced in this sprint; re-run
`scripts/diff_campaign_015_signals.py` with parity flags as follow-up).

## Safety

- CAMPAIGN_015 remains **unapproved**
- Paper / demo / live remain **blocked**

## Artifacts

- JSON: `research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity/fold_window_comparison.json`
- Summary: `research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity/parity_run_summary.json`
