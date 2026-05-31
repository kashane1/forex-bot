# USD_JPY Post-Entry Trade-Management Diagnostic — Sprint 001 Plan

**Date:** 2026-05-28 · **Branch:** `research-usdjpy-post-entry-trade-management-diagnostic-001`
(off the USD_JPY microstructure entry-closeout tip `110181e`).
**Type:** read-only diagnostic. Approves nothing, executes no campaign, implements no
strategy, tunes nothing, changes no verdict, creates no C024, claims no edge.

> The USD_JPY M15 microstructure **entry** lane is CLOSED (no live entry edge). This
> sprint is a **post-entry trade-management** diagnostic: it asks whether post-entry
> behavior (retest-hold / trap / early MFE-MAE) — knowable *while a trade is already
> open* — could inform early-invalidation / hold decisions. Everything here is
> **trade management, not entry alpha**, and **diagnostic, not a rule**.

## 1. Purpose

The only above-floor separation found in the entry diagnostic was **post-entry**
(retest-hold AUC 0.611/0.552; trap). That cannot gate an entry, but it is the natural
input to managing a trade already open. This sprint tests, read-only and USD_JPY-only,
whether post-entry events separate:

- trades to **exit early** vs **keep holding**,
- trades likely to become **hard-stop losses** vs **survive to profitable time exits**.

## 2. USD_JPY-only scope

USD_JPY only; reuse the existing 306 C022 USD_JPY base trades and materialized M15
paths (read-only). H1/H4 not needed. No seven-pair aggregation. USD_JPY focus is a
research-scoping decision, **not** an edge claim.

## 3. Post-entry-only framing (live-manageable vs hindsight)

Every signal is evaluated **after** entry, at fixed diagnostic horizons (**2, 4, 8, 16**
M15 bars). For each event we label:

- **live-manageable** — knowable in real time by horizon N while the trade is open
  (could *in principle* become a management rule);
- **hindsight-only** — knowable only at/after exit (e.g. full time-to-threshold);
- **descriptive** — metadata.

A management decision at horizon N may use only post-entry bars `1..N` and only matters
for trades **still open at N**. No event may use bars beyond its declared horizon.

## 4. Non-goals

Not a strategy; not C024; not C023 execution; not a campaign; not entry-alpha; not
paper/demo/live; not a tradable rule. No threshold is selected from outcome performance.

## 5. Safety rules (hard)

- No CAMPAIGN_024; no C023 execution; no strategy/entry-exit logic edits; no campaign.
- No verdict change; no historical-metric rewrite.
- `configs/approved_strategies.yaml` stays `approved: []` (verify only).
- No paper/demo/live; no broker/executor/order/live changes; no OANDA mutation/order
  calls; no live credentials. `.env` used **only** read-only for the research DB.
- Gitignore the full per-trade dataset; commit only manifest + small preview + summary JSON.
- Counterfactual early-exit deltas are **optimistic** (assume the signal is acted on
  perfectly) and are reported as diagnostic, never tradable.
- Clearly separate live-manageable vs hindsight-only; never present post-entry signals
  as entry alpha; no threshold mining.

## 6. Diagnostic event families (Phase 1)

1. `early_retest_hold` — post-entry retest of the reclaimed EMA that holds (live).
2. `early_reclaim_failure` — close back through the reclaim level against the trade (live).
3. `no_continuation_within_n_bars` — no +0.25R/+0.5R reached within N bars (live).
4. `early_adverse_expansion` — adverse excursion past −0.5R before +0.25R within N (live).
5. `early_favorable_displacement` — +0.25R/+0.5R reached quickly with controlled MAE (live).
6. `trap_or_failed_breakout` — reclaim invalidated within the first 2 bars (live).
7. `range_compression_after_entry` — trade stalls in a tight range after entry (live).
8. `time_to_first_mfe_threshold` — bars to +0.25R/+0.5R/+1.0R (hindsight/descriptive).
9. `time_to_first_mae_threshold` — bars to −0.25R/−0.5R/−0.9R (hindsight/descriptive).

Horizons are a small fixed set (2/4/8/16); conventional cuts (e.g. −0.5R, tol) are
documented as **non-tuned**. Pure, read-only, lookahead-bounded; synthetic unit tests
for long/short and a no-lookahead-beyond-horizon test.

## 7. Expected artifacts

- `docs/research/USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_PLAN.md` (this, Phase 0).
- `src/forex_bot/research/post_entry_trade_management.py` + unit tests (Phase 1).
- `scripts/build_usdjpy_post_entry_trade_management_dataset.py` + compact outputs (Phase 2).
- `scripts/analyze_usdjpy_post_entry_trade_management.py` + summary JSON + `docs/research/USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_RESULT.md` (Phase 3).
- `scripts/simulate_usdjpy_post_entry_management_counterfactuals.py` + outputs OR a `COUNTERFACTUALS_NOT_RUN` note (Phase 4).
- `docs/research/USDJPY_TRADE_MANAGEMENT_READINESS_DECISION.md` (Phase 5).
- `docs/research/USDJPY_POST_ENTRY_TRADE_MANAGEMENT_DIAGNOSTIC_001_SUMMARY.md` (Phase 6).

Full per-trade parquet is **gitignored**; only manifest + small preview + summary JSON committed.

## 8. Separation method

AUC = P(event-value > on the "positive" class), effect = |AUC−0.5|, negligible below
0.05; "stable" = train & validation AUC on the same side of 0.5 with ≥ 30 per class
(small-sample caveats flagged). Targets: hard_stop vs time_exit, profitable vs losing,
straight_to_stop vs not, clean_winner vs not. Each event is also assessed for
early-exit loss reduction **and** winner damage (cutting trades that would have won).

## 9. Validation commands

`pytest tests/ -q` · `ruff check src tests scripts research` ·
`python scripts/check_research_freeze.py` · `python scripts/validate_research_archive.py` ·
`python scripts/scan_artifacts_for_secrets.py` · `git status --short`.

## 10. Phase-0 baseline (executed on this branch)

| Check | Result |
|---|---|
| Prior docs present | All 5 present. |
| C023 / C024 | C023 scaffold-only/not executed; C024 absent. |
| `approved_strategies.yaml` | `approved: []`. |
| USD_JPY data | C022 USD_JPY trades + microstructure parquet/manifest present; DB reachable read-only. |
| `pytest tests/ -q` | 1984 passed, 3 skipped (data-dependent). |
| `ruff` / `check_research_freeze` / `validate_research_archive` / `scan_artifacts_for_secrets` | all pass. |

## 11. Explicit no-C024 / no-C023 / no-approval statement

This sprint creates **no CAMPAIGN_024**, executes **no C023**, runs **no campaign**,
approves **no strategy** (`approved: []` unchanged), changes **no verdict**, and keeps
**paper/demo/live blocked**. It ends at a **trade-management readiness classification**;
even `TRADE_MANAGEMENT_PRECOMMIT_READY` only unlocks a separate pre-committed,
out-of-sample study — never a campaign or C024 here. USD_JPY is not presented as edge.
