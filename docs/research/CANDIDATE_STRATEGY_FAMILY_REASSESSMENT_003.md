# Candidate Strategy Family Reassessment (Sprint 003)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-003`
`strategy_evidence: false`

Phase 2 reassessment of the remaining real candidate families
(C2 / C3 / C4) under the expanded rejected baseline (now 6
rejected families plus the CAMPAIGN_011 null-model anchor) and
current infrastructure constraints. **This document does not
approve any strategy.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. CAMPAIGN_011 remains REJECT (null-model
> anchor). `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. The expanded rejected baseline (6 rejected families + 1 null anchor)

Per [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
+ [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md):

| family | rejected verdict |
|---|---|
| **TF** — `trend_following 0.1.0` (CAMPAIGN_002) + ADX-gated variant (CAMPAIGN_003) | REJECT |
| **VB** — `volatility_breakout 0.1.0-c004` (CAMPAIGN_004) | REJECT |
| **PB** — `pullback_continuation` (CAMPAIGN_007) | REJECT |
| **MR** — `mean_reversion` (CAMPAIGN_008 / CAMPAIGN_009) | REJECT |
| **SB** — `session_breakout 0.1.0-c010` (CAMPAIGN_010) | REJECT |
| **RAND (null)** — `random_entry_anchor 0.1.0-c011` (CAMPAIGN_011) | REJECT (null-model anchor; cannot be approved by design); functions as falsifiability floor |

Every new candidate must score ≥ 3 of 6 distinctness vs every
prior REJECTED family **and** must beat the CAMPAIGN_011 null
anchor by a meaningful margin (per Phase 1 §3).

## 2. The candidate roster (recap from prior reassessments)

| # | candidate name | category | prior status |
|---:|---|---|---|
| ~~C1~~ | ~~Asian-range / London-open session breakout~~ | ~~Session-of-day breakout~~ | **REJECTED (CAMPAIGN_010)** — out of consideration |
| C2 | Carry-aware long-only overlay | Carry-aware position overlay | deferred (blocked on MODELED financing) |
| C3 | Daily-ATR-percentile regime switcher | Volatility-regime switching | candidate (recommended for selection per discovery-002 §8.4) |
| C4 | Volatility-expansion non-directional straddle | Volatility-regime expansion | deferred (blocked on engine paired-entry) |
| ~~C5~~ | ~~H4 random-entry diagnostic anchor~~ | ~~Baseline / null model~~ | **EXECUTED (CAMPAIGN_011 REJECT — null-model anchor)** — out of consideration as a real candidate |

The remaining real candidates are **C2, C3, C4**. No new family
is proposed in this reassessment — see §7 for the rationale.

## 3. Scored comparison table (this sprint's reassessment)

### 3.1 Distinctness scoring (≥ 3 of 6 required vs every rejected family)

| candidate | vs TF | vs VB | vs PB | vs MR | vs SB (CAMPAIGN_010) | vs RAND (CAMPAIGN_011 null) | min score | clears 3-of-6? |
|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| C2 — carry overlay | 6 / 6 | 6 / 6 | 6 / 6 | 6 / 6 | 6 / 6 | 6 / 6 (different theoretical bucket, different entry, different exit, different data inputs, different failure-mode hypothesis; only universe/timeframe overlap) | 6 | ✓ |
| C3 — daily-ATR percentile regime switcher | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 (regime-conditional entry vs random; different data inputs — daily ATR percentile vs none) | 5 | ✓ |
| C4 — volatility-expansion straddle | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 | 6 / 6 (paired entry vs single random; different exit; different inputs) | 5 | ✓ |

All three remaining real candidates clear the distinctness gate
against every rejected family including the CAMPAIGN_011 null
anchor.

### 3.2 Implementation complexity

| candidate | new strategy module | new config sub-model | new tests | new scripts | engine work | data work | total complexity |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| C2 | yes | yes | ~30 cases | runner + financing overlay + risk diagnostics | none (single-instrument-per-account works) | none for prices; **YES** for financing (real DAILY_FINANCING capture is a separate credentialed-pilot sprint) | **high** (data work is the blocker) |
| **C3** | **yes** | **yes** | **~30 cases** (D1AGG-from-H4 aggregation in-strategy; ATR-percentile rolling window; regime-conditional entry; no-lookahead audits) | **runner + financing overlay + risk diagnostics** (clone CAMPAIGN_010/011 pattern) | **none** (single-instrument H4 entry; D1AGG aggregated in-strategy from H4 windowed data using existing `src/forex_bot/backtesting/d1_aggregation.py` helpers, OR a simpler internal rolling-window daily aggregation that returns prior-day completed data) | **none** (existing 7-pair H4 store covers everything; D1AGG is computed in-process per request) | **medium** |
| C4 | yes | yes | ~30 cases | runner + financing overlay + risk diagnostics | **YES** — paired-entry semantics; `max_positions_per_instrument = 2` for the straddle; possibly two separate positions per pair | none | **high** (engine work is the blocker) |

### 3.3 Engine compatibility

| candidate | compatible with existing BacktestEngine? | notes |
|---|:---:|---|
| C2 | ✓ | Single-instrument-per-account; needs financing-rate source plumbed in (the calculator exists; the engine consumes per-fold trade artifacts). |
| **C3** | **✓** | Single-instrument; H4 entry; daily-ATR percentile computed in-strategy from H4 windowed data (the strategy module can call `aggregate_h4_to_d1(...)` from `forex_bot.backtesting.d1_aggregation` against `ctx.candles.completed_only()` to produce prior-completed-day ATR — no D1 backtest semantics involved, so no CAMPAIGN_006 blocker). |
| C4 | **✗** | Bespoke `BacktestEngine` is single-instrument-single-position. A literal straddle requires either (a) two simultaneous positions on the same instrument or (b) two separate "instrument" instances — both are engine-level changes. |

### 3.4 Data availability

| candidate | local data sufficient? | data work needed | new credentials needed | new external dependency? |
|---|:---:|---|:---:|:---:|
| C2 | **partial** | Real `DAILY_FINANCING` capture from OANDA practice account (separate credentialed-pilot sprint) | yes (practice token, separate sprint) | none |
| **C3** | **✓** | None (existing 7-pair H4 store via `data/campaign_002.sqlite3` symlink; D1AGG derived in-process per backtest) | none | none |
| C4 | ✓ | None (existing 7-pair H4 store) | none | none |

### 3.5 Walk-forward harness compatibility

| candidate | rolling-window frozen-parameter walk-forward feasible? | min fold count satisfied? |
|---|:---:|:---:|
| C2 | ≈ (carry is a slow signal; 6-fold rolling on 6-year H4 is structurally fine, but the **effective independent windows** are fewer — carry regimes change slowly) | ✓ |
| **C3** | **✓** (same 8-fold structure as CAMPAIGN_010/011 works; the rolling daily-ATR percentile lookback is bounded by the strategy's per-bar warmup; no fold-boundary leakage because each fold runs in isolation against its test window) | ✓ |
| C4 | ≈ (straddle accounting must be reconciled per-leg before fold metrics can be computed; harness consumes per-fold trade artifacts the runner produces) | ✓ |

### 3.6 Financing-overlay dependency

| candidate | financing matters? | depends on MODELED? | ESTIMATED/STRESS sufficient? |
|---|:---:|:---:|:---:|
| C2 | **yes — financing is the candidate's primary edge** | **yes** for a defensible headline number | no — without MODELED, the result is synthetic and the candidate is structurally blocked from approval |
| **C3** | yes (per-trade carry incurred on held-overnight positions; regime-conditional holding period) | no | **yes** (conservative-stress is a valid posture) |
| C4 | yes (straddle's losing leg is closed bar 2; winning leg may hold longer) | no | yes (conservative-stress is a valid posture) |

### 3.7 Portfolio-risk implications

| candidate | concurrency? | per-pair exposure pattern | new risk-engine rules? |
|---|---|---|:---:|
| C2 | up to 3 positions (max_concurrent_positions = 3 per prior sketch) | concentrated in carry-positive pairs | yes — `max_open_positions` must allow > 1 |
| **C3** | **1 (single-instrument single-position)** | **regime-gated; even distribution when regime is on; some pairs may be quieter** | **none** |
| C4 | 2 per pair (paired straddle) | concentrated per pair on entry bars | **yes** — `max_positions_per_instrument` must allow 2 |

### 3.8 Independent-verifier feasibility

| candidate | verifier extension needed? | scope of extension | priority |
|---|:---:|---|---|
| C2 | yes | new rules.py path: financing-gate evaluator + slow-trend confirmation; new bespoke reference loader | low (paper-only after MODELED) |
| **C3** | **yes** | **new rules.py path: D1AGG-from-H4 aggregator + ATR-percentile rolling-window + regime-conditional H4 entry; new bespoke reference loader** | **medium** (only required for paper-promotion; not required for REJECT verdict) |
| C4 | yes | new rules.py path: ATR-jump detection + paired-entry semantics + per-leg PnL; **non-trivial** | high (paired-entry is structurally new) |

### 3.9 Overfitting risk per candidate

| candidate | overfit risk | dominant risk pattern |
|---|---|---|
| C2 | **low** | The edge is structural (carry) not pattern-fitted. Risk is "carry-regime regime change" (e.g. central-bank rate cuts), which is documented as a known limitation, not curve-fitting. |
| **C3** | **medium** | "Trend-on-H4 with a daily-vol gate" framing is structurally close to TF; the gate's parameter choice (percentile threshold, lookback window) has multiple defensible values, opening the door to implicit search. **Phase 3 feasibility deep dive will codify exactly which gate values are pre-committed and forbidden from tuning.** The mitigation is: pre-commit one specific percentile threshold + lookback before any code; runner rejects any deviation. |
| C4 | medium | The "vol-jump" definition (ATR ≥ X percentile of last N bars) has multiple defensible parameter choices; the paired-leg accounting opens new tuning surfaces. |

### 3.10 Expected diagnostic value

| candidate | diagnostic value | rationale |
|---|---|---|
| C2 | high *if MODELED becomes available* | The first carry-aware result would tell the project whether *any* edge survives the H4-majors cost drag after carry. |
| **C3** | **high** | Tells the project whether trend persistence is conditional on macro vol regime. A REJECT under C3 sharpens the "TF on H4 majors does not work, even with regime gating" conclusion; a PASS-then-paper would be the first edge case the project has found. Either outcome is informative. |
| C4 | medium | Tells the project whether the non-directional bet survives cost + paired-entry friction. |

### 3.11 Ability to beat the CAMPAIGN_011 null floor

| candidate | plausibility of beating null | rationale |
|---|---|---|
| C2 | **strong** if MODELED carry edge is real (most carry research literature suggests positive long-horizon carry effects exist on majors); structurally a positive-expectancy bet conditional on regime stability | the carry signal is a real economic effect (interest-rate differential); a candidate built on it has a defensible *prior* that it could beat random |
| **C3** | **plausible** if vol-regime conditioning actually correlates with trend persistence; not all economic research backs this but H4-specific evidence is thin enough that a frozen-parameter test is informative | the regime gate is a *filter*, not a new entry — its incremental value depends on whether vol-conditioning improves the base trend signal's PnL distribution |
| C4 | **plausible** if vol-expansion correlates with directional follow-through on average | the paired structure is symmetric, so the candidate doesn't bet on direction — it bets on volatility-expansion magnitude; weakly motivated by economic prior |

### 3.12 Suitability as a real candidate vs diagnostic anchor

All three (C2, C3, C4) are real candidates. None should be
considered as a null-model diagnostic — that role is filled by
CAMPAIGN_011, and adding a second null model would not yield new
pipeline-validation information.

## 4. Blockers by candidate (summary)

| candidate | blockers |
|---|---|
| C2 | **MODELED financing refused** (4-layer block in `src/forex_bot/financing.py` + research/financing); requires separate credentialed-pilot sprint `research-financing-modeled-capture-credentialed-001` to capture ≥ 60 reconciled `DAILY_FINANCING` events. Also requires risk-engine `max_open_positions > 1` configuration (not a code change but a config choice that must be pre-committed). **Long-term blocker; cannot be selected this sprint.** |
| **C3** | **None hard.** D1AGG aggregation infra already exists (`src/forex_bot/backtesting/d1_aggregation.py` with `aggregate_h4_to_d1` + `rollover_safe`); D1AGG can be computed in-process from H4 windowed data without invoking the CAMPAIGN_006 native-D1 blocker. The medium-priority overfitting risk is mitigated by pre-committing the regime gate parameters before any code (Phase 4–5 of this sprint will do this). **C3 is the only candidate this sprint can select.** |
| C4 | **Engine paired-entry support absent** — `BacktestEngine` is single-instrument-single-position; the straddle requires either two simultaneous positions on the same instrument or per-leg modelling as two "instruments". Requires separate engine sprint `infra-engine-paired-entry-support-001`. **Long-term blocker; cannot be selected this sprint.** |

## 5. Overfitting-risks consolidated (Phase 1 guardrails applied)

Cross-referencing
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
§2 + [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
§7:

| candidate | pattern A (test-window leakage) | pattern B (filter-set tuning) | pattern C (parameter range overlap) | pattern D (per-pair tuning) | pattern E (pick-best-fold) | pattern F (gate drift) | pattern G (result-driven family selection) | null-floor tuning risk |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C2 | clean | clean | clean | clean | clean | clean | clean | clean (carry edge is structural; not motivated by CAMPAIGN_011 metrics) |
| **C3** | clean | clean | **caution** — `atr_lookback=14` and `atr_stop_multiple=2.0` are values that overlap with TF / VB / CAMPAIGN_010/011 | clean | clean | clean | clean | clean (selection here on distinctness + null-baseline-plausibility, not on prior-result inversion) |
| C4 | clean | clean | clean | clean | clean | clean | clean | clean |

C3's parameter-overlap caution is **identical to CAMPAIGN_010
and CAMPAIGN_011**'s — `atr_lookback=14` and `atr_stop_multiple=2.0`
are the project's standard exit-sizing constants used by every
H4 candidate. The mitigation is unchanged: pre-commit these
values verbatim from the start; runner rejects any deviation.
The regime gate's percentile threshold + lookback window are
the new tunable surfaces — Phase 3–4 will pre-commit one
specific choice from independent reasoning, not from prior
campaign output.

## 6. Infrastructure gaps (consolidated)

| infrastructure | C2 needs | C3 needs | C4 needs |
|---|:---:|:---:|:---:|
| MODELED financing | **yes (BLOCKER)** | no | no |
| Engine paired-entry support | no | no | **yes (BLOCKER)** |
| D1AGG aggregator | no | no (already exists; usable in-process from `forex_bot.backtesting.d1_aggregation.aggregate_h4_to_d1`) | no |
| Walk-forward harness | no (already exists; same as CAMPAIGN_010/011) | **no (already exists)** | no (already exists; per-leg adapter is the campaign sprint's job) |
| Financing calculator | no (already exists) | **no (already exists)** | no (already exists) |
| Risk diagnostics | no (already exists) | **no (already exists)** | no (already exists) |
| Verifier extension | yes (low priority; post-MODELED) | yes (medium priority; only for paper-promotion) | yes (high priority; paired-entry is non-trivial) |

## 7. Why no new family is proposed

Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§§4 / 5, an addition to the whitelist requires "an explicit,
justified case for an addition". Considered and explicitly
**not** proposed:

| would-be family | why not proposed this sprint |
|---|---|
| Time-of-week seasonal filter | Stand-alone diagnostic only per protocol §4; **as a filter** on a new entry signal it is allowed as secondary, but as a primary edge it has no theoretical mechanism. |
| News-window avoidance | Disallowed per protocol §5 (no reliable historical event data committed). |
| Multi-pair correlation breakout | Disallowed per protocol §5 (multi-asset family without a separate data-foundation sprint). |
| Multi-instrument basket | Same — multi-asset; also requires engine multi-instrument support. |
| Bollinger-band squeeze breakout | Subsumed by C4 (vol-expansion family); designing two parallel volatility-expansion candidates this sprint would be duplicative. |
| Range-bound oscillator | Subsumed by mean-reversion (REJECTED via CAMPAIGN_008/009). |
| **A new family motivated by CAMPAIGN_011 numbers** | **Disallowed** — pattern G (result-driven family selection) per protocol §12 + Phase 1 §7 null-baseline anti-overfit rule. CAMPAIGN_011 is a measurement instrument, not a feature source. |
| **A second null-model anchor** | No incremental pipeline-validation value beyond CAMPAIGN_011; duplicative diagnostic infrastructure. |

## 8. Recommendation — select C3 as the next preferred real candidate

**Recommendation: select C3 — Daily-ATR-percentile regime
switcher** as the next preferred real candidate, contingent on
Phase 3's feasibility deep dive confirming the D1AGG-based
regime feature is safely computable without lookahead.

### 8.1 Why C3 (not C2 / C4)

| factor | C2 | **C3 (recommended)** | C4 |
|---|:---:|:---:|:---:|
| structurally compatible with engine today | ✓ | **✓** | ✗ |
| no MODELED-financing dependency | ✗ | **✓** | ✓ |
| no engine code change | ✓ | **✓** | ✗ |
| no infrastructure prerequisite sprint | ✗ | **✓** | ✗ |
| can produce a verdict in the next two sprints | no | **yes** | no |
| distinctness from every rejected family | ≥ 6/6 | **≥ 5/6** | ≥ 5/6 |
| plausibility of beating CAMPAIGN_011 null floor | strong (carry-conditional) | **plausible (regime-conditional trend persistence)** | plausible (vol-expansion magnitude) |
| zero parameter-tuning risk | low | **medium (mitigated by Phase 3–4 pre-commit)** | medium |

### 8.2 Why C2 is deferred (not abandoned)

C2 remains a strong candidate, but it cannot be evaluated as a
real (approval-eligible) candidate until MODELED financing is
available. The next-step path for C2 is:

1. `research-financing-modeled-capture-credentialed-001` —
   separately-authorized credentialed practice / live capture
   sprint to collect ≥ 60 reconciled `DAILY_FINANCING` events.
2. Human approval to lift the MODELED slot in
   `src/forex_bot/financing.py`.
3. Then a future
   `research-new-candidate-strategy-discovery-004` sprint can
   re-select C2.

C2 may *also* be evaluated **research-only** (with ESTIMATED
financing) at any time, but the result would be diagnostic only
— it cannot become a paper-promotion candidate without MODELED.

### 8.3 Why C4 is deferred (not abandoned)

C4 requires engine paired-entry semantics. The next-step path
for C4 is:

1. `infra-engine-paired-entry-support-001` — separately-authorized
   engine sprint to add paired-position semantics.
2. `RiskEngine` config / policy change to allow
   `max_positions_per_instrument = 2`.
3. Then a future discovery sprint can re-select C4.

### 8.4 Recommended ordering for future selection rounds

1. **C3 (this sprint's recommendation — CAMPAIGN_012)**
2. C2 (after MODELED financing is available)
3. C4 (after engine paired-entry support is added)

## 9. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011 remains REJECT (null-model anchor)** (untouched).
- **Paper / demo / live remain blocked.**
- No strategy code edited this phase.
- No broker / OANDA call.
- No `.env` read; no credential printed.
- No QuantConnect / LEAN.
- No engine-PnL change.
- No `src/forex_bot/financing.py` edit.
- No new external dependency.

## 10. Cross-links

- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
  (prior shortlist with C1–C5)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)
  (prior reassessment under 5-rejected baseline)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
  (this sprint's binding null-baseline reference)
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §§3 / 4 / 5 / 12
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`D1_AGGREGATION_DESIGN.md`](D1_AGGREGATION_DESIGN.md)
- [`src/forex_bot/backtesting/d1_aggregation.py`](../../src/forex_bot/backtesting/d1_aggregation.py)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
