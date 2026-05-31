# C1 Factor Validation — Plan (Phase 0 audit)

**Status:** PLAN (factor-validation only; no campaign, no strategy, no approval)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001` (off clean `origin/main`)
**Type:** factor-validation / response-analysis. **Not** a campaign, **not** a
strategy, **not** a backtest, **not** a front gate. Freeze intact.

---

## 0. Why this sprint exists

The `m1-htf-confluence-sampling-matrix-001` sprint (complete 2026-05-29) ran a
locked 18-state confluence response matrix on USD_JPY + EUR_USD and surfaced
**exactly one** state that survived a session-matched null with the *same sign on
both pairs*:

> **`C1_trend_cont_long`** — when **H4 trend up, H1 trend up, and M15 aligned up**
> (full multi-timeframe bullish alignment), M1 mid price tends to **revert DOWN**
> over the next 30–60 minutes.

The prior sprint's own decision (`FRONT_GATE_CANDIDATE_EXISTS`) was explicit that
this is a **factor, not an edge**, and flagged three open questions it could not
resolve on two USD-legged pairs:

1. **Cost.** The 60-min reversion (~1.1–1.2 pips) is *below* spread on both pairs
   (~1.76 USD_JPY ≈0.65×; ~1.61 EUR_USD ≈0.72×).
2. **Mechanism may differ by pair.** On USD_JPY (a 2021–2026 up-mover) `C1_long`
   reads as over-extension fade; on EUR_USD (broadly down) as bear-rally
   resumption. Same *observable*, possibly different cause.
3. **USD-regime confound.** Both test pairs have a USD leg. A "C1_long reverts
   down" signal could simply be "USD strength mean-reverts" wearing a
   multi-timeframe-alignment costume.

**This sprint resolves which of four things C1 is — without building anything.**

## 1. The question (verbatim from the brief)

Determine whether `C1_trend_cont_long` represents:

1. A genuine market factor.
2. A USD-regime artifact.
3. A sample-selection artifact.
4. A statistical mirage.

## 2. What is already established (audited evidence)

Read directly from the committed prior-sprint artifacts
(`docs/research/usd_jpy_m1_response_matrix_*.csv`,
`docs/research/eur_usd_m1_response_matrix_*.csv`, and the four prior-sprint docs):

| Fact | Source artifact | Value |
|---|---|---|
| C1_long USD_JPY 60-min mean ret | `usd_jpy_..._summary.csv` | **−1.137 pip** (t −3.56, n 2127) |
| C1_long EUR_USD 60-min mean ret | `eur_usd_..._summary.csv` | **−1.167 pip** (t −3.65, n 1584) |
| C1_long USD_JPY matched-Z @30/60 | `usd_jpy_..._nulls.csv` | **−2.96 / −3.20** (within-null 5–15 min) |
| C1_long EUR_USD matched-Z (all horizons) | `eur_usd_..._nulls.csv` | **−3.22 → −4.09** |
| `matched_z ≈ rand_z` | both nulls CSVs | effect intrinsic, not session-timing |
| C1_long mean spread | summary CSVs | 1.757 (USD_JPY) / 1.606 (EUR_USD) pips |
| C1_short (mirror) | summary CSVs | EUR_USD parametric t −2.4…−3.3; USD_JPY within-null |

**Locked state definition (not to be re-tuned):** EMA fast=20, slow=50, slope
lookback=3 completed HTF bars; `trend_up = close>ema50 & slope>0`;
`aligned_up = close>ema50`. C1_long = `H4_trend_up & H1_trend_up & M15_aligned_up`.
Events = rising edge + 60-min cooldown. Forward return signed by context
direction. See `M1_HTF_CONFLUENCE_STATE_DEFINITIONS.md`.

**Data corpus (verified this sprint):** local research Postgres, M1 source
`oanda-practice-m1`, materialized M5/M15/H1/H4M1 (`m1_materialized`), span
2021-05-27 → 2026-05-26 (~5.0y). All **seven** USD-legged majors are present:

| Pair | M1 bars | M5 | M15 | H1 | H4M1 |
|---|---|---|---|---|---|
| EUR_USD | 1,843,476 | 360,972 | 116,628 | 27,249 | 5,234 |
| GBP_USD | 1,836,170 | 357,741 | 115,243 | 26,758 | 5,186 |
| USD_JPY | 1,844,454 | 362,519 | 118,035 | 28,013 | 5,448 |
| AUD_USD | 1,822,196 | 348,717 | 109,904 | 24,774 | 4,362 |
| NZD_USD | 1,824,352 | 351,408 | 110,462 | 23,856 | 4,199 |
| USD_CAD | 1,836,013 | 356,992 | 114,562 | 26,405 | 5,015 |
| USD_CHF | 1,786,535 | 336,541 | 105,604 | 23,400 | 4,039 |

**Hard data limit (carried from C031):** the store has **only USD-legged majors —
no non-USD crosses** (no EUR_GBP, AUD_JPY, etc.). The prior sprint's preferred
confound test ("run on ≥2 non-USD crosses") is **not executable on this corpus.**
This sprint therefore resolves the USD confound a different way: by exploiting the
fact that USD sits on the **base** side of three pairs (USD_JPY, USD_CAD, USD_CHF)
and the **quote** side of four (EUR_USD, GBP_USD, AUD_USD, NZD_USD). If C1 is a USD
artifact, the *pair-space* sign must **flip** between base-USD and quote-USD pairs;
if it is a genuine multi-TF-alignment factor, the *pair-space* sign should be
consistent regardless of where USD sits. This is the central test of Phase 3.

## 3. Method (reuse the locked, audited framework — no new signal invention)

All analysis reuses `src/forex_bot/research/m1_response_matrix.py` primitives
(lookahead-safe HTF→M1 as-of alignment, locked C1 definition, rising-edge +
cooldown sampling, signed forward response, random + session-matched nulls). A
thin new research-only module `c1_factor_validation.py` will:

- build a per-pair **C1 event panel** (one row per C1_long / C1_short event:
  timestamp, base/quote ccy, session, year, quarter, spread, H4 ATR volatility,
  H4 extension-above-EMA50-in-ATR, and `ret_/mfe_/mae_` at 5/10/15/30/60 min),
  persisted to CSV so every reported number traces to an on-disk artifact;
- compute per-pair null comparisons (random + session-matched, 200 seeds) for
  C1_long and C1_short;
- re-derive C1 under **alternative specifications** (EMA lengths, trend
  definitions, nearby confluence depth) for the robustness phase only.

**Integrity rule (from the prior sprint's hard-won lesson):** every figure in
every doc is read back from the committed CSV on disk, never from buffered
stdout or memory. Numbers are quoted with their source filename.

## 4. Phase plan

| Phase | Output doc | Question |
|---|---|---|
| 0 | `C1_FACTOR_VALIDATION_PLAN.md` (this) | audit + plan |
| 1 | `C1_CROSS_PAIR_STUDY.md` | sign/magnitude consistency across 7 majors; USD-concentrated? |
| 2 | `C1_REGIME_STABILITY_STUDY.md` | persistent / episodic / concentrated by year, quarter, vol, session, trend regime? |
| 3 | `C1_USD_CONFOUND_STUDY.md` | is C1 just USD strength? base vs quote, inversion, directional asymmetry |
| 4 | `C1_ROBUSTNESS_STUDY.md` | survives small spec changes (EMA, trend def, nearby confluence)? |
| 5 | `C1_COST_REALISM_STUDY.md` | could this ever realistically be tradable? |
| 6 | `C1_FACTOR_VERDICT.md` | one of REJECTED / REAL_BUT_NOT_TRADABLE / FRONT_GATE_CANDIDATE |
| 7 | `NEXT_PROMPT_AFTER_C1_FACTOR_VALIDATION.md` | next-step prompt (only if verdict warrants) |
| 8 | `C1_FACTOR_VALIDATION_SUMMARY.md` | validation gates + full report |

## 5. Decision criteria (pre-committed, before any new number is computed)

To avoid post-hoc rationalization, the verdict mapping is fixed **now**:

- **FACTOR_REJECTED** if any of: (a) the pair-space sign **flips** with USD leg
  position (pure USD artifact → choice #2), or (b) the effect collapses to one or
  two pairs / one or two years / a single session (sample-selection → #3), or
  (c) it does not survive matched nulls once the surface is widened to 7 pairs and
  vanishes under small spec perturbations (mirage → #4).
- **FACTOR_REAL_BUT_NOT_TRADABLE** if it is **sign-consistent in pair space across
  most pairs, broadly stable across regimes, robust to spec perturbation, and
  null-surviving — but the magnitude stays below realistic round-trip cost** (a
  genuine factor #1 that is still cost-defeated, like the prior sprint measured).
- **FACTOR_FRONT_GATE_CANDIDATE** only if it is real **and** there exists a
  plausible cost-aware path (e.g. a session/extension sub-regime where the
  spread-adjusted effect is positive) that merits one future pre-registered
  front-gate screen.

The prior measured cost-defeat makes **REAL_BUT_NOT_TRADABLE** the prior-most
likely outcome; the phases exist to rule REJECTED in or out and to check whether
any cost-aware path survives.

## 6. Hard rules (enforced for the whole sprint)

Do **not**: create CAMPAIGN_032 or any campaign; build a strategy; create
entry/exit logic; run train/validation/test; create a front gate; approve any
strategy; enable paper/demo/live; call OANDA APIs; use credentials. The local
research Postgres store is read-only descriptive analysis (no broker, no orders),
consistent with every prior research sprint and the freeze gates.

## 7. Files to review first

`M1_RESPONSE_MATRIX_DECISION.md` → `M1_RESPONSE_MATRIX_NULL_COMPARISON.md` →
`M1_HTF_CONFLUENCE_STATE_DEFINITIONS.md` →
`src/forex_bot/research/m1_response_matrix.py` → this plan.
