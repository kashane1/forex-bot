# Non-time-bar thesis discovery — sprint 001 PLAN

**Branch:** `research-external-non-time-bar-thesis-discovery-001`
**Date:** 2026-05-29
**Type:** research & hypothesis-generation **only** — no code, no campaign, no
backtests, no evidence, no approval.

> **Branch note:** the preceding `research-range-volatility-bar-feasibility-001`
> branch is not yet merged to `origin/main`, and this sprint must review its outputs
> (Phase 0). So this docs-only sprint is **stacked on the feasibility branch tip**
> to retain context. It adds only Markdown under `docs/research/`; it touches no
> code, config, or strategy. When the feasibility branch merges, this rebases
> cleanly onto the updated `origin/main`.

---

## 0. Why this sprint exists

The non-time-bar **infrastructure** question is settled. The
[feasibility study](RANGE_VOLATILITY_BAR_FEASIBILITY_001_SUMMARY.md) proved cost
stops dominating at **25–30 pip range bars** and **50-pip volatility bars** on every
major, and that USD_JPY is unremarkable. CAMPAIGN_029's rejection was a 10-pip
**threshold-cost** problem, not a verdict on non-time bars.

**The bottleneck is no longer infrastructure — it is idea quality.** We have a
cost-feasible canvas and no compelling reason to paint on it. This sprint does deep
external research to generate a small number of **genuinely new, externally
motivated** non-time-bar trading hypotheses worth *future* testing.

**Success ≠ finding an edge.** Success = a short list of hypotheses that are
materially different from everything already rejected, each tied to a real external
rationale and honestly scored for novelty/fit/overfitting risk.

## 1. Hard rules (this sprint)

No campaign / no CAMPAIGN_030 / no backtests / no strategy-code or
execution-infra edits / no approvals / no `approved_strategies.yaml` edits / no
paper-demo-live / no OANDA / no credentials / **no performance claims, no Sharpe,
no expectancy or PnL projections**. Markdown docs under `docs/research/` only.

## 2. What has already been tested (do not re-discover)

| family / campaign | what it was | verdict |
|---|---|---|
| C001–C014 (trend/MR/breakout/event, time bars) | classic time-bar systems on M15–D1 | REJECT (mostly cost / no edge; some evidence-integrity caveats) |
| C015 failed-breakout reversal | H4 reversal | REJECT |
| C016 weekly cross-sectional momentum | portfolio momentum | REJECT |
| C017 weekly volatility-contraction breakout | squeeze→breakout | REJECT |
| C018/C019 exit-hypothesis (protective stop / thesis-invalidation) | exit overlays | REJECT (no exit edge) |
| C020/C021/C022/C023 MTF / pullback continuation | H4↔H1↔M-resolved pullback | RETIRED (no entry edge; exhausted) |
| USD_JPY price-structure + macro-context thread | session/vol/compression/macro overlays | PAUSED (direction ≈ null; no actionable conditioning) |
| C025 M5 Donchian + HTF | fast-timeframe breakout | REJECT (cost gradient, no edge) |
| C026 timeframe ladder M3–M30 | C025 across timeframes | REJECT (monotone cost gradient, best M30 still net-neg) |
| C027 H4 filtered z-score reversion | the one front-gate survivor | REJECT_TRAIN_GATE (edge wafer-thin, AUD-dominated) |
| C028 relative-value / cointegration spread | two-leg reversion | NO SCAFFOLD (selection noise; two-leg cost hostile) |
| **C029 USD_JPY 10-pip range-bar MTF breakout** | first non-time-bar lane | **REJECT_TRAIN_GATE** (gross +0.084R, net −0.019R, cost-defeated) |
| feasibility 001 | 7 majors × 13 thresholds geometry/cost | diagnostic; lane PAUSED |

## 3. What must NOT be repeated (anti-patterns)

1. **C029 at a bigger number.** A range/volatility-bar *breakout* at 25–30/50 pip with
   the same MTF-trend confluence is a threshold retune of a rejected rule — forbidden.
2. **Threshold/parameter tweaks dressed as new ideas.** Changing the bar size, stop
   multiple, ADX window, EMA length, etc. is not a new thesis.
3. **"Same strategy, slower timeframe/bigger bar."** C026 already showed slowing the
   clock only walks a cost gradient; it does not create edge.
4. **Mining many variants then keeping the best.** C028's `LIKELY_SELECTION_NOISE`
   trap — best-of-N beats nothing once best-of-N noise is accounted for.
5. **Single-pair / single-period artifacts.** C027 was AUD-dominated; the front gate's
   pair-holdout (G5) and recency checks exist for this.
6. **Edge that is really structure.** If a "signal" dies once a matched null
   reproduces its pair/side/session/hold structure, it was never skill (G1/G2).
7. **Cost-hostile fast cells.** Anything that trades a `true_range ≤ 40 pip` /
   sub-feasible cadence cell (the C025/C026/C029 cost trap; G3).
8. **Discretionary patterns with no rule.** Anything that can't be specified as a
   precommitted, lookahead-free rule.
9. **Data we don't have.** Hypotheses requiring true tick/trade prints, signed order
   flow, full-market consolidated volume, or L2 depth — the repo has none of these.

## 4. The data reality (hard constraint on every hypothesis)

The local corpus is **M1 OHLCV with bid/ask + mid and a tick-count `volume`**, for 7
majors, 2021-05-27 → 2026-05-26, aggregable to M5/M15/H1/H4/D. Therefore:

- **Available now:** range bars; volatility bars (abs_close / true_range, fixed /
  atr-scaled); anything derivable from M1 OHLC, the bid/ask **spread**, M1
  **tick-count volume**, realized variance / overshoot geometry, and the existing
  **session / macro-regime / calendar** context infra.
- **NOT available (hypotheses needing these are out unless reframed):** true
  trade/tick prints, **signed** trade flow / aggressor side, consolidated market
  volume (FX is decentralized; OANDA "volume" is a *tick-count proxy*), L2 order-book
  depth, options/positioning feeds.
- **Implication:** López de Prado **dollar bars** are approximable (price × tick
  volume), **volume (tick) bars** are buildable, but true **imbalance / run bars**
  (signed flow) are **not** — any imbalance idea must use a *proxy* (e.g. close
  location within the bar, bid/ask pressure) and that proxy quality is itself a
  research risk to flag.

## 5. The bar to clear (front gate, unchanged)

Any hypothesis that graduates from this sprint still owes the full
[front gate](FUTURE_CAMPAIGN_REENTRY_GATES.md) **before** any campaign number is
assigned: G1 beats a matched null post-cost; G2 beats the *structure-matched* null;
G3 cost-feasible on the traded cell; G4 each filter adds edge; G5 not a single-pair
artifact. Plus the lane's own re-entry criteria
([lane decision §4](NON_TIME_BAR_LANE_DECISION_AFTER_C029.md)): mandatory external
thesis, cost/threshold ≤ 0.10, cost/risk ≤ 0.05, sane cadence, distinctness memo.

## 6. Research goals

1. Learn how **professionals** (futures, FX, CTA, microstructure) actually use
   non-time bars — vs. retail myth (Phase 1).
2. Ground the ideas in **literature** (López de Prado info-driven bars, microstructure,
   volatility clustering, trend persistence, FX session research) (Phase 2).
3. Find **publicly scrutinised** non-time-bar systems that recur across independent
   sources (Phase 3).
4. Generate ≥ 20 distinct candidate hypotheses (Phase 4).
5. Screen/rank with the lab's principles (Phase 5).
6. Shortlist ≤ 5 (Phase 6).
7. Recommend exactly one lane action + draft (if applicable) a **front-gate** (not
   campaign) next prompt (Phase 7).
8. Validate + summarise (Phase 8).

## 7. Phase → deliverable map

| phase | doc |
|---|---|
| 0 | this plan |
| 1 | `NON_TIME_BAR_PROFESSIONAL_USAGE_SURVEY.md` |
| 2 | `NON_TIME_BAR_LITERATURE_REVIEW.md` |
| 3 | `NON_TIME_BAR_PUBLIC_STRATEGY_REVIEW.md` |
| 4 | `NON_TIME_BAR_HYPOTHESIS_CATALOG.md` (≥20) |
| 5 | `NON_TIME_BAR_HYPOTHESIS_RANKING.md` |
| 6 | `NON_TIME_BAR_FINAL_SHORTLIST.md` (≤5) |
| 7 | `NON_TIME_BAR_NEXT_RESEARCH_DECISION.md` (+ `NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md` if applicable) |
| 8 | `NON_TIME_BAR_THESIS_DISCOVERY_001_SUMMARY.md` |

## 8. Honesty constraints on the research docs

- No fabricated metrics, citations, Sharpe ratios, or PnL. Where a claim is
  established literature, name the source at a verifiable level (author/work/concept);
  where it is my synthesis or inference, say so.
- "Might work" reasoning is allowed; "does work / would return X" is not.
- Every hypothesis is explicitly checked against §3 (anti-patterns) and §4 (data).
