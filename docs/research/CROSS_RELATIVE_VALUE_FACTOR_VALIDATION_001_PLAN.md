# Cross Relative-Value Factor-Validation 001 — Plan & Baseline Audit

**Branch:** `research-cross-relative-value-factor-validation-001`
**Type:** **factor-validation study only** (multi-market front-gate Stage 1–2).
Not a strategy, campaign, front-gate screen, or train/validation/test exercise.
**Date:** 2026-05-30.
**Freeze status:** intact. `approved: []`; paper/demo/live blocked; no trading-API
calls; read-only research-DB access only.

> **The one question this sprint answers:** does **cross relative-value structure**
> exist in the expanded FX universe, and do **deviations** from it exhibit
> **statistically meaningful reversion**? The objective is **factor existence and
> robustness, NOT tradability** — no cost gate, no signal, no entry/exit.

---

## PHASE 0 — Baseline audit

### 0.1 S2 factor validation (`CURRENCY_STRENGTH_FACTOR_VERDICT`)

S2 (cross-implied currency strength) → **FACTOR_REJECTED**: a real, breadth-diverse
**descriptor** (breadth H2 *passed* — PC1 a haven-vs-risk axis, not a USD artifact)
with **no forward-predictive power** (0/80 null cells cleared, sign-incoherent
everywhere). It **pre-falsified S3** (cross-sectional momentum trades that same
non-predictive ranking). Three directional/cross-sectional families are now null
on this corpus (C1 cost-defeat, C1 cross-replication failure, currency-strength
rejection). The implication carried here: **directional prediction is closed; the
remaining untested mechanism is *reversion of a stable relationship*** — exactly S4.

### 0.2 Cross-universe shortlist (`CROSS_UNIVERSE_FACTOR_SHORTLIST`)

S4 = "economically-motivated, half-life-matched cross RV" (families F15+F18). It is
the **only remaining shortlist family** (S1 spent/failed, S2 rejected, S3
pre-falsified, S5 moot without a generator) and the **only one testing a
fundamentally different mechanism** — *mean-reversion of a stationary relationship*,
not directional/cross-sectional prediction.

### 0.3 S4 rationale

Among crosses pinned by a **triangle** (a cross vs its two USD legs) or sharing a
**leg** (the JPY-cross complex), a relationship can be stationary for a *stated
economic reason*. The thesis: **deviations revert**. It must fix C028's two failure
modes: (i) relationships are **economically motivated and pre-named** — NOT
best-of-N spread mining; (ii) a **half-life diagnostic** is reported as a
precondition, not fitted to a result.

### 0.4 Cross-universe search-space map (`EXPANDED_FX_SEARCH_SPACE_MAP`)

Category **F (triangular / no-arbitrage consistency)** is flagged **NEW** —
structurally impossible on USD-only majors (no cross to close a triangle); **9+
triangles now closable**. The map's own caution is carried in verbatim: *"true
arbitrage is latency/cost-defeated for a retail backtest; the research angle is
consistency-of-drift / reversion, not arb capture."* So this sprint measures
**reversion structure**, and will explicitly separate genuine RV reversion from a
trivial **non-synchronous-quote / no-arb-band microstructure** artifact.

### 0.5 Current instrument universe

15 instruments, 8 currencies, M5 materialized, 2021-05-27 → 2026-05-26 (304k
common aligned bars, established in S2). **Every one of the 8 crosses closes a
triangle** against two USD majors (below). No new data required.

---

## Rationale

Reversion of a *pinned relationship* is mechanistically distinct from everything
the programme has tested. A no-arbitrage triangle (EUR_JPY vs EUR_USD·USD_JPY) or a
shared-leg spread (EUR_JPY vs GBP_JPY) is a **relationship between instruments**,
not a directional bet on one. If its deviations revert beyond a matched null, that
is a genuine factor — *whether or not it is tradable* (cost is out of scope). This
is the cleanest remaining no-new-data test on the corpus.

## Relationships to be constructed (pre-named; full freeze in Phase 1)

**Primary — Triangular consistency residuals (synthetic-vs-observed), 8 crosses.**
For each cross, `residual = ln(observed cross) − ln(implied cross)`, where the
implied cross is built from the two USD legs (no-arbitrage triangle). One per cross
→ 8 pre-named relationships, zero spread search.

**Secondary (Phase-6 robustness, nearby relationship definition) — shared-leg
cointegration spreads** (e.g. EUR_JPY vs GBP_JPY, hedge-ratio β). Pre-named on the
shared-leg economic rationale, not mined.

## Success criteria (FRONT_GATE_CANDIDATE — Phase 7 detail)

All of:
1. **Existence** — deviations (stretched/extreme) are followed by **reversion**
   (signed forward residual move toward zero) coherently across horizons.
2. **Null separation** — reversion exceeds randomized-relationship / shuffled-
   timestamp / matched / unconditional nulls (|matched-Z| ≥ 2) on **multiple**
   relationships, not a single best-of-N.
3. **Robustness** — stable across pairs/years/sessions and nearby normalization /
   relationship / threshold definitions.
4. **Not a trivial artifact** — the reversion is **not** explained purely by
   non-synchronous-quote staleness / the no-arb band (judged via horizon profile,
   half-life, and residual scale vs spread — descriptive).

## Failure criteria

- **FACTOR_REJECTED:** no reversion beyond null, OR reversion is sign-incoherent /
  single-relationship-driven, OR it is entirely a microstructure/no-arb-band
  artifact (instantaneous, sub-spread, vanishes once non-synchronicity is
  accounted for).
- **FACTOR_REAL_BUT_WEAK:** genuine reversion survives the nulls *somewhere
  stable* but is narrow (few relationships / modest Z / partial robustness) or
  confined to the no-arb band — insufficient for a front gate.
- **FACTOR_FRONT_GATE_CANDIDATE:** reversion is real, null-separated, robust, and
  not a trivial artifact → merits a *future* (separate) front-gate screen.

> Tradability is excluded from every branch. Even FRONT_GATE_CANDIDATE earns only
> the *right to be cost-screened later* — the two-/three-leg cost wall (C028's
> other failure mode) is the *future* gate's job, not this sprint's.

## Distinction from previous families

| Family | Mechanism | Verdict |
|---|---|---|
| Trend / breakout (C015/017/025) | directional momentum | REJECT (cost) |
| Pullback (C020–023) | directional continuation | RETIRED |
| C1 confluence | multi-TF directional reversion | cost-defeated + cross-replication FAILED |
| C016 / S2 / S3 | cross-sectional **directional ranking** | REJECT / pre-falsified |
| C031 TSMOM | time-series **directional** momentum | WITHIN_NULL |
| **S4 cross RV (this)** | **reversion of a stable inter-instrument relationship** | **under test** |

S4 is **not** trend, momentum, confluence, currency ranking, or directional factor
discovery. It asks whether *relationships* between instruments are stable and their
deviations revert — a reversion mechanism none of the above tested.

## Hard boundaries (restated)

No CAMPAIGN_032 / no campaign; no strategy / entry-exit / trading system; no
train/validation/test; no approval; no paper/demo/live; no trading-API calls;
read-only research-DB only; **definitions frozen before data review, not altered
after** (Phase 1).

## Deliverables (one doc per phase)

| Phase | Document |
|---|---|
| 0 | `CROSS_RELATIVE_VALUE_FACTOR_VALIDATION_001_PLAN.md` (this) |
| 1 | `CROSS_RELATIVE_VALUE_PROTOCOL.md` (frozen pre-registration) |
| 2 | `CROSS_RELATIVE_VALUE_DESIGN.md` (+ research-only construction code) |
| 3 | `CROSS_RELATIVE_VALUE_RESPONSE_STUDY.md` |
| 4 | `CROSS_RELATIVE_VALUE_CROSS_SECTIONAL_VALIDATION.md` |
| 5 | `CROSS_RELATIVE_VALUE_NULL_COMPARISON.md` |
| 6 | `CROSS_RELATIVE_VALUE_ROBUSTNESS.md` |
| 7 | `CROSS_RELATIVE_VALUE_FACTOR_VERDICT.md` |
| 8 | `NEXT_PROMPT_AFTER_CROSS_RELATIVE_VALUE_FACTOR_VALIDATION.md` + `..._001_SUMMARY.md` |
