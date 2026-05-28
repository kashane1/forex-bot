# Next-Thesis Selection Decision

**Date:** 2026-05-28 · **Sprint:** `research-post-c022-family-retirement-and-new-thesis-selection-001`
**Type:** selection decision. Approves nothing, executes nothing, creates no campaign, proposes no threshold.

> This decision selects **one** next research lane to pursue as a **read-only
> diagnostic**. It is **not** a campaign, **not** C024, and **not** an approval. The
> selected lane must be independently precommitted in a future sprint before any
> execution. Inputs:
> [`NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md`](NEXT_STRUCTURALLY_DIFFERENT_THESIS_OPTIONS.md),
> [`C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md`](C022_C023_PULLBACK_RESOLUTION_FAMILY_CLOSEOUT.md).

---

## 1. Selected lane

### Lane D — Market-microstructure-style confirmation diagnostic

Pursued first as a **read-only diagnostic** (presence of confirmation primitives on
C022 winners vs losers), **not** a full campaign and **not** C024.

## 1a. Scope amendment (2026-05-28) — USD_JPY-only

**The selected lane is unchanged: market-microstructure-style confirmation
diagnostic.** What changes here is the **scope of the next diagnostic sprint**, which
is narrowed to **USD_JPY only** (not the seven-pair universe).

### Why USD_JPY-only is justified as a research-scoping decision

- **Seven-pair universal rules have repeatedly failed.** A single static rule across
  EUR_USD/GBP_USD/USD_JPY/AUD_USD/USD_CAD/USD_CHF/NZD_USD has been rejected across
  many campaigns (C010, C015–C017, C020–C022). A universal rule may simply be too
  blunt an instrument for *discovery*; narrowing reduces the chance that a real
  per-pair effect is averaged away into a basket null.
- **Single-pair research reduces confounding and speeds iteration.** One pair removes
  cross-pair spread/volatility/session heterogeneity and shrinks run time, so each
  diagnostic question is answered faster and more cleanly.
- **USD_JPY has repeatedly appeared "less bad" / near-flat** in prior failed evidence
  (never strong enough to promote). That makes it the most defensible single pair to
  interrogate first — not because it has proven edge (it has not), but because it is
  the least-uniformly-bad starting point.
- **USD_JPY is operationally cleaner for eventual demo research** *if* a strategy ever
  earned it — a single, well-understood instrument is simpler to monitor than a basket.
  (This is a far-future consideration only; nothing here brings demo closer.)
- **Pair-specific research is easier to interpret** than broad-basket failure: a
  USD_JPY-only separation result has a single, inspectable session/macro personality
  behind it rather than seven superimposed ones.
- **Still diagnostic only.** This is read-only winner/loser separation analysis on a
  narrowed scope. It is **not** proof of edge, **not** a campaign, and **not** C024.

### Risks this scope introduces (and how they are bounded)

- **Higher overfit risk.** A single pair invites curve-fitting. Mitigation: the
  diagnostic still reports per train/validation split, keeps post-hoc labels out of
  features, and applies the same 0.05 negligibility floor.
- **Smaller universe / smaller sample.** USD_JPY is ~1/7 of the corpus
  (≈299 C022 base trades by the MFE/MAE diagnostic). Sample-size preservation is an
  explicit output of the next sprint; a primitive that separates only on a tiny
  residual sample is not a positive result.
- **Stricter walk-forward discipline required later.** If this ever becomes a
  campaign, it needs a clean train/validation/test lockbox — single-pair results are
  *more*, not less, demanding of out-of-sample confirmation.
- **No gate-lowering.** Narrowing to one pair must **not** lower the evidence bar.
  The five-part C024 readiness bar (§5) applies unchanged; "it's only one pair" is
  never a reason to relax it.
- **Not approval-adjacent.** A USD_JPY focus does not mean USD_JPY has edge, does not
  approve anything, and does not move paper/demo/live any closer.

## 2. Why selected

1. **It targets the actual diagnosed defect.** The C022 closeout localized the
   failure to the **entry trigger**: `m15_reclaim_distance_atr` is inert
   (AUC 0.494/0.485). Stop, time, ADX, and cost-free variants all stay negative, so
   the problem is not mechanics around the trigger — it is the trigger itself. Lane D
   replaces the weak M15 EMA reclaim with **stronger, structurally different
   confirmation** (sweep+displacement, break/retest, range expansion, trap
   avoidance). This is the one untested lever; "re-gate the same signal" is empty.
2. **It is the most structurally distinct lane.** It changes *what is detected* (an
   order-flow / micro-structure shift) rather than re-filtering the H4→H1→M15
   confluence on context (cost/vol/hour), which the evidence shows is mechanical and
   weak.
3. **It can start falsifiable and threshold-free.** The first step measures whether
   *any* confirmation primitive separates winners from losers at all — a read-only
   presence/separation diagnostic on the existing C022 trade set. If nothing
   separates, the lane is closed cheaply with no campaign and no threshold-mining. The
   C022 feature-separation sprint already established the lookahead-safe,
   side-agreement-verified reconstruction pattern this would reuse.
4. **It needs no new data.** M1/M15 OHLC already available; no calendar feed, no new
   ingest, no live calls.

## 3. Why the other lanes were not selected

- **A (session/time-of-day)** and **B (volatility)** rest on the *context* separators
  (`hour`, `atr_at_entry`), which are weak (AUC ≲ 0.58) and risk re-deriving the
  mechanical cost effect under a new name; B additionally carries strong negative
  priors (CAMPAIGN_010, CAMPAIGN_017 both REJECT). Neither changes *what* is detected.
- **C (cost/tradeability)** is valuable but is **process/guardrail infrastructure**,
  not an alpha thesis — it can only reduce untradeable entries, not create edge. It is
  recommended as a *companion overlay* to whatever signal lane runs, not the headline
  lane.
- **E (single-pair)** has weak support (stop-outs are *not* pair-concentrated; USD_JPY
  not meaningfully better) and high overfit risk on ~7× smaller samples.
- **F (news/calendar)** is genuinely distinct but gated on economic-calendar data
  quality (the weakest data dependency) and small event samples.
- **G (pause/infra)** is the honest null and always defensible, but it would leave the
  now-specific entry-confirmation question unanswered when that question is cheap to
  answer read-only. Its best element (cost guardrails) is already captured by C.

## 4. What the next sprint should produce

A **read-only, USD_JPY-only confirmation-primitive diagnostic** (per §1a), not a
campaign:

1. An inventory of candidate M15 confirmation primitives (sweep+displacement,
   reclaim+impulse, reclaim+break-of-micro-swing, reclaim+retest-hold, range expansion
   after compression, failed-reclaim/trap), plus USD_JPY session-aware context
   (Tokyo/London/NY) and spread/ATR context.
2. Read-only, decision-bar-anchored, lookahead-safe **detectors** for each
   (no strategy-logic edits; side-agreement / causality checks as in the C022
   reconstruction).
3. A winner-vs-loser **separation comparison** of each primitive's presence on the
   **USD_JPY subset** of the existing C022 trade set (same AUC / quintile method as the
   feature-separation sprint), reported per train/validation split, **with the USD_JPY
   sample size reported at every step**.
4. A **readiness decision**: does any primitive separate USD_JPY winners from losers in
   both splits, with plausible non-overfit logic, while reducing straight-to-stop
   behavior and preserving a usable sample? Output is `READY_FOR_PRECOMMIT` /
   `NOT_READY` for a future **USD_JPY-only** C024 — **no C024 created in that sprint
   either**.

## 5. What would count as enough evidence to justify a future C024 precommit

A future C024 (microstructure-confirmation entry) is justified only if the Lane D
diagnostic shows **all** of:

1. **At least one confirmation primitive separates** C022 winners from losers with a
   non-negligible effect (|AUC−0.5| materially above the 0.05 floor and above the best
   structural C022 feature) in **both** train and validation.
2. **Plausible market logic** for the separation (an order-flow / liquidity mechanism),
   not a curve-fit artifact.
3. **Not pair/session/cost overfit** — the separation survives controlling for the
   known mechanical context effects (cost, hour, volatility).
4. **No outcome leakage** — detectors are strictly causal / decision-bar-anchored.
5. **Plausible economic materiality** — the effect is large enough that a confirmation
   filter could plausibly move a REJECT toward non-negative expectancy *while keeping a
   usable sample*, judged before (not after) any threshold is chosen.

If those hold, the *next* sprint after that precommits C024 out-of-sample. If they do
not, Lane D is closed like the pullback family — no campaign, no approval.

**Single-pair note (per §1a).** Under the USD_JPY-only scope, this bar is **not
relaxed**. Criterion 3 becomes "not session/cost/volatility overfit *within* USD_JPY,"
and a USD_JPY-only result additionally inherits a heightened generalization burden:
because it cannot borrow strength from other pairs, any future USD_JPY C024 must show
its effect survives a clean USD_JPY train/validation/test lockbox. "It's only one
pair" is never grounds to lower the bar.

## 6. What is explicitly forbidden

- **No threshold mining.** Do not select a primitive cut-off from the same data used
  to measure separation and call it an edge.
- **No campaign execution.** The next sprint is read-only diagnostic; it runs no
  CAMPAIGN_024 and does not execute C023.
- **No approval.** `configs/approved_strategies.yaml` stays `approved: []`.
- **No paper/demo/live**, no broker/executor/order/live changes, no OANDA
  mutation/order calls, no live credentials.
- **No verdict changes** and no rewriting of historical metrics.

## 7. Companion recommendation (non-binding)

Carry **Lane C (cost/tradeability guardrail)** as a *secondary overlay* in any future
signal sprint — not as the alpha thesis, but as a tradeability filter applied **after**
a real signal is demonstrated. This is bookkeeping/process hardening, not edge
discovery, and must never be presented as alpha.
