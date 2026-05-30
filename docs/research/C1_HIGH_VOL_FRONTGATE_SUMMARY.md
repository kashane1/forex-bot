# C1 High-Volatility Front-Gate Screen — Summary (Phase 8)

**Status:** COMPLETE
**Date:** 2026-05-29
**Branch:** `research-c1-high-volatility-frontgate-001` (off clean `origin/main`)
**Type:** front-gate SCREEN (pre-registered, single pass). **Not** a campaign,
strategy, backtest, or approval. Freeze intact.

## 1. What we asked

Does **volatility-conditioned `C1_trend_cont_long` mean-reversion** (fade full
H4+H1+M15 bullish alignment in a high-volatility regime) survive realistic
execution cost, beat a matched null, and prove stable — strongly enough to justify
a future campaign scaffold? Three outcomes: FAIL / INCONCLUSIVE / PASS.

## 2. What we built

- `scripts/run_c1_highvol_frontgate.py` — applies the frozen high-vol filter to
  C1_long events on EUR_USD/USD_JPY/GBP_USD and computes the subset's matched /
  randomised / **volatility-matched** nulls (200 seeds) via the locked
  `m1_response_matrix` samplers. No trade mechanics.
- Reused the committed C1 validation event panels for the event study, cost, and
  stability analyses; reused `c1_factor_validation.py` for frame/event construction.
- Eight docs + `docs/research/c1_highvol_frontgate/` artifacts (per-pair hi-vol
  event CSVs, `c1_hivol_nulls.csv`, `c1_hivol_meta.json`).

## 3. Verdict

# `FAIL_FRONT_GATE`

The effect is **statistically real and C1-specific** (it beats even a
volatility-matched null on both primaries) but is **cost-defeated** under the
frozen, realistic cost model and **concentrated** rather than broadly persistent.
By the pre-committed rule it fails on cost. ([decision](C1_HIGH_VOL_FRONTGATE_DECISION.md))

## 4. Final report

1. **Branch:** `research-c1-high-volatility-frontgate-001`.
2. **Commit hashes by phase:**
   - Phase 0 (audit + plan): `58fa5c3`
   - Phase 1 (frozen hypothesis + thresholds): `18c693a`
   - Phase 2 (event study): `391007e`
   - Phase 3 (cost study): `901e985`
   - Phase 5 (stability): `97a661a`
   - Phase 4 (null comparison + runner + artifacts): `d111d33`
   - Phase 6 (verdict): `b629aaa`
   - Phase 8 (validation + this summary): this commit
   - (Phase 7 intentionally absent — produced only on PASS.)
3. **Files changed:** `scripts/run_c1_highvol_frontgate.py`; `docs/research/`
   (8 docs: plan, hypothesis, event study, cost, null comparison, stability,
   decision, summary) + `docs/research/c1_highvol_frontgate/` artifacts.
4. **Event-study findings:** high-vol conditioning amplifies the 60-min reversion
   (EUR_USD −1.17→−1.78, USD_JPY −1.14→−2.09, GBP_USD −0.65→−1.26), but it is
   shallow/skew-driven (60-min median only −0.6/−0.65/−1.4; hit(neg) ≈ 0.52–0.55)
   and MAE > MFE at every horizon.
5. **Cost findings:** net-of-cost (spread_hivol + 0.5 slippage) is **negative on
   all three pairs** (EUR −0.36, JPY −0.23, GBP −1.36) and worse at 1.0-pip stress;
   the reversion only marginally clears the raw high-vol spread on the primaries
   and is below it on GBP. **Not economically meaningful.**
6. **Null findings:** both primaries beat the matched **and** volatility-matched
   null at 60 min (EUR matched-Z −3.71 / vol-matched −2.76; USD_JPY −3.48 / −2.58),
   and conditioning adds value everywhere — the effect is real and C1-specific.
   GBP_USD (quasi-OOS) fades at 60 min (matched-Z −1.87). **Null gate passes on
   primaries** but cannot rescue a cost-defeated effect.
7. **Stability findings:** sign persistent (negative in all 4 sessions on all 3
   pairs, most years) but **magnitude concentrated** in specific pair×session×year
   pockets (EUR_USD·London·2022, USD_JPY·Tokyo·2024); year-robustness not clean.
8. **Front-gate verdict:** `FAIL_FRONT_GATE` (cost wall; reinforced by concentrated
   stability and cost-defeated/null-failing generalisation pair).
9. **Any campaign created?** **No.**
10. **Any strategy approved?** **No.**
11. **Paper/demo/live remain blocked?** **Yes.**
12. **Recommended next step:** **None that creates anything.** Per the
    pre-committed stop, the M1/HTF time-bar confluence directional lane is **closed**
    on this corpus (C1 catalogued as a real-but-not-tradable factor). Reopen only
    with new data (10–15y / genuine non-USD crosses), tighter real execution data,
    or a new external thesis — via a fresh pre-registered screen, never a re-tune.
13. **Files to review first:** `C1_HIGH_VOL_FRONTGATE_DECISION.md` →
    `C1_HIGH_VOL_COST_STUDY.md` → `C1_HIGH_VOL_NULL_COMPARISON.md` →
    `C1_HIGH_VOL_EVENT_STUDY.md` / `C1_HIGH_VOL_STABILITY.md` →
    `C1_HIGH_VOL_HYPOTHESIS.md` (the frozen pre-commit).

## 5. Validation (Phase 8)

- `pytest tests/ -q --continue-on-collection-errors` → **2,389 passed, 3 skipped,
  0 failures** (skips are local-data-absent cases).
- `ruff check src scripts tests` → this sprint's files **clean**; 4 pre-existing
  `UP017` errors remain in `scripts/run_edge_discovery_vol_managed_tsmom.py`
  (C031 sprint), untouched here.
- `python scripts/check_research_freeze.py` → **PASS**.
- `python scripts/validate_research_archive.py` → **PASS**.
- `python scripts/scan_artifacts_for_secrets.py` → **PASS**.
- `git status --short` → clean.

Freeze intact; nothing approved; paper/demo/live blocked.

## 6. Note on method integrity

The decisive discipline was **pre-registration**: Phase 1 froze the pairs, the
volatility definition (within-pair top-tertile H4 ATR), the cost model
(spread + 0.5/1.0 slippage), the nulls, and the numeric PASS/FAIL thresholds
**before any conditioned number was computed** (committed in `18c693a`, ahead of
the Phase-2 results). The validation sprint's promising cost pockets were
**session-specific**; the honestly pre-registered **all-session** high-vol
hypothesis does not clear cost, and re-introducing a session filter post-hoc was
explicitly disallowed. The screen thus did exactly its job: it prevented a
post-hoc-attractive but cost-defeated pocket from being promoted, and it closed the
lane on a pre-committed rule rather than on a tuned one.
