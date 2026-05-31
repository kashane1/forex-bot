# Financing / Rate-Data Ingestion 001 — Plan & Baseline Audit

**Branch:** `research-financing-rate-data-ingestion-001`
**Type:** **data ingestion + research preparation only.** Not a campaign, strategy,
factor-validation, factor-discovery, front gate, or train/validation/test exercise.
**Date:** 2026-05-30.
**Freeze status:** intact. `approved: []`; paper/demo/live blocked; no broker /
OANDA order APIs called.

> **Goal:** build a **validated historical interest-rate / carry-differential
> dataset** for the FX research universe (8 currencies, 15 instruments), and
> determine whether that data asset is **sufficient to justify a future carry-factor
> validation study** — without running any factor study and without presenting carry
> as an edge.

---

## PHASE 0 — Baseline audit

### 0.1 Source decisions reviewed

- **Cross-Factor Programme Synthesis** → chose **Option A**: financing/rate-data
  ingestion enabling carry, because carry is the one genuinely-new, untested
  mechanism and is nearly testable in-repo.
- **Remaining Untested Mechanisms** §1–§2 → carry (interest-rate differential) is a
  *different return source* from every spread-capture/reversion family tested; it was
  **data-blocked all programme**; the cross expansion supplied real carry *pairs*
  (AUD_JPY, NZD_JPY, EUR_JPY) but real *rates* are still un-ingested.
- **Next Major Direction Decision** → the immediate sprint is **data + design only**;
  the FRED interbank differential is the **economic signal**; OANDA real financing
  (broker markup; the C031 ≈4× reality) is a **separate later authorized cost-gate**
  step, not this sprint.

### 0.2 Existing infrastructure reviewed

- **FRED tooling:** `scripts/fetch_cross_asset_fred_features.py` +
  `research/cross_asset_features/fred.py` (`fetch_fred_observations`) +
  `CROSS_ASSET_FRED_INGEST_RUNBOOK.md`. The existing registry is **US-centric**
  (DTWEXBGS, DGS2/10, VIX, SP500, oil) — it has **no per-currency policy rates**, so
  this sprint adds a **dedicated harmonized 8-currency rate set** (reusing the FRED
  HTTP/cache/provenance machinery, not the US feature list).
- **Financing infrastructure:** `src/forex_bot/research/cost_models/carry.py` (a
  two-legged carry **estimate** model using the registry's qualitative
  `conservative_bp_per_day`) — this sprint produces the **real rate differential**
  that a future study uses in place of those estimates. `forex_bot.financing`
  (majors, single-leg) is unchanged.
- **Cross-universe support:** the 8 crosses are populated/materialized; the carry
  pairs exist as spot data. This sprint adds the **rate leg**.

### 0.3 Gate verification (this sprint, Phase 0)

- `configs/approved_strategies.yaml` → **`approved: []`** (confirmed empty).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**.

### 0.4 Connectivity pre-check (done before planning the build)

A throttled probe confirmed **FRED is reachable, `FRED_API_KEY` is present
(gitignored), and all 8 harmonized OECD 3-month interbank series return data** over
2021–2026 with regime-sensible values (e.g. JPY ≈1.3%, CHF ≈−0.04%, AUD ≈4.3%, USD
≈3.8%). The dataset is buildable from public data with no broker/trading API.

---

## Objectives

1. Ingest **harmonized per-currency short-term interest rates** (FRED, public,
   credential-free of any trading API) for USD, EUR, GBP, JPY, AUD, NZD, CHF, CAD.
2. Construct a **reproducible, provenance-tracked, lookahead-safe** historical
   **carry-differential** dataset for all 15 instruments (7 majors + 8 crosses):
   `carry(BASE_QUOTE) = r_base − r_quote`.
3. **Validate** coverage, gaps, consistency, and cross-construction logic; produce
   diagnostics (distribution, positive/negative-carry frequency, currency-ranking
   frequency).
4. **Plausibility-review** against known rate regimes and central-bank cycles.
5. **Design** (do not run) a future carry-factor validation protocol.
6. Issue a **readiness verdict** (NOT_READY / READY_WITH_LIMITATIONS /
   READY_FOR_FACTOR_VALIDATION).

## Non-goals (explicit)

- **No factor study, no carry response measurement, no nulls, no verdict on whether
  carry predicts/pays.** Design only.
- **No signal, no entry/exit, no trading logic, no campaign, no approval.**
- **No OANDA real-financing ingest** (separate, later, user-authorized cost-gate
  step) and **no broker/order API calls**.
- **Carry is NOT presented as an edge** anywhere — it is an un-validated data asset.

## Assumptions

- The harmonized **OECD 3-month interbank rate** (FRED `IR3TIB01<CC>M156N`) is an
  acceptable cross-country **interbank carry proxy** (the academic standard return
  driver), distinct from OANDA's tradable broker financing.
- **Monthly** frequency is adequate for carry (a slow signal); it is forward-filled
  to any finer grid **lookahead-safely** (a month's value applied only from its
  observation date forward, with a documented publication-lag caveat).
- Interbank rates capture the **economic** carry signal; the **tradable** carry cost
  (broker markup, the binding wall) is a *separate later* ingest — so this dataset
  alone cannot establish tradability and will not be used to claim it.

## Success criteria

- A committed, reproducible rate-series + carry-differential dataset covering the
  corpus window for **all 8 currencies / 15 instruments**, with provenance
  (series ids, fetch date, attribution; **no API key committed**).
- Validation confirms coverage/gaps are within documented tolerances and the cross
  construction is internally consistent (triangular rate consistency holds).
- Plausibility review confirms known regimes/cycles appear.
- A clear, evidence-based **readiness verdict** and a frozen-draft future-study
  design — with carry never presented as an edge.

## Deliverables (one doc per phase)

| Phase | Document |
|---|---|
| 0 | `FINANCING_RATE_DATA_INGESTION_001_PLAN.md` (this) |
| 1 | `CURRENCY_RATE_DATA_INVENTORY.md` |
| 2 | `CARRY_DATASET_CONSTRUCTION.md` (+ research-only code + data) |
| 3 | `CARRY_DATASET_VALIDATION.md` |
| 4 | `CARRY_DATASET_PLAUSIBILITY_REVIEW.md` |
| 5 | `CARRY_FACTOR_VALIDATION_DESIGN.md` |
| 6 | `CARRY_RESEARCH_READINESS_VERDICT.md` |
| 7 | `NEXT_PROMPT_AFTER_FINANCING_RATE_DATA_INGESTION.md` |
| 8 | `FINANCING_RATE_DATA_INGESTION_001_SUMMARY.md` (+ validation) |
