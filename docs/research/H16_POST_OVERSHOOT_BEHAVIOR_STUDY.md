# H16 — post-overshoot behaviour study (Phase 3)

**Sprint:** `research-non-time-bar-overshoot-frontgate-001` · Phase 3
**Artifacts:** [`behavior_study.json`](../../research/h16_overshoot_frontgate/behavior_study.json),
[`h16_screen_matrix.csv`](../../research/h16_overshoot_frontgate/h16_screen_matrix.csv).

> Conditional forward-return measurement. **fade = −completion_dir × (mid_close[i+k] −
> mid_close[i])** in pips; **positive ⇒ reversion** (exhaustion), negative ⇒
> continuation. No positions, no PnL, no signals, no optimisation. Pre-cost.

---

## 1. Mean fade return (pips) by overshoot bucket, horizon = 1 bar

| pair | small | medium | large | extreme | top-5% tail | unconditional |
|---|---:|---:|---:|---:|---:|---:|
| EUR_USD | **+2.58** | +0.31 | +1.32 | +0.60 | −2.26 | +1.22 |
| GBP_USD | +0.73 | +1.28 | +0.15 | −0.20 | −0.98 | +0.49 |
| USD_JPY | −0.35 | −0.22 | +0.12 | −0.39 | +0.28 | −0.21 |

## 2. Reversion rate (fraction of fades > 0) — extreme bucket, all horizons

| pair | h1 | h2 | h3 |
|---|---:|---:|---:|
| EUR_USD | 0.507 | 0.492 | 0.524 |
| GBP_USD | 0.502 | 0.510 | 0.526 |
| USD_JPY | 0.490 | 0.524 | 0.492 |

Extreme-bucket mean fade ± SEM (pips), by horizon — all within ~1 SEM of zero:

| pair | h1 | h2 | h3 |
|---|---|---|---|
| EUR_USD | +0.60 ± 1.37 | +0.38 ± 1.86 | +1.09 ± 2.29 |
| GBP_USD | −0.20 ± 1.06 | +2.02 ± 1.51 | +2.34 ± 1.83 |
| USD_JPY | −0.39 ± 1.00 | +1.03 ± 1.38 | −0.66 ± 1.71 |

## 3. Answers to the Phase-3 questions

### Does exhaustion appear more common than continuation? **No.**
- **No bucket gradient.** The thesis predicts reversion *increasing* with overshoot.
  The data show the opposite or nothing: on EUR_USD the **small** bucket fades most
  positively (+2.58) while **extreme** is +0.60; on GBP_USD and USD_JPY the extreme
  bucket is ≈ 0 or slightly **negative**. There is no monotone "bigger overshoot →
  more reversion" relationship on any pair.
- **Reversion rate ≈ 0.50 everywhere** (0.49–0.53). Post-overshoot direction is a
  coin-flip; there is no exhaustion tendency.
- **Magnitudes are within ~1 SEM of zero.** Every extreme-bucket mean fade is small
  relative to its standard error (means ≈ −0.7…+2.3 pips vs SEM ≈ 1.0–2.3). None is
  statistically distinguishable from zero.
- **Signs are inconsistent** across pairs and horizons (e.g. USD_JPY h2 +1.03 but h3
  −0.66; GBP_USD rises with horizon, EUR_USD does not). No coherent effect.
- The **top-5% tail** (the most extreme overshoots — exactly where exhaustion should be
  strongest) is, if anything, *negative* at h1 on EUR_USD (−2.26) and GBP_USD (−0.98),
  i.e. mild **continuation**, the opposite of the thesis.

### Or is the effect nonexistent?
**Effectively nonexistent.** Overshoot magnitude does not carry a usable, consistent,
directional signal about subsequent moves. The hypothesised exhaustion-fade is not
present in the conditional means or reversion rates.

## 4. Falsifier check (from the hypothesis doc)

- ❌ **No gradient** — confirmed (falsifier #1).
- ❌ **Sign not reversion** — the largest-overshoot tail leans to continuation on two
  pairs (falsifier #2 region).
- The effect is also within ~1 SEM of zero throughout.

This already meets the FAIL falsifiers before cost (Phase 4) and null (Phase 5) are
even applied — those phases confirm and harden the conclusion.
