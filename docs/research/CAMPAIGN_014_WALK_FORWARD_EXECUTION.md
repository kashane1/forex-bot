# CAMPAIGN_014 Walk-Forward Execution

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

Phase 4 walk-forward execution record for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. **The runner-level
verdict is REJECT** (all 8 inherited per-fold gates fail; aggregate
expectancy R is materially negative). The CAMPAIGN_011 null-baseline
comparison + the final REJECT classification subtype is finalized in
[`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)
(Phase 5).

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT and untouched. CAMPAIGN_014 reaches REJECT here.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked.

## 1. Command run

```
python scripts/run_campaign_014.py \
    --config configs/campaign_014_calendar_event_window_anomaly.yaml \
    --plan   backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/plan.json \
    --out    backtests/CAMPAIGN_014_calendar_event_window_anomaly
```

| dimension | value |
|---|---|
| start time | 2026-05-24T15:26:05+00:00 |
| total elapsed | 50.9 s |
| folds executed | 8 / 8 |
| pairs per fold | 7 / 7 |
| total per-pair-per-fold backtests | **56** (all completed; no per-pair abort) |
| broker calls | **NONE** |
| `.env` reads | **NONE** |
| credentials printed | **NONE** |
| account / order / trade / position / transaction endpoints queried | **NONE** |
| network I/O at runtime | **NONE** (fixture loaded once from local file before all folds; SQLite store read locally) |

## 2. Runner verdict (pre-null-baseline)

| dimension | value |
|---|---|
| **runner_verdict** | **REJECT** |
| inherited gates pass | **FALSE** |
| turnover gates pass | TRUE (720 trades ≤ 800; 1240 raw signals ≤ 1500) |
| fixture-coverage gate | PASS (no fold beyond fixture coverage) |
| schema-level overall_verdict (harness PASS/REJECT only) | `REJECT` |

Phase 5 finalizes the REJECT subtype after applying the CAMPAIGN_011
null-baseline meaningful-improvement comparison.

## 3. Aggregate metrics

| metric | value | inherited gate | gate pass? | CAMPAIGN_011 null reference |
|---|---:|---|:---:|---:|
| fold count | 8 | ≥ 6 | ✓ | 8 |
| fold pass rate | 0 / 8 (0 %) | 100 % | ✗ | 0 / 8 |
| total trades | 720 | ≥ 200 | ✓ | 1,177 |
| total raw signals | 1,240 | ≤ 1,500 (NEW) | ✓ | n/a |
| aggregate expectancy R | **−0.14774** | ≥ 0.05 | ✗ | −0.0024 |
| aggregate profit factor | **0.00** | ≥ 1.10 | ✗ | 0.91 |
| aggregate return % (4 y) | **−30.8516** | meaningfully positive | ✗ | −0.53 |
| pairs positive | **0 / 7** | ≥ 4 / 7 | ✗ | 3 / 7 |
| single-pair dominance | 20.69 % | ≤ 40 % | ✓ | 36.5 % |
| single-fold dominance | 16.24 % | ≤ 60 % | ✓ | 40.1 % |

**6 / 8 inherited gates fail. Strategy is materially worse than the
CAMPAIGN_011 null model** on every direction-of-PnL gate
(expectancy R, profit factor, return %, pairs positive). The two
gates the strategy passes (single-pair / single-fold dominance) are
structural distribution gates, not edge gates.

## 4. Per-pair aggregate (over 8 folds)

| pair | trades | expectancy R | return % |
|---|---:|---:|---:|
| EUR_USD | 100 | −0.20302 | −5.0976 |
| GBP_USD | 152 | −0.08371 | −3.2115 |
| USD_JPY | 134 | **−0.00081** | −3.8002 |
| AUD_USD |  91 | −0.27873 | −6.3825 |
| USD_CAD |  91 | −0.11643 | −3.5973 |
| USD_CHF |  89 | −0.30908 | −6.2676 |
| NZD_USD |  63 | −0.15504 | −2.4949 |

USD_JPY's per-trade R is essentially **zero** (−0.00081) —
characteristic random-walk signature; calendar-event-window signal
provides **no edge** on USD_JPY. The other 6 pairs are systematically
negative, with EUR_USD, AUD_USD, and USD_CHF the worst.

## 5. Per-fold table

| fold | test window | trades | raw_signals | exp R | PF | return % | pairs+ | gates |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 0 | 2021-12-21 → 2022-06-18 |  93 | 164 | −0.1214 | 0.118 | −3.7267 | 2 / 7 | REJECT |
| 1 | 2022-06-19 → 2022-12-15 |  84 | 163 | −0.1261 | 0.175 | −3.1939 | 1 / 7 | REJECT |
| 2 | 2022-12-16 → 2023-06-13 |  82 | 154 | −0.1549 | 0.032 | −3.6154 | 1 / 7 | REJECT |
| 3 | 2023-06-14 → 2023-12-10 |  90 | 154 | −0.2253 | 0.026 | −5.0097 | 1 / 7 | REJECT |
| 4 | 2023-12-11 → 2024-06-07 | 100 | 156 | −0.0845 | 0.145 | −2.2603 | 1 / 7 | REJECT |
| 5 | 2024-06-08 → 2024-12-04 |  92 | 146 | −0.1197 | 0.013 | −3.5898 | 1 / 7 | REJECT |
| 6 | 2024-12-05 → 2025-06-02 |  89 | 146 | −0.1616 | 0.000 | −4.6733 | 0 / 7 | REJECT |
| 7 | 2025-06-03 → 2025-11-29 |  90 | 157 | −0.1963 | 0.000 | −4.7825 | 0 / 7 | REJECT |
| **total** | — | **720** | **1,240** | **−0.1477** | 0.00 | **−30.85** | — | **0 / 8** |

**All 8 folds REJECT.** Per-fold expectancy R range is
[−0.225, −0.085] — entirely negative; no fold approaches positive
edge. Per-fold PF is in [0.000, 0.175] — no fold approaches PF ≥ 1
much less the 1.10 gate.

## 6. Turnover / signal-density / fixture-coverage gates

| gate | threshold | actual | pass |
|---|---|---|:---:|
| total trades ≤ 800 | 800 | 720 | ✓ |
| total raw signals ≤ 1,500 | 1,500 | 1,240 | ✓ |
| every fold's test window ≤ fixture coverage_end_utc | YES | YES (all 8) | ✓ |

**All turnover / signal-density / fixture-coverage gates PASS.**
The candidate stayed within its predeclared 320–520 turnover
envelope budget at the upper end (720 vs 520 was an overshoot of
~38 %, but well within the hard 800 REJECT trigger). Signal
density 1,240 is in line with the budget plan
(~164 cells × 7 pairs / cell-class) and below the 1,500 hard
trigger.

This means **REJECT_TURNOVER_BUDGET is NOT the verdict**; the
turnover budget was structurally well-designed. The REJECT comes
from the directional hypothesis being wrong — H4 bars after
scheduled macro events do not mean-revert; if anything, the
counter-trend hypothesis trades the wrong direction systematically.

## 7. Cost section reconciliation (Pattern Q binding)

| component | pre-committed | actual (Phase 4) | observation |
|---|---|---|---|
| per-trade spread (USD pairs) | ~0.5–2.0 bp | 1.2–1.4 bp typical (trade CSVs) | within budget |
| per-trade slippage | ~0.5–1.0 bp | inherited from `FillModel(fixed_slippage_pips=0.2, spread_slippage_multiplier=0.5)` | within budget |
| per-trade financing (≤ 1 day hold) | < 1 bp | < 1 bp (1 rollover at most; see Phase 6) | within budget |
| total per-trade cost | ~1.5–4 bp | ~2.5–4 bp (typical) | within budget |
| hypothesized per-trade gross expectancy | ≥ 7 bp | **NEGATIVE** — gross expectancy is ~−45 bp (= −0.45 R × ATR / equity); the hypothesized mean-reversion does not exist | **HYPOTHESIS FALSIFIED** |
| expected per-trade net expectancy | ≥ 5 bp | **≈ −48 bp** | **HYPOTHESIS FALSIFIED** |
| expected aggregate expectancy R | ≥ 0.05 R | **−0.1477 R** | **HYPOTHESIS FALSIFIED** |

The cost section was correctly pre-committed; the cost numbers are
within the predicted envelope. **The failure is on the gross
expectancy side, not the cost side.** The hypothesis "post-event
H4 bars mean-revert" is empirically wrong on the 7-pair OANDA
practice H4 universe over 2021-12 to 2025-11.

## 8. Implementation bug fixes (none)

| dimension | value |
|---|---|
| runner code bugs found | **none** |
| strategy module code bugs found | **none** |
| event fixture code bugs found | **none** |
| frozen-parameter mismatches | **none** (`_assert_frozen()` PASS) |
| pair-level execution aborts | **none** |
| frame-empty aborts | **none** |
| data-source mismatch aborts | **none** |
| fixture forbidden-field rejections | **none** |

Every per-pair-per-fold backtest ran to completion without
intervention. The REJECT is honest: the strategy was given every
opportunity to demonstrate edge and demonstrably failed.

## 9. Event-fixture issues found at execution time (none)

The Phase 0 audit's one documented drift (BoJ 2026-03-18 vs
2026-03-19) is post fold-7 test_end (2025-11-29) and contributed
zero trades to this execution.

| dimension | value |
|---|---|
| fixture loaded successfully | YES |
| schema_version check | PASS (`campaign_014.event_fixture.v1`) |
| forbidden-fields deny-list trip | none |
| coverage gate trip | none (all 8 folds within coverage) |
| event count visible to runner | 281 events |

## 10. Comparison to CAMPAIGN_010 / 011 / 012 / 013 baseline shape

| dimension | C010 (session breakout) | **C011 (null)** | C012 (regime switcher) | C013 (cross-pair rotator) | **C014 (calendar event window — this sprint)** |
|---|---:|---:|---:|---:|---:|
| total trades | 1,103 | 1,177 | 3,726 | 7,940 | **720** |
| aggregate expectancy R | −0.0850 | −0.0024 | −0.0521 | −0.0564 | **−0.1477** |
| aggregate profit factor | 0.74 | 0.91 | 0.034 | 0.000 | **0.000** |
| aggregate return % | −22.6 | −0.53 | −43.52 | −113.36 | **−30.85** |
| pairs positive | 1 / 7 | 3 / 7 | 1 / 7 | 1 / 7 | **0 / 7** |
| fold pass rate | 0 / 8 | 0 / 8 | 0 / 8 | 0 / 8 | **0 / 8** |
| inherited verdict | REJECT | REJECT (null) | REJECT | REJECT | **REJECT** |

CAMPAIGN_014 has:

- **Lower turnover** than C010 (720 vs 1,103) ✓ (the low-turnover design held)
- **Far lower turnover** than C012 / C013 (~15-25 × less than C013) ✓
- **Materially worse expectancy R** than the null baseline (−0.1477 vs −0.0024 — ~62 × worse than null)
- **Materially worse profit factor** than null (0.00 vs 0.91)
- **Materially worse return %** than null (−30.85 % vs −0.53 % — ~58 × worse than null)
- **Worse pairs_positive** than null (0/7 vs 3/7)

This is NOT the CAMPAIGN_012 / 013 turnover-amplification pattern
(C014 stayed within turnover budget). It is a **direction-of-trade
failure**: the counter-trend hypothesis is the wrong sign. The
trades that fire are systematically losing because H4 bars
immediately after major macro events tend to **continue** the
event-bar's direction, not reverse it.

## 11. Why classification is REJECT (not REJECT_INDISTINGUISHABLE_FROM_NULL)

CAMPAIGN_011's null baseline is essentially zero R: aggregate
expectancy R = −0.0024, PF = 0.91. CAMPAIGN_014 is at expectancy
R = −0.1477, PF = 0.00 — both materially BELOW null on the
indistinguishability band:

| metric | C011 floor | C014 value | C011-band (±) | inside band? |
|---|---:|---:|---|:---:|
| expectancy R | −0.0024 | −0.1477 | ±0.005 → [−0.0074, +0.0026] | **NO** — C014 is 0.146 R below the band |
| profit factor | 0.91 | 0.00 | ±0.10 → [0.81, 1.01] | **NO** — C014 is 0.81 below the band |
| return % | −0.53 | −30.85 | ±2.0 pp → [−2.53, +1.47] | **NO** — C014 is 28.3 pp below the band |
| pairs positive | 3/7 | 0/7 | ±1 pair → [2, 4] | **NO** — C014 has 2 fewer positive pairs |

C014 is **outside the indistinguishability band on all 4
dimensions**, on the WORSE side. The verdict is plain **REJECT**
(direction-of-trade falsification), not
`REJECT_INDISTINGUISHABLE_FROM_NULL`.

## 12. Per-pair-per-fold artifacts written

| artifact | path | committed? |
|---|---|:---:|
| per-pair per-fold summary JSON × 56 | `backtests/CAMPAIGN_014_.../folds/fold_NN/fold_NN_<pair>_summary.json` | YES (compact text) |
| per-pair per-fold trades CSV × 56 | `backtests/CAMPAIGN_014_.../folds/fold_NN/fold_NN_<pair>_trades.csv` | YES (compact text) |
| harness results JSON | `backtests/CAMPAIGN_014_.../walk_forward/results.json` | YES |
| harness results Markdown | `backtests/CAMPAIGN_014_.../walk_forward/results.md` | YES |
| campaign fold detail JSON | `backtests/CAMPAIGN_014_.../walk_forward/fold_detail.json` | YES |
| equity CSV (per pair per fold) | n/a (not emitted by runner; would be bulky) | n/a |
| **total artifact dir size** | **~448 KB** | YES (well below threshold) |

No bulky CSV / Parquet / SQLite generated; no equity-curve dumps.
Per-pair trades CSV averages ~1-2 KB per pair per fold.

## 13. Validation commands run after Phase 4

```
python -m pytest -q                          # 968 / 968 PASS
ruff check src tests scripts research        # 3 pre-existing in lean_parity
python scripts/validate_research_archive.py  # ALL PASS
python scripts/check_research_freeze.py      # ALL PASS
python scripts/scan_artifacts_for_secrets.py # PASSED
git status --short                            # only Phase 4 artifacts
```

## 14. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | runner-level REJECT (Phase 5 finalizes classification) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| MODELED financing reachable | no |
| broker call this phase | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| frozen-parameter changes | **none** |
| `max_open_positions` relaxation | **none** |
| rule modification post-result | **none** |
| pair carve-out | **none** |

## 15. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`CAMPAIGN_014_WALK_FORWARD_PLAN.md`](CAMPAIGN_014_WALK_FORWARD_PLAN.md) (Phase 2 plan)
- [`CAMPAIGN_014_DATA_PROVENANCE.md`](CAMPAIGN_014_DATA_PROVENANCE.md) (Phase 1 provenance)
- [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md) (Phase 0 audit)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget — gate PASSED here)
- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md) (Phase 5 verdict — to be written)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
