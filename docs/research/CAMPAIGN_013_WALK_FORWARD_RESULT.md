# CAMPAIGN_013 Walk-Forward Result (Phase 5)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Formal Phase 5 verdict for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**.

> **Research verdict: `REJECT`.** 5 of 8 inherited aggregate gates
> fail; CAMPAIGN_013 is the **worst-performing campaign to date** on
> aggregate return, profit factor, and trade count, well outside the
> indistinguishable-from-null band on every binding axis in the worse
> direction. The cross-pair runner integration contract was
> **satisfied** on all 8 folds — the REJECT is on inherited gates
> alone.
>
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 / CAMPAIGN_012 remain
> REJECT and untouched. CAMPAIGN_011 is the **null baseline only**;
> this verdict does not revive CAMPAIGN_011 as a tradable strategy.
> Paper / demo / live remain blocked.

## 1. Research verdict

**`REJECT`** — not `REJECT_INDISTINGUISHABLE_FROM_NULL` (because
CAMPAIGN_013's metrics diverge from CAMPAIGN_011's *in the worse
direction*, well outside the symmetric indistinguishability band on
every binding axis), and not `BLOCKED` (because the cross-pair runner
integration contract — see §6 — was satisfied on all 8 folds).

Rationale:

- **5 of 8 inherited aggregate gates FAIL** (see §2.2 for the table).
- **Aggregate expectancy −0.0564 R** is *worse* than CAMPAIGN_011's
  −0.0024 R by 0.0540 R — ~11 × the indistinguishability half-band
  (±0.005 R).
- **Aggregate return −113.36 % over 4 years** is *catastrophically
  worse* than CAMPAIGN_011's −0.53 % — ~214 × CAMPAIGN_011's loss in
  absolute terms and ~2.6 × worse than CAMPAIGN_012 (−43.52 %), the
  previous worst.
- **Profit factor 0.000** (literally zero) is *vastly worse* than
  CAMPAIGN_011's 0.91 — ~9 × the indistinguishability half-band
  (±0.10 PF). In 7 of 8 folds **every** trading pair posted a
  non-positive aggregate return.
- **Only 1 of 7 pairs positive** (USD_JPY at +0.0000 R, essentially
  zero) versus CAMPAIGN_011's 3 of 7 — *worse* by 2 pairs, exactly on
  the indistinguishability boundary (±2 pp = ±1 pair) in the worse
  direction.
- **0 of 8 folds passing** — same as CAMPAIGN_010 / 011 / 012.
- The strategy fired **7,940 trades** — ~2.1 × CAMPAIGN_012 and ~6.7 ×
  CAMPAIGN_011 — without producing a single profitable fold or a
  positive profit factor in 7 of 8 folds. The cross-pair rotator
  amplifies trade frequency dramatically without improving signal
  quality.

## 2. Inherited gate table

### 2.1 Per-fold gates (`CAMPAIGN_010 §10` / `CAMPAIGN_011 §11` verbatim)

| fold | trades | exp R | return % | PF | pairs+ / 7 | single-pair dom % | pass? |
|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 794 | −0.1017 | −19.33 | 0.000 | 0 / 3 trading | ≤ 60 % | **REJECT** |
| 1 | 321 | −0.0027 | −0.28 | 0.000 | 0 / 1 trading | ≤ 60 % | **REJECT** |
| 2 | 1,166 | −0.0452 | −13.29 | 0.000 | 0 / 4 trading | ≤ 60 % | **REJECT** |
| 3 | 810 | −0.0874 | −17.03 | 0.000 | 0 / 3 trading | ≤ 60 % | **REJECT** |
| 4 | 1,255 | −0.0452 | −14.93 | 0.000 | 0 / 4 trading | ≤ 60 % | **REJECT** |
| 5 | 1,252 | −0.0498 | −16.31 | 0.000 | 0 / 4 trading | ≤ 60 % | **REJECT** |
| 6 | 1,149 | −0.0253 | −6.86 | 0.126 | 1 / 4 trading (USD_JPY) | ≤ 60 % | **REJECT** |
| 7 | 1,193 | −0.0794 | −25.32 | 0.000 | 0 / 4 trading | ≤ 60 % | **REJECT** |

**0 / 8 folds pass.** Every fold fails `expectancy_r ≥ 0.05 R`,
`profit_factor ≥ 1.10`, and `pairs_positive ≥ 4 / 7`. The
`single_pair_dominance_le_60pct` gate passes per-fold (no single pair
accounts for > 60 % of its fold's |return|).

`pairs+` is counted across the 7-pair universe (not "trading pairs
only") for the formal gate evaluation; the "trading pairs"
denominator is shown here for diagnostic context — see §6.2 for the
zero-trade-cell distribution. Either way, ≥ 4 / 7 is not met in any
fold.

### 2.2 Aggregate gates

| gate | threshold | observed | result |
|---|---|---|:---:|
| `fold_pass_rate_eq_100pct` | = 100 % | 0 % | **FAIL** |
| `fold_count_ge_6` | ≥ 6 | 8 | PASS |
| `expectancy_r_ge_0p05` | ≥ 0.05 R | **−0.0564 R** | **FAIL** |
| `profit_factor_ge_1p10` | ≥ 1.10 | **0.000** | **FAIL** |
| `trade_count_ge_200` | ≥ 200 | 7,940 | PASS |
| `pairs_positive_ge_4_of_7` | ≥ 4 / 7 | **1 / 7** | **FAIL** |
| `single_fold_dominance_le_60pct` | ≤ 60 % | 22.34 % | PASS |
| `single_pair_dominance_le_40pct` | ≤ 40 % | 36.55 % | PASS |

**5 of 8 aggregate gates FAIL.** Inherited-gate overall verdict:
`REJECT`.

## 3. Null-baseline comparison (binding; CAMPAIGN_011-derived)

Per
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§3 + §8 + §9, this verdict doc applies the CAMPAIGN_011 null-baseline
comparison with explicit margins:

| metric | CAMPAIGN_011 floor | CAMPAIGN_013 result | difference | meaningful-improvement margin | beat margin? | in indistinguishability band (±)? |
|---|---:|---:|---:|---|:---:|:---:|
| aggregate expectancy R | −0.0024 | **−0.0564** | **−0.0540** | ≥ +0.0524 (→ ≥ 0.05 R) | **NO — WORSE** | NO (~11 × half-band) |
| aggregate profit factor | 0.91 | **0.000** | **−0.910** | ≥ +0.19 (→ ≥ 1.10) | **NO — WORSE** | NO (~9 × half-band) |
| aggregate return (4 y) | −0.53 % | **−113.36 %** | **−112.83 pp** | ≥ +5 % | **NO — WORSE** | NO (~56 × half-band) |
| `pairs_positive` | 3 / 7 | **1 / 7** | **−2 pairs** | ≥ 4 / 7 | **NO — WORSE** | NO (= ±1-pair boundary, worse direction) |
| `fold_pass_rate` | 0 / 8 | **0 / 8** | 0 | 100 % | **NO** | YES (same as null) |
| `single_fold_dominance` | 40.1 % | 22.34 % | −17.8 pp | ≤ 60 % (CAMPAIGN_010 gate) | yes (within gate; not a beat margin) | n/a |

**Classification (per
`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` §8):**

- CAMPAIGN_013 does **NOT** meet the meaningful-improvement margins
  on any of the four binding axes (expectancy / PF / return /
  pairs-positive).
- CAMPAIGN_013 is **NOT** indistinguishable from null on the four
  binding axes either — it is **WORSE than null** on all four,
  outside the symmetric indistinguishability band on three of four
  (and exactly at the boundary on `pairs_positive`, in the worse
  direction).
- Therefore: **`REJECT`** (not `REJECT_INDISTINGUISHABLE_FROM_NULL`).

The cross-pair rotator's effect is **not** "noise around zero" (which
would be indistinguishable from null). It is **active and severe
destruction of equity** through amplified trade count under the same
spread + slippage cost model — the rank-gap rule fires ~6.7 × as
often as CAMPAIGN_011's PRNG, and each additional trade pays the same
per-trade cost without an offsetting signal-quality gain.

## 4. Aggregate metrics

| metric | value |
|---|---|
| fold count | 8 |
| folds passing all per-fold gates | 0 |
| fold pass rate | **0 / 8 = 0 %** |
| total trades across folds | **7,940** |
| aggregate expectancy R | **−0.0564** |
| aggregate return % (4-year window) | **−113.36 %** |
| profit factor | **0.000** (sum of positive fold-pair returns = 0 in 7 of 8 folds) |
| pairs_positive_count | **1 / 7** (USD_JPY at +0.0000 R) |
| single_fold_dominance % | 22.34 % |
| single_pair_dominance % | 36.55 % (NZD_USD) |
| worst single pair | NZD_USD (−0.0897 R, 1,863 trades, **−41.76 %**) |
| best single pair | USD_JPY (+0.0000 R, 310 trades, +0.45 % — random-walk floor) |
| worst-fold return | fold 7: −25.32 % |
| best-fold return | fold 1: −0.28 % (still REJECT — −0.0027 R; 1 trading pair) |
| zero-trade pair-fold cells | **29 / 56** (51.8 %; see §6.2) |

## 5. Fold metrics (compact reproduction)

(See [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
§7 for the full table.)

| # | test window | trades | exp R | return % | PF | DD % | win % | passes? |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | 794 | −0.1017 | −19.33 | 0.000 | 0.00 | 19.0 % | NO |
| 1 | 2022-06-19 → 2022-12-15 | 321 | −0.0027 | −0.28 | 0.000 | 0.00 | 6.9 % | NO |
| 2 | 2022-12-16 → 2023-06-13 | 1,166 | −0.0452 | −13.29 | 0.000 | −3.99 | 26.6 % | NO |
| 3 | 2023-06-14 → 2023-12-10 | 810 | −0.0874 | −17.03 | 0.000 | 0.00 | 18.7 % | NO |
| 4 | 2023-12-11 → 2024-06-07 | 1,255 | −0.0452 | −14.93 | 0.000 | −3.73 | 25.3 % | NO |
| 5 | 2024-06-08 → 2024-12-04 | 1,252 | −0.0498 | −16.31 | 0.000 | −5.74 | 25.8 % | NO |
| 6 | 2024-12-05 → 2025-06-02 | 1,149 | −0.0253 | −6.86 | 0.126 | −3.51 | 26.4 % | NO |
| 7 | 2025-06-03 → 2025-11-29 | 1,193 | −0.0794 | −25.32 | 0.000 | −5.76 | 25.3 % | NO |

## 6. Cross-pair rotation interpretation

### 6.1 Cross-pair runner integration contract: SATISFIED on all 8 folds

Per the Phase 0 plan §7 and the Phase 3 runner implementation, the
cross-pair runner integration contract was **mandatory**. The runner
must align all 7 pairs' completed H4 closes to a common timestamp
index, inject `cross_pair_closes` into each pair's `strategy_config`,
and fail closed (verdict = `BLOCKED`) if any required pair is
missing, misaligned, non-finite, or insufficient.

**All 8 folds satisfied the contract.** The runner emitted
`cross_pair_diagnostics` per fold:

| fold | common_index_length (H4 bars) | contract_satisfied |
|---|---:|:---:|
| 0 | 1,841 | ✓ |
| 1 | 1,848 | ✓ |
| 2 | 1,837 | ✓ |
| 3 | 1,830 | ✓ |
| 4 | 1,835 | ✓ |
| 5 | 1,836 | ✓ |
| 6 | 1,825 | ✓ |
| 7 | 1,829 | ✓ |

The cross-pair runner contract does **NOT** block this verdict; the
REJECT comes from inherited gates alone. Had any fold failed the
contract, the verdict would have been `BLOCKED` regardless of fold
metrics (per the binding rule in the Phase 0 plan).

### 6.2 Per-pair aggregate (all 8 folds combined)

| pair | trade count | aggregate return (%) | aggregate expectancy R |
|---|---:|---:|---:|
| EUR_USD | 1,412 | −16.93 | −0.0478 |
| GBP_USD | 648 | −9.79 | −0.0604 |
| USD_JPY | 310 | **+0.45** | **+0.0000** |
| AUD_USD | 1,942 | −20.26 | −0.0413 |
| USD_CAD | 958 | −10.40 | −0.0309 |
| USD_CHF | 807 | −14.67 | −0.0801 |
| NZD_USD | 1,863 | **−41.76** | **−0.0897** |

USD_JPY again sits at the **random-walk floor +0.0000 R** — the same
signature CAMPAIGN_011 (a known null) and CAMPAIGN_012 (regime
switcher) surfaced for this pair on H4. NZD_USD is the worst pair by
a wide margin (−41.76 % over 4 years, −0.0897 R). AUD_USD fired the
most trades (1,942) yet lost 20.26 %.

### 6.3 Zero-trade pair-fold cell distribution

Of the 56 (pair × fold) cells, **29 produced zero trades** because
the rank-gap rule `|rank(quote) − rank(base)| ≥ 4` was never
satisfied for that pair within the fold's test window — this is the
gate's *intended* sparseness, not a runner failure. The remaining 27
cells produced 207 to 328 trades each, averaging ~294 trades per
trading cell.

This sparseness is also visible in the per-fold long/short balance:

| fold | long | short | total | imbalance |
|---|---:|---:|---:|---|
| 0 | 509 | 285 | 794 | long-skewed (USD weakness phase) |
| 1 | 0 | 321 | 321 | all-short (single trading pair: AUD_USD short) |
| 2 | 1,166 | 0 | 1,166 | all-long (USD weakness regime) |
| 3 | 207 | 603 | 810 | short-skewed |
| 4 | 322 | 933 | 1,255 | short-skewed |
| 5 | 321 | 931 | 1,252 | short-skewed |
| 6 | 524 | 625 | 1,149 | near-balanced |
| 7 | 878 | 315 | 1,193 | long-skewed |

The cross-pair signal flips between strong-USD and weak-USD regimes
without producing a profitable pattern in either — the long/short
mix tracks USD's regime but the within-regime pair-direction
expectancy is uniformly negative on this universe.

### 6.4 `MAX_OPEN_POSITIONS_EXCEEDED` rejection observation

The Phase 0 plan §11 anticipated that cross-pair rotation might
generate concurrent signals and trigger
`MAX_OPEN_POSITIONS_EXCEEDED` rejections under `max_open_positions
= 1`. **In the actual runner, this rejection code fires 0 times
across all 56 pair-fold cells.** This is because the
`BacktestEngine` is single-instrument: the runner invokes one
independent engine per pair per fold, so the engine's
`max_open_positions` cap is *not* a portfolio-wide constraint — each
pair operates in its own isolated equity bucket.

Implications:

1. The 7,940-trade total is the **union of 7 independent per-pair
   runs**, not a portfolio-aware count. A true portfolio runner would
   reject many of these (via portfolio max-positions) and reduce trade
   count proportionally.
2. The negative aggregate expectancy is **not** an artifact of
   concurrent rejection rate — each pair sees the same expectancy it
   would see if traded standalone.
3. Even with a portfolio-aware runner that gated to ≤ 1 open
   position, the **per-pair expectancy is already negative on 6 of 7
   pairs**, so portfolio-level concurrency control cannot rescue this
   strategy. Picking the "best" of multiple simultaneous signals does
   not turn 6 negative pair-expectancies into a positive aggregate.
4. The Phase 0 plan's standing rule — "do not relax
   `max_open_positions` or any risk limits to rescue trade count" —
   is moot: relaxing nothing produces this result.

The non-rescue conclusion holds.

### 6.5 Why did the cross-pair rotator fail?

The C6 hypothesis was: "rank the 8 G8 currencies by 24-bar log-return
strength, take only the largest rank gaps (≥ 4 / 7), long the
strong-base / short the strong-quote pair." The walk-forward result
is incompatible with this hypothesis:

1. **The rank-gap filter does not improve signal quality.** Every
   per-fold expectancy is negative (range −0.1017 R to −0.0027 R;
   no fold reaches break-even). The cross-pair filter selects for
   trades that lose **on this universe at this cost model**.

2. **The rank-gap filter amplifies trade count under the same cost
   model.** CAMPAIGN_013 placed **7,940 trades** vs CAMPAIGN_011's
   **1,177** (6.7 × as many). On a universe where each trade pays
   spread + slippage, more trades = larger aggregate cost drag. The
   cross-pair rule fires aggressively whenever a rank gap exists; it
   does not gate against per-trade cost-effectiveness.

3. **Short holding period + cross-pair rotation = high turnover, low
   per-trade edge.** The 6-bar `max_bars_in_trade` (24 hours)
   combined with the rank-gap rule means the strategy enters and
   exits frequently. Per-trade expectancy is uniformly negative
   except USD_JPY (which sits at the random-walk floor).

4. **The rank gap is not a directional edge for the *pair-level*
   distribution.** The implicit premise — that the strongest currency
   in the basket will outperform the weakest over a 6-H4-bar holding
   period — is not borne out empirically. Currency-strength rank is
   a slow-moving feature (24-bar lookback ≈ 96 H4 bars worth of
   smoothing) but the 6-bar holding period is short — by the time
   the strategy enters, the rank-gap-implied move has often already
   played out (mean reversion against the rank-implied direction).

5. **USD_JPY's +0.0000 R signature is again diagnostic.** USD_JPY
   produced 310 trades across 8 folds with literally near-zero
   expectancy. The same near-exact-zero appeared in CAMPAIGN_011 (a
   null model) and CAMPAIGN_012 (regime switcher). USD_JPY's
   H4 distribution is so close to symmetric that any zero-edge
   strategy on H4 lands at ~+0.0000 expectancy. The cross-pair
   rotator's inability to move USD_JPY off this floor is evidence
   that the rank-gap rule is not identifying a real directional edge.

6. **NZD_USD's catastrophic loss reflects pair-specific basis risk,
   not rank-gap failure.** NZD_USD lost 41.76 % over 4 years with
   1,863 trades — by far the worst pair. The cross-pair rotator's
   USD-relative ranking pushed it into NZD_USD positions during
   trending periods that subsequently reversed, with the short
   holding period magnifying whipsaw losses.

### 6.6 Did the cross-pair rotator destroy value relative to baseline?

**Yes, catastrophically.** Compared to CAMPAIGN_011's null model:

| metric | CAMPAIGN_011 (null) | CAMPAIGN_013 (cross-pair rotator) | difference |
|---|---|---|---|
| total trades | 1,177 | 7,940 | +6,763 (~6.7 ×) |
| aggregate expectancy R | −0.0024 | −0.0564 | −0.0540 (~23 × worse) |
| aggregate return % | −0.53 % | −113.36 % | −112.83 pp (~214 × worse in absolute terms) |
| profit factor | 0.91 | 0.000 | −0.910 (literally zero) |
| pairs positive | 3 / 7 | 1 / 7 | −2 |

The cross-pair rotator's effect is *not* "no edge" (which would land
near the null). It is "amplified cost drag at 6.7 × turnover" — each
extra trade pays a deterministic cost, and the rank-gap filter does
not discriminate between profitable and unprofitable trades.

### 6.7 Is the cross-pair feature itself defensible?

The cross-pair feature is **computed correctly** (per the structural-
audit unit tests in
`tests/unit/test_cross_pair_currency_strength_rotation.py`; all 57
pass). The 8-currency strength matrix uses correctly signed log
returns (USD-base `+log_return`; USD-quote `−log_return`; USD =
`−mean(non-USD)`), the rank-gap rule uses `|rank(quote) − rank(base)|
≥ 4` inclusively, and there is no full-sample lookahead — each bar's
strength uses the prior 24 completed H4 closes only.

The feature simply **does not predict trade profitability** for the
candidate's entry direction (long strong-base / short strong-quote
over a 6-bar holding period) on this universe + cost model. The
hypothesis is falsified by the evidence.

## 7. Comparison to CAMPAIGN_002 / 010 / 011 / 012 (diagnostic context)

| metric | CAMPAIGN_002 trend_following | CAMPAIGN_010 session_breakout | CAMPAIGN_011 random_entry_anchor (null) | CAMPAIGN_012 regime_switcher | **CAMPAIGN_013 cross-pair rotator** |
|---|---:|---:|---:|---:|---:|
| aggregate expectancy R | −0.085 | −0.085 | −0.0024 | −0.0521 | **−0.0564** |
| aggregate return % | −1.02 % | −1.02 % | −0.53 % | −43.52 % | **−113.36 %** |
| profit factor | 0.75 | — | 0.91 | 0.034 | **0.000** |
| total trades (8-fold) | — | 2,791 | 1,177 | 3,726 | **7,940** |
| fold pass rate | n/a | 0 / 8 | 0 / 8 | 0 / 8 | **0 / 8** |
| pairs positive | — | — | 3 / 7 | 1 / 7 | **1 / 7** |
| verdict | REJECT | REJECT | REJECT (null anchor) | REJECT | **REJECT** |

**CAMPAIGN_013 is the worst aggregate-return and worst-profit-factor
result of any campaign to date.** The cross-pair rotator's effect on
this universe is *uniformly destructive* — it does not even reach
CAMPAIGN_010's cost-drag floor (which itself was REJECTED), and is
roughly 2.6 × worse than CAMPAIGN_012's regime-switcher (the
previous worst).

The two single-instrument rejections (CAMPAIGN_002 / 010) lost ~1 %
over 4 years. The two extensions of trend-following (CAMPAIGN_012 /
013) lost 43 % and 113 % respectively. The pattern is consistent:
adding turnover-amplifying filters to a negative-edge entry direction
on H4 majors makes results materially worse, not better. The
incremental complexity costs (regime gate, cross-pair rotation) buy
extra trade frequency without buying signal quality.

## 8. Caveats

- **All metrics are pre-financing.** The Phase 6 financing overlay
  applies ESTIMATED + conservative stress on top of these
  pre-financing trades; it is expected to *worsen* them (rollover
  costs are debits-on-both-sides under conservative stress).
- **The runner used `RiskEngine(mode='backtest')`** with the
  CAMPAIGN_010 / 011 / 012-inherited risk caps. The rejection counts
  per pair are recorded in Phase 7 diagnostics.
- **The runner is per-pair, not portfolio-wide.** The 7,940-trade
  total is the union across 7 independent per-pair engine runs.
  `MAX_OPEN_POSITIONS_EXCEEDED` is **zero** because the engine sees
  one instrument at a time (see §6.4). A portfolio-aware runner
  would reduce trade count but cannot rescue per-pair negative
  expectancy.
- **Per-fold and per-pair noise.** Some pair-fold cells have small
  trade counts (e.g. fold 1 has only one trading pair, AUD_USD with
  321 trades); this is expected variance from the rank-gap rule's
  conditional firing. The aggregate metrics are what govern the
  verdict.
- **No DST artifact.** Unlike CAMPAIGN_012 (which depended on D1AGG
  aggregation and DST-clean days), the cross-pair feature uses H4
  close-to-close log returns directly. There is no DST-based fold
  variance.
- **`pairs_positive` counting convention.** §2.1 displays the
  diagnostic "pairs_positive / trading_pairs_in_fold" alongside the
  formal "pairs_positive / 7" gate. The formal gate denominator is
  always 7 (the full universe); the diagnostic denominator helps
  interpret why no fold has 4+ positive pairs when several folds have
  ≤ 4 trading pairs.

## 9. Explicit no-approval statement

**This verdict is REJECT.** `cross_pair_currency_strength_rotation
0.1.0-c013` is rejected from any further paper / demo / live
consideration under the current frozen-parameter pre-commit.

- `configs/approved_strategies.yaml` remains `approved: []`
  (verified).
- The candidate is **not** enabled in `configs/paper.yaml` or
  `configs/practice.yaml`.
- The 6-evidence ladder stops at items 1–3 (data provenance,
  walk-forward, financing) for a REJECT; items 4 (risk diagnostics),
  5 (independent verifier), and 6 (human approval) are not required
  and would not change the verdict.
- The recommended verifier-extension sprint
  `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`
  is **not needed** for this REJECT and is **deferred
  indefinitely**.
- A different cross-pair hypothesis (different lookback, different
  rank-gap threshold, different holding period, different pair
  universe) would require a new discovery + design + pre-commit
  cycle as a NEW candidate; it cannot reuse CAMPAIGN_013's name,
  version, or pre-commit. Per the Phase 0 plan §11, the frozen
  parameters cannot be altered based on this result.

## 10. Paper / demo / live blocked statement

- `paper-loop -c configs/paper.yaml` → **refused** (registry empty
  for `trend_following`; the only paper-supported strategy is
  CAMPAIGN_002, which is itself REJECT).
- `demo-loop -c configs/practice.yaml` → **refused** (same
  rationale).
- `forex_bot.cli --help` → **no `live-loop` command present**.
- `check_research_freeze.py` → **ALL PASS** (loops_refuse PASS).
- The live-promotion financing blocker (MODELED refused) stands
  independently.
- `cross_pair_currency_strength_rotation` is **not** wired into the
  paper/demo loops; even if it were, the registry adapter would
  refuse to instantiate it without an approved-strategies entry.

## 11. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_013_WALK_FORWARD_PLAN.md`](CAMPAIGN_013_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)
- [`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) (sibling)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) (sibling — the null baseline)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (sibling)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
