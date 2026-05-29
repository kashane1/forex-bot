# CAMPAIGN_025 — train-matrix result

**Classification:** **`REJECT_MATRIX_NO_TRAIN_CANDIDATE`** — no candidate passed the
train-only selection filters. **No champion selected. Validation NOT run** (per
protocol: no champion → no promotion-style validation). No tuning. Test lockbox
closed. No approval.

Artifacts: `research/campaign_025/train_matrix/` (metrics/gate/pair/side/exit/
cost-stress/holding/spread-atr/funnel/C011/selection JSON+CSV).

---

## Command & windows

```
python scripts/run_campaign_025_m5_donchian_htf_confluence.py --train-matrix \
  --train-start 2021-07-01 --train-end 2023-06-30
```

- **Train window:** 2021-07-01 → 2023-06-30 (24 months), 7 majors, M5 execution.
- **Candidates:** 16 (`C025_MTX_001`…`016`), the full frozen matrix.
- Validation window (2023-07-01→2024-12-31) and test window (LOCKED) **not run**.

## Aggregate matrix results (TRAIN, net of base costs)

Every candidate is **negative**. Expectancy_R range **−0.077 to −0.178**; profit
factor **0.70–0.85**; **≤ 1/7 pairs non-negative** for all; 2× cost-stress
expectancy **−0.40 to −0.75 R**; **no candidate beats the C011 null** (all
beat-by margins negative). Mean spread/ATR ≈ **0.44–0.50** (entry spread is roughly
half the M5 ATR — a structurally hostile cost ratio).

| ID | archetype | trades | exp_R | PF | pairs≥0 | 2×stress exp_R | avg hold (bars) | spread/ATR |
|---|---|---|---|---|---|---|---|---|
| 009 | strict_trend_runner | 3970 | −0.0767 | 0.835 | 1 | −0.403 | 46.2 | 0.44 |
| 008 | wider_trend_runner | 4412 | −0.0801 | 0.829 | 1 | −0.422 | 46.1 | 0.45 |
| 016 | wider_base_no_target | 4174 | −0.0829 | 0.850 | 1 | −0.428 | 54.8 | 0.46 |
| 011 | wide_donchian_channel_follower | 3500 | −0.1098 | 0.800 | 1 | −0.498 | 43.6 | 0.49 |
| 014 | conservative_strict_no_target | 4380 | −0.1166 | 0.812 | 1 | −0.515 | 51.3 | 0.45 |
| 001 | baseline_continuation | 5657 | −0.1254 | 0.775 | 1 | −0.541 | 37.5 | 0.46 |
| 005 | balanced_strict_2r | 5246 | −0.1318 | 0.750 | 0 | −0.527 | 34.9 | 0.45 |
| 004 | balanced_2r_breakout | 5902 | −0.1326 | 0.749 | 0 | −0.541 | 34.8 | 0.46 |
| 006 | balanced_3r_continuation | 4900 | −0.1334 | 0.782 | 1 | −0.538 | 48.9 | 0.46 |
| 010 | donchian_channel_follower | 5622 | −0.1389 | 0.739 | 1 | −0.561 | 36.0 | 0.47 |
| 007 | compression_3r_continuation | 3739 | −0.1497 | 0.773 | 1 | −0.603 | 45.4 | 0.49 |
| 015 | shorter_base_no_target | 6781 | −0.1491 | 0.770 | 1 | −0.671 | 34.5 | 0.47 |
| 003 | tight_strict_scalp | 6998 | −0.1617 | 0.714 | 0 | −0.662 | 25.6 | 0.46 |
| 013 | fast_compression_runner | 5129 | −0.1692 | 0.707 | 0 | −0.737 | 25.7 | 0.50 |
| 002 | tight_breakout_scalp | 7970 | −0.1704 | 0.703 | 0 | −0.686 | 25.3 | 0.46 |
| 012 | fast_compression_breakout | 5414 | −0.1780 | 0.707 | 0 | −0.749 | 23.9 | 0.50 |

## Train filter table

**0/16 candidates eligible.** Every candidate fails on `expectancy_gte_0`,
`pf_gte_1_03`, `pairs_nonneg_gte_3`, and `stress_2x_exp_gte_neg_0_005`. Trade-count
≥100 is satisfied by all (so **not** `BLOCKED_MATRIX_TOO_SPARSE`). Single-pair
concentration is ≤ 0.24 for all (no concentration breach). **No champion.**

## Candidate ranking

Not produced — ranking only applies to eligible candidates, of which there are
none. (The least-negative candidates are the slow trend-runners 009/008/016; the
most-negative are the fast scalps 002/012/013.)

## Pair-level results

USD_JPY is the **only** pair that is non-negative on some candidates (e.g. baseline
+0.039R, compression-3R +0.031R, wider-runner +0.019R). All other six majors are
negative on **every** candidate. USD_JPY's edge is small and **does not survive 2×
cost stress** (turns negative), so it is **not "materially strong"**.

## Side-level results

Longs and shorts are **both negative** and similar in magnitude (baseline long
−0.124R / short −0.126R). No directional asymmetry rescues the family.

## Exit-reason diagnostics

- time-only (001): hard_stop 2269 / time_stop 3388.
- +2R target (004): converts 773 exits to `fixed_target_2r` but expectancy is no
  better (targets cap winners while stops/costs persist).
- channel follower (010): 3602 `donchian_channel_exit` / 1243 stop / 777 time —
  exits late, still negative.
- trend runner (008): breakeven 413 + trailing 886 + stop 1542 + time 1571.

No exit model converts the family to positive; the cost drag dominates regardless
of harvest scheme.

## Signal-funnel diagnostics (baseline)

964,176 M5 bars examined → H4 context pass 768,425 (80%) → H1 context pass 690,669
(72%) → M5 breakout pass 117,353 (12%) → **21,625 gated signals** → **5,657 entries**
(one-position throttle). The funnel is healthy and produces ample trades; the
problem is **trade quality net of cost**, not signal scarcity.

## Holding & spread/ATR

Avg hold 24–55 M5 bars (2–4.6 hours). Spread/ATR ≈ 0.44–0.50 across all candidates
— the decisive structural fact: on M5 the bid/ask spread (~1.3–1.5 pips majors,
~1.3 pips JPY) is roughly **half the per-bar ATR**, so round-trip cost consumes a
large fraction of any breakout edge. Faster candidates (more turnover) lose more.

## C011 null comparison

No candidate beats the C011 deduped null (−0.0029R); the best (009) sits ~0.074R
**below** it. The +0.010R beat-margin gate is failed by every candidate.

## Decision

- **`REJECT_MATRIX_NO_TRAIN_CANDIDATE`.** No champion. **Validation is NOT allowed
  to run.** No `SINGLE_PAIR_REVIEW_ONLY` (USD_JPY is not materially strong and is
  cost-fragile). No tuning, no rescue, no invented champion.
- Validation **was not used** for selection (there was no selection to make).
- **No approval. Test lockbox closed. Paper/demo/live blocked.**
