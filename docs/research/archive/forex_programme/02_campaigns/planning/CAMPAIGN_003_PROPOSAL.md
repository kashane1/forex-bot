# CAMPAIGN_003 Proposal

Status: **PROPOSAL ONLY. Not approved, not run.** This document
proposes the next research campaign. It does not change any strategy
rule, run any backtest, or touch the paper/demo/live path. Execution
requires explicit sign-off.

## Scope discipline

The user's instruction: no more than 2 strategy hypotheses, no broad
optimizer, fixed splits, explicit gates, real OANDA data, RiskEngine
wired in, no promotion unless gates pass.

**This proposal recommends ONE strategy hypothesis, not two.** The
diagnostics point clearly enough that hedging across two families would
spend evidence-generation effort without sharpening the question. The
single hypothesis below is a *compound condition test* on the existing
frozen entry; the alternative family (volatility breakout) is explicitly
deferred to a possible CAMPAIGN_004 and only becomes the priority if
CAMPAIGN_003 fails.

## The hypothesis — CAMPAIGN_003-H1

> **Restricting the frozen Donchian breakout to favourable conditions —
> H4 only, a cost-viable universe, and an established-trend regime
> filter — lifts trend-following expectancy across break-even on the
> untouched test split.**

This is Option A from the task brief. It tests a single causal claim:
*the baseline fails because it takes the breakout in the wrong
conditions, not because the breakout entry is irreparable.* If
CAMPAIGN_003 still fails, that claim is falsified and CAMPAIGN_004
should test a different entry family (volatility breakout, H-11) — at
which point the breakout-conditioning question is settled and not
revisited.

### Why this and not Option B (volatility breakout) first

The CAMPAIGN_002 diagnostics isolate the failure precisely: 452 trades
exit on the initial stop with the trailing stop never engaging
(−0.744R, 0% win) — immediate reversals. The trailing-stop mechanism
itself is mildly positive. So the defect is *entry timing in chop*. An
ADX regime filter attacks that directly and is a minimal change to a
frozen, already-validated strategy. Volatility breakout is a new family
with its own parameters and its own false-breakout exposure — a larger,
less controlled step. Test the cheap, decisive question first.

### Strategy definition (new version: `trend_following 0.2.0-c003`)

Frozen baseline rules, **unchanged**:
- EMA 50 / 200 direction filter.
- Donchian-20 breakout using prior bars only.
- ATR-14, 2.0×ATR initial stop, 2.0×ATR trailing stop.
- 0.25% risk per trade, one open position per instrument.

New conditions for CAMPAIGN_003 (all pre-committed, **no sweep**):
1. **H4 only.** H1 is dropped from the campaign matrix (H-01).
2. **Universe:** drop **NZD_USD** on a cost-structure basis (widest
   median spread, 2.5 pips; only 38 H4 trades survive 6 years — barely
   tradeable). Keep the other six: EUR_USD, GBP_USD, USD_JPY, AUD_USD,
   USD_CAD, USD_CHF. The exclusion is justified by spread/ATR
   structure, **not** by NZD_USD's realized return — see Overfitting
   controls.
3. **ADX-14 regime filter (H-05):** an entry is allowed only when
   ADX-14 on the H4 series is **> 25** at signal time. 25 is the
   textbook "trend present" threshold, pre-committed; it is **not**
   optimized or swept.

That is the entire change set: one timeframe restriction, one universe
exclusion, one new pre-committed filter. No parameter grid.

### Data

- Real OANDA practice candles only, host `api-fxpractice.oanda.com`.
- Reuse the CAMPAIGN_002 H4 candles already stored in
  `data/campaign_002.sqlite3` (provenance hashes already recorded), or
  re-fetch into a `data/campaign_003.sqlite3` — either way the data
  source must be declared and hashed in the report.
- No synthetic data.

### Splits (fixed, identical to CAMPAIGN_002)

- Train: 2020-01-01 → 2022-12-31
- Validation: 2023-01-01 → 2024-12-31
- Untouched test: 2025-01-01 → 2026-05-20
- Full descriptive: 2020-01-01 → 2026-05-20

The ADX threshold is **pre-committed at 25 before any split is run** —
it is not chosen on train. If a future campaign wants to tune it, that
is a separate, explicitly-labelled optimization campaign with its own
deflated-Sharpe / probability-of-backtest-overfitting controls.

### Cost regimes

Same three as CAMPAIGN_002: base, stress_15x (1.5× spread + 0.3 pip),
stress_2x (2.0× spread + 0.5 pip).

### Run matrix

2 strategy versions? **No — one.** `trend_following 0.2.0-c003` only.

- Baseline phase: 1 strategy × 6 pairs × 4 splits = 24 runs.
- Cost stress: 1 strategy × 6 pairs × 3 regimes (full window) = 18 runs.
- **No robustness grid** unless the baseline phase passes its gate —
  and even then the grid is for sensitivity reporting, not selection.

Total: ~42 runs. Small, fast, controlled. No optimizer anywhere.

### RiskEngine

Wired in exactly as CAMPAIGN_002 (`mode="backtest"`). Rejected signals
and reasons recorded. The parity test must still pass.

### Financing

Still **unmodeled** for CAMPAIGN_003 — but the report must:
- restate the financing blocker from `docs/financing_decision.md`;
- apply the conservative financing stress estimate from that document
  as a separate "financing-stressed" column on the untouched-test
  result;
- state explicitly that **even a passing CAMPAIGN_003 cannot promote to
  live until H-09 (the financing model) is done.** CAMPAIGN_003 can at
  most earn a PAPER-TRADE-ONLY recommendation.

## Pass / fail gates (pre-committed)

CAMPAIGN_003-H1 **passes** (earns a PAPER-TRADE-ONLY recommendation,
not live) only if **all** hold:

1. Untouched-test expectancy ≥ **+0.05R** after base costs.
2. Untouched-test profit factor ≥ **1.10**.
3. Untouched-test result is positive on **≥ 3 of 6 pairs** — not
   carried by a single pair.
4. Under **stress_2x**, untouched-test expectancy remains **≥ 0**
   (survives doubled costs).
5. The financing-stressed untouched-test expectancy (conservative
   estimate applied) remains **≥ 0**.
6. RiskEngine parity test still green; data audit shows no new defects.

If any gate fails → **REJECT or REVISE**, and the recommendation is
explicitly *not* paper-trade. If CAMPAIGN_003 fails, the conclusion is
"conditioning the Donchian breakout does not rescue it" and CAMPAIGN_004
should test the volatility-breakout family (H-11) as a different entry.

**Live promotion is out of scope for CAMPAIGN_003 entirely** — the best
attainable outcome is PAPER-TRADE-ONLY, and only if all six gates pass
AND H-09 financing modeling is subsequently completed.

## Overfitting controls

- One new parameter (ADX threshold), pre-committed to a textbook value,
  never swept.
- The universe exclusion (NZD_USD) is justified structurally
  (spread/ATR), not by its CAMPAIGN_002 return. Residual leakage risk
  is acknowledged: NZD_USD *was* also the worst-returning pair, so the
  exclusion is not perfectly clean. The report must show results
  **with and without** NZD_USD so the reader can see the exclusion's
  effect rather than trust it.
- No robustness grid in the decision path — the grid, if run at all,
  is sensitivity reporting only and cannot change the strategy.
- Fixed splits committed before the run; ADX threshold committed
  before the run.
- Every run recorded, not just winners (same as CAMPAIGN_001/002).

## What CAMPAIGN_003 will NOT do

- Will not optimize or sweep any parameter.
- Will not test a second strategy family in the same campaign.
- Will not enable paper-loop, demo-loop, or order submission.
- Will not promote anything to live.
- Will not modify the frozen `0.1.0-baseline-frozen` strategy.

---

## Proposed CAMPAIGN_003 prompt

> Run CAMPAIGN_003 per `docs/research/CAMPAIGN_003_PROPOSAL.md`.
>
> Create a new versioned strategy `trend_following 0.2.0-c003`: the
> frozen baseline rules plus three pre-committed conditions — H4 only,
> universe excluding NZD_USD (EUR_USD, GBP_USD, USD_JPY, AUD_USD,
> USD_CAD, USD_CHF), and an ADX-14 > 25 regime filter. Do not sweep or
> optimize the ADX threshold; 25 is fixed before any run.
>
> Add the ADX-14 indicator to `strategies/indicators.py` with unit
> tests. Add the new strategy as its own module/version; do not edit
> `0.1.0-baseline-frozen`.
>
> Use real OANDA practice H4 candles only (declare and hash the data
> source). RiskEngine wired in (`mode="backtest"`); the parity test must
> stay green. Fixed splits: train 2020-2022, validation 2023-2024,
> untouched test 2025-01-01 → 2026-05-20, full descriptive. Cost
> regimes base / stress_15x / stress_2x.
>
> Run matrix: 1 strategy × 6 pairs × 4 splits + cost stress (~42 runs).
> No robustness grid in the decision path. Record every run.
>
> Financing stays unmodeled but the report must restate the blocker and
> apply the conservative financing stress estimate from
> `docs/financing_decision.md` as a separate column. The best possible
> recommendation is PAPER-TRADE-ONLY; live is out of scope.
>
> Apply the six pre-committed pass/fail gates in the proposal. Produce
> `backtests/CAMPAIGN_003_REPORT.md` with provenance, data audit,
> RiskEngine rejection summary, metrics by split/pair, cost stress,
> results with and without NZD_USD, financing-stressed column, and a
> REJECT / REVISE / PAPER-TRADE-ONLY / CONTINUE-RESEARCH recommendation.
> Do not overwrite CAMPAIGN_001 or CAMPAIGN_002 artifacts. Do not enable
> any order submission.
