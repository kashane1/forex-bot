# CAMPAIGN_026 — train timeframe-ladder result

**Classification: `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED /
NOT_APPROVED`.** 0/11 candidates eligible on train; no champion; no single-pair review;
validation not run; lockbox closed; `approved_strategies.yaml` stays `approved: []`.

Command:
```
PYTHONPATH=$PWD/src python scripts/run_campaign_026_donchian_htf_timeframe_ladder.py \
  --train-matrix --train-start 2021-07-01 --train-end 2023-06-30
```
Train window 2021-07-01 → 2023-06-30, 7 majors, net of `COST_BASE`.

## Candidate matrix (11) — train results

| ID | TF | trades | expectancy_R | PF | pairs≥0 | 2× stress R | spread/ATR | avg hold |
|---|---|---|---|---|---|---|---|---|
| C026_TF_001 | M3 | 8,544 | −0.1822 | 0.69 | 0/7 | −0.732 | 0.637 | 41.5 |
| C026_TF_002 | M3 | 6,366 | −0.1406 | 0.73 | 0/7 | −0.600 | 0.628 | 54.4 |
| C026_TF_003 | M3 | 7,209 | −0.1664 | 0.66 | 0/7 | −0.646 | 0.645 | 39.3 |
| C026_TF_004 | M15 | 2,659 | −0.0671 | 0.85 | 1/7 | −0.264 | 0.220 | 25.6 |
| C026_TF_005 | M15 | 2,270 | −0.0394 | 0.92 | 1/7 | −0.233 | 0.218 | 36.3 |
| C026_TF_006 | M15 | 2,032 | −0.0604 | 0.85 | 1/7 | −0.214 | 0.215 | 36.7 |
| C026_TF_007 | M15 | 2,414 | −0.0796 | 0.83 | 1/7 | −0.282 | 0.218 | 25.1 |
| C026_TF_008 | M30 | 2,197 | −0.0315 | 0.92 | 1/7 | −0.163 | 0.145 | 20.2 |
| C026_TF_009 | M30 | 1,899 | −0.0095 | 0.98 | 1/7 | −0.141 | 0.146 | 28.9 |
| **C026_TF_010** | **M30** | **1,592** | **−0.0083** | **0.976** | **2/7** | **−0.112** | **0.142** | 30.1 |
| C026_TF_011 | M30 | 1,635 | −0.0312 | 0.91 | 1/7 | −0.136 | 0.141 | 27.3 |

Every candidate is **net-negative**; none beats the C011 null (−0.0029R) — best is
C026_TF_010 at −0.0083R (0.0054R *below* the null). The least-bad candidate is the M30
trend-runner (TF_010).

## Result by timeframe — M3 vs M15 vs M30 vs M5 (reference)

| TF | expectancy_R range | PF range | 2× stress | spread/ATR (median) |
|---|---|---|---|---|
| **M3** | −0.140 … −0.182 | 0.66–0.73 | −0.60 … −0.73 | 0.59 |
| **M5** (C025) | −0.077 … −0.178 | 0.70–0.85 | −0.40 … −0.75 | 0.44 |
| **M15** | −0.039 … −0.080 | 0.83–0.92 | −0.21 … −0.28 | 0.23 |
| **M30** | −0.008 … −0.031 | 0.91–0.98 | −0.11 … −0.16 | 0.15 |

**Expectancy improves monotonically as the timeframe slows**, tracking the spread/ATR
drop almost exactly: M3 (−0.16, 0.59) → M5 (−0.12, 0.44) → M15 (−0.06, 0.23) → M30
(−0.02, 0.15). The cost-ladder hypothesis is *confirmed* — slower bars carry far less
cost drag. **But even M30, at one-third of M5's spread/ATR, is still net-negative**:
the cost improvement is real and large, yet insufficient to make the signal profitable.

## Selected champion

**None.** 0/11 eligible.

## Why each failed

Identical failure pattern across all 11: `expectancy_gte_0` ✗, `pf_gte_1_03` ✗,
`pairs_nonneg_gte_3` ✗, `stress_2x_exp_gte_neg_0_005` ✗. The trade-count floor
(M3 ≥150, M15/M30 ≥80) **passed** for every candidate (1,592–8,544 trades) — this is
not a scarcity failure. No candidate had positive expectancy, so the
single-pair-review flag (which requires aggregate expectancy > 0) was never set.

## Pair-level diagnostics

Best candidate **C026_TF_010 (M30)** per-pair expectancy_R:
USD_JPY **+0.190** ·  NZD_USD **+0.039** ·  AUD_USD −0.014 ·  USD_CHF −0.031 ·
EUR_USD −0.038 ·  GBP_USD −0.084 ·  USD_CAD −0.109. Only **2/7** positive; the
positives are the two cheapest-spread legs. USD_JPY is the lone consistently-positive
pair across timeframes (M15 TF_005 USD_JPY +0.124; M3 TF_001 USD_JPY −0.055, still the
least-bad) — **the same lone-USD_JPY signal seen in C025**, and again **not** strong
enough (fails 2× stress; aggregate negative) to trigger SINGLE_PAIR_REVIEW_ONLY.

## Side-level diagnostics

Longs and shorts both negative on the M3/M15 candidates. On M30 TF_010, longs are
marginally positive (+0.035R) but shorts negative (−0.050R) → net negative. No
systematic directional edge.

## Exit-reason diagnostics

Time stops + hard stops dominate every candidate. M3 TF_001: 3,800 time / 3,474 stop /
1,268 fixed-target. M15 TF_005: 1,254 time / 879 stop / 137 fixed-3R. M30 TF_010:
1,015 time / 393 stop / 126 ATR-trail / 54 breakeven. Trailing/breakeven on M30
amortise cost over longer holds (the least-bad exit) but cannot manufacture edge.

## Spread/ATR diagnostics

Per-candidate average spread/ATR matches the Phase 3 diagnostic: M3 ≈ 0.63–0.64,
M15 ≈ 0.22, M30 ≈ 0.14. The simulator's realised cost profile is consistent with the
pre-evidence cost diagnostic.

## Signal-funnel diagnostics

Funnels are **healthy** — scarcity is not the problem. M30 TF_010: 144,731 exec bars →
H4 context 117,309 → breakout 14,218 → 4,912 gated signals → 1,592 entries. M3 TF_001:
1,639,675 bars → 35,710 signals → 8,544 entries. Ample signal supply at every
timeframe; the failure is cost-adjusted **quality**, not quantity.

## Holding diagnostics

Avg hold: M3 ≈ 39–54 bars (~2–2.7h), M15 ≈ 25–37 bars (~6–9h), M30 ≈ 20–30 bars
(~10–15h). Slower timeframes hold longer in clock time, amortising fixed cost — part of
why M30 is least-bad — but not enough to clear breakeven.

## Is validation allowed?

**No.** No champion was selected on train, so promotion-style validation is **not
run** (Phase 8). Per protocol, no rescue, no invented champion.

## No approval

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live blocked. No
executor/broker/OANDA changes. Test lockbox closed. `not_approved: true`.
