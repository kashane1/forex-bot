# CAMPAIGN_015 — Post-Run Interpretation

> **SUPERSEDED / STALE DUE TO DUPLICATE-CANDLE CONTAMINATION** — see
> [`CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md`](CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md)
> and [`CAMPAIGN_015_DUPLICATE_CANDLE_CONTAMINATION_MEMO.md`](CAMPAIGN_015_DUPLICATE_CANDLE_CONTAMINATION_MEMO.md).

**Sprint:** [CAMPAIGN_015 Post-Run Diagnostics 001](CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md)
**Branch:** `research-campaign-015-post-run-diagnostics-001`
**Date:** 2026-05-26
**Strategy under inspection:** `failed_breakout_reversal 0.1.0-c015`
**Runner verdict:** **REJECT**
**Final post-run interpretation label:** **`SPARSE_BUT_PROMISING` (with concentration caveats)**
**Final recommendation:** **`COLLECT_MORE_DATA_FIRST`** (downgraded from
`RESEARCH_C015_VARIANT_PRECOMMIT` because the BT secondary lane is
BLOCKED and concentration in USD_CHF is meaningful).

> Interpretation document only. Does **NOT** approve any strategy,
> does **NOT** relax any gate, does **NOT** revise the runner verdict.
> `configs/approved_strategies.yaml` remains `approved: []`.

This memo is the human-readable answer to the sprint's core question:
*Is CAMPAIGN_015 a genuinely promising sparse edge that deserves a
future pre-committed follow-up candidate, or is it a fragile aggregate
artifact caused by a small number of lucky trades / pairs / folds?*

It draws strictly on the diagnostics from this sprint:

- Phase 0 — [rehydrate walk-forward](../../research/campaign_015/diagnostics/walk_forward_rehydrate/)
- Phase 1 — [Gate-failure autopsy](CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md)
- Phase 2 — [Concentration diagnostics](CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md)
- Phase 3 — [Null + anti-overfit diagnostic](CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md)
- Phase 4 — [Backtrader post-run comparison](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md) (`DATA_MISMATCH` → `BLOCKED`)

---

## 1 · Why did the runner REJECT despite +0.23 R aggregate expectancy?

Two pre-committed aggregate gates fail (at both base and 2x cost):

| failed gate | actual | required |
|---|---|---|
| `fold_pass_rate_ge_5_of_8` | 0 / 8 folds pass | ≥ 5 / 8 |
| `trade_count_min_200` | 164 trades | ≥ 200 |

Both failures trace to **per-fold trade-count sparsity**: at base
cost, every one of the 8 folds fails `trade_count_ge_30`
([series `[18, 26, 26, 28, 24, 14, 14, 14]`](CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md#2--which-exact-per-fold-gates-failed)).
With no fold clearing the per-fold gate set, the aggregate gate
`fold_pass_rate_ge_5_of_8` is mechanically locked to FAIL.

Every other aggregate gate **passes** — expectancy, PF, fold count,
pairs-positive, single-pair dominance, trade-count-max. The campaign
is genuinely above the quality floor; it fails the *robustness* gates.

---

## 2 · Is the result better than prior campaigns?

**Yes — and dramatically so.** All prior campaigns with completed
walk-forward results on the same universe show **negative** aggregate
expectancy at base cost:

| campaign | strategy | aggregate exp R (base) |
|---|---|---|
| CAMPAIGN_010 | `session_breakout` | -0.041 |
| CAMPAIGN_011 | `random_entry_anchor` (null) | -0.002 |
| CAMPAIGN_012 | `regime_switcher_atr_percentile` | -0.052 |
| CAMPAIGN_013 | `cross_pair_currency_strength_rotation` | -0.056 |
| CAMPAIGN_014 | `calendar_event_window_anomaly` | -0.148 |
| **CAMPAIGN_015** | **`failed_breakout_reversal`** | **+0.230** |

CAMPAIGN_015 is the first sprint candidate to clear the matched
random-entry null with statistical significance (per-fold gap mean
+0.225 R, t-stat +3.19 over n=8; LOO-min mean gap +0.184 R).
Anti-overfit classifier label: **`ROBUST_ABOVE_NULL`**.

This is the most affirmative diagnostic result in the project's history.
It is also the noisiest, the sparsest, and the most concentrated.

---

## 3 · Is the result robust enough for approval?

**No.** Approval is governed by:

- the runner's pre-committed gate set ⇒ **REJECT** (fold-pass-rate
  and trade-count both fail), AND
- the human review process keyed on `configs/approved_strategies.yaml`
  ⇒ unchanged at `approved: []`.

Neither this sprint nor any diagnostic can flip either lever. Even a
`ROBUST_ABOVE_NULL` anti-overfit label cannot — by design.

---

## 4 · Is the result promising enough for a follow-up?

**Yes, conditionally** — but the conditions are non-trivial. The
favorable signals are:

- aggregate expectancy R +0.23 (no other campaign came close);
- 7/8 folds non-negative on expectancy;
- 6/7 pairs aggregate-positive;
- LOO-fold expectancy never drops below +0.19 (no single-fold artifact);
- per-fold t-stat vs matched null is +3.19;
- all 7 binding anti-overfit gates pass;
- median per-fold expectancy +0.259 (close to mean +0.223 — i.e., not
  pulled by one outlier fold).

The unfavorable signals are:

- **sparsity**: 164 trades in 4 years × 7 pairs (≈ 6 trades/pair-year);
  every fold fails the 30-trade gate;
- **trade-level concentration**: top-5 trades = 77% of total R (88% at
  2x cost); top-3 = 48% of total R;
- **pair concentration (net R basis)**: USD_CHF = 54.5% of total R;
  dropping it (LOO-pair) cuts aggregate expectancy from +0.23 to +0.13;
- **right-skewed distribution**: median trade R is **negative**
  (-0.254); p25 and p10 sit at the -1.0 R stop floor; the upside is
  entirely in the upper tail (p90 +2.57, max +6.21);
- **headline-PF artifact**: the runner's PF=107.55 is a return_pct-
  denominator artifact (one negative pair). The honest trade-level PF
  is **1.48 base / 1.40 2xcost** — modest, not extraordinary;
- **BT secondary lane is BLOCKED**: cross-engine corroboration was not
  possible (data-provenance drift; an infra issue).

> The favorable and unfavorable signals are not contradictory; they
> simply measure different things. The classifier passes its
> *gross-positive-R-per-pair* concentration gate (USD_CHF at 30.2%,
> threshold 70%) because that lens averages winners and losers within
> a pair. The Phase 2 net-R view (USD_CHF at 54.5%) is the lens that
> matters for "would the edge survive if USD_CHF underperforms next
> year." Both are honest; both must be held together.

**Final label: `SPARSE_BUT_PROMISING`** with strong USD_CHF concentration
caveats. This is *not* `AGGREGATE_ARTIFACT` (no single-fold dominance,
LOO-fold expectancy never negative) and *not* `NULL_DOMINATED` (gap is
+0.225 R, t=3.19). It is a positive per-trade edge that the data is
too thin and the cell grid too concentrated to gate-pass.

---

## 5 · What is the dominant failure mode?

In rank order:

1. **Trade-count sparsity at the fold level.** Every fold fails
   `trade_count_ge_30`. This is the binding constraint on
   `fold_pass_rate_ge_5_of_8`. Counterfactually (NON-GATING), if
   trade-count were dropped, 5/8 folds would clear the remaining
   gates at base cost.
2. **Aggregate trade-count sparsity.** 164 trades < 200 minimum.
3. **Cell-level sparsity.** 30% of pair-fold cells have 0 or 1 trade;
   68% have ≤ 3 trades. A single trade swing dominates many cells.
4. **Pair concentration (USD_CHF).** Half the aggregate edge lives in
   one pair. LOO-pair cuts aggregate expectancy by 45%.
5. **Tail concentration.** 5 trades carry 77% of total R.

These are *all sparsity-derived*. Fold concentration is mild
(top fold = 32% of total R); cost-fragility is mild (expectancy
drops only 0.04 R from base to 2xcost).

---

## 6 · What is the safest next research move?

Several legitimate paths, ranked by what the diagnostics support:

### 6.1 — `COLLECT_MORE_DATA_FIRST` (recommended, primary)

The natural fix for sparsity is more data — more years, more pairs
(if the available H4 pool grows), and especially more years on the
existing pairs. With ~25 trades/fold currently, doubling the validation
window per fold could bring the fold trade count close to the
30-trade gate without changing the strategy or its frozen parameters.

This is the right call because:
- the per-trade edge is real (Phase 3 t-stat +3.19);
- the failure mode is sparsity, not concentration *of the edge in
  one fold* (LOO-fold preserves the edge);
- it does not require a strategy redesign;
- it does not bypass any gate.

A future infra sprint should:
- extend the universe to the deepest H4 history available,
- re-export the lean-parity CSVs in lock-step with their provenance
  JSONs (unblocking Phase 4),
- run **a fresh pre-committed campaign** with the same frozen
  CAMPAIGN_015 parameters on the extended universe.

This is **not** "tuning" — the parameters do not move. It is data
expansion.

### 6.2 — `RUN_BACKTRADER_OR_NULL_FIRST` (precondition for 6.1 or 6.3)

The Phase 4 BT lane is BLOCKED on data-provenance drift in
`research/lean_parity/exports/campaign_002_h4/`. A small infra sprint
should restore lock-step provenance, then re-run the BT comparison
against the rehydrate bespoke output. If BT disagrees with bespoke at
the trade level, every CAMPAIGN_015 number above is suspect — that
single result would change the picture.

This is a **hard precondition** for any further CAMPAIGN_015-derived
research.

### 6.3 — `RESEARCH_C015_VARIANT_PRECOMMIT` (Phase 6 candidate; conditional)

If 6.2 confirms bespoke and 6.1 yields more trades that still show a
positive per-trade edge, *then* a docs-only follow-up candidate design
becomes worth writing — e.g. a **structural change** (not a
parameter tweak) that addresses the cell-level sparsity, such as a
single-pair-declared variant or a lower-frequency confirmation gate.

Phase 6 of this sprint produces only a **docs-only** stub justifying
this future candidate, and only if the diagnostics in §4 support it.

### 6.4 — `STOP_C015` (rejected by the diagnostics)

The diagnostics do **not** support a STOP recommendation. The
campaign clears the matched random-entry null with significance and
shows a positive per-trade edge across 7/8 folds. STOP would be
appropriate for `AGGREGATE_ARTIFACT` or `NULL_DOMINATED`; this is
neither.

---

## 7 · Recommendation label

**`COLLECT_MORE_DATA_FIRST`**, with `RUN_BACKTRADER_OR_NULL_FIRST`
as a hard precondition for any subsequent CAMPAIGN_015-derived work.

This sprint does **not** itself unblock Phase 4 or run an extended
universe — both are infra sprint work. This sprint's output is the
honest interpretation memo and the diagnostic artifacts that the
next sprint can build on.

---

## 8 · Safety statement (verified one more time)

- `configs/approved_strategies.yaml` is `approved: []`. ✓
- Paper / demo / live loops refuse to start. ✓
- Runner verdict for CAMPAIGN_015 is REJECT (NOT_APPROVED). ✓
- No CAMPAIGN_015 parameter has been tuned. ✓
- No pre-committed gate has been relaxed. ✓
- No broker call was made; no live OANDA contact. ✓
- No prior campaign evidence was modified. ✓
- The local sqlite DB and lean_parity CSVs are gitignored symlinks
  from the main repo root; never committed. ✓
- Even the strongest diagnostic label (`ROBUST_ABOVE_NULL`) does not
  approve this strategy. ✓
