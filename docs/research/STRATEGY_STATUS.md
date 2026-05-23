# Strategy Status Registry

**Date:** 2026-05-22 · **Branch:** `research-freeze-no-go`

This is the human-readable status of every strategy family the project
has built. It is the companion to the machine-enforced registry
`configs/approved_strategies.yaml`, which gates the paper / demo / live
loops.

> ## No strategy is approved for paper, demo, or live trading.
>
> Every strategy below is **paper: NO · demo: NO · live: NO.**
> `configs/approved_strategies.yaml` is empty; every order-capable loop
> refuses to start. See `docs/research/FINAL_RESEARCH_DECISION_MEMO.md`.

## Status legend

- **rejected** — tested on real data, failed its pre-committed gates;
  not a promotion candidate.
- **research-only** — may be backtested for research; never approved for
  any trading loop.
- **blocked** — cannot be validly tested with current infrastructure.

Backtesting any strategy for research is always allowed. "Approved" here
means *only* "permitted to run in a paper / demo / live loop", and **no
strategy is approved.**

## Summary table

| strategy / version | status | paper | demo | live | primary evidence |
|---|---|:--:|:--:|:--:|---|
| `trend_following 0.1.0` (EMA + Donchian baseline) | rejected | NO | NO | NO | CAMPAIGN_002 |
| `trend_following` + ADX-14 gate (the "0.2.0 ADX" variant) | rejected | NO | NO | NO | CAMPAIGN_003 |
| `volatility_breakout 0.1.0-c004` | rejected | NO | NO | NO | CAMPAIGN_004 |
| `pullback_continuation` | rejected | NO | NO | NO | CAMPAIGN_007 |
| `mean_reversion 0.1.0-c008` | rejected (research-only) | NO | NO | NO | CAMPAIGN_008 |
| `mean_reversion 0.2.0-c009` | rejected (research-only) | NO | NO | NO | CAMPAIGN_009 |
| `session_breakout 0.1.0-c010` | rejected | NO | NO | NO | CAMPAIGN_010 |
| `random_entry_anchor 0.1.0-c011` | rejected (null model anchor) | NO | NO | NO | CAMPAIGN_011 |

There is also a daily-trend hypothesis (CAMPAIGN_006) that is **blocked**
— not a strategy verdict but an infrastructure one: D1 candles cannot be
validly backtested by the current engine.

`session_breakout 0.1.0-c010` is **rejected**: the
`research-asian-london-session-breakout-walk-forward-001`
evidence sprint ran the full 8-fold walk-forward (rolling, frozen,
540/180/180/180 days, 7-pair OANDA practice H4 universe), the
ESTIMATED + conservative-stress financing overlay, and the
portfolio-risk diagnostics, and recorded a clean REJECT against
the verbatim gates in
[`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
§10. The independent verifier did not run (it is capability-locked
to CAMPAIGN_002); this matters only for a hypothetical PASS, not
for a REJECT. See
[`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
for the gate-by-gate evidence.

### `random_entry_anchor 0.1.0-c011`

- **Status:** rejected (null model anchor — cannot be approved
  by design).
- **Evidence:** CAMPAIGN_011 walk-forward
  (`research-random-entry-diagnostic-anchor-walk-forward-001`),
  real OANDA practice H4, 7-pair universe, 8 folds
  rolling/frozen, 1,177 trades total: **fold pass rate 0 / 8,
  aggregate expectancy −0.0024 R (≈ 0; null-model signature),
  profit factor 0.91 (≈ 1), aggregate return −0.53 % over 4
  years (≈ 0), 3 / 7 pairs positive (≈ uniform-noise
  expectation), USD_JPY expectancy literally +0.0000**.
- **Paper / demo / live:** NO / NO / NO (structurally
  impossible — null model by design).
- **Reason:** Diagnostic anchor / null model. The REJECT
  verdict is the *expected and desired outcome* — it validates
  the evidence pipeline by demonstrating the gates correctly
  REJECT a known-zero-edge strategy with metrics consistent
  with random expectations. Per-pair distribution near-uniform
  (ratio max/min 1.65 vs CAMPAIGN_010's 12.0); session
  distribution diffuse across all 4 UTC buckets (vs
  CAMPAIGN_010's 100 % London); 79 % time-stop exit (matches
  CAMPAIGN_010's exit mechanics — confirms cost model
  consistency); 8 / 8 pipeline sanity checks pass.
  Conservative-stress financing strictly worsens (USD_JPY flips
  +→−; pairs_positive → 2 / 7). `master_seed = 20260523` was
  the only seed used; no seed optimization. The anchor
  establishes the falsifiability floor (aggregate expectancy
  −0.0024 R, profit factor 0.91, 3 / 7 pairs positive, 0 / 8
  fold pass rate) that every future C2 / C3 / C4 / new-family
  candidate must beat by a meaningful margin to count as
  evidence of an edge.

## Per-strategy detail

### `trend_following 0.1.0` — EMA + Donchian baseline

- **Status:** rejected.
- **Evidence:** CAMPAIGN_001 (synthetic data — harness validation only,
  not evidence), then CAMPAIGN_002 on real OANDA H4/H1 majors,
  2020–2026: **−0.085 R, profit factor 0.75, −1.02 %**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on real data; CAMPAIGN_005 showed it
  is no better than random entry once spreads are paid. Retired as a
  live candidate.

### `trend_following` + ADX-14 > 25 gate — the "0.2.0 ADX" variant

- **Status:** rejected.
- **Evidence:** CAMPAIGN_003 — the frozen baseline plus an ADX-14 > 25
  trend-strength gate, real OANDA H4, 6-pair universe:
  **−0.071 R, profit factor 0.77, −0.63 %**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** The ADX gate was the obvious fix for the baseline; it did
  not rescue it. Still negative expectancy. Retired.

### `volatility_breakout 0.1.0-c004`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_004 — breakout out of an ATR-compressed
  regime, no EMA trend filter, real OANDA H4:
  **−0.163 R, profit factor 0.63, −1.40 %** — the worst of the four
  trend/breakout families.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on real data; a genuinely different
  entry family that still failed. Retired.

### `pullback_continuation`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_007 (Research Marathon 001) — H4
  pullback-continuation. Screening failed outright: **train −0.164 R,
  validation −0.166 R**. The 2025–2026 test window was never opened.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on both screening splits. Retired.

### `mean_reversion 0.1.0-c008`

- **Status:** rejected — research-only by design (`paper_only = True`).
- **Evidence:** CAMPAIGN_008 — regime-filtered (ADX-14 < 20) reversion
  of z-score extremes, real OANDA H4. Screening **failed by a single
  gate**: train expectancy −0.017 R against a "train ≥ 0" gate.
  Validation (2023–2024) was **+0.172 R, PF 1.29, 6/6 pairs positive**,
  surviving 2× cost stress — the strongest positive signal in the
  project, but unconfirmed.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Failed its pre-committed train-split gate; capped at
  research-only; flagged for human review (`CAMPAIGN_008_HUMAN_REVIEW.md`).

### `mean_reversion 0.2.0-c009`

- **Status:** rejected — research-only (`paper_only = True`).
- **Evidence:** CAMPAIGN_009 — the human-authorized follow-up that added
  exactly one rule, a midline-target exit, and re-screened under fresh,
  stricter gates. Screening **failed**: train expectancy **−0.062 R**
  (worse than c008's −0.017 R); validation +0.170 R. The midline exit
  caps reversion winners — it falsified the rescue hypothesis.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Failed its pre-committed train-split gate by a wider
  margin than c008. The 2025–2026 test window was never opened.

### `session_breakout 0.1.0-c010`

- **Status:** rejected.
- **Evidence:** CAMPAIGN_010 walk-forward
  (`research-asian-london-session-breakout-walk-forward-001`),
  real OANDA practice H4, 7-pair universe, 8 folds rolling/frozen,
  2,791 trades total: **fold pass rate 0 / 8, aggregate
  expectancy −0.041 R, profit factor 0.04, aggregate return
  −36.6 %, 1 / 7 pairs positive (USD_CHF only)**.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** Negative expectancy on out-of-sample data on the
  pre-committed 7-pair × 6-year universe under frozen parameters.
  Conservative-stress financing strictly worsens the verdict; the
  only marginally positive pair (USD_CHF) flips to net negative.
  The breakout direction does not persist over a 6-bar H4 holding
  window; 75.5 % of trades hit the time stop.

### D1 daily trend (CAMPAIGN_006) — blocked, not a strategy verdict

- **Status:** blocked (infrastructure).
- **Evidence:** CAMPAIGN_006 — could not be validly tested. D1 candles
  close at the 17:00 NY rollover; the engine's intraday fill / session /
  spread logic is invalid for them.
- **Paper / demo / live:** NO / NO / NO.
- **Reason:** No valid result is possible until the engine gains
  next-bar-open fills and a non-rollover spread reference. This is an
  infrastructure task, not a strategy.

## How a strategy could become approved (it has not)

Approval is a deliberate human action, never a default:

1. A genuinely new, human-approved thesis (not a tweak of a rejected
   campaign).
2. A fresh pre-commit with gates fixed before the run.
3. A campaign that passes every screening gate **and** every test-window
   gate on real OANDA data, earning at most PAPER-TRADE-ONLY.
4. A human edits `configs/approved_strategies.yaml` to add the strategy
   name, with review.
5. Live trading additionally requires every existing config-layer live
   gate (acknowledgement phrase, approved config hash, etc.) and a
   modelled financing cost — none of which is satisfied today.
