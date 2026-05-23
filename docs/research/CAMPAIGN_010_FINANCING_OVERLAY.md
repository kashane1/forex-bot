# CAMPAIGN_010 — Financing Overlay (ESTIMATED + Conservative Stress)

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 5 financing overlay for the CAMPAIGN_010 walk-forward
evidence. Applies the existing
[`research/financing/`](../../research/financing) calculator with
the default conservative-stress rate source (debit-only on both
long and short) to every committed CAMPAIGN_010 trade. **This is
an off-engine overlay; engine PnL is unchanged. MODELED financing
remains refused at four layers.**

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. The four-layer
> `MODELED`-refusal in `src/forex_bot/financing.py` plus the
> research-side calculator stands untouched.

## 1. Financing source and treatment ladder

| dimension | value |
|---|---|
| source name | `conservative_stress` (`research.financing.default_stress_rate_source()`) |
| treatment | **`ESTIMATED`** |
| MODELED reachable here? | **no** — `TableRateSource(treatment=MODELED)` raises at construction; `calculate_run(source)` raises if `source.treatment == MODELED`; the campaign runner does not configure or pass any MODELED source. |
| OBSERVED treatment exercised? | **no** — no observed-rate fixture or capture is consumed by this overlay; the calculator falls back to `default_stress_rate_source()` which is debit-only on both sides per pair. |
| `default_stress_rate_source()` rates | per-pair pessimistic annual bp (see [`research/financing/rates.py`](../../research/financing/rates.py) `CONSERVATIVE_BP_PER_DAY`); applied identically to long and short so the net cashflow is debit only. |
| engine-PnL modification? | **no** — `BacktestEngine` is unchanged; financing is added *on top of* the committed engine results. |
| live-promotion blocker status | **`financing_is_live_blocker = true`** — unchanged by this sprint. |

## 2. Commands

```bash
# Phase 5 — financing overlay (no broker call, no credential).
.venv/bin/python scripts/build_campaign_010_financing_overlay.py \
    --campaign-dir backtests/CAMPAIGN_010_session_breakout/
```

The script reads every `backtests/CAMPAIGN_010_session_breakout/folds/fold_NN/fold_NN_<PAIR>_trades.csv`,
constructs a `PositionInterval` per trade (units, side, entry
price, open / close times — all from the engine's output, all
tz-aware), and calls `research.financing.calculate_run(...,
default_stress_rate_source())`. Outputs:

- [`backtests/CAMPAIGN_010_session_breakout/financing/financing_run.json`](../../backtests/CAMPAIGN_010_session_breakout/financing/financing_run.json)
  — the canonical `FinancingRunReport` JSON (sorted keys, ISO-8601 dates).
- [`backtests/CAMPAIGN_010_session_breakout/financing/financing_run.md`](../../backtests/CAMPAIGN_010_session_breakout/financing/financing_run.md)
  — the deterministic markdown rendering.
- [`backtests/CAMPAIGN_010_session_breakout/financing/financing_summary.json`](../../backtests/CAMPAIGN_010_session_breakout/financing/financing_summary.json)
  — extended per-pair / per-side / per-fold breakdown the Phase 4
  verdict cross-references.

## 3. Headline numbers (verbatim from `FinancingRunReport`)

| field | value |
|---|---|
| `event_count` (per-day rollovers across all trades, weekend skip + Wednesday triple) | **2,483** |
| `cashflow_home_total` (USD, sum across all events) | **−$55.69** |
| `cashflow_home_stress_total` (USD; identical here because the conservative source is debit-only) | **−$55.69** |
| `missing_rate_event_count` | **0** (the conservative stress source is defined for every pair) |
| `financing_treatment` | `ESTIMATED` |
| `financing_in_engine_pnl` | `false` |
| `financing_is_live_blocker` | `true` |

The events:trades ratio = 2,483 / 2,791 ≈ **0.89** — many
session_breakout trades are intraday (open during London, close
on the next H4 bar or via time-stop / stop-loss within 6 bars),
so they never cross a rollover.

## 4. Impact on the verdict

| metric | pre-financing | financing (ESTIMATED + conservative stress) | post-financing |
|---|---:|---:|---:|
| total trade PnL (USD, sum across 7 pairs × 8 folds) | −$182.78 | **−$55.69** | **−$238.47** |
| aggregate-return-pct on starting equity (per pair $500 × 7 = $3,500) | **−5.22 %** of starting bank | **−1.59 %** | **−6.81 %** of starting bank |
| (the engine's reported `aggregate_return_pct = −36.56 %` sums the per-pair % returns, so each pair's −5 % equity hit aggregates to −36 % when summed across 7 pairs; the financing %/equity equivalent is correspondingly −7.95 %, giving a combined **−44.51 %**) | | | |

Financing strictly **worsens** the verdict. Every gate that
failed in Phase 4 remains failed by a wider margin under
financing.

| gate | pre-financing | post-financing |
|---|---|---|
| `aggregate.expectancy_R_net_of_stress_financing ≥ 0.05` | **−0.0408 R** (FAIL) | **−0.0539 R** (FAIL — wider) |
| `aggregate.profit_factor_net_of_stress_financing ≥ 1.10` | **0.04** (FAIL) | **0.04** (FAIL) |
| `aggregate.pairs_positive ≥ 4 of 7` | **1 / 7 (USD_CHF only)** (FAIL) | **0 / 7** (FAIL — USD_CHF flips to net negative under stress) |
| `financing.conservative_stress_run_does_not_flip_verdict` | n/a | **PASS — verdict was already REJECT pre-financing; stress deepens the loss** |
| `financing.modeled_refused` | n/a | **PASS — MODELED never reached, all four refusal layers held** |
| `financing.missing_rate_event_count == 0` | n/a | **PASS — 0 missing** |

The expectancy R approximation in the post-financing row above
uses the per-trade financing share applied as a debit to the
realized R contribution: `expectancy_R_post ≈ -0.0408 +
(financing_total / sum_abs_risked)` — see the precise
re-computation in §5; the conclusion (REJECT widens) is robust.

## 5. Per-pair financing sensitivity

| pair | trades | rollover events | trade PnL (USD) | financing (USD) | net (USD) | sign change? |
|---|---:|---:|---:|---:|---:|:---:|
| EUR_USD | 310 | 275 | −31.07 | −5.52 | −36.59 | already − |
| GBP_USD | 565 | 497 | −30.57 | −10.41 | −40.98 | already − |
| USD_JPY | 492 | 452 | −26.81 | −14.86 | −41.67 | already − |
| AUD_USD | 511 | 457 | −48.14 | −7.59 | −55.72 | already − |
| USD_CAD | 434 | 363 | −46.32 | −6.78 | −53.09 | already − |
| **USD_CHF** | 432 | 394 | **+8.45** | **−10.08** | **−1.63** | **+→−** (flips) |
| NZD_USD | 47 | 45 | −8.33 | −0.45 | −8.77 | already − |
| **total** | 2,791 | 2,483 | −182.78 | −55.69 | −238.47 | |

Under conservative stress, the single positive-expectancy pair
(USD_CHF) flips to net negative. `pairs_positive` falls from
1 / 7 to **0 / 7** — already below the ≥ 4 / 7 gate either way.

## 6. Long vs short sensitivity

| side | trades | rollover events | trade PnL (USD) | financing (USD) |
|---|---:|---:|---:|---:|
| long | 1,413 | 1,262 | −61.38 | −29.88 |
| short | 1,378 | 1,221 | −121.40 | −25.81 |

Both sides debit roughly equally (the conservative source applies
the worse rate to both); shorts contribute more of the trade loss
(−$121 vs −$61) and slightly less of the financing debit.

## 7. Per-fold financing sensitivity

| fold | trades | rollover events | trade PnL (USD) | financing (USD) | net (USD) |
|---:|---:|---:|---:|---:|---:|
| 0 | 367 | 321 | −6.15 | −7.15 | −13.30 |
| 1 | 390 | 344 | −60.24 | −5.27 | −65.51 |
| 2 | 409 | 362 | −36.59 | −6.99 | −43.58 |
| 3 | 374 | 325 | −16.26 | −8.23 | −24.49 |
| 4 | 347 | 303 | −46.39 | −8.47 | −54.86 |
| 5 | 265 | 247 | −21.26 | −6.06 | −27.32 |
| 6 | 347 | 317 | **+8.17** | **−6.44** | **+1.73** |
| 7 | 292 | 264 | −4.06 | −7.08 | −11.14 |

Fold 6 remains net positive under conservative-stress financing
(+$1.73 vs +$8.17 pre-financing) — but its per-fold expectancy R
(+0.0211) is still below the per-fold gate of ≥ 0.05 R, and its
`pairs_positive` is 3 / 7 (gate ≥ 4 / 7). The fold still fails.

## 8. Missing data + caveats

- **No OBSERVED financing data is available** for the
  2020-2026 universe — OANDA's v20 REST API publishes no
  historical financing-rate series, and no `DAILY_FINANCING`
  transactions were captured under the freeze. The
  `default_stress_rate_source()` is the only authorized
  bp/day reference today, per
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
  §11.
- **No MODELED treatment.** The four-layer refusal stands:
  1. `TableRateSource(treatment=MODELED)` raises.
  2. `calculate_run(rate_source)` raises if
     `source.treatment == MODELED`.
  3. `FinancingRunReport.treatment` is Pydantic-pinned to
     `ESTIMATED` / `OBSERVED` via the calculator output here.
  4. `src/forex_bot/financing.py`
     `financing_treatment_blocks_approval` continues to refuse
     paper / demo / live promotion without MODELED.
- **Cross-pair conversion deferred.** Every pair in this
  universe is XXX_USD or USD_XXX (USD is home for all), so the
  cross-pair fallback note never fires here — `notes` is empty
  for every event.
- **Holiday calendar absent.** The calculator skips weekends
  but does not skip US/UK/AU/CA/CH/JP/NZ holidays. The
  conservative source has a non-zero bp/day for every pair, so
  missing rate events do not fire (count = 0); the holiday
  treatment is therefore "rollover applies"; impact is small
  but documented.

## 9. Why this does not approve the strategy

- The overlay is **diagnostic context** added on top of the
  Phase 4 REJECT — it strictly worsens the result; it cannot
  upgrade the verdict.
- Even if financing were *favorable* and flipped the verdict,
  the candidate would still need items 4–6 of the six-evidence
  ladder per
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 — including independent corroboration (Phase 7) and human
  approval (a deliberate
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
  action).
- **`configs/approved_strategies.yaml` remains `approved: []`.**

## 10. Cross-links

- [`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_FINANCING_RISK_READINESS.md`](CAMPAIGN_010_FINANCING_RISK_READINESS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`OBSERVED_FINANCING_CAPTURE.md`](OBSERVED_FINANCING_CAPTURE.md)
- [`backtests/CAMPAIGN_010_session_breakout/financing/financing_run.json`](../../backtests/CAMPAIGN_010_session_breakout/financing/financing_run.json)
- [`backtests/CAMPAIGN_010_session_breakout/financing/financing_run.md`](../../backtests/CAMPAIGN_010_session_breakout/financing/financing_run.md)
- [`backtests/CAMPAIGN_010_session_breakout/financing/financing_summary.json`](../../backtests/CAMPAIGN_010_session_breakout/financing/financing_summary.json)
- [`scripts/build_campaign_010_financing_overlay.py`](../../scripts/build_campaign_010_financing_overlay.py)
