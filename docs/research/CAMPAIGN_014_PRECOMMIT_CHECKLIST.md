# CAMPAIGN_014 Pre-Commit Checklist

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 5 binding pre-commit checklist for **CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`**. **This pre-commit
freezes the candidate's hypothesis, frozen parameters, fixture
schema, no-lookahead invariants, turnover budget, cost section, and
gate vector before any walk-forward evidence runs.** The future
evidence sprint's runner asserts these match the loaded YAML
verbatim (`_assert_frozen()` pattern from CAMPAIGN_010 / 011 / 012 /
013 runners). **Scaffold sprint only — no historical backtest, no
walk-forward evidence, no broker call.**

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain
> REJECT and untouched. `configs/approved_strategies.yaml` remains
> `approved: []`. CAMPAIGN_011 is the null baseline only.

## 1. Hypothesis (binding; verbatim from
[`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) §1)

Around scheduled high-impact macroeconomic events (US NFP, US FOMC
rate decisions, ECB rate decisions, BoJ rate decisions, BoE rate
decisions), USD-pair returns exhibit a **mean-reverting overshoot**
in the H4 bars immediately after the event close.

Trade **counter to the first post-event H4 bar's direction** with an
H4 ATR-2 stop and a max-hold of `max_post_event_bars` (= 6) H4 bars.

This is a single-pair, single-leg, time-stop-only, ATR-stopped
counter-trend hypothesis **conditional on a public scheduled
calendar event**, not on a within-pair price statistic.

## 2. Implementation files (committed)

| file | role |
|---|---|
| `src/forex_bot/calendar_events.py` | event-fixture loader + helpers (≥ 270 LOC) |
| `src/forex_bot/strategies/calendar_event_window_anomaly.py` | strategy module (≥ 320 LOC) |
| `src/forex_bot/strategies/__init__.py` | re-export `CalendarEventWindowAnomalyStrategy` |
| `src/forex_bot/config.py` | `CalendarEventWindowAnomalyStrategyConfig` + `StrategyConfig` slot |
| `tests/unit/test_calendar_event_window_anomaly.py` | 93 unit tests |
| `configs/campaign_014_calendar_event_window_anomaly.yaml` | research-only candidate config |
| `scripts/build_campaign_014_event_fixture.py` | deterministic fixture compilation script |

## 3. Fixture files (committed)

| file | role |
|---|---|
| `research/calendar/fixtures/campaign_014_events.json` | 281-event committed fixture: NFP 77 + FOMC 51 + ECB 51 + BoJ 51 + BoE 51; coverage 2020-01-01 → 2026-05-20; UTC timestamps |
| `docs/research/CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` | provenance doc — source URLs, deterministic compilation, no-network rails, scaffold-grade date accuracy note + future-evidence audit step |

## 4. Config files (committed)

| file | role |
|---|---|
| `configs/campaign_014_calendar_event_window_anomaly.yaml` | research-only YAML; `trading_enabled: false`; `allow_order_submission: false`; `allow_live_trading: false`; same 7-pair universe; same database path as CAMPAIGN_010 / 011 / 012 / 013 |

## 5. Frozen parameters (binding; mirrors implementation spec §5)

| parameter | value | rationale / bounds |
|---|---|---|
| `version` | `0.1.0-c014` | binding string |
| `timeframe` | `H4` | matches CAMPAIGN_010 / 011 / 012 / 013 |
| `event_calendar_path` | `research/calendar/fixtures/campaign_014_events.json` | committed text fixture; broker-free |
| `event_set` | `[NFP, FOMC, ECB, BoJ, BoE]` | pre-declared; mid-sprint expansion forbidden |
| `impact_ordering` | `[FOMC, NFP, ECB, BoJ, BoE]` | pre-declared precedence for R4 overlap |
| `post_event_window_bars` | `6` | matches CAMPAIGN_010 / 011 / 012 / 013 max-hold envelope |
| `atr_lookback` | `14` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim |
| `atr_stop_multiple` | `2.0` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim; within standing `[1.0, 3.0]` |
| `max_post_event_bars` | `6` | maximum holding time (= `post_event_window_bars`) |
| `re_entry_block_bars` | `3` | new for C7; prevents same-event re-entry |
| `event_warmup_bars` | `1` | ≥ 1 completed event before signaling |
| `trailing_stop_atr_multiple` | `null` | v1 uses time-stop only; validator rejects non-null |
| `min_atr_pips` | `{}` | no per-pair floor in v1 |
| `risk.starting_equity_usd` | `500` | matches CAMPAIGN_010 / 011 / 012 / 013 |
| `risk.risk_per_trade_pct` | `0.25` (= 0.25 % per trade per the YAML; matches CAMPAIGN_010 / 011 / 012 / 013 verbatim) | within standing `RiskConfig` bounds |

**No sweep of any of these parameters.** Any deviation constitutes a
NEW candidate (must go through a fresh discovery sprint).

## 6. Event-fixture provenance (binding summary)

| dimension | value |
|---|---|
| fixture path | `research/calendar/fixtures/campaign_014_events.json` |
| schema_version | `campaign_014.event_fixture.v1` |
| coverage range | 2020-01-01 → 2026-05-20 (matches walk-forward universe) |
| total events | 281 |
| per-class counts | NFP 77, FOMC 51, ECB 51, BoJ 51, BoE 51 |
| forbidden fields | actual / actual_value / forecast / consensus / surprise / revision / revised_value / market_reaction / post_event_move / commentary — all rejected at load time |
| credentials used | **none** |
| broker endpoints touched | **none** |
| `.env` read | **none** |
| network fetch at runtime | **none** (loader reads local JSON only) |

## 7. No-lookahead checklist (binding; mirrors implementation spec §9)

| # | invariant |
|---|---|
| 1 | Strategy may only see events with `event_time_utc <= bar_t_minus_1_close_time` |
| 2 | Loader returns no future events from `eligible_events_at_or_before()` |
| 3 | Strategy uses only event-class label + `bars_since_event` — never `actual` / `forecast` / `surprise` / `revision` / `market_reaction` / `commentary` |
| 4 | Walk-forward harness rejects any fold whose test window extends beyond `coverage_end_utc` (BLOCKED verdict) |
| 5 | Fixture uses first-published timestamps only |
| 6 | H4 ATR is computed from completed bars only; `prior_atr_h4 = atr.iloc[-2]` |
| 7 | Strategy module performs no network I/O at signal time |
| 8 | All timestamps in fixture are UTC-aware; naive timestamps rejected at load time |

All 8 are enforced by tests; see
`tests/unit/test_calendar_event_window_anomaly.py`.

## 8. Event-window rule (binding R3)

At each H4 bar `t`:
1. Compute `bar_t_minus_1_close_time` (= `bar_t_open` since H4 bars
   are 4 hours wide).
2. Query `eligible_events_at_or_before(events, bar_t_minus_1_close_time, event_classes=event_set)`.
3. From the most-recent eligible event, find the bar whose
   `[open_time, open_time + 4h)` interval contains the event timestamp
   (= the "event bar").
4. Compute `bars_since_event = current_bar_pos - event_bar_pos`.
5. **Trigger only if `bars_since_event == 1`** (= the first post-event
   H4 bar; the trigger bar).
6. Confirm `ctx.instrument.name` is in `impacted_pairs(event.event_class)`.

## 9. Event-class precedence rule (binding R4)

If multiple events of different classes fall in the **same event bar**:

| precedence (high → low) | class |
|---|---|
| 0 | FOMC |
| 1 | NFP |
| 2 | ECB |
| 3 | BoJ |
| 4 | BoE |

The lower-index class wins. Determinism: precedence comparison uses
index in `impact_ordering`.

## 10. Turnover budget (binding; mirrors anti-pattern §4)

| dimension | binding pre-commit |
|---|---|
| event count per year | ~40–55 (NFP ≈ 12, FOMC ≈ 8, ECB ≈ 8, BoJ ≈ 8, BoE ≈ 8) |
| trade-eligible event-pair cells per year | (NFP × 7) + (FOMC × 7) + (ECB × 1) + (BoJ × 1) + (BoE × 1) = ~164 |
| qualification rate (R3 + R4 + R5 + R6 + R7) | ~50–80 % |
| **expected trades per year** | **~80–130** |
| **expected trades over 4-year walk-forward** | **~320–520** |
| **comparison to CAMPAIGN_011 null floor (1,177)** | ~3.5–7 × less |
| **comparison to CAMPAIGN_012 (3,726)** | ~7–12 × less |
| **comparison to CAMPAIGN_013 (7,940)** | ~15–25 × less |

### 10.1 Hard REJECT triggers (binding for future evidence sprint)

| trigger | threshold | classification |
|---|---|---|
| total trades > 800 over 4y | hard | **REJECT (turnover overshoot)** |
| total raw signals > 1,500 over 8 folds | hard | **REJECT (signal-density overshoot)** |
| any walk-forward fold's test window beyond fixture coverage | hard | **BLOCKED (event-fixture coverage)** |
| any of 8 inherited aggregate gates fails | hard | **REJECT (inherited gates)** |

## 11. Cost section (Pattern Q binding)

| component | assumption |
|---|---|
| per-trade spread (USD pairs) | ~0.5–2.0 bp |
| per-trade slippage | ~0.5–1.0 bp |
| per-trade financing (short hold ≤ 6 bars ≤ 1 day) | < 1 bp |
| **total per-trade cost** | **~1.5–4 bp** |
| **hypothesized per-trade gross expectancy** | **≥ 7 bp** |
| **expected per-trade net expectancy** | **≥ 5 bp** |
| **expected aggregate expectancy R** | **≥ 0.05 R** at upper trade-count budget; **≥ 0.10 R** at lower |

## 12. Null-baseline comparison requirement (binding)

Per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§8 + §9, the future evidence sprint's Phase 5 verdict doc MUST
include a side-by-side aggregate metrics table (CAMPAIGN_014 vs
CAMPAIGN_011), per-pair expectancy table, binary "meaningful
improvement over null?" verdict per metric, and explicit
indistinguishability-band check.

Meaningful-improvement margins (binding):

- aggregate expectancy R: **≥ +0.0524** (→ ≥ 0.05 R)
- aggregate profit factor: **≥ +0.19** (→ ≥ 1.10)
- aggregate return %: **≥ +5 pp** (vs CAMPAIGN_011 −0.53 %)
- pairs_positive: **≥ +1 pair** (→ ≥ 4 / 7)
- fold_pass_rate: **100 %**

Indistinguishability band (REJECT if within):
± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of CAMPAIGN_011.

## 13. Evidence sprint prerequisites (binding)

The future evidence sprint
`research-calendar-event-window-anomaly-walk-forward-001` MUST not
launch until:

1. Date-verification audit step against the 5 source URLs has been
   completed (per `CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md` §8 +
   `CAMPAIGN_014_WALK_FORWARD_READINESS.md` Phase 7).
2. The committed fixture, loader, strategy module, config schema,
   research config, and 93 unit tests are all in place (this Phase 4
   + 5 scaffold output).
3. The frozen parameters table (this §5) is treated as immutable by
   the runner's `_assert_frozen()` check.

## 14. Walk-forward requirements (binding)

Inherits CAMPAIGN_010 / 011 / 012 / 013 plan verbatim:

- 8 folds rolling/frozen
- 540 train / 180 validation / 180 test / 180 buffer days per fold
- Universe: 7-pair OANDA practice H4 (verbatim)
- Data window: 2020-01-01 → 2026-05-20
- Inherited per-fold + aggregate gates (8 + new turnover-budget +
  new signal-density + new fixture-coverage)

## 15. Financing overlay requirements (binding)

ESTIMATED + conservative-stress overlay required (per CAMPAIGN_010 /
011 / 012 / 013 pattern). MODELED refused at 4 layers; the overlay
script must abort if treatment is MODELED. Short hold (≤ 6 bars,
≤ 1 trading day) means financing is < 1 bp / trade — ESTIMATED +
conservative-stress is sufficient for research evidence.

## 16. Portfolio-risk diagnostic requirements (binding; CAMPAIGN_014-specific)

Standard battery from CAMPAIGN_010 / 011 / 012 / 013 plus:

- Event-class clustering (NFP / FOMC / ECB / BoJ / BoE PnL distribution)
- Per-event-class per-pair sensitivity (heatmap)
- Pre-event vs post-event direction breakdown
- Entry-window concentration

## 17. Independent verifier status (binding)

Capability-locked to CAMPAIGN_002 / `trend_following`. **NOT
REQUIRED for REJECT verdict.** Required only if CAMPAIGN_014 reaches
`RESEARCH_PASS_UNAPPROVED`, via separately-scoped sprint
`infra-free-local-parity-verifier-calendar-event-window-anomaly-001`.

## 18. Explicit no-approval statement (binding)

**A passing unit-test suite or smoke run is NOT strategy approval.**
**An evidence-sprint verdict of `RESEARCH_PASS_UNAPPROVED` is NOT
strategy approval.** Approval requires a deliberate human edit to
`configs/approved_strategies.yaml` per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md). Even
after the evidence sprint, paper / demo / live remain **blocked**
until that human edit.

## 19. Unexpected-PASS 5-step escalation protocol (binding)

If the future evidence sprint produces `RESEARCH_PASS_UNAPPROVED`:

1. **Re-verify all 8 inherited aggregate gates** + the new turnover-
   budget + signal-density + fixture-coverage gates pass at machine
   precision.
2. **Document the null-baseline comparison** vs CAMPAIGN_011 with
   explicit margins (per §12 above).
3. **Run the cost-section reconciliation** (per §11) — confirm actual
   per-trade cost ≤ 4 bp and net expectancy ≥ 5 bp.
4. **Recommend the verifier-extension sprint**
   `infra-free-local-parity-verifier-calendar-event-window-anomaly-001`
   as the next sprint.
5. **Do NOT modify `configs/approved_strategies.yaml`.** Only a
   deliberate human approval action can promote the strategy.

## 20. Safety state (unchanged after this pre-commit)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only (this pre-commit; no evidence verdict) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| broker call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |

## 21. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md`](CALENDAR_EVENT_WINDOW_ANOMALY_IMPLEMENTATION_SPEC.md) (binding spec)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md) (Phase 0 plan)
- [`CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md`](CAMPAIGN_014_EVENT_FIXTURE_PROVENANCE.md) (fixture provenance)
- [`CAMPAIGN_014_STATUS.md`](CAMPAIGN_014_STATUS.md) (scaffold-only status)
- [`CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md`](CALENDAR_EVENT_WINDOW_ANOMALY_READINESS.md) (readiness summary)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns R-W)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)
