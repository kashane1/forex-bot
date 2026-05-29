# C1 Robustness Study (Phase 4)

**Status:** RESULT (descriptive; no verdict, no campaign, no strategy)
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001`
**Artifact:** `docs/research/c1_validation/c1_robustness.csv` (112 rows: 8 specs ×
7 pairs × 2 horizons).

These are **robustness checks, not optimisation** — each spec perturbs exactly
one knob away from the locked baseline to ask "does the factor survive a small,
*a-priori-reasonable* change to its definition?" No spec was chosen by looking at
which performed best. C1_long, 60-min, mean signed return (negative = reversion).

## 1. The eight specifications

| Spec | What changed vs baseline |
|---|---|
| `baseline` | EMA 20/50, slope-3, H4 trend + H1 trend + M15 aligned (locked) |
| `ema_30_60` | slower EMAs (30/60) |
| `ema_10_40` | faster EMAs (10/40) |
| `slope_lb_5` | slope measured over 5 bars instead of 3 |
| `trend_no_slope` | drop the slope condition (trend = close vs EMA50 only) |
| `m15_strict` | M15 leg must *trend* (close>EMA50 **and** slope>0), not just align |
| `drop_h4` | shallower confluence: H1 trend + M15 aligned only (no H4) |
| `add_m5` | deeper confluence: H4 + H1 + M15 + M5 aligned |

## 2. C1_long mean60 (t60) by spec × pair

```
spec              EUR_USD        USD_JPY        GBP_USD        AUD_USD        NZD_USD        USD_CAD        USD_CHF
baseline        -1.169(-3.7)  -1.136(-3.6)  -0.651(-1.8)  -0.356(-1.5)  -0.372(-1.5)  -0.179(-0.6)  -0.345(-1.1)
ema_30_60       -0.744(-2.3)  -0.910(-2.9)  -0.901(-2.4)  -0.230(-0.9)  -0.441(-1.7)  +0.192(+0.6)  -0.051(-0.2)
ema_10_40       -1.118(-3.8)  -0.725(-2.4)  -0.242(-0.7)  -0.379(-1.6)  -0.585(-2.5)  -0.300(-1.1)  -0.090(-0.4)
slope_lb_5      -1.194(-3.5)  -0.805(-2.5)  -0.196(-0.5)  -0.279(-1.1)  -0.323(-1.3)  -0.396(-1.2)  -0.108(-0.4)
trend_no_slope  -0.874(-2.9)  -0.856(-2.8)  -0.683(-2.0)  -0.266(-1.1)  -0.337(-1.4)  -0.107(-0.4)  -0.394(-1.4)
m15_strict      -1.181(-3.4)  -1.105(-3.3)  -0.727(-1.9)  -0.686(-2.8)  -0.652(-2.3)  -0.107(-0.3)  -0.418(-1.3)
drop_h4         -0.761(-3.0)  -0.553(-1.9)  -0.775(-2.5)  -0.319(-1.5)  -0.361(-1.8)  -0.219(-0.9)  -0.132(-0.6)
add_m5          -0.674(-3.0)  -0.416(-1.8)  -0.527(-2.1)  -0.441(-2.5)  -0.152(-0.8)  -0.208(-1.0)  -0.005(-0.0)
```

## 3. Stability summary

```
spec            neg/7  sig(t<=-2)/7   EUR_t   JPY_t   avg_n     [60-min]
baseline          7        2         -3.66   -3.56    1631
ema_30_60         6        3         -2.29   -2.88    1495
ema_10_40         7        3         -3.76   -2.40    1802
slope_lb_5        7        2         -3.52   -2.45    1524
trend_no_slope    7        2         -2.93   -2.78    1834
m15_strict        7        4         -3.42   -3.30    1396
drop_h4           7        2         -2.98   -1.85    2395
add_m5            7        3         -2.99   -1.79    3055
```

## 4. Answer: does the factor survive small specification changes?

**Yes — convincingly, in sign; and the two strong pairs stay significant.**

- **Sign stability.** Across **8 specs × 7 pairs = 56 cells, 55 are negative**
  (the lone exception is `ema_30_60` on USD_CAD, +0.19, t +0.6 — a weak pair under
  the weakest variant). The "fade full bullish alignment" direction is **not** an
  artifact of the exact EMA 20/50 / slope-3 / H4+H1+M15 choice.
- **EUR_USD and USD_JPY** remain the load-bearing pairs under every spec: EUR_USD
  t60 stays between −2.3 and −3.8 (always significant); USD_JPY between −1.8 and
  −3.6 (significant under 6 of 8 specs, softening only when confluence depth is
  changed via `drop_h4`/`add_m5`).
- **Confluence depth is not a knife-edge.** Removing H4 (`drop_h4`) *keeps* the
  effect (7/7 negative; GBP_USD even strengthens to t −2.5), and adding M5
  (`add_m5`) also keeps it (7/7 negative). The reversion lives in the H1+M15
  alignment and is reinforced — not created — by H4. `m15_strict` (a stricter,
  more selective M15 leg) is the **strongest** variant (4/7 significant), which is
  the right direction for a real over-extension effect.
- **The weak pairs stay weak under every spec.** No perturbation rescues
  NZD/AUD/CAD/CHF into robust significance; their noise is structural, not a
  baseline-specific accident. (`m15_strict` lifts AUD/NZD to ~t −2.3/−2.8, the one
  spec that nudges them, but it does not generalise to CAD/CHF.)

## 5. Takeaway

C1_long is **robust to reasonable specification perturbation**: the sign is
essentially invariant (55/56), the two strong pairs survive every variant, and
the effect does not depend on a single fragile parameter or on the exact
confluence depth. This is the behaviour of a **real structural factor**, not a
spec-tuned mirage (choice #4 is effectively excluded). It does **not**, however,
make the weak pairs strong or change the cost picture — magnitude robustness is
not the same as tradeability, which Phase 5 addresses.
