# External FX Thesis Sourcing Framework

**Sprint:** `external-thesis-sourcing-and-session-atlas-001` · **Phase 1**
**Status:** methodology only. No thesis is claimed to have edge. No campaign, no C024,
no C023, no approval, no implementation. `approved_strategies.yaml` = `approved: []`.

---

## 0. Why this framework exists

Every strategy family this repo has tested has been a variation on the same internal
idea: combine indicators (trend filters, ADX, pullback depth, MTF confluence) on
USD-pairs and hope the confluence produces an entry edge. The documented record:

- Campaigns 002–021: rejected / diagnostic / no approval.
- C022 H4/H1 pullback-resolution: **rejected**, no entry edge (USD_JPY win rate 0.379,
  mean R ≈ 0).
- C023 (incl. ADX22 sibling): **not executed, not supported.**
- USD_JPY microstructure entry + post-entry management: **CLOSED / NOT_READY**;
  early-exit counterfactuals *reduced* expectancy.

The common failure mode is **threshold-mining within one structural idea**: when an
indicator combination fails, we tweak a threshold (ADX 20 → 22, pullback 0.5 → 0.382)
and re-run. That is curve-fitting noise, not hypothesis testing.

This framework forces a different discipline: **source structurally-distinct theses
from outside the failed family, and screen them on paper against ten criteria before
a single line of strategy code is written.** A thesis must earn the right to be
designed; it does not get a campaign by default.

---

## 1. The ten evaluation criteria

Each candidate thesis is scored on all ten. A thesis is only eligible for a future
*precommit-design* sprint if it passes the **gating** criteria (marked ⛔ = hard gate)
and scores acceptably on the rest. Scoring is qualitative (`strong` / `adequate` /
`weak` / `fail`) and must cite atlas evidence or repo history — never vibes.

### 1. Structural distinctness from failed internal families ⛔
Is the *entry mechanism* genuinely different from trend/pullback/ADX/MTF-confluence?
A thesis that reduces to "another indicator threshold on the same confluence idea"
fails this gate. Distinctness is judged on the **decision variable**, not cosmetics:
e.g. "time-of-day conditioning" or "prior-session level interaction" are structurally
distinct; "EMA 50 instead of EMA 55" is not. Cross-reference the existing
`CAMPAIGN_0XX_STRUCTURAL_DISTINCTNESS_MEMO.md` series.

### 2. Plausible economic / market-structure mechanism ⛔
Is there a *reason* this would work that is not "the backtest said so"? Acceptable
mechanisms: liquidity/participant rotation across sessions, scheduled-flow imbalances
(fixings, option expiries, calendar releases), structural stop placement around
prior-session extremes, carry/rate-differential regime. A thesis with no mechanism is
a data-mining artifact waiting to happen.

### 3. Compatibility with USD_JPY
Does the mechanism specifically make sense for USD_JPY? (e.g. Tokyo-session relevance,
JGB/UST rate-differential carry, MoF/BoJ intervention regimes, Gotobi fixing flows.)
A generic-EUR_USD idea ported blindly scores `weak` here.

### 4. Compatibility with available M1/M15/H1/H4 data ⛔
Can the thesis be measured with what we actually have read-only (2021-05→2026-05 M1;
H4 back to 2020; bid/ask + spread)? A thesis needing tick data, order-book depth,
options surfaces, or COT positioning that we do **not** have fails this gate.

### 5. Sufficient sample size
How many independent decision events does the thesis generate over the train+validation
window? A once-a-month setup yields ~50 events over the usable history — too few to
distinguish from noise. State the expected event count and whether it supports
inference. Beware pseudo-replication (overlapping windows counted as independent).

### 6. Objective codability ⛔
Can the entry/exit be specified as a deterministic function of observable data with
**no discretionary judgment**? "Buy the London breakout" must reduce to an exact
range definition, breakout trigger, invalidation, and timeout. If it can't be coded
unambiguously, it can't be precommitted.

### 7. Realistic transaction-cost survival ⛔
Given the **measured** USD_JPY spread atlas (median/p90/p95 spread by session, plus
spread/ATR), does the expected per-trade move plausibly clear costs? A thesis whose
edge is smaller than the spread it pays in its own trading window is dead on arrival.
This is a *plausibility* gate using real spread data — not an edge claim.

### 8. Low lookahead risk
How easy is it to accidentally use future information? Theses keyed to *completed*
prior sessions / closed bars are low-risk; theses needing "today's high" or
same-bar extremes are high-risk and require careful next-bar-open execution semantics
(the repo already enforces a next-bar-open policy — note compatibility).

### 9. Low threshold-mining risk
How many free parameters does the thesis have, and how sensitive is the result to
them? Fewer parameters + monotonic/robust behavior = lower overfit risk. A thesis with
many interacting thresholds (each a degree of freedom to mine) scores `weak`. The
future precommit must fix parameters *before* seeing validation/test results.

### 10. Precommit cleanliness
Can the full hypothesis — entry, exit, risk, universe, window, success metric, and
kill criteria — be written down *in advance* such that the result is unambiguous and
non-p-hackable? If the thesis can only be stated after looking at the data, it is not
precommittable.

**Gating summary:** criteria 1, 2, 4, 6, 7 are hard gates. A thesis failing any hard
gate cannot advance, regardless of how attractive the others look.

---

## 2. Thesis categories under consideration

These are *categories to source from*, not endorsements. Each is mapped to the
criteria it must satisfy and the atlas dimension that would test its plausibility.

| # | Category | Core mechanism (hypothesized) | Atlas dimension that screens it |
|---|---|---|---|
| A | Session / time-of-day effects | Participant rotation → systematic drift/vol by hour | Hour-of-day forward return, vol-by-session |
| B | Tokyo/London/NY transition behavior | Liquidity handover → range break or fade at open | Session-boundary range expansion prob. |
| C | Macro / calendar windows | Scheduled-flow imbalance around releases | Vol/return clustering by time (calendar overlay needed) |
| D | Volatility expansion / compression | Vol mean-reverts; compression precedes expansion | Rolling vol percentile → forward range expansion |
| E | Carry / rates / risk-off regime | Rate-differential + risk sentiment drives JPY trend | Regime conditioning (needs rates/risk overlay) |
| F | Previous-session high/low sweeps | Stops cluster at prior extremes → sweep + displacement | False-breakout / sweep-then-reverse frequency |
| G | Opening-range behavior | First-N-min range defines day's bias | Opening-range break continuation prob. |
| H | Range breakout / fakeout | Breaks of consolidation continue or trap | Breakout continuation vs reversal prob. |
| I | Trend-day vs chop-day classification | Days are bimodal; classify early, trade accordingly | Intraday directional persistence distribution |
| J | Mean reversion after extreme intraday extension | Overextension reverts within session | MFE/MAE after extreme moves, reversion prob. |

Categories C and E require external overlays (calendar, rates/risk) we may only have
partially (FRED cache exists: DGS2/DGS10/VIX/SP500/etc.); their data-compatibility
gate (criterion 4) will be judged conservatively.

---

## 3. How this framework is applied downstream

- **Phase 2** builds the USD_JPY session/volatility/spread atlas — the *evidence base*
  for criteria 3, 4, 5, 7, and the screening columns above.
- **Phase 3** scores each candidate thesis against the atlas + repo history on all ten
  criteria, producing the candidate scorecard.
- **Phase 4** selects **at most one** thesis for a future precommit-design sprint, or
  declares MORE_DIAGNOSTICS_REQUIRED / PAUSE_STRATEGY_RESEARCH.

No thesis is implemented in this sprint. Atlas statistics are descriptive market
structure, **not** edge. Passing this framework's screen means a thesis is *worth
designing a precommitted test for* — it does **not** mean the thesis has edge.

---

## 4. Anti-patterns this framework is designed to stop

- **Threshold re-mining** a rejected family under a new name.
- Treating a descriptive statistic ("NY session has higher vol") as a tradable signal.
- Selecting a thesis *because* the atlas showed an attractive cell (that is
  in-sample selection / the atlas becomes the training set).
- Stating the hypothesis after seeing the data.
- Carrying many free parameters into a "precommit."
- Ignoring spread: a setup that only wins gross but loses net.

The atlas informs *which mechanisms are plausible to test*. The actual edge test must
be a **separate, precommitted, out-of-sample** campaign designed in a later sprint —
never inferred from the atlas itself.
