# CAMPAIGN_027_TRAIN_VALIDATION_001_PLAN

**Status:** TRAIN/VALIDATION EXECUTION — IN PROGRESS / NOT_APPROVED / TEST_LOCKBOX_CLOSED.
Phase 0 of `research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`
(branch off `origin/main` @ `7b50b0e`, after the scaffold sprint merge).

This sprint runs **train + validation** evidence on CAMPAIGN_027's *own* ledgers
for the single frozen candidate that survived the edge-discovery front gate, and
decides **REJECT vs PROCEED-TO-PARITY**. It approves nothing, opens no test
lockbox, and keeps paper/demo/live blocked and `configs/approved_strategies.yaml`
= `approved: []`.

> Binding inputs (frozen — not re-derived here):
> [precommit scope](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md),
> [reconciliation](CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md),
> [artifact contract](CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md) +
> [`research/campaign_027/artifact_contract.json`](../../research/campaign_027/artifact_contract.json),
> [parity design](CAMPAIGN_027_BACKTRADER_PARITY_DESIGN.md),
> [next-sprint prompt](NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD.md).

---

## Purpose

Adjudicate the nine pre-registered kill conditions on a clean train/validation
split using the campaign's own per-signal and per-trade ledgers, computed with
the **exact frozen rule** and the **conservative (binding) cost model**. The
maximum possible outcome is
`TRAIN_VALIDATION_PASS_PARITY_REQUIRED / TEST_LOCKBOX_CLOSED / NOT_APPROVED`.
Backtrader parity and the human-gated single-use test open are downstream sprints;
approval is a separate manual human edit and is never automatic.

## Source scaffold docs (read and reconciled in Phase 0)

All six binding docs were read; the frozen rule is **internally consistent** across
the precommit scope, the reconciliation, `artifact_contract.json`, the scaffold
summary, the config YAML, and the strategy module. **No `BLOCKED_PRECOMMIT_AMBIGUITY`.**

## Exact frozen rules (verbatim from the precommit; not re-tuned)

| element | frozen value |
|---|---|
| timeframe | **H4** (signal + execution; no other TF read) |
| universe | 7 majors: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD |
| signal source | mid close `(bid+ask)/2` |
| z-score lookback | **20** bars |
| z-score shift | mean/σ **`.shift(1)`** (no lookahead) |
| z-score σ | pandas **`ddof=1`** (inline; matches lab engine) |
| base trigger | `\|z\| ≥ 2.0` |
| strong-extension (effective entry) | **`\|z\| ≥ 2.5`** |
| side | **SHORT-ONLY**: enter short when `z ≥ +2.5`; long (`z ≤ −2.5`) **diagnostic-only, never entered** |
| low-vol filter | ATR(14) **simple mean of TR**; trailing **250**-bar percentile **`.shift(1)`**; pass when **`≤ 0.33`** |
| quiet-session filter | UTC bucket ∈ {asia [0,7), london [7,12)} |
| dropped filters | `f_cost_adv_pair` (sample-only), `f_long_side` (hurts) |
| entry fill | **`next_bar_open`** (open of bar `t+1`) |
| primary exit | **time stop at 12 H4 bars** (filled next_bar_open of `t_entry+12`) |
| protective exit | wide **3×ATR(14)** hard stop; **adverse stop wins a same-bar tie** |
| take-profit / trailing | **none** / **none** |
| cost — optimistic (diagnostic) | realized per-bar spread + 2×0.2-pip slip |
| cost — conservative (**BINDING**) | flat 1.5-pip spread + 2×0.2-pip slip + financing over the 12-bar hold |
| cost — stress | 2× conservative (spread + slip doubled) |

## Non-goals (hard prohibitions, unchanged from the freeze)

- **No tuning.** The frozen rule runs as-is. No parameter matrix, no re-selection
  of filters/side/thresholds/exits after seeing results. A failing rule → REJECT,
  never a re-tune.
- **One frozen candidate** only (single-candidate registry).
- **No long-side trading** added.
- **No matrix** added.
- **No test lockbox** sampled (2025-01-01 → 2026-05-20 sealed).
- **No approval**; no edit to `configs/approved_strategies.yaml`.
- No paper/demo/live; no executor/broker/OANDA mutation; no live creds; no new
  fetch; local H4 store only.
- **No gate changes after seeing results.** All gates are fixed in this plan.
- No `.env`/credentials/DB/raw-candle/bulky-artifact commits.
- If train/validation fails, the campaign is **not rescued**.

## Safety invariants (verified continuously)

- `configs/approved_strategies.yaml` stays `approved: []`.
- Paper/demo/live loops keep refusing.
- No executor/broker/OANDA mutation file is changed.
- The runner refuses (and is tested to refuse) any window overlapping the test
  lockbox; `--fail-if-test-window` defaults true, `--no-test-lockbox` defaults true.
- Ledgers are compact (per-signal / per-trade rows; never per-bar dumps).

## Split plan (frozen before execution — repo-standard, same as the precommit)

```
train:      2020-01-01 → 2022-12-31   (selection window — single candidate, no tuning)
validation: 2023-01-01 → 2024-12-31   (confirmation only; G7 — never selection)
test:       2025-01-01 → 2026-05-20   (LOCKBOX — sealed; NOT opened this sprint)
```

Chronological, non-overlapping. Validation includes the **2024 recency** period —
the headline kill risk. The exact per-pair coverage and warmup adequacy are
frozen in Phase 1 (`CAMPAIGN_027_DATA_COVERAGE_AND_SPLIT_DECISION.md`) before any
execution.

## Gate plan (pre-registered; binding on the conservative cost metric)

**Train gates (Phase 4):**

1. conservative train expectancy **> 0**
2. train profit factor **≥ 1.05**
3. train trades **≥ 100** (documented minimum; mirrors C025 convention)
4. **≥ 4/7** train pairs non-negative
5. **≥ 2/3** train years (2020–2022) non-negative
6. 2× train cost stress expectancy **≥ 0**, or only mildly negative with a
   documented reason
7. matched-null: train beats the structure-matched null by a meaningful margin
8. filter-ablation: each retained filter re-derives `FILTER_ADDS_EDGE` on train

**Validation gates (Phase 5 — run once, only if train gates pass):**

1. conservative validation expectancy **> 0**
2. validation profit factor **≥ 1.05**
3. validation trades **≥ 100** (documented minimum)
4. **≥ 4/7** validation pairs non-negative
5. **2024 must not be materially negative** (recency gate — may not be weakened)
6. 2× validation cost stress expectancy **≥ 0**, or only mildly negative with reason
7. matched-null: validation beats the structure-matched null by a meaningful margin
8. filter-ablation: retained filters still supported on validation

**Outcome classification:**

- Train fails → `REJECT_TRAIN_GATE` (validation not run).
- Validation fails → `REJECT_VALIDATION_GATE` / `REJECT_RECENCY_GATE` /
  `REJECT_COST_STRESS_GATE` / `REJECT_MATCHED_NULL_GATE` (most specific binding cause).
- Both pass → `TRAIN_VALIDATION_PASS_PARITY_REQUIRED / TEST_LOCKBOX_CLOSED / NOT_APPROVED`.
- Blockers → `BLOCKED_PRECOMMIT_AMBIGUITY` / `BLOCKED_ARTIFACT_CONTRACT` /
  `BLOCKED_DATA_PRECONDITION`.

## Artifact contract plan (per `artifact_contract.json`, items 1–12)

Emitted under `research/campaign_027/train_validation/`:
`run_manifest.json`, `candidate_registry.json`, `signal_ledger.csv`,
`trade_ledger_train.csv`, `trade_ledger_validation.csv`, `filter_stage_ledger.csv`,
`signal_funnel_ledger.csv`, `train_metrics.json`, `validation_metrics.json`,
`gate_result.json`, `pair_metrics_{train,validation}.csv`,
`year_metrics_{train,validation}.csv`, `side_metrics_{train,validation}.csv`,
`cost_stress_2x.json`, `matched_null_result.json`,
`filter_ablation_confirmation.json`, `recency_risk_report.json`,
`artifact_contract_compliance.json`, `blocked_or_warning_conditions.json`.

Both `*_optimistic` and `*_conservative` cost figures carried; conservative is
binding. Reproducibility manifest carries commit hash, input data path, dedupe
policy, date span, the precommitted rule, lab module versions, seed metadata, and
`strategy_evidence` (true for this campaign's own evidence run, while
`promotion_eligible`/`approved` stay false). C011 deduped null referenced.

**Compatibility note (documented honestly):** the edge-discovery `matched_nulls`
module reconstructs the strategy's forward log-return from the frame's close
prices at the ledger's `entry_time` over `bars_held` — a close-to-close *timing/
direction information* benchmark. It is intentionally **not** the campaign's
realized `next_bar_open` post-cost PnL (which the trade ledger carries
separately). Both are reported; the matched-null gate is on the information
benchmark, the expectancy/PF/recency gates are on the realized ledger.

## Validation commands

```
PYTHONPATH=$PWD/src python -m pytest tests/ -q
PYTHONPATH=$PWD/src ruff check src tests scripts research
PYTHONPATH=$PWD/src python scripts/check_research_freeze.py
PYTHONPATH=$PWD/src python scripts/validate_research_archive.py
PYTHONPATH=$PWD/src python scripts/scan_artifacts_for_secrets.py
PYTHONPATH=$PWD/src python scripts/run_campaign_027_h4_filtered_zscore_reversion.py --preflight-only
PYTHONPATH=$PWD/src python scripts/run_campaign_027_h4_filtered_zscore_reversion.py --data-feature-preflight
```

(Worktree runs require `PYTHONPATH=$PWD/src`; the H4 store resolves worktree-aware
to the primary checkout's `data/campaign_002.sqlite3`.)

## Blocked conditions (stop and document; do not improvise)

- `BLOCKED_PRECOMMIT_AMBIGUITY` — scaffold/precommit inconsistent. *(Not present:
  Phase-0 audit found the frozen rule internally consistent.)*
- `BLOCKED_ARTIFACT_CONTRACT` — the runner cannot emit a required artifact schema
  (Phase 3 pre-run check). Train/validation does not proceed.
- `BLOCKED_DATA_PRECONDITION` — H4 store missing or warmup insufficient for any
  pair (Phase 1).

## Phase 0 baseline (recorded)

- Branch created off `7b50b0e` (scaffold merged into main).
- `approved_strategies.yaml` = `approved: []` (verified).
- `ruff` clean; freeze gate ALL PASS; archive ALL PASS; secret scan PASSED
  (value scan skipped — no live creds in env).
- `pytest tests/ -q` → **2188 passed, 3 skipped** (pre-existing local-data skips).
- `--preflight-only` → preflight_ok=true, 7/7 PASS (~9,949 H4 bars/pair).
- `--data-feature-preflight` → preflight_ok=true, 7/7 features computable (train window).
- No executor/broker/OANDA mutation file changed.
</content>
</invoke>
