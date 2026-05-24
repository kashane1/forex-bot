# Next Preferred Direction (Phase 6)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 6 selection. Picks exactly one next path from the
[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md)
shortlist + [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md)
infrastructure options. **No implementation; no backtest; no broker
call.** Phase 7 designs the selected path; Phase 8 writes the binding
future-branch specs.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 all
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`.

## 1. Selection

# **SELECTED: C7 — Calendar-Event Window Anomaly (CEWA)**

| field | value |
|---|---|
| **candidate id** | **C7** |
| **proposed strategy id** | `calendar_event_window_anomaly` |
| **proposed version** | `0.1.0-c014` |
| **proposed campaign label** | **CAMPAIGN_014** |
| **proposed scaffold branch** | `research-calendar-event-window-anomaly-001` |
| **proposed evidence branch** | `research-calendar-event-window-anomaly-walk-forward-001` |
| **path type** | new candidate (not infrastructure) |

## 2. Why C7 was selected (vs C10 / C12 / C11 / C13 / infra-A / infra-B / infra-C / infra-D)

| comparison | C7 wins because |
|---|---|
| **vs C10 (WBH4E)** | both are excellent; C7 is preferred because (a) its hypothesis is **economically grounded** (post-event mis-priced-surprise mean reversion is a well-documented FX phenomenon, citable in academic and practitioner literature), (b) the calendar fixture is a **reusable data primitive** that future event-window candidates can share, (c) C7's **per-event-class diagnostic surface** (NFP / FOMC / ECB / BoJ / BoE × 7 pairs) produces high-information evidence even if the verdict is REJECT, (d) C7's defense against turnover-amplification is **structural** (the event set is finite per year, not threshold-tuned). C10 stays as the **immediate fallback** if C7 hits a data-fixture blocker |
| **vs C12 (MFSR)** | C12 is viable but its **long hold (21 trading days)** makes financing a meaningful per-trade cost (~25–45 bp under conservative stress); the gross-expectancy bar is ~80 bp net, which is a stringent first-principles requirement for a monthly-rebalance signal. C7's short hold (2–6 H4 bars) keeps financing < 1 bp per trade, making the cost section more naturally clearable |
| **vs C11 (LHRVPS)** | C11 is a **modifier, not a standalone**; it requires both an entry candidate AND an engine sizing-injection point. C7 is a complete, standalone proposal. C11 can be paired with C7 in a future sprint if research warrants it |
| **vs C13 (QESCF)** | C13 is **DISQUALIFIED** at shortlist (Pattern U + K + G; rejected-family stack disguised as calendar filter) |
| **vs infra-A (MODELED financing capture)** | infra-A requires **human authorization** Claude Code cannot grant; touches account / transaction endpoints; involves credentialed broker access. The discovery-005 sprint cannot start infra-A. C7 produces research evidence in this sprint cycle without human-authorization dependencies |
| **vs infra-B (engine paired-entry support)** | infra-B is **multi-sprint engine rewrite** scope. The only candidate that needs it (C4) does not have independent multi-family justification today. C7 produces research evidence faster and does not require engine changes |
| **vs infra-C (verifier extension)** | infra-C is **post-PASS by design**. No candidate has reached `RESEARCH_PASS_UNAPPROVED`; infra-C cannot be valuable until one does. C7 may eventually trigger infra-C if it passes — but selecting infra-C now would be premature |
| **vs infra-D (ruff cleanup)** | infra-D is cosmetic; does not unblock anything; clear waste of a discovery-output slot |

## 3. Why this is not a rejected-family tune

| rejected family | shared mechanism with C7? | distinctness argument |
|---|---|---|
| CAMPAIGN_002 (`trend_following`) | NO | C7 has no EMA / Donchian / single-pair direction trigger; signal is *post-event counter-trend*, not within-pair momentum |
| CAMPAIGN_003 (`trend_following + ADX`) | NO | no trend filter; no momentum gate |
| CAMPAIGN_004 (`volatility_breakout`) | NO | no ATR-compression / breakout logic; signal is event-window-conditional, not vol-regime-conditional |
| CAMPAIGN_007 (`pullback_continuation`) | NO | no pullback definition or continuation trigger |
| CAMPAIGN_008/009 (`mean_reversion` range) | LIMITED — C7 is **also counter-trend**, but the *trigger* is fundamentally different (scheduled-event timestamp vs Bollinger Z-score / range overshoot). The mechanism is event-conditional, not statistic-conditional. Defense: C7's mean-reversion is **temporally conditional** on a calendar event (a structural feature), while CAMPAIGN_008/009's was conditional on a *statistic* (which CAMPAIGN_008/009 falsified on this universe); C7 trades only ~150–400 trades per 4y (vs CAMPAIGN_008's ~10,000+ if continuously enabled), which directly avoids the turnover-amplification pattern that took CAMPAIGN_008/009 down |
| CAMPAIGN_010 (`session_breakout`) | NO | no Asian-range / London-window logic; events span all sessions; no breakout direction |
| CAMPAIGN_011 (`random_entry_anchor`, null) | NO | fully deterministic from calendar fixture + price; no PRNG, no `master_seed`, no Bernoulli draw |
| CAMPAIGN_012 (`regime_switcher_atr_percentile`) | NO | no single-pair vol-percentile gate; no close-vs-close trend filter; signal is event-window-conditional |
| CAMPAIGN_013 (`cross_pair_currency_strength_rotation`) | NO | no cross-pair ranking; no cross-sectional FX-rank metric; signal is per-pair event-window-conditional |

**Distinctness vs each rejected family: 8 / 8.** Confirmed pre-Phase 7.

The closest adjacency is CAMPAIGN_008/009 (also counter-trend), but
the *trigger* is fundamentally different (calendar timestamp vs price
statistic) and the *cadence* is fundamentally different (finite event
set vs continuous Bollinger). Phase 7 implementation design must make
this distinction explicit in the binding spec.

## 4. Patterns H–W that C7 could be *mistaken* for, and why it is not

| pattern | could C7 be mistaken for it? | why C7 is not this pattern |
|---|---|---|
| **H** — "same regime gate, different threshold" | NO — C7 does not use a regime gate at all | event-window is a deterministic timestamp filter, not a vol-percentile threshold |
| **I** — "same trend filter, different lookback" | NO — C7 does not use a trend filter | counter-trend mean reversion in event windows; no lookback at all |
| **J** — "same daily-ATR-percentile, different cutoff" | NO — C7 does not use a percentile metric | event timestamps are not percentile-based |
| **K** — "rescue rejected regime switcher with session/pair/day filters" | NO — C7 does not combine with any rejected family | C7 is single-mechanism; no session filter; no pair filter; no day filter; no overlay on any rejected strategy |
| **L** — "pick new family because it fixes a CAMPAIGN_012 per-fold artifact" | NO — C7's hypothesis exists independent of CAMPAIGN_012 | post-event mean-reversion is documented in FX literature (e.g. Bouchaud-Farmer trade-flow literature; post-NFP / post-FOMC overshoot studies) and was *considered and not selected* in discovery-004 only because C6 was selected first |
| **M** — "high-frequency H4 firehose entries" | NO — explicitly LOW turnover (~150–400 trades/4y; well below CAMPAIGN_011's 1,177 null floor) | event set is finite per year by construction |
| **N** — "broad simultaneous multi-pair entries without portfolio-level edge proof" | NO — most events are USD-driven, so simultaneous-pair entries are concentrated to USD-major pairs; this is justified by the hypothesis (the event affects USD specifically, so all USD-pairs are simultaneously informative) | the hypothesis explicitly justifies simultaneous USD-pair entries during USD events; Phase 7 will pre-commit a per-trade portfolio-risk diagnostic |
| **O** — "turnover-amplifying filter on rejected core" | NO — the core direction (counter-trend mean-reversion) is *not* a previously-rejected entry signal in this specific (event-window) context | CAMPAIGN_008/009 rejected continuous-trigger Bollinger MR; C7's MR is event-time-conditional, structurally different. C7 *reduces* turnover vs CAMPAIGN_008/009 by ~25–60 ×, not amplifies |
| **P** — "pair-only survivor selection from rejected campaigns" | NO — C7's universe is all 7 pairs | no per-pair carve-out; events apply per pair based on event-class relevance (e.g. NFP is USD-relevant, applies to all USD pairs; ECB is EUR-relevant, applies to EUR_USD; etc.) |
| **Q** — "cost-insensitive signal design" | NO — C7's pre-commit will include the full cost section | per-trade spread + slippage ~1.5 bp; per-trade financing < 1 bp; gross expectancy bar ~5 bp net to clear 0.05 R |
| **R** — "same cross-pair rank gate, different threshold" | NO — C7 does not rank | event-window trigger is not a rank |
| **S** — "same cross-pair ranking metric, different lookback" | NO — C7 does not rank | event-window trigger is not a metric to lookback over |
| **T** — "same cross-pair rotator, pair-filtered after rejection" | NO — C7 is not a cross-pair rotator | per-pair event-window candidate |
| **U** — "same cross-pair rotator with session/regime rescue filter" | NO — C7 is not a cross-pair rotator | per-pair event-window candidate |
| **V** — "high-turnover variant of any rejected family" | NO — C7's turnover is LOW | ~150–400 trades over 4y |
| **W** — "select new family because it fixes a CAMPAIGN_013 per-pair / per-fold artifact" | NO — C7's hypothesis exists independent of CAMPAIGN_013 | post-event mean-reversion was on the discovery-004 shortlist (predates CAMPAIGN_013 sprint outcome) |

## 5. Why this is not parameter tuning

The C7 candidate proposes a **brand new signal family**, not a
re-parameterization of any rejected strategy:

- **No existing strategy in the bespoke engine implements calendar-
  event-window-conditional entries.** All 8 implemented strategies
  (`trend_following`, `volatility_breakout`, `pullback_continuation`,
  `mean_reversion`, `session_breakout`, `random_entry_anchor`,
  `regime_switcher_atr_percentile`, `cross_pair_currency_strength_
  rotation`) gate entries on **price features only** (trend, breakout,
  pullback, range Z-score, session window, PRNG, vol percentile,
  cross-pair rank). C7 introduces a **new gating modality**:
  scheduled-event timestamp matching.
- **C7 requires a new event-calendar fixture** (~10 KB committed JSON
  / CSV) and a new event-calendar loader. This is a **new data
  primitive**, not a knob on an existing one.
- **C7's frozen parameters (proposed)** will be pre-committed pre-
  implementation in Phase 7 design (`event_set`, `pre_event_block_
  bars`, `post_event_window_bars`, `atr_stop_multiple`, etc.). No
  sweep around prior campaigns' values.
- **No CAMPAIGN_013 parameter is reused.** C7 does not use
  `currency_strength_lookback_bars`, `rank_gap_threshold`, or any
  cross-pair-rotation parameter. No CAMPAIGN_012 parameter reused
  either.

## 6. Why C7 is compatible with current infrastructure

| dimension | C7 status |
|---|---|
| bespoke engine | YES — fits single-instrument single-position invariant; per-pair runner pattern (used by CAMPAIGN_010 / 011 / 012 / 013 runners) handles multi-pair orchestration naturally |
| data | YES — uses existing 7-pair H4 OANDA-practice store + a new bounded committed calendar fixture; no broker fetch needed for either |
| walk-forward harness | YES — inherits 8-fold rolling/frozen plan verbatim |
| financing | YES — ESTIMATED + conservative stress sufficient (short hold); MODELED refused remains intact |
| RiskEngine | YES — existing per-pair spread filter + session filter + max-position caps unchanged |
| `D1AGG` aggregator | not used by C7 (the event-window signal is H4 + event-timestamp only) |
| LEAN | N/A (retired) |
| MODELED financing | **not required** (this is critical — C7 is not blocked) |
| paired-entry engine support | **not required** |
| live broker credentials | **not required** |
| event calendar | **NEW DATA DEPENDENCY** — a one-time committed JSON/CSV fixture of ~30–60 high-impact events per year × ~6 years (2020 → 2026); compiled from public sources (BLS, FOMC.gov, ECB.europa.eu, BoJ.or.jp, BoE) before scaffold sprint runs |

## 7. Safety under current project rules

- **No `.env` read** required (data + signal are local; event fixture
  is committed).
- **No broker / account / order / trade / position / transaction
  endpoint queries** required.
- **No `live-loop` creation** required.
- **No QuantConnect / LEAN** usage required.
- **No MODELED financing** required (live-promotion blocker stands
  but is informationally separate from C7's research-evidence
  evaluation).
- **`configs/approved_strategies.yaml` remains `approved: []`**
  throughout the scaffold + evidence sprints; only a deliberate human
  approval action per `STRATEGY_APPROVAL_PROCESS.md` can add it (and
  no Claude Code sprint can do so).
- The scaffold sprint's tests are deterministic synthetic-fixture
  unit tests + small calendar-fixture tests; the evidence sprint
  runs walk-forward only against the local SQLite store + the
  committed event fixture.
- **The calendar fixture** is sourced from public, verifiable
  government / central-bank URLs (BLS for NFP, FOMC.gov for FOMC,
  etc.); compilation is a deterministic, audited, one-time step;
  the fixture itself is a small text file committed to the repo, not
  a broker call.

## 8. Why this is valuable even if C7 later rejects

A REJECT verdict on C7 is still high-value research evidence:

- **Falsifies event-window-mean-reversion hypothesis on the 7-pair
  H4 universe** — eliminates an entire signal class from the next
  discovery sprint's menu.
- **Adds a reusable calendar-fixture data primitive** to the repo
  for future event-window candidates (e.g. C8-style vol-compression
  triggered by events; carry-aware overlay reacting to rate-decision
  events).
- **Stress-tests the no-lookahead invariants for calendar-time
  access** — a new no-lookahead invariant ("`event_time <= bar_
  complete_time`") is a useful general capability for the harness.
- **Adds to the rejected-family corpus** for future overfit
  guardrails (Pattern X: "no event-window mean-reversion with
  different window length" if C7 rejects).
- **Provides a non-cross-pair real-edge candidate** alongside
  CAMPAIGN_002 / 010 / 012 / 013 — the rejected corpus would then
  span trend (CAMPAIGN_002 / 003), vol-breakout (CAMPAIGN_004),
  pullback (CAMPAIGN_007), MR (CAMPAIGN_008 / 009), session
  (CAMPAIGN_010), null (CAMPAIGN_011), regime (CAMPAIGN_012),
  cross-pair (CAMPAIGN_013), event-window (CAMPAIGN_014) —
  strengthening the meta-falsification claim that H4-on-majors with
  the current cost model is a hostile environment for many signal
  families.

If C7 unexpectedly passes (reaches `RESEARCH_PASS_UNAPPROVED`):

- The verifier-extension sprint
  `infra-free-local-parity-verifier-calendar-event-window-anomaly-001`
  becomes required for any paper-promotion consideration (item 5 of
  six-evidence ladder).
- A deliberate human approval action (item 6) remains required.
- `configs/approved_strategies.yaml` still cannot change without that
  human action.

## 9. Key implementation requirements (preview; Phase 7 has the binding spec)

- **R1–R8 rule table** (binding; Phase 7 will write) — calendar
  fixture warm-up, event-window proximity check, no-lookahead event-
  time access, counter-trend signal direction definition, ATR stop
  placement, max-hold time stop, exit semantics, deterministic
  Signal emission.
- **Pre-committed event set** — the binding list of event classes
  (NFP, FOMC, ECB, BoJ, BoE rate decisions) and impact ranks pre-
  declared in `CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`; mid-sprint
  expansion forbidden.
- **No-lookahead invariants** for calendar-time access (new for the
  harness; ≥ 5 invariants).
- **8–10 frozen parameters** pre-committed.
- **`CalendarEventWindowAnomalyStrategyConfig`** schema with
  `extra="forbid"` + `@model_validator` rejecting invalid bounds.
- **≥ 30 unit tests** planned (config validation, happy path, no-
  lookahead audit, event-fixture loader, event-window boundary,
  per-event-class diagnostics, forbidden imports, rejected-family
  contamination, approval regression).
- **Walk-forward** inherits CAMPAIGN_010 / 011 / 012 / 013 plan
  verbatim (8 folds rolling/frozen) + null-baseline comparison gate
  + **turnover-budget gate (new; Phase 2 binding)** + **per-event-
  class diagnostic surface (new; C7-specific)**.
- **Financing** ESTIMATED + conservative stress; MODELED refused
  (live-promotion blocker stands).
- **Risk diagnostics** must include event-class clustering, per-
  pair event-sensitivity, entry-window concentration, pre vs post
  event distribution.
- **Verifier extension** required only if `RESEARCH_PASS_UNAPPROVED`.

## 10. Safety state (unchanged)

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

## 11. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
- [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_005.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_005.md) (Phase 7 — to be written)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_005.md) (Phase 8 — to be written)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (Phase 8 — to be written)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
