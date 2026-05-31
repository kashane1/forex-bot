# C1 Cross-Replication Screen 001 — Summary

**Branch:** `research-c1-cross-replication-screen-001`
**Type:** factor **replication screen only** — not a strategy, campaign, trading
front-gate, or train/validation/test exercise.
**Date:** 2026-05-30. **Freeze intact; nothing approved; paper/demo/live blocked.**

This sprint ran a **fresh, pre-registered, frozen-threshold replication** of the
locked C1 factor on the 8 populated non-USD crosses to answer one question: does
C1 replicate outside the USD-major universe? **It does not.**

---

## 1. Branch

`research-c1-cross-replication-screen-001` (from clean `origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `b44e774` | `C1_CROSS_REPLICATION_001_PLAN.md` (baseline audit + frozen C1 spec) |
| 1 | `ae699d5` | `C1_CROSS_REPLICATION_PROTOCOL.md` (pre-registration, frozen) |
| 2 | `ff0690f` | `C1_CROSS_REPLICATION_RESULT.md` + 16 cross CSVs + cross meta/robustness |
| 3 | `33d6d76` | `C1_CROSS_REPLICATION_NULL_COMPARISON.md` |
| 4 | `95992ec` | `C1_CROSS_REPLICATION_ROBUSTNESS.md` |
| 5 | `9fb05ba` | `C1_CROSS_REPLICATION_VERDICT.md` (**REPLICATION_FAILED**) |
| 6 | `5151181` | `C1_CROSS_REPLICATION_IMPLICATIONS.md` |
| 7 | `0ba23fd` | `NEXT_PROMPT_AFTER_C1_CROSS_REPLICATION.md` (S2) |
| 8 | _this commit_ | this summary + validation |

## 3. Files changed

Nine new docs under `docs/research/` + 18 result artifacts under
`docs/research/c1_validation/` (16 per-cross `*_c1_events.csv` / `*_c1_nulls.csv`,
`c1_cross_validation_meta.json`, `c1_cross_robustness.csv`). The majors' shared
`c1_robustness.csv` / `c1_validation_meta.json` were **preserved** (cross outputs
renamed to `c1_cross_*` to avoid clobbering provenance). **Zero code changed** —
`git diff --name-only origin/main...HEAD -- '*.py'` is empty; the existing C1
runner was reused with only its pair-list widened on the command line.

## 4. Crosses analyzed

All 8 first-wave crosses, window 2021-05-26 → 2026-05-26:
- **Required (4):** EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY
- **Optional (4):** NZD_JPY, EUR_CHF, GBP_CHF, EUR_AUD

Frozen `BASELINE` C1 spec (EMA 20/50, slope-3, H4-trend + H1-trend + M15-aligned,
rising-edge + 60-min cooldown, signed forward return), 60 null seeds — **identical
to the majors run; only the instrument list differed.** Definition not altered
after results were observed.

## 5. Replication findings

C1_long, 60-min signed reversion (the majors' signature: **negative 7/7**,
strengthening to 60 min, mZ60 −4.21/−3.55 on EUR_USD/USD_JPY):

| Cross | req | mean60 (p) | mZ60 | note |
|-------|-----|-----------|------|------|
| EUR_GBP | Y | −0.059 | −0.31 | ≈0, within null |
| EUR_JPY | Y | **+0.162** | −0.14 | sign-flip; cleared null at 30m (−2.26) then **reversed** |
| GBP_JPY | Y | −0.071 | −0.64 | ≈0, within null |
| AUD_JPY | Y | **+0.045** | −0.27 | sign-flip; within null |
| NZD_JPY | o | −0.034 | −0.56 | within null |
| EUR_CHF | o | −0.089 | −0.17 | within null |
| GBP_CHF | o | −0.774 | **−2.79** | only null-clearing pair (single optional → noise) |
| EUR_AUD | o | −0.328 | −0.76 | within null |

- **Required-set sign: 2/4 negative** (vs 7/7 on majors); magnitudes **~10×
  smaller** (|mean60| ≤ 0.16 vs ~1.1).
- A weak 30-min tilt on the JPY-quote crosses (EUR_JPY/GBP_JPY/AUD_JPY negative at
  30 m) **does not persist** to 60 m — the reverse of the majors' strengthening.

## 6. Null-comparison findings

- Cells clearing **|matched-Z| ≥ 2**: **2/8 at 30 min** (EUR_JPY, GBP_CHF), **1/8
  at 60 min** (GBP_CHF only).
- **Zero required crosses** clear the null at 60 min. The one required 30-min hit
  (EUR_JPY) reverses by 60 min.
- Observed C1 means sit **inside one matched-null SD** on every required pair at 60
  min — C1 events earn what a session-matched **random** event earns.
- 1 isolated |Z|≈2 hit over 16 cells = the **multiple-comparison noise
  expectation**. Replication is **not statistically meaningful**.

## 7. Robustness findings

No required cross is stable on any axis (factor definition unchanged):
- **Year:** signs flip year to year on every required pair.
- **Session:** signs flip; negatives cluster in **thin off-hours** (wide spread).
- **Volatility:** no majors-like gradient; EUR_JPY's largest 60-min reading is
  **+1.20 in LOW vol** (wrong sign).
- **Spec (one-knob):** required signs flip under single perturbations (EUR_JPY →
  −0.24; GBP_JPY → +0.39). Only GBP_CHF holds across specs — but it is
  period-concentrated (2022–23), off-hours/wide-spread, single-pair → a
  regime/microstructure artifact, not the C1 mechanism.

## 8. Replication verdict

# `REPLICATION_FAILED`

All three frozen failure triggers fire: **inconsistent sign**, **indistinguishable
from null**, and **single-pair/inconsistent behavior**. Success criteria
(majority-negative 60-min sign + multi-pair null-clearing + majors-band magnitude)
are not met; the evidence is not *mixed* (which would be PARTIAL) but
*consistently negative* for replication. Maps to the planning sprint's
pre-stated **`C1_ARTIFACT`** branch: C1's significant magnitude was specific to the
USD-major discovery pairs / USD-regime structure and **does not generalize**.
*Tradability was out of scope and not evaluated.*

## 9. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 10. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`;
`forex_bot.approval` fails closed.

## 11. Do paper/demo/live remain blocked?

**Yes.** Freeze gate confirms `paper-loop refuses ['trend_following'] — frozen`
and `demo-loop refuses ['trend_following'] — frozen`.

## 12. Recommended next step

**Retire C1 as a research target** (keep as a control/null reference; both its
tradability and generality questions are now closed-negative). Make **S2 — the
cross-implied currency-strength index** the next discovery direction: branch
`research-currency-strength-factor-validation-001`, a pre-registered Stage-1/2
factor-validation study (verdict-producing, **no campaign, no approval**). Full
prompt in `NEXT_PROMPT_AFTER_C1_CROSS_REPLICATION.md`. Carry remains
prerequisite-blocked on a separate financing-data ingest sprint.

## 13. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2443 passed** — exit 0 |
| `ruff check src scripts tests` | **4 errors — ALL pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (CAMPAIGN_031, on `origin/main`). Zero Python changed this sprint (`git diff … -- '*.py'` empty) → not a regression. |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 (registry empty; loops refuse) |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 (pattern scan; value scan skipped, no creds in env) |
| `git status --short` | clean after this commit |

## 14. Files to review first

1. `C1_CROSS_REPLICATION_VERDICT.md` — the verdict and how the frozen map resolved.
2. `C1_CROSS_REPLICATION_RESULT.md` — the per-cross replication table.
3. `C1_CROSS_REPLICATION_NULL_COMPARISON.md` — the null separation.
4. `C1_CROSS_REPLICATION_ROBUSTNESS.md` — year/session/vol/spec instability.
5. `C1_CROSS_REPLICATION_IMPLICATIONS.md` + `NEXT_PROMPT_AFTER_C1_CROSS_REPLICATION.md` — retire C1, go to S2.

---

## Data-access note (transparency)

The Phase-2 analysis read the populated cross bars from the **local research
database** (URL+password in `.env`). Pre-registration (Phases 0–1) was completed
and committed **before any data was read**. The auto-mode boundary initially
blocked the DB read under the "do not use credentials" rule; the user was asked
and **explicitly authorized the local research-DB read** (read-only data
analysis — **no OANDA/trading APIs, no broker credentials, no orders**), matching
the original C1 majors run's stated scope ("no credentials beyond the local
research DB URL"). No trading credential was used at any point.

## Bottom line

C1 — the programme's one genuine factor — **does not replicate on non-USD
crosses**: sign-inconsistent, null-indistinguishable on the required set, and
unstable across years/sessions/vol/spec. Its significant magnitude was a
**USD-regime artifact**. The cross data delivered exactly the independent
replication it was justified on and returned a clean, decision-relevant negative.
**Retire C1; pursue S2 (currency-strength index) next.** No factor was re-tuned,
no strategy built, no campaign created; freeze intact; paper/demo/live blocked.
