# CAMPAIGN_026 — Donchian + HTF confluence timeframe-ladder (001) SUMMARY

**Final classification:** `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE /
TEST_LOCKBOX_CLOSED / NOT_APPROVED`. 0/11 candidates eligible on train across M3/M15/M30;
no champion; validation not run; no approval; lockbox closed.

---

1. **Branch:** `research-campaign-026-donchian-htf-timeframe-ladder-001` (off main @
   `a38126d`, post-C025-REJECT merge).
2. **Commit hashes by phase:** 0 `1eeab1c` (audit+plan) · 1 `bad9b18` (M3/M30 support) ·
   2 `29825e2` (materialize+verify) · 3 `8ea42b6` (cost diagnostic + C026 code) ·
   4 `7a30ec0` (frozen matrix+spec) · 5 `aec1e45` (tests) · 6 `7339087` (split) ·
   7 `8f335c4` (train REJECT) · 8 `e01901b` (validation not run) · 9–10 `54dd6cd`
   (interpretation + parity) · 11 `2dda414` (registry/archive/status) · 12 _this summary
   + final validation_.
3. **Files changed by phase:** P0 plan doc · P1 `domain/candles.py`,
   `data/timeframe_aggregation.py`, `data/m1_timeframe_materialization.py`,
   `scripts/materialize_m1_derived_timeframes.py` + 2 test files + design doc · P2
   `scripts/materialize_campaign_026_m3_m30.py` + 6 materialization artifacts + result
   doc · P3 `campaign_026_loader.py`, `campaign_026_timeframe_ladder.py`,
   `run_campaign_026_donchian_htf_timeframe_ladder.py` + 6 cost artifacts + diagnostic
   doc · P4 spec doc + `candidate_registry.json` · P5 2 unit-test files · P6 split doc ·
   P7 12 train artifacts + result doc · P8 `validation_result.json` + validation doc ·
   P9–10 interpretation + parity docs · P11 STRATEGY_STATUS / EVIDENCE_INDEX /
   EVIDENCE_MANIFEST / FUTURE_RESEARCH_BACKLOG + archive test roster · P12 this summary.
4. **Did M3/M30 have to be materialized?** **Yes** — both were absent (Phase 0 audit).
   M3/M30 support added (hash-stable, opt-in) and materialized from canonical M1.
5. **M3/M30 materialization row counts + verification:** M3 ≈ 4.18M bars, M30 ≈ 380K
   bars, 7/7 majors, 2021-05-27→2026-05-26. **Verification PASS** (full-window SQL: 0
   duplicate / 0 misaligned / 0 OHLC-order / 0 bid-ask-order / 0 incomplete-stored;
   exact re-aggregation cross-check: 0 missing / 0 extra / 0 mismatch). No broker calls.
6. **Data coverage & split decision:** all execution/context TFs begin 2021-05-27
   (USD_CHF H4M1 2021-06-17); D1AGG from native H4 (2020→). Split frozen **identical to
   C025** for comparability; no pair excluded; warmup satisfied for all TFs/pairs.
7. **Train window:** 2021-07-01 → 2023-06-30 (24 months).
8. **Validation window:** 2023-07-01 → 2024-12-31 — **not run** (no champion).
9. **Candidate count:** **11** (`C026_TF_001`…`011`; preferred count, ≤15 cap).
10. **Timeframes tested:** M3, M15, M30 (M5 as C025 reference in the cost diagnostic).
11. **Candidate parameter dimensions:** Donchian {20,30}; ATR stop {2.0,2.5}×;
    exits {fixed_2r, fixed_3r, breakeven_then_atr_trail, donchian_channel_exit};
    time-stop {24,32,36,48,60,90} bars; context {standard, strict}; local setup
    {pullback_or_compression, pullback_only}.
12. **Spread/ATR by timeframe (median):** M3 0.59 · M5(ref) 0.44 · M15 0.23 · M30 0.15.
13. **Cost diagnostics by timeframe:** monotone decreasing with slower TF; M3
    cost-hostile (≥0.30) and worse than M5; M15/M30 materially better; Asia session
    worst at every TF; USD_JPY cheapest pair, NZD/CAD/CHF most expensive (stable
    across TFs). Decision: **PROCEED** (not BLOCKED_COST_STRUCTURE).
14. **Train matrix results:** all 11 net-negative; expectancy_R −0.0083…−0.182; PF
    0.66–0.976; ≤2/7 pairs non-negative; 2× stress −0.11…−0.73R; none beats the C011
    null (−0.0029R). **0/11 eligible.**
15. **Result by timeframe (best candidate expectancy_R / PF / median spread-ATR):**
    M3 −0.140 / 0.73 / 0.59 · **M5 (ref, C025) −0.077 / 0.85 / 0.44** · M15 −0.039 /
    0.92 / 0.23 · M30 **−0.0083 / 0.976 / 0.15**. Expectancy improves monotonically as
    TF slows, tracking spread/ATR — but never crosses zero.
16. **Selected champion:** **none** (0/11 eligible).
17. **Champion timeframe/parameters:** n/a.
18. **Why none selected:** every candidate failed expectancy≥0, PF≥1.03, ≥3/7 pairs
    non-negative, and 2×-stress≥−0.005 simultaneously. Trade-count floors passed
    (1,592–8,544 trades) — not a scarcity failure. No positive-expectancy candidate, so
    no single-pair-review flag.
19. **Validation ran?** **No** — no champion, so `--validate-champion` returned
    `validation_run: false`. Validation was never executed.
20. **Validation metrics:** n/a.
21. **Gate table:** train filters above (all fail expectancy/PF/pairs/stress);
    validation gates not evaluated.
22. **Pair-level results:** best candidate C026_TF_010 (M30): USD_JPY +0.190,
    NZD_USD +0.039 positive; EUR/GBP/AUD/CAD/CHF negative (2/7). USD_JPY the only
    consistently-positive leg across timeframes (M15 +0.124) — the same lone-USD_JPY
    pattern as C025.
23. **Side-level results:** longs/shorts both negative on M3/M15; on M30 TF_010 longs
    +0.035R but shorts −0.050R → net negative. No directional edge.
24. **Exit-reason distribution:** time-stops + hard-stops dominate every candidate;
    fixed targets convert ~13–25%; M30 trailing/breakeven least-bad; none profitable.
25. **Holding diagnostics:** avg hold M3 ≈ 39–54 bars (~2–2.7h), M15 ≈ 25–37 (~6–9h),
    M30 ≈ 20–30 (~10–15h). Slower TFs hold longer, amortising fixed cost.
26. **Signal-funnel diagnostics:** healthy at every TF (M30 TF_010: 144,731 bars →
    14,218 breakouts → 4,912 gated signals → 1,592 entries; M3 TF_001: 1.64M bars →
    35,710 signals → 8,544 entries). Failure is cost-adjusted **quality**, not quantity.
27. **2× cost stress:** −0.11…−0.16R (M30), −0.21…−0.28R (M15), −0.60…−0.73R (M3) — all
    ≪ the −0.005 floor.
28. **C011 null comparison:** no candidate beats −0.0029R; best (TF_010) is 0.0054R
    *below* it; the +0.010R promotion margin failed by all.
29. **SINGLE_PAIR_REVIEW_ONLY assessment:** **not triggered** — USD_JPY's edge is best
    explained by its cheap spread, fails 2× stress, aggregate negative; also duplicates
    the already-exhausted USD_JPY microstructure thread.
30. **Backtrader parity readiness:** `DEFER_PARITY_REJECTED` (no champion). Parity risk
    spec recorded for a future externally-motivated revival.
31. **Final verdict/classification:** `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE /
    TEST_LOCKBOX_CLOSED / NOT_APPROVED`. The lower-timeframe Donchian + HTF family is
    rejected across M3–M30.
32. **Any tuning occurred?** **No** — matrix frozen (Phase 4) before train evidence
    (Phase 7); no post-result parameter or gate changes.
33. **Validation influenced selection?** **No** — selection is train-only by
    construction (`selection_uses_validation: false`); validation never ran.
34. **Test lockbox opened?** **No** — runner refuses any window intersecting
    2025-01-01…2026-05-20 (`--fail-if-test-window` default on).
35. **Any strategy approved?** **No** — `approved_strategies.yaml` = `approved: []`.
36. **Paper/demo/live blocked?** **Yes.**
37. **Archive/freeze/secrets status:** research freeze **PASS**, research archive
    **PASS**, secret scan **PASS** (Phase 12 final validation, worktree src).
38. **Ruff/pytest:** ruff **clean** (src/tests/scripts/research); pytest **2101 passed /
    3 skipped** (the 3 skips are pre-existing local-data-absent; baseline was 2073, +28
    new C026 tests across aggregation/materialization/simulator/registry/runner-guards).
    Run with `PYTHONPATH=$PWD/src` so the suite exercises the worktree code.
39. **Known blockers/warnings:** M1 history begins ~2021-05 (pre-2021 unavailable, not
    claimed); USD_CHF H4M1 from 2021-06-17 (warm by train start). A pre-existing cosmetic
    f-string bug in the shared `verify_materialized_pair` mismatch label (`field` vs
    `price_field`) never executed (no mismatches); flagged, out of scope.
40. **Recommended next sprint & why:** **None for this family.** Close the
    lower-timeframe Donchian + HTF construct across M3–M30 and stop tuning it — the
    cost-ladder experiment was the decisive test and returned a clean null (cost
    gradient, no edge). Any revival needs a **new external thesis/signal**, not another
    timeframe/parameter sweep (consistent with the standing `PAUSE_STRATEGY_RESEARCH`
    posture). The M3/M30 materialization + timeframe cost-diagnostic infrastructure is
    reusable for future timeframe-sensitive studies.
41. **Files to review first:**
    [`CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md`](CAMPAIGN_026_TIMEFRAME_LADDER_INTERPRETATION.md),
    [`CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md`](CAMPAIGN_026_TRAIN_TIMEFRAME_LADDER_RESULT.md),
    [`CAMPAIGN_026_TIMEFRAME_COST_ATR_DIAGNOSTIC.md`](CAMPAIGN_026_TIMEFRAME_COST_ATR_DIAGNOSTIC.md),
    [`../../src/forex_bot/research/campaign_026_timeframe_ladder.py`](../../src/forex_bot/research/campaign_026_timeframe_ladder.py).
