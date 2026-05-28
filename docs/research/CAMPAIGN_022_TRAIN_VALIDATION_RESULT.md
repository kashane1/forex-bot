# CAMPAIGN_022 — Train/Validation Result

**Date:** 2026-05-28
**Strategy:** `h4_h1_pullback_resolution_entry 0.1.0-c022` (frozen)
**Fill timing:** `next_bar_open` · **Verdict:** **REJECT** (train gate failed)
**Test lockbox:** NOT opened

## Commands run

```
export FOREX_BOT_RESEARCH_DATABASE_URL=<local research postgres>   # localhost/forex_bot
python scripts/run_campaign_022_h4_h1_pullback_resolution.py --preflight-only   # 7/7 PASS, 0 lookahead
python scripts/run_campaign_022_h4_h1_pullback_resolution.py train-validation   # 21 cells, 7216.8s
```

Engine speedups used (verified trade-for-trade identical vs baseline): `max_signal_window_bars=1500`
and HTF indicator-frame memoization. No strategy logic or frozen parameters changed.

## Data provenance

Materialized `m1_derived` M15 execution + H4/H1 context (storage `H4M1`), local research
Postgres only. **No D1 / D1AGG accessed.** Splits frozen pre-results:
train 2021-06-01→2023-12-31, validation 2024-01-01→2025-06-30 (test 2025-07-01→2026-05-20, unopened).

## Aggregate metrics (base cost)

| split | trades | expectancy_R | profit_factor | pairs_positive |
|---|---|---|---|---|
| **train** | 1369 | **−0.1042** | 0.752 | **0 / 7** |
| **validation** | 1027 | **−0.1663** | 0.690 | 1 / 7 |
| validation 2× cost-stress | 565 | −0.2468 | 0.495 | 0 / 7 |

## Per-pair (base)

| pair | train exp_R (n) | validation exp_R (n) |
|---|---|---|
| EUR_USD | −0.1533 (207) | −0.4667 (67) |
| GBP_USD | −0.1059 (236) | −0.4280 (74) |
| USD_JPY | −0.0017 (133) | +0.0004 (173) |
| AUD_USD | −0.0757 (166) | −0.1470 (205) |
| USD_CAD | −0.0512 (275) | −0.1425 (149) |
| USD_CHF | −0.1051 (274) | −0.1552 (170) |
| NZD_USD | −0.3877 (78) | −0.1594 (189) |

Every train pair is negative; the single non-negative validation pair (USD_JPY +0.0004R) is
statistically indistinguishable from zero.

## Gate table

| gate | required | actual | pass |
|---|---|---|---|
| train expectancy ≥ 0 | ≥ 0 | −0.1042 | ❌ |
| validation expectancy > 0 | > 0 | −0.1663 | ❌ |
| validation PF ≥ 1.05 | ≥ 1.05 | 0.690 | ❌ |
| validation trades ≥ 150 | ≥ 150 | 1027 | ✅ |
| validation pairs positive ≥ 4/7 | ≥ 4 | 1 | ❌ |
| 2× cost-stress validation exp ≥ 0 | ≥ 0 | −0.2468 | ❌ |
| beat C011 null by +0.010R (> +0.0071R) | > +0.0071 | −0.1663 | ❌ |
| Backtrader parity PASS | required pre-lockbox | not run (moot) | ❌ |

**Binding train gate fails → REJECT. No validation rescue. No test lockbox.**

## Comparison to baselines

| reference | expectancy_R | note |
|---|---|---|
| **C022 train** | −0.1042 | this campaign |
| **C022 validation** | −0.1663 | this campaign |
| C011 deduped null | −0.0029 | C022 is **far below** the null; `beat_null = false` |
| C020 (all-green H4) train | −0.035 | C022 train is **worse** than C020 train |
| C020 (all-green H4) validation | +0.053 | C022 validation is **worse** (and negative) |
| C021 (all-green M15) | — | scaffold only; **no executed evidence** — no numeric head-to-head (not fabricated) |

The pullback-resolution framework did **not** beat the prior all-green alignment campaigns —
it underperformed C020 on both train and validation, and it lost to the C011 null.

## Mechanism (preview; full Phase 3 in BEHAVIOR_DIAGNOSTICS)

Overall base: win rate 32.6%, avg win +1.24R, avg loss −0.79R; exit mix 60% stop / 40% time;
mean R by exit: stop −0.86R, time +0.96R; 42% of trades lose ≥0.9R. The M15 EMA20 reclaim after
an H1 holding-pullback is whipsawed too often: continuation does not follow through at a rate
sufficient to overcome the −2R-stop / +open payoff geometry.

## Statements

- **No approval.** `configs/approved_strategies.yaml` remains `approved: []`.
- **No retuning, no gate softening, no validation rescue.** Train failure is terminal.
- Average hold 0.31 calendar days (~19 M15 bars); financing overlay immaterial (avg hold < 1 day).
- Artifacts: `research/campaign_022/{train_metrics,validation_metrics,cost_stress_2x,gate_result,comparison_to_c011_null,hold_diagnostics,metrics_summary,run_manifest,evidence_status}.json`; per-cell trades/equity under `backtests/CAMPAIGN_022_h4_h1_pullback_resolution/`.
