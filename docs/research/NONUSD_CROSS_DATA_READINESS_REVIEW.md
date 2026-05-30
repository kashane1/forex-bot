# Non-USD Cross Data Readiness Review (Sprint 001, Phase 6)

**Sprint:** `research-nonusd-cross-data-population-001`
**Status:** readiness reassessment on **real, populated** data. No factor
discovery, no hypothesis, no front-gate screen, no campaign, no approval.
Freeze intact.

## Summary

The first-wave non-USD crosses are no longer infrastructure assumptions —
they are **populated, validated, materialized, and cost-profiled from real
OANDA practice data** over the majors' window (2021-05-26 → 2026-05-26).
All eight crosses (4 required + 4 optional) are complete.

## Which crosses are fully populated

**All eight**, M1 + M5/M15/H1/H4M1, parity-verified:

| Cross | tier | M1 rows | M5 | M15 | H1 | H4M1 | parity |
|-------|------|---------|----|-----|----|------|--------|
| EUR_GBP | required | 1,823,232 | 346,991 | 107,953 | 23,598 | 4,045 | PASS |
| EUR_JPY | required | 1,841,779 | 360,104 | 116,586 | 27,403 | 5,289 | PASS |
| GBP_JPY | required | 1,852,770 | 365,917 | 119,806 | 28,446 | 5,609 | PASS |
| AUD_JPY | required | 1,857,000 | 367,668 | 120,433 | 28,770 | 5,757 | PASS |
| NZD_JPY | optional | 1,845,840 | 362,924 | 117,075 | 26,431 | 4,867 | PASS |
| EUR_CHF | optional | 1,811,686 | 343,763 | 107,931 | 24,120 | 4,249 | PASS |
| GBP_CHF | optional | 1,838,790 | 360,538 | 116,985 | 27,209 | 5,180 | PASS |
| EUR_AUD | optional | 1,849,425 | 363,783 | 118,250 | 27,797 | 5,407 | PASS |

Total: **14,720,522 M1 rows** + **4,050,884 materialized bars**. Single
fetch_batch_id per cross, 100% data_hash, 0 duplicate timestamps, 0 bid>ask,
0 non-positive spreads, 0 aggregation mismatches.

## Which remain incomplete

**None of the first wave.** Both the required and optional crosses are fully
populated. Not populated (by design, out of scope): any **native broker H4**
for crosses (only M1 was fetched; H4 is derived as H4M1), the diagnostic
**M3/M30** timeframes, and any **second-wave** instruments (no plans here).

## Data-quality concerns

1. **Missing-minute WARN is benign.** 7/8 crosses show quality `WARN`
   driven solely by the missing-minute heuristic (FX daily break + holidays
   counted against a naive all-weekday-minute expectation). A control major
   (USD_JPY) also `WARN`s under the identical heuristic; hard-integrity
   checks (dups, bid>ask, OHLC, non-positive spread) are **all zero**.
2. **No native H4 cross series** — `h4_consistency` reports
   `no_native_h4_in_store`. This is expected (M1-only fetch); the derived
   H4M1 is parity-verified against fresh M1 re-aggregation, so the H4 path
   is sound — it simply has no independent native series to cross-check.
3. **EUR_CHF 2015 SNB break is outside the window** (window starts 2021),
   so the populated EUR_CHF data is free of that discontinuity. The
   registry flag remains for any future longer-horizon ingest.
4. **Same ~5y window, same vendor, tick-count volume** — crosses add
   breadth, **not** history or true microstructure (unchanged from the
   infra-sprint readiness).

## Spread concerns

Measured (Phase 5): crosses are **wider and less stable** than the
comparable majors — cross median 1.4–3.1p vs major 1.3–1.9p; cross p99
8.4–19.9p vs major 4.9–11.8p; cross spread-volatility 1.3–3.2p vs 0.65–1.5p.
EUR_GBP (1.4p) is the only cross with a near-major central spread; AUD_JPY
and EUR_CHF are moderate; **GBP_JPY, EUR_AUD, GBP_CHF, NZD_JPY carry a
clearly higher cost wall** (wide medians + fat tails). The prior programme
was already cost-defeated on the *tighter* majors, so crosses do not relax
the binding cost constraint.

## Is factor discovery now technically justified?

**Technically justified to PLAN, on real data — but not performed, and not
authorized here.** With the data populated, validated, materialized, and
cost-profiled to the major-pair standard, the *technical* prerequisites for
factor-discovery work now exist (real bars, real spreads, parity-verified
timeframes, cost models that consume measured spreads). That is exactly the
boundary this sprint stops at.

Crucial framing carried forward unchanged:

- This justifies **planning** the next step, not running it. No hypothesis,
  screen, or campaign is created here.
- Crosses are a **breadth/replication** expansion. The two intended uses
  remain: (a) **independent replication** of the one genuine factor (C1) on
  non-collinear data via a *fresh pre-registered screen* (not a re-tune),
  and (b) **breadth families** (cross-sectional / carry / relative-value)
  that were data-blocked on USD-only majors.
- Any candidate must clear the **cost-realism gate** (round-trip spread +
  two-legged carry, using the now-measured wider/fatter-tailed cross
  spreads) before earning a screen — and the cost wall is *higher* here,
  not lower.

## Decision

`DATA_READY_FOR_DISCOVERY_PLANNING`. First-wave crosses are real and
research-grade. Proceed (in a later sprint) to **factor-discovery planning
only** — pre-screen, pre-campaign, pre-strategy. No edge work is performed
in this sprint.
