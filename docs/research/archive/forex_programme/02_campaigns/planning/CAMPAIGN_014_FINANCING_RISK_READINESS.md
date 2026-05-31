# CAMPAIGN_014 Financing / Risk Readiness

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 7 financing-overlay + portfolio-risk-diagnostics readiness
summary for the **future** CAMPAIGN_014 evidence sprint. **Scaffold
sprint only — no financing-overlay run, no risk-diagnostics run.**

> No strategy approved. **A passing readiness doc is NOT approval
> and is NOT evidence.** The financing / risk runs will execute in
> the future evidence sprint.

## 1. Financing source (binding)

| dimension | value |
|---|---|
| treatment | **ESTIMATED + conservative-stress only** |
| MODELED status | **refused at 4 layers** in `src/forex_bot/financing.py` |
| MODELED-availability gate | the future evidence sprint's `scripts/build_campaign_014_financing_overlay.py` MUST abort if treatment is MODELED |
| conservative-stress overlay | required (per CAMPAIGN_010 / 011 / 012 / 013 pattern) |
| home currency | USD |
| missing_rate policy | `conservative` (debit-on-both-sides bp/day fallback) |

## 2. Expected holding period

| dimension | value |
|---|---|
| signal triggers on | first post-event H4 bar (the "trigger bar") |
| max holding period | `max_post_event_bars = 6` H4 bars (= 1 trading day) |
| typical holding period | 2–6 H4 bars (≤ 1 day) |
| financing exposure per trade | **< 1 bp** (one rollover at most, often zero if trade exits before 21:00 UTC rollover) |

Short hold ⇒ financing is small per trade ⇒ ESTIMATED +
conservative-stress is sufficient for research evidence (MODELED
unblock would only be required for live promotion).

## 3. Expected low turnover

Per [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) §10:

- expected trades over 4-year walk-forward: **~320–520**
- comparison to CAMPAIGN_011 null (1,177): ~3.5–7 × less
- comparison to CAMPAIGN_013 (7,940): ~15–25 × less

Combined with short hold, the **aggregate financing cashflow over
the full walk-forward** is expected to be on the order of **$5–15
USD total drag** (rough estimate: ~400 trades × ~30 % financing-
exposed × ~0.05 USD per rollover under conservative stress). For
reference, CAMPAIGN_013 had −$139.99 over 7,940 trades; CAMPAIGN_011
had −$24.38 over 1,177.

## 4. Max concurrent positions per instrument

| dimension | value |
|---|---|
| `RiskConfig.max_open_positions` | 1 |
| `RiskConfig.max_positions_per_instrument` | 1 |
| simultaneous-pair entries possible? | YES for NFP / FOMC days (event impacts all 7 USD pairs simultaneously) — but each pair trade is independent and per-pair-capped |

**Note on NFP / FOMC simultaneous entries:** unlike CAMPAIGN_013's
cross-pair rotator which fired ~40 % of trades simultaneously across
multiple pairs without portfolio-level edge proof (Pattern N), C7's
NFP / FOMC simultaneous-pair entries are **explicitly justified by
the hypothesis** (the event affects USD specifically, so all USD-
pairs are simultaneously informative; this is the cleanest form of
portfolio-level edge proof — same event-driven mechanism per pair).
The future risk diagnostics (§7) will measure this simultaneous-pair
behavior and confirm it does not produce concentration risk.

## 5. Per-event-class diagnostic battery (binding for future evidence sprint)

The future `scripts/build_campaign_014_risk_diagnostics.py` MUST
produce **standard** + **CAMPAIGN_014-specific** diagnostics:

### 5.1 Standard battery (from CAMPAIGN_010 / 011 / 012 / 013)

- 8 sanity checks (consistency between trade-log + engine PnL + daily
  marks + summary JSON)
- Per-pair exposure (units; total notional)
- Per-fold long/short imbalance
- Per-pair max loss / win streak
- Spread filter rejection counts (per pair; per reason)
- Session filter rejection counts
- MAX_OPEN_POSITIONS_EXCEEDED count
- Drawdown clustering
- Exit-reason distribution (stop-loss / time-stop / spread-rejected)

### 5.2 CAMPAIGN_014-specific (new)

- **Event-class clustering**: per-event-class (NFP / FOMC / ECB /
  BoJ / BoE) PnL distribution + trade-count breakdown + median
  trade PnL
- **Per-event-class per-pair sensitivity**: heatmap of event-class
  × pair → aggregate PnL (5 classes × 7 pairs = 35 cells; many will
  be N/A by design — e.g. ECB only impacts EUR_USD)
- **Pre-event vs post-event direction breakdown**: confirms the
  signal-direction rule (positive event-bar return → SHORT; negative
  → LONG) is balanced across event classes; no class systematically
  produces one-sided signals
- **Entry-window concentration**: fraction of trades occurring within
  each post-event bar offset (= 1 by R3 — should be 100 % at offset
  1; verifies R3 binding)
- **Event-fixture coverage report**: per-fold `fixture_covers_test_window`
  boolean status

### 5.3 Concurrent-rejection diagnostic

For simultaneous-pair NFP / FOMC events: report how many of the 7
impacted pairs actually fired signals (out of 7), and how many were
filtered by RiskEngine (SPREAD_TOO_WIDE / SESSION_BLOCKED /
DRAWDOWN_LIMIT). This confirms the simultaneous-pair behavior is
NOT producing pathological concentration (per Pattern N defense).

## 6. Concurrent positions per instrument = 1

`max_positions_per_instrument = 1` enforced at the RiskEngine level
+ R2 (no signal when position already open) at the strategy level.
**Defense in depth.** No portfolio-wide cap relaxation will be
proposed by the evidence sprint regardless of any per-pair
concentration finding (per the binding "no `max_open_positions`
relaxation" rule).

## 7. Risk diagnostics expected in future evidence sprint

| diagnostic | source | required |
|---|---|---|
| 8 sanity checks (CAMPAIGN_010 baseline) | standard | ✓ |
| Per-pair exposure | standard | ✓ |
| Per-fold long/short imbalance | standard | ✓ |
| Per-pair streaks | standard | ✓ |
| Spread / session rejection counts | standard | ✓ |
| MAX_OPEN_POSITIONS_EXCEEDED | standard | ✓ |
| Drawdown clustering | standard | ✓ |
| **Event-class PnL distribution** | NEW (C7-specific) | ✓ |
| **Per-event-class per-pair sensitivity heatmap** | NEW (C7-specific) | ✓ |
| **Pre/post event direction balance** | NEW (C7-specific) | ✓ |
| **Entry-window concentration** | NEW (C7-specific) | ✓ |
| **Event-fixture coverage per fold** | NEW (C7-specific) | ✓ |
| **Concurrent-rejection diagnostic for NFP / FOMC** | NEW (C7-specific) | ✓ |

## 8. No evidence run yet

| dimension | value |
|---|---|
| financing overlay run | **NOT RUN** (scaffold sprint only) |
| financing-overlay script | **NOT CREATED** (`scripts/build_campaign_014_financing_overlay.py` is a future-evidence-sprint deliverable) |
| risk diagnostics run | **NOT RUN** |
| risk-diagnostics script | **NOT CREATED** (`scripts/build_campaign_014_risk_diagnostics.py` is a future-evidence-sprint deliverable) |

## 9. Explicit no-approval statement

**The future evidence sprint's financing / risk runs cannot approve
the strategy.** Even a clean financing-overlay result + clean risk-
diagnostics result + clean walk-forward verdict produces at most
`RESEARCH_PASS_UNAPPROVED`, which still requires the verifier-
extension sprint + a deliberate human approval action per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

## 10. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |

## 11. Cross-links

- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md) (walk-forward readiness)
- [`CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_014_INDEPENDENT_VERIFIER_READINESS.md) (verifier readiness)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md) (MODELED status)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
