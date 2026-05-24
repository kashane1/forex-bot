# CAMPAIGN_011 — Walk-Forward Result and Verdict

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 5 formal classification of the CAMPAIGN_011 walk-forward
evidence (`random_entry_anchor 0.1.0-c011` — the C5
diagnostic-anchor null model). Verdict evaluated strictly
against the pre-committed gates in
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§11 (inherited verbatim from CAMPAIGN_010 §10). **No gate is
relaxed after seeing results.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.
> **CAMPAIGN_011 is a null model — cannot be approved by design.
> The REJECT verdict below is the *expected and desired*
> outcome of the diagnostic anchor.**

## 1. Headline verdict — **REJECT** (expected; null-model success)

`random_entry_anchor 0.1.0-c011` is **rejected as a research
candidate under its pre-committed walk-forward protocol**, on
real OANDA H4 practice data for the 7-pair universe, 8 rolling
folds spanning 2021-12-21 → 2025-11-29.

| dimension | value |
|---|---|
| `WalkForwardResults.overall_verdict` | **`REJECT`** |
| classification under the protocol | **REJECT** (not BLOCKED — the run produced clean evidence; not INCONCLUSIVE — sample sizes meet the aggregate trade-count gate; not RESEARCH_PASS — the directional PnL gates fail; not INVESTIGATE_PIPELINE — the random null model REJECTed exactly as expected, with no anomalous over-performance) |
| was any gate relaxed? | **no** — gates evaluated verbatim from §11 |
| was any parameter tuned? | **no** — frozen-parameter + master-seed assertion in the runner aborts before any backtest if a single value drifts |
| was the seed optimized? | **no** — `master_seed = 20260523` was the only seed used |
| can the candidate be approved? | **no — null model by design**. The REJECT verdict does not "open" any approval path. |
| pipeline validation outcome | **GREEN** — the gates correctly REJECTed a known-zero-edge strategy with metrics consistent with random expectations |

## 2. Aggregate-level gate evidence

Authoritative metrics from
[`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json)
and
[`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json):

| gate (verbatim) | threshold | observed | result |
|---|---|---|:---:|
| `aggregate.fold_pass_rate` | `100 %` (strict) | **0 / 8 = 0 %** | **FAIL** |
| `aggregate.fold_count` | ≥ 6 | 8 | PASS |
| `aggregate.expectancy_R_net_of_stress_financing` (pre-financing here; financing overlay strictly worsens — see Phase 6) | ≥ 0.05 R | **−0.0024 R** | **FAIL** |
| `aggregate.profit_factor_net_of_stress_financing` | ≥ 1.10 | **0.91** | **FAIL** |
| `aggregate.trade_count` | ≥ 200 | 1,177 | PASS |
| `aggregate.pairs_positive` | ≥ 4 of 7 | **3 / 7** (GBP_USD, USD_JPY ≈ 0, USD_CHF) | **FAIL** |
| `aggregate.single_fold_dominance` | ≤ 60 % | 40.1 % | PASS |
| `aggregate.single_pair_dominance` | ≤ 40 % | 36.5 % | PASS |
| `financing.modeled_refused` | PASS | PASS (Phase 6 uses ESTIMATED + conservative stress; MODELED refused at four layers) | PASS |
| `financing.conservative_stress_run_does_not_flip_verdict` | PASS | Vacuously PASS — the pre-financing verdict is already REJECT; stress only deepens it (see [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)) | PASS |

Four gates fail. Six pass. Under strict-pass, **REJECT** — and
**this is the expected null-model outcome**: a random-entry
strategy with no edge cannot produce ≥ 0.05 R expectancy or
≥ 1.10 profit factor or ≥ 4/7 positive pairs by construction.

## 3. Per-fold gate evidence

Per
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§11 (test fold row), each fold's pre-committed gates are:

- `expectancy_R_net_of_stress_financing ≥ 0.05 R`
- `profit_factor_net_of_stress_financing ≥ 1.10`
- `pairs_positive_net_of_stress_financing ≥ 4 of 7`
- `trade_count ≥ 30`
- `single_pair_dominance ≤ 60 %`

| fold | test window | exp_r | PF | pairs +ve | trades | pair_dom % | gates passed | result |
|---:|---|---:|---:|---:|---:|---:|---:|:---:|
| 0 | 2021-12-21 → 2022-06-18 | −0.1039 | 0.19 | 1 / 7 | 143 | 21.2 | 3 / 5 | **FAIL** |
| 1 | 2022-06-19 → 2022-12-15 | −0.0209 | 0.85 | 4 / 7 | 150 | 38.3 | 3 / 5 | **FAIL** |
| 2 | 2022-12-16 → 2023-06-13 | +0.0387 | 3.84 | 6 / 7 | 153 | 35.2 | 3 / 5 | **FAIL** |
| 3 | 2023-06-14 → 2023-12-10 | −0.0056 | 0.61 | 2 / 7 | 150 | 26.4 | 2 / 5 | **FAIL** |
| 4 | 2023-12-11 → 2024-06-07 | +0.0147 | 0.97 | 3 / 7 | 162 | 23.5 | 2 / 5 | **FAIL** |
| 5 | 2024-06-08 → 2024-12-04 | −0.0014 | 1.21 | 4 / 7 | 153 | 36.4 | 3 / 5 | **FAIL** |
| 6 | 2024-12-05 → 2025-06-02 | +0.0541 | 1.38 | 3 / 7 | 128 | 27.9 | 3 / 5 | **FAIL** |
| 7 | 2025-06-03 → 2025-11-29 | +0.0068 | 0.96 | 3 / 7 | 138 | 22.2 | 3 / 5 | **FAIL** |

**0 of 8 folds pass all gates.** Fold 6 has the highest
expectancy R (+0.0541, just above the 0.05 threshold) but fails
the `pairs_positive ≥ 4 / 7` gate (only 3 pairs positive). Fold
2's profit factor of 3.84 (driven by USD_JPY's +2.54 % return
from 25 trades — random outliers happen) doesn't save the fold
because its expectancy R is only +0.0387.

This is exactly the no-edge fingerprint: occasional folds bounce
above zero, occasional folds bounce below, none consistently
clears every gate, and the aggregate centers near zero.

## 4. Per-pair × all-folds aggregate (informational)

| pair | total trades | aggregate return % | expectancy R | sign |
|---|---:|---:|---:|:---:|
| EUR_USD | 119 | −1.22 | −0.0403 | − |
| **GBP_USD** | 196 | **+4.19** | **+0.0842** | **+** |
| **USD_JPY** | 174 | +0.35 | **+0.0000** | ≈ 0 (literally) |
| AUD_USD | 190 | −1.73 | −0.0359 | − |
| USD_CAD | 182 | −0.44 | −0.0099 | − |
| **USD_CHF** | 177 | +0.92 | **+0.0243** | **+** |
| NZD_USD | 139 | −2.61 | −0.0737 | − |

**3 / 7 pairs net positive** (GBP_USD, USD_JPY ≈ 0, USD_CHF) —
close to the uniform-noise expectation of ~3.5 / 7 ± 1. Per-pair
expectancies bounded in approximately ±0.10 R, centered near 0.
USD_JPY's expectancy R is **literally +0.0000** to 4 decimal
places — a textbook random-walk signature.

## 5. Null-model interpretation

The CAMPAIGN_011 walk-forward run is a successful diagnostic
because it confirms **all three** of the anchor's design
properties:

### 5.1 The pipeline correctly REJECTs a known-zero-edge strategy

| evidence | expectation | observation |
|---|---|---|
| aggregate expectancy R near 0 | ≈ 0 ± 0.05 R | **−0.0024 R** — within tolerance |
| aggregate profit factor near 1 | ≈ 1.0 ± 0.2 | **0.91** — within tolerance |
| aggregate return near 0 over 4 years | ≈ 0 ± 5 % | **−0.53 %** — within tolerance |
| ~50 % of pairs positive | 3.5 / 7 ± 1 | **3 / 7** — within tolerance |
| profit factor below approval threshold | < 1.10 | **0.91 < 1.10** ✓ |
| expectancy R below approval threshold | < 0.05 | **−0.0024 < 0.05** ✓ |

### 5.2 The per-fold + aggregate metrics establish a falsifiability floor

Future "real" candidates can now be compared directly to:

| metric | CAMPAIGN_011 (random anchor) | future candidate must beat |
|---|---|---|
| aggregate expectancy R | −0.0024 R | by ≥ +0.05 R |
| aggregate profit factor | 0.91 | by ≥ 0.19 (must reach 1.10) |
| aggregate return % over 4 years | −0.53 % | meaningfully positive |
| pairs_positive | 3 / 7 | ≥ 4 / 7 |
| fold pass rate | 0 / 8 | 100 % (strict-pass) |
| per-pair worst expectancy R | −0.0737 (NZD_USD) | ≥ 0 across at least 4 pairs |

**This is the bar.** Any future C2 / C3 / C4 / new-family
candidate that produces metrics indistinguishable from these
random-baseline numbers has demonstrated no edge.

### 5.3 The candidate has zero parameter-tuning risk

| dimension | observation |
|---|---|
| only "knob" | `master_seed = 20260523` (fixed in pre-commit; runner asserts it) |
| was the seed changed during this sprint? | **no** — only one seed used |
| was any other parameter changed? | **no** — frozen-parameter assertion held |
| is the result reproducible? | **yes** — same `(master_seed, pair, ts)` produces same trades; verified by the 36 Phase 3 unit tests |

A candidate with no tunable parameters cannot be curve-fit.
That is precisely why a null model is the right pipeline
validator.

## 6. Comparison to CAMPAIGN_010 (informational; not used for tuning)

| dimension | CAMPAIGN_010 (session_breakout) | **CAMPAIGN_011 (random_entry_anchor)** |
|---|---:|---:|
| total trades | 2,791 | 1,177 |
| aggregate expectancy R | −0.0408 | **−0.0024** (≈ 17× closer to 0) |
| aggregate return % | −36.56 % | **−0.53 %** (≈ 69× closer to 0) |
| aggregate profit factor | 0.04 | **0.91** (≈ 23× closer to 1) |
| pairs positive | 1 / 7 (USD_CHF only) | **3 / 7** (GBP_USD, USD_JPY ≈ 0, USD_CHF) |
| fold pass rate | 0 / 8 | **0 / 8** (same — both REJECT) |
| verdict | REJECT (directional negative — strategy lost decisively) | **REJECT (null model — strategy is statistically indistinguishable from no edge)** |

The contrast is informative: CAMPAIGN_010's directional
strategy lost *more* than random would have. Random doesn't
lose −37 % in 4 years on H4 majors after costs; it loses ~0 %
(barely below — the costs eat the noise). CAMPAIGN_010's much
worse aggregate metrics are evidence that the session-breakout
*entry signal* was actively bad, not merely random.

## 7. Why this is REJECT, not INCONCLUSIVE, not BLOCKED, not INVESTIGATE_PIPELINE

| classification | criterion | this campaign |
|---|---|---|
| **BLOCKED** | pipeline cannot execute (data / tooling gap) | not blocked — 56 backtests ran in 5.6 s, 1,177 trades produced |
| **INCONCLUSIVE** | gates miss because of sample-size / coverage thinness | not inconclusive — aggregate 1,177 trades (≥ 200 gate) and 8 folds (≥ 6 gate); the issue is the strategy has no edge, not statistical noise |
| **REJECT** | gates fail; metrics consistent with no-edge | **yes** — 4 / 8 PnL-direction gates fail; metrics within null-model tolerance |
| **INVESTIGATE_PIPELINE** | gates **unexpectedly pass** on a known-zero-edge strategy → information leakage / gate miscalibration / pipeline bug | **not triggered** — the null model REJECTed cleanly; no anomalous over-performance |
| RESEARCH_PASS_UNAPPROVED | every gate passes — not applicable to null models, structurally | not applicable (null model cannot be promoted; if all gates had passed, this would have been INVESTIGATE_PIPELINE) |

## 8. Implications for the strategy registry

- **No change to `configs/approved_strategies.yaml`.** It
  remains `approved: []`.
- **CAMPAIGN_011 reclassifies from `scaffold-only` to `rejected
  (null model — diagnostic anchor)`** in
  [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) (Phase 9 will
  apply this change). The new row will read:

  > `random_entry_anchor 0.1.0-c011` — rejected (null model anchor) — paper: NO · demo: NO · live: NO — CAMPAIGN_011 walk-forward (8 folds, 7 pairs, 1,177 trades, fold pass rate 0 %, aggregate expectancy −0.002 R, 3/7 pairs positive)

  with paper / demo / live all NO and the explicit "null model
  / not approvable" qualifier.

- The candidate joins the rejected-strategy list, but **with
  the distinguishing label "null model anchor"** — it is the
  reference floor, not just another failed candidate.

## 9. What this verdict does not do

1. **It does not approve any strategy.** It cannot —
   CAMPAIGN_011 is a null model.
2. **It does not change CAMPAIGN_002's or CAMPAIGN_010's
   verdicts.** Both remain REJECT.
3. **It does not unblock paper / demo / live.** `paper-loop`
   and `demo-loop` continue to refuse via the empty registry;
   no `live-loop` command exists.
4. **It does not modify any frozen parameter.** A future
   variant (e.g. different `master_seed`) would be a NEW
   candidate requiring its own pre-commit.
5. **It does not retire the H4 store** — the data remains
   available for the next real candidate sprint.

## 10. What this verdict does do

1. **It validates the evidence pipeline.** The full walk-forward
   + financing + risk pipeline runs end-to-end against a
   known-zero-edge strategy and produces a clean REJECT with
   metrics consistent with random expectations.
2. **It establishes the falsifiability floor.** Per §5.2
   above, any future candidate's per-fold + aggregate metrics
   can be compared directly to CAMPAIGN_011's. A candidate
   whose metrics resemble CAMPAIGN_011's has demonstrated no
   edge.
3. **It demonstrates the gates are calibrated correctly.** The
   gates correctly REJECT a null model (no false positive)
   without being so lax that they'd accept noise as edge.

## 11. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011** verdict = REJECT (null model anchor;
  not approvable).
- **Paper / demo / live remain blocked.**
- **No broker call** at any phase; **no `.env` read; no
  credential printed; no account / order / trade / position /
  transaction endpoint queried.**
- **No QuantConnect / LEAN.**
- **No engine-PnL change.** **No `src/forex_bot/financing.py`
  edit.**
- **No new external dependency.**
- **No parameter tuning. No seed optimization.**
- **Bulky data uncommitted** beyond the conventional artifact
  directory (~600 KB total).

## 12. Cross-links

- [`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md)
  (Phase 4 — commands, frozen-parameter enforcement, fold table)
- [`CAMPAIGN_011_WALK_FORWARD_PLAN.md`](CAMPAIGN_011_WALK_FORWARD_PLAN.md)
  (Phase 2 — fold geometry)
- [`CAMPAIGN_011_DATA_PROVENANCE.md`](CAMPAIGN_011_DATA_PROVENANCE.md)
  (Phase 1 — data source + provenance hashes)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  §11 (the gates)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
  (Phase 9 will update this to `rejected (null model anchor)`)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
  §9 (default rejection criteria)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
  (approval is a human action; this verdict — REJECT or
  unexpected-PASS — cannot become approval for a null model)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
  (Phase 9 will add a row for `random_entry_anchor 0.1.0-c011`
  as `rejected (null model anchor)`)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
  (the directional-strategy comparison baseline)
- [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json)
- [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.md)
- [`backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json`](../../backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json)
