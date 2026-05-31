# Currency-Strength Factor-Validation 001 — Plan & Baseline Audit

**Branch:** `research-currency-strength-factor-validation-001`
**Type:** **factor-validation study only** (multi-market front-gate framework
**Stage 1–2**). Not a strategy, campaign, front-gate screen, or
train/validation/test exercise.
**Date:** 2026-05-30.
**Freeze status:** intact. `approved: []`; paper/demo/live blocked; no trading-API
calls; read-only research-DB access only.

> **The one question this sprint answers:** does a **cross-implied
> currency-strength factor** exist in the expanded 15-instrument FX universe — is
> it real, null-separated, and robust? **The objective is factor existence and
> robustness, NOT tradability.** No net-of-cost gate, no signal, no entry/exit.

---

## PHASE 0 — Baseline audit

### 0.1 Cross-universe planning sprint (`NONUSD_CROSS_FACTOR_DISCOVERY_PLANNING_001`)

Mapped the 15-instrument universe (7 USD majors + 8 non-USD crosses); crosses add
**breadth only** (history/microstructure/cost walls unchanged). Generated 24
cross-enabled families, fenced the re-tunes, ranked and shortlisted 5 (S1–S5).

### 0.2 Factor-family ranking (`CROSS_UNIVERSE_FACTOR_RANKING`)

S2 (cross-implied currency-strength index, family F01) scored **4.17** —
**#2 overall**, behind only the now-spent C1 replication (S1). It ranked top on
**novelty** (structurally impossible on USD-only majors), **data requirements**
(needs nothing new), and **replication potential** (confirms across many
non-collinear legs).

### 0.3 S2 rationale (`CROSS_UNIVERSE_FACTOR_SHORTLIST`)

Thesis: decompose the 15-instrument return matrix into a **per-currency strength
vector**; a currency's strength relative to the *whole field* (not just USD) is a
cleaner state variable than any single pair. It directly removes the
**USD-collinearity** that made C016 a USD bet and C031's book "a structural USD
bet." Pre-named failure modes: (a) strength vector dominated by the USD/EUR
liquidity axis (adds little over a single pair); (b) divergence real but sub-cost
(out of scope here — tradability excluded); (c) collinearity sneaks back (EUR
loads on 5 instruments) and overstates breadth — mitigated by a proper
decomposition + a collinearity diagnostic.

### 0.4 C1 replication failure (`C1_CROSS_REPLICATION_VERDICT`)

C1 → **REPLICATION_FAILED** (`C1_ARTIFACT`): the one genuine majors factor did
**not** generalize to non-collinear crosses (sign-inconsistent, null-
indistinguishable, unstable). This is the **second** independent signal that the
programme's single-instrument "edges" are entangled with **USD-regime
structure** — which is precisely S2's motivation: a **breadth-pure,
currency-level** construction that removes USD-collinearity *by design* rather
than inheriting it. The C1 failure raises, not lowers, the value of testing S2 —
but with sober priors: a currency-strength effect that is merely a restated
USD/EUR axis would be the same artifact in new clothes.

### 0.5 Non-USD cross readiness review (`NONUSD_CROSS_DATA_READINESS_REVIEW`)

All 8 crosses are **populated, validated, materialized (M5/M15/H1/H4M1), and
cost-profiled** over 2021-05-26 → 2026-05-26 (14.7M M1 rows + 4.05M materialized
bars, parity PASS 8/8). Crosses are **wider + fatter-tailed** than majors — but
cost is **out of scope** for this existence/robustness study. Data is
research-grade and sufficient; **no new ingestion required.**

### 0.6 Current instrument universe

15 instruments spanning **8 currencies** (USD, EUR, GBP, JPY, AUD, NZD, CHF, CAD).
Leg coverage (how many instruments each currency appears in, of the 15):
USD **7**, EUR **6** (EUR_USD/GBP/JPY/CHF/AUD + …), JPY **5** (USD/EUR/GBP/AUD/
NZD_JPY), GBP **4**, AUD **4**, CHF **3**, NZD **3**, CAD **1** (USD_CAD only).
**CAD is a known weak link** — it appears in a single instrument, so its
"strength" is just USD_CAD; this is pre-registered as a caveat, not fixed
post-hoc.

---

## Why S2 was chosen

It is the highest-ranked **new, breadth-pure** family that (a) needs no new data,
(b) tests a genuinely different hypothesis from every rejected lane (cross-
sectional currency strength, not single-instrument confluence/breakout/reversion),
and (c) attacks the exact USD-collinearity that C016, C031, **and** now C1 reveal
as the recurring confound. It is the disciplined next step the planning sprint
pre-committed to on the realized `C1_ARTIFACT` branch.

## Hypotheses

- **H1 (existence):** a per-currency strength score computed from the 15-instrument
  return matrix carries cross-sectional information about **forward currency
  moves** beyond chance (momentum *or* reversion — direction is an empirical
  output, not assumed).
- **H2 (breadth/independence):** the strength vector is **not** merely a restated
  USD (or USD/EUR) axis — multiple currencies contribute independent variance
  (tested by a collinearity diagnostic).
- **H3 (robustness):** any effect is **stable** across currencies, pairs, years,
  sessions, and nearby lookback/ranking/aggregation definitions — not a single
  currency, period, or knob.

## Success criteria (FRONT_GATE_CANDIDATE — Phase 7 detail)

A genuine factor requires **all**:
1. **Existence** — a conditional forward-return effect (strongest/weakest/rapidly-
   changing) that is directionally coherent across horizons.
2. **Null separation** — exceeds randomized-rank / shuffled-currency / matched-
   timestamp / unconditional nulls (|matched-Z| ≥ 2) on **multiple** conditions,
   not a single best-of-N cell.
3. **Robustness** — stable across currencies/pairs/years/sessions and across
   nearby lookback/ranking/aggregation definitions.
4. **Breadth** — not reducible to a single-currency (USD) axis (H2 holds).

## Failure criteria

- **FACTOR_REJECTED:** unstable, fails the nulls, or inconsistent (effect sits in
  the null band, or flips sign across horizons/years/sessions, or is one-currency/
  one-period driven, or is just the USD axis).
- **FACTOR_REAL_BUT_WEAK:** exists and survives the nulls *somewhere* coherent but
  is too weak/narrow (e.g. one horizon, modest Z, partial robustness) to merit a
  future front-gate screen.
- **FACTOR_FRONT_GATE_CANDIDATE:** survives existence + null + robustness +
  breadth → merits a *future* (separate, later) front-gate screen. **This sprint
  does not build that screen.**

> Tradability is excluded from every branch. Even FRONT_GATE_CANDIDATE makes no
> trading claim — it only earns the *right to be cost-screened later*.

## Hard boundaries (restated)

No CAMPAIGN_032 / no campaign; no strategy / entry-exit / trading system; no
train/validation/test; no approval; no paper/demo/live; no trading-API calls;
read-only research-DB access only; **definitions frozen before data review and not
altered after** (Phase 1).

## Deliverables (one doc per phase)

| Phase | Document |
|---|---|
| 0 | `CURRENCY_STRENGTH_FACTOR_VALIDATION_001_PLAN.md` (this) |
| 1 | `CURRENCY_STRENGTH_FACTOR_PROTOCOL.md` (frozen pre-registration) |
| 2 | `CURRENCY_STRENGTH_INDEX_DESIGN.md` (+ research-only construction code) |
| 3 | `CURRENCY_STRENGTH_RESPONSE_STUDY.md` |
| 4 | `CURRENCY_STRENGTH_CROSS_SECTIONAL_VALIDATION.md` |
| 5 | `CURRENCY_STRENGTH_NULL_COMPARISON.md` |
| 6 | `CURRENCY_STRENGTH_ROBUSTNESS.md` |
| 7 | `CURRENCY_STRENGTH_FACTOR_VERDICT.md` |
| 8 | `NEXT_PROMPT_AFTER_CURRENCY_STRENGTH_FACTOR_VALIDATION.md` + `..._001_SUMMARY.md` |
