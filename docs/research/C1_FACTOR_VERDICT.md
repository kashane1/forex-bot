# C1 Factor Verdict (Phase 6)

**Status:** VERDICT (factor-validation only)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001`
**Freeze state:** intact — this verdict creates **no** campaign, **no** strategy,
**no** front gate, **no** approval, and enables **no** paper/demo/live. It
recommends (does not start) at most one future pre-registered front-gate screen.

---

## Verdict

# `FACTOR_FRONT_GATE_CANDIDATE`

`C1_trend_cont_long` — fade a full **H4 + H1 + M15 bullish alignment** for a
30–60-minute downward reversion — is a **genuine, robust, non-USD-artifact market
factor** that is **cost-defeated as a flat signal** but retains **one
economically-motivated, cost-aware sub-regime** (high-volatility on
EUR_USD/USD_JPY) strong enough to earn **exactly one** future pre-registered
front-gate screen — and nothing more.

## The sprint's actual question, answered

> Is C1 (1) a genuine market factor, (2) a USD-regime artifact, (3) a
> sample-selection artifact, or (4) a statistical mirage?

**Answer: (1) a genuine market factor.** The other three are excluded by the
evidence:

| Candidate explanation | Verdict | Why (phase) |
|---|---|---|
| #2 USD-regime artifact | **excluded** | Pair-space sign is negative and equal-magnitude across **both** USD-base and USD-quote pairs (no flip, unlike `A3_breakout`); long & short mirror both revert; cross-pair synchrony is low (idiosyncratic, not one USD factor). (Phase 3) |
| #3 sample-selection artifact | **excluded** | Persistent across 5/6 years and all 4 sessions; not removable by dropping any single regime window. (Phase 2) |
| #4 statistical mirage | **excluded** | Sign survives 55/56 spec×pair perturbations; EUR_USD/USD_JPY significant under nearly every reasonable EMA/slope/trend/confluence-depth change. (Phase 4) |
| #1 genuine factor | **supported** | Sign-universal (7/7 negative); null-surviving on EUR_USD (mZ60 −4.21) and USD_JPY (−3.55); vol- and extension-scaled monotonically (over-extension mechanism). (Phases 1–2) |

## Why `FRONT_GATE_CANDIDATE` and not `FACTOR_REJECTED`

REJECTED requires instability, confounding, or non-robustness. C1 is the
opposite on all three: it is **stable** (Phase 2), **not confounded by USD**
(Phase 3), and **robust** to specification (Phase 4). It is the first directional
confluence factor on this corpus to clear that bar.

## Why `FRONT_GATE_CANDIDATE` and not `FACTOR_REAL_BUT_NOT_TRADABLE`

This was the genuinely close call. Unconditionally, C1 **is** cost-defeated on all
seven majors (best case EUR_USD 0.73× spread), which on its own reads
`REAL_BUT_NOT_TRADABLE`. What tips it to `FRONT_GATE_CANDIDATE` is a **single
cost-aware path that is independently motivated, not post-hoc fished**:

- Phase 2 showed — on the **full sample, all 7 pairs, before any cost analysis** —
  that the reversion **grows monotonically with volatility** (high-ATR tertile
  t −3.78). High-volatility conditioning is therefore predicted by the mechanism,
  not chosen by scanning cost cells.
- Phase 5 then found that in **high-volatility windows on EUR_USD/USD_JPY** the
  spread-adjusted reversion is **positive and survives an outlier check**
  (EUR_USD London hi-vol: median −2.0, t −3.4; USD_JPY Tokyo hi-vol: median −2.25,
  t −2.8) — while explicitly catching one cell (USD_JPY NY) that was an
  outlier mirage.

Per this sprint's **pre-committed** Phase-0 criteria, "a session/volatility
sub-regime where the spread-adjusted effect is positive" is exactly what
distinguishes `FRONT_GATE_CANDIDATE` from `REAL_BUT_NOT_TRADABLE`. Choosing the
weaker verdict after finding that path would be moving the goalposts.

## Honest caveats the verdict does NOT assume away

1. **Still cost-defeated unconditionally.** The candidate rests entirely on the
   high-vol sub-regime; the flat factor is not tradable.
2. **The cost-aware cells are post-hoc and optimistically costed.** "net = |mean|
   − spread" ignores entry/exit slippage, exit-rule cost, and high-vol spread
   spikes; per-event variance is ±~20 pips. This is a *hypothesis* of tradeability.
3. **Concentrated on the two discovery pairs.** The cost path does not appear on
   the five new majors.
4. **Irreducible residual USD share.** All seven pairs share the USD leg, so the
   confound is *substantially* — not *completely* — excluded; only non-USD crosses
   (absent from the corpus) could close that gap.

## Recommended next step — exactly ONE future front-gate screen

**Proposed screen:** `C1 high-volatility multi-TF-alignment mean-reversion
front-gate screen`.

Pre-register (frozen precommit) and test **only**:

1. **Volatility-conditioned, post-cost, out-of-sample.** Take the C1_long fade
   restricted to high-volatility windows on EUR_USD + USD_JPY; charge **realistic
   round-trip cost** (event-bar spread + slippage, with high-vol spread widening),
   and test against a **matched, post-cost null** on a **held-out** period, using
   the lab's `cost_feasibility` + `matched_nulls` machinery. The make-or-break is
   "beats the matched null **after** realistic cost, out-of-sample."
2. **Volatility monotonicity holds out-of-sample.** Confirm the pre-cost
   high-vol > low-vol gradient (Phase 2) replicates on the held-out period rather
   than being an in-sample tilt.
3. **GBP_USD as a partial third pair.** GBP_USD cleared the matched null at 30 min
   (mZ30 −2.46); include it as a weaker out-of-USD-pair check of generalisation.

**Stop criterion (pre-committed):** if the high-vol-conditioned C1 fade does
**not** beat the matched-null-**post-cost** bar out-of-sample on **both** EUR_USD
and USD_JPY, the M1/HTF time-bar confluence directional lane is **closed** on this
corpus (joining the retired non-time-bar lane); reopen only with new data
(10–15y, or genuine non-USD crosses) or a new external thesis — via a fresh
screen, never a re-tune.

A `PASS` of that future screen would authorise only a *separate, later* scaffold
sprint; it would not, by itself, create a campaign or approve anything.

## Hard-rule confirmation

No campaign created (no CAMPAIGN_032 or any campaign). No strategy built. No
entry/exit rules. No train/validation/test run. No parameters optimised (the
factor is the locked prior-sprint definition; robustness specs were perturbations,
not selections). No front gate created. No strategy approved. Paper/demo/live
remain blocked. No OANDA APIs, no credentials. Only a recommendation for one
future *research* screen.
