# CAMPAIGN_010 — Financing + Portfolio Risk Readiness

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
`strategy_evidence: false`

Phase 6 financing-overlay + portfolio-risk integration-readiness
assessment for the **CAMPAIGN_010 research candidate**
(`session_breakout 0.1.0-c010`). **Reading this document does
not approve the strategy and does not lift the live-promotion
financing blocker.** It records whether the scaffold is
*structurally ready* for a future evidence sprint to compute
the financing overlay and the risk-engine diagnostic
checklist.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper
> / demo / live remain blocked. `MODELED` financing remains
> refused at four layers in `research/financing/`; the
> live-promotion financing blocker stands.

## 1. Headline status

| dimension | status | note |
|---|---|---|
| Financing calculator (`research.financing.calculate_run`) interface fit | **READY** | candidate emits trade intervals consumable by `PositionInterval` |
| `ESTIMATED` rate source available | **READY** | `research.financing.default_stress_rate_source()` returns a `ConservativeStressRateSource` covering all 7 pairs |
| Per-pair `TableRateSource` sample (2-week fixtures) | **READY (diagnostic only)** | committed `research/financing/fixtures/rates_two_week_*.json` (one per pair) |
| `MODELED` rate source for the candidate's window | **REFUSED** | four-layer refusal in `research/financing/`; will remain refused until a separately-authorized credentialed capture pilot lands |
| RiskEngine `mode='backtest'` integration | **READY** | existing path; no new gate required |
| Portfolio-risk diagnostic checklist computation | **READY** (structurally) | implementation can drive the existing `RiskEngine` gates; computation requires a backtest run (future evidence sprint) |
| Engine-PnL financing integration | **NOT TOUCHED (by design)** | `src/forex_bot/backtesting/engine.py` is untouched; the financing overlay is applied post-hoc as a diagnostic, **not** rolled into engine PnL |

**Net: financing-overlay plumbing readiness is GREEN with the
ESTIMATED / STRESS posture; MODELED remains refused; portfolio-
risk integration readiness is GREEN structurally with the
existing RiskEngine.**

## 2. Financing — expected holding period

The candidate's design:

- one signal per pair per *eligible* London H4 bar (zero or one
  candidate per pair per day under either NY-standard or NY-DST
  alignment per
  [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
  §3.4);
- `max_bars_in_trade = 6` (≈ 1 trading day on H4) — the time
  stop closes the position by the next London open;
- no trailing stop in v1.

**Holding-period implication:** most trades close within the
same trading day; they incur **0** financing rollover events.
A small minority span the daily 17:00-NY rollover and incur
**1** event (the conservative-stress overlay debits both
sides). Wednesday-Thursday rollover positions incur a triple
swap if held into the 17:00 NY Wednesday→Thursday boundary.

This is materially *less* financing exposure than the prior
trend-following / pullback / mean-reversion campaigns (which
allowed `max_bars_in_trade = 40 – 120` and routinely held
multi-day positions).

## 3. Financing — notional exposure required

Per the candidate's risk block:

| field | value |
|---|---|
| `starting_equity_usd` | `500` (matches CAMPAIGN_004 / 007 / 008 / 009 conservative profile) |
| `risk_per_trade_pct` | `0.25` |
| `max_open_positions` | `1` (universe-wide; very conservative) |
| `max_positions_per_instrument` | `1` |

A `Position` notional is governed by the `RiskEngine` sizing
(`size_position`) per the strategy's emitted `stop_price`. The
financing calculator's `PositionInterval` consumes the notional
verbatim; no new conversion is required.

## 4. Financing — pair / direction mapping

| pair | rate fixture (diagnostic sample) | base | quote |
|---|---|---|---|
| EUR_USD | `research/financing/fixtures/rates_two_week_eur_usd.json` | EUR | USD |
| GBP_USD | `research/financing/fixtures/rates_two_week_gbp_usd.json` | GBP | USD |
| USD_JPY | `research/financing/fixtures/rates_two_week_usd_jpy.json` | USD | JPY |
| AUD_USD | `research/financing/fixtures/rates_two_week_aud_usd.json` | AUD | USD |
| USD_CAD | `research/financing/fixtures/rates_two_week_usd_cad.json` | USD | CAD |
| USD_CHF | `research/financing/fixtures/rates_two_week_usd_chf.json` | USD | CHF |
| NZD_USD | `research/financing/fixtures/rates_two_week_nzd_usd.json` | NZD | USD |

The candidate trades both directions on every pair. The
existing `RatePair` sign convention in
[`research/financing/`](../../research/financing/) handles
`long_annual_bp` / `short_annual_bp` correctly without
modification.

## 5. Financing — treatment status

| layer | treatment cap | refusal mechanism |
|---|---|---|
| `TableRateSource` constructor | **ESTIMATED** | raises on `treatment=MODELED` |
| `calculate_run` entry point | **ESTIMATED** | raises if rate source self-reports `MODELED` |
| `_build_report` in `scripts/reconcile_financing_fixtures.py` | **ESTIMATED** | raises before write |
| `scripts/capture_oanda_observed_financing_pilot.py` | n/a (writes events, not a treatment) | does not declare a treatment |

**The candidate's first walk-forward run uses the
`default_stress_rate_source()`** per
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§10.1 Option 1. The per-pair `TableRateSource` overlays are a
diagnostic sidecar only (the committed fixtures span just two
weeks each — sufficient for a sanity check, not the full
2020–2026 universe). The headline PnL gate uses the
conservative-stress source for the full window.

## 6. `MODELED` financing remains unavailable / refused

`MODELED` financing is unavailable for the candidate's window
because:

1. The OANDA v20 REST API publishes no historical
   `DAILY_FINANCING` series for 2020–2026.
2. The repo's `observed_financing_events` table is empty (no
   capture has been authorized + executed; the capture pilot
   script
   `scripts/capture_oanda_observed_financing_pilot.py` is
   in-place but requires a credentialed run that is itself a
   separately-authorized human step per
   [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)).
3. The four refusal layers in §5 actively prevent any code
   path from emitting `MODELED`.

The candidate is therefore **structurally ineligible** for live
promotion until either a credentialed capture pilot produces
≥ 60 reconciled events and a `MODELED` `FinancingModel` is
human-approved, *or* the project's MODELED-acceptance criteria
in
[`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
§11 are otherwise satisfied.

Paper / demo promotion is separately blocked by the empty
`configs/approved_strategies.yaml` registry.

## 7. Portfolio-risk diagnostics — what the future sprint must compute

Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§9 and
[`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
§11, the future evidence sprint must produce:

| diagnostic | candidate's expected behaviour | flag if |
|---|---|---|
| per-pair exposure trace at fold boundaries | matches `RiskEngine` sizing (0.25 % equity per trade) | any fold > 0.30 % equity exposure |
| max concurrent open positions | **conservative ceiling = 1** under candidate's `max_open_positions=1` — concurrent positions across the universe are *blocked* by the risk engine, so the candidate is structurally serial | > 3 across the universe (will NOT fire under candidate's config; flag is for less-conservative variants) |
| max aggregate notional | bounded by `risk_per_trade_pct=0.25` × open count (1) | > 6 % NAV (will NOT fire under candidate's config) |
| correlation-cap activation count | bounded by `max_correlated_positions=1` | > 25 % of signals |
| daily / weekly loss-limit activation count | bounded by `max_daily_loss_pct=1.0`, `max_weekly_loss_pct=2.0` | > 5 in any fold |
| session-blackout activation count | bounded by the `session_filter` blocks (rollover 16:45–17:15 NY; Friday close; Sunday open) | > 10 % of signals |

These diagnostics are **informational** and do **not** gate the
verdict. The future sprint emits them alongside the strategy
metrics so a future paper-promotion reviewer has the
risk-engine picture without re-running the campaign.

### 7.1 Note on `max_open_positions = 1` (intentional conservative posture)

The candidate's `risk.max_open_positions = 1` means that across
the 7-pair universe, only **one** position is allowed open at a
time. Some London-open bars will produce signals on multiple
pairs simultaneously; the `RiskEngine` will accept the first
signal in deterministic order and reject the rest with a
`max_open_positions_reached` rejection code. The future
sprint's report should surface the per-fold count of
"rejected-due-to-1-position-cap" so a future variant
(`max_open_positions = 2` or `3`) can be evaluated on the same
signal stream without re-running the strategy.

This is consistent with the design's preference to never
relax a risk-engine gate at evaluation time.

## 8. Why the scaffold sprint cannot grant a financing / risk verdict

- It produced no `FinancingRunReport`.
- It produced no per-fold or per-pair `cashflow_home_total`.
- It produced no per-pair `TableRateSource` overlay against the
  candidate's actual trade list.
- It produced no per-pair exposure trace.
- It produced no risk-rejection count.
- It executed no `BacktestEngine` invocation.
- It loaded no candle data.

A non-evidence smoke (Phase 5) cannot upgrade to a financing /
risk verdict. Only the future evidence sprint can.

## 9. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT.**
- **Paper / demo / live remain blocked.**
- `MODELED` financing remains refused at four layers.
- `live-promotion` financing blocker stands.
- No broker / OANDA call made by this readiness check.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.

## 10. Cross-links

- [`CAMPAIGN_010_WALK_FORWARD_READINESS.md`](CAMPAIGN_010_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md)
- [`CAMPAIGN_010_STATUS.md`](CAMPAIGN_010_STATUS.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md`](FINANCING_BP_DAY_FIXTURE_EXPANSION_STATUS.md)
- [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- [`FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md`](FINANCING_OBSERVED_CAPTURE_PILOT_SPEC.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
