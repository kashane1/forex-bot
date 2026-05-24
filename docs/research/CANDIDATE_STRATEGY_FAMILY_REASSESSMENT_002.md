# Candidate Strategy Family Reassessment (Sprint 002)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-002`
`strategy_evidence: false`

Phase 2 reassessment of the prior shortlist's remaining
candidates (C2 — C5) under the expanded rejected-family baseline
that now includes CAMPAIGN_010 (`session_breakout 0.1.0-c010`).
**This document does not approve any strategy.** It records the
scored comparison, the blockers, the overfitting risks, the
infrastructure gaps, and the recommended next-preferred candidate
for Phase 3's selection.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## 1. The expanded rejected baseline (now 5 families)

Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§3 + [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
§1, the 5 rejected families against which every new candidate
must score ≥ 3 of 6 distinctness:

- **TF** — `trend_following 0.1.0` (CAMPAIGN_002) + ADX-gated
  variant (CAMPAIGN_003).
- **VB** — `volatility_breakout 0.1.0-c004` (CAMPAIGN_004).
- **PB** — `pullback_continuation` (CAMPAIGN_007).
- **MR** — `mean_reversion 0.1.0-c008` / `0.2.0-c009`.
- **SB** — `session_breakout 0.1.0-c010` (CAMPAIGN_010). **NEW.**

The 6 distinctness dimensions (unchanged from prior protocol):

| # | dimension |
|---:|---|
| 1 | theoretical bucket |
| 2 | primary entry signal |
| 3 | primary exit signal |
| 4 | timeframe / universe |
| 5 | data inputs |
| 6 | failure-mode hypothesis |

## 2. The candidate roster (recap from prior shortlist)

Per
[`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
§2, the four remaining candidates after C1's rejection:

| # | candidate name | category | prior status |
|---:|---|---|---|
| ~~C1~~ | ~~Asian-range / London-open session breakout~~ | ~~Session-of-day breakout~~ | **REJECTED (CAMPAIGN_010)** — out of consideration |
| C2 | Carry-aware long-only overlay | Carry-aware position overlay | runner-up (blocked on MODELED) |
| C3 | Daily-ATR-percentile regime switcher | Volatility-regime switching | candidate |
| C4 | Volatility-expansion non-directional straddle | Volatility-regime expansion | candidate |
| C5 | H4 random-entry diagnostic anchor | Baseline / null model | **anchor (NOT a paper candidate)** |

No new family is proposed in this reassessment — see §7 for the
rationale.

## 3. Scored comparison table (this sprint's reassessment)

The table re-scores each candidate's distinctness against **all 5**
rejected families (TF, VB, PB, MR, **SB-new**), plus each
candidate's status on every blocker that surfaced in the prior
sprints' work.

### 3.1 Distinctness scoring (≥ 3 of 6 required vs every rejected family)

| candidate | vs TF | vs VB | vs PB | vs MR | vs **SB (new)** | min score | clears 3-of-6 vs every family? |
|---|---:|---:|---:|---:|---:|---:|:---:|
| C2 — carry overlay | 6 / 6 | 6 / 6 | 6 / 6 | 6 / 6 | **6 / 6** | 6 | ✓ |
| C3 — daily-ATR percentile regime switcher | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 | **5 / 6** | 5 | ✓ |
| C4 — volatility-expansion straddle | 5 / 6 | 5 / 6 | 5 / 6 | 5 / 6 | **5 / 6** | 5 | ✓ |
| C5 — random-entry diagnostic anchor | n/a (null) | n/a | n/a | n/a | **n/a** | n/a | n/a — null model exempt from the rubric |

#### 3.1.1 C2 vs SB (new) detail

| dim | C2 (carry overlay) | SB (session_breakout) | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | carry / cost of capital | liquidity-flow event timing | ✓ |
| 2 entry signal | financing-rate gate + slow trend | London-close vs prior Asian-bar high/low | ✓ |
| 3 exit signal | held until carry flips | ATR stop + 6-bar time stop | ✓ |
| 4 timeframe / universe | D1 (regime) / H4 (entry); long-only subset | H4 throughout; symmetric long/short | ✓ |
| 5 data inputs | financing rates + D1 EMA + price | price + bar-of-day metadata | ✓ |
| 6 failure-mode hypothesis | "no prior family considered carry as an entry input" | "no prior family used session-of-day liquidity as an entry input" | ✓ |

**Score: 6 / 6.** C2 remains maximally distinct from SB.

#### 3.1.2 C3 vs SB (new) detail

| dim | C3 (regime switcher) | SB (session_breakout) | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | regime-switching / volatility-conditional trend | liquidity-flow event | ✓ |
| 2 entry signal | prior-H4 high/low close, gated by daily ATR percentile | London-close vs prior Asian-bar high/low | ✓ (different gate; different reference bar) |
| 3 exit signal | ATR stop + time stop | ATR stop + 6-bar time stop | ≈ (both ATR-stop families; not distinctly different) |
| 4 timeframe / universe | D1 (regime gate) / H4 (entry) | H4 throughout | ✓ |
| 5 data inputs | daily ATR percentile + H4 high/low | bar-of-day metadata + H4 high/low | ✓ |
| 6 failure-mode hypothesis | "trend persistence is regime-conditional" | "London-open continuation" | ✓ |

**Score: 5 / 6.** Clears the threshold; the only ≈ is the
exit-signal flavour (both use ATR-multiple stops, which is the
default exit logic for almost every H4 candidate).

#### 3.1.3 C4 vs SB (new) detail

| dim | C4 (vol-expansion straddle) | SB (session_breakout) | distinct? |
|---:|---|---|:---:|
| 1 theoretical bucket | non-directional volatility expansion | directional liquidity-flow continuation | ✓ |
| 2 entry signal | ATR-jump → paired long + short | London-close vs prior Asian-bar high/low | ✓ |
| 3 exit signal | close losing side bar 2 + ATR stop on winning side | ATR stop + time stop | ✓ |
| 4 timeframe / universe | H4 / 7 pairs | H4 / 7 pairs | ≈ |
| 5 data inputs | H4 ATR percentile | bar-of-day + H4 high/low | ✓ |
| 6 failure-mode hypothesis | "we don't predict direction — let the move pick it" | "we predict London-open direction" | ✓ |

**Score: 5 / 6.** Clears the threshold.

#### 3.1.4 C5 — exempt (null model)

C5 is a null model and is not scored under the distinctness
rubric. Per [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST.md)
§7, it exists as a falsifiability anchor against which any
"real" candidate's expectancy is measured.

### 3.2 Implementation complexity

| candidate | new strategy module | new config sub-model | new tests | new scripts | engine work | data work | total complexity |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| C2 | yes | yes | ~30 cases | runner + financing overlay + risk diagnostics | none (single-instrument-per-account works) | none for prices; **YES** for financing (real DAILY_FINANCING capture) | **high** (data work is the blocker) |
| C3 | yes | yes | ~25 cases | runner + financing overlay + risk diagnostics | none (single-instrument H4 entry; D1 ATR derived from H4 internally) | none (D1 ATR aggregation internal; uses existing H4 store) | medium |
| C4 | yes | yes | ~30 cases | runner + financing overlay + risk diagnostics | **YES** — paired-entry semantics; `max_positions_per_instrument = 2` for the straddle; possibly two separate positions per pair | none | **high** (engine work is the blocker) |
| C5 | yes (tiny) | yes (tiny) | ~20 cases | runner + financing overlay + risk diagnostics | none | none | **low** |

### 3.3 Engine compatibility

| candidate | compatible with existing BacktestEngine? | notes |
|---|:---:|---|
| C2 | ✓ | Single-instrument-per-account; needs financing-rate source plumbed in (the calculator exists; the engine just consumes per-fold trade artifacts). |
| C3 | ✓ | Single-instrument; H4 entry; D1 ATR can be aggregated from H4 internally (no D1 backtest semantics involved). |
| C4 | ✗ | Bespoke `BacktestEngine` is single-instrument-single-position. A literal straddle requires either (a) two simultaneous positions on the same instrument or (b) two separate "instrument" instances — both are engine-level changes. |
| C5 | ✓ | Identical engine surface to all prior H4 strategies. |

### 3.4 Data availability

| candidate | local data sufficient? | data work needed | new credentials needed | new external dependency? |
|---|:---:|---|:---:|:---:|
| C2 | **partial** | Real `DAILY_FINANCING` capture from OANDA practice account (separate credentialed-pilot sprint) | yes (practice token, separate sprint) | none |
| C3 | ✓ | None (existing 7-pair H4 store via `data/campaign_002.sqlite3` symlink) | none | none |
| C4 | ✓ | None (existing 7-pair H4 store) | none | none |
| C5 | ✓ | None (existing 7-pair H4 store) | none | none |

### 3.5 Walk-forward harness compatibility

| candidate | rolling-window frozen-parameter walk-forward feasible? | min fold count satisfied? |
|---|:---:|:---:|
| C2 | ≈ (carry is a slow signal; 6-fold rolling on 6-year H4 is structurally fine, but the **effective independent windows** are fewer — carry regimes change slowly) | ✓ |
| C3 | ✓ (same 8-fold structure as CAMPAIGN_010 works; the 60-bar daily-ATR percentile lookback is within fold) | ✓ |
| C4 | ≈ (straddle accounting must be reconciled per-leg before fold metrics can be computed; harness consumes per-fold trade artifacts the runner produces) | ✓ |
| C5 | ✓ (same structure) | ✓ |

### 3.6 Financing-overlay dependency

| candidate | financing matters? | depends on MODELED? | ESTIMATED/STRESS sufficient? |
|---|:---:|:---:|:---:|
| C2 | **yes — financing is the candidate's primary edge** | **yes** for a defensible headline number | no — without MODELED, the result is synthetic and the candidate is structurally blocked from approval |
| C3 | yes (per-trade carry incurred on held-overnight positions) | no | yes (conservative-stress is a valid posture) |
| C4 | yes (straddle's losing leg is closed bar 2; winning leg may hold longer) | no | yes (conservative-stress is a valid posture) |
| C5 | yes (random-entry holds for a fixed bar count; rollover incurred deterministically by frequency) | no | yes (conservative-stress is a valid posture) |

### 3.7 Portfolio-risk implications

| candidate | concurrency? | per-pair exposure pattern | new risk-engine rules? |
|---|---|---|:---:|
| C2 | up to 3 positions (max_concurrent_positions = 3 per prior sketch) | concentrated in carry-positive pairs | yes — `max_open_positions` must allow > 1 |
| C3 | 1 (single-instrument single-position) | even across the 7 pairs when regime is on | none |
| C4 | 2 per pair (paired straddle) | concentrated per pair on entry bars | **yes** — `max_positions_per_instrument` must allow 2 |
| C5 | 1 | random across the 7 pairs | none |

### 3.8 Independent-verifier feasibility

| candidate | verifier extension needed? | scope of extension | priority |
|---|:---:|---|---|
| C2 | yes | new rules.py path: financing-gate evaluator + slow-trend confirmation; new bespoke reference loader | low (paper-only after MODELED) |
| C3 | yes | new rules.py path: D1 ATR percentile + prior-H4 high/low entry; new bespoke reference loader | medium |
| C4 | yes | new rules.py path: ATR-jump detection + paired-entry semantics + per-leg PnL; **non-trivial** | high (paired-entry is structurally new) |
| C5 | yes (tiny) | random-entry under the same engine gates; reusable as a comparison anchor for every future candidate | **low and reusable** |

### 3.9 Overfitting risk per candidate

| candidate | overfit risk | dominant risk pattern |
|---|---|---|
| C2 | low | The edge is structural (carry) not pattern-fitted. Risk is "carry-regime regime change" (e.g. central-bank rate cuts), which is documented as a known limitation, not curve-fitting. |
| C3 | **medium-high** | "Adjacent to CAMPAIGN_002 in spirit" (per prior shortlist §5.3). The "trend on H4 with a daily-vol gate" framing is structurally close to TF; the gate's parameter choice (top quartile, 60-bar lookback) has multiple defensible values, opening the door to implicit search. |
| C4 | medium | The "vol-jump" definition (ATR ≥ X percentile of last N bars) has multiple defensible parameter choices; the paired-leg accounting opens new tuning surfaces. |
| C5 | **none** | Random has no parameters except seed; the *only* tuning is the seed count for the statistical estimate, which is set in advance. |

### 3.10 Expected diagnostic value

| candidate | diagnostic value | rationale |
|---|---|---|
| C2 | high *if MODELED becomes available* | The first carry-aware result would tell the project whether *any* edge survives the H4-majors cost drag after carry. |
| C3 | medium | Tells the project whether trend persistence is conditional on macro vol regime. A negative result tightens the "TF on H4 majors does not work" conclusion. |
| C4 | medium | Tells the project whether the non-directional bet survives cost + paired-entry friction. |
| C5 | **very high** | Tells the project (a) what zero-edge looks like under the *full* walk-forward + financing + risk-diagnostic pipeline (CAMPAIGN_005 was pre-walk-forward, pre-financing-overlay, pre-explicit-risk-diagnostics), (b) whether the gates correctly REJECT a known-zero-edge strategy, and (c) per-fold + aggregate random expectancy values that any future candidate must beat by a margin. Establishes the *falsifiability bar* for every subsequent C2 / C3 / C4 / new-family work. |

### 3.11 Paper-candidate suitability

| candidate | could ever become a paper candidate? | gate to that path |
|---|:---:|---|
| C2 | yes (long-term) | requires MODELED financing (separate credentialed-pilot sprint) + full six-evidence ladder + human approval |
| C3 | yes | requires the full six-evidence ladder + human approval |
| C4 | yes | requires engine paired-entry support (separate engine sprint) + full six-evidence ladder + human approval |
| C5 | **no, by design** | C5 is a null model — its purpose is to be REJECTED so it can serve as the falsifiability anchor. It would never be added to `configs/approved_strategies.yaml`. |

## 4. Blockers by candidate (summary)

| candidate | blockers |
|---|---|
| C2 | **MODELED financing refused** (4-layer block in `src/forex_bot/financing.py` + research/financing); requires separate credentialed-pilot sprint to capture ≥ 60 reconciled `DAILY_FINANCING` events. Also requires risk-engine `max_open_positions` > 1 configuration (not a code change but a config choice that must be pre-committed). |
| C3 | **D1 aggregation closure** — `src/forex_bot/backtesting/d1_aggregation.py` exists but the prior shortlist marked it "partially in place". An evidence sprint would need to verify the D1 ATR percentile path is usable from within an H4-driven strategy without requiring D1-bar backtest semantics (CAMPAIGN_006 blocker). The aggregation can be implemented inside the strategy module itself if necessary (compute D1 OHLC from H4 windowed on UTC midnight or 17:00-NY rollover). |
| C4 | **Engine paired-entry support** — current `BacktestEngine` is single-instrument-single-position; the straddle requires either two simultaneous positions on the same instrument (engine change) or per-leg modelling as two "instruments" (a hack). |
| C5 | **None.** Zero blockers; runs cleanly against today's engine + harness + financing + risk. |

## 5. Overfitting risks (consolidated; applies the Phase 1 guardrails)

Cross-referencing [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
§2:

| candidate | pattern A (test-window leakage) | pattern B (filter-set tuning) | pattern C (parameter range overlap) | pattern D (per-pair tuning) | pattern E (pick-best-fold) | pattern F (gate drift) | pattern G (result-driven family selection) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C2 | clean | clean | clean | clean | clean | clean | clean — selection here on distinctness, not on prior-result inversion |
| C3 | clean | clean | **caution** — `atr_lookback = 14`, `atr_stop_multiple = 2.0` are values that overlap with TF / VB / CAMPAIGN_010; the daily-percentile gate is the candidate's primary edge and must be the variable under test, not the ATR | clean | clean | clean | clean |
| C4 | clean | clean | clean | clean | clean | clean | clean |
| C5 | n/a | n/a | n/a | n/a | n/a | n/a | clean (anchor) |

No candidate trips a §12 disqualifier outright. C3 has a soft
warning on §2.C (parameter range overlap) that the Phase 4
design must explicitly justify.

## 6. Infrastructure gaps (consolidated)

| infrastructure | C2 needs | C3 needs | C4 needs | C5 needs |
|---|:---:|:---:|:---:|:---:|
| MODELED financing | **yes (blocker)** | no | no | no |
| D1 aggregation in-strategy | no | yes (small — H4 → D1 OHLC reduction) | no | no |
| Engine paired-entry | no | no | **yes (blocker)** | no |
| New broker / data fetch | yes (credentialed pilot — separate sprint) | no | no | no |
| Verifier extension | yes (low priority) | yes (medium) | yes (high — paired-entry is non-trivial) | yes (tiny — reusable) |
| Risk-engine `max_open_positions > 1` config | yes | no | yes | no |

## 7. Why no new family is proposed in this sprint

Per [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§§4 / 5, an addition to the whitelist requires "an explicit,
justified case for an addition". Considered and explicitly
**not** proposed:

| would-be family | why not proposed this sprint |
|---|---|
| Time-of-week seasonal filter (e.g. avoid Friday) | Stand-alone diagnostic per §4; **as a filter** on a new entry signal it is allowed as secondary, but as a primary edge it has no theoretical mechanism. |
| News-window avoidance | Disallowed per §5 (no reliable historical event data committed). |
| Multi-pair correlation breakout | Disallowed per §5 (multi-asset family without a separate data-foundation sprint). |
| Multi-instrument basket | Same — multi-asset; also requires engine multi-instrument support. |
| Bollinger-band squeeze breakout | Subsumed by C4 (vol-expansion family); designing two parallel volatility-expansion candidates this sprint would be duplicative. |
| Range-bound oscillator | Subsumed by mean-reversion (REJECTED via CAMPAIGN_008/009). |
| Selection-after-results new family motivated by CAMPAIGN_010 patterns | **Disallowed** — pattern G (result-driven family selection) per §12. |

The protocol's existing whitelist (carry overlay; session
breakout; volatility regime; time-of-week filter; mean reversion;
baseline / null model) covers every "clean" category. C1 was
the preferred candidate and is now rejected; the remaining
candidates C2, C3, C4 represent the three other distinct
mechanism families on the whitelist. C5 is the null-model anchor.

## 8. Recommendation — select C5 as the next preferred candidate

**Recommendation: select C5 — H4 random-entry diagnostic anchor**
as the next preferred candidate, with the explicit framing that
it is a **diagnostic anchor, not a paper candidate**, and that
its purpose is to validate the full evidence pipeline and
establish the falsifiability bar for every subsequent C2 / C3 / C4
/ new-family work.

### 8.1 Why C5 (not C2 / C3 / C4)

| factor | C2 | C3 | C4 | **C5 (recommended)** |
|---|:---:|:---:|:---:|:---:|
| structurally compatible with engine today | ✓ | ✓ | ✗ | ✓ |
| no MODELED-financing dependency | ✗ | ✓ | ✓ | ✓ |
| no D1-aggregation work | ✓ | ✗ | ✓ | ✓ |
| no result-driven selection risk | ✓ | ⚠ (parameter overlap warning) | ✓ | ✓ |
| can be approved (long-term) | yes | yes | yes | no (by design) |
| zero parameters to tune | ✗ | ✗ | ✗ | **✓** |
| zero blockers (anything) | ✗ (MODELED) | ⚠ (D1 agg) | ✗ (engine) | ✓ |
| validates the evidence pipeline as designed | weak | medium | medium | **strong** |
| establishes a per-fold + aggregate falsifiability bar that *every* future candidate must beat | no | no | no | **yes** |
| recoverable from a wrong choice (cost of being wrong is low) | medium (sprint blocked on MODELED for a long time) | medium | high (engine sprint is a meaningful commitment) | **low (a clean REJECT is the *expected* output)** |

### 8.2 The protocol explicitly authorizes C5 as a candidate role

Per
[`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
§4 (whitelisted families):

> **Baseline / null model** — e.g. a buy-and-hold, a coin-flip
> entry on H4 close, an always-flat baseline. Allowed only as a
> diagnostic comparison anchor for the preferred candidate;
> cannot itself be the "preferred candidate" for paper promotion.

The user's Phase 3 instruction in this sprint's task list
explicitly allows the null-model choice:

> Choose exactly one next preferred candidate family for a
> future scaffold sprint, **or explicitly select a
> diagnostic/null candidate if that is the highest-value next
> step.**

After three consecutive directional REJECTs (CAMPAIGN_002,
CAMPAIGN_009, CAMPAIGN_010), validating the evidence pipeline is
the highest-value next step — and C5 is the way to do that.

### 8.3 What C5 achieves that CAMPAIGN_005 did not

CAMPAIGN_005 already exists as a benchmark report
([`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)).
It reported random-entry expectancy of −0.095 R on 6 majors
(NZD_USD excluded) under a single-window, fixed 30-bar hold, 20
seeds, with bid/ask + base costs.

CAMPAIGN_011 (the proposed C5 implementation) would:

| dimension | CAMPAIGN_005 | CAMPAIGN_011 (proposed) |
|---|---|---|
| protocol | single-window benchmark | **rolling walk-forward (frozen, 540/180/180/180 days, 8 folds)** |
| universe | 6 majors | **7 pairs (matches CAMPAIGN_010)** |
| financing overlay | not applied | **ESTIMATED + conservative stress** |
| risk diagnostics | not applied | **full RiskEngine rejection table + concurrency + exposure trace** |
| evidence-pipeline coverage | trades + per-pair expectancy only | **full `WalkForwardResults` + gate vector + verdict classification** |
| comparison value | aggregate-only random expectancy | **per-fold + aggregate + per-pair random expectancies under the same gates used by CAMPAIGN_010 and any future candidate** |
| seed determinism | single seed per run | **frozen seed sequence committed in the pre-commit; deterministic across runs** |
| repeatability | one-off | **re-runnable with deterministic outputs for verifier corroboration** |

CAMPAIGN_011 is therefore a strictly stronger anchor than
CAMPAIGN_005 because the latter pre-dates the walk-forward
harness + financing calculator + risk-diagnostic conventions.

### 8.4 Why C2 / C3 / C4 stay on the shortlist (deferred, not rejected)

| candidate | next-step needed before consideration |
|---|---|
| C2 | (a) `research-financing-modeled-capture-credentialed-001` — separately-authorized credentialed practice / live capture sprint to collect real `DAILY_FINANCING` events; **and** (b) `src/forex_bot/financing.py` MODELED slot lifted under human approval. Only then can C2 be considered as the next preferred candidate. |
| C3 | (a) verify `src/forex_bot/backtesting/d1_aggregation.py` is closed (or accept that the D1 ATR percentile can be computed inside the strategy module from H4 windowed data — Phase 4 of any future C3 sprint would decide); **and** (b) Phase 4's pre-commit must explicitly justify the parameter overlap warning (§5 above). C3 is *not* blocked; it is the strongest "real" candidate among the remaining three. |
| C4 | (a) `infra-engine-paired-entry-support-001` — separately-authorized engine sprint to add paired-position semantics; (b) `RiskEngine` config / policy change to allow `max_positions_per_instrument = 2`. C4 is paused on engine work. |

After C5's CAMPAIGN_011 establishes the falsifiability bar, the
recommended ordering for future selection rounds is:

1. C5 (this sprint's selection — CAMPAIGN_011)
2. C3 (strongest "real" candidate without infrastructure blockers, subject to Phase 4 design discipline)
3. C2 (after MODELED financing is available)
4. C4 (after engine paired-entry support is added)

## 9. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`** (verified).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
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
- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_PROTOCOL.md)
  §§3 / 4 / 5 / 12
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
  (this sprint's guardrails)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md`](../../backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md)
  (existing single-window random benchmark)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`WALK_FORWARD_HARNESS_STATUS.md`](WALK_FORWARD_HARNESS_STATUS.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md`](FINANCING_OBSERVED_CAPTURE_PILOT_STATUS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FUTURE_RESEARCH_BACKLOG.md`](FUTURE_RESEARCH_BACKLOG.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
