# CAMPAIGN_015 — Post-Run Diagnostics Sprint 001 — Plan

**Branch:** `research-campaign-015-post-run-diagnostics-001`
**Sprint kind:** post-run diagnostic only — NOT a new strategy, NOT a tuning
pass, NOT a promotion pass.
**Strategy under inspection:** `failed_breakout_reversal 0.1.0-c015`
**Frozen config:** [`configs/campaign_015_failed_breakout_reversal.yaml`](../../configs/campaign_015_failed_breakout_reversal.yaml)
**Config hash:** `17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`
**Approved-strategy registry:** unchanged, must remain `approved: []`.
**Date:** 2026-05-25 / 2026-05-26

> Loading this plan does not approve any strategy. No paper / demo / live
> loop is enabled by this work. No broker call, no `.env`, no live OANDA.
> Diagnostics cannot — and will not — flip the CAMPAIGN_015 verdict from
> REJECT to PASS.

---

## 1 · Observed run summary (the input we are explaining)

From the CAMPAIGN_015 bespoke walk-forward runner, frozen config + frozen
plan + frozen strategy parameters; the verdict and aggregate metrics
exactly reproduced under this sprint's clearly-labeled rehydrate run
(see §6 below):

| dimension | base cost | 2x cost |
|---|---|---|
| verdict (runner) | REJECT | REJECT |
| aggregate expectancy R | **+0.2300** | **+0.1909** |
| profit factor | **107.5543** | **39.6926** |
| total trades | **164** | **164** |
| folds passing fold-gates | **0 / 8** | **0 / 8** |
| pairs positive | **6 / 7** | (same trades) |
| single-pair dominance % | 30.21% | 30.21% |
| median per-fold expectancy R | +0.2588 | — |
| trade-level cumulative R | +37.73 | — |
| aggregate-gate verdict | FAIL | FAIL |

Failing aggregate gates (both cost regimes):
- `fold_pass_rate_ge_5_of_8` — **FAIL** (0/8)
- `trade_count_min_200` — **FAIL** (164 < 200)

Passing aggregate gates:
- `fold_count_ge_8`, `expectancy_r_min`, `profit_factor_min`,
  `trade_count_max_800`, `pairs_positive_ge_4_of_7`,
  `single_pair_dominance_le_70pct`.

Runner conclusion: **REJECT — NOT_APPROVED**.

This is — by aggregate expectancy and aggregate profit factor — the
best-looking CAMPAIGN result on file. It is still rejected because the
*pre-committed robustness gates* (fold-pass rate and minimum trade
count) failed. This sprint is about understanding **why**.

---

## 2 · Core diagnostic question

> Is CAMPAIGN_015 a genuinely promising sparse edge that deserves a
> future pre-committed follow-up candidate, or is it a fragile
> aggregate artifact caused by a small number of lucky trades / pairs
> / folds?

Sub-questions:
1. Which aggregate gate(s) actually failed, and by how much?
2. Which fold-gate(s) failed in each of the 8 folds, and is the
   pattern dominated by `trade_count_ge_30` (the sparse-edge
   signature) or by expectancy / pair-positivity / single-pair
   dominance?
3. Is the positive aggregate R concentrated in 1–3 trades / 1 pair /
   1 fold / 1 pair-fold cell?
4. How fragile is the aggregate to leave-one-out by fold and by pair?
5. How does CAMPAIGN_015 compare to the CAMPAIGN_011 random-entry
   null (the canonical null baseline)?
6. Does the Backtrader secondary lane corroborate the bespoke
   numbers?

---

## 3 · Input artifacts and reconciliation

### 3.1 Pre-existing artifacts (left untouched)
- [`backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/gate_result.json`](../../backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/gate_result.json) —
  the prior sprint's published artifact, which records
  `blocked: true` with `database_path does not exist: data/campaign_002.sqlite3`.
- [`backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/preflight.json`](../../backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/preflight.json) —
  matching BLOCKED preflight from the prior sprint.
- [`backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/plan.json`](../../backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/plan.json) —
  the frozen 8-fold rolling plan.

> The CAMPAIGN_015 sprint that produced the §1 observed run executed
> the runner against a local sqlite at the main repo root
> (`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`); that
> sqlite is not visible from this worktree's `data/` directory, so the
> committed `gate_result.json` reflects the BLOCKED preflight, not the
> aggregate numbers. The metrics in §1 are real and reproducible — but
> the public, committed artifact of record was BLOCKED. This sprint
> closes that evidence gap by producing a clearly-labeled rehydrate run
> alongside the original, without overwriting it.

### 3.2 Rehydrate run for diagnostics (NEW, this sprint)
- [`research/campaign_015/diagnostics/walk_forward_rehydrate/`](../../research/campaign_015/diagnostics/walk_forward_rehydrate/) —
  rehydrate of the frozen CAMPAIGN_015 walk-forward, into a
  clearly-labeled diagnostic directory, with full per-fold + per-pair
  detail. Same `config_hash`, same plan, deterministic.

  Contains:
  - `walk_forward/gate_result.json` — aggregate gate outcomes
  - `walk_forward/fold_detail.json` — per-fold + per-pair + per-trade R series
  - `walk_forward/plan.json`, `walk_forward/preflight.json`, `walk_forward/results.json`, `walk_forward/results.md`
  - `folds/base/fold_<NN>/fold_<NN>_<PAIR>_summary.json`
  - `folds/base/fold_<NN>/fold_<NN>_<PAIR>_trades.csv`
  - same under `folds/2xcost/`.

### 3.3 Comparator artifacts referenced (NOT modified)
- CAMPAIGN_011 random-entry null: [`backtests/CAMPAIGN_011_random_entry_anchor/`](../../backtests/CAMPAIGN_011_random_entry_anchor/).
- Backtrader secondary lane: [`backtrader/`](../../backtrader/) if/when present.

---

## 4 · Diagnostic phases (this sprint)

| Phase | Output | Purpose |
|---|---|---|
| 0 | this plan | truth audit; sprint scaffold |
| 1 | `scripts/diagnose_campaign_015_gate_failures.py` + `research/campaign_015/diagnostics/gate_failure_autopsy.{json,md}` + `docs/research/CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md` | which gates failed and why |
| 2 | `scripts/diagnose_campaign_015_concentration.py` + `research/campaign_015/diagnostics/concentration.{json,md}` + `docs/research/CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md` | trade / pair / fold concentration + LOO fragility |
| 3 | `scripts/run_campaign_015_anti_overfit_diagnostics.py` + `research/campaign_015/diagnostics/null_and_anti_overfit.{json,md}` + `docs/research/CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md` | matched-null gap + anti-overfit label |
| 4 | `research/campaign_015/diagnostics/backtrader_comparison.json` + `docs/research/BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md` | bespoke-vs-Backtrader sanity check |
| 5 | `docs/research/CAMPAIGN_015_POST_RUN_INTERPRETATION.md` | human-readable answer |
| 6 | `docs/research/CAMPAIGN_016_CANDIDATE_DESIGN_FROM_C015_DIAGNOSTICS.md` *or* `docs/research/CAMPAIGN_015_NO_FOLLOWUP_DECISION.md` | follow-up decision, **docs-only** |
| 7 | `docs/research/CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_SUMMARY.md` | sprint summary + final validation |

A phase that lacks its required inputs emits a clearly-labeled
`BLOCKED` diagnostic that explains exactly what is missing; it does
not invent results.

---

## 5 · Non-goals (hard rules)

- Not adding `failed_breakout_reversal` to `configs/approved_strategies.yaml`.
- Not enabling paper / demo / live for any strategy.
- Not creating, modifying, cancelling, or closing broker orders.
- Not contacting live OANDA.
- Not tuning CAMPAIGN_015 parameters; not editing any frozen
  CAMPAIGN_015 setting (config, plan windows, gates, strategy params).
- Not relaxing pre-committed gates.
- Not revising the runner verdict from REJECT to PASS.
- Not inventing missing data — BLOCKED is a legitimate diagnostic outcome.
- Not committing `.env`, credentials, sqlite DBs, or large CSVs.
- Not mutating prior campaign evidence except by adding clearly-labeled
  diagnostic artifacts under `research/campaign_015/diagnostics/` and
  `docs/research/CAMPAIGN_015_*_POST_RUN_*.md`.

---

## 6 · Worktree truth audit (Phase 0 result)

- Branch: `research-campaign-015-post-run-diagnostics-001` — new, clean.
- `configs/approved_strategies.yaml` — `approved: []`. ✅
- Paper-loop / demo-loop refuse trend_following — confirmed by
  `python scripts/check_research_freeze.py` ⇒ `research freeze gate: ALL CHECKS PASSED`.
- `python scripts/validate_research_archive.py` ⇒ `research archive: ALL CHECKS PASSED`.
- `python scripts/scan_artifacts_for_secrets.py` ⇒ `artifact secret scan: PASSED`.
- `pytest tests/ -q` ⇒ `1423 passed in 10.37s`.
- `ruff check src tests scripts research` ⇒ 3 pre-existing findings
  in `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  introduced by an earlier sprint (commit `e382af4`), unrelated to
  CAMPAIGN_015 and out of scope for this sprint.
- CAMPAIGN_015 run artifacts:
  - prior `backtests/CAMPAIGN_015_.../walk_forward/gate_result.json` —
    BLOCKED (database missing from worktree-relative path).
  - new `research/campaign_015/diagnostics/walk_forward_rehydrate/` —
    full, deterministic, REJECT verdict reproducing the §1 metrics
    exactly, same `config_hash`.
- Local sqlite `data/campaign_002.sqlite3` — symlinked from the main
  repo root (`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`,
  133 MB), in the worktree's gitignored `data/` directory. **Not
  committed.**

---

## 7 · Classification labels available to this sprint

For the **gate-failure autopsy / concentration / null** phases, the
final post-run interpretation must pick **exactly one** label:

- `SPARSE_BUT_PROMISING` — positive aggregate, broadly distributed,
  fails only on trade-count; gap vs null is meaningful per fold;
  worthy of a *new pre-committed* follow-up candidate.
- `AGGREGATE_ARTIFACT` — positive aggregate driven by a handful of
  trades / one pair / one fold; LOO instability is severe; not a
  candidate edge.
- `PAIR_CONCENTRATION_ARTIFACT` — positive aggregate driven by ≥ ~50%
  of one pair's R; aggregate evaporates LOO-by-pair.
- `FOLD_CONCENTRATION_ARTIFACT` — positive aggregate driven by one
  fold's contribution; aggregate evaporates LOO-by-fold.
- `COST_FRAGILE` — gap between base and 2x-cost expectancy is large
  enough that small cost mis-specification destroys the edge.
- `NULL_BEATING_BUT_FRAGILE` — meaningful gap vs matched null, but
  some other fragility (concentration, fold instability) blocks
  approval-track work.
- `NULL_DOMINATED` — no meaningful gap vs the CAMPAIGN_011 random-entry
  null.
- `BLOCKED` — diagnostics could not be completed (e.g., null tooling
  missing, BT lane missing).

---

## 8 · Validation commands (run at Phase 0 and Phase 7)

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

Plus, post-Phase-7, manual checks:
- `configs/approved_strategies.yaml` still `approved: []`.
- No `.env`, credentials, sqlite, or large CSV staged.
- `data/campaign_002.sqlite3` is a symlink, gitignored, never staged.

---

## 9 · This sprint cannot approve the strategy

Even if every diagnostic in §4 landed in CAMPAIGN_015's favour, the
sprint's verdict ceiling is `INFORMATIONAL_DIAGNOSTIC`.
Approval requires:
- a fresh pre-committed campaign on a clean candidate, AND
- an explicit human review and registry edit.

Neither is in scope here. CAMPAIGN_015 remains REJECT, paper / demo /
live remain blocked, `approved_strategies.yaml` remains `approved: []`.
