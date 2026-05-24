# Candidate Strategy Family Shortlist (Phase 5)

**Date:** 2026-05-23 · **Branch:** `research-new-candidate-strategy-discovery-005`
`strategy_evidence: false`

Phase 5 deliverable. Proposes a **shortlist of 5 genuinely-new
candidate families** (C7-reaffirmed plus 4 fresh proposals C10–C13)
plus 1 infrastructure-first fallback path. Each candidate satisfies
the [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
§3 "genuinely new" criteria (11 axes including turnover budget + cost
section) against the now-8 rejected baseline (5 prior + CAMPAIGN_011
null + CAMPAIGN_012 real + CAMPAIGN_013 real). **No implementation;
no backtest; no broker call.** Phase 6 selects exactly one.

> No strategy approved. CAMPAIGN_002 / 010 / 011 / 012 / 013 all
> remain REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`.

## 1. Naming convention

Discovery-004's shortlist used C6–C9 (C6 → CAMPAIGN_013 REJECT; C7 / C8 /
C9 retained from that shortlist). I label the four fresh proposals
C10 / C11 / C12 / C13 for traceability. None of these is a tune of
CAMPAIGN_002 / 010 / 011 / 012 / 013. **The CAMPAIGN_NN label space
and the C-candidate label space are independent** — C12 / C13 here
are candidate-shortlist IDs, not CAMPAIGN_012 / CAMPAIGN_013
references.

## 2. Candidate proposals

### 2.1 C7 — Calendar-Event Window Anomaly (CEWA) — REAFFIRMED

| dimension | value |
|---|---|
| hypothesis | Around scheduled high-impact economic events (NFP, FOMC, ECB, BoJ, BoE), USD-pair returns exhibit a **mean-reverting overshoot** in the H4 bars immediately after the event. The hypothesis is that the post-event N-bar window is structurally different from random H4 bars (it carries a footprint of mis-priced surprise) and can be traded *against* the immediate post-event move with an ATR stop. |
| why distinct from CAMPAIGN_002 | not trend-following; not EMA + Donchian; trades **against** the move (counter-trend) only in event windows |
| why distinct from CAMPAIGN_010 | session-agnostic (events span all sessions); not range-breakout |
| why distinct from CAMPAIGN_011 (null) | deterministic event-calendar trigger; no PRNG |
| why distinct from CAMPAIGN_012 | no vol-percentile gate; no close-vs-close trend continuation; signal is event-window-conditional counter-trend |
| **why distinct from CAMPAIGN_013** | **no cross-pair ranking; no cross-sectional FX-rank metric; signal is single-pair event-window-conditional** |
| required data | H4 universe (already in local store) + **calendar feed** (NEW dependency) for event timestamps and impact ranking. The calendar feed is a small committed JSON / CSV fixture of historical event timestamps from public sources (BLS for NFP, FOMC.gov for FOMC, ECB.europa.eu for ECB, BoJ.or.jp for BoJ, BoE for BoE). ~10 KB; one-time committed file; deterministic; no broker call; no real-time fetch |
| required engine support | YES — fits single-instrument single-position invariant; the strategy reads the event-calendar fixture and gates entries on event proximity |
| financing implications | ESTIMATED + conservative stress sufficient; short holding period (≤ 6 H4 bars) means financing is small |
| expected holding period | 2–6 H4 bars post-event |
| walk-forward compatibility | YES (8-fold rolling/frozen plan); the event calendar must be available for every fold's test window |
| null-baseline comparison expectation | must beat CAMPAIGN_011 by ≥ +0.0524 R aggregate expectancy |
| **turnover budget (binding pre-commit if selected)** | **~150–400 trades over 4 years** (derivation: ~30–60 high-impact events per year × 7 pairs × 50 % qualification rate × 4 years; well below CAMPAIGN_011's 1,177 null floor). **Explicitly disqualifies Pattern M (high-frequency H4 firehose) and Pattern V (high-turnover variant of rejected family)** |
| **cost section (Pattern Q binding pre-commit if selected)** | per-trade spread ~0.5–2 bp; per-trade slippage ~0.5–1 bp; per-trade financing < 1 bp (short hold); per-trade gross expectancy must be ≥ 5 bp net of all costs; pre-declared net expectancy floor ≥ 0.05 R after costs |
| risk diagnostics required | event-class clustering (NFP vs FOMC vs ECB vs BoJ vs BoE); per-pair event-sensitivity; entry-window concentration; per-event-class pre vs post |
| overfitting hazards | **event-set selection** (which events to trade) — must be pre-committed before any backtest fires (e.g. "all FOMC + all NFP + all major ECB days"); event-window-length sweep (forbidden); per-event-class carve-outs forbidden; mid-sprint event-list expansion forbidden |
| immediate blockers | **NEW data dependency** (calendar fixture) — but bounded, one-time, deterministic, broker-free; compiling from public sources is straightforward |
| scaffold complexity | MEDIUM-HIGH — strategy module ~350 LOC; event-calendar loader; ~30 unit tests; fixture file ~10 KB; new no-lookahead invariants for event-time access |

**Distinctness vs each rejected family:** 8 / 8 (no shared mechanism
with CAMPAIGN_002 / 010 / 011 / 012 / 013 / 004 / 007 / 008-009).

### 2.2 C10 — Weekly-Bias H4-Execution (WBH4E)

| dimension | value |
|---|---|
| hypothesis | Use the **completed prior weekly close** to derive a directional bias for each pair (e.g. positive if `close[w-1] > close[w-2] × (1 + threshold)`), then execute **at most one** H4 entry per pair per week at a pre-declared execution time (e.g. first London H4 close of the week). Hypothesis: weekly persistence is a structurally different signal than within-week directional momentum (which CAMPAIGN_002 falsified) because it integrates over 5 trading days of information rather than reacting to within-day noise. |
| why distinct from CAMPAIGN_002 | weekly bias, not H4 momentum; one entry per pair per week (not "as many as the H4 trigger allows") |
| why distinct from CAMPAIGN_010 | not session-windowed within a day; week-anchored |
| why distinct from CAMPAIGN_011 (null) | deterministic from weekly close; no PRNG |
| why distinct from CAMPAIGN_012 | no vol-percentile gate; weekly time scale not within-day |
| **why distinct from CAMPAIGN_013** | **no cross-pair ranking; signal is per-pair weekly bias** |
| required data | H4 universe (already in local store; weekly aggregation is straightforward from H4 closes) — no new fetch; no new fixture |
| required engine support | YES — single-leg single-instrument; the runner gates entry on "is this the first London H4 close of the ISO week?" |
| financing implications | ESTIMATED + conservative stress; weekly hold (~5 trading days) means financing is non-trivial but bounded |
| expected holding period | 1 trading week (5 trading days; ~30 H4 bars; held to weekly close) |
| walk-forward compatibility | YES (8-fold rolling/frozen plan); weekly cadence sits naturally within each fold |
| null-baseline comparison expectation | must beat CAMPAIGN_011 by ≥ +0.0524 R aggregate expectancy |
| **turnover budget (binding if selected)** | **~50–350 trades over 4 years** (derivation: ~50 trading weeks per year × 7 pairs × 50 % qualification rate × 4 years; **well below** CAMPAIGN_011's 1,177 null floor). **Explicitly disqualifies Pattern M and V** |
| **cost section (Pattern Q binding)** | per-trade spread + slippage ~1.5 bp; per-trade financing ~5–10 bp (5-day hold × 1–2 bp/day under stress); per-trade gross expectancy must be ≥ 20 bp net of all costs to clear 0.05 R aggregate |
| risk diagnostics required | per-pair weekly bias frequency; weekly direction distribution; per-week-of-year clustering; long/short imbalance per pair |
| overfitting hazards | **bias-threshold** sweep (forbidden); **execution-time** sweep (forbidden); per-pair / per-week carve-outs forbidden |
| immediate blockers | NONE — fits engine + data + ESTIMATED financing today |
| scaffold complexity | LOW-MEDIUM — strategy module ~200 LOC; weekly aggregation helper (already implicit in the H4 store); ~25 unit tests; no fixture |

**Distinctness vs each rejected family:** 8 / 8.

### 2.3 C11 — Long-Horizon Realized-Vol-Parity Sizing (LHRVPS) — NOT an entry signal

| dimension | value |
|---|---|
| hypothesis | This is **NOT** an entry signal candidate. It is a **position-sizing-only** candidate to be paired with a *separately-justified* entry signal (e.g. C7 or C10). Hypothesis: a static fundamental-bias entry signal sized by realized-vol-parity weights (each pair's notional inversely proportional to its 60-day realized vol) survives the inherited cost model better than uniform sizing because the cost-per-trade is a smaller fraction of the position's expected per-pair move on low-vol pairs |
| why distinct from CAMPAIGN_013 | C13's sizing is uniform per-trade; cross-pair ranking is in the *entry trigger*, not sizing. C11 inverts: ranking-like cross-sectional information is in *sizing*, with the entry trigger separately justified |
| required data | H4 universe (already in local store); realized-vol is computed from completed H4 closes |
| required engine support | LIMITED — current RiskEngine uses fixed `risk_per_trade_pct`; per-pair dynamic sizing would require a new `position_sizer` injection point in the runner (small engine change; not as large as paired-entry support). **This may be an infrastructure prerequisite** |
| financing implications | inherits the underlying entry signal's financing profile |
| expected holding period | inherits the underlying entry signal's holding period |
| walk-forward compatibility | depends on the underlying entry signal; sizing-only candidate evaluable only paired with one |
| null-baseline comparison | not directly comparable; the null baseline is uniform-sized; C11's evaluation must include both uniform-sized and parity-sized variants of the *same* underlying entry signal |
| **turnover budget** | inherits underlying entry signal's count |
| **cost section** | the *thesis* is cost-aware (sizing by realized vol *is* cost-aware); trivially passes Pattern Q |
| risk diagnostics required | per-pair sizing distribution; correlation of sizing weights across pairs; sizing-weight stability over folds |
| overfitting hazards | realized-vol-lookback sweep (forbidden); parity-formula variants (forbidden); pair-only carve-outs forbidden |
| immediate blockers | **engine sizing-injection point is not yet implemented**; this candidate is effectively gated by a small infra sprint OR can be deferred until paired with an entry-signal candidate that justifies the engine change |
| scaffold complexity | NEEDS INFRA — engine sizing injection point + sizing module + test fixtures |

**Distinctness vs each rejected family:** 8 / 8 (it's a different
*role* — sizing — rather than a competing entry signal).

**CAUTION:** C11 is **not a standalone candidate**. It must be paired
with an independently-justified entry signal. Phase 6 should consider
it as a *modifier* if C7 / C10 / C12 is selected and the additional
sizing dimension is judged to be a useful research extension; or
defer entirely.

### 2.4 C12 — Monthly Fundamentals-Spread Rebalance (MFSR)

| dimension | value |
|---|---|
| hypothesis | At each **first H4 bar of the calendar month**, compute a deterministic per-pair fundamental-spread proxy from the **prior month's** closing data (e.g. `close[m-1, month_end] − close[m-2, month_end]` smoothed over 3 months) and take a single position per pair held until the **next first H4 bar of the calendar month** (~21 trading days). Hypothesis: monthly rebalance windows align with macro-data release cycles (Q-end, year-end) and a slow, low-turnover bias-shift survives the inherited cost model |
| why distinct from CAMPAIGN_002 | EMA / Donchian replaced by monthly close differences; entry cadence is 1/month, not H4 |
| why distinct from CAMPAIGN_010 | not session-windowed; not Asian-range |
| why distinct from CAMPAIGN_011 | deterministic from prior monthly closes |
| why distinct from CAMPAIGN_012 | no vol-percentile gate; monthly time scale |
| **why distinct from CAMPAIGN_013** | **no cross-pair ranking; per-pair monthly direction** |
| required data | H4 universe (already in local store; monthly aggregation is straightforward from H4 closes; no new fetch) |
| required engine support | YES — single-leg single-instrument; runner gates entry on "first H4 bar of new calendar month?" |
| financing implications | ESTIMATED + conservative stress; ~21-day hold means **financing is meaningful** (~21 × 1–2 bp/day under stress = 21–42 bp); the cost section must show gross expectancy ≥ ~45 bp to clear |
| expected holding period | 1 calendar month (~21 trading days; ~126 H4 bars; the longest candidate in the shortlist) |
| walk-forward compatibility | YES (8-fold rolling/frozen plan); monthly cadence sits within each fold's ~180-day test window (~6 entries per pair per fold) |
| null-baseline comparison expectation | must beat CAMPAIGN_011 by ≥ +0.0524 R aggregate expectancy |
| **turnover budget (binding if selected)** | **~150–340 trades over 4 years** (derivation: 48 months × 7 pairs × 100 % entry rate = 336 trades; well below CAMPAIGN_011's 1,177 null floor). **Explicitly disqualifies Pattern M and V** |
| **cost section (Pattern Q binding)** | per-trade spread + slippage ~1.5 bp; per-trade financing ~25–45 bp (21-day hold); per-trade gross expectancy must be ≥ 80 bp net of all costs to clear 0.05 R aggregate. **This is a stringent bar; the hypothesis must justify it** |
| risk diagnostics required | per-pair monthly direction frequency; per-month-of-year clustering; long/short imbalance; max drawdown over 21-day hold (single-position duration risk) |
| overfitting hazards | smoothing-window sweep (forbidden); entry-time sweep (forbidden); per-pair carve-outs forbidden; per-month-of-year carve-outs forbidden |
| immediate blockers | NONE — fits engine + data + ESTIMATED financing today; the long hold makes financing more important than short-hold candidates but it remains under the ESTIMATED + conservative-stress regime |
| scaffold complexity | LOW-MEDIUM — strategy module ~200 LOC; monthly aggregation helper; ~25 unit tests; no fixture |

**Distinctness vs each rejected family:** 8 / 8.

### 2.5 C13 — Quarterly Earnings-Season Calendar Filter (QESCF) — NOT recommended

| dimension | value |
|---|---|
| hypothesis | Concentrate H4 mean-reversion entries during US earnings-season windows (Apr / Jul / Oct / Jan first 4 weeks) and avoid them otherwise. Hypothesis: earnings-season FX flow correlates with equity-side rebalancing and produces excess mean-reversion opportunities |
| why this is problematic | This is a **calendar filter on top of CAMPAIGN_008/009 (rejected mean-reversion)** — it stacks rejected mean-reversion with a session-style time filter (Pattern K + Pattern U). The "earnings-season" framing is a thin disguise for "apply rejected mean-reversion when something might happen" |
| why distinct from CAMPAIGN_013 | not cross-pair ranking |
| **disqualifier** | **Pattern U + Pattern K + Pattern G** (rejected-family stack + result-driven calendar carve-out + filter rescue of rejected family) |
| immediate blockers | DISQUALIFIED at shortlist stage |

**Outcome:** **C13 IS DISQUALIFIED.** Listed only to demonstrate that
the discovery process can recognize a disguised rejected-family stack
before scaffolding effort. **Not eligible for Phase 6 selection.**

### 2.6 Infrastructure-first fallback path: infra-A `research-financing-modeled-capture-credentialed-001`

| dimension | value |
|---|---|
| scope | a credentialed pilot to capture real OANDA `DAILY_FINANCING` events under a separately-authorized broker account; populate MODELED fixture set; lift the 4-layer refusal in `src/forex_bot/financing.py` after fixtures match observed events within a documented tolerance |
| why this is the fallback | if Phase 6 judges that no C7 / C10 / C12 candidate is honestly evaluable today, infra-A is the most-impactful next path because it unlocks the entire **carry** strategy family (C2 + future carry candidates) |
| recommendation | **HOLD** — discovery-005 cannot authorize or run infra-A (requires human authorization for credentialed broker access); the recommendation is a *future-sprint* path, not a discovery-005 action |
| value | unlocks C2 (carry overlay) for live promotion + future carry candidates; **does not by itself produce strategy evidence** |

## 3. Disqualifications considered (and applied)

The following candidate families were **considered and disqualified**
during this Phase 5 ideation, per the
[`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md)
§3 criteria + [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md)
§5:

| disqualified family | reason |
|---|---|
| `cross_pair_currency_strength_rotation 0.2.0-c014` with `rank_gap_threshold = 3` | Pattern R — CAMPAIGN_013 retune |
| `cross_pair_currency_strength_rotation_pair_filtered` (USD_JPY only) | Pattern T + Pattern P |
| `cross_pair_currency_strength_rotation_session_filtered` | Pattern U — rejected-family stack (C6 + CAMPAIGN_010) |
| `cross_pair_currency_strength_rotation_inverted` (mean-revert rank) | Pattern V (CAMPAIGN_013 retune via inversion) |
| `regime_switcher_atr_percentile + cross_pair_rank_filter` | Pattern U (CAMPAIGN_012 + CAMPAIGN_013 stack) |
| `random_entry_anchor with entry_probability = 0.10` | Pattern V (CAMPAIGN_011 retune; null model is permanently un-approvable) |
| C2 carry overlay (without infra-A) | gated by MODELED-financing infra unblock; out of scope (deferred per Phase 4) |
| C4 vol-expansion straddle (without infra-B) | gated by paired-entry engine support; out of scope (deferred per Phase 4) |
| C6 cross-pair rotation variants | binding cooldown ≥ 3 sprints per `CAMPAIGN_013_REJECTION_CLOSEOUT.md` §5 |
| Trend-following with momentum filter | Pattern G + Pattern O — CAMPAIGN_002 retune with new knob |
| volatility_breakout 0.2.0 (different ATR window) | CAMPAIGN_004 retune (Pattern G + Pattern V) |
| mean_reversion 0.3.0 (different Bollinger band) | CAMPAIGN_008/009 retune (Pattern G + Pattern V) |
| session_breakout 0.2.0 (Tokyo + NY-overlap window) | CAMPAIGN_010 retune (Pattern G + Pattern V) |
| pullback_continuation 0.2.0 (different lookback) | CAMPAIGN_007 retune (Pattern G + Pattern V) |
| weighted-pair-vote ensemble of rejected strategies | rejected-family stack (Pattern K + Pattern U) |
| **C13 QESCF** | Pattern U + Pattern K + Pattern G (rejected-family stack disguised as calendar filter) |
| "high-frequency M30 momentum scalp" | Pattern M (high-frequency firehose; expected > 20,000 trades/4y) + Pattern V (M30 trend = CAMPAIGN_002 lineage at faster timeframe) |
| "all-pair simultaneous entry on broad H4 signal" | Pattern N (broad simultaneous multi-pair without portfolio-level edge proof) |

## 4. Shortlist summary

| candidate | name | distinctness | turnover | infra needed | complexity | recommendation |
|---|---|:---:|---|---|---|---|
| **C7** | Calendar-Event Window Anomaly (CEWA) | 8/8 | LOW (~150–400 trades/4y) | one-time small calendar fixture (broker-free) | MEDIUM-HIGH | **strong — LEAD** |
| **C10** | Weekly-Bias H4-Execution (WBH4E) | 8/8 | LOWEST (~50–350 trades/4y) | NONE | LOW-MEDIUM | **strong — runner-up** |
| **C11** | Long-Horizon Realized-Vol-Parity Sizing (LHRVPS) | n/a (sizing, not entry) | inherits | engine sizing-injection point | NEEDS INFRA | **defer — modifier only, requires entry candidate paired** |
| **C12** | Monthly Fundamentals-Spread Rebalance (MFSR) | 8/8 | LOW (~150–340 trades/4y) | NONE | LOW-MEDIUM | **strong — long-hold variant; financing burden** |
| **C13** | Quarterly Earnings-Season Calendar Filter (QESCF) | n/a | n/a | n/a | n/a | **DISQUALIFIED — rejected-family stack** |
| (infra fallback) | infra-A MODELED financing capture | n/a | n/a | (this IS the infra) | medium | **HOLD — requires human authorization** |

## 5. Recommendation to Phase 6

**Recommend selecting one of: C7 (CEWA) or C10 (WBH4E).**

- **C7** is the cleanest distinct mechanism (event-window anomaly;
  fundamentally novel for this repo; explicitly low turnover; new
  data dependency is bounded and broker-free).
- **C10** is the lowest-blocker candidate (zero new dependencies;
  weekly cadence is a fresh time scale; turnover is lowest of all
  shortlist candidates).
- **C12** is the long-hold variant (lowest-frequency entry); its
  financing burden is higher than C7/C10 but it is a structurally
  different time scale.
- **C11** is a modifier, not a standalone — should be considered
  *after* C7 / C10 / C12 is selected, and only if Phase 6 judges
  pairing with a sizing dimension valuable.
- **C13** is disqualified.

**Phase 6 picks one** between C7 and C10 (or, if Phase 6 judges that
neither is ready, falls back to infra-A as the next-sprint
recommendation).

**Strong preference for C7** because:

- Its hypothesis is **economically grounded** (post-event mis-priced-
  surprise mean reversion is a well-documented phenomenon in FX
  literature).
- The new calendar fixture is **a small one-time commit** and adds a
  reusable data primitive (future event-window candidates can share
  it).
- C7's defense against turnover-amplification is **structural** (the
  event set is finite per year, not threshold-tuned).
- C7's per-pair, per-event-class diagnostic surface is rich (NFP vs
  FOMC vs ECB vs BoJ vs BoE × 7 pairs) — even a REJECT verdict
  produces high-information evidence.

**C10 as the runner-up** because:

- Zero new dependencies.
- Lowest turnover budget (~50–350 trades / 4 y).
- Weekly cadence is **the only candidate not at the H4 time scale**
  for entry — fundamentally different signal class.

## 6. Safety state (unchanged)

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

## 7. Cross-links

- [`NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md`](NEW_CANDIDATE_STRATEGY_DISCOVERY_005_PLAN.md) (Phase 0)
- [`CAMPAIGN_013_REJECTION_CLOSEOUT.md`](CAMPAIGN_013_REJECTION_CLOSEOUT.md) (Phase 1)
- [`TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md`](TURNOVER_AMPLIFICATION_ANTI_PATTERN_005.md) (Phase 2; binding turnover guardrail)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS_005_ADDENDUM.md) (Phase 3; Patterns R–W)
- [`NEXT_DIRECTION_REASSESSMENT_005.md`](NEXT_DIRECTION_REASSESSMENT_005.md) (Phase 4; reassessment recommending C7+C10+ family)
- [`CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md`](CANDIDATE_STRATEGY_FAMILY_SHORTLIST_004.md) (predecessor shortlist; sources for C7 reaffirmation)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md) (binding null baseline; meaningful-improvement margins)
- [`NEXT_PREFERRED_DIRECTION_005.md`](NEXT_PREFERRED_DIRECTION_005.md) (Phase 6 — to be written)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
