# H03 thin-move fade — front-gate screen PLAN

**Branch:** `research-non-time-bar-thin-move-frontgate-001`
**Date:** 2026-05-29
**Type:** **front-gate SCREEN only.** Not a campaign, not evidence, not
train/validation/test, no lockbox, no approval, no edge claim.

> **Branch note:** this screen starts from clean, updated `origin/main`
> (`4ad9495`, which already contains the merged H16 overshoot screen). It reuses
> the non-time-bar infra (`forex_bot.data.non_time_bars`) and the H16 screen
> pattern. It adds a small, tested diagnostic harness + compact docs; it creates
> **no** campaign, **no** backtest runner, **no** train/val/test split.

---

## 0. Purpose

Determine whether hypothesis **H03 (thin-move fade)** deserves a *future* campaign
scaffold — **nothing more**. The output is a single front-gate verdict
(`FAIL_FRONT_GATE` / `INCONCLUSIVE` / `PASS_FRONT_GATE`). A PASS authorises only a
*separate, later* scaffold sprint; it does **not** create or imply a campaign here.

**Success ≠ finding a strategy.** Success = a defensible, cost- and null-aware answer
to "is there any conditional information in **participation (tick-count volume)** worth
a campaign?" A clean null is a successful outcome.

H03 is the **last** pre-registered front-gate candidate in the non-time-bar
thesis-discovery shortlist. H16 (the #1 candidate) already `FAIL_FRONT_GATE`. If H03
also fails, Phase 7 addresses whether to retire directional/conditional non-time-bar
search on this corpus.

## 1. The hypothesis (recap from discovery sprint)

From `NON_TIME_BAR_FINAL_SHORTLIST.md` (#2) and `NON_TIME_BAR_HYPOTHESIS_RANKING.md`
(H03, FRONT_GATE_CANDIDATE):

> When a range/volatility bar completes its travel on **unusually low tick-volume**
> (a "thin" move), test short-horizon **reversion**; contrast with high-volume
> completions. The signal is **travel-per-unit-volume**, not travel itself; intraday
> exit (financing-free).

**Core intuition:** moves that occur during unusually low participation may be less
reliable (more prone to mean-reversion) than moves that occur during normal/high
participation. We are *only* testing whether this conditional behaviour exists — not
building a signal.

## 2. Why H03 survived screening (and is now the candidate)

- **Distinct** from every rejected family — it conditions on **participation
  (volume) as a move-quality filter**, not trend/breakout (C029/C025), not price-level
  reversion (C027/C008), not time-series momentum (C031), not completion geometry
  (H16, already failed). No prior campaign used volume as a move-quality conditioner.
- **Cheap** — per-bar tick-count volume is already summed by the `non_time_bars`
  builders (`RangeBar.volume`); no new data needed.
- **Intraday / financing-free** — short holding (next 1–3 bars), so it dodges the
  ≈4×-spread overnight-financing channel that defeated C031.
- **Falsifiable** — "low-participation moves revert more than high-participation
  moves" is a clean conditional claim with an obvious null.

## 3. Why range bars are the right vehicle (the G4 move-matched point)

The shortlist warned: *"matched null must hold the move fixed so the volume
conditioning is what's tested (G4)."* **Range bars hold travel ≈ fixed** (each bar
spans `threshold + a small overshoot`). Conditioning on **volume across bars of
nearly-equal travel** is therefore already approximately move-matched — the *amount*
moved is held roughly constant and only the *participation that produced it* varies.
This is exactly the disagreement H03 targets ("travel ÷ volume"): with travel ~fixed,
ranking by travel/volume ≈ ranking by 1/volume, so **low volume = thin move**.

Confound to verify (Phase 2): if thin (low-volume) bars systematically carry larger
overshoot, longer duration, or wider spreads, the volume effect is confounded — these
are reported explicitly.

## 4. What this screen will and will not do

**Will:** measure the **participation (volume) distribution** by pair / session /
spread state (Phase 2); measure **conditional forward fade returns** after completions
by participation bucket and horizon (Phase 3); compare the conditional move to
**realistic cost** (Phase 4); compare to **unconditional and shuffled-participation
nulls** (Phase 5); render a **verdict** (Phase 6); make a **lane decision** (Phase 7).

**Will not:** build a backtest runner, open positions, compute PnL/equity, place stops,
create train/val/test splits, touch the test lockbox, optimise thresholds, or emit a
tradeable signal. It measures **conditional distributions only**.

## 5. Method guardrails (pre-registered to avoid known traps)

- **Window:** C029 **train** window `2021-05-27 → 2023-12-31` only — the test lockbox is
  never read.
- **Pairs:** EUR_USD, GBP_USD, USD_JPY (the prompt's focus set).
- **Bar/threshold (pre-declared, no tuning):** **30-pip range bars** — the single
  cost-feasible threshold the feasibility study found viable on *all* majors, and the
  same one H16 used (keeps the two screens comparable). One threshold, declared up
  front; no sweep-and-pick (the C028 selection-noise trap).
- **Participation metric (pre-declared):** per-bar **tick-count volume** = sum of the
  M1 `volume` (OANDA tick count, a documented tick-count proxy for FX) over the bar's
  constituent M1 candles. **Lower volume ⇒ thinner participation.** We also report the
  `travel_pips / volume` ratio for completeness, but bucket on volume (travel ~fixed).
- **Participation buckets (pre-declared):** per-pair **tertiles** → `low` / `medium` /
  `high` participation (terciles, not quartiles, to keep cell sizes ample), plus an
  explicit **bottom-decile "ultra-thin" tail** (the mirror of H16's top-5% tail, but on
  the *low* side, since thin = low). Fixed edges; not optimised.
- **Horizons:** next **1 / 2 / 3** completed bars (event time).
- **Fade convention (same as H16):** `fade_k(i) = −completion_dir(i) ×
  (mid_close[i+k] − mid_close[i])` in pips; **positive ⇒ price reverted** against the
  completion move, negative ⇒ continuation. H03 predicts the **low-participation**
  bucket reverts **more** (higher reversion rate / more positive fade) than the
  high-participation bucket.
- **Cost model:** the C029 model — round-trip ≈ per-pair spread + 2×0.2-pip slippage.
- **Null:** unconditional fade-return baseline + a **seeded shuffle** of participation
  labels vs forward returns (breaks the conditioning link) → null distribution of the
  low-participation (and ultra-thin tail) group mean.

## 6. Evidence that would justify a future campaign (PASS)

All of:
- A **monotone-ish** relationship: reversion **strengthens as participation falls**
  (low / ultra-thin buckets fade-positive, clearly above the high bucket).
- The low-participation / ultra-thin conditional fade move **materially exceeds
  round-trip cost** at a tradeable horizon.
- The effect is **outside the shuffled null** (observed low-participation mean beyond
  ~95th null percentile) and exceeds the **unconditional** baseline.
- Present on **≥ 2 of the 3 pairs** (not a single-pair artifact), and not confined to
  expensive (rollover) sessions where cost eats it.

## 7. Evidence that would kill it immediately (FAIL)

Any of:
- No participation gradient / low-participation bucket not more reversion (or it is
  *continuation*).
- Conditional move **below cost** at all tradeable horizons (esp. if thin bars carry
  *wider* spreads — a cost confound).
- Indistinguishable from the shuffled / unconditional null.
- Effect only on one pair, or only in expensive (rollover/Tokyo-thin) sessions where
  cost eats it.

## 8. Phase → deliverable map

| phase | doc / artifact |
|---|---|
| 0 | this plan (`H03_THIN_MOVE_FRONTGATE_PLAN.md`) |
| 1 | `H03_THIN_MOVE_HYPOTHESIS.md` |
| 2 | `H03_PARTICIPATION_DISTRIBUTION_STUDY.md` (+ harness + tests) |
| 3 | conditional-behavior study (in the harness JSON + decision docs) |
| 4 | `H03_COST_FEASIBILITY_STUDY.md` |
| 5 | `H03_NULL_COMPARISON.md` |
| 6 | `H03_FRONTGATE_DECISION.md` (FAIL / INCONCLUSIVE / PASS) |
| 7 | `NON_TIME_BAR_LANE_FINAL_DECISION.md` |
| 8 | validation + `H03_THIN_MOVE_FRONTGATE_SUMMARY.md` |

Compact diagnostics under `research/h03_thin_move_frontgate/` (bulky raw gitignored;
whitelist compact summaries only). No raw M1, no full bars, no ledgers committed.

## 9. Hard constraints (restated)

No CAMPAIGN_030; no campaign of any number; no strategy approved; approved strategies
untouched; no paper/demo/live; no OANDA APIs / live credentials; no backtesting runner;
no lockbox opened; no train/validation/test evidence. This is a front-gate screen only.
