# CAMPAIGN_027_H4_FILTERED_ZSCORE_REVERSION_SCAFFOLD_001_PLAN

**Status:** SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED.
**Sprint:** `research-campaign-027-h4-filtered-zscore-reversion-scaffold-001`.
**Date:** 2026-05-28.

This is a **scaffold/precommit** sprint. It freezes the hypothesis, rules,
artifact contract, kill conditions, execution realism, and future evidence plan
for the single idea that survived the edge-discovery front gate — **before** any
train/validation evidence is run. It runs **no** strategy evidence, opens **no**
test lockbox, and approves **nothing**.

---

## Purpose

The edge-discovery front gate
(`research-edge-discovery-front-gate-idea-selection-001`, merged to `main` at
`556759a`) screened **12 idea families** and found **exactly one** borderline
`CAMPAIGN_ELIGIBLE` idea: **H4 low-volatility, quiet-session, strong-extension,
short-biased z-score mean reversion on the seven majors.** That sprint
*explicitly created no campaign*. This sprint creates the **CAMPAIGN_027
scaffold** for that idea — config skeleton, strategy module, artifact contract,
preflight-only runner, parity design, future-execution prompt, and frozen
precommit rules — so a *later, separately-authorized* train/validation sprint
can adjudicate it on a clean split without any post-hoc parameter tuning.

## Source front-gate docs (read first)

- [Front-gate summary](EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_SUMMARY.md)
- [Idea ranking & decision](EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md)
- [Filter ablation results](EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md)
- [Matched-null screening results](EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md)
- [Signal-probe results](EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md)
- [Opportunity-map refresh](EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md)
- [Next-campaign precommit prompt](NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md)
- [Future-campaign artifact requirements](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md)
- [Edge-discovery compatibility checklist](EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md)
- [Future-campaign reentry gates](FUTURE_CAMPAIGN_REENTRY_GATES.md)
- [Pre-campaign edge-discovery checklist](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md)

## Campaign identity

| field | value |
|---|---|
| campaign_id | **CAMPAIGN_027** (verified free — see truth audit below) |
| strategy_family | `h4_filtered_zscore_reversion` |
| version | `0.1.0-c027` |
| timeframe | H4 |
| universe | EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD (7 majors) |
| status | SCAFFOLD_ONLY / PRECOMMITTED / NOT_RUN / NOT_APPROVED |

### CAMPAIGN_027 free — truth-audit record

`556759a` (latest `origin/main`) includes the edge-discovery null-benchmark lab,
the front-gate idea-selection sprint, and the C025/C026 rejected artifacts. Greps
for `CAMPAIGN_027` / `campaign_027` / `c027` / `0.1.0-c027` return **only
forward-looking, negative references** (`campaign_027_created: false`, "no
CAMPAIGN_027 created", "C027 expected free"). No config, strategy module,
research dir, version code, or status row uses the number as an *occupied*
campaign. **CAMPAIGN_027 is free**; this sprint assigns it.

## Non-goals (this sprint does NOT)

- run train, validation, or test evidence;
- open the test lockbox (sealed: 2025-01-01 → 2026-05-20);
- approve any strategy or touch `configs/approved_strategies.yaml`
  (stays `approved: []`);
- enable paper/demo/live or modify executor/broker/OANDA behavior;
- call OANDA order/trade/position/transaction/live endpoints or use live creds;
- fetch new broker data;
- tune any parameter after reading additional results;
- revive C022/C024/C025/C026 or any rejected family;
- weaken the edge-discovery kill conditions or reentry gates.

## Safety invariants (held throughout)

- `configs/approved_strategies.yaml` remains `approved: []`.
- Paper/demo/live loops remain frozen/refusing; `trading_enabled: false`,
  `allow_order_submission: false`, `allow_live_trading: false`.
- No executor/broker/OANDA mutation files are changed.
- `not_approved: true`, `scaffold_only: true`, `promotion_eligible: false`,
  `strategy_evidence: false` on every emitted artifact.
- All committed artifacts are compact; no `.env`, credentials, DB dumps, raw
  candles, or bulky per-bar data are staged.
- Local existing H4 store only (`data/campaign_002.sqlite3`); no new fetch.

## Edge-discovery evidence summary (why this idea earned a scaffold)

- **Cost feasibility — PASS.** H4 spread/ATR ≈ 0.04–0.10, far below the 0.25
  hostile gate. Edge-adding subset survives a conservative financing-inclusive
  overlay: **+0.000626 conservative / +0.000754 optimistic** (n=1,065, hit 0.55).
- **Forward-return information — PASS.** Signed forward log-return rises
  monotonically with horizon (pre-cost +0.000009 → +0.000341, h1→h24); post-cost
  turns positive at **h12** and stays positive at h24.
- **Matched null — PASS.** `BEATS_MATCHED_NULL` on **all six** modes
  (timestamp-random, side-shuffled, pair-matched, session-matched,
  holding-period-matched, full) at percentile 100, effect 3.7–6.0.
- **Filter ablation — PASS.** `f_low_vol` (+0.000301), `f_strong_extension`
  (+0.000208), `f_quiet_session` (+0.000234) each `FILTER_ADDS_EDGE` (not
  sample-only). `f_cost_adv_pair` only reduces sample; `f_long_side` **hurts**
  (−0.000199) → short bias.
- **Robustness — PARTIAL PASS.** Pair-robust (6/7 positive; USD_CHF ≈ flat);
  multi-year positive 4/7 conservative (5/7 optimistic); **not** a single-year
  (2023) artifact after filtering.

## Known risks (carried into binding future kill conditions)

1. **Edge is wafer-thin** (≈0.005–0.007%/trade, hit ≈ 0.50): a small asymmetry,
   not a win-rate edge; sits inside the cost-assumption uncertainty band.
2. **Recency / non-stationarity:** conservative-cost subset was **negative in
   2021, 2024, and 2026-partial**. The two most recent periods being negative is
   the headline risk.
3. **Filter forking-path:** the three filters were retained *after* seeing the
   ablation; the rule must be precommitted and re-confirmed on a clean split.
4. **Selection-noise context:** the raw cross-variant matrix flagged
   `LIKELY_SELECTION_NOISE` (USD_JPY single-pair). The campaign must demonstrate
   `ROBUST_MATRIX_SIGNAL` on its own train matrix.
5. **Signal information, not a proven tradable strategy.** Nothing is approved.

## Precommitted kill conditions for the FUTURE execution sprint

A future train/validation sprint must **REJECT or BLOCK** CAMPAIGN_027 if any of
these occur (these may not be weakened):

1. Train expectancy ≤ 0 after conservative cost.
2. Validation expectancy ≤ 0 after conservative cost.
3. The filtered edge is not robust across pairs or becomes single-pair dominated.
4. The filtered edge remains negative or collapses in recent years, especially
   **2024/2026**.
5. Matched-null comparison no longer beats random by a meaningful margin.
6. Filter ablation shows filters only reduce sample instead of adding edge.
7. 2× cost stress fails materially.
8. Backtrader parity cannot be achieved before any promotion-review step.
9. Required artifact ledgers are missing or incompatible with the
   edge-discovery lab.

## Expected phases (this sprint)

0. **Truth audit + plan** (this doc) — branch, freeze, CAMPAIGN_027-free,
   baseline gates.
1. **Evidence-to-precommit reconciliation** — reconcile front-gate diagnostics
   into the exact precommit decision.
2. **Precommit strategy specification** — freeze the future strategy rules
   (the most important document).
3. **Artifact contract + edge-discovery compatibility design** — machine-readable
   contract + contract tests.
4. **Scaffold strategy/config skeleton** — config, strategy module, pure-signal
   unit tests.
5. **Preflight-only runner** — `--preflight-only` / `--data-feature-preflight` /
   `--sample-signals-only`; runner-refuses-evidence tests.
6. **Backtrader parity design stub** — design only.
7. **Future execution prompt** — full train/validation prompt (NOT executed).
8. **Archive/status/backlog updates** — status SCAFFOLD_ONLY; no evidence
   recorded.
9. **Final validation + summary** — re-run gates, preflight, write 25-item
   summary.

## Validation commands

```
PYTHONPATH=$PWD/src python -m pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
# scaffold preflight (added in Phase 5):
python scripts/run_campaign_027_h4_filtered_zscore_reversion.py --preflight-only
python scripts/run_campaign_027_h4_filtered_zscore_reversion.py --data-feature-preflight
```

NB: worktree runs require `PYTHONPATH=$PWD/src` (the editable install points at
the primary checkout), and the H4 store resolves to the primary checkout's
`data/campaign_002.sqlite3` (worktree-aware resolution in the runner).

## Blocked conditions (stop and ask)

- **BLOCKED_CAMPAIGN_ID_COLLISION** — if CAMPAIGN_027 were already used as a real
  campaign (it is not; documented above). Resolved: proceed.
- **BLOCKED_DATA_PRECONDITION** — if the H4 store is unavailable, the runner
  records the block rather than improvising; no evidence is fabricated.

## Baseline validation (Phase 0 result)

Run on the fresh branch before any change:

- `pytest tests/ -q` → **2157 passed, 3 skipped** (skips are local-data-absent,
  pre-existing).
- `ruff check src tests scripts research` → **All checks passed.**
- `check_research_freeze.py` → **ALL CHECKS PASSED** (loops refuse; approved=[]).
- `validate_research_archive.py` → **ALL CHECKS PASSED** (all campaigns
  strategy_approved=false).
- `scan_artifacts_for_secrets.py` → **PASSED** (value scan skipped — no live
  creds in env; pattern scan clean).
