# Sprint summary — `infra-bespoke-campaign-011-norisk-reference-001`

**Date:** 2026-05-25
**Branch:** `infra-bespoke-campaign-011-norisk-reference-001`
**Sprint type:** infrastructure / reference-artefact generation
**`strategy_evidence: false`**

> Produces the canonical no-RiskEngine bespoke reference for
> CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` so the future
> Backtrader CAMPAIGN_011 sprint has a clean apples-to-apples
> comparison target. **No strategy was approved.** CAMPAIGN_011
> remains REJECT / null diagnostic anchor by design.
> `configs/approved_strategies.yaml` remains `approved: []`.
> Paper / demo / live remain blocked. **No OANDA API call was made.**

## 1. What this sprint produced

| artefact | path | size | role |
|---|---|---|---|
| Canonical full-window reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | 2.4 KB | the Backtrader-vs-bespoke comparison target |
| Informational per-fold rollup JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | 13.8 KB | sanity check vs the published walk-forward plan |
| Diagnostics MD | `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | 2.3 KB | human-readable parity-style summary |
| Exporter script | `scripts/export_campaign_011_norisk_reference.py` | new | the runner; deterministic; fail-loud on frozen-parameter drift |
| 23 unit tests | `tests/unit/test_export_campaign_011_norisk_reference.py` | new | covers helpers, schema, fail-loud paths, safety invariants |
| 6 doc files under `docs/research/` | see §3 | — | plan, contract, runner, result, handoff, this summary |
| `.gitignore` rule | `.gitignore` | +5 lines | `backtests/diagnostics/campaign_011_norisk/` for optional raw trade dumps |
| `EVIDENCE_INDEX.md` + `EVIDENCE_MANIFEST.json` updates | `docs/research/...` | — | 7 new diagnostic-artifact entries under `parity_reproduction` kind |

**Full-window summary:** 2 800 trades across 7 pairs, window
`2020-01-01` → `2026-05-20`, `risk_engine_used=false`,
`master_seed=20260523`, `fill_timing=signal_bar_close`.

**Per-fold rollup:** 1 661 trades across 8 rolling-plan test
windows (≈41 % more than the published with-RiskEngine
walk-forward's 1 177, confirming the spread / session / loss-limit
gates are silenced as intended).

**Determinism:** two consecutive `--full-window-only` runs
produced bit-identical JSON output (sha256
`fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78`).

## 2. Commits by phase

| phase | commit | description |
|---|---|---|
| 0 — plan | `7e3d6a8` | `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md` |
| 1 — contract | `2411cad` | `CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` |
| 2 — runner | `09cb028` | exporter + tests + runner doc + `.gitignore` |
| 3 — generate | `df2007f` | reference JSONs + diagnostics MD + result doc |
| 4 — handoff | `3836af5` | `BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md` |
| 5 — summary (this commit) | `<TBC after commit>` | summary + evidence-index + manifest |

## 3. Files changed by phase

### Phase 0 — `7e3d6a8`

- `docs/research/CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md` (new)

### Phase 1 — `2411cad`

- `docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` (new)

### Phase 2 — `09cb028`

- `scripts/export_campaign_011_norisk_reference.py` (new, 489 lines)
- `tests/unit/test_export_campaign_011_norisk_reference.py` (new, 23 tests)
- `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md` (new)
- `.gitignore` (+5 lines for `backtests/diagnostics/campaign_011_norisk/`)
- `docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` (tweak: contract budget for per-fold JSON 12 KB → 16 KB)

### Phase 3 — `df2007f`

- `research/lean_parity/campaign_011_h4_bespoke_reference.json` (new, 2.4 KB)
- `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` (new, 13.8 KB)
- `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` (new, 2.3 KB)
- `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` (new)
- `docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` (per-fold budget bump)

### Phase 4 — `3836af5`

- `docs/research/BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md` (new)

### Phase 5 — (this commit)

- `docs/research/INFRA_BESPOKE_CAMPAIGN_011_NORISK_REFERENCE_001_SUMMARY.md` (new)
- `docs/research/EVIDENCE_INDEX.md` (new sprint section)
- `docs/research/EVIDENCE_MANIFEST.json` (+7 diagnostic-artifact entries; branch + generated date bumped)

## 4. Data source

- **Local SQLite only:** `/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3`
  (115 MB, gitignored; lives in the main repo working directory, reachable
  from the worktree because git worktrees do not isolate the host
  filesystem above `.git/worktrees/...`).
- The 7 H4 series under that DB are the same series the existing
  CAMPAIGN_011 walk-forward artefacts were generated against, per
  `configs/campaign_011_random_entry_anchor.yaml:44`.
- Data source label `oanda-practice` verified by
  `DataSourceRepo.latest_for(<pair>, "H4")` for every pair before
  the engine runs.

## 5. OANDA / API usage

**None.** No OANDA API call was made in any phase. No credentials
were sourced. The exporter reads `data/campaign_002.sqlite3` only.
The artefact secret-scanner confirmed no credential-shaped strings
in committed artefacts after Phase 5.

## 6. Reference outputs created

| output | path | committed | sha256 |
|---|---|---|---|
| Full-window reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | yes | `fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78` |
| Per-fold rollup JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | yes | `a5a2a7088375162ef21400f2a136de8ca2bf85c694aee7626fb8696d7c8fef5e` |
| Diagnostics MD | `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | yes | (not signed; small human-readable summary) |

## 7. Full-window / per-fold status

| dimension | value |
|---|---|
| Full-window status | **PRODUCED** — `2020-01-01..2026-05-20`, 2 800 trades, deterministic |
| Per-fold status | **PRODUCED** — 8 folds × 7 pairs, 1 661 trades, deterministic |
| Train / validation windows | **not run** (not part of CAMPAIGN_011's published evidence) |

## 8. Total / per-pair / per-fold trade counts

### 8.1 Full-window per-pair (the canonical comparison target)

| instrument | trades | expectancy R | return % |
|---|---|---|---|
| EUR_USD | 394 | -0.0496 | -4.83 |
| GBP_USD | 400 | -0.0073 | -0.80 |
| USD_JPY | 418 | +0.0004 | +5.90 |
| AUD_USD | 385 | -0.0646 | -6.08 |
| USD_CAD | 394 | -0.0161 | -2.02 |
| USD_CHF | 409 | +0.0503 | +4.77 |
| NZD_USD | 400 | -0.0265 | -2.67 |
| **total** | **2 800** | aggregate negative | aggregate negative |

USD_JPY and USD_CHF show positive full-window expectancy. This is
expected null-model fluctuation across 7 pairs × 6.5 years × random
5 %-per-bar entry; the original CAMPAIGN_011 with-RiskEngine
walk-forward also produced positive aggregate folds (e.g. folds 5,
6). It is **not** evidence of an edge; CAMPAIGN_011 is a null model
by construction.

### 8.2 Per-fold aggregates

| fold | test window | trades | expectancy R | return % |
|---|---|---|---|---|
| 0 | 2021-12-21..2022-06-18 | 214 | -0.0398 | -1.93 |
| 1 | 2022-06-19..2022-12-15 | 230 | -0.0037 | +1.36 |
| 2 | 2022-12-16..2023-06-13 | 206 | -0.0072 | +1.84 |
| 3 | 2023-06-14..2023-12-10 | 192 | +0.0010 | -0.34 |
| 4 | 2023-12-11..2024-06-07 | 216 | -0.0153 | -0.72 |
| 5 | 2024-06-08..2024-12-04 | 211 | +0.0219 | +1.02 |
| 6 | 2024-12-05..2025-06-02 | 188 | +0.0389 | +0.79 |
| 7 | 2025-06-03..2025-11-29 | 204 | +0.0066 | +0.35 |
| **total** | — | **1 661** | — | — |

## 9. Deterministic seed / repeat status

| check | result |
|---|---|
| `master_seed = 20260523` | frozen, verified pre-run by `_assert_frozen(...)` |
| Random source | SHA-256 in `_derive_random_pair(...)` only |
| `random.random()` / `numpy.random.*` / `hash()` in the exporter | **none** (structurally guarded by `test_exporter_module_does_not_use_random_or_numpy_random`) |
| Two consecutive `--full-window-only` runs sha256-identical | **PASS** (`fba55057...` matched) |
| Committed JSON matches re-run output bit-for-bit | **PASS** |

## 10. Tests and validation commands

### 10.1 Targeted new tests (Phase 2 added 23 tests)

```bash
python -m pytest tests/unit/test_export_campaign_011_norisk_reference.py -q
# 23 passed
```

### 10.2 Full validation suite (Phase 5 final pass — see §13)

```bash
python -m pytest -q                              # 1204 passed
ruff check src tests scripts research/backtrader_lane
python scripts/check_research_freeze.py          # PASS
python scripts/validate_research_archive.py      # PASS
python scripts/scan_artifacts_for_secrets.py     # PASS
```

### 10.3 Determinism check

```bash
python scripts/export_campaign_011_norisk_reference.py \
    --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 \
    --out /tmp/c011_a.json --diagnostics-md /tmp/c011_a.md \
    --full-window-only
python scripts/export_campaign_011_norisk_reference.py \
    --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 \
    --out /tmp/c011_b.json --diagnostics-md /tmp/c011_b.md \
    --full-window-only
shasum -a 256 /tmp/c011_a.json /tmp/c011_b.json \
    research/lean_parity/campaign_011_h4_bespoke_reference.json
# All three hashes identical: fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78
```

## 11. No strategy approved

`configs/approved_strategies.yaml` is byte-identical to `main`:
`approved: []`. No new entry was added.
`src/forex_bot/strategies/random_entry_anchor.py` is byte-identical
to `main`. `configs/campaign_011_random_entry_anchor.yaml` is
byte-identical to `main`. The bespoke engine
`src/forex_bot/backtesting/engine.py` is byte-identical to `main`.
Existing CAMPAIGN_011 walk-forward / fold / financing / risk
artefacts under `backtests/CAMPAIGN_011_random_entry_anchor/` are
byte-identical to `main`.

## 12. CAMPAIGN_011 verdict — unchanged

CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
This sprint produces the missing no-RiskEngine bespoke reference;
it does **not** approve any strategy, does **not** tune any
parameter, does **not** change the CAMPAIGN_011 rules, and does
**not** mutate any existing artefact under
`backtests/CAMPAIGN_011_random_entry_anchor/`.

CAMPAIGN_011 cannot be added to `configs/approved_strategies.yaml`
under any circumstance per
`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §2 (null model by design;
"approval path: none").

## 13. Paper / demo / live blocked — unchanged

`paper-loop` and `demo-loop` continue to refuse to start because
`configs/approved_strategies.yaml` is `approved: []`. The freeze
gate confirms:

```
[PASS] loops_refuse
       paper-loop refuses ['trend_following'] — frozen
       demo-loop refuses ['trend_following'] — frozen
research freeze gate: ALL CHECKS PASSED
```

## 14. No credentials / secrets / data files committed

`scan_artifacts_for_secrets.py` PASS over 3 076 committed files in
`docs/`, `backtests/`, `research/`, `configs/`, `scripts/`. No
credential value, no credential-shaped string. No `.env`, no
SQLite, no bulk CSV, no raw trade dump was staged or committed.
`git ls-files` confirms only small committed artefacts (≤ 16 KB
each).

## 15. Local generated files NOT committed

| file | location | committed | reason |
|---|---|---|---|
| `data/campaign_002.sqlite3` | main repo `data/` | no | gitignored (`*.sqlite3`); 115 MB |
| `/tmp/c011_a.json`, `/tmp/c011_b.json` | `/tmp/` | no | determinism-check scratch |
| `/tmp/c011_a.md`, `/tmp/c011_b.md` | `/tmp/` | no | determinism-check scratch |
| Optional raw trade dumps (if any) | `backtests/diagnostics/campaign_011_norisk/` | no | gitignored by Phase 2 commit |

`backtests/diagnostics/campaign_011_norisk/` does not exist on
disk (no opt-in `--trades-out` was passed during Phase 3 — kept
artefact set small and clean).

## 16. Files to review first

For a reviewer who wants the fastest comprehension path:

1. `docs/research/CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md` — the
   sprint plan + non-goals (the "why" + "what we deliberately did
   NOT do").
2. `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` — the
   numbers, determinism check, and the per-fold-vs-with-RiskEngine
   diff.
3. `research/lean_parity/campaign_011_h4_bespoke_reference.json` —
   the canonical artefact itself (2.4 KB, sorted-key JSON).
4. `scripts/export_campaign_011_norisk_reference.py` — the runner
   (deterministic, frozen-parameter enforcement at the top).
5. `tests/unit/test_export_campaign_011_norisk_reference.py` — the
   23 safety-invariant tests, including the static-grep guards
   against random / numpy / broker imports.
6. `docs/research/BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md` —
   the hand-off doc telling the next sprint exactly what to do
   with the reference.

## 17. Recommended next branch

```
infra-backtrader-secondary-lane-004-campaign-011
```

This is the Backtrader CAMPAIGN_011 port sprint. Its work is fully
described in
`BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md` §10,
including:

- The full-window reference is the primary comparison target.
- The CAMPAIGN_002 BT adapter
  (`research/backtrader_lane/strategies/campaign_002_trend_following.py`)
  is the structural template; only the entry / exit logic needs
  to change (EMA/Donchian → R1–R8 with SHA-256 seed).
- The sprint-003 R-formula fix is binding — do **not** introduce
  a `risk_distance / exit_price` conversion for USD-base pairs.
- The expected approximation flags are
  `CAMPAIGN_011_DETERMINISTIC_SEED`, `CAMPAIGN_011_TIME_STOP_ONLY`,
  `CAMPAIGN_011_NO_RISK_ENGINE_PARITY`, `R_FORMULA_MATCHES_BESPOKE`.

`strategy_evidence: false`. CAMPAIGN_011 remains REJECT / null
diagnostic anchor by design. Paper / demo / live remain blocked.
