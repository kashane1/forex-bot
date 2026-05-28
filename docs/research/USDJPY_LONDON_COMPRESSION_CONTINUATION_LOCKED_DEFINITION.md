# USD_JPY London Compression-Continuation — Locked Definition

**Sprint:** `usdjpy-london-compression-continuation-confirmation-001` · **Phase 1**
**Purpose:** freeze the candidate **exactly and narrowly BEFORE any new simulation**, so
the Phase-2 confirmation cannot drift into threshold-mining. Nothing below may be changed
after results are seen; the only allowed outputs are pass/fail against these locked terms.

> This is a locked specification, not a strategy and not an edge claim. No campaign, no
> C024, no C023, no approval. TEST sealed.

---

## 1. Locked candidate definition

| dimension | locked value |
|---|---|
| Instrument | **USD_JPY only** |
| Timeframe | **M15** |
| Session | **London only** (per the canonical `session_bucket`: London 08:00–16:00 Europe/London active, AND not NY-active → bucket `london`; the overlap bucket is **excluded**) |
| Compression state | **≥3 of 4 percentile features ≤ 0.20** {range_pct, atr_pct, bandwidth_pct, realized_vol_pct}, decision-time, from `forex_bot.research.volatility_compression_expansion` (unchanged from prior sprint) |
| Trigger | **first break of the prior 16-bar range** in bars `i+1..i+h` (the decision bar `i` is the completed compressed London M15 bar) |
| Direction | **continuation** — enter in the break direction at the broken level |
| Horizons | **h16 and h32 only** (the prior positive horizons; no others tested) |
| Exit | horizon close **or** intrabar protective stop, whichever first |
| Data | **train (2021-06-01..2023-12-31) + validation (2024-01-01..2025-06-30) only** |
| TEST | **2025-07-01+ sealed — not read** |

Entry timing is a diagnostic next-bar-open approximation (level fill on the break bar);
slippage is charged via the cost variants below.

## 2. Locked cost variants (round-trip pips)

| variant | round-trip cost | basis (atlas-measured London spread: med 1.7, p90 1.9) |
|---|---|---|
| optimistic | **2.2** | ~1 spread + 0.5 slippage |
| base | **4.4** | 2 × median (1.7) + 1.0 slippage |
| conservative | **5.8** | 2 × p90 (1.9) + 2.0 slippage |

Whipsaw (both sides of the prior range break before the horizon) charges **one extra
round-trip** of the same variant.

## 3. Locked intrabar protective-stop variants

| variant | stop distance (from entry level, adverse) |
|---|---|
| none | hold to horizon close |
| range_1.0x | 1.0 × compressed decision-bar (high−low) |
| range_1.5x | 1.5 × compressed decision-bar (high−low) |
| atr_1.0x | 1.0 × decision-bar ATR(14) |

Intrabar fill rule: scanning bars from the break bar to `i+h`, if the bar's adverse
extreme (low for longs, high for shorts) breaches `entry ∓ stop`, the trade exits at the
stop level (loss = stop distance + cost). Otherwise it exits at `close[i+h]`. No stop
distance is optimized.

## 4. Locked multiple-testing haircut

The prior sprint searched **12 cells** (6 sessions × 2 horizons) for continuation. The
London cell is therefore 1 of 12. Confirmation requires the per-trade mean to be
statistically positive **after a Bonferroni-style haircut**: report the one-sample
t-statistic and two-sided p-value of per-trade net pips, and the **Bonferroni-adjusted
p (× 12)**; require adjusted p < 0.05 on **both** splits for a "survives haircut" pass.

## 5. Locked KILL criteria (any one ⇒ fail)

The lead **fails confirmation** (→ NOT_READY, and if clearly dead → PAUSE_STRATEGY_RESEARCH) if:

1. train **or** validation net expectancy ≤ 0 after **base** cost (no stop or with stop);
2. **conservative** cost flips **either** split negative;
3. the intrabar stop model (any of the predeclared stops) **eliminates** the positive
   expectancy on either split;
4. sample size is too small — fewer than **~150 trades per split** in the confirmed
   configuration;
5. results depend on a single threshold/cell (i.e. only survive at one cost/stop/horizon
   combination and collapse at the adjacent predeclared ones);
6. the multiple-testing haircut (×12) removes significance on either split;
7. the effect is dominated by outliers — removing the **top 5 trades by |pips|** flips
   either split negative;
8. year/half-split robustness fails — the sign is **not** consistent across the
   per-year buckets within each split.

## 6. What is explicitly NOT allowed in Phase 2+

- No new session tested (London only).
- No new horizon (h16/h32 only).
- No new cut (0.20 consensus only; the {0.10,0.30} grid is reported for robustness, not
  for selection).
- No added entry/exit filters, no parameter search, no "best variant" cherry-pick.
- The pass/fail is read off the **base** cost + **predeclared** stop set, not the most
  favorable combination.

This definition is frozen as of this commit. Phase 2 implements it verbatim.
