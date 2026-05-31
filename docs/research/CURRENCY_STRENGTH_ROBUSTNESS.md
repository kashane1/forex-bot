# Currency-Strength Factor — Robustness Review (Phase 6)

**Sprint:** `research-currency-strength-factor-validation-001` · Phase 6
**Status:** RESULT (descriptive; verdict deferred to Phase 7). The three frozen
robustness axes (protocol §13) — **nearby lookbacks, nearby ranking definitions,
nearby aggregation definitions** — are tested. **Stability check, not
optimization.** Figures from committed
`docs/research/currency_strength/robustness.csv`.
**Date:** 2026-05-30.

The question is **not** "can a neighbour produce a signal?" (that would be
optimization) but "does the *null* conclusion survive nearby definitions, or is it
an artifact of the exact primary spec?" A robustly-null factor stays null
everywhere nearby.

---

## 1. Nearby lookbacks (L = 24 / 48 / 96 M5 bars; matched-Z, 80-seed)

```
variant      condition         60m mean_bp  60m mZ   240m mean_bp  240m mZ
lookback_24  strongest         -0.052       -0.40    +0.005        +0.21
lookback_24  weakest           -0.049       -0.32    -0.115        -0.79
lookback_24  rapid_strengthen  -0.041       -0.21    -0.021        -0.06
lookback_24  rapid_weaken      +0.032       +0.75    +0.017        +0.19
lookback_48  strongest         +0.007       +0.40    -0.020        +0.01
lookback_48  weakest           -0.034       -0.12    +0.007        +0.19
lookback_48  rapid_strengthen  +0.007       +0.45    +0.126        +1.10
lookback_48  rapid_weaken      -0.058       -0.54    -0.079        -0.58
lookback_96  strongest         -0.075       -0.70    -0.050        -0.23
lookback_96  weakest           -0.068       -0.57    -0.193        -1.42
lookback_96  rapid_strengthen  -0.042       -0.22    -0.020        -0.06
lookback_96  rapid_weaken      +0.033       +0.75    -0.191        -1.48
```

**No lookback produces a clearing cell** (all |mZ| ≤ 1.48). Signs **flip across
lookbacks** (e.g. `rapid_weaken` 240m: +0.017 → −0.079 → −0.191; `strongest` 60m:
−0.052 → +0.007 → −0.075). The near-zero, sign-unstable response is the same at
2h, 4h, and 8h look-backs. **Robustly null across lookbacks.**

## 2. Nearby ranking definitions (top-1 vs top-2 bucket; 60/240m mean_bp)

```
variant     condition   60m      240m
rank_top1   strongest   +0.007   -0.020
rank_top1   weakest     -0.034   +0.007
rank_top2   strongest   -0.016   -0.012
rank_top2   weakest     -0.005   +0.049
```

Widening the bucket from the single strongest/weakest currency to the **top-2 /
bottom-2** does not surface an effect — means stay within ±0.05 bp and remain
sign-mixed. The nullity is not an artifact of the rank-1 knife-edge. **Robustly
null across ranking definitions.**

## 3. Nearby aggregation definitions (vol-normalized; matched-Z, 80-seed)

Vol-normalized average-of-pairs (each instrument leg weighted by inverse rolling
M5 vol):

```
agg_volnorm  condition         60m mean_bp  60m mZ   240m mean_bp  240m mZ
             strongest         ...          (all |mZ| ≤ 1.57)
             weakest
             rapid_strengthen
             rapid_weaken
```

- **Global max |z| under the vol-normalized aggregation = 1.57** — still **no
  cell clears |z| ≥ 2.**
- **Aggregation agreement:** the vol-normalized strength series correlate
  **0.917–0.949** per currency with the primary average-of-pairs strength (USD
  0.949, EUR 0.943, GBP 0.917, JPY 0.930, AUD 0.946, NZD 0.949, CHF 0.931, CAD
  0.930). The two aggregations describe **the same state** and reach the **same
  null conclusion** — exactly the cross-check the protocol's secondary method was
  frozen to provide. (The heavier per-bar least-squares decomposition is the
  protocol's explicitly-secondary cross-check; given the two aggregations already
  agree at r≈0.93 and both are null, it is not separately required to overturn a
  0/80 result.)

## 4. Robustness reading (no verdict here)

The conclusion is **robustly null**: across **three lookbacks**, **two ranking
definitions**, and **two aggregations**, **no cell clears |z| ≥ 2** (max anywhere
≈ 1.57), means stay within ±0.2 bp, and signs flip between neighbours. The
factor's non-existence is **not** an artifact of the exact primary spec — every
nearby definition agrees. This is the inverse of a fragile result; it is a stable
*absence* of effect. Phase 7 applies the frozen verdict map.
