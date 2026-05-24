# Next Preferred Direction (Phase 5)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 5 selection. Picks exactly one next path from the
[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md)
shortlist + [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md)
infrastructure options. **No implementation; no backtest; no broker
call.** Phase 6 designs the selected path; Phase 7 writes the binding
future-branch specs.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 all remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Selection

# **SELECTED: C6 — Cross-Pair Currency Strength Rotation (CPCSR)**

| field | value |
|---|---|
| **candidate id** | **C6** |
| **proposed strategy id** | `cross_pair_currency_strength_rotation` |
| **proposed version** | `0.1.0-c013` |
| **proposed campaign label** | **CAMPAIGN_013** |
| **proposed scaffold branch** | `research-cross-pair-currency-strength-rotation-001` |
| **proposed evidence branch** | `research-cross-pair-currency-strength-rotation-walk-forward-001` |
| **path type** | new candidate (not infrastructure) |

## 2. Why C6 was selected (vs C7 / C8 / C9 / infra-A / infra-B)

| comparison | C6 wins because |
|---|---|
| **vs C7 (Calendar-Event Window Anomaly)** | C6 has **zero new data dependencies**. C7 requires a new event-calendar fixture (NFP / FOMC / ECB / BoJ / BoE dates), which is one-time small but still a new committed JSON + new loader code + new no-lookahead invariants. C6 reuses the existing 7-pair H4 store unchanged. C7 is a strong fallback if C6 also rejects. |
| **vs C8 (Multi-Window Volatility-Compression Breakout)** | C6 is structurally further from any rejected family. C8 sits next to CAMPAIGN_004 (volatility-breakout, REJECTED) and would need a careful defense in Phase 6 to demonstrate the cross-timeframe AND-gate is a genuinely different mechanism rather than a CAMPAIGN_004 retune with an extra knob. C6 has no such proximity risk. |
| **vs C9 (Time-of-Day Cost-Adjusted Mean Reversion on Spreads)** | C9 sits next to CAMPAIGN_008 / 009 (mean-reversion, REJECTED). Same Phase 6 defense burden. C9's *direction* (counter-trend) is the same as CAMPAIGN_008/009; only the *trigger* (spread-time-of-day) differs. Distinctness 5/6 (the weakest of the shortlist). |
| **vs infra-A (MODELED financing capture)** | infra-A requires **human authorization** Claude Code cannot grant; touches account / transaction endpoints; involves credentialed broker access. The discovery-004 sprint cannot start infra-A. C6 produces research evidence in this sprint cycle without human-authorization dependencies. |
| **vs infra-B (engine paired-entry support)** | infra-B is **multi-sprint engine rewrite** scope. The only candidate that needs it (C4) does not have independent multi-family justification today. C6 produces research evidence faster and unblocks future families that fit the existing engine. |
| **vs infra-C (verifier extension)** | infra-C is **post-PASS by design**. No candidate has reached `RESEARCH_PASS_UNAPPROVED`; infra-C cannot be valuable until one does. C6 may eventually trigger infra-C if it passes — but selecting infra-C now would be premature. |
| **vs infra-D (ruff cleanup)** | infra-D is cosmetic; does not unblock anything; clear waste of a discovery-output slot. |

## 3. Why this is not a rejected-family tune

| rejected family | shared mechanism with C6? | distinctness argument |
|---|---|---|
| CAMPAIGN_002 (`trend_following`) | NO | C6 has no EMA / Donchian / single-pair direction trigger; signal is *cross-pair rank delta*, not within-pair momentum. |
| CAMPAIGN_010 (`session_breakout`) | NO | C6 has no Asian-range / London-window logic; trades any H4 bar where the rank-gap exceeds threshold. |
| CAMPAIGN_011 (`random_entry_anchor`, null) | NO | C6 is fully deterministic from price — no PRNG, no `master_seed`, no Bernoulli draw. |
| CAMPAIGN_012 (`regime_switcher_atr_percentile`) | NO | C6 has **no single-pair vol-percentile gate**. The signal is structural cross-pair relative strength, *not* "trade within HIGH-VOL regime". |
| CAMPAIGN_004 (`volatility_breakout`) | NO | C6 has no ATR-compression / breakout logic. |
| CAMPAIGN_007 (`pullback_continuation`) | NO | C6 has no pullback definition or continuation trigger. |
| CAMPAIGN_008 / 009 (`mean_reversion`) | NO | C6 trades in the direction of relative strength, not counter to a range overshoot. |

**Distinctness vs each rejected family: 6 / 6.** Confirmed pre-Phase 6.

## 4. Patterns H–L (discovery-004 addendum) that C6 could be *mistaken* for, and why it is not

| pattern | could C6 be mistaken for it? | why C6 is not this pattern |
|---|---|---|
| **H** — "same regime gate, different threshold" | not really — but observers might say "rank threshold is a vol-style threshold" | C6's "rank-gap threshold" is over a cross-pair *rank* (a relative metric), not a within-pair vol percentile. The rank metric is fundamentally different from vol-percentile because it depends on *all 7 pairs* contributing simultaneously, not on any one pair's volatility. |
| **I** — "same trend filter, different lookback" | could be mistaken for "rolling-window relative strength is a trend lookback" | C6 does not trade in the direction of any one pair's trend. It trades in the direction of *relative strength across the 7-pair universe*. The rolling window is for ranking, not for direction. |
| **J** — "same daily-ATR-percentile, different cutoff" | NO — C6 does not use a percentile metric at all. | The signal feature is rolling-window currency-strength rank, not a percentile. |
| **K** — "rescue rejected regime switcher with session/pair/day filters" | NO — C6 does not combine with any rejected family's signal. | C6 is single-mechanism; no session filter; no pair filter; no day filter; no overlay on any rejected strategy. |
| **L** — "pick new family because it fixes a CAMPAIGN_012 per-fold artifact" | NO — C6's hypothesis exists independent of CAMPAIGN_012. | The cross-pair currency-strength concept is documented in FX literature (e.g. "currency strength index", widely used in retail FX education and academic FX-momentum literature) and was *considered and disqualified* in discovery-003 only because the C3 candidate was selected first — not because CAMPAIGN_012's per-fold results suggested it. |

## 5. Why this is not parameter tuning

The C6 candidate proposes a **brand new signal family**, not a
re-parameterization of any rejected strategy:

- **No existing strategy in the bespoke engine implements cross-pair
  ranking.** All 7 implemented strategies (`trend_following`,
  `volatility_breakout`, `pullback_continuation`, `mean_reversion`,
  `session_breakout`, `random_entry_anchor`, `regime_switcher_atr_percentile`)
  operate on a **single instrument** at a time and emit per-pair
  signals from within-pair features.
- **C6 requires a new orchestration layer** that reads all 7 pairs'
  H4 closes simultaneously to compute currency-strength ranks. This
  is a new mechanism, not a knob on an existing one.
- **C6's frozen parameters (proposed)** — `currency_strength_lookback_bars`,
  `rank_gap_threshold`, etc. — are pre-committed pre-implementation
  (Phase 6 binds them). No sweep around prior campaigns' values.
- **No CAMPAIGN_012 parameter is reused.** C6 does not use
  `daily_atr_lookback`, `regime_lookback_days`, `regime_percentile_threshold`,
  `min_close_move_atr_fraction`, or `trend_lookback_h4_bars`.

## 6. Why C6 is compatible with current infrastructure

| dimension | C6 status |
|---|---|
| bespoke engine | YES — fits single-instrument single-position invariant **per pair**; the per-pair runner pattern (used by CAMPAIGN_010 / 011 / 012 runners) handles multi-pair orchestration naturally |
| data | YES — uses existing 7-pair H4 OANDA-practice store; no new fetch; provenance matches CAMPAIGN_010 / 011 / 012 |
| walk-forward harness | YES — inherits 8-fold rolling/frozen plan verbatim |
| financing | YES — ESTIMATED + conservative stress sufficient; MODELED refused remains intact |
| RiskEngine | YES — existing per-pair spread filter + session filter + max-position caps unchanged |
| `D1AGG` aggregator | not used by C6 (the rank signal is H4-only) |
| LEAN | N/A (retired) |
| MODELED financing | **not required** (this is critical — C6 is not blocked) |
| paired-entry engine support | **not required** |
| live broker credentials | **not required** |

## 7. Safety under current project rules

- **No `.env` read** required (data + signal are local).
- **No broker / account / order / trade / position / transaction
  endpoint queries** required.
- **No `live-loop` creation** required.
- **No QuantConnect / LEAN** usage required.
- **No MODELED financing** required (live-promotion blocker stands
  but is informationally separate from C6's research-evidence
  evaluation).
- **`configs/approved_strategies.yaml` remains `approved: []`**
  throughout the scaffold + evidence sprints; only a deliberate human
  approval action per `STRATEGY_APPROVAL_PROCESS.md` can add it (and
  no Claude Code sprint can do so).
- The scaffold sprint's tests are deterministic synthetic-fixture
  unit tests; the evidence sprint runs walk-forward only against the
  local SQLite store.

## 8. Why this is valuable even if C6 later rejects

A REJECT verdict on C6 is still high-value research evidence:

- **Falsifies cross-pair-rotation hypothesis on the 7-pair H4
  universe** — eliminates an entire signal class from the next
  discovery sprint's menu.
- **Adds to the rejected-family corpus** for future overfit
  guardrails (Pattern M: "no cross-pair rank gate with different
  threshold" if C6 rejects).
- **Stress-tests the multi-pair orchestration layer** of the
  bespoke engine, which is currently exercised only by the
  per-pair-loop pattern. If the orchestration layer has bugs, C6
  will surface them.
- **Provides a second non-trivial real-edge candidate** alongside
  CAMPAIGN_012 — strengthens the null-baseline comparison
  framework (we'd then have two real-edge candidates both compared
  to CAMPAIGN_011, both rejected, both informationally distinct).

If C6 unexpectedly passes (reaches `RESEARCH_PASS_UNAPPROVED`):

- The verifier-extension sprint
  `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`
  becomes required for any paper-promotion consideration (item 5 of
  six-evidence ladder).
- A deliberate human approval action (item 6) remains required.
- `configs/approved_strategies.yaml` still cannot change without that
  human action.

## 9. What the next sprint will produce (preview; Phase 6 has the binding spec)

- `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py`
  (the strategy module)
- `CrossPairCurrencyStrengthRotationStrategyConfig` in
  `src/forex_bot/config.py` + `StrategyConfig` slot + enabled-list
  check
- `tests/unit/test_cross_pair_currency_strength_rotation.py` (≥ 30
  tests planned)
- `configs/campaign_013_cross_pair_currency_strength_rotation.yaml`
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`
- `docs/research/CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`
- `docs/research/CAMPAIGN_013_STATUS.md`
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_READINESS.md`
- `docs/research/CAMPAIGN_013_SMOKE_RESULT.md`
- `docs/research/CAMPAIGN_013_WALK_FORWARD_READINESS.md`
- `docs/research/CAMPAIGN_013_FINANCING_RISK_READINESS.md`
- `docs/research/CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`
- `docs/research/CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`

That is the scaffold sprint output (mirrors the CAMPAIGN_012 scaffold
structure). The evidence sprint follows the same pattern as
`research-regime-switcher-atr-percentile-walk-forward-001`.

## 10. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 | all REJECT (untouched) |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| this sprint's broker call | none |
| `.env` read / credential printed | none |
| account / order / trade / position / transaction endpoint queried | none |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing (unchanged) |

## 11. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_004.md) (Phase 6 — to be written)
- [`NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_SCAFFOLD_BRANCH_SPEC_004.md) (Phase 7 — to be written)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_004.md) (Phase 7 — to be written)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
