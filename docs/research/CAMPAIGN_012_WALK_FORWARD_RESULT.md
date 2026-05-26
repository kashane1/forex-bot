# CAMPAIGN_012 Walk-Forward Result (Phase 5)

**Date:** 2026-05-26 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

> **EVIDENCE INTEGRITY UNKNOWN — RERUN REQUIRED BEFORE USE.** Metrics and
> null-baseline comparison used pre-fix SQLite; CAMPAIGN_011 baseline is
> also pre-fix. REJECT verdict unchanged.

Formal Phase 5 verdict for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**.

> **Research verdict: `REJECT`.** 5 of 8 inherited aggregate gates
> fail; CAMPAIGN_012 is markedly worse than the CAMPAIGN_011 null
> baseline (well outside the indistinguishable-from-null band, in the
> worse direction).
>
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain REJECT and
> untouched. CAMPAIGN_011 is the **null baseline only**; this verdict
> does not revive CAMPAIGN_011 as a tradable strategy. Paper / demo /
> live remain blocked.

## 1. Research verdict

**`REJECT`** — not `REJECT_INDISTINGUISHABLE_FROM_NULL` (because
CAMPAIGN_012's metrics diverge from CAMPAIGN_011's *in the worse
direction*, far outside the symmetric indistinguishability band).

Rationale:

- **5 of 8 inherited aggregate gates FAIL** (see §2.2 for the table).
- **Aggregate expectancy −0.0521 R** is *worse* than CAMPAIGN_011's
  −0.0024 R by 0.0497 R — ~21 × the indistinguishability half-band
  (±0.005 R).
- **Aggregate return −43.52 % over 4 years** is *catastrophically
  worse* than CAMPAIGN_011's −0.53 % — ~22 × CAMPAIGN_011's loss in
  pure absolute terms.
- **Profit factor 0.034** is *vastly worse* than CAMPAIGN_011's 0.91
  — ~9 × the indistinguishability half-band (±0.10 PF).
- **Only 1 of 7 pairs positive** (USD_JPY at +0.0004 R, essentially
  zero) versus CAMPAIGN_011's 3 of 7 — *worse* by 2 pairs, exactly
  on the indistinguishability boundary (±2 pp = ±1 pair) in the worse
  direction.
- **0 of 8 folds passing** — same as CAMPAIGN_011 (the
  pass-rate-on-its-own does not differentiate; the other four metrics
  do).

The regime gate **did not rescue trend-following on H4 majors.** It
generated more trades than the null model (3,726 vs 1,177) without
improving signal quality — every additional trade incurred the same
spread + slippage + per-trade cost as the null model, accumulating
into a vastly worse aggregate return.

## 2. Inherited gate table

### 2.1 Per-fold gates (`CAMPAIGN_010 §10` / `CAMPAIGN_011 §11` verbatim)

| fold | trades | exp R | return % | PF | pairs+ / 7 | single-pair dom % | pass? |
|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 678 | −0.0815 | −13.29 | 0.016 | 1 | — | **REJECT** |
| 1 | 811 | −0.0680 | −12.94 | 0.097 | 1 | — | **REJECT** |
| 2 | 320 | −0.0787 | −7.68 | 0.030 | 1 | — | **REJECT** |
| 3 | 254 | −0.0424 | −2.83 | 0.455 | 1 | — | **REJECT** |
| 4 | 358 | −0.0437 | −2.05 | 0.557 | 3 | — | **REJECT** |
| 5 | 407 | −0.0077 | +1.52 | 1.363 | 3 | — | **REJECT** |
| 6 | 638 | −0.0365 | −4.76 | 0.482 | 1 | — | **REJECT** |
| 7 | 260 | −0.0221 | −1.50 | 0.568 | 3 | — | **REJECT** |

**0 / 8 folds pass.** All folds fail `expectancy_r ≥ 0.05` and
`profit_factor ≥ 1.10`. All folds also fail `pairs_positive ≥ 4 / 7`.
The best fold (fold 5) has a positive aggregate return but its
expectancy is still negative (−0.0077 R) and only 3 of 7 pairs are
positive.

### 2.2 Aggregate gates

| gate | threshold | observed | result |
|---|---|---|:---:|
| `fold_pass_rate_eq_100pct` | = 100 % | 0 % | **FAIL** |
| `fold_count_ge_6` | ≥ 6 | 8 | PASS |
| `expectancy_r_ge_0p05` | ≥ 0.05 R | −0.0521 R | **FAIL** |
| `profit_factor_ge_1p10` | ≥ 1.10 | 0.034 | **FAIL** |
| `trade_count_ge_200` | ≥ 200 | 3,726 | PASS |
| `pairs_positive_ge_4_of_7` | ≥ 4 / 7 | 1 / 7 | **FAIL** |
| `single_fold_dominance_le_60pct` | ≤ 60 % | 28.54 % | PASS |
| `single_pair_dominance_le_40pct` | ≤ 40 % | 22.39 % | PASS |

**5 of 8 aggregate gates FAIL.** Inherited-gate overall verdict:
`REJECT`.

## 3. Null-baseline comparison (binding; CAMPAIGN_011-derived)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3 + §8 + §9, this verdict doc applies the CAMPAIGN_011 null-baseline
comparison with explicit margins:

| metric | CAMPAIGN_011 floor | CAMPAIGN_012 result | difference | meaningful-improvement margin | beat margin? | in indistinguishability band (±)? |
|---|---:|---:|---:|---|:---:|:---:|
| aggregate expectancy R | −0.0024 | **−0.0521** | **−0.0497** | ≥ +0.0524 (→ ≥ 0.05 R) | **NO — WORSE** | NO (21 × half-band) |
| aggregate profit factor | 0.91 | **0.034** | **−0.876** | ≥ +0.19 (→ ≥ 1.10) | **NO — WORSE** | NO (9 × half-band) |
| aggregate return (4 y) | −0.53 % | **−43.52 %** | **−42.99 pp** | ≥ +5 % | **NO — WORSE** | NO (22 × half-band) |
| `pairs_positive` | 3 / 7 | **1 / 7** | **−2 pairs** | ≥ 4 / 7 | **NO — WORSE** | NO (= ±1-pair boundary, worse direction) |
| `fold_pass_rate` | 0 / 8 | **0 / 8** | 0 | 100 % | **NO** | YES (same as null) |
| `single_fold_dominance` | 40.1 % | 28.54 % | −11.6 pp | ≤ 60 % (CAMPAIGN_010 gate) | yes (within gate; not a beat margin) | n/a |

**Classification (per `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`
§8):**

- CAMPAIGN_012 does **NOT** meet the meaningful-improvement margins
  on any of the four binding axes (expectancy / PF / return /
  pairs-positive).
- CAMPAIGN_012 is **NOT** indistinguishable from null on the four
  binding axes either — it is **WORSE than null** on all four,
  outside the symmetric indistinguishability band on three of four
  (and exactly at the boundary on `pairs_positive`, in the worse
  direction).
- Therefore: **`REJECT`** (not `REJECT_INDISTINGUISHABLE_FROM_NULL`).

The regime gate's effect is not "noise around zero" (which would be
indistinguishable). It is **active destruction of equity** through
amplified trade count under the same cost model — the gate fires more
often than the null model's PRNG, and each additional trade pays the
same spread + slippage cost without an offsetting signal-quality
gain.

## 4. Aggregate metrics

| metric | value |
|---|---|
| fold count | 8 |
| folds passing all per-fold gates | 0 |
| fold pass rate | **0 / 8 = 0 %** |
| total trades across folds | 3,726 |
| aggregate expectancy R | **−0.0521** |
| aggregate return % (4-year window) | **−43.52 %** |
| profit factor | **0.034** |
| pairs_positive_count | **1 / 7** (only USD_JPY at +0.0004 R) |
| single_fold_dominance % | 28.54 % |
| single_pair_dominance % | 22.39 % |
| longest losing-pair run | NZD_USD (−0.108 R, 391 trades, −10.74 %) |
| best-fold return | fold 5: +1.52 % (still REJECT — expectancy −0.0077 R; pairs+ 3 / 7) |
| worst-fold return | fold 0: −13.29 % |

## 5. Fold metrics (compact reproduction)

(See [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
§6 for the full table.)

| # | test window | trades | exp R | return % | PF | DD % | win % | passes? |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | 678 | −0.0815 | −13.29 | 0.016 | −2.17 | 43.6 % | NO |
| 1 | 2022-06-19 → 2022-12-15 | 811 | −0.0680 | −12.94 | 0.097 | −2.41 | 45.8 % | NO |
| 2 | 2022-12-16 → 2023-06-13 | 320 | −0.0787 | −7.68 | 0.030 | −1.89 | 43.8 % | NO |
| 3 | 2023-06-14 → 2023-12-10 | 254 | −0.0424 | −2.83 | 0.455 | −1.03 | 46.8 % | NO |
| 4 | 2023-12-11 → 2024-06-07 | 358 | −0.0437 | −2.05 | 0.557 | −1.06 | 48.3 % | NO |
| 5 | 2024-06-08 → 2024-12-04 | 407 | −0.0077 | +1.52 | 1.363 | −1.11 | 50.1 % | NO |
| 6 | 2024-12-05 → 2025-06-02 | 638 | −0.0365 | −4.76 | 0.482 | −1.78 | 47.1 % | NO |
| 7 | 2025-06-03 → 2025-11-29 | 260 | −0.0221 | −1.50 | 0.568 | −1.35 | 46.6 % | NO |

## 6. Regime-specific interpretation

### 6.1 Why did the regime gate fail?

The C3 hypothesis was: "filter for HIGH-VOL regimes (top 30 % daily
ATR percentile), then take a 4-bar trend continuation; calm regimes
do not trade." The walk-forward result is incompatible with this
hypothesis:

1. **The regime gate did not improve signal quality.** Every per-fold
   expectancy is negative (range −0.0815 R to −0.0077 R; only fold 5
   approaches break-even). The per-pair signal is just as negative in
   HIGH-VOL regimes as it would be in LOW-VOL regimes, on this
   universe.

2. **The regime gate amplified trade count under the same cost
   model.** CAMPAIGN_012 placed **3,726 trades** vs CAMPAIGN_011's
   **1,177** (3.2 × as many). On a universe + cost model where each
   trade pays ~0.2 pip spread + slippage, more trades = larger
   aggregate cost drag. The regime feature does not gate against
   cost — only against percentile.

3. **The trend filter on H4 close-vs-close drift is not predictive
   on majors.** A 4-H4-bar (= 16 hour ≈ 1 trading day) close-to-
   close move with a 0.25 × ATR floor catches noise as readily as
   signal on these pairs. Per-pair expectancy is uniformly negative
   except USD_JPY (which sits at the random-walk floor +0.0004 R).

4. **USD_JPY's +0.0004 R signature is diagnostic.** USD_JPY produced
   624 trades across 8 folds with literally near-zero expectancy. The
   same near-exact-zero appeared in CAMPAIGN_011 (a null model).
   USD_JPY's tick-by-tick H4 gain/loss distribution is so close to
   symmetric that any zero-edge strategy on H4 lands at ~+0.0000
   expectancy. The regime gate's inability to move USD_JPY off this
   floor is evidence that the gate is not identifying a real
   directional edge.

5. **HIGH-VOL ≠ trend-friendly.** The implicit premise of the
   hypothesis — that high-vol regimes are more trend-friendly — is
   not borne out on this universe + timeframe. High-vol periods on
   these majors often coincide with mean-reverting central-bank-event
   spikes, not persistent multi-day trends; the trend filter goes the
   wrong way often enough that the gate produces more losing trades
   than it filters out.

### 6.2 Did the regime gate destroy value relative to baseline?

**Yes, materially.** Compared to CAMPAIGN_011's null model:

| metric | CAMPAIGN_011 (null) | CAMPAIGN_012 (regime switcher) | difference |
|---|---|---|---|
| total trades | 1,177 | 3,726 | +2,549 (~3.2 ×) |
| aggregate expectancy R | −0.0024 | −0.0521 | −0.0497 (~22 × worse) |
| aggregate return % | −0.53 % | −43.52 % | −42.99 pp (~82 × worse in absolute terms) |
| profit factor | 0.91 | 0.034 | −0.876 |
| pairs positive | 3 / 7 | 1 / 7 | −2 |

The regime gate's effect is *not* "no edge" (which would land near
the null). It is "amplified cost drag" — each extra trade pays a
deterministic cost, and the regime filter does not discriminate
between profitable and unprofitable trades.

### 6.3 Is the regime feature itself defensible?

The regime feature is **computed correctly** (per the structural-audit
unit tests in `tests/unit/test_regime_switcher_atr_percentile.py`; all
47 pass). The R3 trailing-percentile slice uses exactly 60 strictly
preceding D1AGG ATR-14 values; the reference is the most recent
completed D1AGG bar; no full-sample lookahead.

The feature simply **does not predict trade profitability** for the
candidate's entry direction (H4 close-vs-close trend continuation) on
this universe + cost model. The hypothesis is falsified by the
evidence.

## 7. Comparison to CAMPAIGN_010 and CAMPAIGN_011 (diagnostic context)

| metric | CAMPAIGN_002 trend_following | CAMPAIGN_010 session_breakout | CAMPAIGN_011 random_entry_anchor (null) | **CAMPAIGN_012 regime_switcher** |
|---|---:|---:|---:|---:|
| aggregate expectancy R | −0.085 | −0.085 | −0.0024 | **−0.0521** |
| aggregate return % | −1.02 % | −1.02 % | −0.53 % | **−43.52 %** |
| profit factor | 0.75 | — | 0.91 | **0.034** |
| total trades (8-fold) | — | 2,791 | 1,177 | **3,726** |
| fold pass rate | n/a | 0 / 8 | 0 / 8 | **0 / 8** |
| pairs positive | — | — | 3 / 7 | **1 / 7** |
| verdict | REJECT | REJECT | REJECT (null anchor) | **REJECT** |

CAMPAIGN_012 is the **worst aggregate-return** result of any campaign
to date. The regime gate's effect on this universe is *uniformly
negative* — it does not even reach CAMPAIGN_010's cost-drag floor
(which itself was REJECTED).

## 8. Caveats

- **All metrics are pre-financing.** The Phase 6 financing overlay
  applies ESTIMATED + conservative stress on top of these
  pre-financing trades; it is expected to *worsen* them (rollover
  costs are debits-on-both-sides under conservative stress).
- **The runner used `RiskEngine(mode='backtest')`** with the
  CAMPAIGN_010 / 011-inherited risk caps. The rejection rate per pair
  is recorded in Phase 7 diagnostics.
- **Per-fold and per-pair noise.** Some pair-fold cells are positive
  (e.g. fold 3 EUR_USD +0.25 R / +2.36 %); this is expected variance.
  The aggregate metrics are what govern the verdict.
- **DST handling.** The D1AGG aggregator drops "ambiguous" days at
  DST transitions. This is structural; the strategy fail-closes on
  insufficient D1AGG history. Fold-by-fold trade counts vary in part
  because of how many DST-clean days each test window contains. This
  is not a tuning artifact.

## 9. Explicit no-approval statement

**This verdict is REJECT.** `regime_switcher_atr_percentile 0.1.0-c012`
is rejected from any further paper / demo / live consideration under
the current frozen-parameter pre-commit.

- `configs/approved_strategies.yaml` remains `approved: []` (verified).
- The candidate is **not** enabled in `configs/paper.yaml` or
  `configs/practice.yaml`.
- The 6-evidence ladder stops at items 1–3 (data provenance,
  walk-forward, financing) for a REJECT; items 4 (risk diagnostics),
  5 (independent verifier), and 6 (human approval) are not required
  and would not change the verdict.
- The recommended verifier-extension sprint
  `infra-free-local-parity-verifier-regime-switcher-001` is **not
  needed** for this REJECT and is **deferred indefinitely**.
- A different regime hypothesis (different threshold, different
  lookback, different trend definition) would require a new
  discovery + design + pre-commit cycle as a NEW candidate; it
  cannot reuse CAMPAIGN_012's name, version, or pre-commit.

## 10. Paper / demo / live blocked statement

- `paper-loop -c configs/paper.yaml` → **refused** (registry empty
  for `trend_following`).
- `demo-loop -c configs/practice.yaml` → **refused** (registry empty
  for `trend_following`).
- `forex_bot.cli --help` → **no `live-loop` command present**.
- `check_research_freeze.py` → **ALL PASS** (loops_refuse PASS).
- The live-promotion financing blocker (MODELED refused) stands
  independently.

## 11. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_012_WALK_FORWARD_PLAN.md`](CAMPAIGN_012_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)
- [`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) (sibling)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) (sibling — the null baseline)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
