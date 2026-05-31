# M1 Full Corpus Validation And Aggregation 001 Plan

**Branch:** `infra-m1-full-corpus-validation-and-aggregation-001`
**Base:** `main` at `bc8a5b1`
**Scope:** infrastructure validation only. No CAMPAIGN_021, no strategy evidence, no approvals, no paper/demo/live.

## Purpose

Validate the ingested ~5-year OANDA practice M1 corpus for all seven major FX pairs in local Postgres, produce compact quality and aggregation reports, compare M1-derived H4/D1AGG to existing references, and decide whether the lower-timeframe lane is ready for CAMPAIGN_021 **scaffold** (not execution).

## Non-Goals

- No CAMPAIGN_021 evidence or train/validation/test campaigns.
- No strategy tuning, verdicts, or `configs/approved_strategies.yaml` edits.
- No paper/demo/live enablement.
- No OANDA mutation endpoints or live hosts.
- No additional bulk ingestion unless a documented repair is required.
- No raw M1 exports, DB dumps, or credentials in commits.

## Safety Rules

`configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live refusal must hold. Scripts load `.env` via `forex_bot.project_env` without printing secrets. Validation is read-only against local Postgres.

## Expected Corpus

| Pair | Expected M1 rows |
| --- | ---: |
| EUR_USD | 1,843,476 |
| GBP_USD | 1,836,170 |
| USD_JPY | 1,844,454 |
| AUD_USD | 1,822,196 |
| USD_CAD | 1,836,013 |
| USD_CHF | 1,786,535 |
| NZD_USD | 1,824,352 |

Approximate span: 2021-05-26/27 through 2026-05-26. Existing native H4 (~69k rows total) remains reference-only.

## Validation Checks

1. Inventory: row counts, date span, completeness, duplicates, provenance (`fetch_batch_id`, `data_hash`).
2. Quality: spreads, bid/ask/OHLC sanity, weekday missing-minute rate (weekends excluded), gap summaries.
3. Aggregation: M5/M15/H1/H4/D1AGG coverage from M1 without committing aggregate candles.
4. H4 drift: M1-derived H4 vs stored native H4 on overlapping timestamps.
5. D1AGG convention: M1→H4→D1AGG vs H4→D1AGG reference.
6. LTF/HTF alignment: M15 default, M5 subset; no lookahead on completed HTF features.
7. LTF preflight: M15 execution + H1/H4/D1AGG context, `next_bar_open`, time-stop bars.

## Drift Classification

Non-exact H4/D1AGG matches are classified as: timestamp convention, bid/ask aggregation, missing minutes, OANDA native alignment, data-store issue, or unknown. Small spread/volume differences alone do not block the lane.

## Readiness Criteria

- **READY_FOR_C021_SCAFFOLD:** all pairs PASS or acceptable WARN on counts/quality; aggregation viable for M15/M5; H4 drift not materially blocking; alignment/preflight PASS.
- **READY_WITH_WARNINGS:** documented drift or USD_CHF row delta with safe M15 lane.
- **BLOCKED_*:** material data repair, aggregation drift, or alignment failure.

## Blocked / Fail Criteria

- Missing pair or >0.5% row-count FAIL vs expected without explanation.
- Duplicate timestamps, bid>ask failures, or >2% weekday missing minutes.
- Material OHLC/timestamp mismatch rate on H4 overlap (>1%).
- Lookahead violations in alignment samples.

## No-Approval Statement

This sprint does not approve any strategy, does not create CAMPAIGN_021 evidence, and does not change C020 REJECT or prior verdicts.
