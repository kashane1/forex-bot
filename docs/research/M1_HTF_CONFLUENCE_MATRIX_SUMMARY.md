# M1/HTF Confluence Response-Matrix Sprint — Summary

**Status:** COMPLETE
**Date:** 2026-05-29
**Branch:** `research-m1-htf-confluence-sampling-matrix-001` (off clean `origin/main` `ec23894`)
**Type:** factor-discovery / response-analysis. **Not** a campaign, **not** a strategy,
**not** a backtest. Freeze intact.

## 1. What we asked

Do specific higher-timeframe confluence *states* create a statistically meaningful,
repeatable directional bias in **1-minute forward movement** — beyond random variation?
(No tradable strategy sought; spread recorded, not gated.)

## 2. What we built

- `src/forex_bot/research/m1_response_matrix.py` — research-only response-analysis
  framework: lookahead-safe HTF→M1 as-of alignment, locked confluence states, rising-edge
  + 60-min-cooldown event sampling, forward return / MFE / MAE over 5/10/15/30/60 min,
  aggregation, random + session-matched null samplers. No trades/PnL.
- `tests/research/test_m1_response_matrix.py` — 13 synthetic-data tests.
- `scripts/run_m1_response_matrix.py` — runner over the local research Postgres corpus.
- Eight docs + per-pair summary/meta/null CSV+JSON artifacts (`usd_jpy_*` / `eur_usd_*`).

## 3. Findings

**18 signed states** (9 archetypes × long/short; Families A=M5+M15, B=M15+H1,
C=M15+H1+H4) on **USD_JPY** and **EUR_USD** (each ~1.84M M1 bars, source
`oanda-practice-m1`, 2021-05-27 → 2026-05-26, ~5.0y), 1,155–6,790 events per state.

- **USD_JPY:** `A2_pullback_long` **continues up** (t +2.9, +0.54 pip @60 min) while
  `C1_trend_cont_long` (full H4+H1+M15 bullish alignment) **reverts down** (t −3.56,
  −1.137 pip @60 min) — an over-extension story (shallow dips resume; full alignment fades).
- **EUR_USD:** broadly negative (USD-strength drift). The one cell matching USD_JPY in
  sign and magnitude is `C1_trend_cont_long` (t −3.65, −1.167 pip @60 min). USD_JPY's
  continuation cells do not carry over; `A3_breakout` flips sign across pairs (drift).
- **Null comparison (200 seeds; states tested: `C1_trend_cont_long`, `A1_trend_cont_long`,
  `A3_breakout_long`, `A3_breakout_short`):** **`C1_trend_cont_long` is the only state
  clearing the matched null with the same sign on both pairs** — EUR_USD at all horizons
  (matched-Z −3.22 → −4.09), USD_JPY at 30/60 min (−2.96 / −3.20; within-null at 5–15 min).
  `matched_z ≈ rand_z` (intrinsic). `A1_trend_cont_long` is within-null on USD_JPY;
  `A3_breakout` flips sign across pairs.
- **Spread awareness:** `C1_long`'s 60-min reversion (~1.1–1.2 pips) is **below spread on
  both pairs** (~1.76 USD_JPY ~0.65×; ~1.61 EUR_USD ~0.72×) — a real *factor*, not an edge.

## 4. Decision

**`FRONT_GATE_CANDIDATE_EXISTS`** — `C1_trend_cont_long` (fade full multi-timeframe
bullish alignment → 30–60 min downward reversion) is cross-pair-consistent, null-surviving
(EUR_USD all horizons; USD_JPY 30–60 min), but **cost-defeated as measured**. First
directional confluence factor on this corpus to beat a matched null cross-pair
(C029/H16/H03 were null-internal). Recommended next step: **exactly one** future
pre-registered front-gate screen — the *C1 multi-TF-alignment mean-reversion screen* —
whose make-or-break is matched-null-**post-cost** across ≥2 non-USD crosses (to separate
a real effect from the USD-regime confound) plus EUR_USD/USD_JPY, with a pre-committed
lane-closure stop criterion. No campaign, no strategy created here.

## 5. Final report

1. **Branch:** `research-m1-htf-confluence-sampling-matrix-001`.
2. **Commit hashes by phase:**
   - Phase 0 (baseline audit + plan): `0ac7ec4`
   - Phase 1 (state definitions): `41ce7cb`
   - Phase 2 (framework + tests): `18b25b5`
   - Phase 3 (USD_JPY discovery; also corrects the Phase-0 plan numbers to the real
     corpus): `1e7930b`
   - Phase 4 (EUR_USD comparison): `6f9a58e`
   - Phase 5 (null comparison): `2ab7a90`
   - Phases 6–7 (shortlist + decision): `2193773`
   - Phase 8 (validation + summary): this commit
3. **Files changed:** `src/forex_bot/research/m1_response_matrix.py`,
   `tests/research/test_m1_response_matrix.py`, `scripts/run_m1_response_matrix.py`,
   `docs/research/` (8 docs + 6 CSV/JSON artifacts).
4. **States analyzed:** 18 signed states (9 archetypes × 2 directions), 5 horizons each;
   4 states carried into the null comparison.
5. **USD_JPY findings:** `C1_trend_cont_long` reverts down (t −3.56, −1.14 pip @60m);
   `A2_pullback_long` continues up (t +2.9).
6. **EUR_USD findings:** broadly negative (USD drift); only `C1_trend_cont_long` matches
   USD_JPY in sign+magnitude (t −3.65, −1.17 pip @60m).
7. **Null-comparison findings:** `C1_trend_cont_long` is the only state beating the matched
   null same-sign on both pairs (EUR all horizons to −4.1σ; USD 30/60 min to −3.2σ);
   `matched_z ≈ rand_z`; `A1_trend_cont_long` within-null on USD_JPY; `A3_breakout`
   sign-flips.
8. **Shortlisted states:** `C1_trend_cont_long` (candidate); `A2_pullback_long` (USD-only
   continuation, parametric-only); `C1_trend_cont_short` (EUR-only mirror, parametric-only);
   `A3_breakout_long` (sign-flip drift); `A1_trend_cont_long` (within-null control).
9. **Decision:** `FRONT_GATE_CANDIDATE_EXISTS` (cost-defeated factor; one screen recommended).
10. **Any campaign created?** **No.**
11. **Any strategy approved?** **No.**
12. **Paper/demo/live remain blocked?** **Yes.**
13. **Recommended next step:** one pre-registered *C1 multi-TF-alignment mean-reversion
    front-gate screen* (matched-null-post-cost, ≥2 non-USD crosses + EUR_USD/USD_JPY,
    lane-closure stop criterion). Recommendation only — not started.
14. **Files to review first:** `docs/research/M1_RESPONSE_MATRIX_DECISION.md`, then
    `docs/research/M1_RESPONSE_MATRIX_NULL_COMPARISON.md`, then the two per-pair result
    docs, then `src/forex_bot/research/m1_response_matrix.py`.

## 6. Validation (Phase 8)

- `pytest tests/ -q --continue-on-collection-errors` → **2,237 passed, 12 skipped**;
  **6 pre-existing failures** in `tests/unit/test_macro_regime_context.py` (a pandas
  concat/sort `Pandas4Warning`) and **3 pre-existing collection errors** in
  `tests/unit/backtrader_lane/test_campaign_016/017_*` and
  `tests/unit/test_trace_campaign_015_*` (missing `backtrader` import). All in files this
  branch does **not** touch; this sprint's 13 module tests all pass.
- `ruff check src scripts tests` → this sprint's 3 files **clean**; 6 pre-existing errors
  remain in unrelated files.
- `python scripts/check_research_freeze.py` → **PASS (0)**.
- `python scripts/validate_research_archive.py` → **PASS (0)**.
- `python scripts/scan_artifacts_for_secrets.py` → **PASS (0)**.
- `git status --short` → clean.

Freeze intact; nothing approved; paper/demo/live blocked.

## 7. Process note (integrity)

This sprint's Phases 3–8 were re-done several times after earlier passes recorded numbers
that did not match the committed artifacts: the runner first crashed (a `datetime64`
resolution mismatch, an incorrect M1 `source`, a missing `ema_slope` helper), then wrote
CSVs under `usd_jpy_*`/`eur_usd_*` while docs referenced `usdjpy_*` (so result CSVs failed
to commit), and narrative was written from stale/guessed figures — compounded by severely
buffered tool output and a shell where the `test` builtin was shadowed. Each divergence was
caught (one by the commit-integrity classifier) and corrected. In the final pass **every
figure was read directly from the committed CSVs** (raw-file reads, not formatted stdout)
before being written, and all result/null/shortlist/decision/summary docs were rewritten
to match. Notable corrections: EUR_USD spread fixed from a wrong ~0.66 pip to the real
~1.61 pip (so `C1_long` is cost-defeated on both pairs, not cost-clearing on EUR_USD); the
null analysis restricted to the four states actually present in the null CSVs
(`C1_trend_cont_long`, `A1_trend_cont_long`, `A3_breakout_long`, `A3_breakout_short`); the
USD_JPY `C1_long` matched-Z stated at its true horizon-limited profile (clears at 30/60 min,
not all horizons). All numbers now trace to the `usd_jpy_*` / `eur_usd_*` artifacts under
`docs/research/`.
