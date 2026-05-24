# CAMPAIGN_014 Status — `calendar_event_window_anomaly 0.1.0-c014` — REJECT

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-walk-forward-001`
`strategy_evidence: false`

| dimension | value |
|---|---|
| candidate | `calendar_event_window_anomaly 0.1.0-c014` |
| family | calendar-event window anomaly (C7) |
| campaign id | CAMPAIGN_014 |
| **status** | **REJECT (direction-of-trade falsification)** |
| backtest verdict | REJECT (8-fold walk-forward; per-fold all REJECT) |
| walk-forward verdict | **REJECT** ([`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)) |
| null-baseline comparison | **WORSE than null on every PnL-direction axis** (OUTSIDE indistinguishability band on WORSE side) |
| financing overlay verdict | overlay applied (ESTIMATED + conservative stress; −$10.64 drag; verdict unchanged) |
| portfolio-risk diagnostics verdict | diagnostics applied; bounded concentration; FOMC = 0 trades + NFP-dominated losses surfaced |
| independent verifier status | **not run** (capability-locked to CAMPAIGN_002; not required for REJECT) |
| strategy approval | **NO — REJECT** |
| paper / demo / live | **blocked** |
| in `configs/approved_strategies.yaml` | **no** (registry remains `approved: []`) |
| enabled in `configs/paper.yaml` | **no** |
| enabled in `configs/practice.yaml` | **no** |

## What this evidence sprint produced

| deliverable | type |
|---|---|
| Phase 0 fixture date-verification audit | NEW — `CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md` |
| Phase 0 sprint plan | NEW — `CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md` |
| Phase 1 data provenance | NEW — `CAMPAIGN_014_DATA_PROVENANCE.md` |
| Phase 2 walk-forward plan | NEW — `backtests/.../walk_forward/{plan.json,plan.md}` + `CAMPAIGN_014_WALK_FORWARD_PLAN.md` |
| Phase 3 runner | NEW — `scripts/run_campaign_014.py` (~620 LOC) |
| Phase 4 execution | NEW — 56 per-pair per-fold summary JSONs + trades CSVs + `walk_forward/{results.json,results.md,fold_detail.json}` + `CAMPAIGN_014_WALK_FORWARD_EXECUTION.md` |
| Phase 5 verdict + null-baseline | NEW — `CAMPAIGN_014_WALK_FORWARD_RESULT.md` |
| Phase 6 financing overlay | NEW — `scripts/build_campaign_014_financing_overlay.py` + `financing/{financing_run.json,financing_run.md,financing_summary.json}` + `CAMPAIGN_014_FINANCING_OVERLAY.md` |
| Phase 7 risk diagnostics | NEW — `scripts/build_campaign_014_risk_diagnostics.py` + `risk/{diagnostics.json,diagnostics.md}` + `CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md` |
| Phase 8 verifier status | NEW — `CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md` |
| Phase 9 (this) | NEW — sprint summary + `EVIDENCE_INDEX.md` update + `EVIDENCE_MANIFEST.json` update + `STRATEGY_STATUS.md` update + this STATUS revision + test campaign-count assertion update (13 → 14) |

## What this evidence sprint did NOT do

| dimension | value |
|---|---|
| approve any strategy | **NO** |
| modify `configs/approved_strategies.yaml` | **NO** (remains `approved: []`) |
| modify CAMPAIGN_002 / 010 / 011 / 012 / 013 verdict | **NO** |
| modify CAMPAIGN_014 frozen parameters post-result | **NO** |
| relax `max_open_positions` | **NO** |
| pair-only carve-out for ECB + BoE (slightly +) | **NO** (Pattern P binding refuses) |
| modify fixture mid-evidence (e.g. patch BoJ 2026-03 drift) | **NO** (drift logged for future fixture-revision sprint) |
| broker / OANDA call | **NONE** |
| `.env` read | **NONE** |
| credential print | **NONE** |
| account / order / trade / position / transaction endpoint queried | **NONE** |
| QuantConnect / LEAN command | **NONE** |

## What this means

`calendar_event_window_anomaly 0.1.0-c014` is the 5th REJECT
verdict in the recent C-family sweep
(010 → 011 (null) → 012 → 013 → 014). Unlike C012 / C013, C014's
REJECT is NOT a turnover-amplification failure — turnover stayed
within budget (720 ≤ 800; 1,240 ≤ 1,500). The REJECT is
**direction-of-trade falsification**: the hypothesis that "H4
bars immediately after scheduled macro events mean-revert" is
empirically WRONG on this universe — the post-event H4 bar
**continues** the event-bar's direction.

Phase 7 surfaced two findings of independent research value:

1. **FOMC = 0 trades.** The session_filter blocks the 22:00-UTC
   trigger bar following the 19:00-UTC FOMC release. The 51 FOMC
   events in the fixture generate zero trades on any of the 7 USD
   pairs. The C7 hypothesis's claim about FOMC is structurally
   untestable here.
2. **NFP dominates and loses.** 571 / 720 trades (79 %) are
   NFP-triggered, generating −$151.17 (98 % of total losses).
   Near-50/50 long/short → losses on both sides → continuation,
   not reversion.

## Relation to prior campaigns

| campaign | status | relation to CAMPAIGN_014 |
|---|---|---|
| CAMPAIGN_002 | REJECT (`trend_following 0.1.0`) | unrelated — no shared mechanism |
| CAMPAIGN_010 | REJECT (`session_breakout 0.1.0-c010`) | unrelated — no Asian/London/session windowing |
| CAMPAIGN_011 | REJECT (null-model anchor `random_entry_anchor 0.1.0-c011`) | **null baseline** — CAMPAIGN_014 is materially WORSE on every PnL-direction axis (OUTSIDE indistinguishability band on WORSE side) |
| CAMPAIGN_012 | REJECT (`regime_switcher_atr_percentile 0.1.0-c012`) | unrelated — no single-pair vol-percentile gate |
| CAMPAIGN_013 | REJECT (`cross_pair_currency_strength_rotation 0.1.0-c013`) | unrelated — no cross-pair ranking |

All five prior campaigns remain REJECT and are untouched.

## Why CAMPAIGN_014 cannot be revived

Per [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
+ [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
(Patterns A–W binding):

- Re-tuning event-set, ATR settings, max-hold, re-entry-block, or
  any other frozen parameter would be Pattern C / H / I / J
  (parameter-tweak rescue) — **forbidden**.
- Pair carve-out (e.g. "trade only ECB on EUR_USD; only BoE on
  GBP_USD") is Pattern P (pair-only survivor selection) —
  **forbidden** even though those cells are slightly +.
- Adding a turnover-amplifying filter (e.g. "trade post-NFP every
  4 hours for 24 hours") is Pattern O — **forbidden**.
- Restructuring the session_filter to enable FOMC trading would
  be a NEW candidate (changes universe / cost-model identity).

A genuinely new event-window candidate (e.g. event-CONTINUATION
opposite-direction strategy, finer-timeframe M30/H1 study) would
require a fresh discovery sprint with pre-committed gates — none
of which are scheduled.

## Safety state (verified at sprint close)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers; intact) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 / 012 / 013 untouched) |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| `max_open_positions` relaxation | **none** |
| pair carve-out | **none** (ECB + BoE positive cells flagged but NOT used) |
| fixture modification mid-sprint | **none** (BoJ 2026-03 drift logged only) |

## Cross-links

- [`CAMPAIGN_014_EVIDENCE_SUMMARY.md`](CAMPAIGN_014_EVIDENCE_SUMMARY.md) (one-page summary)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_WALK_FORWARD_001_PLAN.md)
- [`CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md`](CAMPAIGN_014_EVENT_FIXTURE_DATE_VERIFICATION.md)
- [`CAMPAIGN_014_DATA_PROVENANCE.md`](CAMPAIGN_014_DATA_PROVENANCE.md)
- [`CAMPAIGN_014_WALK_FORWARD_PLAN.md`](CAMPAIGN_014_WALK_FORWARD_PLAN.md)
- [`CAMPAIGN_014_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_014_WALK_FORWARD_EXECUTION.md)
- [`CAMPAIGN_014_WALK_FORWARD_RESULT.md`](CAMPAIGN_014_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_014_FINANCING_OVERLAY.md`](CAMPAIGN_014_FINANCING_OVERLAY.md)
- [`CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_014_PORTFOLIO_RISK_DIAGNOSTICS.md)
- [`CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_STATUS.md)
- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
