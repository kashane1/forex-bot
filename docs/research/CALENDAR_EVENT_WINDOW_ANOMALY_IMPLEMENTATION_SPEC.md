# Calendar-Event Window Anomaly — Binding Implementation Spec

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 1 machine-facing implementation spec for **CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`** (the C7 candidate
selected by discovery-005). **Scaffold sprint only — no historical
backtest, no walk-forward evidence, no broker call.** This document
binds Phase 2–8 of this sprint and the future evidence sprint
`research-calendar-event-window-anomaly-walk-forward-001` against
parameter drift or signal-shape drift.

> No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. CAMPAIGN_002 / 010 / 011 / 012 / 013 remain REJECT
> and untouched. **A passing unit-test suite or smoke run is NOT
> strategy approval.**

## 1. Hypothesis (binding)

Around scheduled high-impact macroeconomic events (US NFP, US FOMC
rate decisions, ECB rate decisions, BoJ rate decisions, BoE rate
decisions), USD-pair returns exhibit a **mean-reverting overshoot**
in the H4 bars immediately after the event close. Specifically:

> *During the post-event window (H4 bars `[+1, +N]` after the H4 bar
> containing the event timestamp; N = `post_event_window_bars`), the
> directional move of the first post-event H4 bar (= the "trigger
> bar") is structurally more likely to be partially reversed in the
> subsequent `N − 1` bars than a randomly-selected sequence of H4
> bars on the same universe. Trade **against** the trigger bar's
> direction with an H4 ATR-2 stop and a max-hold of N bars; one
> entry per event-pair cell; no re-entry within `re_entry_block_bars`
> after an exit.*

This is a single-pair, single-leg, time-stop-only, ATR-stopped
counter-trend hypothesis **conditional on a public scheduled
calendar event**, not on a within-pair price statistic.

## 2. Universe (binding)

7-pair OANDA practice H4 universe, **identical to CAMPAIGN_010 /
011 / 012 / 013**:

```
EUR_USD · GBP_USD · USD_JPY · AUD_USD · USD_CAD · USD_CHF · NZD_USD
```

**No per-pair carve-out.** Universe is part of family identity per
`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §3.

Per-event-class **impacted-pairs mapping** (binding pre-declared
deterministic mapping):

| event class | impacted pairs |
|---|---|
| NFP (US Bureau of Labor Statistics monthly employment release) | all 7 (all are USD pairs) |
| FOMC (US Federal Reserve rate decision) | all 7 (all are USD pairs) |
| ECB (European Central Bank rate decision) | EUR_USD |
| BoJ (Bank of Japan MPM rate decision) | USD_JPY |
| BoE (Bank of England MPC rate decision) | GBP_USD |

This mapping is **immutable** for the evidence sprint and is
encoded as a module-level constant in
`src/forex_bot/strategies/calendar_event_window_anomaly.py`.

## 3. Timeframe (binding)

**H4** entry / exit. Calendar timestamps are minute-resolution
UTC. Events are mapped to the H4 bar whose `[open_time, close_time)`
half-open interval contains the event timestamp ("the event bar").
The strategy waits until the **completed** event bar before
evaluating any post-event signal. Entry occurs at the **first
post-event H4 bar close** (= "trigger bar"); the trade is held for
up to `max_post_event_bars` H4 bars or until an ATR stop / time
stop hits.

## 4. R1–R8 binding rule table

The strategy implementation must satisfy R1–R8 verbatim. Each rule
is exercised by ≥ 1 dedicated unit-test fixture (see §10).

| rule | description |
|---|---|
| **R1** Warm-up | The strategy maintains a warm-up cursor. Signals are emitted only once the strategy has seen `event_warmup_bars` (= 1) completed event of class C ∈ `event_set` AND `atr_lookback + 2` completed H4 bars for the active pair. |
| **R2** Event-fixture availability | The strategy receives the event-fixture object via `ctx.config["event_fixture"]` (preloaded by the future evidence runner) **or** loads it lazily from `ctx.config["event_calendar_path"]` (preferred for the scaffold smoke). Fail-closed if neither key is present or both keys are present with inconsistent values. The fixture must satisfy `validate_event_fixture()`. |
| **R3** Event-window proximity trigger | At each H4 bar `t`, the strategy queries `eligible_events_at_or_before(events, bar_t_minus_1_close_time)` to find the most recent **completed-bar** event matching the impacted-pairs mapping for `ctx.instrument.name`. If the bar offset between `t` and the event-bar's index is in `[1, post_event_window_bars]` AND the offset is exactly `1` (the trigger bar is the first post-event bar) → continue to R5; else → no signal. |
| **R4** Event-class precedence / overlap | If multiple events of different classes fall within the same H4 bar, the higher-impact class takes precedence per `impact_ordering = ["FOMC", "NFP", "ECB", "BoJ", "BoE"]`. The lower-impact event is treated as not having occurred *for that bar*. Determinism: precedence comparison uses the index of the class in `impact_ordering`; lower index = higher impact. |
| **R5** Signal direction | The Signal direction is **counter to the event-bar's directional move**. Define `event_bar_return = (close[event_bar] / open[event_bar]) − 1`. If `event_bar_return > 0` → `Side.SHORT` (fade the post-event rally). If `event_bar_return < 0` → `Side.LONG` (fade the post-event sell-off). If `event_bar_return == 0` exactly → no signal (degenerate / data quality issue). |
| **R6** H4 ATR fail-closed | The strategy uses **H4 ATR-14** (`atr_lookback = 14`) computed from completed bars only. `prior_atr_h4 = h4_atr_series.iloc[-2]`. Fail-closed if `prior_atr_h4` is `NaN`, non-finite, or `≤ 0`. |
| **R7** ATR stop placement | Stop = `last_close ± atr_stop_multiple × prior_atr_h4` (= 2.0 × ATR-14). `last_close` is read **only** for stop placement; the entry decision (R3 + R4 + R5) is fully determined by event-time + event-bar-return + impacted-pairs-mapping *before* `last_close` is consulted. Position is closed on the earlier of: stop-loss hit, or `max_post_event_bars` (= 6) H4 bars elapsed. |
| **R8** Deterministic Signal emission | Emit `Signal` with deterministic `signal_id` (SHA-1 of `strategy_name|version|instrument|timeframe|bar_iso|side|event_id`) and `exit_model="time_stop_only"`. Signal `features` include `event_class`, `event_id`, `event_time_utc`, `bars_since_event` (= 1 at trigger), `prior_atr_h4`, `last_close`, `event_bar_return`, the active `post_event_window_bars`. Signal `features` **must not** include `actual`, `forecast`, `surprise`, `revision`, `market_reaction`, or any other event-result field — these fields are forbidden in both the fixture and the Signal. |

## 5. Frozen parameters (binding pre-commit)

| parameter | value | rationale / bounds |
|---|---|---|
| `version` | `"0.1.0-c014"` | binding string |
| `timeframe` | `"H4"` | matches CAMPAIGN_010 / 011 / 012 / 013 |
| `event_calendar_path` | `"research/calendar/fixtures/campaign_014_events.json"` | committed text fixture; broker-free |
| `event_set` | `["NFP", "FOMC", "ECB", "BoJ", "BoE"]` | pre-declared; mid-sprint expansion forbidden |
| `impact_ordering` | `["FOMC", "NFP", "ECB", "BoJ", "BoE"]` | pre-declared precedence for overlap (R4); must be a permutation of `event_set` |
| `post_event_window_bars` | `6` | matches CAMPAIGN_010 / 011 / 012 / 013 max-hold envelope; within standing `[1, 30]` |
| `atr_lookback` | `14` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim; within standing `[8, 28]` |
| `atr_stop_multiple` | `2.0` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim; within standing `[1.0, 3.0]` |
| `max_post_event_bars` | `6` | maximum holding time (= `post_event_window_bars`) |
| `re_entry_block_bars` | `3` | new for C7; prevents same-event re-entry; ≥ 0 |
| `event_warmup_bars` | `1` | strategy must see at least 1 completed event before signaling (per R1); ≥ 0 |
| `risk_per_trade_pct` | `0.005` (= 0.5 %) | matches CAMPAIGN_010 / 011 / 012 / 013; set in `RiskConfig`, not the strategy config |
| `initial_equity_per_pair` | `500` (USD) | matches CAMPAIGN_010 / 011 / 012 / 013; set in `RiskConfig.starting_equity_usd` |
| `trailing_stop_atr_multiple` | `null` | v1 uses time-stop only; validator rejects non-null |
| `min_atr_pips` | `{}` (empty dict) | no per-pair floor in v1; matches CAMPAIGN_010 / 011 / 012 / 013 |

**No sweep of any of these parameters.** The pre-commit checklist
(`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`, Phase 5) freezes them
before the strategy module is written; the strategy's
`generate_signal()` reads them directly from `ctx.config`; the
future evidence-sprint runner's `_assert_frozen()` pattern (mirrors
CAMPAIGN_010 / 011 / 012 / 013 runners) blocks parameter drift.

## 6. Turnover-budget pre-commit (Phase 2 anti-pattern §4 binding)

| dimension | binding pre-commit |
|---|---|
| event count per year (binding event set) | ~40–55 events (NFP ≈ 12, FOMC ≈ 8, ECB ≈ 8, BoJ ≈ 8, BoE ≈ 8; some overlap days reduce union) |
| trade-eligible event-pair cells per year | (NFP × 7 pairs) + (FOMC × 7 pairs) + (ECB × 1 pair) + (BoJ × 1 pair) + (BoE × 1 pair) ≈ ~164 cells/year |
| qualification rate (R3 + R4 + R5 + R6 + R7) | ~50–80 % of cells |
| **expected trades per year** | **~80–130** |
| **expected trades over 4-year walk-forward** | **~320–520** |
| **comparison to CAMPAIGN_011 null floor** | well below 1,177 (~3.5–7 × less) |
| **comparison to CAMPAIGN_012** | ~7–12 × less than 3,726 |
| **comparison to CAMPAIGN_013** | ~15–25 × less than 7,940 |

### 6.1 Hard REJECT triggers (binding for the future evidence sprint)

| trigger | threshold | classification |
|---|---|---|
| total trades > 800 over 4-year walk-forward | hard | **REJECT (turnover overshoot)** |
| total raw signals > 1,500 over 8 folds | hard | **REJECT (signal-density overshoot)** |
| any walk-forward fold's test window extends beyond event-fixture coverage | hard | **BLOCKED (event-fixture coverage)** |
| any of 8 inherited aggregate gates fails | hard | **REJECT (inherited gates)** |

### 6.2 Cost section (Pattern Q binding)

| component | pre-committed assumption |
|---|---|
| per-trade spread (USD pairs) | ~0.5–2.0 bp (from `FillModel` per-pair spread table) |
| per-trade slippage | ~0.5–1.0 bp (from `FillModel`) |
| per-trade financing (short hold ≤ 6 bars ≤ 1 trading day) | < 1 bp |
| **total per-trade cost** | **~1.5–4 bp** |
| **hypothesized per-trade gross expectancy** | **≥ 7 bp** |
| **expected per-trade net expectancy** | **≥ 5 bp** |
| **expected aggregate expectancy R** | **≥ 0.05 R** at the upper trade-count budget; **≥ 0.10 R** at the lower |

If the gross-expectancy hypothesis fails empirically in walk-forward,
the candidate **rejects honestly** per the inherited gates — the
cost section is a *commitment to the hypothesis*, not gate
manipulation.

## 7. Event-fixture schema (binding)

The committed fixture file
`research/calendar/fixtures/campaign_014_events.json` must be a JSON
document with the following top-level schema:

```json
{
  "schema_version": "campaign_014.event_fixture.v1",
  "coverage_start_utc": "2020-01-01T00:00:00+00:00",
  "coverage_end_utc": "2026-05-20T23:59:59+00:00",
  "event_classes": ["NFP", "FOMC", "ECB", "BoJ", "BoE"],
  "source_attribution": {
    "NFP": {"name": "US Bureau of Labor Statistics — Employment Situation", "url": "https://www.bls.gov/schedule/news_release/empsit.htm"},
    "FOMC": {"name": "US Federal Reserve — FOMC Meeting Calendar", "url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"},
    "ECB": {"name": "European Central Bank — Monetary Policy Decisions", "url": "https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html"},
    "BoJ": {"name": "Bank of Japan — Monetary Policy Meetings", "url": "https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm"},
    "BoE": {"name": "Bank of England — MPC Calendar", "url": "https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates"}
  },
  "events": [
    {
      "event_id": "NFP_2020-01-10",
      "event_class": "NFP",
      "event_time_utc": "2020-01-10T13:30:00+00:00"
    },
    {
      "event_id": "FOMC_2020-01-29",
      "event_class": "FOMC",
      "event_time_utc": "2020-01-29T19:00:00+00:00"
    }
    // ... ~250-350 events over 2020-01-01 → 2026-05-20
  ]
}
```

### 7.1 Per-event allowed fields (binding allow-list)

| field | type | required | notes |
|---|---|:---:|---|
| `event_id` | string | ✓ | unique; pattern `^{event_class}_{YYYY-MM-DD}$` (or `^{event_class}_{YYYY-MM-DD}_{N}$` for rare same-day repeats) |
| `event_class` | string | ✓ | one of `event_set` |
| `event_time_utc` | string (ISO-8601 UTC) | ✓ | timezone-aware UTC; minute resolution |

### 7.2 Per-event explicitly FORBIDDEN fields (binding deny-list)

The fixture loader **must reject** any event containing any of:

| forbidden field | rationale |
|---|---|
| `actual` | leakage of post-event result |
| `actual_value` | leakage of post-event result |
| `forecast` | leakage of consensus expectation (potentially future-knowable) |
| `consensus` | leakage of consensus |
| `surprise` | leakage of (actual − forecast) |
| `revision` | leakage of post-event revision |
| `revised_value` | leakage of post-event revision |
| `market_reaction` | leakage of post-event price move |
| `post_event_move` | leakage of post-event price move |
| `commentary` | leakage of post-event narrative |

Detection is field-name-based (case-insensitive substring match
against the deny-list); the loader raises on any match. This is a
**no-lookahead rail** enforced by the loader, not by the strategy.

### 7.3 Provenance / sourcing rules

- All `source_url` values must be **public official URLs** (BLS,
  FOMC.gov, ECB.europa.eu, BoJ.or.jp, BoE.co.uk).
- **No broker URLs.** No `*.oanda.com`, no `*.fxcm.com`, no
  `*.interactivebrokers.com`, no any-broker.
- **No paid-API URLs.** No `forexfactory.com/api`, no `tradingeconomics.com/api`, no `econoday`, no `bloomberg`, no `refinitiv`.
- **No credentials** in any URL or field.
- **No scraped page content** committed; only the date+class+time triple per event.

## 8. Event classes (binding)

| class | full name | typical UTC time | impacted pairs |
|---|---|---|---|
| NFP | US Bureau of Labor Statistics — Employment Situation (Nonfarm Payrolls) | 13:30 (12:30 in DST) — first Friday of month | all 7 |
| FOMC | US Federal Reserve — FOMC rate decision | varies (typically 18:00–19:00) — 8/year per published calendar | all 7 |
| ECB | European Central Bank — Monetary Policy rate decision | typically 12:15 — ~8/year | EUR_USD only |
| BoJ | Bank of Japan — Monetary Policy Meeting rate decision | varies — ~8/year | USD_JPY only |
| BoE | Bank of England — MPC rate decision | typically 11:00 — ~8/year | GBP_USD only |

Mid-sprint event-list expansion is **forbidden** (Phase 7 design
§5; the pre-commit checklist freezes the event set).

## 9. No-lookahead safeguards (binding)

The scaffold sprint must enforce the following invariants (≥ 5
new ones for calendar access, plus the standard H4 close-only
invariants):

1. **Event-time ≤ bar-complete-time.** The strategy may only see
   events whose `event_time_utc <= bar_t_minus_1_close_time` where
   `bar_t_minus_1` is the most recently completed H4 bar at the
   time of signal evaluation.
2. **Loader exposes no future events.** `eligible_events_at_or_before(events, cutoff)` returns only events with `event_time_utc <= cutoff`.
3. **No surprise / consensus / actual / revision.** The strategy uses only the event-class label + `bars_since_event` offset; never `actual`, `forecast`, `consensus`, `surprise`, `revision`, `market_reaction`, `commentary`.
4. **Walk-forward fold-coverage check.** The future evidence-sprint harness rejects any fold whose test window extends beyond `coverage_end_utc`; if any fold is uncovered → BLOCKED verdict (not silent partial coverage).
5. **First-published-only values.** The fixture must contain only the **first-published** event timestamp; if an event is later rescheduled and a revised timestamp is published, the fixture must still use the original first-published timestamp (or document the revision explicitly with a `provenance_note` field — TODO Phase 1b).
6. **Closed-bar-only ATR.** Standard from CAMPAIGN_010 / 011 / 012 / 013: `atr` is computed from `completed_only()` H4 bars; `prior_atr_h4 = h4_atr_series.iloc[-2]` (one bar back from current, for `[t-1]` invariance).
7. **No real-time data fetch at strategy runtime.** The loader reads the fixture once at construction or at the first `generate_signal()` call; subsequent calls reuse the cached fixture. **The strategy module never opens a network connection.**
8. **UTC normalization.** All timestamps in the fixture are UTC-aware (`tzinfo=timezone.utc`); naive timestamps are rejected at load time.

## 10. Fail-closed rules (binding)

The strategy emits **no signal** under any of the following conditions
(each exercised by ≥ 1 unit test):

| condition | description |
|---|---|
| FC-1 | `event_calendar_path` missing or unreadable (loader fails fast at construction; strategy fails-closed at signal time) |
| FC-2 | fixture schema invalid (missing `schema_version`, malformed `events`, etc.) |
| FC-3 | event time not UTC (`tzinfo` not `timezone.utc`) |
| FC-4 | unsupported event class in fixture (not in `event_set`) |
| FC-5 | fixture contains any forbidden field (per §7.2) |
| FC-6 | fixture coverage insufficient for the current bar time (`bar_t_close > coverage_end_utc`) — strictly speaking, this is checked by the walk-forward harness; the strategy itself just returns no signal if no eligible event exists |
| FC-7 | no eligible event in the trigger window for `(ctx.instrument, bar_t_minus_1_close)` |
| FC-8 | event-bar's `open` or `close` is non-finite or `≤ 0` |
| FC-9 | `event_bar_return == 0.0` exactly (degenerate / data quality) |
| FC-10 | H4 ATR-14 is non-finite or ≤ 0 at `[t-2]` |
| FC-11 | A position is already open for this instrument |
| FC-12 | Re-entry block active (last exit on this instrument was < `re_entry_block_bars` H4 bars ago) — the strategy state for "last exit time" is implicit via `ctx.open_positions` + recent closures; the scaffold relies on the engine's `max_positions_per_instrument = 1` + the time stop to enforce the spirit; explicit re-entry-block enforcement requires runner-level state which is **deferred to the future evidence sprint** with a `# TODO: re-entry-block` marker in the strategy module |
| FC-13 | Warm-up not satisfied (`len(df) < atr_lookback + 2` or no completed events seen yet) |
| FC-14 | `ctx.instrument.name` not in `impacted_pairs(event_class)` for the most recent eligible event |

**Note on FC-12:** The discovery-005 design §7 specifies a 3-bar
re-entry block. In the scaffold sprint, the engine's per-pair
`max_positions_per_instrument = 1` + time-stop at 6 bars
collectively enforces the spirit (one position at a time per pair;
the block kicks in implicitly while a position is held). Explicit
per-bar-elapsed-since-exit re-entry tracking requires runner-level
state and is documented as a future-evidence-runner deliverable.
The scaffold's strategy module includes the `re_entry_block_bars`
parameter, validates it (must be `≥ 0`), and emits the value in
Signal features for the runner to consume.

## 11. Expected unit tests (Phase 4)

≥ 50 deterministic tests. Categories (with target counts):

| category | target tests |
|---|---|
| Config defaults + validation + `extra="forbid"` | 9 |
| Event-fixture schema validation (loader-positive + loader-negative) | 12 |
| Eligible-event helper (no future events; deterministic ordering; precedence) | 6 |
| R1–R8 happy path + fail-closed | 10 |
| Counter-direction signal logic (positive / negative / zero event-bar return) | 3 |
| Signal determinism + ID stability | 2 |
| Anti-contamination source-grep (no broker / execution / loops imports; no PRNG; no CAMPAIGN_*-specific keys) | 8 |
| Approval-registry / paper / demo config regression | 3 |
| Fixture path / coverage / no-credentials | 3 |
| **total** | **~56** |

Implementation may add more if natural; the floor is ≥ 50.

## 12. Turnover/cost budget expectations for future evidence

These are **not enforced in the scaffold sprint** but are binding
pre-commits for the future evidence sprint
`research-calendar-event-window-anomaly-walk-forward-001`:

- See §6.1 for hard REJECT triggers (800 trades; 1,500 signals).
- See §6.2 for cost-section reconciliation.
- The future evidence sprint's Phase 5 verdict doc MUST include
  the turnover-budget evaluation table, the signal-density
  evaluation table, the cost-section reconciliation, the event-
  fixture coverage report, and the null-baseline comparison
  (CAMPAIGN_014 vs CAMPAIGN_011).

## 13. Safety state (unchanged after this scaffold sprint)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only after this sprint; **no evidence verdict yet** |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 → ≥ 925 target after Phase 4 |
| ruff baseline | 3 pre-existing (unchanged) |

## 14. Cross-links

- [`CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md`](CALENDAR_EVENT_WINDOW_ANOMALY_001_PLAN.md) (Phase 0)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) (binding design from discovery-005)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (C7 selection)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) (this sprint's prompt template)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) (binding cooldown)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover guardrail)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
