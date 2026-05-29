# CAMPAIGN_025 — data coverage & split decision

**Sprint:** train-matrix + champion-validation 001. **Test lockbox: CLOSED.**
Machine-readable copy: `research/campaign_025/train_matrix/data_coverage.json`.

---

## Per-pair materialized coverage (queried 2026-05-28)

M5/M15/H1/H4M1 from `m1_materialized`; H4 (native) feeds D1AGG.

| pair | M5 first | M5 last | M15 first | H1 first | H4M1 first | native H4 first..last |
|---|---|---|---|---|---|---|
| EUR_USD | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-26 | 2021-05-26 | 2020-01-01 .. 2026-05-24 |
| GBP_USD | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-26 | 2021-05-26 | 2020-01-01 .. 2026-05-24 |
| USD_JPY | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-26 | 2021-05-26 | 2020-01-01 .. 2026-05-24 |
| AUD_USD | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-26 | **2021-05-28** | 2020-01-01 .. 2026-05-24 |
| USD_CAD | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-26 | 2021-05-27 | 2020-01-01 .. 2026-05-24 |
| USD_CHF | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-27 | **2021-06-17** | 2020-01-01 .. 2026-05-24 |
| NZD_USD | 2021-05-26 | 2026-05-26 | 2021-05-26 | 2021-05-26 | 2021-05-27 | 2020-01-01 .. 2026-05-24 |

M5 counts ≈ 337k–363k bars/pair over the full ~5-year materialized span.
D1AGG (native-H4-derived) has full coverage from 2020-01-01, so its EMA20/50
warmup is never the binding constraint.

## Warmup requirements

- M5: ATR(14), Donchian(≤30), EMA — needs ≳60 prior M5 bars (minutes).
- M15: EMA20 + Donchian(12)/ATR(14) — ≳20 bars.
- H1 / H4M1 **context EMA50** — needs ≳52 completed higher-TF bars.
- D1AGG EMA50 — ≳52 D1 bars (covered from 2020 native H4).

**Binding constraint:** USD_CHF H4M1 starts **2021-06-17**; 52 H4M1 bars of EMA50
warmup ≈ ~2 market-weeks ⇒ usable from ≈ 2021-06-30.

## Selected split (frozen)

| split | window | note |
|---|---|---|
| **train** | **2021-07-01 → 2023-06-30** | 24 months; starts after all-pair H4M1 EMA50 warmup |
| **validation** | **2023-07-01 → 2024-12-31** | 18 months; strictly after train |
| **test (LOCKED, NOT run)** | 2025-01-01 → 2026-05-20 | unchanged from precommit; lockbox stays closed |

- Chronological order preserved; validation strictly after train; **test untouched**.
- The pre-committed scaffold train window (2020-01-01 → 2022-12-31) **cannot be used
  verbatim** — M5 does not exist before ~2021-05-26. We do **not** pretend otherwise.
- No pair is excluded; all seven have full M5/M15/H1/H4M1 over both train and
  validation windows after the 2021-07-01 warmup gate.

## What older history is unavailable

All of **2020-01-01 → 2021-05-25** has **no materialized M5/M15/H1/H4M1** (M1 source
not yet materialized that far back). This sprint makes no claim over that period.
Native H4 exists there but is used only to warm D1AGG, not as execution data.

## Is this enough history for a meaningful run?

Yes. 24 months train + 18 months validation × 7 pairs × M5 execution yields tens of
thousands of candidate signals (scaffold bounded probes already showed dozens of
signals per pair per few-month window). This is sufficient for a ≥100-trade
aggregate train filter and a ≥100-trade validation gate without touching the test
window. If, when run, any candidate cannot reach 100 train trades, classify
`BLOCKED_MATRIX_TOO_SPARSE` rather than forcing a verdict.

## Decision

**Proceed** with the narrowed split above. Not `BLOCKED_DATA_COVERAGE`: coverage is
ample and even across pairs within the chosen windows. Test lockbox remains closed.
