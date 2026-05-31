# CAMPAIGN_012 Financing / Risk Readiness

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

Phase 6 readiness doc for the FUTURE financing overlay + portfolio-risk
diagnostics that the
`research-regime-switcher-atr-percentile-walk-forward-001` evidence
sprint will produce. This doc records what the evidence sprint will
do; it does not run any of it.

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
  `src/forex_bot/financing.py`. No code change permitted. Any attempt
  to switch source in CAMPAIGN_012 must abort the runner.

### 1.2 Why MODELED stays refused

The live-promotion financing blocker (see
[`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)) stands.
Lifting it requires the separately-authorized credentialed pilot
**`research-financing-modeled-capture-credentialed-001`**, which:

- Has its own ethics + safety review.
- Captures real OANDA `DAILY_FINANCING` events under a credentialed
  account with prior human authorization.
- Populates the MODELED fixture set.
- Lifts the 4-layer refusal *only* after recorded fixtures match
  observed events within a documented tolerance.

CAMPAIGN_012's evidence sprint cannot lift this blocker. Even a
passing CAMPAIGN_012 retains the live-promotion blocker; paper
promotion remains acceptable under ESTIMATED with explicit human
override per the existing rule.

### 1.3 Expected per-trade financing impact

- **Per-rollover cost.** Order of magnitude ~$0.022–$0.023 per
  rollover event (consistent with CAMPAIGN_010 / CAMPAIGN_011 on the
  same universe + risk-per-trade-pct).
- **Holding period.** ≤ 6 H4 bars per trade (`max_bars_in_trade = 6`).
  Most trades incur 0–1 daily rollover events.
- **Total financing impact.** Scales with trade count. The regime gate
  reduces trade count (only HIGH-VOL bars qualify); total
  `cashflow_home_stress_total` is expected to be modest in absolute
  terms but **direction-dependent** under stress.
- **Pair-flip behavior.** Per CAMPAIGN_010 / 011, USD_CHF and USD_JPY
  are the candidates most likely to flip +→− under conservative
  stress; the evidence-sprint financing overlay must record the
  pair-flip table.

### 1.4 Financing-overlay artifact paths

| path | purpose |
|---|---|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.json` | per-pair per-fold rollover events + cashflow |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_run.md` | human-readable overlay summary |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/financing/financing_summary.json` | aggregate cashflow + pair-flip table |
| `docs/research/CAMPAIGN_012_FINANCING_OVERLAY.md` | sprint-level doc |

### 1.5 Financing gates (binding)

- `conservative_stress_run_does_not_flip_verdict = PASS` — if
  pre-financing the verdict is PASS but post-financing it flips, the
  overall verdict is REJECT.
- `modeled_refused = PASS` — verify the 4-layer refusal is intact.
- `missing_rate_event_count = 0` — no rollover event without a rate.

## 2. Portfolio-risk diagnostics

### 2.1 Per-instrument concurrency

- `risk.max_open_positions = 1` (engine-enforced).
- `risk.max_positions_per_instrument = 1` (engine-enforced).
- The strategy's R2 also blocks re-entry while a position is open
  (defense in depth).
- Result: max 1 open position per instrument; the runner expects
  concurrency to be structurally bounded.

### 2.2 Expected holding period

≤ 6 H4 bars per trade (~24 hours). Time-stop exit rate is expected to
be ~75 % (consistent with CAMPAIGN_010 / 011 on the same cost model
and universe). The diagnostics doc must record per-pair time-stop
fraction.

### 2.3 Expected exposure profile

- Notional per trade bounded by `risk_per_trade_pct = 0.25 %` × NAV
  divided by the ATR-stop distance.
- The regime gate suppresses trades in LOW-VOL periods, so the
  effective trade count per pair per fold is expected to be lower than
  CAMPAIGN_010 / 011's. The per-fold gate `trade_count >= 30` may be
  a binding constraint; if a pair-fold combination produces < 30
  trades it fails the fold gate.

### 2.4 Expected regime / time clustering diagnostics

The diagnostics doc must record:

- **Regime-period clustering.** Trades should cluster in HIGH-VOL
  periods (e.g. central-bank announcement weeks, FOMC, BoJ
  intervention, geopolitical-event months). Report which fold's
  HIGH-VOL periods drove the trades — this is the *signature* of a
  regime-switcher.
- **Session-of-day distribution.** Distribution across 4 UTC buckets;
  no single bucket > 50 % concentration expected. (The regime filter
  is daily, not session-of-day, so the session distribution should be
  diffuse — similar to CAMPAIGN_011 and unlike CAMPAIGN_010's 100 %
  London concentration.)
- **Per-pair ratio max/min.** For a real-edge candidate the expected
  range is intermediate between CAMPAIGN_010's 12.0 (highly
  concentrated → red flag) and CAMPAIGN_011's 1.65 (uniform → likely
  no edge).
- **Loss streaks per pair.** Length distribution; depends on regime
  persistence.
- **Drawdown clustering.** Should be moderate — the regime gate's
  purpose is to avoid the cost-drag traps that hurt CAMPAIGN_010.

### 2.5 Risk-diagnostics artifact paths

| path | purpose |
|---|---|
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.json` | machine-readable diagnostics |
| `backtests/CAMPAIGN_012_regime_switcher_atr_percentile/risk/diagnostics.md` | human-readable summary |
| `docs/research/CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md` | sprint-level doc |

### 2.6 Pipeline sanity checks (8/8 must pass)

Identical to CAMPAIGN_010 / 011:

1. Per-fold trade-count is non-zero.
2. Per-fold per-pair trade-count sums to fold trade-count.
3. No trade extends past `max_bars_in_trade`.
4. No trade exits at a price violating the stop.
5. Per-fold returns sum across pairs equal the fold aggregate.
6. RiskEngine rejection count is recorded.
7. SESSION_BLOCKED rejections are recorded (rollover / Friday close /
   Sunday open).
8. SPREAD_TOO_WIDE rejections are recorded (per-pair spread filter).

## 3. Max concurrent positions per instrument = 1

Verified by:

- `configs/campaign_012_regime_switcher_atr_percentile.yaml` sets
  `risk.max_positions_per_instrument = 1`.
- The strategy's R2 blocks re-entry on an existing position
  (`tests/unit/test_regime_switcher_atr_percentile.py::test_no_signal_when_open_position_present`).
- The engine enforces single-position per instrument.

## 4. Independent-verifier coordination

The risk diagnostics + financing overlay are item 3 + item 4 of the
six-evidence ladder. Item 5 (independent verifier) is a *separate*
prerequisite for paper promotion. See
[`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md).

## 5. What this readiness doc does NOT do

- Does not run any financing overlay.
- Does not run any risk diagnostics.
- Does not call any broker.
- Does not load any candles.
- Does not produce strategy evidence.
- Does not approve any strategy.

## 6. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md) (if present)
- [`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md) (sibling reference)
- [`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md) (sibling reference)
- [`CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_010_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling reference)
- [`CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_011_PORTFOLIO_RISK_DIAGNOSTICS.md) (sibling reference)
