# CAMPAIGN_026 — data coverage & train/validation split decision (Phase 6)

**Split frozen** (identical to CAMPAIGN_025, so the timeframe ladder is directly
comparable to the M5 rejection):

- **Train:** 2021-07-01 → 2023-06-30 (24 months)
- **Validation:** 2023-07-01 → 2024-12-31 (18 months)
- **Test:** 2025-01-01 → 2026-05-20 — **closed / unused (lockbox)**

No pair excluded.

## Per-pair coverage (materialized, M1-derived, UTC)

All execution + context timeframes begin **2021-05-27** and run to **2026-05-26** for
every pair (one exception: USD_CHF H4M1 begins 2021-06-17 — the same binding edge seen
in C025). Counts over full history:

| Pair | M3 | M15 | M30 | H1 | H4M1 (first) |
|---|---|---|---|---|---|
| EUR_USD | 606,857 | 116,628 | 56,671 | 27,249 | 2021-05-27 |
| GBP_USD | 602,436 | 115,243 | 55,863 | 26,758 | 2021-05-27 |
| USD_JPY | 608,321 | 118,035 | 57,767 | 28,013 | 2021-05-27 |
| AUD_USD | 591,765 | 109,904 | 52,459 | 24,774 | 2021-05-28 |
| USD_CAD | 601,816 | 114,562 | 55,339 | 26,405 | 2021-05-27 |
| USD_CHF | 573,219 | 105,604 | 50,192 | 23,400 | **2021-06-17** |
| NZD_USD | 594,912 | 110,462 | 52,125 | 23,856 | 2021-05-27 |

(All last = 2026-05-26.)

## D1AGG coverage

D1AGG is derived from **native H4** (`source=oanda-practice`), which spans **2020-01-01
→ 2026-05-24** (69,648 bars). This gives D1AGG **years** of history before the train
start, so the daily regime filter is fully warmed for the entire train window.

## Warmup requirements vs the split

Train starts 2021-07-01; materialized execution/context frames begin 2021-05-27
(USD_CHF H4M1 2021-06-17) → ~35 calendar days (USD_CHF ~14 days) of pre-train warmup.
Binding indicator warmups:

| Indicator | Warmup | Covered? |
|---|---|---|
| Execution Donchian(30) / ATR(14) | M3 ≤1.5h, M15 ≤7.5h, M30 ≤15h | ✓ |
| Local setup (EMA20 + pullback8 / compression) | ≤28 bars of local frame (M15 ≤7h, H1 ≤28h) | ✓ |
| H1 trend EMA(50) + slope(3) | ~53h | ✓ |
| H4 trend EMA(50) | ~8.3 days | ✓ (incl. USD_CHF 14-day buffer) |
| D1AGG EMA(50) + slope(3) | ~70 calendar days | ✓ (native H4 from 2020) |

The loader requests a 60-day warmup buffer (from ~2021-05-02); the effective buffer is
~35 days (data starts 2021-05-27), which still exceeds every execution/context
warmup, and D1AGG is independently warmed from 2020. **The preferred split is fully
supported for all three execution timeframes and all seven pairs.**

## Comparability to C025

The split is **identical** to C025 (same train/validation windows, same pairs, same
D1AGG source). C026 therefore isolates the **execution-timeframe** variable cleanly:
any difference vs C025's M5 rejection is attributable to timeframe (and its cost/edge
profile), not to a different sample.

## Limitations

- M1 history begins ~2021-05; pre-2021 is unavailable and not claimed (same as C025).
- USD_CHF H4M1 begins 2021-06-17; its H4 trend gate is warm by the 2021-07-01 train
  start (8.3-day requirement < 14-day buffer), so no pair is excluded.
- Incomplete buckets (weekend/session edges) are omitted by the materialization policy;
  the simulator only counts trades whose signal bar falls inside the window.

Test lockbox stays **closed** — no window in this sprint intersects 2025-01-01…2026-05-20.
