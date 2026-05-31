# Currency-Strength Factor — Response Study (Phase 3)

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 3
**Status:** RESULT (descriptive; verdict deferred to Phase 7). Frozen factor
applied unchanged. All figures read directly from committed
`docs/research/currency_strength/response_by_condition.csv` (artifact-first).
**Date:** 2026-05-30.

**Question:** when a currency becomes **strongest / weakest / rapidly strengthening
/ rapidly weakening** (by the frozen 4h strength / 1h Δstrength), what is the
**forward currency return** at 5/15/30/60/240 min? Returns are in **basis points**
of cumulative log return (1 bp = 1e-4). 25,330 events.

---

## 1. Forward response by condition × horizon

```
condition         horizon  n      mean_bp   p_pos  p_neg   mfe_bp   mae_bp  rank_persist
strongest           5    25330   -0.007    0.493  0.506   -0.007   -0.007    0.840
weakest             5    25330   -0.015    0.501  0.498   -0.015   -0.015    0.843
rapid_strengthen    5    25330   -0.009    0.496  0.503   -0.009   -0.009      —
rapid_weaken        5    25330   -0.006    0.503  0.495   -0.006   -0.006      —
strongest          15    25330   +0.007    0.490  0.509   +1.99    -1.98     0.737
weakest            15    25330   +0.008    0.510  0.489   +1.94    -1.95     0.738
rapid_strengthen   15    25330   -0.005    0.494  0.505   +1.93    -1.96       —
rapid_weaken       15    25330   -0.063    0.500  0.499   +1.89    -1.96       —
strongest          30    25329   -0.037    0.489  0.511   +3.74    -3.74     0.643
weakest            30    25329   +0.023    0.506  0.493   +3.70    -3.69     0.638
rapid_strengthen   30    25329   -0.017    0.489  0.510   +3.67    -3.68       —
rapid_weaken       30    25329   -0.054    0.506  0.493   +3.62    -3.70       —
strongest          60    25329   +0.007    0.493  0.507   +6.17    -6.14     0.525
weakest            60    25329   -0.034    0.503  0.496   +6.10    -6.13     0.520
rapid_strengthen   60    25329   +0.007    0.493  0.507   +6.08    -6.06       —
rapid_weaken       60    25329   -0.058    0.506  0.493   +5.98    -6.10       —
strongest         240    25326   -0.020    0.499  0.501   +14.37   -14.16    0.161
weakest           240    25326   +0.007    0.499  0.501   +14.28   -14.43    0.166
rapid_strengthen  240    25326   +0.126    0.501  0.499   +14.15   -14.05      —
rapid_weaken      240    25326   -0.079    0.497  0.502   +14.11   -14.15      —
```

---

## 2. What happens next? (answers)

### Mean forward return — effectively zero at every horizon
Across **all 4 conditions × 5 horizons**, the mean forward currency return is
**between −0.13 and +0.13 bp**. For scale, the path's own MFE/MAE are **±2 bp
(15m), ±6 bp (60m), ±14 bp (240m)** — so the conditional mean is **~1–2% of the
typical path excursion**. The signal-to-noise is negligible: conditioning on
strength tells you essentially nothing about the next move's direction or size.

### Probability positive/negative — coin flips
`p_pos` and `p_neg` sit in **0.489–0.510** for every condition and horizon — i.e.
~0.50 ± 0.01. A strong (or weak, or rapidly-moving) currency is **as likely to
rise as fall** next.

### MFE/MAE — symmetric
MFE ≈ −MAE at every horizon for every condition (e.g. strongest-60m: +6.17 /
−6.14). The forward path is **symmetric** around zero — no favourable skew for
"buy the strong" nor "fade the strong."

### Rank persistence — strength persists, returns do not
`rank_persist` is **high at short horizons** (strongest stays strongest 84% at
5m, 74% at 15m) and decays with horizon (53% at 60m, 16% at 240m). This is the
**only** non-trivial number — but it is mechanical: a 4h look-back strength
changes slowly, so a currency ranked #1 now is likely still #1 in 5–15 min. **Yet
its forward *return* is ~0.** The factor is **autocorrelated as a state but
carries no forward return information** — strength persists, price does not follow.

### Direction (the empirical output)
No coherent continuation or reversion emerges. The largest, most consistent tilt
is a **weak negative** on `rapid_weaken` (−0.06 bp at 15m, −0.05 at 30m, −0.06 at
60m) — i.e. a currency that just fell fast continues fractionally down — but it is
**~0.06 bp against ~6 bp of path noise** and (Phase 5) does not clear any null.

---

## 3. Phase-3 reading (no verdict here)

Conditioning on cross-implied currency strength produces **forward currency
returns indistinguishable from zero** — negligible means (~1–2% of path noise),
coin-flip hit rates, symmetric MFE/MAE — at every horizon and for every condition.
The strength state is **persistent** (mechanically) but **non-predictive**. This
already points away from a tradable-or-even-existing directional factor; Phases 4
(cross-sectional stability) and 5 (formal nulls) test whether even this near-zero
tilt is anything but noise, and Phase 6 checks robustness. **No tradability is
evaluated (out of scope).**
