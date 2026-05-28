# Next Structurally-Different Thesis — Options Comparison

**Date:** 2026-05-28 · **Sprint:** `research-post-c022-family-retirement-and-new-thesis-selection-001`
**Type:** options analysis. Approves nothing, executes nothing, creates no campaign, proposes no threshold.

> This document compares **candidate research lanes** to follow the retired
> C022/C023 pullback-resolution family. It is a menu, not an authorization. Nothing
> here is precommitted; the selected lane (Phase 4) is a diagnostic direction only
> and must be independently precommitted in a future sprint before any execution.

## What "structurally different" must mean here

The C022 closeout established that the failure is an **entry-edge / signal-quality**
failure: stop geometry, time-invalidation, cost-free baselines, and ADX re-gating all
stay negative, and every structural entry feature is at AUC ≈ 0.50. The only
above-floor separators are **context** (cost, volatility, time-of-day), all weak
(AUC ≲ 0.58) and at least partly mechanical. A genuinely different lane must
therefore **not** be "re-filter the same H4→H1→M15 pullback signal." It must change
*what is being detected* (a different market mechanism) or *what question is being
asked* (tradeability/process rather than alpha).

## Scoring key

Each lane is scored 1–5 (5 = best/strongest) on:

- **Distinct** — structural distinctness from the retired pullback family.
- **Support** — support from *current* evidence (without threshold-mining it).
- **Complexity** — implementation simplicity (5 = simplest).
- **Overfit-resist** — resistance to overfitting (5 = most resistant).
- **Data-fit** — compatibility with available **M1/M15** (+ H1/H4 derived) data (5 = fully covered).
- **Sample** — expected diagnostic sample size (5 = large).
- **Precommit** — how cleanly it can be precommitted as a falsifiable hypothesis (5 = cleanest).

"Data requirements" and "Priority" are called out per lane in prose.

---

## Lane A — Session / time-of-day behavior

London open, NY open, London close, rollover avoidance.

- **Reason it's a candidate.** `hour` was one of the few above-floor context
  separators (|AUC−0.5| = 0.074) in the C022 feature separation.
- **Risk.** Likely cost/session overfit — spreads and liquidity vary by session, so a
  "time-of-day edge" can be a relabeled cost effect. The C022 signal already showed
  the largest mechanical separator was `spread_to_atr_pct`.
- **Data requirements.** Already covered — bar timestamps + the existing cost atlas.
- **Distinct 2 · Support 3 · Complexity 5 · Overfit-resist 2 · Data-fit 5 · Sample 5 · Precommit 3**
- **Priority:** medium-low. It is *context*, not a new entry mechanism; it risks
  re-deriving the cost effect under a new name. Best pursued as a context overlay
  *after* a stronger entry primitive exists, or folded into Lane C.

## Lane B — Volatility expansion / compression

ATR percentile, range contraction, breakout expansion, realized-vol regimes.

- **Reason.** `atr_at_entry` separated (|AUC−0.5| = 0.068) more than any structural
  C022 signal feature.
- **Risk.** Prior volatility-breakout attempts already failed in this repo —
  CAMPAIGN_010 session_breakout (REJECT, 0/8 folds), CAMPAIGN_017 weekly volatility
  contraction breakout (REJECT, dedup-safe cluster). A new vol lane must be
  *materially* different from these, not a re-run.
- **Data requirements.** Covered (ATR/range from M1/M15).
- **Distinct 2 · Support 3 · Complexity 4 · Overfit-resist 2 · Data-fit 5 · Sample 5 · Precommit 3**
- **Priority:** low. Heavily explored and repeatedly rejected here; the weak C022 vol
  separation does not justify re-opening a lane with this much negative prior.

## Lane C — Cost / spread-aware tradeability filter

Not alpha generation — reduce structurally untradeable entries.

- **Reason.** `spread_to_atr_pct` was the single largest separator (|AUC−0.5| = 0.077)
  with a clean monotonic quintile decline (win-rate 0.43→0.25 as spread/ATR rises).
- **Risk.** Mechanical, not edge — cost is subtracted from net R by construction.
  A spread filter likely only **reduces trade count**, not creates edge; it cannot
  rescue a signal that is zero-edge gross.
- **Data requirements.** Covered (cost atlas already exists).
- **Distinct 4 · Support 4 · Complexity 5 · Overfit-resist 4 · Data-fit 5 · Sample 4 · Precommit 4**
- **Priority:** medium — but as **process/tradeability infrastructure**, explicitly not
  as an alpha thesis. Valuable as a guardrail on any *future* signal; on its own it
  discovers no edge. Strong overlap with Lane G.

## Lane D — Market-microstructure-style confirmation

Liquidity sweep + displacement, break/retest, range-expansion candle, failed-continuation trap.

- **Reason.** C022 failed *because the M15 EMA reclaim trigger is too weak*
  (`m15_reclaim_distance_atr` AUC 0.494/0.485 — literally inert). The diagnostic
  pointed squarely at entry confirmation. This lane replaces the weak trigger with
  stronger, structurally different proof of an order-flow shift — exactly the lever
  the closeout says is untested, rather than the "re-gate the same signal" lever that
  is empty.
- **Risk.** Harder to encode without hindsight; sweep/displacement/trap definitions
  can smuggle lookahead if not carefully causal. Must be detector-only and
  decision-bar-anchored (the C022 feature-separation reconstruction already
  demonstrated lookahead-safe, side-agreement-verified encoding, so the pattern is
  established here).
- **Data requirements.** M1/M15 OHLC — covered. No new data feed required.
- **Distinct 5 · Support 4 · Complexity 2 · Overfit-resist 3 · Data-fit 4 · Sample 3 · Precommit 4**
- **Priority:** **high.** It directly targets the diagnosed defect (weak trigger),
  is the most structurally distinct from the retired family, and can be run as a
  read-only **diagnostic** (presence on C022 winners vs losers) before any campaign —
  no threshold-mining required to learn whether any primitive separates at all.

## Lane E — Single-pair (USD_JPY) specialist diagnostic

Especially USD_JPY or pairs that are repeatedly "less bad."

- **Reason.** The universal seven-pair rule may be too broad.
- **Risk.** Pair-specific overfit; and the C022 MFE/MAE diagnostic showed stop-outs
  are **not** concentrated by pair (hard-stop share 0.55–0.61 across all seven), and
  USD_JPY was not meaningfully better. The current evidence gives little reason to
  expect a single-pair *edge* hiding in the pullback signal.
- **Data requirements.** Covered, but per-pair sample shrinks ~7× (USD_JPY ≈ 299 C022
  base trades).
- **Distinct 2 · Support 2 · Complexity 4 · Overfit-resist 1 · Data-fit 5 · Sample 2 · Precommit 2**
- **Priority (as a *standalone* thesis):** low. Single-pair specialization on its own
  — looking for a USD_JPY-specific edge *in the already-dead pullback signal* — has
  weak support, high overfit risk, and small samples.

### Amendment (2026-05-28): USD_JPY adopted as the *scope* for Lane D, not as a standalone thesis

Single-pair specialization is **not** selected as its own lane. Instead, **USD_JPY is
adopted as the scope of the Lane D microstructure-confirmation diagnostic** (see
[`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md) §1a). This is
a **research-scoping decision**, not a claim that USD_JPY has edge. The distinction
matters: Lane E-as-thesis hunts for a pair-specific edge in the retired signal (weak);
USD_JPY-as-scope simply runs the *new* microstructure question on the cleanest single
pair first.

**Why USD_JPY-only microstructure confirmation is preferable to testing all seven pairs immediately:**

- **Fewer confounds.** One pair removes cross-pair heterogeneity, so a separation
  result is attributable to the primitive, not to which pairs dominated the basket.
- **Faster runs.** ~1/7 the data per iteration → quicker diagnostic turnaround.
- **Clearer session behavior.** USD_JPY has a distinct Tokyo/London/NY session
  personality that is interpretable on its own rather than averaged across seven pairs.
- **Clearer spread/ATR behavior.** A single, well-characterized cost/volatility profile
  instead of seven superimposed ones — important given cost was the largest C022
  context separator.
- **Clearer macro/session personality.** One instrument's narrative is inspectable;
  basket failure is not.
- **Simpler future paper/demo monitoring** *if* a strategy ever earned it — a single
  instrument is operationally simpler to watch (far-future consideration only).

**But — limits that this scope does not change:**

- **Not enough evidence to approve** anything; `approved_strategies.yaml` stays
  `approved: []`.
- **Not enough evidence to launch C024** — readiness is still `NOT_READY` until a
  USD_JPY diagnostic shows real, stable, non-overfit separation.
- **Not enough evidence to demo trade** — narrowing scope brings demo no closer.
- **Pair-specific overfit risk is higher, not lower** — a single-pair result carries a
  heightened generalization burden and must clear the same five-part C024 bar
  (no gate-lowering) plus a clean USD_JPY train/validation/test lockbox if it ever
  becomes a campaign.

## Lane F — News / calendar / event lane revisit

Event-time windows, macro-release effects.

- **Reason.** Structurally different from indicator confluence.
- **Risk.** Fixture/calendar quality and low sample size. The repo already has
  CAMPAIGN_014 calendar_event_window_anomaly history and a calendar fixture lane with
  known quality caveats; a revisit inherits those data-quality risks.
- **Data requirements.** **Not** covered by M1/M15 alone — needs a reliable economic
  calendar with accurate release timestamps, the weakest data dependency of any lane.
- **Distinct 4 · Support 2 · Complexity 2 · Overfit-resist 2 · Data-fit 2 · Sample 2 · Precommit 3**
- **Priority:** low-medium. Genuinely distinct, but gated on calendar data quality and
  small event samples; not the cheapest or best-supported next step.

## Lane G — Pause strategy campaigns; deepen execution/cost/parity infrastructure

- **Reason.** Many campaigns have failed; perhaps the process should stay diagnostic
  and keep hardening cost/parity/execution realism.
- **Risk.** No new edge discovery — indefinitely deferring the entry-edge question.
- **Data requirements.** Covered.
- **Distinct 5 (it's not a strategy thesis at all) · Support 4 · Complexity 4 · Overfit-resist 5 · Data-fit 5 · Sample n/a · Precommit 5**
- **Priority:** medium. The honest "null" option and always defensible under the
  freeze. But the entry-confirmation question (Lane D) is now *specifically* posed by
  the C022 diagnostics and is cheap to answer read-only; pure infrastructure work
  would leave that open. Lane G's strongest element — cost/tradeability guardrails —
  is already captured by Lane C.

---

## Summary scoring table

| Lane | Distinct | Support | Complexity | Overfit-resist | Data-fit | Sample | Precommit | Priority |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| A · Session/time-of-day | 2 | 3 | 5 | 2 | 5 | 5 | 3 | med-low |
| B · Volatility expansion/compression | 2 | 3 | 4 | 2 | 5 | 5 | 3 | low |
| C · Cost/spread tradeability filter | 4 | 4 | 5 | 4 | 5 | 4 | 4 | med (process) |
| **D · Microstructure confirmation** | **5** | **4** | **2** | **3** | **4** | **3** | **4** | **high** |
| E · Single-pair specialization (standalone thesis) | 2 | 2 | 4 | 1 | 5 | 2 | 2 | low (but USD_JPY adopted as *scope* for D) |
| F · News/calendar/event | 4 | 2 | 2 | 2 | 2 | 2 | 3 | low-med |
| G · Pause / infra deepening | 5 | 4 | 4 | 5 | 5 | — | 5 | med (null) |

## Reading (not a decision — see Phase 4)

- **Lane D (microstructure confirmation)** is the only lane that is both highly
  structurally distinct **and** directly targets the diagnosed defect (the inert M15
  EMA-reclaim trigger). It can begin as a **read-only diagnostic** — measuring whether
  any confirmation primitive separates C022 winners from losers — which is precisely
  the falsifiable, no-threshold-mining first step the freeze favors. **Per the
  2026-05-28 amendment, the next Lane D diagnostic is scoped to USD_JPY only** (Lane E
  reframed as a *scope* for D, not a standalone thesis) — fewer confounds, faster runs,
  and a single interpretable session/cost personality, with no relaxation of the
  evidence bar.
- **Lane C / Lane G** are the strongest *non-alpha* options and remain valuable as
  tradeability/process guardrails regardless of which alpha lane is chosen.
- **Lanes A, B, E, F** are weaker: A/B risk re-deriving mechanical context effects
  already seen, B/E carry strong negative priors, and F is gated on calendar-data
  quality.

The selection is made in
[`NEXT_THESIS_SELECTION_DECISION.md`](NEXT_THESIS_SELECTION_DECISION.md).
