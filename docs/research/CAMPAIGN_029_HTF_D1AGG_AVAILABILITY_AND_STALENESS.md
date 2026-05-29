# CAMPAIGN_029 — HTF / D1AGG availability and staleness (frozen policy)

**Strategy:** `usdjpy_range_bar_mtf_breakout 0.1.0-c029`
**Status:** execution continuation; `NOT_RUN / NOT_APPROVED`
**Artifact:** [`research/campaign_029/execution/htf_staleness_summary.json`](../../research/campaign_029/execution/htf_staleness_summary.json)
**Script:** [`scripts/analyze_campaign_029_htf_staleness.py`](../../scripts/analyze_campaign_029_htf_staleness.py)

> Measures, at every 10-pip range-bar decision over **train (2021-05-27→2023-12-31)**
> and **validation (2024)**, whether the H4M1 trend and the native-H4-derived D1AGG
> regime are **available** and how **stale** the last completed HTF bar is. No
> signals, trades, or P&L; the test window is never loaded. The frozen staleness
> policy below binds the execution runner (Phase 3/5).

---

## 1. Availability over train / validation (measured)

| split | range bars | H4 missing | H4 stale (>8h) | H4 max staleness | D1AGG missing | D1AGG stale (>3d) | D1AGG max staleness |
|-------|-----------:|-----------:|---------------:|-----------------:|--------------:|------------------:|--------------------:|
| train | 33,457 | 182 | 4,697 | 517,620 s (~6.0 d) | 536 | 59 | 344,880 s (~4.0 d) |
| validation | 17,566 | 0 | 1,006 | 300,900 s (~3.5 d) | 0 | 52 | 340,980 s (~3.9 d) |

- **H4 available & fresh (≤8h):** train **28,578 / 33,457 = 85.4%**, validation
  **16,560 / 17,566 = 94.3%**.
- **D1AGG available & fresh (≤3d):** train **32,862 / 33,457 = 98.2%**, validation
  **17,514 / 17,566 = 99.7%**.
- H4 `missing` (182, train only) and D1AGG `missing` (536, train only) are the
  **EMA warm-up** at the very start of the corpus (H4M1 begins 2021-05-26; the
  EMA50 + slope need ~53 prior bars). Validation has zero missing.

## 2. Data-coverage finding (H4M1 is sparser than native H4) — noted constraint

Native `H4` holds **9,959** bars (2020-01-01 →, ≈30/week ≈ full). The **`H4M1`
(m1_materialized)** series holds **5,448** bars (≈21/week ≈ **70%** of native).
H4M1 omits bars whose underlying M1 window is incomplete (`missing_policy=omit`),
so the *gap to the last completed H4M1 bar* is frequently larger than the nominal
4 h — which is why the H4 stale count (>8h) is **14.6% of train** / **5.7% of
validation** decisions, with a long right tail (H4 max ~6 days over year-end /
holiday M1 gaps).

This is a **data-quality caveat, not a rule change**: the precommit froze
`context_h4 = m1_derived` (H4M1), so we keep H4M1 and **report** the coverage
limitation. The execution sprint should treat the resulting blocked fraction as a
real reduction in tradable sample (and a future backfill of H4M1 coverage as the
clean fix). It is flagged again as a remaining blocker in the summary.

## 3. Frozen binding staleness policy

Chosen **before** any trade evidence; may not change after results.

1. **H4 (mandatory trend bias):** if at the range-bar decision the last completed
   H4M1 bar is **missing** *or* **older than 8 hours** (`max_staleness = 8h =
   28,800 s`, i.e. > 2 nominal H4 bars) → **NO TRADE.** Enforced in
   `precompute_h4_trends(..., max_staleness_seconds=28_800)` which returns
   `HTF_STALE`/`HTF_UNAVAILABLE`; the engine skips any blocked decision.

2. **D1AGG (optional macro confirmation):** if at the decision the last completed
   D1AGG bar is **missing** *or* **older than 3 calendar days**
   (`max_staleness = 3d = 259,200 s`, covering normal weekend gaps) → the **D1AGG
   gate is skipped** and the trade is permitted on **H4 alone** (`d1agg_required =
   false`, frozen). Enforced in `precompute_d1agg_regimes(...,
   max_staleness_seconds=259_200)`; the engine treats the block as "gate not
   applied".

This is consistent with `CAMPAIGN_029_HTF_ALIGNMENT_DESIGN.md` (H4 mandatory,
D1AGG optional) and replaces its *candidate* bounds with these **final** values.

## 4. Lookahead safety

All alignment uses the last completed HTF bar at/before the decision
(`searchsorted` on completed HTF close times; cross-checked against the strategy's
`align_last_completed`-based `aligned_h4_trend` in
`tests/unit/test_range_bar_execution.py`). Staleness only ever **removes** trades;
it can never introduce a future bar.
