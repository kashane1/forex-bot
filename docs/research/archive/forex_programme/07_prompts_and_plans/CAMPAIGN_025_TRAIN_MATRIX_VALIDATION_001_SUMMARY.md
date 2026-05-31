# CAMPAIGN_025 — train-matrix + champion-validation (001) SUMMARY

**Final classification:** `REJECT_MATRIX_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED /
NOT_APPROVED`. No champion, no validation, no approval, lockbox closed.

---

1. **Branch:** `research-campaign-025-m5-donchian-htf-confluence-train-matrix-validation-001`.
2. **Commit hashes by phase:** 0 `444a0eb` (audit+plan) · 1 `33f0cf7` (coverage+split) ·
   2 `30cdd2d` (matrix spec+registry+tests) · 3 `40542eb` (runner+simulator+tests) ·
   4 `2f65d5f` (train matrix executed) · 5 `39b09a2` (no champion / no validation) ·
   6+7 `5913385` (interpretation + parity readiness) · 8 `ccc7333` (registry) ·
   9 _this commit_ (final validation + summary).
3. **Files changed by phase:** P0 plan · P1 coverage/split doc + `data_coverage.json` ·
   P2 matrix spec + `candidate_registry.json` + registry tests · P3
   `campaign_025_train_matrix.py` + runner train-matrix/validate-champion modes +
   simulator tests · P4 train-matrix artifacts (CSV/JSON) + result doc · P5 champion
   validation result doc · P6 interpretation doc · P7 parity readiness doc · P8
   STRATEGY_STATUS / EVIDENCE_INDEX / EVIDENCE_MANIFEST / FUTURE_RESEARCH_BACKLOG ·
   P9 this summary.
4. **Data coverage & split decision:** materialized M5/M15/H1/H4M1 begin ~2021-05-26
   (binding: USD_CHF H4M1 2021-06-17); native H4 (D1AGG) from 2020. Narrowed split
   frozen; pre-committed 2020–2022 train window unusable (no M5). No pair excluded.
5. **Train window:** 2021-07-01 → 2023-06-30 (24 months).
6. **Validation window:** 2023-07-01 → 2024-12-31 — **not run** (no champion).
7. **Matrix candidate count:** 16 (`C025_MTX_001`…`016`).
8. **Parameter dimensions:** Donchian {12,20,30}; stop {1.5,2.0,2.5}×ATR (farther of
   channel); time stop {36,48,72}; H1 {standard,strict}; M15 {pullback_or_compression,
   pullback_only, compression_only}.
9. **Exit models tested:** time_stop_only, fixed_2r_target, fixed_3r_target,
   breakeven_then_atr_trail, donchian_channel_exit.
10. **Train matrix results summary:** all 16 net-negative; expectancy_R −0.077 to
    −0.178; PF 0.70–0.85; ≤1/7 pairs non-negative; 2× cost-stress −0.40 to −0.75R;
    none beats the C011 null.
11. **Candidate selection filters:** trades≥100 (all pass), expectancy≥0 (all fail),
    PF≥1.03 (all fail), ≥3/7 pairs non-negative (all fail), 2×stress≥−0.005 (all
    fail), single-pair concentration≤0.50 (all pass). **0/16 eligible.**
12. **Selected champion:** **none.**
13. **Champion parameters:** n/a.
14. **Why none selected:** every candidate failed the expectancy/PF/pairs/stress
    filters; the matrix is uniformly negative after cost. No rescue, no invented
    champion (per protocol).
15. **Validation ran?** **No** — no champion, so promotion-style validation was not
    run (`--validate-champion` returned `validation_run: false`).
16. **Test lockbox opened?** **No** (runner refuses the 2025+ window).
17. **Full evidence beyond train-matrix/champion-validation?** **No.**
18. **Train metrics for champion:** n/a (no champion).
19. **Validation metrics for champion:** n/a (validation not run).
20. **Gate table:** train selection filters above; validation gates not evaluated.
21. **Pair-level results:** USD_JPY the only weakly non-negative pair on a few
    candidates (+0.02 to +0.04R), not cost-robust; the other six majors negative on
    every candidate.
22. **Side-level results:** longs and shorts both negative, symmetric (~−0.12R each
    on baseline).
23. **Exit-reason distribution:** stops + time stops dominate; fixed targets convert
    ~13% of exits but don't help; channel exits fire often (010: 3602) yet stay
    negative; trailing (008/009) least-bad but negative.
24. **Holding diagnostics:** avg hold 24–55 M5 bars (~2–4.6h); scalps shortest,
    runners longest.
25. **Spread/ATR diagnostics:** ≈ 0.45–0.50 across all candidates — the decisive
    structural cost fact on M5.
26. **Signal-funnel diagnostics:** (baseline) 964,176 M5 bars → H4 80% → H1 72% →
    breakout 12% → 21,625 gated signals → 5,657 entries. Funnel healthy; problem is
    cost-adjusted quality, not scarcity.
27. **2× cost stress:** −0.40 to −0.75R for all candidates (≪ the −0.005 floor).
28. **C011 null comparison:** no candidate beats the −0.0029R null; best is ~0.074R
    below it; +0.010R beat-margin failed by all.
29. **Matrix robustness assessment:** "robust badness" — all 16 negative, monotone
    with turnover; no fragile-but-promising corner.
30. **Parameter fragility assessment:** the only systematic gradient is turnover
    (faster = worse); no parameter dimension makes the family positive.
31. **Exit-model assessment:** time_stop_only — neutral framing, still negative;
    fixed_2r/3r — cap winners, no help; breakeven_then_atr_trail — least-bad
    (amortizes cost over longer holds) but negative; donchian_channel_exit — exits
    late, negative.
32. **SINGLE_PAIR_REVIEW_ONLY assessment:** **not triggered** — USD_JPY is not
    materially strong (small edge, fails 2× stress) and aggregate evidence is
    negative.
33. **Backtrader parity readiness:** `DEFER_PARITY_REJECTED` (nothing passed train).
34. **Final verdict/classification:** `REJECT_MATRIX_NO_TRAIN_CANDIDATE /
    TEST_LOCKBOX_CLOSED / NOT_APPROVED`.
35. **Any tuning occurred?** **No.**
36. **Validation influenced selection?** **No** (validation never ran; selection is
    train-only by construction).
37. **Any strategy approved?** **No** — `approved_strategies.yaml` = `approved: []`.
38. **Paper/demo/live blocked?** **Yes.**
39. **Archive/freeze/secrets status:** research freeze **PASS**, research archive
    **PASS**, secret scan **PASS**.
40. **Ruff/pytest:** ruff **clean** (src/tests/scripts/research); pytest
    **2055 passed / 3 skipped** (the archive-roster test
    `test_real_manifest_has_all_campaigns` was updated to include `CAMPAIGN_025`).
41. **Known blockers/warnings:** M5 materialized history begins ~2021-05; pre-2021
    is unavailable and not claimed. The cost model deducts fixed-slippage + spread×
    multiplier per fill from PnL (exit *triggers* are cost-agnostic) — a documented
    simplification; a future Backtrader parity build would tighten this.
42. **Recommended next sprint & why:** **None for the C025 family** — it is REJECT
    and must not be re-gated/re-tuned. If M5 is revisited at all, a *new* idea must
    clear a **cost-stress gate before signal design** (spread/ATR ≈ 0.5 is the
    blocker) and target a much larger per-trade move or a lower-spread regime.
    Otherwise hold/freeze.
43. **Files to review first:**
    [`CAMPAIGN_025_TRAIN_MATRIX_RESULT.md`](CAMPAIGN_025_TRAIN_MATRIX_RESULT.md),
    [`CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md`](CAMPAIGN_025_INTERPRETATION_AND_PRIOR_COMPARISON.md),
    [`CAMPAIGN_025_TRAIN_MATRIX_SPEC.md`](CAMPAIGN_025_TRAIN_MATRIX_SPEC.md),
    [`src/forex_bot/research/campaign_025_train_matrix.py`](../../src/forex_bot/research/campaign_025_train_matrix.py).
