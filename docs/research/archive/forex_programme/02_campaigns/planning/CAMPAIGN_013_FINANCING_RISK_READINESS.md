# CAMPAIGN_013 Financing / Risk Readiness

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

Phase 6 readiness doc for the FUTURE financing overlay + portfolio-
risk diagnostics that the
`research-cross-pair-currency-strength-rotation-walk-forward-001`
evidence sprint will produce. Records what the evidence sprint will
do; does not run any of it.

> No financing overlay run. No risk diagnostics run. No broker call.
> No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. **MODELED financing remains refused** at all 4
> layers in `src/forex_bot/financing.py`; this is not lifted by this
> sprint or by the future evidence sprint.

## 1. Financing overlay (ESTIMATED + conservative-stress only)

### 1.1 Authorized source

- **ESTIMATED** financing via the existing `research/financing/`
  calculator.
- **Conservative stress** via `default_stress_rate_source()`.
- **MODELED is refused** at all 4 layers in
  `src/forex_bot/financing.py`. No code change permitted. Any
  attempt to switch source in CAMPAIGN_013 must abort the runner.

### 1.2 Expected per-trade financing impact

- **Per-rollover cost.** Order of magnitude ~$0.022–$0.023 per
  rollover event (consistent with CAMPAIGN_010 / 011 / 012 on the
  same universe).
- **Holding period.** ≤ 6 H4 bars per trade (`max_bars_in_trade = 6`).
  Most trades incur 0–1 daily rollover events.
- **Cross-pair systematic balance.** Cross-pair rotation creates
  **systematic long/short balance** across pairs (e.g. long EUR_USD
  often implies short USD_JPY when EUR is strong and JPY is weak).
  Expected net financing impact: approximately neutral. The per-pair
  recording must still pass.
- **Pair-flip behavior.** Per CAMPAIGN_010 / 011 / 012, USD_CHF and
  USD_JPY are typical flip candidates under conservative stress; the
  evidence-sprint financing overlay must record the pair-flip table.

### 1.3 Financing-overlay artifact paths

| path | purpose |
|---|---|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.json` | per-rollover-event detail |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_run.md` | human-readable per-position summary |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/financing/financing_summary.json` | aggregate + by-pair / by-side / by-fold breakdown |
| `docs/research/CAMPAIGN_013_FINANCING_OVERLAY.md` | sprint-level doc |

### 1.4 Financing gates (binding)

- `conservative_stress_run_does_not_flip_verdict = PASS`.
- `modeled_refused = PASS` — verify the 4-layer refusal is intact.
- `missing_rate_event_count = 0` — no rollover event without a rate.

## 2. Portfolio-risk diagnostics

### 2.1 Per-instrument concurrency

- `risk.max_open_positions = 1` (engine-enforced).
- `risk.max_positions_per_instrument = 1` (engine-enforced).
- The strategy's R2 also blocks re-entry while a position is open
  (defense in depth).
- Result: max 1 open position per instrument.

### 2.2 Expected holding period

≤ 6 H4 bars per trade (~24 hours). Time-stop exit rate expected to
be ~75 % (consistent with CAMPAIGN_010 / 011 / 012). The diagnostics
doc must record per-pair time-stop fraction.

### 2.3 Expected exposure profile

- Notional per trade bounded by `risk_per_trade_pct = 0.25 %` × NAV
  divided by the ATR-stop distance.
- Cross-pair rotation may produce *uneven trade counts across pairs*
  if certain pair rank-gaps rarely exceed threshold.
- Aggregate trade count is potentially much lower than CAMPAIGN_010
  / 011 / 012 because of the
  `MAX_OPEN_POSITIONS_EXCEEDED` rejection mechanism (§2.6).

### 2.4 Expected simultaneous-signal diagnostics (CAMPAIGN_013-specific)

The cross-pair rotator naturally generates **multiple simultaneous
signals** when rank gaps are wide. The diagnostics must record:

- **Rank-gap distribution histogram** per pair per fold — how often
  does the gap exceed threshold?
- **Simultaneous-signal frequency** — at how many bars does the
  strategy signal on 2+, 3+, 4+, 5+ pairs concurrently?

### 2.5 Currency-rank flip + pair-direction conflict diagnostics (CAMPAIGN_013-specific)

- **Currency-rank flip rate** — how often does a currency move from
  top-rank to bottom-rank within a single lookback window?
  (Stability diagnostic.)
- **Pair-direction conflict rate** — fraction of bars where, e.g.,
  USD_JPY and USD_CAD would signal *opposite* directions for USD
  (i.e. the runs of inconsistent USD-vs-other-currency signals).
  Sanity check on the currency-strength derivation.

### 2.6 `MAX_OPEN_POSITIONS_EXCEEDED` (or equivalent) rejection rate

With `risk.max_open_positions = 1` and cross-pair concurrent signals,
many signals will be **rejected** by the RiskEngine when a position is
already open on another pair. The diagnostics must record:

- Per fold per pair rejection counts.
- Aggregate rejection rate as fraction of total signals.

**This is known behavior of C6, NOT a bug to fix.** The evidence
sprint records the rejection rate honestly and does NOT relax
`max_open_positions` to "rescue" trade count. If C6 cannot clear the
`trade_count_min = 200` aggregate gate, that itself is part of the
research evidence (the candidate is operationally infeasible under
the project's current risk envelope).

### 2.7 Standard pipeline sanity checks (8/8 must pass)

Same as CAMPAIGN_010 / 011 / 012:

1. Per-fold trade-count non-zero.
2. Per-fold per-pair trade-count sums to fold trade-count.
3. No trade exceeds `max_bars_in_trade = 6`.
4. No trade exits at a price violating the stop.
5. Per-fold returns sum across pairs = fold aggregate.
6. RiskEngine rejection counts recorded.
7. SESSION_BLOCKED rejections present.
8. SPREAD_TOO_WIDE rejections present.

### 2.8 Risk-diagnostics artifact paths

| path | purpose |
|---|---|
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.json` | machine-readable diagnostics (including CAMPAIGN_013-specific) |
| `backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/risk/diagnostics.md` | human-readable summary |
| `docs/research/CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md` | sprint-level doc |

## 3. Max concurrent positions per instrument = 1

Verified by:

- `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`
  sets `risk.max_positions_per_instrument = 1`.
- The strategy's R2 blocks re-entry on an existing position.
- The engine enforces single-position per instrument.

**Cross-pair caveat:** `max_open_positions = 1` is across all pairs
combined; this means at most one pair can have an open position at
any time. Cross-pair rotation generating multiple simultaneous
signals will see most of them rejected (§2.6).

## 4. Independent-verifier coordination

The risk diagnostics + financing overlay are item 3 + item 4 of the
six-evidence ladder. Item 5 (independent verifier) is a *separate*
prerequisite for paper promotion. See
[`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md).

## 5. What this readiness doc does NOT do

- Does not run any financing overlay.
- Does not run any risk diagnostics.
- Does not call any broker.
- Does not load any candles.
- Does not produce strategy evidence.
- Does not approve any strategy.

## 6. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md), [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md), [`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md) (sibling references)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md), [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md), [`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling references)
