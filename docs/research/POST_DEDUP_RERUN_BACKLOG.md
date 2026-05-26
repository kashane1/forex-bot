# Post-Dedupe Rerun Backlog

**Sprint:** CAMPAIGN_CONTAMINATION_AUDIT_001 (updated POST_DEDUP_NULL_REFERENCE_REFRESH_001)  
**Date:** 2026-05-26  
**Branch:** `research-broad-strategy-pause-and-roadmap-001`

> CAMPAIGN_011 deduped null baseline **promoted**. CAMPAIGN_015–017 **dedup-safe REJECT**
> certified. Post-dedup meta-analysis: **NO_RELIABLE_ARCHETYPE** — broad strategy search
> **paused** ([`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md)).
> CAMPAIGN_012–014 null-reference **refreshed**; optional deduped reruns remain backlog only.

## Priority 1 — Must rerun (blocks integrity-safe decisions)

| rank | campaign | why | status |
|---:|---|---|---|
| 1 | **CAMPAIGN_011** null baseline | Canonical null-model anchor | **DONE** — see `research/null_baselines/campaign_011_deduped_null_baseline.json` |

## Priority 2 — Should rerun (null baseline validity / comparison hygiene)

| rank | campaign | why | notes |
|---:|---|---|---|
| 2 | **CAMPAIGN_012** | Walk-forward on pre-fix SQLite; null ref refreshed | REJECT holds vs deduped null; deduped rerun for certified metrics |
| 3 | **CAMPAIGN_013** | Same | Catastrophic REJECT; direction unlikely to flip |
| 4 | **CAMPAIGN_014** | Same | REJECT; event diagnostics may shift trade counts on deduped candles |
| 5 | **CAMPAIGN_010** | Walk-forward on pre-fix SQLite | Strong REJECT; magnitude unverified |

## Priority 2a — Null-reference refresh (docs only — complete)

| campaign | status | doc |
|---|---|---|
| CAMPAIGN_012 | **DONE** — null gap vs deduped null; REJECT unchanged | [`CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_012_POST_DEDUP_NULL_REFERENCE.md) |
| CAMPAIGN_013 | **DONE** | [`CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_013_POST_DEDUP_NULL_REFERENCE.md) |
| CAMPAIGN_014 | **DONE** | [`CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md`](CAMPAIGN_014_POST_DEDUP_NULL_REFERENCE.md) |

## Priority 3 — Archive-only (already rejected; low decision impact)

| campaign | why defer |
|---|---|
| CAMPAIGN_002–004 | REJECT on real OANDA; no promotion path; metrics may shift but verdict stable |
| CAMPAIGN_005 | Diagnostic benchmarks only |
| CAMPAIGN_007–009 | REJECT / narrow validation splits; marathon-era closed |
| CAMPAIGN_008–009 validation-positive rows | Interesting but pre-commit REJECT; rerun only if revisiting mean-reversion family |

## Priority 4 — No rerun needed

| item | status |
|---|---|
| CAMPAIGN_001 | **DEDUP-SAFE** — synthetic harness |
| CAMPAIGN_006 | **BLOCKED_NO_RUN** — D1 infrastructure blocker |
| CAMPAIGN_015 deduped | **DEDUP-SAFE** — canonical evidence post dedupe sprint |
| CAMPAIGN_016 deduped | **DEDUP-SAFE** — REJECT WITHIN_NULL; no rerun during pause |
| CAMPAIGN_017 deduped | **DEDUP-SAFE** — REJECT WITHIN_NULL; no rerun during pause |
| CAMPAIGN_015 contaminated bespoke | **SUPERSEDED BY DEDUP AUDIT** — retain for history only |
| CAMPAIGN_018 | **NOT CREATED** — broad search paused |
| Backtrader parity lane | **CSV_EXPORT_SAFE** / **BACKTRADER_ONLY_DIAGNOSTIC** — deduped CSV exports; not strategy evidence |
| CAMPAIGN_002 free-local parity verifier | Uses deduped export path; verifier artifacts safe for plumbing checks |

## CAMPAIGN_002 specific note

CAMPAIGN_002 **does not need an urgent rerun** for promotion decisions (already REJECT). A **should-rerun** pass is optional if exact H4/H1 metrics must be re-certified post-dedupe. Backtrader / Lean CSV parity artifacts remain **CSV_EXPORT_SAFE**.

## Recommended execution order

1. ~~Formal CAMPAIGN_011 deduped promotion sprint~~ — **complete**.
2. ~~Re-evaluate null comparisons for CAMPAIGN_012–014 against deduped null band~~ — **complete** (POST_DEDUP_NULL_REFERENCE_REFRESH_001).
3. Optional deduped walk-forward reruns for CAMPAIGN_012–014 (validated rejection certification).
4. Optional CAMPAIGN_010 deduped walk-forward if session-breakout metrics needed for meta-analysis.
5. Defer CAMPAIGN_002–009 unless a new hypothesis reopens those families.

## Out of scope

- Strategy tuning or gate changes
- Paper / demo / live enablement
- SQLite file mutation (dedupe remains load-boundary only)
- OANDA API calls
