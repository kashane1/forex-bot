# Non-USD Cross Data Population — Sprint 001 Plan

**Branch:** `research-nonusd-cross-data-population-001`
**Date:** 2026-05-29
**Type:** **data population + validation** sprint. Uses the capability built
in `research-nonusd-cross-ingestion-and-cost-models-001` to fetch, validate,
materialize, and cost-profile the first-wave non-USD crosses from **real
OANDA practice data**. No factor discovery, no front-gate screen, no
campaign, no strategy, no approval. Freeze stays intact.

## 0. Why this sprint exists

The infrastructure sprint left all crosses `NOT_INGESTED`. This sprint
populates real data so future research starts from measured reality, not
infrastructure assumptions. Scope ends at "populated, validated,
materialized, cost-profiled" — no edge work.

## 1. Hard rules (non-negotiable)

- No CAMPAIGN_032 / no campaign of any kind.
- No trading logic, no entry/exit logic.
- No train/validation/test evidence.
- **No factor discovery, no edge discovery, no front-gate analysis.**
- No strategy approved; paper/demo/live stay blocked.
- No mutation APIs — practice-only, read-only GET candles via the existing
  ingestion script (live host refused, candle endpoint only).
- Preserve provenance (`fetch_batch_id`, `data_hash`) and validation
  standards; hold crosses to the identical bar conventions as the majors.
- Commit **manifests/docs only** — never commit raw datasets (data lives in
  the local research Postgres).

## 2. Baseline audit (Phase 0 — verified on `origin/main` tip 245bde2)

- Branch created from clean `origin/main` (`245bde2`).
- Cross support present: `domain/cross_instruments.py`,
  `data/cross_ingestion.py`, `research/cost_models/`,
  `scripts/validate_nonusd_cross_data.py`, materialization gate on
  `SUPPORTED_PAIRS`.
- `pytest tests/ -q` → **2440 passed, 3 skipped** (local-data skips).
- `ruff check src scripts tests` → **4 errors, all pre-existing** in
  `scripts/run_edge_discovery_vol_managed_tsmom.py` (C031); no new code yet.
- `check_research_freeze.py` → **ALL CHECKS PASSED**.
- `validate_research_archive.py` → **ALL CHECKS PASSED**.
- `scan_artifacts_for_secrets.py` → **PASSED**.
- `configs/approved_strategies.yaml` → `approved: []`.

## 3. Environment & target horizon (discovered at Phase 0)

- **Credentials now present** (unlike the infra sprint): OANDA
  `practice` token + account id, and a local research database
  (`postgresql://…@localhost:5432/forex_bot`, schema `market_data`,
  non-prod — `research_db` safety check passed). Real ingestion is
  therefore possible.
- **Majors' M1 horizon (the target to match):** `2021-05-26 → 2026-05-26`
  (~5 years), ~1.79M–1.84M M1 rows per major. Native broker H4 reaches back
  to 2020-01-01, but **M1 (and everything materialized from it) starts
  2021-05-26** — so cross M1 ingestion targets `2021-05-26 → 2026-05-27`.
- Crosses currently hold **zero** rows at every granularity.

## 4. Phase plan

- **P0** baseline audit + this plan (commit).
- **P1** ingestion planning: per-cross available history, expected row
  counts, storage, sequencing → `NONUSD_CROSS_INGESTION_PLAN.md` (commit).
- **P2** ingest EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY (required) over the
  matched M1 horizon via `scripts/ingest_oanda_m1_candles.py --crosses
  --execute-readonly-ingestion --allow-large-range`; optional crosses if
  feasible. Compact manifests only (commit manifests/docs, not data).
- **P3** validation via `scripts/validate_nonusd_cross_data.py` →
  `NONUSD_CROSS_DATA_VALIDATION_RESULT.md` (commit).
- **P4** materialize M5/M15/H1/H4M1 for ingested crosses; verify parity →
  `NONUSD_CROSS_MATERIALIZATION_RESULT.md` (commit).
- **P5** descriptive cost baseline (spread stats, session, vs majors) →
  `NONUSD_CROSS_COST_BASELINE.md` (commit). Descriptive only.
- **P6** readiness reassessment on real data →
  `NONUSD_CROSS_DATA_READINESS_REVIEW.md` (commit).
- **P7** next prompt (factor-discovery **planning** only) →
  `NEXT_PROMPT_AFTER_NONUSD_CROSS_DATA_POPULATION.md` (commit).
- **P8** full validation + `..._001_SUMMARY.md` (commit).

## 5. Risk / honesty notes

- Ingestion is large (~1.8M M1 candles × 4 crosses via ~1,825 daily chunks
  each). It runs sequentially through the existing safeguarded script; if a
  cross is only partially populated by the end, the validation/readiness
  docs will report the **actual** coverage honestly rather than assume
  completion. No numbers will be written that are not read back from the
  store on disk.
- Optional crosses (NZD_JPY, EUR_CHF, GBP_CHF, EUR_AUD) are ingested only
  if the four required complete with margin; otherwise they are left
  `NOT_INGESTED` and documented as such.
