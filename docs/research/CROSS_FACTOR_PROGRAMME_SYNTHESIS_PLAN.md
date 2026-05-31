# Cross-Factor Programme Synthesis — Plan & Truth Audit

**Branch:** `research-cross-factor-programme-synthesis-001`
**Type:** project-level **synthesis & direction decision**. Docs-only. No factor,
no factor-validation, no screen, no front gate, no campaign, no strategy, no
train/validation/test, no trading-API calls.
**Date:** 2026-05-30.
**Freeze status:** intact. `approved: []`; paper/demo/live blocked.

> **Purpose:** the S1–S5 cross-factor shortlist is exhausted. This sprint produces
> a rigorous synthesis of the *entire* expanded FX research programme and chooses
> the single highest-value remaining direction — without doing any more factor
> work. It is the cross-era analogue of the majors-era corpus-viability review.

---

## PHASE 0 — Truth audit (where the programme actually stands)

A complete, honest accounting of every major effort and its verdict. Sources are
the committed verdict/summary docs and the project memory; nothing is re-run.

### 0.1 The arc of the programme

1. **Majors directional families** (trend/breakout/pullback/mean-reversion) —
   C015/017/025 breakout, C020–023 pullback, C008/027 reversion → **REJECT,
   cost-defeated** (one front-gate survivor, C027, failed its train gate).
2. **M1/H1/H4 confluence (C1)** — validated as a **GENUINE factor** (sign-universal
   on 7 majors) but **cost-defeated**; its high-vol path **FAILED its front gate**
   (net-negative 3/3). Directional time-bar confluence lane CLOSED.
3. **Non-time-bar research** (range/volatility bars) — C029 10-pip range-bar
   campaign **REJECT (net −0.019R, cost)**; feasibility kept infra, paused search.
4. **H16 overshoot-exhaustion front gate** → **FAIL** (no effect, rev ≈0.50,
   null-internal).
5. **H03 thin-move front gate** → **FAIL** (weak, non-monotone, cost-defeated) →
   **directional non-time-bar search RETIRED**.
6. **C1 factor validation** (7 majors) — GENUINE, magnitude-concentrated on the
   discovery pairs, **cost-defeated everywhere**.
7. **C1 cross replication** (8 crosses) → **REPLICATION_FAILED** — C1's magnitude
   did **not** generalize to non-collinear crosses (a **USD-regime artifact**).
8. **S2 currency-strength validation** → **FACTOR_REJECTED** — a real,
   breadth-diverse **descriptor** (breadth/H2 *passed*: not a USD artifact) with
   **no forward-predictive power** (0/80 null cells). **Pre-falsified S3.**
9. **S4 cross relative-value validation** → **FACTOR_REAL_BUT_WEAK** — the
   programme's **first non-rejected factor**: triangular no-arbitrage reversion is
   **genuinely real** (20/20 null cells clear, beats the wrong-triangle null,
   stable across all pairs/years/sessions) but **confined to the no-arb cost band**
   (~0.5 bp vs ~5 bp; front-loaded; 4/8 half-life ≤1 bar).
10. **Non-USD cross expansion** (data) — 8 crosses **populated/validated/
    materialized/cost-profiled** (14.7M M1 rows). Delivered **breadth only**;
    crosses are **wider + fatter-tailed** than majors — **no** cost, history, or
    microstructure relief.

Adjacent portfolio-level efforts: **C016 cross-sectional momentum → REJECT** (a
USD bet); **C028 relative-value spread → LIKELY_SELECTION_NOISE**; **C031
vol-managed TSMOM → WITHIN_NULL + financing-defeated** (financing ≈4× spread).

### 0.2 The one-paragraph truth

The OANDA spot-FX corpus — now **majors + 8 crosses, ~5y, M5/H4, retail spreads** —
has been searched across **trend, breakout, pullback, mean-reversion, multi-TF
confluence, non-time-bar/microstructure, cross-sectional momentum, currency
strength, time-series momentum, and relative-value/cointegration**. Every effect is
**rejected, a failed replication, cost-defeated, financing-defeated, or
real-but-sub-cost-band**. The cross expansion **confirmed breadth was the only new
lever** (S2 proved the field is genuinely multi-currency; S4 found genuine no-arb
structure) yet **every genuine effect is still inside the venue's cost band**. No
strategy or campaign is approved; paper/demo/live are blocked.

### 0.3 What is genuinely settled vs genuinely open

- **Settled (closed):** directional and cross-sectional *prediction* on this venue
  (trend/momentum/confluence/strength), and *reversion* of both no-arb triangles
  (real but sub-cost) and cointegration spreads (non-stationary, C028/S4-secondary).
  Infrastructure and the front-gate discipline are **working**, not failed.
- **Open (genuinely untested on this venue/data):** **carry / financing**
  (interest-rate-differential return source — always data-blocked, never tested
  with real rates on real carry crosses); and the standing corpus-reopen levers —
  **lower-cost venue / true tick-L2**, **different market (futures/metals/crypto)**,
  **longer history**.

### 0.4 Hard boundaries for this sprint

No CAMPAIGN_032 / no campaign; no trading logic / entry-exit; no factor discovery
or validation; no screen / front gate; no train/validation/test; no approval; no
paper/demo/live; no trading-API calls; **no reviving rejected ideas.** Output is
documentation, evidence synthesis, and one strategic decision.

## Deliverables (one doc per phase)

| Phase | Document |
|---|---|
| 0 | `CROSS_FACTOR_PROGRAMME_SYNTHESIS_PLAN.md` (this) |
| 1 | `COMPLETE_PROGRAMME_EVIDENCE_INVENTORY.md` |
| 2 | `PROGRAMME_LESSONS_LEARNED.md` |
| 3 | `REMAINING_UNTESTED_MECHANISMS.md` |
| 4 | `NEXT_PROGRAMME_OPTIONS.md` |
| 5 | `NEXT_MAJOR_DIRECTION_DECISION.md` |
| 6 | `NEXT_PROMPT_AFTER_PROGRAMME_SYNTHESIS.md` |
| 7 | `CROSS_FACTOR_PROGRAMME_SYNTHESIS_SUMMARY.md` (+ validation) |

## Method

Evidence-first: every claim traces to a committed verdict/summary doc. The
synthesis weighs the *mechanism space* (what return sources have been tested) and
the *constraint space* (cost, financing, history, microstructure, venue), then
chooses the direction with the **highest information gain per unit cost and lowest
repeat-risk** — explicitly preferring a genuinely *new mechanism or constraint
regime* over any re-mining of the exhausted one.
