# CAMPAIGN_011 no-RiskEngine reference — runner

**Date:** 2026-05-25
**Branch:** `infra-bespoke-campaign-011-norisk-reference-001`
**Phase:** 2 of `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`
**`strategy_evidence: false`**

> Documents the new `scripts/export_campaign_011_norisk_reference.py`
> runner. The runner produces the canonical no-RiskEngine bespoke
> reference for CAMPAIGN_011. It does not approve any strategy,
> does not tune anything, and does not change CAMPAIGN_011's
> REJECT / null-diagnostic verdict.

## 1. Command

```bash
python scripts/export_campaign_011_norisk_reference.py \
    --config configs/campaign_011_random_entry_anchor.yaml \
    --db data/campaign_002.sqlite3 \
    --out research/lean_parity/campaign_011_h4_bespoke_reference.json \
    --per-fold-out research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json \
    --diagnostics-md backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md \
    --plan backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json
```

All defaults above are wired in; the bare command
`python scripts/export_campaign_011_norisk_reference.py` produces
the same output paths.

Determinism check (Phase 3):

```bash
python scripts/export_campaign_011_norisk_reference.py \
    --full-window-only --out /tmp/c011_a.json \
    --diagnostics-md /tmp/c011_a.md
python scripts/export_campaign_011_norisk_reference.py \
    --full-window-only --out /tmp/c011_b.json \
    --diagnostics-md /tmp/c011_b.md
sha256sum /tmp/c011_a.json /tmp/c011_b.json
```

Both hashes must match. `--full-window-only` skips the per-fold pass
so the determinism check stays fast (the per-fold pass is also
deterministic by the same SHA-256 seed mechanism).

## 2. Inputs

| input | source | required |
|---|---|---|
| YAML config | `configs/campaign_011_random_entry_anchor.yaml` | yes; frozen pre-commit |
| Strategy module | `src/forex_bot/strategies/random_entry_anchor.py` | yes; frozen |
| SQLite store | `data/campaign_002.sqlite3` | yes; local only, gitignored |
| Walk-forward plan | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` | optional (only the per-fold rollup needs it) |
| `master_seed` | `20260523` (read from the YAML; verified frozen) | yes |
| Window | `2020-01-01` → `2026-05-20` (compiled-in constants) | yes |

Frozen-parameter enforcement is identical to
`scripts/run_campaign_011.py`: any deviation aborts the run before
any backtest fires, with a clear error message and a pointer to
`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5.

## 3. Outputs

| output | path | committed | role |
|---|---|---|---|
| Full-window reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | yes | the canonical comparison target for the future Backtrader sprint |
| Per-fold rollup JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | yes | informational sanity check vs the published walk-forward plan |
| Diagnostics MD | `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | yes | human-readable parity-style summary table |
| Run log line(s) | stdout | n/a | per-pair trade count + expectancy_r live progress |
| Optional raw trade dumps | `backtests/diagnostics/campaign_011_norisk/...` | **gitignored** | opt-in via `--trades-out`; never committed |

Both committed JSONs are ≤ 16 KB combined. The diagnostics MD is
≤ 8 KB. The schema is fixed by
`CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md`.

## 4. Failure modes (fail-loud)

| condition | behaviour |
|---|---|
| SQLite missing | `BLOCKER:` line on stderr; exit code `1`. |
| Frozen parameter drift | `SystemExit` with a per-key diff list and pointer to §5 of the pre-commit. |
| `master_seed != 20260523` | `SystemExit` — seed tuning is forbidden. |
| Universe mismatch | `SystemExit` — pairs must be the seven canonical OANDA majors in canonical order. |
| Data source ≠ `oanda-practice` | `SystemExit` per pair on first non-match. |
| No candles for a pair in the window | `BLOCKER:` line on stderr; exit code `1`. |
| `--plan` path missing (and `--full-window-only` not passed) | `SystemExit`. |
| Plan not `rolling` / `frozen` / `strategy_evidence: false` | not enforced by this exporter — the plan is the already-committed CAMPAIGN_011 plan, and `scripts/run_campaign_011.py` already enforces those invariants. |

## 5. Gitignore behaviour

The exporter's small artefacts (full-window JSON, per-fold JSON,
diagnostics MD) are committed. Any optional raw trade dump goes
under `backtests/diagnostics/campaign_011_norisk/` which is added
to `.gitignore` by this sprint (Phase 2 commit). The opt-in
`--trades-out` flag must point inside that directory (this is a
convention, not enforced — the operator is responsible).

## 6. Safety notes

- The exporter never calls OANDA APIs. It reads
  `data/campaign_002.sqlite3` only.
- The exporter never reads or writes `configs/approved_strategies.yaml`.
  CAMPAIGN_011 cannot be added to that registry under any
  circumstance.
- The exporter never imports `forex_bot.broker`,
  `forex_bot.execution`, or `forex_bot.loops` (structural unit
  tests enforce this).
- The exporter never uses `random.random()`, `numpy.random.*`, or
  Python's built-in `hash()`. Determinism comes from SHA-256 in
  the strategy module.
- The exporter never prints credentials. `RiskEngine` is not
  instantiated; no broker credentials are read.
- The reference's `risk_engine_used` field is **always** `false`
  (it is a constant in the writer). Any future caller who attempts
  to flip this is committing a contract violation.

## 7. Validation

```bash
python -m pytest tests/unit/test_export_campaign_011_norisk_reference.py -q
ruff check scripts/export_campaign_011_norisk_reference.py
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

## 8. What this runner does **not** do

- It does **not** approve any strategy.
- It does **not** change any of the existing CAMPAIGN_011 artefacts
  under `backtests/CAMPAIGN_011_random_entry_anchor/`.
- It does **not** run the financing-overlay or portfolio-risk
  diagnostics — those are separate scripts and remain untouched.
- It does **not** run the Backtrader lane.
- It does **not** produce strategy evidence.
- It does **not** signal any verdict change. CAMPAIGN_011 remains
  REJECT / null diagnostic anchor by design.

`strategy_evidence: false`. Paper / demo / live remain blocked.
