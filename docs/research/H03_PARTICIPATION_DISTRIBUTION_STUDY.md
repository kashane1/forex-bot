# H03 thin-move fade — participation distribution study (Phase 2)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 2
**Type:** conditional-distribution measurement. No PnL, no positions, no approval.
**Artifacts:** `research/h03_thin_move_frontgate/distribution_study.json`,
`scripts/screen_h03_thin_move.py`, `src/forex_bot/research/thin_move_screen.py`,
`tests/unit/test_thin_move_screen.py`.

> 30-pip range bars, C029 train window (2021-05-27 → 2023-12-31), EUR_USD / GBP_USD /
> USD_JPY. Participation = per-bar tick-count volume. Lockbox untouched.

---

## 1. Sample

| pair | completed 30-pip range bars |
|---|---:|
| EUR_USD | 2,132 |
| GBP_USD | 3,853 |
| USD_JPY | 4,403 |

Ample for tertile + decile-tail conditioning, matching the H16 screen's sample scale.

## 2. Participation (tick-count volume) distribution

Per-pair tertile edges (ticks) and the bottom-decile "ultra-thin" cut:

| pair | P33.3 | P66.7 | ultra-thin P10 | median vol (low / med / high) |
|---|---:|---:|---:|---|
| EUR_USD | 15,756 | 36,159 | 6,221 | 8,858 / 24,414 / 60,219 |
| GBP_USD | 8,402 | 22,011 | 3,202 | 4,575 / 13,618 / 38,274 |
| USD_JPY | 7,000 | 19,239 | 2,333 | 3,615 / 11,789 / 33,097 |

Volume spans roughly an order of magnitude low→high on every pair, so the tertiles are
well separated — the conditioning variable has real dynamic range.

## 3. The decisive confounds — what a "thin" 30-pip bar actually *is*

Because each range bar travels the same ~30 pips, **low volume does not mean a small,
quiet move — it means the same 30 pips were covered in fewer ticks, i.e. faster and more
violently.** Every confound flagged in the hypothesis (§6) fires, in the same direction,
on all three pairs:

### 3.1 Duration — thin bars complete in *minutes*, thick bars over *hours*

Median M1 minutes to complete (low / medium / high participation):

| pair | low | medium | high |
|---|---:|---:|---:|
| EUR_USD | 49 | 224 | 914 |
| GBP_USD | 22 | 89 | 346 |
| USD_JPY | 15 | 83 | 348 |

A "thin" 30-pip bar is a **fast** 30-pip bar (USD_JPY: 15 min vs 348 min). This is a
jump/impulse, not a low-energy drift.

### 3.2 Overshoot — thin bars overshoot *more* (overlap with the failed H16)

Mean completion overshoot (pips), low / medium / high:

| pair | low | medium | high |
|---|---:|---:|---:|
| EUR_USD | 3.29 | 2.53 | 2.33 |
| GBP_USD | 4.56 | 2.71 | 2.48 |
| USD_JPY | 6.77 | 3.78 | 3.36 |

**This is the critical finding.** Low-participation bars carry the *largest* overshoot
(USD_JPY: 2× the high bucket). So the H03 "thin-move" cell is heavily **collinear with
the large-overshoot cell that H16 already screened to `FAIL_FRONT_GATE`.** Any reversion
seen after thin bars is, to first order, the *same* (absent) overshoot-exhaustion effect
re-measured under a different name — not an independent participation effect.

### 3.3 Spread — thin bars are *more expensive* (liquidity confound)

Mean spread at completion (pips), low / medium / high:

| pair | low | medium | high |
|---|---:|---:|---:|
| EUR_USD | 1.66 | 1.60 | 1.60 |
| GBP_USD | 2.44 | 2.14 | 2.15 |
| USD_JPY | 2.50 | 1.95 | 1.90 |

Thin moves occur in **thinner liquidity → wider spreads** (USD_JPY +0.6 pip vs the high
bucket). They are structurally the *worst* bars to trade, exactly where a small fade
cannot survive cost (Phase 4).

### 3.4 Session — thin bars skew to Tokyo / rollover (esp. USD_JPY)

USD_JPY low-participation bars over-concentrate in **Tokyo (372)** and **rollover_late
(99)** relative to the high bucket — the thin-liquidity, wide-spread, financing-charged
windows the feasibility and C031 work already flagged as cost-toxic. EUR/GBP low buckets
sit mostly in london / london_ny_overlap, but still carry the duration + overshoot +
spread confounds above.

## 4. Implication for the screen

The participation variable is **not clean**: "thin" is entangled with *fast + large
overshoot + wide spread + off-hours*. This means:

- A move-matched read is only approximate even on range bars, because thin bars
  systematically overshoot more (the travel is 30 pip + a *larger* tail for thin bars).
- The honest test is therefore: **does the low-participation bucket beat its
  shuffled-participation null and its own (wider) cost on ≥ 2 pairs**, despite these
  confounds? Phases 3–5 answer this — and the confounds make a clean PASS unlikely a
  priori. Measuring it anyway (not assuming the answer) is the point of the screen.
