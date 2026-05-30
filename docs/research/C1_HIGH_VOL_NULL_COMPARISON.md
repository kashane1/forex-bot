# C1 High-Volatility Null Comparison (Phase 4)

**Status:** RESULT (descriptive; no verdict here)
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001`
**Runner:** `scripts/run_c1_highvol_frontgate.py` (200 seeds).
**Artifacts:** `docs/research/c1_highvol_frontgate/c1_hivol_nulls.csv`,
`{pair}_c1_hivol_events.csv`, `c1_hivol_meta.json`.

For the **high-vol** C1_long subset we compare the observed mean signed return to
four references (frozen Phase-1 list): a **matched** null (random bars, same
session+direction), a **randomised-timestamp** null (`rand_z`), the
**unconditional** all-events C1_long mean (`uncond_mean_ret` — does conditioning
add value?), and the strict **volatility-matched** null (random bars drawn only
from high-vol M1 bars, same session+direction — is the effect C1-specific or just
"high-vol bars revert?"). All Z are `(obs − null_mean)/null_std`; negative =
observed reverts more than the null.

## 1. Z by horizon

**EUR_USD (hi-vol n=532)**
```
h    obs      uncond    rand_z  matched_z  volmatched_z
5   -0.640   -0.280    -4.65    -4.78      -3.50
10  -0.885   -0.397    -4.27    -5.23      -3.29
15  -1.095   -0.576    -4.38    -4.91      -3.45
30  -1.496   -0.747    -4.35    -4.66      -3.10
60  -1.777   -1.169    -4.07    -3.71      -2.76
```

**USD_JPY (hi-vol n=715)**
```
h    obs      uncond    rand_z  matched_z  volmatched_z
5   -0.288   -0.155    -1.65    -1.73      -1.15
10  -0.262   -0.090    -1.18    -1.21      -0.73
15  -0.559   -0.200    -1.83    -1.93      -1.37
30  -1.223   -0.681    -2.86    -2.70      -2.32
60  -2.094   -1.136    -3.79    -3.48      -2.58
```

**GBP_USD (hi-vol n=528)**
```
h    obs      uncond    rand_z  matched_z  volmatched_z
5   -0.546   -0.334    -2.85    -2.83      -2.31
10  -0.936   -0.478    -3.56    -3.66      -2.76
15  -1.212   -0.555    -3.92    -4.01      -3.10
30  -1.445   -0.686    -3.13    -3.02      -2.57
60  -1.258   -0.651    -2.09    -1.87      -1.56
```

## 2. Findings

1. **Conditioning adds value.** On every pair and horizon the high-vol `obs` mean
   is more negative than the `uncond` all-events mean — the volatility filter
   genuinely concentrates the reversion (the Phase-1 "adds value" sub-condition is
   met on the primaries).
2. **The two primaries beat the matched null — and the strict vol-matched null —
   at 60 min.** EUR_USD: matched-Z −3.71, **vol-matched-Z −2.76**; USD_JPY:
   matched-Z −3.48, **vol-matched-Z −2.58**. Surviving the *vol-matched* null is
   the important result: the high-vol C1 reversion is **C1-specific**, not merely a
   restatement of "high-volatility bars mean-revert." (USD_JPY is within-null at
   5–15 min and clears only at 30/60 min — horizon-limited, as in validation.)
3. **GBP_USD (quasi-OOS) does not clear at 60 min** (matched-Z −1.87, vol-matched
   −1.56). It is strong at 10–30 min (vol-matched-Z to −3.1) but fades by 60 min —
   the generalisation pair does not replicate the primaries' 60-min null survival.

## 3. Answer to the Phase-4 question

**Does the high-volatility subset remain statistically distinct? Yes, on the two
primaries — robustly, including against a volatility-matched null.** The effect is
statistically real and demonstrably C1-specific, not a generic volatility
artifact. This is the **strongest** evidence in the screen *for* the factor — and
it is precisely why the Phase-6 verdict turns entirely on **cost** (Phase 3) and
**stability/generalisation** (Phase 5), not on statistical reality: a real,
null-surviving effect that still cannot pay its spread is not a tradeable edge.

**Phase-1 null gate status:** PASS on both primaries (matched-Z ≤ −2 and
vol-matched-Z ≤ −2 at 60 min). It does **not** rescue the verdict, because the
frozen rule fails the gate on cost regardless.
