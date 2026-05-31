# Currency-Strength Factor-Validation 001 — Summary

**Branch:** `research-currency-strength-factor-validation-001`
**Type:** **factor-validation study only** (multi-market front-gate Stage 1–2).
Not a strategy, campaign, front-gate screen, or train/validation/test exercise.
**Date:** 2026-05-30. **Freeze intact; nothing approved; paper/demo/live blocked.**

This sprint ran a **pre-registered, frozen** existence/robustness study of S2 —
the cross-implied currency-strength factor — on the 15-instrument universe.
Verdict: **`FACTOR_REJECTED`**.

---

## 1. Branch

`research-currency-strength-factor-validation-001` (from clean `origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `cf745dd` | `CURRENCY_STRENGTH_FACTOR_VALIDATION_001_PLAN.md` |
| 1 | `9446957` | `CURRENCY_STRENGTH_FACTOR_PROTOCOL.md` (frozen pre-registration) |
| 2 | `2b7b9d0` | `CURRENCY_STRENGTH_INDEX_DESIGN.md` + module + runner + construction/collinearity |
| 3 | `aef2efc` | `CURRENCY_STRENGTH_RESPONSE_STUDY.md` + response/events CSVs |
| 4 | `a9bc75e` | `CURRENCY_STRENGTH_CROSS_SECTIONAL_VALIDATION.md` + cross_sectional CSV |
| 5 | `3801f0e` | `CURRENCY_STRENGTH_NULL_COMPARISON.md` + nulls CSV |
| 6 | `2e51d2a` | `CURRENCY_STRENGTH_ROBUSTNESS.md` + robustness CSV |
| 7 | `bfbdabc` | `CURRENCY_STRENGTH_FACTOR_VERDICT.md` (**FACTOR_REJECTED**) |
| 8 | _this commit_ | next prompt + this summary + validation |

## 3. Files changed

9 new docs under `docs/research/`; 1 new research module
(`research/edge_discovery/currency_strength.py`) + 1 runner
(`scripts/run_currency_strength_factor.py`) — both **ruff-clean**, import-isolated,
research-only (no trades/signals/PnL); 7 result artifacts under
`docs/research/currency_strength/`. No change to `src/`, configs, registry, or any
executor/loop.

## 4. Strength-index definition

Synthetic per-currency cumulative log-index (average-of-pairs):
`CC_c(t) = mean over instruments containing c of [sign_ci · ln(mid_close_i(t))]`,
`sign_ci = +1` (base) / `−1` (quote); `strength_c(t) = CC_c(t) − CC_c(t−48)`
(4h look-back on M5). Derived: rank (1=strongest..8=weakest), 1h Δstrength,
cross-sectional dispersion (mean 0.00177) and spread (mean 0.00526). 15
instruments, 8 currencies, **304,014 common M5 bars, 25,330 events**, 2021-05-27
→ 2026-05-26.

## 5. Response-study findings

Conditioning on strongest/weakest/rapidly-strengthening/rapidly-weakening
currency → forward currency returns **≈ 0** at every horizon: means **−0.13 to
+0.13 bp** vs path MFE/MAE of **±2 bp (15m) … ±14 bp (240m)** (≈1–2% S/N); hit
rates **0.49–0.51**; MFE ≈ −MAE (symmetric). Rank persistence is high at short
horizons (strongest stays strongest 84% at 5m) but the forward **return** is ~0 —
strength **persists** but does not **predict**.

## 6. Cross-sectional findings

No coherent sub-population. Across **currencies** (4+/4−), **years** (2+/3−), and
**sessions** (2+/3−), signs split ~50/50 with magnitudes ≤ 0.6 bp. Because each
currency's forward return is the pair-average, the absent currency-level effect
forbids any pair-level coherence. No currency/year/session rescues the factor.

## 7. Null-comparison findings

Four nulls (randomized ranks, shuffled currencies, **session-matched** timestamps,
unconditional), 200 seeds: **0 of 80 cells clear |z| ≥ 2**; **global max |z| =
1.65**. All four nulls coincide — no part of the strength→return link, when broken,
changes the result. Statistically indistinguishable from random.

## 8. Robustness findings

Robustly **null** across all three frozen axes: lookbacks **24/48/96** (max |mZ|
1.48, signs flip), ranking **top-1 vs top-2** (means ±0.05 bp), aggregation
**vol-normalized** (max |z| 1.57; correlates 0.92–0.95 per currency with the
primary — the two aggregations agree and both are null). The non-existence is not
an artifact of the primary spec.

**Breadth diagnostic (notable):** PC1 explains only **47%** and is a
**haven-vs-risk axis** (USD/JPY vs AUD/NZD/CAD), **not** a USD axis; PC2/PC3 add
independent variance. The strength vector is **genuinely multi-currency** — the
feared "USD-artifact" failure mode did **not** occur (H2 breadth passed). The
factor fails on **predictability**, not on degenerate breadth.

## 9. Final verdict

# `FACTOR_REJECTED`

Cross-implied currency strength is a real, breadth-diverse **descriptor** with
**no forward-predictive information** — within null on 0/80 cells, sign-incoherent
across every slice, robustly null across every neighbour. **Tradability was not
evaluated (out of scope).**

## 10. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 11. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`; fails closed.

## 12. Do paper/demo/live remain blocked?

**Yes.** Freeze gate confirms paper/demo loops refuse — frozen.

## 13. Recommended next step

**Do NOT run S3** (currency cross-sectional momentum) — it is **pre-falsified**:
S3 trades exactly the strength ranking this sprint showed carries no forward
information. **S5** (regime gate) is moot (no surviving generator to gate).
Recommended next sprint: **S4 — cross relative-value / cointegration
factor-validation** (`research-cross-relative-value-factor-validation-001`), the
one remaining shortlist family testing a **different mechanism** (stationary-spread
reversion, not directional prediction), no new data. **Stop-criterion:** if S4 also
fails, the no-new-data shortlist (S1–S5) is exhausted and the next move is a
**financing-data ingest** to unblock the carry family (a *data* sprint, not a
factor screen) — never more directional mining on this corpus. Full prompt in
`NEXT_PROMPT_AFTER_CURRENCY_STRENGTH_FACTOR_VALIDATION.md`.

## 14. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2443 passed** — exit 0 |
| `ruff check src scripts tests` | 4 errors — **all pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (CAMPAIGN_031). This sprint's new code (`currency_strength.py`, `run_currency_strength_factor.py`) is **ruff-clean**. |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 |
| `git status --short` | clean after this commit |

## 15. Files to review first

1. `CURRENCY_STRENGTH_FACTOR_VERDICT.md` — verdict + the breadth-passed/
   predictability-failed nuance.
2. `CURRENCY_STRENGTH_NULL_COMPARISON.md` — 0/80 cells clear.
3. `CURRENCY_STRENGTH_INDEX_DESIGN.md` — construction + PCA breadth diagnostic.
4. `CURRENCY_STRENGTH_RESPONSE_STUDY.md` — near-zero response.
5. `NEXT_PROMPT_AFTER_CURRENCY_STRENGTH_FACTOR_VALIDATION.md` — S3 pre-falsified;
   S4 next; carry needs a data sprint.

---

## Data-access note (transparency)

The study read populated M5 bars from the **local research database** (URL+password
in `.env`) — the user's standing authorization for **read-only research-DB access**
(no OANDA/trading APIs, no broker credentials, no orders). Pre-registration
(Phases 0–1) was committed **before any data was read**. One descriptive miscount
in the frozen protocol's §1 leg-count annotation (EUR/AUD/NZD) was caught during
construction on synthetic data and logged transparently in
`CURRENCY_STRENGTH_INDEX_DESIGN.md` §4 (it affects no computation — the code
derives counts from the instrument list); the frozen protocol was left unedited.
One deviation was *avoided*: the `matched_timestamps` null was implemented as
genuinely session-matched (protocol §10) and the study re-run before any results
were committed.

## Bottom line

Cross-implied currency strength is a **genuine, breadth-diverse descriptor that
does not forecast** forward currency moves on this corpus — `FACTOR_REJECTED`.
Uniquely, it **cleared the USD-artifact suspicion** (breadth passed); the problem
is intraday currency-level **efficiency**, not collinearity. This pre-falsifies S3,
leaving S4 (cross relative-value reversion) as the next different-mechanism test
and the carry-data ingest as the fallback. No factor was tradability-screened, no
strategy built, no campaign created; freeze intact; paper/demo/live blocked.
