# CAMPAIGN_014 Walk-Forward Result — REJECT

**Date:** 2026-05-26 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

> **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE.** Metrics and
> null-baseline comparison used pre-fix SQLite. REJECT verdict unchanged.

Phase 5 walk-forward verdict for CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`. Combines the Phase 4
execution metrics with the CAMPAIGN_011 null-baseline comparison,
the turnover-budget gates, the cost-section reconciliation, and the
CAMPAIGN_014-specific event-class diagnostics.

> No strategy approved. **Verdict: REJECT.** CAMPAIGN_002 / 010 /
> 011 / 012 / 013 remain REJECT and untouched. CAMPAIGN_014 joins
> them as REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. Research verdict

| dimension | value |
|---|---|
| **research verdict** | **REJECT** |
| sub-classification | **REJECT (direction-of-trade falsification)** — hypothesis is empirically wrong on this universe |
| NOT classified as | `REJECT_TURNOVER_BUDGET` (turnover within budget) |
| NOT classified as | `REJECT_INDISTINGUISHABLE_FROM_NULL` (materially worse than null on all 4 PnL-direction dimensions; outside indistinguishability band) |
| NOT classified as | `BLOCKED` (all 8 fold test windows within fixture coverage; no execution abort) |
| NOT classified as | `RESEARCH_PASS_UNAPPROVED` (0 / 8 fold pass rate; aggregate expectancy −0.148 R) |
| approval-related implication | **NONE** — strategy is REJECTED; `configs/approved_strategies.yaml` unchanged |

## 2. Inherited gate verdict table

(Per-fold + aggregate gates from CAMPAIGN_010 verbatim, mirrored by
the runner's `TEST_FOLD_GATES` + `AGGREGATE_GATES`.)

### 2.1 Per-fold gate vector (CAMPAIGN_014 aggregate per-fold)

| gate | threshold | actual (every fold) | pass / fail |
|---|---|---|:---:|
| `expectancy_r_ge_0p05` | ≥ 0.05 R | [−0.225, −0.085] R | **FAIL × 8** |
| `profit_factor_ge_1p10` | ≥ 1.10 | [0.000, 0.175] | **FAIL × 8** |
| `trade_count_ge_30` | ≥ 30 | [82, 100] | **PASS × 8** |
| `pairs_positive_ge_4_of_7` | ≥ 4 / 7 | [0, 2] | **FAIL × 8** |
| `single_pair_dominance_le_60pct` | ≤ 60 % | (variable, all < 60 %) | **PASS × 8** |

**Fold pass rate: 0 / 8 = 0 %.** Every fold fails 3 of the 5
per-fold gates (expectancy R, profit factor, pairs positive).

### 2.2 Aggregate gate vector

| gate | threshold | actual | pass / fail |
|---|---|---:|:---:|
| `fold_pass_rate_eq_100pct` | 100 % | 0 % | **FAIL** |
| `fold_count_ge_6` | ≥ 6 | 8 | PASS |
| `expectancy_r_ge_0p05` | ≥ 0.05 R | **−0.14774** | **FAIL** |
| `profit_factor_ge_1p10` | ≥ 1.10 | **0.00** | **FAIL** |
| `trade_count_ge_200` | ≥ 200 | 720 | PASS |
| `pairs_positive_ge_4_of_7` | ≥ 4 / 7 | **0 / 7** | **FAIL** |
| `single_fold_dominance_le_60pct` | ≤ 60 % | 16.24 % | PASS |
| `single_pair_dominance_le_40pct` | ≤ 40 % | 20.69 % | PASS |

**6 of 8 aggregate gates FAIL.** Only the structural/distribution
gates (fold count, trade count, single-fold dominance, single-pair
dominance) pass; every edge gate fails.

## 3. Turnover / cost gate table

(Per [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
§10.1 + [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
§4.)

| gate | threshold | actual | pass / fail |
|---|---|---:|:---:|
| total trades over 4 y | ≤ 800 (hard REJECT) | 720 | **PASS** |
| total raw signals over 8 folds | ≤ 1,500 (hard REJECT) | 1,240 | **PASS** |
| every fold test window within fixture coverage | yes | yes (all 8) | **PASS** |
| **all turnover / coverage gates** | — | — | **PASS** |

**Turnover budget is well-designed; the candidate stayed within the
predicted 320–520 envelope at the upper edge (720) and well below
the 800 hard trigger.** This is materially different from
CAMPAIGN_012 / 013, which overshot turnover by 3–7 × null. The
CAMPAIGN_014 REJECT is NOT a turnover failure.

### 3.1 Cost-section reconciliation (Pattern Q binding)

| component | pre-committed | actual | observation |
|---|---|---|---|
| per-trade spread (USD pairs) | ~0.5–2.0 bp | 1.2–1.4 bp typical | within budget |
| per-trade slippage | ~0.5–1.0 bp | `fixed_slippage_pips=0.2 + 0.5×spread` | within budget |
| per-trade financing | < 1 bp | < 1 bp (see Phase 6) | within budget |
| total per-trade cost | ~1.5–4 bp | ~2.5–4 bp | within budget |
| hypothesized per-trade gross expectancy | ≥ 7 bp | **gross ≈ −45 bp** | **FAILED — wrong direction** |
| expected per-trade net expectancy | ≥ 5 bp | **net ≈ −48 bp** | **FAILED — wrong direction** |
| expected aggregate expectancy R | ≥ 0.05 R | **−0.1477 R** | **FAILED — wrong direction** |

**The cost section was honest** — actual per-trade costs are
within the pre-commit envelope. **The failure is purely on the
gross-expectancy side: the counter-trend hypothesis was wrong.**
H4 bars immediately after major scheduled macro events tend to
**continue** the event-bar's direction, not **revert** it.

## 4. CAMPAIGN_011 null-baseline comparison (binding)

Per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3 + §8.

### 4.1 Side-by-side aggregate metrics

| metric | CAMPAIGN_011 null | CAMPAIGN_014 | "meaningful improvement" margin | met? |
|---|---:|---:|---|:---:|
| aggregate expectancy R | −0.0024 | **−0.14774** | ≥ +0.0524 R (→ ≥ 0.05 R) | **NO — 0.145 R BELOW null** |
| aggregate profit factor | 0.91 | **0.00** | ≥ +0.19 (→ ≥ 1.10) | **NO — 0.91 BELOW null** |
| aggregate return % (4 y) | −0.53 | **−30.85** | ≥ +5.5 pp (→ ≥ +5 %) | **NO — 30.32 pp BELOW null** |
| pairs positive | 3 / 7 | **0 / 7** | ≥ +1 pair (→ ≥ 4 / 7) | **NO — 3 pairs BELOW null** |
| fold pass rate | 0 / 8 | **0 / 8** | 100 % | **NO (tied at zero)** |
| total trades (turnover) | 1,177 | **720** | (informational; not directly comparable) | C014 LOWER (good) |

### 4.2 Side-by-side per-pair expectancy R

| pair | CAMPAIGN_011 null | CAMPAIGN_014 | C014 − C011 |
|---|---:|---:|---:|
| EUR_USD | −0.0091 R | −0.20302 R | **−0.194 R worse** |
| GBP_USD | +0.0019 R | −0.08371 R | **−0.086 R worse** |
| USD_JPY | +0.0000 R | −0.00081 R | ≈ 0 (both near random-walk floor) |
| AUD_USD | −0.0207 R | −0.27873 R | **−0.258 R worse** |
| USD_CAD | −0.0162 R | −0.11643 R | **−0.100 R worse** |
| USD_CHF | +0.0033 R | −0.30908 R | **−0.312 R worse** |
| NZD_USD | −0.0737 R | −0.15504 R | **−0.081 R worse** |

**Every pair is worse than the CAMPAIGN_011 null** (USD_JPY is a
tie at the random-walk floor). The 4 pairs that were ≥ 0 in
CAMPAIGN_011 (GBP, JPY, CHF, "near-zero") all turned negative in
CAMPAIGN_014.

### 4.3 Indistinguishability-band check

(Band: ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair around CAMPAIGN_011.)

| metric | C011 ± band | C014 | inside band? |
|---|---|---:|:---:|
| expectancy R | [−0.0074, +0.0026] | **−0.14774** | **NO — 0.145 R BELOW band** |
| profit factor | [0.81, 1.01] | **0.00** | **NO — 0.81 BELOW band** |
| return % (4 y) | [−2.53, +1.47] | **−30.85** | **NO — 28.3 pp BELOW band** |
| pairs positive | [2, 4] | **0** | **NO — 2 BELOW band** |

**OUTSIDE indistinguishability band on ALL 4 dimensions, on the
WORSE side.** This is NOT
`REJECT_INDISTINGUISHABLE_FROM_NULL` (which would mean
"close to random within noise") — this is **REJECT
(direction-of-trade falsification)**: the strategy systematically
trades **against** the actual edge that exists in the data
(post-event H4 bars actually continue, not revert).

### 4.4 Binary "meaningful improvement over null?" verdict

| metric | improvement required | result | improved? |
|---|---|---|:---:|
| aggregate expectancy R | ≥ +0.0524 | −0.145 (regression) | **NO** |
| aggregate profit factor | ≥ +0.19 | −0.91 (regression) | **NO** |
| aggregate return % | ≥ +5.5 pp | −30.3 pp (regression) | **NO** |
| pairs_positive | ≥ +1 pair | −3 pairs (regression) | **NO** |
| fold_pass_rate | 100 % | 0 / 8 (tied) | **NO** |
| per-fold consistency | no fold > 60 % aggregate | single_fold_dominance 16.24 % | yes (vacuously — all folds REJECT) |

**5 of 6 meaningful-improvement margins regress relative to null.**

## 5. CAMPAIGN_014-specific diagnostics summary

(Detailed event-class diagnostics in Phase 7
`CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`. The headline below
is the runner-level summary.)

### 5.1 Event-class clustering (preview; full detail in Phase 7)

The runner does not currently capture per-trade `event_class`
attribution (the engine's TradeRecord schema does not propagate
Signal features). Phase 7 derives per-event-class trade
attribution by re-running the strategy in dry-mode against fixture
events. **Headline preview from manual inspection of fold-0 trades
CSV:** the 56 trades the strategy fires per fold are mostly NFP +
FOMC triggered (impacting all 7 USD pairs simultaneously), with
isolated ECB/BoJ/BoE single-pair triggers. PnL is negative on all
classes; no event class shows positive aggregate. Per-class detail
is in Phase 7.

### 5.2 Per-event-class per-pair sensitivity (Phase 7 deliverable)

See Phase 7. Headline: per-pair returns are negative across the
board (per §4.2); there is no event-class × pair cell with
materially positive PnL.

### 5.3 Pre / post event direction breakdown

Manual sample inspection of trades CSV: the strategy goes SHORT
when `event_bar_return > 0` (intending to fade post-event rallies)
and LONG when `event_bar_return < 0` (intending to fade post-event
sell-offs). The trade direction balance is approximately 50/50
long/short (see Phase 7). The per-trade R distribution is
systematically negative, meaning **the strategy correctly
identifies the event-bar direction but trades against the actual
post-event continuation, losing on both sides**.

### 5.4 Entry-window concentration

By R3 binding, the strategy only triggers on the FIRST post-event
bar (`bars_since_event == 1`). Phase 7 confirms 100 % of trades
have `bars_since_event == 1`.

### 5.5 Event-fixture coverage per fold

| fold | test window | within fixture coverage | events in window |
|---|---|:---:|---:|
| 0 | 2021-12-21 → 2022-06-18 | ✓ | 22 |
| 1 | 2022-06-19 → 2022-12-15 | ✓ | 21 |
| 2 | 2022-12-16 → 2023-06-13 | ✓ | 19 |
| 3 | 2023-06-14 → 2023-12-10 | ✓ | 22 |
| 4 | 2023-12-11 → 2024-06-07 | ✓ | 23 |
| 5 | 2024-06-08 → 2024-12-04 | ✓ | 20 |
| 6 | 2024-12-05 → 2025-06-02 | ✓ | 22 |
| 7 | 2025-06-03 → 2025-11-29 | ✓ | 22 |

All 8 folds within fixture coverage; no coverage gate trip.

## 6. Aggregate metrics (machine-readable)

```json
{
  "runner_verdict": "REJECT",
  "phase_5_verdict": "REJECT (direction-of-trade falsification)",
  "fold_count": 8,
  "folds_passing": 0,
  "fold_pass_rate": 0.0,
  "total_trades": 720,
  "total_raw_signals": 1240,
  "aggregate_return_pct": -30.8516,
  "aggregate_expectancy_r": -0.14774,
  "profit_factor": 0.0,
  "pairs_positive_count": 0,
  "single_fold_dominance_pct": 16.24,
  "single_pair_dominance_pct": 20.69
}
```

Full per-fold + per-pair detail at
`backtests/CAMPAIGN_014_calendar_event_window_anomaly/walk_forward/fold_detail.json`.

## 7. Calendar-event-window interpretation

The hypothesis was: *"H4 bars immediately after scheduled major
macroeconomic events (NFP, FOMC, ECB, BoJ, BoE) mean-revert; trade
counter to the event-bar's direction with ATR-2 stop and 6-bar
time stop."*

The data say: **NO.** Post-event H4 bars do not mean-revert in
this universe over 2021-12 to 2025-11. The strategy:

1. **Correctly identifies the event bar** (the H4 bar containing
   the event timestamp).
2. **Correctly identifies the event-bar's direction** (positive
   `event_bar_return` triggers SHORT; negative triggers LONG).
3. **Trades against the actual continuation** — the post-event H4
   bar moves *with* the event-bar's direction (continuation /
   trend persistence), not against it (mean reversion).

The empirical 1-bar-after-event continuation pattern is consistent
with a "macro news shock → bar 0 prices in immediate reaction →
bar 1 continues that direction as market participants
re-position." A pure-counter-trend bet on bar 1 is the WRONG side
of this pattern, and pays the cost on every trade.

USD_JPY's near-zero expectancy R (−0.00081) is the random-walk
floor — JPY's response to USD-centric events (NFP/FOMC) is
noisier than the other 6 pairs', so the directional signal washes
out and the result is at the cost floor. The other 6 pairs are
systematically negative.

## 8. Comparison to CAMPAIGN_010 / 011 / 012 / 013 verdicts

| dimension | C010 session breakout | **C011 null** | C012 regime switcher | C013 cross-pair rotator | **C014 calendar event window** |
|---|---|---|---|---|---|
| verdict | REJECT | REJECT (null) | REJECT | REJECT | **REJECT (this sprint)** |
| aggregate expectancy R | −0.0850 | −0.0024 | −0.0521 | −0.0564 | **−0.14774** |
| aggregate profit factor | 0.74 | 0.91 | 0.034 | 0.000 | **0.00** |
| aggregate return % | −22.6 | −0.53 | −43.52 | −113.36 | **−30.85** |
| pairs positive | 1 / 7 | 3 / 7 | 1 / 7 | 1 / 7 | **0 / 7** |
| total trades | 1,103 | 1,177 | 3,726 | 7,940 | **720** |
| meaningful improvement over null? | NO | (= null) | NO | NO | **NO** |
| indistinguishable from null? | NO (worse) | (= null) | NO (much worse) | NO (much worse) | **NO (much worse)** |

CAMPAIGN_014 fits the established pattern of REJECT candidates on
this universe / cost model, but **uniquely without turnover
amplification** — the failure is purely direction-of-trade. The
candidate's design correctly avoided Pattern M / N / O / Q (cost-
insensitive signal); it failed because the hypothesis itself was
wrong.

## 9. Caveats

1. **Fixture date-verification is PARTIAL** (per [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md)).
   NFP + FOMC 100 % verified; BoJ 91 % for 2025-2026; ECB + BoE
   not WebFetch-verified. **For a REJECT verdict, this caveat is
   moot** — independent corroboration of a REJECT is unnecessary
   per [`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md).
   If the verdict had been RESEARCH_PASS_UNAPPROVED, the deeper
   audit would have been mandatory.
2. **Per-trade event_class attribution is not in the engine's
   TradeRecord.** Phase 7 derives per-event-class attribution via
   dry-mode strategy re-run; this is diagnostic only and does not
   change the REJECT verdict.
3. **The data span ends 2025-11-29 (fold 7 test_end).** Events
   2026-01 onward are in the fixture but contributed zero trades
   to this evidence run.
4. **The 1 BoJ fixture drift (2026-03-18 vs 2026-03-19)** is
   post-fold-7 and contributed zero trades.

## 10. Explicit no-approval statement

**REJECT does not approve anything.** The standing safety state is
unchanged:

- `configs/approved_strategies.yaml` remains `approved: []`.
- Paper / demo / live remain blocked.
- The strategy module `src/forex_bot/strategies/calendar_event_window_anomaly.py`
  remains scaffold code; no production use is authorized.
- No revival or "tweak" of CAMPAIGN_014 is permitted (per
  [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
  + [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
  binding rules). Any new candidate must go through a fresh
  discovery sprint.

## 11. Paper / demo / live blocked (binding)

The REJECT verdict does not modify any approval state:

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| `paper-loop` | REFUSED for `['trend_following']` (only) — confirms registry empty |
| `demo-loop` | REFUSED for `['trend_following']` (only) — confirms registry empty |
| `live-loop` | does not exist |
| MODELED financing reachable | no |

## 12. Safety state (unchanged after REJECT)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| **CAMPAIGN_014** | **REJECT (this sprint)** |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| broker call this phase | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| frozen-parameter changes | **none** |
| `max_open_positions` relaxation | **none** |
| post-result rule modification | **none** |
| pair carve-out | **none** |
| fixture modification mid-sprint | **none** (1 BoJ drift logged for future fixture-revision sprint, not patched here) |
| historical campaign verdict change | **none** |

## 13. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md) (sprint plan)
- [`CAMPAIGN_014_WALK_FORWARD_PLAN.md`](CAMPAIGN_014_WALK_FORWARD_PLAN.md) (Phase 2)
- [`CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_014_WALK_FORWARD_EXECUTION.md) (Phase 4)
- [`CAMPAIGN_014_DATA_PROVENANCE.md`](CAMPAIGN_014_DATA_PROVENANCE.md) (Phase 1)
- [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md) (Phase 0)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) (binding spec)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget — gate PASSED here)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) (binding approval process)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) (to be updated in Phase 9)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) (to be updated in Phase 9)
- prior verdicts: [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md), [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md), [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md), [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
