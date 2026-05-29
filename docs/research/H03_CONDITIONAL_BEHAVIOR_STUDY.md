# H03 thin-move fade — conditional behaviour study (Phase 3)

**Sprint:** `research-non-time-bar-thin-move-frontgate-001` · Phase 3
**Type:** conditional forward-return measurement. No PnL, no positions, no approval.
**Artifacts:** `research/h03_thin_move_frontgate/behavior_study.json`,
`research/h03_thin_move_frontgate/h03_screen_matrix.csv`.

> Fade return (pips): `fade_k(i) = −dir[i] × (mid_close[i+k] − mid_close[i]) / pip`.
> **Positive ⇒ reversion** (H03's claim for thin moves); negative ⇒ continuation.
> Buckets are per-pair volume tertiles (low/med/high) + a bottom-decile ultra-thin tail.

---

## 1. Fade by participation bucket × horizon (mean pips, reversion rate)

| pair | h | low | medium | high | ultra-thin | uncond | low−high |
|---|--:|---|---|---|---|---|--:|
| EUR_USD | 1 | +1.75 (.526) | +2.11 (.536) | −0.19 (.498) | −1.48 (.467) | +1.22 (.520) | +1.94 |
| EUR_USD | 2 | +2.33 (.502) | +2.10 (.513) | −1.17 (.482) | +0.93 (.481) | +1.09 (.499) | +3.50 |
| EUR_USD | 3 | +3.97 (.547) | +1.06 (.509) | −1.09 (.479) | +5.34 (.537) | +1.32 (.512) | +5.06 |
| GBP_USD | 1 | +0.46 (.507) | +0.69 (.512) | +0.33 (.511) | +0.04 (.508) | +0.49 (.510) | +0.13 |
| GBP_USD | 2 | +1.26 (.508) | +0.55 (.493) | +0.70 (.481) | +0.54 (.525) | +0.84 (.494) | +0.56 |
| GBP_USD | 3 | +0.51 (.507) | −0.88 (.500) | +1.02 (.516) | −0.72 (.514) | +0.22 (.507) | −0.51 |
| USD_JPY | 1 | +0.21 (.502) | −0.04 (.502) | −0.80 (.482) | +1.11 (.510) | −0.21 (.495) | +1.01 |
| USD_JPY | 2 | +0.57 (.501) | +2.11 (.523) | −1.45 (.481) | +2.37 (.521) | +0.41 (.502) | +2.02 |
| USD_JPY | 3 | −0.68 (.489) | +2.76 (.521) | −1.56 (.476) | +0.70 (.503) | +0.17 (.496) | +0.88 |

## 2. Reversion tendency

**Reversion rate ≈ 0.50 on every pair / bucket / horizon** (range 0.467–0.547). The
low-participation buckets are coin-flips at the directional level: there is no
participation cell where the probability of reverting meaningfully departs from 50/50.
This mirrors the H16 result and the repo's repeated finding that FX direction on this
corpus is ~null.

## 3. Continuation tendency

The **high**-participation bucket is mildly **continuation**-leaning (negative fade) on
EUR_USD (−0.19/−1.17/−1.09) and USD_JPY (−0.80/−1.45/−1.56) — slow, high-volume,
long-duration bars drift a little further. This is the *mirror* of the thin-move story,
not confirmation of it.

## 4. Effect consistency — there is no clean gradient

H03 requires reversion to **strengthen monotonically as participation falls**. It does
not:

- **Non-monotone.** The **medium** bucket frequently exceeds **low**: EUR_USD h1
  (med +2.11 > low +1.75), USD_JPY h2 (med +2.11 > low +0.57) and h3 (med +2.76 vs low
  −0.68, which is *negative*). The peak reversion is often the *middle* of the
  distribution, not the thin end.
- **Inconsistent across pairs.** GBP_USD shows essentially nothing (low−high = +0.13 at
  h1, **−0.51** at h3). The low−high sign is positive on EUR/USD_JPY but near-zero or
  negative on GBP.
- **The "gradient" is the high bucket, not the low bucket.** Where low−high is positive,
  it is driven mostly by the *high* bucket sitting **below** the unconditional baseline
  (continuation), not by the *low* bucket sitting above it. On EUR_USD h1 the low bucket
  (+1.75) is barely above unconditional (+1.22); on USD_JPY h1 low (+0.21) ≈ unconditional
  shifted. Phase 5 confirms the low bucket is **inside its shuffled null** everywhere.
- **The ultra-thin tail is erratic, not sharper.** It should be the *strongest* reversion
  if H03 were real. Instead it is **continuation** on EUR_USD h1 (−1.48) and GBP_USD h3
  (−0.72), and only sporadically positive elsewhere — the signature of small-sample noise
  (n≈214–441), not a sharpening effect.

## 5. Read

There is a **weak, correctly-signed average tilt** (low−high > 0 on 7 of 9 pair×horizon
cells) — more than H16 showed — but it is **non-monotone, coin-flip at the reversion-rate
level, GBP-absent, and concentrated in the high bucket's drift rather than the thin
bucket's reversion.** Whether even this survives cost and a matched null is settled in
Phases 4–5 (it does not). The Phase-2 confounds (thin = large-overshoot + fast + wide
spread) mean the small tilt is most parsimoniously the **already-failed H16 overshoot
effect plus bid-ask bounce**, not an independent participation edge.
