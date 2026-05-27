# CAMPAIGN_018 — Exit Hypothesis Gate Design

**Date:** 2026-05-27  
**Branch:** `research-exit-hypothesis-precommit-001`  
**Status:** **PRECOMMIT ONLY — NOT EXECUTED**

> **Precommit only** — `strategy_evidence: false`. Gates apply to a **future** execution sprint.

Complements [`FUTURE_EXIT_RESEARCH_GATE.md`](FUTURE_EXIT_RESEARCH_GATE.md) and [`FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`](FUTURE_MEAN_REVERSION_RESEARCH_GATE.md).

---

## Gate philosophy

Validation-looking-good must **not** become approval. Gates are hard enough that:

- Train failure → automatic REJECT (no lockbox)
- WITHIN_NULL vs C011 → automatic REJECT
- Unmodeled financing on 40-bar holds → **blocker for promotion interpretation** (overlay required in execution sprint)
- Passing screening → permits **test lockbox run only**, not paper/demo/live

---

## Screening gate (train + validation)

Run **only** train and validation splits first. Open test lockbox **only if ALL** checks pass on **base cost** unless noted.

| # | gate | threshold | rationale |
|---|---|---|---|
| G1 | train expectancy (R) | **≥ 0.0** | C008/C009 failed here; primary falsifier |
| G2 | validation expectancy (R) | **> 0.0** | OOS edge required |
| G3 | validation profit factor | **≥ 1.05** | repo MR standard |
| G4 | validation pairs positive | **≥ 2 of 6** | not single-pair artifact |
| G5 | validation trade count | **≥ 30** | repo standard |
| G6 | validation stress 2× expectancy | **≥ 0.0** | cost robustness |
| G7 | beat-null vs C011 deduped | validation exp_r **> −0.003 + margin** | margin = **+0.010 R** minimum above null aggregate (−0.0029R); WITHIN_NULL = FAIL |
| G8 | protective-stop mechanism active | ≥ **10%** of trades trigger stop transition OR documented implementation bug if 0% | hypothesis must be testable |
| G9 | no midline/target exits | target exit share **= 0%** | C009 path forbidden |

**Screening FAIL** → verdict **REJECT**, test lockbox **stays closed**, no further splits.

---

## Train-specific diagnostic gates (non-blocking but recorded)

These do **not** override G1 failure but must be reported:

| diagnostic | compare vs C008 deduped |
|---|---|
| hard-stop exit share | expect decrease vs 68% aggregate |
| time-exit share | expect non-trivial (≥ 15%) |
| time-exit median MFE (R) | expect ≥ **2.0R** (C008 was 3.29R — large collapse falsifies tail preservation) |
| stop ≥1R-before-stop rate | descriptive only — not a gate threshold |

---

## Validation-specific gates

All screening gates (G1–G9) plus:

| # | gate | threshold |
|---|---|---|
| G10 | validation per-pair exp_r | no single pair contributes **> 60%** of total validation R PnL |
| G11 | exit bucket min count | each of {stop, time, protective/break-even} with ≥ **15 trades** or bucket collapsed in report |
| G12 | full-window stress_15x (2020–2026) | expectancy **≥ 0** (C008 passed at +0.04R — parity bar) |

---

## Test-window unlock gates

Test window (2025-01-01 → 2026-05-20) opens **only if** screening gate **PASS**.

| # | gate | threshold |
|---|---|---|
| T1 | test expectancy (R) | **≥ 0.0** |
| T2 | test profit factor | **≥ 1.0** |
| T3 | test trade count | **≥ 20** |
| T4 | combined train+val+test exp_r | **≥ 0.0** |

Test FAIL → verdict **REJECT** even if validation looked strong.

---

## Financing handling requirement

| rule | requirement |
|---|---|
| In-engine | unmodeled (same as C008) |
| Overlay | **mandatory** conservative financing stress before any REVISE recommendation |
| Blocker | if overlay flips validation expectancy negative → **cannot recommend REVISE** |
| Multi-day holds | 40-bar H4 holds cross rollovers — financing must be reported |

Execution sprint must run financing overlay before lockbox interpretation.

---

## Max drawdown / tail loss

| metric | reporting required | gate |
|---|---|---|
| validation max drawdown % | yes | **informational** — no numeric pass gate in v0.1.0-c018 |
| worst single trade R | yes | informational |
| stop-out after protective transition | yes | bucket expectancy recorded |

Hard DD gate deferred to avoid post-hoc threshold from C008/C009.

---

## Comparison requirements (execution sprint)

Must produce side-by-side table vs:

| baseline | metrics |
|---|---|
| C008 deduped forensic | train/val exp_r, exit shares, time MFE |
| C009 deduped forensic | target share (expect 0% in C018) |
| C011 deduped null | validation exp_r, WITHIN_NULL classification |

C018 must **not** be tuned to beat baselines — comparison is **post-hoc descriptive**.

---

## Beat-null requirements

- Primary: validation expectancy vs C011 deduped aggregate **−0.0029 R**
- Classification bands (same as C015 protocol):
  - **WITHIN_NULL** (|Δ| < 0.005R with similar trade count) → **REJECT**
  - **ABOVE_NULL** → necessary but not sufficient for screening pass
- Must also pass G1 train gate — beating null on validation alone is insufficient.

---

## Fold / split stability

v0.1.0-c018 uses **fixed marathon splits** (not 8-fold walk-forward):

- train 2020–2022
- validation 2023–2024
- test 2025–2026 (conditional)

No fold cherry-pick. No re-splitting after seeing results.

---

## Minimum trade counts

| window | minimum |
|---|---|
| validation | 30 |
| test (if opened) | 20 |
| per exit bucket (analysis) | 15 or collapse |

---

## Exact falsification criteria

Hypothesis **falsified** (REJECT, do not iterate exit in same campaign) if **any**:

1. G1 fails (train exp < 0) — same outcome as C008/C009.
2. G7 WITHIN_NULL on validation.
3. G6 fails (2× stress validation negative).
4. Time-exit median MFE < **1.5R** (tail collapsed toward C009 target territory).
5. Protective transition fires on **< 5%** of trades (rule inert / mis-implemented).
6. Aggregate exit share shifts entirely to break-even scratches with **validation exp ≤ 0**.

---

## What passing gates permits (and does not)

| if screening + test pass | permitted | not permitted |
|---|---|---|
| Outcome | test results recorded; **REVISE** ceiling | approval, paper, demo, live |
| Registry | stays `approved: []` | adding to approved_strategies.yaml |
| Next step | separate human promotion review OR financing sprint | automatic strategy approval |

---

## Relationship to approval

Passing these gates **does not approve** `mean_reversion_protective_stop`. It only justifies **continued research** under mean-reversion tail-risk review. Broad strategy search remains paused until separate re-entry memo.
