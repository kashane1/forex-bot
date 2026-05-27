# CAMPAIGN_019 — Exit Hypothesis Gate Design

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-002`  
**Status:** **PRECOMMIT ONLY — NOT EXECUTED**

> **Precommit only** — `strategy_evidence: false`. Gates apply to a **future** execution sprint.

Complements [`FUTURE_EXIT_RESEARCH_GATE.md`](FUTURE_EXIT_RESEARCH_GATE.md),
[`FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`](FUTURE_MEAN_REVERSION_RESEARCH_GATE.md), and
C018 gate design (same philosophy, mechanism-specific gates).

---

## Gate philosophy

Validation-looking-good must **not** become approval. C018 demonstrated validation uplift
(+0.194 R) with **train failure** (−0.119 R) — that path is closed. Gates require:

- Train pass before lockbox
- Beat-null vs C011 deduped
- Financing overlay before REVISE interpretation
- Backtrader parity within ±1 trade post-execution
- Maximum outcome: **RESEARCH_PASS / PROMOTION_REVIEW_REQUIRED** — never approval

---

## Screening gate (train + validation)

Run **only** train and validation splits first. Open test lockbox **only if ALL** pass.

| # | gate | threshold | rationale |
|---|---|---|---|
| G1 | train expectancy (R) | **≥ 0.0** | primary falsifier; C008/C009/C018 failed here |
| G2 | validation expectancy (R) | **> 0.0** | OOS edge required |
| G3 | validation profit factor | **≥ 1.05** | repo MR standard |
| G4 | validation pairs positive | **≥ 2 of 6** | not single-pair artifact |
| G5 | validation trade count | **≥ 30** | repo standard |
| G6 | validation stress 2× expectancy | **≥ 0.0** | cost robustness |
| G7 | beat-null vs C011 deduped | validation exp_r > null + **0.010 R** margin | WITHIN_NULL = FAIL |
| G8 | thesis_invalidation mechanism active | **5–45%** of all trades exit via `thesis_invalidation` | inert if <5%; stop-relabel if >45% without train pass |
| G9 | no midline/target exits | target share **= 0%** | C009 forbidden |
| G10 | no protective_stop exits | protective share **= 0%** | C018 form forbidden in C019 |

**Screening FAIL** → verdict **REJECT**, test lockbox **closed**.

---

## Train-specific gates

| # | gate | threshold | rationale |
|---|---|---|---|
| G11 | train exp vs C008 deduped | C019 train exp_r **≥ C008 train exp_r** (−0.025 R) | must not worsen baseline train |
| G12 | full-window stress_15x | combined exp_r **≥ 0** | C008 passed +0.043 R; C018 failed −0.005 R |

---

## Validation-specific diagnostics (recorded, non-blocking unless noted)

| diagnostic | compare vs C008 |
|---|---|
| hard-stop exit share | expect decrease if invalidation fires early |
| thesis_invalidation share | expect 10–35% if hypothesis operative |
| time-exit share | expect ≥ **15%** |
| time-exit median MFE (R) | expect ≥ **2.0R** (C008 ~3.29R) |
| stop never-+1R-before-stop rate | expect decrease vs ~41% |

---

## Test-window unlock gates

Opens **only if** screening **PASS**.

| # | gate | threshold |
|---|---|---|
| T1 | test expectancy (R) | **≥ 0.0** |
| T2 | test profit factor | **≥ 1.0** |
| T3 | test trade count | **≥ 20** |
| T4 | combined train+val+test exp_r | **≥ 0.0** |

Test FAIL → **REJECT**.

---

## Comparison requirements (execution sprint)

Side-by-side vs:

| baseline | metrics |
|---|---|
| C008 deduped | train/val exp_r, exit shares, time MFE, never-+1R stop rate |
| C009 deduped | target share (expect 0%) |
| C018 executed | protective share (expect 0%), train/val exp_r |
| C011 deduped null | validation exp_r, WITHIN_NULL |

Comparison is **post-hoc descriptive** — not tuning targets.

---

## Financing overlay requirement

| rule | requirement |
|---|---|
| In-engine | unmodeled |
| Overlay | mandatory `apply_financing_overlay` conservative stress |
| Blocker | validation **net** exp_r ≤ 0 after overlay → cannot recommend REVISE |
| Reporting | gross vs net exp_r per split |

Financing sample path remains **paused** — synthetic overlay only.

---

## Backtrader parity requirement

| check | threshold |
|---|---|
| trade count vs bespoke | **±1** per campaign aggregate |
| exit-reason shares | **CLOSE_MATCH** or documented MATERIAL_DIVERGENCE with root cause |
| PnL mode | `home_currency_v1` |
| Risk windows | `engine_aligned` |

Parity failure → **REJECT** independent-lane viability for C019 until resolved.

---

## Fold / split stability

| check | rule |
|---|---|
| Train-only pass with validation fail | REJECT |
| Validation pass with train fail | REJECT (C018 lesson) |
| Single pair > 60% validation R PnL | flag; informational gate G10-style from C018 |

---

## Minimum trade count

Same as repo standard: validation ≥ 30, test ≥ 20 if opened.

---

## Exact falsification criteria

Hypothesis **falsified** if any:

1. G1 fail (train exp < 0)
2. G11 fail (train worse than C008)
3. G8 fail (mechanism inert <5% or dominant >45% without train improvement)
4. G7 WITHIN_NULL vs C011
5. G6 fail (2× stress validation negative)
6. Time-exit median MFE < **1.5R** (tail collapsed)
7. Financing overlay flips validation net exp ≤ 0
8. Backtrader parity gap > ±1 trade unexplained

---

## Maximum possible status

Even if **all** gates pass including test lockbox:

| status | meaning |
|---|---|
| **RESEARCH_PASS** | Hypothesis not falsified on precommitted gates |
| **PROMOTION_REVIEW_REQUIRED** | Human review needed — financing, parity, broad-search pause |
| **APPROVED** | **Forbidden** from this campaign lane |

No update to `configs/approved_strategies.yaml` without separate human approval sprint.

---

## Pair robustness

Require ≥ 2 pairs positive on validation (G4). Report per-pair thesis_invalidation rate
and exp_r — no pair-specific threshold tuning permitted.
