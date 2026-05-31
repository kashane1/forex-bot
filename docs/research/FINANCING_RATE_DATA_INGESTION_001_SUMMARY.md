# Financing / Rate-Data Ingestion 001 — Summary

**Branch:** `research-financing-rate-data-ingestion-001`
**Type:** **data ingestion + research preparation only.** Not a campaign, strategy,
factor-validation, factor-discovery, front gate, or train/validation/test.
**Date:** 2026-05-31. **Freeze intact; nothing approved; paper/demo/live blocked.**

Built and validated a historical carry-differential research dataset for the FX
universe and determined whether carry is ready for formal factor validation.

---

## 1. Branch

`research-financing-rate-data-ingestion-001` (from clean `origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `6367f48` | `FINANCING_RATE_DATA_INGESTION_001_PLAN.md` |
| 1 | `3c054a5` | `CURRENCY_RATE_DATA_INVENTORY.md` |
| 2 | `599e900` | `CARRY_DATASET_CONSTRUCTION.md` + carry module + runner + data |
| 3 | `dd318eb` | `CARRY_DATASET_VALIDATION.md` |
| 4 | `6b64c36` | `CARRY_DATASET_PLAUSIBILITY_REVIEW.md` |
| 5 | `e1883c6` | `CARRY_FACTOR_VALIDATION_DESIGN.md` (design only) |
| 6 | `a550e4e` | `CARRY_RESEARCH_READINESS_VERDICT.md` (**READY_WITH_LIMITATIONS**) |
| 7 | `3036ce1` | `NEXT_PROMPT_AFTER_FINANCING_RATE_DATA_INGESTION.md` |
| 8 | _this commit_ | this summary + validation |

## 3. Currency rate sources used

**FRED** (Federal Reserve Bank of St. Louis), **OECD harmonized 3-month interbank
rates** — one family, one series per currency:
`USD IR3TIB01USM156N · EUR IR3TIB01EZM156N · GBP IR3TIB01GBM156N · JPY
IR3TIB01JPM156N · AUD IR3TIB01AUM156N · NZD IR3TIB01NZM156N · CHF IR3TIB01CHM156N ·
CAD IR3TIB01CAM156N`. Public data via HTTPS (throttled), `FRED_API_KEY` read from
`.env` and **never committed**; raw cache gitignored. **No broker / OANDA / trading
API** was called.

## 4. Coverage obtained

Monthly, annualized %. Full coverage of the corpus window (2021-05 → 2026-05) for all
8 currencies (60 monthly points each after construction); deep history to ~1995
(JPY 2002, CHF 1999). Tail publication lag 1–4 months (forward-filled,
lookahead-safe). No mid-window gaps.

## 5. Carry dataset construction summary

Per-currency rate panel → forward-filled monthly rate matrix → **per-instrument
monthly carry differential** `carry(BASE_QUOTE) = r_base − r_quote` for all **15
instruments** (7 majors + 8 crosses), `2,859` rate rows + `5,043` carry rows.
Internally consistent (triangular rate residual **1.78e-15**). Code:
`research/carry/carry_rates.py` + `scripts/build_carry_rate_dataset.py` (ruff-clean,
research-only). Artifacts under `docs/research/carry_rates/`.

## 6. Validation findings

Complete, gap-free (within window), lookahead-safe (only the 1–4-month tail
imputed), and internally consistent — cross carry = sum of USD-leg carries to
machine precision. Funding currencies **CHF (52.5%) / JPY (47.5%)** are the lowest-
yield in 100% of months; high-yield side **NZD (66%) / USD (15%) / GBP (12%) / AUD
(7%)**. Sign-stable positive carry on the classic crosses (NZD/USD/GBP_JPY,
USD/GBP/EUR_CHF, AUD_JPY); sign-stable negative on EUR_USD/EUR_GBP/EUR_AUD;
regime-flipping on AUD/GBP/NZD_USD/USD_CAD/EUR_JPY (the Fed hiking cycle).

## 7. Plausibility-review findings

**Macro-faithful.** Reproduces 2021 ZIRP/negative rates (EUR −0.54, CHF −0.74, JPY
−0.07), the 2022–23 global hiking peak (USD ~5.3, NZD ~5.7), the 2024–26 easing, the
**BoJ's historic exit from negative rates** (JPY −0.07 → 1.12), the ECB/SNB lag, and
the signature **2022–24 USD_JPY carry trade** (USD_JPY carry 0.16 → 5.35 → 2.50). No
macro-inconsistent anomalies.

## 8. Readiness verdict

# `READY_WITH_LIMITATIONS`

The data asset is **research-grade and sufficient for a GROSS, existence-level carry
factor-validation** — but **NOT** for a tradability/front-gate conclusion (gated on a
separate **real-OANDA-financing** ingest — interbank ≠ broker financing, the C031
≈4× reality), and the **monthly cadence + ~5y spot window** limit statistical power.
Carry is ready to be studied for **existence**, not for tradability.

## 9. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 10. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`; fails closed.

## 11. Do paper/demo/live remain blocked?

**Yes.** Freeze gate confirms paper/demo loops refuse — frozen.

## 12. Recommended next sprint

`research-carry-factor-validation-001` — a pre-registered **gross, existence-level**
carry factor-validation (Stage 1–2) on the committed dataset; monthly holding
horizons, matched nulls, **explicitly gross-only / un-tradable**, no campaign. It is
decision-forcing: if carry fails gross, the last in-repo mechanism closes (avoiding
the financing-ingest effort); if it clears gross, the next sprint ingests real OANDA
financing (user-authorized) for the net-of-cost gate. Full prompt in
`NEXT_PROMPT_AFTER_FINANCING_RATE_DATA_INGESTION.md`.

## 13. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2443 passed** — exit 0 |
| `ruff check src scripts tests` | 4 errors — **all pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (CAMPAIGN_031). New carry module + runner are **ruff-clean**. |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 (no FRED key in any committed artifact) |
| `git status --short` | clean after this commit (FRED cache gitignored) |

## 14. Files to review first

1. `CARRY_RESEARCH_READINESS_VERDICT.md` — the READY_WITH_LIMITATIONS scope.
2. `CARRY_DATASET_PLAUSIBILITY_REVIEW.md` — the macro-faithfulness evidence.
3. `CARRY_DATASET_VALIDATION.md` — coverage/consistency/diagnostics.
4. `CARRY_DATASET_CONSTRUCTION.md` + `CURRENCY_RATE_DATA_INVENTORY.md` — sources + build.
5. `CARRY_FACTOR_VALIDATION_DESIGN.md` + `NEXT_PROMPT_AFTER_FINANCING_RATE_DATA_INGESTION.md` — the future study.

---

## Bottom line

A **credible, validated, macro-faithful carry-differential dataset** now exists for
the full 15-instrument FX universe — internally consistent to machine precision,
lookahead-safe, and reproducing every major 2021–26 central-bank cycle including the
BoJ exit and the USD_JPY carry trade. It is **`READY_WITH_LIMITATIONS`**: sufficient
for a **gross, existence-level** carry factor-validation, **not** for a tradability
verdict (which needs a separate real-financing ingest), with a monthly/~5y power
caveat. **Carry is built and validated as a DATA asset and is explicitly NOT
presented as an edge.** No factor study was run, no strategy or campaign created;
freeze intact; paper/demo/live blocked.
