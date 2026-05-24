# Next Preferred Real Candidate (Sprint 003)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 4 selection of the **next preferred real candidate** for a
future scaffold sprint, following the Phase 2 reassessment in
[`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
and the Phase 3 feasibility deep dive in
[`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md).
**This selection is not an approval and does not become an
approval through any subsequent sprint without a deliberate
human action.**

> No strategy approved. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. Selected candidate (one-line)

**C3 — Daily-ATR-percentile regime switcher**, to be implemented
under campaign label **`CAMPAIGN_012`** with strategy
**`regime_switcher_atr_percentile 0.1.0-c012`**.

| field | value |
|---|---|
| candidate id (from prior shortlist) | **C3** |
| candidate role | **real candidate** (potential paper-promotion candidate if it survives every gate + human approval) |
| proposed strategy id | `regime_switcher_atr_percentile` |
| proposed strategy version | `0.1.0-c012` |
| proposed campaign label | `CAMPAIGN_012` |
| proposed future scaffold branch | `research-regime-switcher-atr-percentile-001` |
| proposed future evidence branch | `research-regime-switcher-atr-percentile-walk-forward-001` |
| timeframe | H4 (matches CAMPAIGN_010 / CAMPAIGN_011) |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (matches CAMPAIGN_010 / CAMPAIGN_011) |
| data source | `data/campaign_002.sqlite3` (gitignored symlink — same as CAMPAIGN_010 / CAMPAIGN_011) |
| financing posture | ESTIMATED + conservative stress (matches CAMPAIGN_010 / CAMPAIGN_011); MODELED refused at four layers |
| risk-engine mode | backtest (matches CAMPAIGN_010 / CAMPAIGN_011) |
| approval path | requires the full six-evidence ladder + a deliberate human approval action per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) |

## 2. Why C3, not C2 / C4 / new family

Summary from Phase 2 §8 + Phase 3 §11; the decisive factors:

| factor | C2 (carry overlay) | **C3 (selected)** | C4 (vol-expansion straddle) | new family |
|---|:---:|:---:|:---:|:---:|
| zero hard infrastructure blocker | ✗ (MODELED financing refused) | **✓** | ✗ (engine paired-entry absent) | depends |
| zero engine-code change | ✓ | **✓** | ✗ | depends |
| zero data fetch / credential need | ✗ (credentialed `DAILY_FINANCING` capture sprint required first) | **✓** | ✓ | depends |
| can produce a verdict in next 2 sprints (scaffold + evidence) | no | **yes** | no | depends |
| distinctness vs every rejected family ≥ 5 / 6 | 6 / 6 | **5 / 6** | 5 / 6 | depends |
| plausibility of beating CAMPAIGN_011 null floor | strong (carry edge has economic prior) | **plausible (regime-conditional trend persistence)** | plausible | depends |
| no result-driven family selection risk | clean | clean | clean | **high** (any new family proposed *now* would be motivated by CAMPAIGN_011's metrics) |

**C3 is the only candidate this sprint can responsibly select.**
C2 and C4 are deferred behind infrastructure prerequisite
sprints; any new family would be result-driven and disqualified
under protocol §12.G.

## 3. Why this candidate is distinct from CAMPAIGN_002

| dimension | CAMPAIGN_002 (`trend_following 0.1.0`) | **C3 (`regime_switcher_atr_percentile`)** | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | unconditional momentum (EMA + Donchian break) | **volatility-regime-conditional trend** (only trade trend signals in HIGH-VOL regime, defined by trailing-60-day D1AGG ATR-14 percentile) | ✓ |
| 2 entry signal | EMA-50 vs EMA-200 crossover + Donchian-20 break in trend direction | **regime-gated `close[t] vs close[t−4]` momentum + ATR-fraction minimum** | ✓ |
| 3 exit signal | ATR-2.0× trailing stop + N-bar time stop | ATR-2.0× hard stop + 6-bar time stop (no trail in v1) | ≈ (both ATR-stop families) |
| 4 timeframe / universe | H4 / 7 majors | H4 / 7 majors | ≈ (deliberately matched for clean comparison) |
| 5 data inputs | EMA inputs + Donchian high/low + ATR | **D1AGG ATR-14 percentile (from H4 windowed aggregation) + H4 close-momentum + H4 ATR for stop sizing only** | ✓ |
| 6 failure-mode hypothesis | "EMA-Donchian momentum captures trend persistence on H4 majors" | **"trend persistence is regime-conditional — unconditional momentum lost on H4 majors, but high-vol-regime momentum may survive costs"** | ✓ |

**Score: 5 of 6 distinctness vs CAMPAIGN_002.** The two ≈
dimensions (exit signal flavour, timeframe / universe) are
deliberately matched for a clean entry-signal comparison.

## 4. Why this candidate is distinct from CAMPAIGN_010

| dimension | CAMPAIGN_010 (`session_breakout 0.1.0-c010`) | **C3 (`regime_switcher_atr_percentile`)** | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | liquidity-flow continuation (London open) | volatility-regime-conditional trend | ✓ |
| 2 entry signal | London-bar close penetrating prior Asian-bar high/low + Asian-range ATR-fraction gate | regime-gated `close[t] vs close[t−4]` momentum + ATR-fraction gate | ✓ |
| 3 exit signal | ATR stop + 6-bar time stop | ATR stop + 6-bar time stop | ≈ |
| 4 timeframe / universe | H4 / 7 pairs | H4 / 7 pairs | ≈ |
| 5 data inputs | session windows + Asian-range OHLC + ATR | D1AGG ATR percentile + H4 close-momentum + ATR | ✓ |
| 6 failure-mode hypothesis | "London-open continuation has no edge net of costs" | "regime-conditional trend persistence has edge net of costs" | ✓ |

**Score: 5 of 6.** C3 uses no session windows, no Asian-range
gate, no London-close vs prior-Asian-high/low rule. The data
inputs (D1AGG ATR percentile + H4 momentum) are fundamentally
different from CAMPAIGN_010's session-of-day metadata.

## 5. Why this candidate is distinct from CAMPAIGN_011

| dimension | CAMPAIGN_011 (`random_entry_anchor 0.1.0-c011`) | **C3 (`regime_switcher_atr_percentile`)** | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | null model (no theoretical edge) | regime-conditional trend (claims an edge) | ✓ |
| 2 entry signal | deterministic-seed coin flip + per-bar entry-probability gate | regime gate + directional `close[t] vs close[t−4]` rule | ✓ |
| 3 exit signal | ATR stop + 6-bar time stop | ATR stop + 6-bar time stop | ≈ |
| 4 timeframe / universe | H4 / 7 pairs | H4 / 7 pairs | ≈ |
| 5 data inputs | bar-timestamp seed + ATR for stop | D1AGG ATR percentile + H4 close-momentum + ATR | ✓ |
| 6 failure-mode hypothesis | random has no edge by construction | regime-conditional trend has edge by hypothesis | ✓ |

**Score: 5 of 6.** C3 is fundamentally feature-driven; CAMPAIGN_011
is random. The two share only the ATR-stop family and the
timeframe / universe (deliberately matched for clean comparison
under the same gates).

## 6. Why this is not parameter tuning

The Phase 3 feasibility doc §2 pre-committed the C3 frozen
parameters **before any code or backtest**:

- `daily_atr_lookback = 14` — standard Wilder daily ATR; matches
  the H4 ATR lookback for conceptual consistency
- `regime_lookback_days = 60` — ≈ 3 trading months; chosen from
  economic-cycle reasoning, not from prior campaign output
- `regime_percentile_threshold = 0.70` — "top 30 %" — chosen from
  conservative regime-classification reasoning, not from prior
  campaign output
- `min_close_move_atr_fraction = 0.25` — bar-to-bar drift filter;
  matches CAMPAIGN_010's `min_asian_range_atr_fraction = 0.30`
  flavour
- `trend_lookback_h4_bars = 4` — one trading day's worth of H4
  bars; chosen from H4-grid reasoning

The §12 / §2.A–§2.G disqualifiers from
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
applied to C3 (per Phase 2 §5):

| pattern | C3 status |
|---|---|
| Test-window leakage in design | clean — no 2020–2026 statistic motivates any C3 parameter |
| Filter-set tuning to a prior campaign's losing trades | clean — no filter conditioned on CAMPAIGN_002 / 010 / 011 output |
| Parameter range overlap with rejected campaigns | **caution** — `atr_lookback=14` and `atr_stop_multiple=2.0` are project-standard exit-sizing constants used by every H4 candidate; deliberately matched for clean comparison; not tuned values |
| Implicit per-pair tuning | clean — single parameter set across all 7 pairs |
| "Pick the best fold" | clean — every fold runs under the same frozen parameter set |
| Rejection-criterion drift | clean — gates inherited verbatim from CAMPAIGN_010 / CAMPAIGN_011 §11 |
| Result-driven family selection | clean — C3 selected from the protocol §4 whitelist + Phase 2 reassessment; not motivated by CAMPAIGN_011 output |

The §7 null-baseline-anti-tuning rules from
[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md):

| rule | C3 status |
|---|---|
| Tune the random seed | n/a — C3 has no random component |
| Use CAMPAIGN_011 as a trading candidate | n/a — C3 is its own candidate |
| Lower future gates so real candidates look better | clean — C3 inherits CAMPAIGN_010 / 011 gates verbatim |
| Treat merely beating random as approval | clean — C3 must pass every gate, not just beat the null floor |
| Pick a candidate because it would have beaten CAMPAIGN_011 on certain folds | clean — selection based on distinctness + structural feasibility |
| Cite CAMPAIGN_011's per-pair / per-fold sub-metrics to justify a C3 per-pair / per-fold filter | clean — no per-pair filters; no per-fold filters |
| Re-run CAMPAIGN_011 with a "smarter" entry_probability | n/a — C3 does not modify CAMPAIGN_011 |

## 7. Compatibility checks

| requirement | status |
|---|:---:|
| compatible with current 7-pair H4 OANDA practice data | ✓ |
| compatible with the bespoke `BacktestEngine` (single-instrument, single-position) | ✓ |
| compatible with the walk-forward harness (`research/walk_forward/`) | ✓ |
| compatible with the financing overlay (`research/financing/`) | ✓ |
| compatible with the existing risk-engine `mode='backtest'` | ✓ |
| compatible with `parameter_mode = "frozen"` (only authorized mode) | ✓ |
| requires MODELED financing? | no |
| requires D1AGG aggregator? | yes — **already exists** (`src/forex_bot/backtesting/d1_aggregation.py`) |
| requires engine paired-entry support? | no |
| requires new external dependency? | no |
| requires new broker / data fetch? | no |
| requires new credentials? | no |
| requires verifier extension before scaffold? | no — verifier extension is optional and only required for paper-promotion |

C3 has **zero hard blockers**. It can be implemented under the
existing engine, evaluated under the existing harness, overlaid
under the existing financing calculator, and diagnosed under
the existing risk-engine — using existing D1AGG aggregation
infra — with no new infrastructure work.

## 8. What makes the future scaffold sprint successful

The future `research-regime-switcher-atr-percentile-001`
scaffold sprint is **successful** if and only if all of the
following hold at its tip commit:

1. **Strategy module**
   [`src/forex_bot/strategies/regime_switcher_atr_percentile.py`](../../src/forex_bot/strategies/regime_switcher_atr_percentile.py)
   implements the `Strategy` protocol with the R-rule table
   from
   [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
   §6 and no broker imports. The regime-feature helper takes
   only `(h4_candles_completed_only, lookback_days,
   percentile_threshold)` — never bar-`t` price data.
2. **`StrategyConfig.regime_switcher_atr_percentile`** sub-model
   added to [`src/forex_bot/config.py`](../../src/forex_bot/config.py)
   with the frozen parameters from
   [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
   §2 as defaults, with `@model_validator` enforcing valid
   ranges.
3. **Tests** in
   [`tests/unit/test_regime_switcher_atr_percentile.py`](../../tests/unit/test_regime_switcher_atr_percentile.py)
   pinning ≥ 25 cases:
   - config defaults / validation
   - **no-lookahead structural audits** (the regime-feature
     helper's signature contains only the documented arguments;
     no bar-`t` reads in the helper's body; AST-level / source-grep
     checks)
   - **D1AGG rolling-window correctness** (percentile uses
     trailing-60 days strictly preceding the reference day; no
     global percentile; fail-closed under insufficient history)
   - regime classification correctness (HIGH-VOL vs LOW-VOL
     boundary)
   - strategy core (R1 warm-up; R2 block re-entry; R5 fail-closed
     on NaN ATR; R7 stop placement; etc.)
   - no broker / execution / loops imports
   - no CAMPAIGN_002 / 010 / 011 parameter contamination
     (no `donchian`, no `ema_*`, no `asian_*`, no `london_*`,
     no `master_seed`, no `entry_probability`)
   - approval / safety regression (`approved_strategies.yaml`
     still empty; `regime_switcher_atr_percentile` NOT in any
     active loop)
4. **Research config**
   [`configs/campaign_012_regime_switcher_atr_percentile.yaml`](../../configs/campaign_012_regime_switcher_atr_percentile.yaml)
   loads via `load_settings(...)` with `trading_enabled=false`,
   `allow_order_submission=false`, `allow_live_trading=false`,
   the standard 7-pair H4 universe, and `risk.max_open_positions=1`.
5. **CAMPAIGN_012 pre-commit checklist**
   [`docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](docs/research/CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
   committed with the frozen parameters from
   [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
   §2 verbatim, the gate vector inherited from CAMPAIGN_010 §10
   verbatim, and a binding **"Null-baseline reference"** section
   citing CAMPAIGN_011's eight aggregate metrics + the six
   meaningful-improvement margins from
   [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
   §3.
6. **CAMPAIGN_012 status doc** [`docs/research/CAMPAIGN_012_STATUS.md`](docs/research/CAMPAIGN_012_STATUS.md)
   recording the candidate-scaffold-only status.
7. **Non-evidence smoke** confirms config-load PASS, unit suite
   PASS, walk-forward dry-run PASS.
8. **All standing safety checks** PASS at the sprint's tip:
   pytest, ruff, archive validator, freeze checker, secret
   scanner, loop-refusal checks, no live-loop, no broker call,
   no `.env` read.

## 9. What would immediately reject the candidate before implementation

The future scaffold sprint must abort if any of these become true:

- **Any frozen parameter is changed** from the values in
  [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
  §2 based on prior campaign output or pilot results.
- **A "regime threshold sweep"** is run to find a better
  percentile cutoff or lookback window.
- **Approval is requested.** Adding
  `regime_switcher_atr_percentile` to
  `configs/approved_strategies.yaml` (even as a comment) is
  forbidden.
- **Paper / demo / live enablement is attempted.**
- **Engine / financing / risk-policy code is modified.** The
  candidate must run on the existing infrastructure.
- **The D1AGG aggregator is modified.** If the existing
  aggregator's behaviour is insufficient, the response is to
  open a separate `infra-d1-aggregation-*` sprint, not to
  modify it inside CAMPAIGN_012's scaffold.
- **The universe is reduced** "because some pairs are noisy"
  — universe is part of candidate identity (see Phase 2 +
  REJECTED_FAMILY_OVERFIT_GUARDRAILS.md §3).
- **The gates are loosened** — gates inherited verbatim from
  CAMPAIGN_010 §10 + CAMPAIGN_011 §11 null-baseline-comparison.

## 10. Cooldown / re-attempt rule

If CAMPAIGN_012 is REJECTED by the evidence sprint:

- The candidate is retired. Per
  [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §12, re-attempting C3 by tweaking the regime threshold,
  lookback window, or trend sub-signal is a curve-fitting
  anti-pattern.
- A future discovery sprint may consider C2 (post-MODELED) or
  C4 (post-engine-paired-entry) or a genuinely new family per
  protocol §4.

If CAMPAIGN_012 unexpectedly PASSES every gate:

- The candidate becomes the first ever evidence-passing
  candidate in the project's history. It still requires items
  5 (independent corroboration via verifier extension —
  recommended `infra-free-local-parity-verifier-regime-switcher-001`)
  and 6 (deliberate human approval per
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md))
  before any paper-promotion consideration.
- A passing result must be reported alongside the CAMPAIGN_011
  null-baseline comparison verbatim (per
  [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  §8) so the "meaningful improvement over null?" check is
  visible.

## 11. C2 / C4 / null model are NOT discarded

| candidate | status after this sprint | recommended subsequent sprint |
|---|---|---|
| C2 (carry overlay) | **deferred** — blocked on MODELED financing | `research-financing-modeled-capture-credentialed-001` to unblock, then revisit |
| **C3 (regime switcher)** | **selected** as CAMPAIGN_012 | `research-regime-switcher-atr-percentile-001` (scaffold) → `research-regime-switcher-atr-percentile-walk-forward-001` (evidence) |
| C4 (vol-expansion straddle) | **deferred** — blocked on engine paired-entry support | `infra-engine-paired-entry-support-001` to unblock, then revisit |
| CAMPAIGN_011 (null anchor) | **REJECT (null model)** — permanent reference floor; cannot become a trading candidate | none — measurement instrument only |

## 12. Independent-verifier expectation (for C3)

- **Extension is not required for a REJECT verdict.** Item 5
  of the six-evidence ladder is a paper-promotion gate; C3 (if
  REJECTED) needs only items 1–3.
- **Extension is required for a paper-promotion verdict.** If
  CAMPAIGN_012 unexpectedly passes every gate, the verifier
  must be extended to corroborate it before approval review.
- **Suggested follow-up sprint** (conditional):
  `infra-free-local-parity-verifier-regime-switcher-001` — adds
  the regime-feature + D1AGG path to
  `research/parity_verifier/rules.py` + a CAMPAIGN_012 bespoke
  reference loader + comparison rules.
- **Neither the scaffold nor the evidence sprint is blocked**
  on verifier extension. Verifier work is a follow-up.

## 13. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 remain REJECT**
  (untouched).
- **Paper / demo / live remain blocked.**
- No strategy code edited this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 14. Cross-links

- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md)
  (Phase 2 scoring)
- [`C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md`](C3_REGIME_SWITCHER_FEASIBILITY_REVIEW.md)
  (Phase 3 feasibility + binding pre-commit parameters)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  (binding null-baseline comparison rules)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §4 + §12
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
  §10 (the gate vector C3 inherits)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  §11 (same gate vector; CAMPAIGN_010 inherited)
- [`NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_IMPLEMENTATION_DESIGN_003.md)
  (Phase 5 — detailed implementation design)
- [`NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_SCAFFOLD_BRANCH_SPEC_003.md)
  (Phase 6 — future scaffold-branch spec)
- [`NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md`](NEXT_REAL_CANDIDATE_EVIDENCE_BRANCH_SPEC_003.md)
  (Phase 6 — future evidence-branch spec)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_PROTOCOL.md`](FINANCING_MODEL_PROTOCOL.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
