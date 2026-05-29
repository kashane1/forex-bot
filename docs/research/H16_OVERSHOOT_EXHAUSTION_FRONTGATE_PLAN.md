# H16 overshoot-exhaustion fade — front-gate screen PLAN

**Branch:** `research-non-time-bar-overshoot-frontgate-001`
**Date:** 2026-05-29
**Type:** **front-gate SCREEN only.** Not a campaign, not evidence, not
train/validation/test, no lockbox, no approval, no edge claim.

> **Branch note:** prior sprints (feasibility, thesis-discovery) are unmerged on
> `origin/main`. This screen reuses the non-time-bar infra and references the discovery
> docs, so it is **stacked on the thesis-discovery tip** (`5cb9bd6`) to retain context.
> It adds a small, tested diagnostic harness + compact docs; it creates no campaign,
> no backtest runner, no train/val/test split.

---

## 0. Purpose

Determine whether hypothesis **H16 (overshoot-exhaustion fade)** deserves a *future*
campaign scaffold — **nothing more**. The output is a single front-gate verdict
(`FAIL` / `INCONCLUSIVE` / `PASS`). A PASS authorises only a *separate, later* scaffold
sprint; it does **not** create or imply a campaign here.

**Success ≠ finding a strategy.** Success = a defensible, cost- and null-aware answer to
"is there any conditional information in overshoot worth a campaign?"

## 1. Why H16 survived screening (recap from discovery sprint)

From `NON_TIME_BAR_HYPOTHESIS_RANKING.md` / `..._FINAL_SHORTLIST.md`, H16 ranked #1
because it is:
- **Distinct** from every rejected family — it conditions on **bar-completion geometry**
  (overshoot magnitude), not trend/breakout (C029/C025), not price-level reversion
  (C027/C008), not time-series momentum (C031).
- **Cheapest to study** — the `overshoot_pips` metric is already produced by the
  feasibility tooling and the `non_time_bars` builders.
- **Intraday / financing-free** — short holding (next 1–3 bars), so it dodges the
  ≈4×-spread overnight-financing channel that defeated C031.
- **Falsifiable** — "large overshoot → reversion" is a clean conditional claim with an
  obvious null.

## 2. What makes it distinct (so the screen is not a re-run)

- No trend filter, no MTF confluence, no breakout entry, no carry, no long holds (the
  prompt's explicit avoid-list).
- The signal is **completion-overshoot magnitude**, measured on a **cost-feasible**
  bar (range ≥ 30 pip, per the feasibility study), faded (counter to completion
  direction) over a **short event-time horizon**.

## 3. What this screen will and will not do

**Will:** measure overshoot **distributions** (Phase 2); measure **conditional forward
returns** after overshoot, by bucket and horizon, *signed as a fade* (Phase 3); compare
the conditional move to **realistic cost** (Phase 4); compare to **unconditional and
shuffled-overshoot nulls** (Phase 5); render a **verdict** (Phase 6).

**Will not:** build a backtest runner, open positions, compute PnL/equity, place stops,
create train/val/test splits, touch the test lockbox, optimise thresholds, or emit a
tradeable signal. It measures **conditional distributions only**.

## 4. Method guardrails (pre-registered to avoid known traps)

- **Window:** C029 **train** window `2021-05-27 → 2023-12-31` only — the test lockbox is
  never read.
- **Pairs:** USD_JPY, EUR_USD, GBP_USD (the prompt's focus set).
- **Bar/threshold (pre-declared, no tuning):** **30-pip range bars** — the single
  cost-feasible threshold the feasibility study found viable on *all* majors. One
  threshold, declared up front; no sweep-and-pick (the C028 selection-noise trap).
- **Overshoot buckets (pre-declared):** per-pair **quartiles** (small/medium/large/
  extreme) + an explicit **top-5% tail**. Fixed edges; not optimised.
- **Horizons:** next **1 / 2 / 3** completed bars (event time).
- **Fade convention:** `fade_return = −completion_dir × (mid_close[i+k] − mid_close[i])`;
  **positive ⇒ price reverted** (exhaustion), negative ⇒ continuation.
- **Cost model:** the C029 model — round-trip ≈ per-pair spread + 2×0.2-pip slippage.
- **Null:** unconditional fade-return baseline + a **seeded shuffle** of overshoot
  labels vs forward returns (breaks the conditioning link) → null distribution of the
  top-bucket mean.

## 5. Evidence that would justify a future campaign (PASS)

All of:
- A **monotone-ish** relationship: reversion strengthens with overshoot magnitude
  (large/extreme buckets fade-positive, clearly above small bucket).
- The large/extreme-bucket conditional fade move **materially exceeds round-trip cost**
  at a tradeable horizon.
- The effect is **outside the shuffled null** (observed top-bucket mean beyond ~95th
  null percentile) and exceeds the **unconditional** baseline.
- Present on **≥ 2 of the 3 pairs** (not a single-pair artifact).

## 6. Evidence that would kill it immediately (FAIL)

Any of:
- No bucket gradient / large-overshoot bucket not fade-positive (or it's *continuation*).
- Conditional move **below cost** at all tradeable horizons.
- Indistinguishable from the shuffled/unconditional null.
- Effect only on one pair, or only in expensive (rollover) sessions where cost eats it.

## 7. Phase → deliverable map

| phase | doc / artifact |
|---|---|
| 0 | this plan |
| 1 | `H16_OVERSHOOT_EXHAUSTION_HYPOTHESIS.md` |
| 2 | `H16_OVERSHOOT_DISTRIBUTION_STUDY.md` (+ harness + tests) |
| 3 | `H16_POST_OVERSHOOT_BEHAVIOR_STUDY.md` |
| 4 | `H16_COST_FEASIBILITY_STUDY.md` |
| 5 | `H16_NULL_COMPARISON.md` |
| 6 | `H16_FRONTGATE_DECISION.md` (FAIL / INCONCLUSIVE / PASS) |
| 7 | `NEXT_PROMPT_AFTER_H16_FRONTGATE.md` |
| 8 | validation + `H16_OVERSHOOT_EXHAUSTION_FRONTGATE_SUMMARY.md` |

Compact diagnostics under `research/h16_overshoot_frontgate/` (gitignored bulky;
whitelist compact summaries). No raw M1, no full bars, no ledgers committed.
