# C1 Factor Validation — Sprint Summary (Phase 8)

**Status:** COMPLETE
**Date:** 2026-05-29
**Branch:** `research-c1-factor-validation-001` (off clean `origin/main`)
**Type:** factor-validation / response-analysis. **Not** a campaign, **not** a
strategy, **not** a backtest, **not** a front gate. Freeze intact.

## 1. What we asked

Determine whether `C1_trend_cont_long` — the one state that survived the M1/HTF
confluence sampling matrix (fade full H4+H1+M15 bullish alignment → 30–60-min M1
reversion down) — is (1) a genuine market factor, (2) a USD-regime artifact,
(3) a sample-selection artifact, or (4) a statistical mirage. **No strategy, no
campaign, no trading.**

## 2. What we built

- `src/forex_bot/research/c1_factor_validation.py` — research-only analysis layer
  over the locked `m1_response_matrix` framework (parametrised `C1Spec`, per-event
  panel with regime covariates + signed EMA50 extension, currency-leg helpers, C1
  null comparison, grouped summaries). No trade mechanics.
- `tests/research/test_c1_factor_validation.py` — 10 synthetic-data tests.
- `scripts/run_c1_factor_validation.py` — runner over the 7-major research corpus;
  emits per-pair event/null CSVs + a cross-pair robustness CSV under
  `docs/research/c1_validation/`.
- Eight docs (this sprint) + the CSV/JSON artifacts they cite.

Integrity: the USD_JPY/EUR_USD C1_long panels reproduce the prior sprint's
mean/t exactly; all reported numbers are read back from committed CSVs.

## 3. Findings by phase

- **Phase 1 (cross-pair, 7 majors):** C1_long signed 60-min return is **negative
  on 7/7 pairs**; null-surviving strongly on **EUR_USD (mZ60 −4.21)** and
  **USD_JPY (−3.55)**, at 30 min on GBP_USD, within-null on NZD/AUD/CHF/CAD.
  **Sign universal, magnitude concentrated** on the two discovery pairs.
- **Phase 2 (regime):** **persistent** — negative in 5/6 years (sig 2023–25) and
  all 4 sessions; reversion **grows monotonically with volatility** (hi-ATR
  tertile t −3.78) and **extension** (hi tertile t −3.59) → over-extension
  mechanism, not an episode.
- **Phase 3 (USD confound):** **not a USD artifact** — base vs quote pair-space
  sign equal & negative (no flip, unlike `A3_breakout`); long & short mirror both
  revert; cross-pair synchrony low (within 0.21/0.30, across −0.08). Residual:
  all pairs share the USD leg, so a modest USD share is non-excludable without
  non-USD crosses (absent from corpus).
- **Phase 4 (robustness):** sign negative in **55/56** spec×pair cells across 8
  one-knob perturbations; EUR_USD/USD_JPY significant under nearly all; confluence
  depth not a knife-edge (drop-H4 and add-M5 both hold). **Not a spec-tuned
  mirage.**
- **Phase 5 (cost):** **cost-defeated unconditionally** on all 7 (best EUR_USD
  0.73× spread). But a vol-conditioned cost-aware path survives: EUR_USD London
  hi-vol (median −2.0, t −3.4) and USD_JPY Tokyo hi-vol (median −2.25, t −2.8)
  show **positive spread-adjusted reversion surviving an outlier check** (one cell,
  USD_JPY NY, caught as an outlier mirage). Optimistically costed, post-hoc → a
  *hypothesis*, not a demonstration.
- **Phase 6 (verdict):** `FACTOR_FRONT_GATE_CANDIDATE`.
- **Phase 7:** copy-paste prompt for the one earned screen.

## 4. Verdict

**`FACTOR_FRONT_GATE_CANDIDATE`.** C1 is a **genuine factor** (#1) — the other
three explanations are excluded (USD-artifact by Phase 3, selection by Phase 2,
mirage by Phase 4). It is cost-defeated as a flat signal but retains one
economically-motivated cost-aware sub-regime (high-volatility on EUR_USD/USD_JPY)
that earns **exactly one** future pre-registered post-cost out-of-sample
front-gate screen, with a pre-committed lane-closure stop. See
`C1_FACTOR_VERDICT.md`.

## 5. Final report

1. **Branch:** `research-c1-factor-validation-001`.
2. **Commit hashes by phase:**
   - Phase 0 (audit + plan): `e9ae1b8`
   - Analysis module + tests + runner: `cb68b01`
   - Phase 1 (cross-pair study + CSV artifacts): `c78dbde`
   - Phase 2 (regime stability): `d0ecfca`
   - Phase 3 (USD confound): `3cbea4f`
   - Phase 4 (robustness): `2a33c2b`
   - Phase 5 (cost realism): `eec9449`
   - Phase 6 (verdict): `5d395e7`
   - Phase 7 (next prompt): `eceffae`
   - Phase 8 (validation + this summary): this commit
3. **Files changed:** `src/forex_bot/research/c1_factor_validation.py`,
   `tests/research/test_c1_factor_validation.py`,
   `scripts/run_c1_factor_validation.py`, `docs/research/` (9 docs + the
   `c1_validation/` CSV/JSON artifacts: 7×events, 7×nulls, robustness, meta).
4. **Cross-pair findings:** C1_long negative 7/7; significant on EUR_USD +
   USD_JPY (+ GBP_USD at 30 min); sign does not flip with USD leg.
5. **Regime findings:** persistent across years/sessions; reversion grows
   monotonically with volatility and extension.
6. **USD-confound findings:** not a USD-directional artifact (no base/quote
   sign-flip, symmetric long/short, low synchrony); residual shared-USD component
   non-excludable on a USD-only corpus.
7. **Robustness findings:** sign-stable in 55/56 spec×pair cells; strong pairs
   survive every reasonable perturbation; not a knife-edge.
8. **Cost findings:** cost-defeated unconditionally (best 0.73×); a high-vol
   sub-regime on EUR_USD/USD_JPY shows positive spread-adjusted reversion
   (post-hoc, optimistically costed → must be screened, not assumed).
9. **Final verdict:** `FACTOR_FRONT_GATE_CANDIDATE` (genuine factor; one screen).
10. **Any campaign created?** **No.**
11. **Any strategy approved?** **No.**
12. **Paper/demo/live remain blocked?** **Yes.**
13. **Recommended next step:** one pre-registered *high-volatility C1-fade
    front-gate screen* (post-cost, out-of-sample, matched-null, EUR_USD/USD_JPY
    (+GBP_USD), hard lane-closure stop). Recommendation only — not started.
14. **Files to review first:** `C1_FACTOR_VERDICT.md` → `C1_USD_CONFOUND_STUDY.md`
    → `C1_CROSS_PAIR_STUDY.md` → `C1_COST_REALISM_STUDY.md` →
    `C1_ROBUSTNESS_STUDY.md` / `C1_REGIME_STABILITY_STUDY.md` →
    `src/forex_bot/research/c1_factor_validation.py`.

## 6. Validation (Phase 8)

- `pytest tests/ -q --continue-on-collection-errors` → **2,389 passed, 3 skipped,
  0 failures, 0 collection errors** (the 3 skips are local-data-absent cases).
- `ruff check` on this sprint's three files → **clean**.
- `python scripts/check_research_freeze.py` → **PASS**.
- `python scripts/validate_research_archive.py` → **PASS**.
- `python scripts/scan_artifacts_for_secrets.py` → **PASS**.
- `git status --short` → clean (a harness `scheduled_tasks.lock` touch was
  reverted; not sprint work).

Freeze intact; nothing approved; paper/demo/live blocked.

## 7. Note on method choices

- **Corpus limit:** the store has only seven USD-legged majors (no non-USD
  crosses), so the prior sprint's preferred "run on non-USD crosses" confound test
  was replaced by the base-vs-quote pair-space analysis (Phase 3). This
  substantially — not completely — resolves the USD confound.
- **Null seeds:** 60 (vs the prior 200) after timing showed the null-mean
  dispersion is already stable; the USD_JPY integrity re-run confirms the
  conclusions are unchanged.
- **No optimisation:** the factor is the locked prior-sprint C1 definition;
  Phase-4 specs are a-priori perturbations, and the Phase-5 cost cells are
  reported with explicit forking-path / cost-optimism caveats and an outlier check.
