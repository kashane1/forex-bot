# Candidate Strategy Family Shortlist (Phase 4)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-004`
`strategy_evidence: false`

Phase 4 deliverable. Proposes a **shortlist of 4 genuinely-new
candidate families** ("C6", "C7", "C8", "C9") that each satisfy the
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
§3 "genuinely new" criteria after the now-7 rejected baseline (5
prior + CAMPAIGN_011 null + CAMPAIGN_012 real). **No implementation;
no backtest; no broker call.** Phase 5 selects exactly one.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 all remain
> REJECT. `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Naming convention

The next candidate IDs after the rejected C2–C5 deferrals would
naturally be C6+. I label the four new proposals C6 / C7 / C8 / C9
for traceability with the prior C-numbering. None of these is a tune
of CAMPAIGN_002 / 010 / 011 / 012.

## 2. Candidate proposals

### 2.1 C6 — Cross-Pair Currency Strength Rotation (CPCSR)

| dimension | value |
|---|---|
| hypothesis | The G7 USD-denominated H4 universe contains 4 USD-base pairs (EUR_USD, GBP_USD, AUD_USD, NZD_USD) and 3 USD-quote pairs (USD_JPY, USD_CAD, USD_CHF). Compute a *rolling currency-strength rank* by aggregating each currency's H4 close-to-close returns over a fixed window across the pairs where it appears, then trade a single H4 bar against the *weakest-relative* currency (long the strongest, short the weakest). Hypothesis: structural relative-strength persistence is independent of any single-pair vol-percentile gate, and the cost model on H4 is survivable when the signal is genuinely cross-pair. |
| why distinct from CAMPAIGN_002 | not EMA + Donchian; no single-pair trend filter; signal is *cross-pair relative ranking*, not per-pair direction |
| why distinct from CAMPAIGN_010 | no session windows; signal fires any H4 bar where the rank gap exceeds a threshold |
| why distinct from CAMPAIGN_011 (null) | fully deterministic from price; no PRNG; no `master_seed` |
| why distinct from CAMPAIGN_012 | no single-pair vol gate; no close-vs-close trend filter; signal is the *rank delta* between currencies, not a within-pair momentum |
| required data | H4 universe (already in local store; 7 pairs; matches CAMPAIGN_010 / 011 / 012 verbatim) — **no new fetch** |
| required engine support | YES — fits single-instrument single-position invariant **per pair**, but the strategy must orchestrate across pairs in the per-bar tick (the existing per-pair runner pattern handles this naturally — same as CAMPAIGN_011 / 012's loop over pairs) |
| financing implications | ESTIMATED + conservative stress sufficient; rotation may have *carry* implications (e.g. long AUD short JPY is implicitly carry-positive) — the runner must record this in the financing overlay |
| expected holding period | ~6 H4 bars (~1 trading day) — matches CAMPAIGN_010 / 011 / 012 envelope |
| walk-forward compatibility | YES — inherits 8-fold rolling/frozen plan verbatim |
| null-baseline comparison expectation | must beat CAMPAIGN_011's −0.0024 R aggregate expectancy by ≥ +0.0524 R |
| risk diagnostics required | per-pair concentration; cross-pair correlation; rotation frequency (how often does the rank flip?); spread filter (already in RiskEngine) |
| overfitting hazards | **rank-window length** sweep (forbidden); **rank-gap threshold** sweep (forbidden); pair-universe carve-outs (forbidden); session filters added post-hoc (forbidden) |
| immediate blockers | NONE — fits bespoke engine + existing data + ESTIMATED financing |
| scaffold complexity | MEDIUM — adds `CrossPairCurrencyStrengthRotation` class; new config schema; ~30 unit tests; one new pair-rank helper; reuses existing H4 ATR + stop logic |

**Distinctness vs each rejected family:** 6 / 6 (no shared mechanism with CAMPAIGN_002 / 010 / 011 / 012; not a re-parameterization).

### 2.2 C7 — Calendar-Event Window Anomaly (CEWA)

| dimension | value |
|---|---|
| hypothesis | Around scheduled high-impact economic events (NFP, FOMC, ECB, BoJ, BoE), USD-pair returns exhibit a **mean-reverting overshoot** in the H4 bars immediately after the event. The hypothesis is that the post-event N-bar window is structurally different from random H4 bars and can be traded *against* the immediate post-event move with an ATR stop. |
| why distinct from CAMPAIGN_002 | not trend-following; not EMA + Donchian; trades **against** the move (counter-trend) only in event windows |
| why distinct from CAMPAIGN_010 | session-agnostic (events span all sessions); not range-breakout |
| why distinct from CAMPAIGN_011 (null) | deterministic event-calendar trigger; no PRNG |
| why distinct from CAMPAIGN_012 | no vol-percentile gate; no close-vs-close trend continuation; signal is event-window-conditional counter-trend |
| required data | H4 universe (already in local store) + **calendar feed** (NEW dependency) for event timestamps and impact ranking. The calendar feed could be a small committed JSON fixture of historical event timestamps (e.g. from FRED for NFP, FOMC press releases, etc.) — no broker call; no real-time fetch |
| required engine support | YES — fits single-instrument single-position invariant; the strategy reads the event-calendar fixture and gates entries on event proximity |
| financing implications | ESTIMATED + conservative stress sufficient; short holding period (≤ 6 H4 bars) means financing is small |
| expected holding period | 2–6 H4 bars post-event |
| walk-forward compatibility | YES (8-fold rolling/frozen plan); the event calendar must be available for every fold's test window |
| null-baseline comparison expectation | must beat CAMPAIGN_011 by ≥ +0.0524 R aggregate expectancy |
| risk diagnostics required | event-class clustering (NFP vs FOMC vs ECB); per-pair event-sensitivity; entry-window concentration |
| overfitting hazards | **event-set selection** (which events to trade) — must be pre-committed before any backtest fires (e.g. "all FOMC + all NFP + all major ECB days"); event-window-length sweep (forbidden); per-event-class carve-outs forbidden; mid-sprint event-list expansion forbidden |
| immediate blockers | **NEW data dependency** (calendar fixture). Must be a small committed JSON / CSV; no real-time fetch; no broker dependency. Compiling the fixture from public sources (BLS for NFP dates, FOMC.gov for FOMC, ECB.europa.eu for ECB) is straightforward and one-time. |
| scaffold complexity | MEDIUM-HIGH — strategy module ~350 LOC; event-calendar loader; ~30 unit tests; fixture file ~10 KB; new no-lookahead invariants for event-time access |

**Distinctness vs each rejected family:** 6 / 6.

### 2.3 C8 — Multi-Window Volatility-Compression Breakout (MWVCB) — single-leg

| dimension | value |
|---|---|
| hypothesis | When *both* the H4 ATR-14 and the D1AGG ATR-14 contract simultaneously (volatility compression across two timeframes), the next directional break is more likely to persist for several H4 bars. Trade in the direction of the eventual break with an ATR stop. **Single-leg only** — no paired-entry requirement. **Distinct from CAMPAIGN_004** (which used compressed H4 ATR alone with no daily-timeframe confirmation, and from a momentum-direction rather than counter-momentum perspective). |
| why distinct from CAMPAIGN_002 | not EMA / Donchian / trend continuation; entry trigger is volatility-state-conditional |
| why distinct from CAMPAIGN_010 | not session-windowed; not Asian-range breakout |
| why distinct from CAMPAIGN_011 | deterministic vol-compression signal |
| why distinct from CAMPAIGN_012 | the regime concept is **vol compression** (low percentile on TWO timeframes simultaneously), NOT vol expansion (high percentile on ONE); the trigger is the breakout *after* compression, not the trend within HIGH-VOL; this is the **inverse hypothesis** of CAMPAIGN_012 (and Pattern J of the addendum forbids "different cutoff on same metric" — but C8 uses a fundamentally different *condition* (cross-timeframe AND-gate on LOW percentiles → breakout signal), not a within-pair vol-percentile gate). |
| why distinct from CAMPAIGN_004 | CAMPAIGN_004 used H4-only compressed ATR (no daily confirmation) and traded a within-bar breakout in compression. C8 requires *simultaneous* H4 + D1AGG low-percentile (cross-timeframe confirmation), and trades a multi-bar continuation post-break, not a single-bar breakout. |
| required data | H4 universe + D1AGG (synthesized via existing `aggregate_h4_to_d1`) — no new fetch |
| required engine support | YES — single-leg, single-instrument |
| financing implications | ESTIMATED + conservative stress sufficient |
| expected holding period | 3–6 H4 bars (post-break continuation) |
| walk-forward compatibility | YES (inherits 8-fold plan) |
| null-baseline comparison expectation | must beat CAMPAIGN_011 by ≥ +0.0524 R |
| risk diagnostics required | per-pair vol-compression frequency; breakout-success rate; cross-timeframe AND-gate hit rate |
| overfitting hazards | **two percentile thresholds** (H4 + D1AGG) — the AND-gate creates a 2D parameter surface that must be pre-committed; **breakout direction definition** (close vs. high/low) must be pre-committed; ATR stop multiple sweep forbidden |
| immediate blockers | **closeness to CAMPAIGN_004 (rejected)** is the risk — must be carefully separated to demonstrate the cross-timeframe AND-gate is a different mechanism, not a CAMPAIGN_004 retune. Risk it gets disqualified by the §3 "genuinely new" criteria; needs careful Phase 6 justification |
| scaffold complexity | MEDIUM — ~300 LOC; reuses D1AGG infrastructure; ~25 unit tests |

**Distinctness vs each rejected family:** 6 / 6 (vs CAMPAIGN_004 requires the most careful argument — see "immediate blockers"). **CAUTION:** Phase 5 should weigh whether C8 is at meaningful risk of being a CAMPAIGN_004 disguised retune (Pattern G).

### 2.4 C9 — Time-of-Day Cost-Adjusted Mean Reversion on Spreads (TODCAMRS)

| dimension | value |
|---|---|
| hypothesis | The H4 spread varies systematically by time-of-day (Asian thin → wider spreads, London/NY thick → tighter). When the H4 close-to-close move within a tight-spread window exceeds K × prevailing spread, the next 1–2 H4 bars exhibit *mean reversion* toward the mid because the original move was partly a spread-driven artifact. Trade against the move in the immediately-following tight-spread window. |
| why distinct from CAMPAIGN_002 | not trend; explicitly counter-trend; no EMA / Donchian |
| why distinct from CAMPAIGN_010 | trades *against* moves, not breakout direction; does not use Asian-range trigger |
| why distinct from CAMPAIGN_011 | deterministic spread + close trigger |
| why distinct from CAMPAIGN_012 | not a vol-percentile gate; uses **spread-time-of-day** as the gating feature (a different observable) |
| why distinct from CAMPAIGN_008 / 009 (rejected mean-reversion) | the prior MR rejection was for range-bar reversion (continuous Z-score / Bollinger); C9 conditions specifically on **spread-time-of-day artifacts**, not on a price-band statistic. Different mechanism + different trigger condition |
| required data | H4 universe with bid/ask spreads (already in the store) — no new fetch |
| required engine support | YES — single-leg single-instrument |
| financing implications | ESTIMATED + conservative stress sufficient; very short holding |
| expected holding period | 1–2 H4 bars |
| walk-forward compatibility | YES |
| null-baseline comparison expectation | must beat CAMPAIGN_011 by ≥ +0.0524 R |
| risk diagnostics required | spread-bucket clustering of signals; per-pair spread distribution; counter-trend frequency |
| overfitting hazards | **K threshold** sweep (forbidden); **spread-bucket definition** sweep (forbidden); pair carve-outs forbidden; very short holding window makes the strategy susceptible to slippage modeling errors — must demonstrate the slippage model used (the existing `FillModel`) is appropriate |
| immediate blockers | **closeness to CAMPAIGN_008 / 009 (rejected MR)** is the risk — must be carefully separated by mechanism (spread-time-of-day artifact, not range Z-score). Risk it gets disqualified by §3 "genuinely new" criteria |
| scaffold complexity | MEDIUM — ~300 LOC; new spread-time-of-day helper; ~25 unit tests |

**Distinctness vs each rejected family:** 5 / 6 (vs CAMPAIGN_008/009 mean-reversion is the most careful argument — the *mechanism* differs but the *direction* (counter-trend) is the same). **CAUTION:** Phase 5 should weigh whether C9 is at meaningful risk of being a CAMPAIGN_008/009 disguised retune.

## 3. Disqualifications considered (and applied)

The following candidate families were **considered and disqualified**
during this Phase 4 ideation, per the
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
§3 criteria:

| disqualified family | reason |
|---|---|
| regime_switcher_atr_percentile 0.2.0 (threshold 0.80) | Pattern H — CAMPAIGN_012 retune |
| regime_switcher_atr_percentile inverted (trade LOW-VOL) | Pattern J — inversion of falsified gate |
| regime_switcher + London session filter | Pattern K — rejected-family stack (C3 + CAMPAIGN_010) |
| regime_switcher restricted to USD_JPY | Pattern G + L — result-driven pair carve-out |
| daily-range-percentile regime switcher | Pattern J — same regime concept, different metric |
| C2 carry overlay (without infra-A) | gated by MODELED-financing infra unblock; out of scope |
| C4 vol-expansion straddle (without infra-B) | gated by paired-entry engine support; out of scope |
| trend_following with momentum filter | Pattern G — CAMPAIGN_002 retune with new knob |
| volatility_breakout 0.2.0 (different ATR window) | CAMPAIGN_004 retune (Pattern G + Pattern I-like) |
| mean_reversion 0.3.0 (different Bollinger band) | CAMPAIGN_008/009 retune (Pattern G + Pattern I-like) |
| session_breakout 0.2.0 (Tokyo + NY-overlap window) | CAMPAIGN_010 retune (Pattern G + Pattern H-like) |
| pullback_continuation 0.2.0 (different lookback) | CAMPAIGN_007 retune |
| weighted-pair-vote ensemble of rejected strategies | rejected-family stack |

## 4. Shortlist summary

| candidate | name | distinctness | blockers | complexity | recommendation |
|---|---|:---:|---|---|---|
| **C6** | Cross-Pair Currency Strength Rotation | 6/6 | NONE | MEDIUM | **strong** — fits engine + data + financing today |
| **C7** | Calendar-Event Window Anomaly | 6/6 | NEW data dep (event calendar fixture) | MEDIUM-HIGH | **strong** — distinct mechanism; calendar fixture is one-time small commit |
| **C8** | Multi-Window Volatility-Compression Breakout | 6/6 | CAMPAIGN_004 proximity risk | MEDIUM | **medium** — needs careful Phase 6 justification vs CAMPAIGN_004 |
| **C9** | Time-of-Day Cost-Adjusted Mean Reversion on Spreads | 5/6 | CAMPAIGN_008/009 proximity risk | MEDIUM | **medium** — needs careful Phase 6 justification vs prior MR rejections |

## 5. Recommendation to Phase 5

**Recommend selecting one of: C6 (CPCSR) or C7 (CEWA).**

- C6 is the cleanest distinct mechanism (cross-pair rotation; no
  shared signal class with any rejected family); zero infrastructure
  or data dependencies; fits the bespoke engine + existing store +
  ESTIMATED financing.
- C7 introduces a new data dependency (event calendar fixture) but
  brings a genuinely different signal class (event-window anomaly)
  that the rejected-family lineage cannot speak to.

**C8 and C9 are deferable** — their proximity to rejected families
makes them harder to defend in Phase 6. Either could become a future
discovery-005 sprint if C6/C7 also rejects.

**Phase 5 will pick one.**

## 6. Safety state (unchanged)

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

## 7. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_004_PLAN.md)
- [`CAMPAIGN_012_REJECTION_CLOSEOUT.md`](CAMPAIGN_012_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_004_ADDENDUM.md)
- [`NEXT_DIRECTION_REASSESSMENT_004.md`](NEXT_DIRECTION_REASSESSMENT_004.md)
- [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_003.md) (predecessor)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
