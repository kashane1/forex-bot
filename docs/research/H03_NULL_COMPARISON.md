# H03 thin-move fade — null comparison (Phase 5)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 5
**Type:** null / matched-null comparison. No PnL, no approval.
**Artifacts:** `research/h03_thin_move_frontgate/null_study.json`,
`research/h03_thin_move_frontgate/behavior_study.json`.

> Two comparators, per the plan and the repo's lab methodology:
> 1. **Unconditional baseline** — the mean fade over *all* bars (does conditioning on
>    participation beat doing nothing?).
> 2. **Shuffled-participation null** — 2,000 seeded permutations that randomly re-assign
>    which fades belong to a group of the low-bucket's size, breaking the
>    participation↔return link. This is the **structure-matched** null (C027 lesson): it
>    asks whether being *thin* carries information beyond being a *random* set of bars of
>    equal size. Seed 20260529; identical method to the H16 screen.

---

## 1. Shuffled-participation null — low bucket

`one_sided_p_ge` = P(null group mean ≥ observed). Small ⇒ observed unusually high
(reversion concentrated in thin bars). The 95th-percentile bar is `p_ge < 0.05`.

| pair | h1 | h2 | h3 |
|---|---|---|---|
| EUR_USD | 0.281 | 0.170 | **0.0525** |
| GBP_USD | 0.517 | 0.343 | 0.424 |
| USD_JPY | 0.277 | 0.440 | 0.762 |

## 2. Shuffled-participation null — ultra-thin (bottom-decile) tail

| pair | h1 | h2 | h3 |
|---|---|---|---|
| EUR_USD | 0.910 | 0.515 | 0.116 |
| GBP_USD | 0.630 | 0.552 | 0.370 |
| USD_JPY | 0.179 | 0.167 | 0.424 |

## 3. Reading the null

**Not one of the 18 cells (3 pairs × 3 horizons × {low, ultra-thin}) crosses the
pre-registered 95th-percentile bar.** The single closest is **EUR_USD low h3 at
`p_ge = 0.0525` (pct_rank 0.9475)** — which is *just inside* the null, not beyond it.

That lone near-miss is exactly what multiple comparisons predict, and the C028 lesson is
explicit about not chasing it:

- With 18 cells, the expected number with `p_ge < 0.05` under the global null is ≈ 0.9.
  Observing **zero** strictly-significant cells and one borderline cell is **fully
  consistent with no effect.**
- A Bonferroni-style bar for 18 cells is `≈ 0.0028`; EUR_USD low h3 (0.0525) misses it by
  ~19×.
- It is the **longest horizon** (most drift-contaminated), on the **single** pair that
  also happened to clear cost (§Phase 4), and it is **cost-confounded** (thin EUR bars
  carry the wider low-bucket spread). It is the textbook profile of **selection noise**,
  not edge.

## 4. Unconditional baseline comparison

Conditioning on low participation does **not** beat doing nothing:

- **EUR_USD:** low-bucket fade (+1.75 / +2.33 / +3.97) is only modestly above
  unconditional (+1.22 / +1.09 / +1.32), and the null means for a *random* equal-size
  group (1.21 / 1.09 / 1.28) essentially *equal* the unconditional — i.e. the low bucket
  sits where a random draw sits.
- **GBP_USD:** low-bucket (+0.46 / +1.26 / +0.51) straddles unconditional (+0.49 / +0.84
  / +0.22); null mean ≈ unconditional. No lift.
- **USD_JPY:** low-bucket (+0.21 / +0.57 / −0.68) ≈ unconditional shifted; h3 is *below*
  baseline. No lift.

The "low−high gradient" of Phase 3 is therefore **not** the low bucket beating the null —
it is the **high** bucket sitting *below* baseline (slow bars continue a little). Thin
participation adds no information over a random set of bars of the same size.

## 5. Matched-null note (the G4 point)

Range bars hold travel ≈ fixed, so the shuffle-within-pair null is already an
approximately move-matched comparator. The residual confound — thin bars overshoot *more*
(Phase 2 §3.2) — would, if anything, *inflate* any apparent thin-bucket reversion via the
overshoot channel; yet even with that tailwind the low bucket stays inside the null. This
strengthens, not weakens, the null verdict: there is no participation-specific signal
once you account for the fact that being assigned to a thin-sized group is no better than
random.

## 6. Read

H03 is **null-indistinguishable** on all three pairs by both comparators (FAIL criterion
§7.4). The shuffled-participation null is not beaten anywhere (one borderline EUR_USD
low-h3 cell is multiple-comparison-expected and cost-confounded), and conditioning on
participation provides no lift over the unconditional baseline.
