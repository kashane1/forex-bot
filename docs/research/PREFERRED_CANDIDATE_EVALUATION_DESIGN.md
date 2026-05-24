# Preferred Candidate Evaluation Design

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-001`
`strategy_evidence: false`

The Phase B4 finalised evidence-pipeline design for the preferred
candidate **C1 — Asian-range / London-open session breakout** from
[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md).
This document **designs the evaluation**; it does **not** run it,
does **not** implement the strategy, and does **not** approve
anything.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. Every gate, fold plan, and pass /
> fail threshold below is frozen for the future implementation
> sprint **only after that sprint commits a `<CAMPAIGN>_PRECOMMIT.md`
> referencing this design verbatim**. Until then, this document is
> a *design*, not a commitment to run.

## 1. Candidate name & version

| field | value |
|---|---|
| `Strategy.name` | `session_breakout` |
| `Strategy.version` | `0.1.0-c010` |
| nickname | "Asian-range / London-open session breakout" |
| campaign label | **CAMPAIGN_010** |
| protocol category | Session-of-day breakout (non-CAMPAIGN_004 flavour) per [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md) §4 |
| future implementation branch | **`research-asian-london-session-breakout-001`** |

## 2. Hypothesis (verbatim, frozen)

> The H4 bar covering the first London session (roughly
> 07:00–11:00 UTC) is preceded by a low-liquidity Asian-session H4
> bar. If the Asian-session H4 bar establishes a clean range AND
> the London-session H4 bar's close penetrates that range in one
> direction, the directional move tends to *continue* through the
> London/NY-overlap H4 bar.
>
> The edge — if any — comes from the liquidity-flow event of the
> London open, not from trend, not from compression, not from
> pullback, and not from mean-reversion. A frozen-parameter,
> walk-forward evaluation with strict pass-rate gates on the seven
> CAMPAIGN_002 H4 pairs will either confirm a small positive
> expectancy *net of conservative-stress financing*, or REJECT the
> candidate.

The hypothesis is *falsifiable* by the per-fold pass-rate gate
(§9) and the aggregate expectancy gate (§10). No
"directional bias" tweak is permitted post-hoc; the campaign's
pre-commit doc will record this hypothesis verbatim.

## 3. Frozen parameter set

The parameters are **final** for the future scaffold sprint's
pre-commit doc. Any later change creates a *new* candidate,
requiring its own discovery / evaluation cycle.

| parameter | value | rationale |
|---|---|---|
| `asian_session_hours_utc_start` | `22` | covers the late-NY-late + Asian sessions on UTC. |
| `asian_session_hours_utc_end` | `6` | 8 hours of low-liquidity bar coverage on H4. |
| `london_session_hours_utc_start` | `6` | first London hours on UTC. |
| `london_session_hours_utc_end` | `12` | 6-hour London-only window before the NY overlap. |
| `min_asian_range_atr_fraction` | `0.30` | the Asian-bar range (`high[t-1] - low[t-1]`) must be ≥ 30 % of ATR-14 at bar `t-1` to count as a clean range. |
| `atr_lookback` | `14` | standard Wilder ATR. |
| `atr_stop_multiple` | `2.0` | same value used by CAMPAIGN_004 and CAMPAIGN_007 — stop sizing is **not** the experimental variable. |
| `trailing_stop_atr_multiple` | `None` | v1 has no trailing stop; the exit logic must stay minimal and falsifiable. |
| `time_stop_bars` | `6` | ≈ 1 trading day on H4 — the candidate's thesis is intraday-window. |
| `min_atr_pips` | `{}` (none) | no per-pair ATR floor in v1 — the universe-wide range fraction gate is the sole regime filter. |
| `risk_per_trade_pct` | `0.25` | matches every prior campaign — risk is fixed, not the variable under test. |
| `max_positions_per_instrument` | `1` | inherits from `RiskConfig` (hard prohibition; cannot be relaxed). |

The candidate emits **one** signal per London H4 bar per
instrument, never more. It blocks new entries while an
instrument has an open position (the same pattern as
`TrendFollowingStrategy.generate_signal`, lines 82–84).

### 3.1 Why no per-pair tuning

The protocol's §12 audit treats implicit per-pair tuning as a
disqualifier. The session-breakout candidate uses **one**
universal parameter set across all seven CAMPAIGN_002 H4 pairs.
The aggregate gate (§10) requires ≥ 4 of 7 pairs positive;
single-pair save is disallowed.

### 3.2 Why no parameter sweep

A robustness grid is explicitly forbidden (§12). The candidate
commits *one* parameter combination. If the candidate fails
its gates, the verdict is REJECT; the next discovery cycle
proposes a *different* family, not a re-tune of this one.

## 4. Allowed universe

| pair | role |
|---|---|
| EUR_USD | core; carries the most liquid Asian-range definition |
| GBP_USD | core |
| USD_JPY | core; USD-base notional path |
| AUD_USD | core |
| USD_CAD | core; USD-base notional path |
| USD_CHF | core; USD-base notional path |
| NZD_USD | core; the same NZD_USD that CAMPAIGN_007 excluded on cost grounds is re-included here because the session-breakout's holding-period is short enough that cost asymmetry is bounded |

Universe is identical to the rate-fixture-expansion set
([`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
§1). No new pair is added. No subset is taken.

## 5. Timeframe

| field | value |
|---|---|
| primary timeframe | H4 (entry, exit, stop) |
| session-of-day input | H4 timestamp's UTC hour (derived; no new data) |
| H4 alignment | OANDA practice H4 candles, `daily_alignment=17` NY (the project standard) |
| D1 / H1 dependency | **none** |

## 6. Data requirements

| requirement | source | already present? |
|---|---|:--:|
| OANDA practice H4 candles for the 7-pair universe, 2020-01-01 → 2026-05-20 | local SQLite store (e.g. `data/campaign_002.sqlite3`, provenance hashes recorded) | ✓ |
| Per-bar UTC timestamps (already on `CandleFrame.df.index`) | candle store | ✓ |
| Instrument metadata (pip size, rounding) | repo metadata | ✓ |
| Conservative-stress financing rate source | [`research/financing/`](../../research/financing/) `default_stress_rate_source()` | ✓ |
| Per-pair `TableRateSource` for the overlay (one fixture per pair) | [`research/financing/fixtures/`](../../research/financing/fixtures/) `rates_two_week_*.json` | ✓ |
| Walk-forward harness | [`research/walk_forward/`](../../research/walk_forward/) | ✓ |

**No new fetch is required.** The candidate is structurally
testable on the data the repo already has.

## 7. Walk-forward fold design

Per
[`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
and the harness's `rolling_window_plan`:

| field | value |
|---|---|
| `SplitStyle` | `rolling` |
| `parameter_mode` | `frozen` (only authorized mode) |
| universe start | `2020-01-01` |
| universe end | `2026-05-20` |
| `train_days` | `540` (~18 months) |
| `validation_days` | `180` (~6 months) |
| `test_days` | `180` (~6 months) |
| `step_days` | `180` |
| minimum fold count | `6` |
| expected fold count | `≈ 9` given the universe span |

### 7.1 Fold-by-fold sketch (illustrative; the harness emits the authoritative plan)

| fold # | train start | train end | val end | test end |
|---:|---|---|---|---|
| 1 | 2020-01-01 | 2021-06-25 | 2021-12-22 | 2022-06-20 |
| 2 | 2020-06-29 | 2021-12-22 | 2022-06-20 | 2022-12-17 |
| 3 | 2020-12-26 | 2022-06-20 | 2022-12-17 | 2023-06-15 |
| 4 | 2021-06-24 | 2022-12-17 | 2023-06-15 | 2023-12-12 |
| 5 | 2021-12-21 | 2023-06-15 | 2023-12-12 | 2024-06-09 |
| 6 | 2022-06-19 | 2023-12-12 | 2024-06-09 | 2024-12-06 |
| 7 | 2022-12-16 | 2024-06-09 | 2024-12-06 | 2025-06-04 |
| 8 | 2023-06-14 | 2024-12-06 | 2025-06-04 | 2025-12-01 |
| 9 | 2023-12-11 | 2025-06-04 | 2025-12-01 | 2026-05-30 |

(Fold 9's test window may be trimmed to the actual universe
end; the harness's `validate_plan` enforces in-universe.)

The plan is generated by:

```python
from datetime import date
from research.walk_forward import rolling_window_plan, validate_plan

plan = rolling_window_plan(
    universe_start=date(2020, 1, 1),
    universe_end=date(2026, 5, 20),
    train_days=540,
    validation_days=180,
    test_days=180,
    step_days=180,
    parameter_mode="frozen",
)
validate_plan(plan)  # min 3 folds, forward-only, no overlap, in-universe
```

The future scaffold sprint commits the rendered `plan.json` and
`plan.md` (per
[`run_walk_forward_dry_run.py`](../../scripts/run_walk_forward_dry_run.py))
to `backtests/CAMPAIGN_010_session_breakout/walk_forward/`.

### 7.2 What each fold gates

- **Train fold** — screen the strategy on the candidate's
  pre-committed train-window gates (§9 row "train"). If train
  fails, the validation and test windows for **that fold** are
  not opened.
- **Validation fold** — screen on the validation gates (§9 row
  "validation"). If validation fails, the test window is not
  opened. (This mirrors the Marathon-001 discipline.)
- **Test fold** — produces the fold's evidence row. Pass / fail
  per the test-fold gates (§9 row "test").

A fold's `FoldMetrics.passed_gates` is `True` only when **all
three** of its train / validation / test gates pass.

## 8. Per-fold pass / fail gates

Every gate runs **after** the conservative-stress financing
overlay is applied. The candidate's headline number is *net*
of financing.

### 8.1 Train-fold gates

| gate | threshold |
|---|---|
| `train.expectancy_R_net_of_stress_financing` | ≥ `0.00` (must be non-negative) |
| `train.trade_count` | ≥ `30` |
| `train.no_lookahead_audit` | PASS (every signal computed from bars strictly < t; grep + structural test) |

### 8.2 Validation-fold gates

| gate | threshold |
|---|---|
| `validation.expectancy_R_net_of_stress_financing` | ≥ `0.05 R` |
| `validation.profit_factor_net_of_stress_financing` | ≥ `1.05` |
| `validation.pairs_positive_net_of_stress_financing` | ≥ `3 of 7` |
| `validation.trade_count` | ≥ `30` |

### 8.3 Test-fold gates

| gate | threshold |
|---|---|
| `test.expectancy_R_net_of_stress_financing` | ≥ `0.05 R` |
| `test.profit_factor_net_of_stress_financing` | ≥ `1.10` |
| `test.pairs_positive_net_of_stress_financing` | ≥ `4 of 7` |
| `test.trade_count` | ≥ `30` |
| `test.single_pair_dominance` | ≤ `60 %` of test-fold PnL |

## 9. Aggregate gates

Computed across the test folds (the test-fold rows the harness
emits into `AggregateMetrics`):

| gate | threshold |
|---|---|
| `aggregate.fold_pass_rate` | `100 %` — **every test fold must pass** (strict-pass) |
| `aggregate.fold_count` | ≥ `6` |
| `aggregate.expectancy_R_net_of_stress_financing` | ≥ `0.05 R` |
| `aggregate.profit_factor_net_of_stress_financing` | ≥ `1.10` |
| `aggregate.pairs_positive` | ≥ `4 of 7` |
| `aggregate.trade_count` | ≥ `200` |
| `aggregate.single_fold_dominance` | ≤ `60 %` of aggregate test-fold PnL |
| `aggregate.single_pair_dominance` | ≤ `40 %` of aggregate test-fold PnL |

A `fold_pass_rate` < 100 % triggers REJECT regardless of how
many folds passed. This is deliberately strict: the candidate
is being designed under post-Marathon-001 discipline, where
relaxing a single gate after seeing results is a hard-no.

## 10. Financing overlay gates

Computed via the research calculator on the candidate's full
test-fold trade list per fold and aggregate.

The candidate's report **must** embed verbatim:

- `financing_treatment` (`estimated`)
- `financing_in_engine_pnl` (`false`)
- `financing_is_live_blocker` (`true`)
- `cashflow_home_total` (per fold and aggregate, conservative-
  stress source)
- `cashflow_home_stress_total` (per fold and aggregate)
- `missing_rate_event_count`
- per-pair `TableRateSource` overlay (one entry per pair, using
  the committed `rates_two_week_*.json` fixture)

| gate | threshold |
|---|---|
| `financing.conservative_stress_run_does_not_flip_verdict` | If the headline PnL passes a gate, the conservative-stress overlay must not push the *same* gate's metric below threshold. |
| `financing.modeled_refused` | The candidate's report explicitly carries `financing_treatment ≠ "modeled"`. (Defense-in-depth; the rate sources refuse MODELED at construction.) |
| `financing.missing_rate_event_count` | Must be `0` when run against the committed per-pair `TableRateSource` fixtures (which span only a two-week sample — for the campaign run, the future scaffold sprint will either extend the fixture window or use `default_stress_rate_source()` for the full universe; the design notes both options below). |

### 10.1 Two-week vs full-universe rate fixtures (design note)

The committed per-pair rate fixtures span two weeks each — a
deliberate choice from the bp/day-expansion sprint (small,
synthetic, reviewable). For the candidate's full 2020-2026
walk-forward, the future scaffold sprint must choose **one**
of:

1. **Use `default_stress_rate_source()`** for the full window.
   This is the simplest path; the overlay is a flat
   conservative debit-on-both-sides per pair. The headline PnL
   gate uses this. (Recommended for v1.)
2. **Extend the per-pair rate fixtures** to span the full
   2020-2026 universe. This is a separate, future
   `research-financing-multi-year-fixture-expansion-001` sprint
   that the candidate does not assume.

Option 1 is the **assumed default** for the candidate's first
walk-forward run. The candidate's pre-commit doc will record
the choice verbatim.

## 11. Risk-engine diagnostic gates

Computed via the same `RiskEngine.evaluate(mode='backtest')`
path the bespoke engine already uses. The candidate's report
must include the standard diagnostic checklist from
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§9 with the following thresholds:

| diagnostic | expected behaviour | flag if … |
|---|---|---|
| per-pair exposure trace at fold boundaries | matches `RiskEngine` sizing | any fold > 0.30 % equity exposure |
| max concurrent open positions | matches signal frequency | > 3 across the universe |
| max aggregate notional | bounded by `risk_per_trade_pct` + `max_open_positions` | > 6 % NAV |
| correlation-cap activation count | bounded | > 25 % of signals |
| daily / weekly loss-limit activation count | bounded | > 5 in any fold |
| session-blackout activation count | bounded | > 10 % of signals |

These diagnostics **do not gate the verdict** (they are
informational only) — they exist so a future paper-promotion
review has the risk-engine picture without re-running the
campaign.

## 12. No-lookahead checks

The candidate is structurally no-lookahead because the entry
rule uses only:

- `high[t-1]`, `low[t-1]` (the prior Asian H4 bar)
- `close[t]` (the current London H4 bar's close, taken from a
  *completed* H4 bar via `CandleFrame.completed_only()`)
- `atr_14[t-1]` (computed from bars strictly before `t`)

The future scaffold sprint will add:

- a unit test that asserts the strategy emits **no signal**
  when fed a `CandleFrame` whose latest bar is incomplete (the
  standard pattern in `tests/unit/test_strategies.py`);
- a structural assertion that the strategy module does not
  reference `df.iloc[-1]` features computed across bar `t`'s
  high / low (only `close[t]` is allowed for bar `t`);
- a grep audit at pre-commit time that no `range(0, ...)` or
  `.shift(-N)` (N > 0) appears in the strategy module — both
  are common lookahead anti-patterns.

The walk-forward harness's plan-level rails (no consecutive
test-window overlap, forward-only ordering, all boundaries
in-universe) provide the orthogonal fold-level no-leakage
check.

## 13. Minimum trade count

Per fold:

- `train.trade_count` ≥ 30
- `validation.trade_count` ≥ 30
- `test.trade_count` ≥ 30

Aggregate (across test folds):

- `aggregate.trade_count` ≥ 200

A candidate that fires fewer than ~30 trades per fold on a 7-pair
universe is producing too sparse a signal to support an
expectancy claim. The session-breakout's structural firing rate
— one London-bar opportunity per pair per trading day —
projects to ~5 × 7 × 180 / 365 ≈ 17 signal *opportunities* per
fold per pair, ~120 per fold across the universe before the
range-fraction gate trims them. The 30-per-fold minimum is the
floor below which the design is structurally too quiet.

## 14. Dominance checks

| check | threshold |
|---|---|
| single-pair dominance (test fold) | no single pair contributes > 60 % of the test-fold's PnL |
| single-pair dominance (aggregate) | no single pair contributes > 40 % of the aggregate test-fold PnL |
| single-fold dominance (aggregate) | no single fold contributes > 60 % of the aggregate test-fold PnL |

A breach is REJECT — the candidate cannot claim a universe-wide
edge if it depends on one pair or one fold.

## 15. Rejection criteria (summary)

A REJECT verdict is mandatory if **any** of these hold:

- any train, validation, or test fold's gates fail;
- `aggregate.fold_pass_rate` < 100 %;
- `aggregate.expectancy_R_net_of_stress_financing` < 0.05 R;
- `aggregate.trade_count` < 200;
- any dominance threshold (§14) is breached;
- the conservative-stress financing overlay flips a passing
  gate to failing;
- the no-lookahead checks (§12) fail;
- the report cannot embed the required financing fields (§10);
- the risk-engine diagnostic checklist (§11) is missing.

No gate is relaxed after seeing results. A campaign report
emitting REJECT is the final verdict; the next discovery cycle
proposes a different family.

## 16. Required artifacts (future scaffold sprint deliverables)

The future `research-asian-london-session-breakout-001` sprint
must commit **all** of these before its candidate verdict counts
as evidence:

| artifact | location |
|---|---|
| Pre-commit doc | `docs/research/CAMPAIGN_010_SESSION_BREAKOUT_PRECOMMIT.md` (cites this design verbatim) |
| Strategy module | `src/forex_bot/strategies/session_breakout.py` |
| StrategyConfig sub-model | `src/forex_bot/config.py` (`SessionBreakoutStrategyConfig` + `StrategyConfig.session_breakout` slot) |
| Strategy test suite | `tests/unit/test_session_breakout.py` (no-lookahead, signal-shape, in-position blocking, NaN guards, session-of-day boundary cases) |
| Walk-forward plan | `backtests/CAMPAIGN_010_session_breakout/walk_forward/plan.json` and `plan.md` |
| Walk-forward results | `backtests/CAMPAIGN_010_session_breakout/walk_forward/results.json` and `results.md` |
| Per-pair financing overlay | `backtests/CAMPAIGN_010_session_breakout/financing/financing_run.json` and `financing_run.md` |
| Campaign report | `backtests/CAMPAIGN_010_SESSION_BREAKOUT_REPORT.md` (headline + per-pair + per-fold + financing + risk-engine diagnostic) |
| Manifest entry | `docs/research/EVIDENCE_MANIFEST.json` row with `strategy_approved: false` |
| Evidence-index row | `docs/research/EVIDENCE_INDEX.md` |
| Audit-passes | `python scripts/validate_research_archive.py`, `python scripts/check_research_freeze.py`, `python scripts/scan_artifacts_for_secrets.py`, `python -m pytest -q` |

A REJECT verdict is documented in a campaign post-mortem
(`docs/research/CAMPAIGN_010_POSTMORTEM.md`); a non-REJECT
verdict does **not** automatically approve — paper / demo
promotion still requires the human approval step per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
and the six-evidence ladder per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8.

## 17. Independent corroboration

Per the six-evidence ladder row 5, the candidate must be
corroborated by either:

- an **exact custom-engine reproduction** within the bespoke
  engine (the candidate's deterministic-replay property already
  gives this for free if the engine is fed identical inputs); or
- a **free / local parity verifier** WARN-band corroboration
  per [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md).

The verifier currently corroborates the trend-following family
specifically. Adding session-breakout coverage is a separate,
future verifier-side sprint and is **not** assumed by this
design. If the candidate's first walk-forward passes its gates,
the project will then choose between (a) accepting deterministic
reproducibility as the corroboration for v1 and explicitly
documenting that the verifier hasn't been extended yet, or (b)
opening a verifier-extension sprint before any paper promotion.

## 18. Future implementation branch

| field | value |
|---|---|
| **branch name** | `research-asian-london-session-breakout-001` |
| **first commit** | adds the `StrategyConfig` slot, the strategy module, and the candidate's test suite |
| **second commit** | adds the pre-commit doc with the §3 parameters and §8–§15 gates copied verbatim |
| **third commit** | runs the walk-forward plan generation + dry-run + commits `plan.json` / `plan.md` |
| **fourth commit** | runs the per-fold backtests + commits `results.json` / `results.md` + per-pair financing overlay |
| **fifth commit** | writes the campaign report + manifest update + evidence-index update + status doc |
| **NOT in scope of this design** | the actual decision to approve the candidate for paper trading; that is a separate, human-authorized step *after* the campaign reports a non-REJECT verdict and *all six* evidence items exist |

The future sprint inherits this design's parameters, gates, and
audit checks verbatim. Editing any of §3 / §7–§15 in the future
sprint constitutes a *new* candidate and requires its own
discovery cycle.

## 19. Pre-flight checklist for the future scaffold sprint

Before any code is written under
`research-asian-london-session-breakout-001`, the future-sprint
operator must:

1. Confirm `git status` is clean.
2. Confirm `configs/approved_strategies.yaml` is `approved: []`.
3. Re-read this design and the protocol verbatim.
4. Verify the H4 OANDA store for the seven pairs has not
   drifted since `data/campaign_002.sqlite3` (provenance hash
   check via `scripts/audit_h4_data_quality.py`).
5. Run the standing safety checks (archive validator, freeze
   checker, secret scanner, pytest suite) to confirm the
   baseline test count and zero failures.
6. Re-run the paper-loop / demo-loop refusal checks.
7. Confirm no `live-loop` command has been added.
8. Confirm no QuantConnect / LEAN re-introduction has occurred.

Only after these are clean may the scaffold sprint open its
first commit.

## 20. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- No code edited this phase.
- No campaign run.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 21. Cross-links

- Sprint plan:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_001_PLAN.md)
- Protocol:
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
- Inventory:
  [`STRATEGY_FRAMEWORK_INVENTORY.md`](STRATEGY_FRAMEWORK_INVENTORY.md)
- Shortlist:
  [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
- Walk-forward protocol:
  [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- Walk-forward status:
  [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- Financing protocol:
  [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- Financing status:
  [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- Bp/day fixture status:
  [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- Six-evidence ladder:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8
- Free / local parity verifier:
  [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
- Evidence index:
  [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
