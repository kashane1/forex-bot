# Cross Relative-Value Factor-Validation 001 — Summary

**Branch:** `research-cross-relative-value-factor-validation-001`
**Type:** **factor-validation study only** (multi-market front-gate Stage 1–2).
Not a strategy, campaign, front-gate screen, or train/validation/test exercise.
**Date:** 2026-05-30. **Freeze intact; nothing approved; paper/demo/live blocked.**

This sprint ran a **pre-registered, frozen** existence/robustness study of S4 —
cross relative-value (triangular no-arbitrage consistency) — on the 15-instrument
universe. Verdict: **`FACTOR_REAL_BUT_WEAK`** — the programme's **first
non-rejected factor**.

---

## 1. Branch

`research-cross-relative-value-factor-validation-001` (from clean `origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `d94e241` | `CROSS_RELATIVE_VALUE_FACTOR_VALIDATION_001_PLAN.md` |
| 1 | `6e8486b` | `CROSS_RELATIVE_VALUE_PROTOCOL.md` (frozen pre-registration) |
| 2 | `59dcbe7` | `CROSS_RELATIVE_VALUE_DESIGN.md` + module + runner + construction meta |
| 3 | `bf1fc21` | `CROSS_RELATIVE_VALUE_RESPONSE_STUDY.md` + response CSVs |
| 4 | `96e06b7` | `CROSS_RELATIVE_VALUE_CROSS_SECTIONAL_VALIDATION.md` + events_long |
| 5 | `ece4958` | `CROSS_RELATIVE_VALUE_NULL_COMPARISON.md` + nulls CSV |
| 6 | `49bae5d` | `CROSS_RELATIVE_VALUE_ROBUSTNESS.md` + robustness/shared-leg CSVs |
| 7 | `5e77b37` | `CROSS_RELATIVE_VALUE_FACTOR_VERDICT.md` (**FACTOR_REAL_BUT_WEAK**) |
| 8 | _this commit_ | next prompt + this summary + validation |

## 3. Files changed

9 new docs under `docs/research/`; 1 new research module
(`research/edge_discovery/cross_relative_value.py`, reusing the C028
`rolling_z`/`ar1_half_life`) + 1 runner (`scripts/run_cross_relative_value_factor.py`)
— both **ruff-clean**, import-isolated, research-only (no trades/signals/PnL); 7
result artifacts under `docs/research/cross_relative_value/`. No change to `src/`,
configs, registry, or any executor/loop.

## 4. Relationship definitions tested

**Primary — 8 triangular no-arbitrage residuals** (one per cross):
`resid_c = ln(observed cross) − implied(two USD legs)` (e.g. EUR_JPY = ln(EUR_JPY) −
[ln(EUR_USD)+ln(USD_JPY)]). All 8 pre-named, zero spread search. **Secondary
(robustness) — shared-leg cointegration spreads** (EUR_JPY~GBP_JPY, etc.). Common
M5 grid, 304,014 bars, 25,331 events, 2021-2026.

## 5. Response-study findings

Stretched residuals (|z|≥2) **revert hard**: pooled P(reverts) **0.94–0.96**, ~**77–
93% of the deviation closed**, signed reversion 0.39→0.50 bp across 5→240 min, all 8
relationships positive. **But:** ~**78% of the reversion is realized in the first 5
min** (front-loaded); residual std (0.23–0.81 bp) and reversion (~0.5 bp) are
**~10× inside** the no-arb spread band (4.25–7.18 bp). Half-life splits: **JPY
crosses 4.8–9.6 bars (genuine slow reversion); non-JPY ≤1 bar (stale-quote
signature)**.

## 6. Cross-sectional findings

**Highly consistent** — same sign and comparable magnitude across **all 8
relationships, all 6 years (0.40–0.48 bp), all 5 sessions (0.39–0.56 bp)**. A
stable, broad, instrument-universal structure (mildly larger in the thin late
session — a microstructure tell). The opposite of S2/C1's sign-incoherence.

## 7. Null-comparison findings

**20 of 20 cells clear |z|≥2.** Three nulls give enormous Z (matched 103–134,
shuffled 120–155, unconditional 370–445). The **conservative randomized-
relationships null** (true triangle vs a *wrong* triangle) clears at every horizon
(9.48/6.34/3.87/2.57/3.90) → reversion is a genuine **no-arbitrage** property, not a
generic effect. Its z is **largest at 5 min, decaying with horizon** → much of the
true-triangle excess is fast (microstructure). Decisively **not within null.**

## 8. Robustness findings

Existence **robust** across normalization (lookback 96, robust median-MAD z) and
thresholds (1.5/2.5). The **2-h-lookback variant collapses at 60 min** (z −0.60) —
localizing much of the effect at short horizons. **Shared-leg cointegration spreads
do NOT revert** (half-life 7,000–27,000 bars — random-walk; two diverge at 240 min):
the genuine reversion is **specific to the no-arb triangle**, and the C028
cointegration-spread idea stays null (half-life ≫ hold).

## 9. Final verdict

# `FACTOR_REAL_BUT_WEAK`

The reversion is **genuinely real** (20/20 null cells, beats the wrong-triangle
null, broad and stable, real multi-bar half-lives on the JPY complex) — so **not
REJECTED** — but **confined to the no-arb/microstructure band** (~10× sub-spread,
front-loaded, 4/8 half-life ≤1 bar), so it **fails the §11 artifact test** and is
**not a FRONT_GATE_CANDIDATE**. The programme's **first real factor**, too weak
(within-band) to merit a front-gate screen. **Tradability not evaluated (out of
scope).**

## 10. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 11. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`; fails closed.

## 12. Do paper/demo/live remain blocked?

**Yes.** Freeze gate confirms paper/demo loops refuse — frozen.

## 13. Recommended next step

The **no-new-data shortlist (S1–S5) is now exhausted** (S1 failed, S2 rejected, S3
pre-falsified, S4 real-but-weak, S5 moot). **Do NOT front-gate S4** (sub-cost-band;
would re-hit C028's cost wall). Recommended next sprint: a **project-level direction
synthesis** (`research-cross-factor-programme-synthesis-001`, docs-only) weighing
the remaining levers — **(a) financing-data ingest for carry** (the one untested
mechanism; a *data* sprint, leading concrete option), **(b) lower-cost venue /
tick-L2** (to revisit the now-proven-real RV structure at institutional costs), or
**(c) conclude the no-new-data search**. No campaign in any branch. Full prompt in
`NEXT_PROMPT_AFTER_CROSS_RELATIVE_VALUE_FACTOR_VALIDATION.md`.

## 14. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2443 passed** — exit 0 |
| `ruff check src scripts tests` | 4 errors — **all pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (CAMPAIGN_031). New module + runner are **ruff-clean**. |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 |
| `git status --short` | clean after this commit |

## 15. Files to review first

1. `CROSS_RELATIVE_VALUE_FACTOR_VERDICT.md` — verdict + the real-but-within-band logic.
2. `CROSS_RELATIVE_VALUE_NULL_COMPARISON.md` — 20/20 cells clear; the conservative null.
3. `CROSS_RELATIVE_VALUE_DESIGN.md` — construction + the scale/half-life facts.
4. `CROSS_RELATIVE_VALUE_RESPONSE_STUDY.md` — the reversion + front-loaded profile.
5. `NEXT_PROMPT_AFTER_CROSS_RELATIVE_VALUE_FACTOR_VALIDATION.md` — shortlist exhausted; synthesis next.

---

## Data-access note (transparency)

The study read populated M5 bars + spreads from the **local research database**
(URL+password in `.env`) — the user's standing **read-only research-DB**
authorization (no OANDA/trading APIs, no broker credentials, no orders).
Pre-registration (Phases 0–1) was committed **before any data was read**. The
detector machinery was validated on synthetic positive/negative controls (an AR(1)
reverting residual → z 3–8.5 with progressive horizon profile; a random-walk
residual → z within ±1.7) before the real run.

## Bottom line

Cross triangular no-arbitrage relative-value structure is **real** — its deviations
revert overwhelmingly beyond all nulls, broadly and stably — making it the
programme's **first genuine factor**. But the reversion lives **~10× inside the
no-arb cost band** (front-loaded, half the relationships ≤1-bar staleness), so it is
**FACTOR_REAL_BUT_WEAK**, not a front-gate candidate. The S1–S5 shortlist is
exhausted; the honest next move is a project-level synthesis weighing carry-data
ingest vs a lower-cost venue vs concluding the search. No factor was tradability-
screened, no strategy built, no campaign created; freeze intact; paper/demo/live
blocked.
