# Next Preferred Candidate — Implementation Design (Phase 7)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 7 binding implementation + evaluation design for the
**C7 — Calendar-Event Window Anomaly (CEWA)** candidate selected
in [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md).
**No implementation; no backtest; no broker call.** This doc binds
the future scaffold sprint (`research-calendar-event-window-anomaly-
001`) and the future evidence sprint (`research-calendar-event-window-
anomaly-walk-forward-001`).

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 all
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **A scaffold or evidence sprint cannot approve any
> strategy** — only a deliberate human approval action per
> `STRATEGY_APPROVAL_PROCESS.md` can.

## 1. Strategy hypothesis (binding)

Around scheduled high-impact macroeconomic events (US NFP, US FOMC
rate decisions, ECB rate decisions, BoJ rate decisions, BoE rate
decisions), USD-pair returns exhibit a **mean-reverting overshoot**
in the H4 bars immediately after the event close. The hypothesis is:

> *During the post-event window (H4 bars [+1, +N] after the bar
> containing the event timestamp), the directional move of the
> first post-event H4 bar is structurally more likely to be partially
> reversed in the subsequent N−1 bars than a randomly-selected
> sequence of H4 bars. Trade against the first post-event bar's
> direction with an ATR stop and a max-hold of N bars.*

This hypothesis is **economically grounded** in the FX literature
on event-driven overshoot (e.g. post-NFP / post-FOMC immediate
moves carry surprise-flow that is partially mis-priced and reverts
within hours).

## 2. Universe (binding)

**Same 7-pair OANDA practice H4 universe as CAMPAIGN_010 / 011 /
012 / 013:**

`EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`, `USD_CAD`, `USD_CHF`,
`NZD_USD`.

No per-pair carve-out. Universe is part of family identity (per
`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §3); no pair drops based on
prior campaigns' results.

Each event class has a **pre-declared subset of impacted pairs**
(deterministic mapping):

| event class | impacted pairs |
|---|---|
| NFP (US Bureau of Labor Statistics) | all 7 (all are USD pairs) |
| FOMC (US Federal Reserve) rate decision | all 7 (all are USD pairs) |
| ECB rate decision | EUR_USD only |
| BoJ rate decision | USD_JPY only |
| BoE rate decision | GBP_USD only |

This mapping is **pre-declared in the scaffold sprint's pre-commit
checklist** and is immutable for the evidence sprint.

## 3. Timeframe (binding)

**H4** entry / exit; calendar timestamps are minute-resolution.

Event timestamps map to the H4 bar containing them (the
"event bar"), and the strategy waits until the **completed** event
bar before evaluating any post-event signal. Entry occurs at the
**first post-event H4 bar close** (= "trigger bar"); the trade is
held for up to N H4 bars or until ATR stop / time stop hits.

## 4. Data requirements (binding)

### 4.1 Existing data

7-pair H4 OANDA-practice store at `data/campaign_002.sqlite3`
(gitignored; provenance per `CAMPAIGN_010_DATA_PROVENANCE.md`).
**No new fetch; no broker call.**

### 4.2 NEW data primitive — calendar fixture

A new committed fixture file:

`research/event_calendar/event_calendar_2020_2026.json`
(or equivalent; the scaffold sprint will pick the exact path/format).

| field | binding requirement |
|---|---|
| size | ≤ 50 KB |
| format | JSON (preferred) or CSV; deterministic schema documented in the loader's docstring |
| event timestamps | UTC; minute resolution |
| event coverage | 2020-01-01 → 2026-05-20 (CAMPAIGN_010 / 011 / 012 / 013's data window verbatim) |
| event classes (binding pre-commit) | NFP (monthly), FOMC (≈ 8/year), ECB (≈ 8/year), BoJ (≈ 8/year), BoE (≈ 8/year) — ~40–55 events/year |
| event sources | public government / central-bank URLs only — BLS for NFP, FOMC.gov for FOMC, ECB.europa.eu for ECB, BoJ.or.jp for BoJ, BoE.co.uk for BoE |
| compilation | one-time deterministic script (`scripts/compile_event_calendar.py`); audited; reproducible from public sources |
| broker dependency | **none** |
| `.env` dependency | **none** |
| credentials | **none** |

The fixture is **committed text** that any future Claude instance
(or human reviewer) can audit; the compilation script's source-
URL list is committed alongside.

### 4.3 No-lookahead invariants for calendar access (binding; NEW for harness)

The scaffold sprint must enforce **at least 5** new no-lookahead
invariants for event-time access:

1. The strategy may only see `event_time <= bar_complete_time` for
   any `bar_complete_time` it is currently evaluating.
2. The event fixture loader must NOT expose any field that depends
   on future events (no "next FOMC date", no "days until next NFP").
3. The strategy's signal computation may use the event-class label
   (e.g. "FOMC") of the most recent completed-bar event and the
   bar offset since that event, but NOT the surprise value, NOT
   the consensus expectation, NOT any post-event commentary or
   subsequent revisions.
4. The walk-forward harness must verify that the event fixture
   covers the entire test window for every fold (a fold is invalid
   if its test window extends beyond the fixture's coverage).
5. The strategy must NOT use any event field that was revised after
   the original event timestamp (e.g. NFP revisions in subsequent
   months); only the **first published** value at the original
   event time may be used.

## 5. Signal rules (R1–R8 binding rule table)

The scaffold sprint will encode these as docstring tags `R1` … `R8`
on the strategy module and exercise each via dedicated unit-test
fixtures.

| rule | description |
|---|---|
| **R1** | The strategy maintains a warm-up cursor over the event fixture; signals are emitted only after the strategy has seen at least one completed event bar matching one of the binding event classes |
| **R2** | At each H4 bar `t`, the strategy checks: "did the bar `t-1` (the most recently *completed* bar) contain an event of class C ∈ binding_event_classes affecting pair P ∈ impacted_pairs(C)?". If YES, bar `t` is a **trigger bar**; the strategy emits a Signal at bar `t`'s close |
| **R3** | The Signal **direction** is: `Side.SHORT` if the event bar's return `(close_event_bar / open_event_bar) − 1` is positive (i.e. fade the post-event rally); `Side.LONG` if the event bar's return is negative (i.e. fade the post-event sell-off). **Counter to the event bar's direction.** |
| **R4** | If multiple events overlap (e.g. ECB on the same day as FOMC), the **higher-impact** event (per a pre-declared impact ordering: FOMC > NFP > ECB > BoJ > BoE) takes precedence; the lower-impact event is treated as not having occurred for that bar |
| **R5** | The strategy uses **H4 ATR-14** (computed from completed bars only) for stop placement. The stop is placed at `entry_price ± atr_stop_multiple × ATR_14`. The `atr_stop_multiple` is pre-committed at **2.0** (within the standing `[1.0, 3.0]` range per `REJECTED_FAMILY_OVERFIT_GUARDRAILS.md` §4); no sweep |
| **R6** | **Max-hold time stop** at `max_post_event_bars` H4 bars after the trigger bar; pre-committed at **6** (within the standing `[1, 30]` range; matches CAMPAIGN_010 / 011 / 012 / 013's `max_bars_in_trade = 6` envelope) |
| **R7** | **Re-entry block** of `re_entry_block_bars` after any exit (stop, time stop, or opposite-event override); pre-committed at **3** H4 bars. No second entry on the same event window |
| **R8** | **Fail-closed missing-data**: if any required input (event fixture coverage, H4 close, H4 ATR-14, or the event bar's open/close) is missing or non-finite for the trigger evaluation, the strategy emits NO signal for that bar; the runner logs the fail-closed reason |

## 6. Exit rules (binding)

- **ATR stop** (per R5).
- **Max-hold time stop** at `max_post_event_bars` H4 bars (per R6).
- **No trailing stop in v1** (per base guardrails §4: "trailing stop
  opt-in v1 = none").
- **No partial exits in v1.**
- **No exit-on-opposite-event** (the re-entry block per R7 handles
  the cross-event case).

## 7. Frozen parameter set (binding pre-commit)

| parameter | value | rationale |
|---|---|---|
| `event_set` | `["NFP", "FOMC", "ECB", "BoJ", "BoE"]` | pre-declared event classes; no expansion or contraction mid-sprint |
| `impact_ordering` | `["FOMC", "NFP", "ECB", "BoJ", "BoE"]` | pre-declared precedence for overlap (per R4) |
| `post_event_window_bars` | `6` | matches CAMPAIGN_010 / 011 / 012 / 013's holding-period envelope (within standing `[1, 30]` range) |
| `atr_lookback` | `14` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim (within standing `[8, 28]` range) |
| `atr_stop_multiple` | `2.0` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim (within standing `[1.0, 3.0]` range) |
| `max_post_event_bars` | `6` | matches max-hold per R6 |
| `re_entry_block_bars` | `3` | new for C7; pre-declared to prevent same-event re-entry |
| `risk_per_trade_pct` | `0.005` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim |
| `initial_equity_per_pair` | `500` | matches CAMPAIGN_010 / 011 / 012 / 013 verbatim |
| `event_warmup_bars` | `1` | strategy must see at least 1 completed event before signaling (per R1) |

**No sweep of any of these parameters.** The pre-commit checklist
freezes them before the strategy module is written; the runner
asserts the loaded YAML config matches the pre-commit verbatim
(`_assert_frozen()` pattern from CAMPAIGN_010 / 011 / 012 / 013
runners).

## 8. Expected turnover budget (binding pre-commit per Phase 2 §4.1)

| dimension | binding pre-commit |
|---|---|
| event count per year | ~40–55 (NFP ~12, FOMC ~8, ECB ~8, BoJ ~8, BoE ~8; some overlap days reduce the union count) |
| trade-eligible event-pair cells per year | (NFP × 7 pairs) + (FOMC × 7 pairs) + (ECB × 1 pair) + (BoJ × 1 pair) + (BoE × 1 pair) = ~84 + ~56 + ~8 + ~8 + ~8 = ~164 cells/year |
| qualification rate (R8 + non-overlap + R7 re-entry block) | ~50–80 % of cells |
| **expected trades per year** | **~80–130** |
| **expected trades over 4-year walk-forward** | **~320–520** |
| **comparison to CAMPAIGN_011 null** | well below 1,177 (the null floor); ~3.5–7 × less than CAMPAIGN_011 |
| **comparison to CAMPAIGN_012** | ~7–12 × less than CAMPAIGN_012 (3,726) |
| **comparison to CAMPAIGN_013** | ~15–25 × less than CAMPAIGN_013 (7,940) |
| **comparison to CAMPAIGN_010** | similar order to CAMPAIGN_010 (2,791); slightly less |

**Pre-committed REJECT trigger:** if the actual trade count exceeds
**800 trades** over the 4-year walk-forward, the evidence sprint
must classify the candidate as **REJECT (turnover overshoot)** in
addition to the inherited gate verdict, regardless of whether the
inherited gates pass. This is the Phase 2 §4.3 binding rule.

## 9. Raw signal rate expectation (binding)

| dimension | pre-committed expectation |
|---|---|
| signal density (per pair per fold's ~180-day test window) | ~10–25 signals |
| signal density (aggregate; per fold; all pairs) | ~50–100 signals |
| signal density (aggregate; 8 folds) | ~400–800 signals (note: signals are not necessarily trades; fail-closed conditions, re-entry block, and risk-engine spread filter can drop signals to trades by ~10–20 %) |

If raw signal density exceeds **1,500 signals over 8 folds**, the
evidence sprint must classify the candidate as **REJECT (signal
density overshoot)**.

## 10. Risk sizing (binding)

- Fixed `risk_per_trade_pct = 0.005` (0.5 % per trade; matches
  CAMPAIGN_010 / 011 / 012 / 013 verbatim).
- Position size = `(equity × risk_per_trade_pct) / (ATR × stop_multiple)`
  (matches existing RiskEngine path).
- **No portfolio-wide max-position cap relaxation.** The per-pair
  `max_open_positions = 1` cap applies; per-pair runner architecture
  is unchanged from CAMPAIGN_010 / 011 / 012 / 013.

## 11. Spread / slippage / financing handling (Pattern Q binding)

The strategy module's docstring MUST include a section "Cost section"
that pre-declares:

| component | pre-committed value |
|---|---|
| per-trade spread (assumed, USD pairs) | ~0.5–2.0 bp (from existing `FillModel` per-pair spread table) |
| per-trade slippage | ~0.5–1.0 bp (from existing `FillModel`) |
| per-trade financing (short hold ≤ 6 bars; ≤ 1 trading day typically) | < 1 bp |
| **total per-trade cost** | **~1.5–4 bp** |
| **expected per-trade gross expectancy (hypothesis)** | **≥ 7 bp** (so net ≥ ~3 bp ⇒ aggregate-R ≥ 0.05 R / 6 ≈ 0.008 R per bar held, easily clearing the 0.05 R gate at ~80–500 trades) |
| **expected net expectancy per trade** | **≥ 5 bp net of all costs** |
| **expected aggregate expectancy R** | **≥ 0.05 R** at the upper trade-count budget; **≥ 0.10 R** at the lower trade-count budget |

If the gross expectancy hypothesis (~7 bp per trade) fails empirically
in walk-forward, the candidate **rejects honestly** per the inherited
gates — the cost section is a *commitment to the hypothesis*, not a
gate manipulation.

## 12. Required indicators / features

- H4 close-to-close return (computed from completed bars).
- H4 ATR-14 (computed from completed bars).
- Event-fixture lookup: "did the most-recently-completed H4 bar
  contain an event of class C affecting pair P?"

**That's it.** No EMA, no Donchian, no Z-score, no Bollinger, no
cross-pair rank, no vol percentile, no regime classifier. C7 is
mechanistically minimal.

## 13. Config schema needs

A new `CalendarEventWindowAnomalyStrategyConfig` class in
`src/forex_bot/config.py`:

```python
class CalendarEventWindowAnomalyStrategyConfig(BaseModel):
    """Frozen config for the C7 candidate (CAMPAIGN_014)."""
    model_config = ConfigDict(extra="forbid")

    event_calendar_path: str  # path to the committed fixture
    event_set: list[str]  # binding: ["NFP", "FOMC", "ECB", "BoJ", "BoE"]
    impact_ordering: list[str]  # binding precedence for overlap
    post_event_window_bars: int = 6
    atr_lookback: int = 14
    atr_stop_multiple: float = 2.0
    max_post_event_bars: int = 6
    re_entry_block_bars: int = 3
    event_warmup_bars: int = 1

    @model_validator(mode="after")
    def _validate(self):
        # frozen-set / bounds checks; rejects unknown event classes,
        # bad bounds, mismatched impact-ordering length
        ...
```

Plus an `enabled` slot in the global `StrategyConfig` (alongside
`trend_following`, `session_breakout`, etc.).

## 14. Strategy module location

`src/forex_bot/strategies/calendar_event_window_anomaly.py`

Plus an event-fixture loader (small, dedicated module):

`src/forex_bot/strategies/event_calendar.py` (or equivalent;
scaffold sprint will pick).

## 15. Tests required (≥ 30, binding)

The scaffold sprint must add **at least 30 new unit tests**, covering:

1. Config validation: `extra="forbid"`, bounds, type errors.
2. Frozen event_set check; rejects unknown event classes.
3. Frozen impact_ordering length match.
4. Happy path: a synthetic-fixture event triggers a Signal with the
   correct direction.
5. Counter-direction signal: positive event-bar return → Side.SHORT.
6. Counter-direction signal: negative event-bar return → Side.LONG.
7. Fail-closed: missing ATR → no signal.
8. Fail-closed: missing event-fixture coverage → no signal.
9. Fail-closed: non-finite event-bar return → no signal.
10. Event overlap: FOMC + ECB on same day → FOMC takes precedence.
11. Event overlap: NFP + ECB on same day → NFP takes precedence.
12. Re-entry block: second signal in `re_entry_block_bars` after
    exit is suppressed.
13. Max-hold time stop fires at exactly `max_post_event_bars`.
14. ATR stop fires at `entry ± atr_stop_multiple × ATR_14`.
15. **No-lookahead invariant 1**: strategy cannot see `event_time
    > bar_complete_time`.
16. **No-lookahead invariant 2**: event-fixture loader does not
    expose future events.
17. **No-lookahead invariant 3**: strategy uses only event-class
    label + bar offset, never surprise / consensus / revision.
18. **No-lookahead invariant 4**: walk-forward harness rejects a
    fold whose test window extends beyond fixture coverage.
19. **No-lookahead invariant 5**: strategy uses only first-
    published event values, never revisions.
20. Event-fixture loader: deterministic JSON / CSV parse.
21. Event-fixture loader: rejects unknown event class.
22. Event-fixture loader: rejects malformed timestamps.
23. Event-fixture loader: handles UTC ↔ pair-instrument timezone
    correctly (no off-by-N-hour bugs).
24. Per-event-class impacted-pairs mapping correct (NFP → 7,
    FOMC → 7, ECB → 1 EUR_USD, BoJ → 1 USD_JPY, BoE → 1 GBP_USD).
25. Warmup: no signal before first completed event.
26. Forbidden-import contamination check: strategy module does not
    import `cross_pair_currency_strength_rotation`, `regime_switcher_
    atr_percentile`, `session_breakout`, `random_entry_anchor`,
    `trend_following`, `pullback_continuation`, `mean_reversion`,
    `volatility_breakout`.
27. Approval-registry regression: adding `calendar_event_window_
    anomaly` to a paper-loop config still REFUSES per the empty
    `approved_strategies.yaml`.
28. Determinism: identical fixture + identical price stream →
    identical signal stream.
29. Multi-pair per-event-class: NFP triggers a signal on every
    USD pair, but only the per-pair runner's spread-filter / re-
    entry-block deduplicates.
30. Pre-event-bar handling: the strategy emits no signal at the
    *event* bar's close; the trigger is the *first post-event* bar.

(The scaffold sprint may add more; ≥ 30 is the floor.)

## 16. Walk-forward requirements

Inherits CAMPAIGN_010 / 011 / 012 / 013 plan verbatim:

- 8 folds rolling/frozen.
- 540 train / 180 validation / 180 test / 180 buffer days per fold.
- Universe: 7-pair OANDA practice H4 (verbatim).
- Data window: 2020-01-01 → 2026-05-20 (verbatim).
- Inherited per-fold gates: expectancy_R ≥ 0.05, profit_factor ≥ 1.10,
  trades ≥ 30, pairs_positive ≥ 4/7, single_pair_dominance ≤ 60 %.
- Inherited aggregate gates: fold_pass_rate = 100 %, fold_count ≥ 6,
  expectancy_R ≥ 0.05, profit_factor ≥ 1.10, trade_count ≥ 200,
  pairs_positive ≥ 4/7, single_fold_dominance ≤ 60 %,
  single_pair_dominance ≤ 40 %.
- **New gate (Phase 2 binding):** turnover-budget rejection if total
  trades > 800.

## 17. Null-baseline comparison requirements

Per `CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md` §8:

- Side-by-side aggregate metrics: CAMPAIGN_014 vs CAMPAIGN_011.
- Side-by-side per-pair expectancy: CAMPAIGN_014 vs CAMPAIGN_011.
- Binary "meaningful improvement over null?" verdict for each of the
  six metrics in CAMPAIGN_011's §3.
- Explicit statement of indistinguishability under
  ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair band.

## 18. Turnover-amplification guardrail (Phase 2 binding pre-commit)

Per `TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md` §4:

- Expected trade-count range pre-declared (§8 above: ~320–520 trades
  over 4 years).
- Derivation documented (§8).
- Comparison to CAMPAIGN_011 / 012 / 013 explicit (§8).
- Pre-declared REJECT trigger if actual count > 800 (§8).
- No `max_open_positions` relaxation; no risk-limit relaxation; no
  pair carve-out (§10).
- Cost section per Pattern Q (§11).

## 19. Financing requirements

- ESTIMATED + conservative-stress overlay required (per CAMPAIGN_010 /
  011 / 012 / 013 pattern).
- MODELED refused; MODELED unavailability does **not** block C7's
  research-evidence sprint (short hold ⇒ financing is < 1 bp / trade
  ⇒ ESTIMATED + conservative-stress is sufficient for research
  evidence; live promotion would still require MODELED unblock).
- Financing overlay must report cashflow_home_total + cashflow_home_
  stress_total + per-pair sensitivity + flip events (matches
  CAMPAIGN_010 / 011 / 012 / 013 report shape).

## 20. Portfolio-risk diagnostics requirements

Standard battery from CAMPAIGN_010 / 011 / 012 / 013 plus C7-specific:

| diagnostic | required |
|---|---|
| 8 sanity checks (CAMPAIGN_010 baseline) | YES |
| Per-pair exposure | YES |
| Per-fold long/short imbalance | YES |
| Per-pair max loss / win streak | YES |
| **Event-class clustering** | **YES (new for C7)** — per event class (NFP/FOMC/ECB/BoJ/BoE) PnL distribution + trade-count breakdown |
| **Per-event-class per-pair sensitivity** | **YES (new for C7)** — heatmap of event class × pair PnL |
| **Pre-event vs post-event direction breakdown** | **YES (new for C7)** — whether the signal direction (counter-trend) is balanced across event classes |
| **Entry-window concentration** | **YES (new for C7)** — fraction of trades that occur within K H4 bars of any event |
| Spread filter rejections | YES (existing) |
| MAX_OPEN_POSITIONS_EXCEEDED count | YES (existing; CAMPAIGN_013 surfaced this as architecturally 0 for per-pair runner) |

## 21. Independent-verifier expectations

| dimension | value |
|---|---|
| verifier capability today | locked to CAMPAIGN_002 (`trend_following`) |
| C7's verifier-extension status | **NOT REQUIRED for REJECT verdict** (per CAMPAIGN_010 / 011 / 012 / 013 precedent) |
| C7's verifier-extension required if | C7 reaches `RESEARCH_PASS_UNAPPROVED` |
| if required, sprint label | `infra-free-local-parity-verifier-calendar-event-window-anomaly-001` |
| extension scope | re-implement event-fixture loader + counter-trend signal in independent verifier; ~5–7 day estimate |

## 22. Rejection criteria

C7 is **REJECTED** if any of the following:

1. Any of the 8 inherited aggregate gates fail.
2. Per Phase 2 §4.3: total trades > 800 over 4-year walk-forward
   (turnover overshoot).
3. Per §9 above: signal density > 1,500 over 8 folds (signal density
   overshoot).
4. The cross-pair runner integration contract is N/A here (C7 is a
   per-pair candidate), but the event-fixture coverage contract is
   binding: any fold whose test window is not fully covered by the
   event fixture → fold is invalid → if ≥ 1 fold invalid →
   **BLOCKED**.

C7 is **REJECT (indistinguishable from null)** if the metrics
cluster within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of
CAMPAIGN_011's.

C7 is **RESEARCH_PASS_UNAPPROVED** if all inherited gates pass AND
the turnover budget is respected AND the signal density is respected
AND the event-fixture coverage contract is satisfied AND the null-
baseline meaningful-improvement margins are beaten — but it still
cannot be approved without a deliberate human approval action per
`STRATEGY_APPROVAL_PROCESS.md`.

## 23. Explicit statement: scaffold/evidence sprints cannot approve strategy

**The scaffold sprint (`research-calendar-event-window-anomaly-001`)
cannot approve `calendar_event_window_anomaly` for paper / demo /
live trading. The evidence sprint (`research-calendar-event-window-
anomaly-walk-forward-001`) cannot approve `calendar_event_window_
anomaly` for paper / demo / live trading.**

Even if the evidence sprint produces a verdict of
`RESEARCH_PASS_UNAPPROVED`, the verdict only authorizes:

1. Independent-verifier-extension consideration.
2. A future deliberate human approval action per
   `STRATEGY_APPROVAL_PROCESS.md`.

Approving the strategy requires a human edit to
`configs/approved_strategies.yaml`; no Claude Code sprint can perform
this action.

## 24. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 25. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (binding turnover budget)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (binding patterns)
- [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (C7 selection)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) (Phase 8 — to be written)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (Phase 8 — to be written)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
