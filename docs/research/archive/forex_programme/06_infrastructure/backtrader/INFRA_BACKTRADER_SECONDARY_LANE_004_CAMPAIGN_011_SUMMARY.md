# Sprint summary — `infra-backtrader-secondary-lane-004-campaign-011`

**Date:** 2026-05-25
**Branch:** `infra-backtrader-secondary-lane-004-campaign-011`
**Sprint type:** infrastructure / parity verification
**`strategy_evidence: false`**

> Ports CAMPAIGN_011 / `random_entry_anchor 0.1.0-c011` into the
> Backtrader secondary lane and compares against the no-RiskEngine
> bespoke reference produced by the previous sprint. After two BT-lane
> fidelity fixes, the full-window comparison reaches **trade-for-trade
> PASS** on all 7 pairs (2 800/2 800). **No strategy approved.**
> CAMPAIGN_011 remains REJECT / null diagnostic anchor by design.
> `configs/approved_strategies.yaml` remains `approved: []`. Paper /
> demo / live remain blocked. **No OANDA API call was made.**

## 1. What this sprint produced

| artefact | path | role |
|---|---|---|
| BT-lane adapter | `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` | implements R1-R8 byte-for-byte against the bespoke strategy; deterministic SHA-256 seed; reuses CAMPAIGN_002 helpers |
| Registry update | `research/backtrader_lane/strategies/__init__.py` | side-effect import to register the new adapter |
| 32 adapter tests | `tests/unit/backtrader_lane/test_campaign_011_adapter.py` | seed parity, frozen-parameter contract, AST-grep safety guards, synthetic-fixture integration, warmup regression |
| 9 comparison fixture tests | `tests/unit/backtrader_lane/test_compare_campaign_011.py` | exact-match PASS, drift mismatches, missing reference, blocked-instrument propagation |
| Phase 0 plan | `docs/research/BACKTRADER_CAMPAIGN_011_004_PLAN.md` | sprint plan + non-goals + reference artefact paths + safety invariants |
| Phase 3 run doc (pre-fix) | `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_RUN_004.md` | initial 2 808-trade BT run; per-pair Δ; determinism check |
| Phase 4 comparison doc (pre-fix) | `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md` | harness TOLERABLE_DRIFT / sprint-plan SIGNAL_RULE_MISMATCH; ruled-out alternatives; root cause |
| Phase 5 fix doc | `docs/research/BACKTRADER_CAMPAIGN_011_FIDELITY_FIX_004.md` | two BT-lane bugs fixed; trade-for-trade PASS post-fix; determinism re-confirmed |
| Phase 6 defer doc | `docs/research/BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md` | per-fold not run; design constraints for a future sprint pinned |
| Pre-fix diagnostics (committed) | `backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix/` | small JSON + MD comparison summary |
| Post-fix diagnostics (committed) | `backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix/` | small JSON + MD comparison summary |

## 2. Commits by phase

| phase | commit | description |
|---|---|---|
| 0 — plan | `532d37a` | `BACKTRADER_CAMPAIGN_011_004_PLAN.md` |
| 1 — BT adapter | `0edfa48` | adapter + 31 tests; registry wired |
| 2 — runner/comparison coverage | `0749739` | 9 comparison fixture tests; no harness change needed |
| 3 — full-window run (pre-fix) | `de110be` | initial BT run; +8 trades Δ; determinism PASS |
| 4 — comparison (pre-fix) | `ff0da86` | harness TOLERABLE_DRIFT; sprint-plan label SIGNAL_RULE_MISMATCH; root cause identified |
| 5 — fidelity fixes | `4cb1a18` | warmup off-by-N (-7) + same-bar EOD re-entry (-1); trade-for-trade PASS |
| 6 — per-fold deferred | `67ff722` | `BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md` |
| 7 — sprint summary (this commit) | `<TBC>` | summary + EVIDENCE updates |

## 3. Files changed by phase

### Phase 0 — `532d37a`

- `docs/research/BACKTRADER_CAMPAIGN_011_004_PLAN.md` (new)

### Phase 1 — `0edfa48`

- `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` (new, ~545 lines)
- `tests/unit/backtrader_lane/test_campaign_011_adapter.py` (new, 31 tests)
- `research/backtrader_lane/strategies/__init__.py` (+1 import line)

### Phase 2 — `0749739`

- `tests/unit/backtrader_lane/test_compare_campaign_011.py` (new, 9 tests)

### Phase 3 — `de110be`

- `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_RUN_004.md` (new)

### Phase 4 — `ff0da86`

- `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md` (new)
- `backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix/comparison_summary.json` (new, ~4.7 KB)
- `backtests/diagnostics/backtrader_campaign_011_full_window_004_prefix/comparison_summary.md` (new, ~1.9 KB)

### Phase 5 — `4cb1a18`

- `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` (two fixes: warmup constants + drop in-loop EOD)
- `tests/unit/backtrader_lane/test_campaign_011_adapter.py` (+1 regression test)
- `docs/research/BACKTRADER_CAMPAIGN_011_FIDELITY_FIX_004.md` (new)
- `backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix/comparison_summary.json` (new, small)
- `backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix/comparison_summary.md` (new, small)

### Phase 6 — `67ff722`

- `docs/research/BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md` (new)

### Phase 7 — this commit

- `docs/research/INFRA_BACKTRADER_SECONDARY_LANE_004_CAMPAIGN_011_SUMMARY.md` (new)
- `docs/research/EVIDENCE_INDEX.md` (sprint section + 6 doc links)
- `docs/research/EVIDENCE_MANIFEST.json` (+6 diagnostic-artifact entries; branch + generated date bumped)

## 4. Reference artifacts used

| artefact | path | sha256 |
|---|---|---|
| Full-window canonical reference | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | `fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78` |
| Per-fold informational rollup | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | `a5a2a7088375162ef21400f2a136de8ca2bf85c694aee7626fb8696d7c8fef5e` |
| Walk-forward plan | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` | (committed; unchanged) |
| Frozen strategy module | `src/forex_bot/strategies/random_entry_anchor.py` | unchanged |
| Frozen strategy config | `configs/campaign_011_random_entry_anchor.yaml` | unchanged |
| Handoff doc (sprint 001 of `infra-bespoke-...`) | `docs/research/BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md` | unchanged |

## 5. Data source

- **Local CSVs only:** `research/lean_parity/exports/campaign_002_h4/<PAIR>_H4_lean.csv` (gitignored bulk; committed `*.provenance.json` sidecars sha256-verified on every load via `research/backtrader_lane/data_adapter.py`).
- Sprint 003 regenerated the 7 CSVs from `data/campaign_002.sqlite3`; their sha256 matches committed provenance bit-for-bit (`BACKTRADER_REAL_DATA_PREFLIGHT_003.md`).
- No OANDA API call. No credentials touched.

## 6. OANDA / API usage

**None.** All data came from the gitignored local CSV export.

## 7. CAMPAIGN_011 Backtrader full-window run status

| field | pre-fix | post-fix |
|---|---|---|
| BT total trades | 2 808 | **2 800** |
| Bespoke total trades | 2 800 | 2 800 |
| Δ | +8 | **0** |
| Determinism (two consecutive runs) | sha256 match | sha256 match |
| Backtrader version | 1.9.78.123 | 1.9.78.123 |

## 8. CAMPAIGN_011 full-window comparison status

| dimension | pre-fix | post-fix |
|---|---|---|
| Per-pair trade-count exact match | 1 of 7 (AUD_USD only) | **7 of 7** |
| Per-pair classification | 1 PASS, 6 TOLERABLE_DRIFT | **7 PASS** |
| Overall harness classification | TOLERABLE_DRIFT | **PASS** |
| Total trades match | -8 from bespoke | **0** |
| Match by `(instrument, entry_time, side)` | 2 800 / 2 808 | **2 800 / 2 800** |

## 9. Divergence classification (final)

**`PASS`** on the full-window comparison under tight CAMPAIGN_011
tolerances (trade count exact, expectancy R ≤ 0.005, return % ≤ 0.10,
win rate ≤ 0.0010). Every pair PASS.

(Pre-fix classification, preserved in Phase 4 doc: harness verdict
`TOLERABLE_DRIFT`; sprint-plan binding label `SIGNAL_RULE_MISMATCH`
from the warmup-window mismatch.)

## 10. Backtrader-lane bugs fixed

**Two**, both in the new CAMPAIGN_011 adapter.

### 10.1 Warmup off-by-N (-7 trades on fix)

The BT adapter respected only R1's in-strategy
`len(df) >= atr_lookback + 2 = 16` check. The bespoke engine respects
`strategy.warmup_bars_required() = 32` declared at
`src/forex_bot/strategies/random_entry_anchor.py:99-101`. Bars 16-31
were eligible for BT but skipped by the bespoke engine.

**Fix:** new module constants
`WARMUP_BARS_REQUIRED = 32` + `WARMUP_BAR_COUNT_THRESHOLD = 33` (1-based
BT `len(self)`). The R1 guard now reads
`if _bar_count(self) < WARMUP_BAR_COUNT_THRESHOLD: return`. A new
regression test imports the bespoke
`RandomEntryAnchorStrategy().warmup_bars_required()` and asserts both
sides agree.

### 10.2 Same-bar EOD re-entry on final bar (-1 trade on fix)

`_try_exit()` had a priority-3 case closing any open trade INSIDE the
per-bar loop with `exit_reason="eod"`. After that close, `next()` ran
`_try_entry()` since `_in_position` was now False — and if the SHA-256
gate fired on the final bar, the adapter opened a new trade,
immediately closed by `stop()` with `bars_held=0`. The bespoke engine
closes open trades **post-loop** at
`src/forex_bot/backtesting/engine.py:646-683`, never giving the
strategy a chance to fire a fresh entry on the very last bar.

**Fix:** drop the priority-3 EOD case from `_try_exit()`. The `stop()`
method (Backtrader's after-the-last-bar hook) already handles EOD
cleanly, matching the bespoke post-loop close.

USD_CAD's last bar (`2026-05-19T21:00:00+00:00`) was the trigger:
SHA-256 gate value 0.029 < 0.05, side=short. BT recorded an extra
trade there pre-fix; bespoke skipped it because it was still in
position from the previous bar.

The CAMPAIGN_002 BT adapter
(`research/backtrader_lane/strategies/campaign_002_trend_following.py`)
contains the same structural pattern but does not manifest because
the trend-following signal almost never fires on a final bar. Documented
as a dormant follow-up; **the CAMPAIGN_002 adapter was deliberately
not touched** to preserve sprint scope discipline.

## 11. Bespoke-engine bugs found

**None.** The bespoke engine respects `strategy.warmup_bars_required()`
correctly (`engine.py:204`) and closes open trades post-loop
correctly (`engine.py:646-683`). Both are doing what they document.

## 12. Per-fold status

**Deferred.** A clean per-fold BT-vs-bespoke comparison requires
extending the BT-lane runner with per-fold windowing (the bespoke
per-fold rollup was generated by 56 separate runs with independent
warmup, not a post-hoc slice of the full-window run). Out of scope
for this sprint per the plan §6. Recommended next branch if needed:
`infra-backtrader-secondary-lane-005-fold-plan-support`.

The full-window PASS is the canonical target; per-fold is
informational per
`docs/research/BACKTRADER_CAMPAIGN_011_HANDOFF_FROM_NORISK_REFERENCE.md`
§6.

## 13. Deterministic repeat status

| check | result |
|---|---|
| Bespoke reference reproducibility | sha256 `fba55057...` matched on two consecutive `--full-window-only` runs (verified in sprint 001 of `infra-bespoke-campaign-011-norisk-reference-*`) |
| Pre-fix BT determinism | sha256 `59b71907...` on `backtrader_summary.json` (two runs identical) |
| Post-fix BT determinism | sha256 `26d078da...` on `backtrader_summary.json` (two runs identical) |
| Post-fix BT trade JSONL determinism | sha256 `86f0e03b...` on `backtrader_trades.jsonl` (two runs identical) |

Determinism on both sides: **PASS**.

## 14. Tests and validation commands

### 14.1 New tests added

- 31 adapter tests in `tests/unit/backtrader_lane/test_campaign_011_adapter.py` (Phase 1)
- 9 comparison-harness fixture tests in `tests/unit/backtrader_lane/test_compare_campaign_011.py` (Phase 2)
- 1 warmup-threshold regression test in `tests/unit/backtrader_lane/test_campaign_011_adapter.py` (Phase 5)
- **Total: +41 new tests on this branch**

### 14.2 Final validation suite (Phase 7 — see §16)

```bash
python -m pytest -q                              # 1245 passed
python -m pytest tests/unit/backtrader_lane -q   # 118 passed (77 prior + 41 new)
ruff check src tests scripts research/backtrader_lane
python scripts/check_research_freeze.py          # PASS
python scripts/validate_research_archive.py      # PASS
python scripts/scan_artifacts_for_secrets.py     # PASS
```

### 14.3 Run / compare commands

```bash
# Full-window BT run
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_011 \
    --output research/backtrader_lane/results/campaign_011_full_window_004_postfix

# Comparison with tight CAMPAIGN_011 tolerances
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_011 \
    --backtrader-results research/backtrader_lane/results/campaign_011_full_window_004_postfix/ \
    --bespoke-reference research/lean_parity/campaign_011_h4_bespoke_reference.json \
    --output backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix \
    --trade-count-tolerance-pct 0.0 \
    --expectancy-r-tolerance 0.005 \
    --return-pct-tolerance 0.10 \
    --win-rate-tolerance 0.001
# Overall classification: PASS
```

## 15. No strategy is approved

`configs/approved_strategies.yaml` is byte-identical to `main`:
`approved: []`. Strategy module (`src/forex_bot/strategies/random_entry_anchor.py`),
strategy config (`configs/campaign_011_random_entry_anchor.yaml`),
bespoke engine (`src/forex_bot/backtesting/engine.py`), bespoke
reference JSONs (`research/lean_parity/campaign_011_h4_bespoke_reference*.json`),
existing CAMPAIGN_011 walk-forward artefacts
(`backtests/CAMPAIGN_011_random_entry_anchor/`), and the CAMPAIGN_002
BT adapter are all **byte-identical to `main`**.

## 16. CAMPAIGN_011 remains REJECT / null diagnostic anchor

Yes — and the BT lane now corroborates that REJECT verdict at
trade-for-trade precision. The full-window PASS does **not** approve
CAMPAIGN_011; it confirms that two engines independently produce the
same trades for the frozen rules, and the rules produce a null-model
outcome.

## 17. Paper / demo / live remain blocked

Yes. Freeze gate confirms:
`paper-loop refuses ['trend_following'] — frozen`,
`demo-loop refuses ['trend_following'] — frozen`.

## 18. No credentials / secrets / data files committed

`scan_artifacts_for_secrets.py` PASS over committed artefact files.
No `.env`, no `*.sqlite3`, no bulk CSV, no raw trade dump (the BT
runner's gitignored output dir is `research/backtrader_lane/results/`;
raw trade JSONL outputs lived only there and in `/tmp/`).

## 19. Local generated files NOT committed

| file | location | committed | reason |
|---|---|---|---|
| `data/campaign_002.sqlite3` | main repo `data/` | no | gitignored (`*.sqlite3`); 115 MB |
| H4 CSVs | `research/lean_parity/exports/campaign_002_h4/` | no | gitignored bulk; sha256-verified against committed provenance |
| `research/backtrader_lane/results/campaign_011_full_window_004/` (pre-fix run) | repo | no | gitignored by sprint 001 (`research/backtrader_lane/results/`) |
| `research/backtrader_lane/results/campaign_011_full_window_004_postfix/` | repo | no | gitignored |
| `backtests/diagnostics/campaign_011_norisk/full_window_trades.jsonl` (bespoke trade dump for diff) | repo | no | gitignored by sprint 001 of `infra-bespoke-campaign-011-norisk-reference-*` |
| `/tmp/c011_*` scratch dirs | `/tmp/` | no | scratch |

Only small comparison summary JSONs + MDs were committed under
`backtests/diagnostics/backtrader_campaign_011_full_window_004_{prefix,postfix}/`.

## 20. Files to review first

For fastest comprehension:

1. `docs/research/BACKTRADER_CAMPAIGN_011_004_PLAN.md` — the sprint plan + non-goals.
2. `docs/research/BACKTRADER_CAMPAIGN_011_FULL_WINDOW_COMPARISON_004.md` + `BACKTRADER_CAMPAIGN_011_FIDELITY_FIX_004.md` — the load-bearing finding (warmup + EOD bugs) and fixes.
3. `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` — the BT adapter.
4. `tests/unit/backtrader_lane/test_campaign_011_adapter.py` — the 32 adapter tests including the SHA-256 parity tests and the warmup-threshold regression.
5. `backtests/diagnostics/backtrader_campaign_011_full_window_004_postfix/comparison_summary.md` — the final PASS verdict.
6. `docs/research/BACKTRADER_CAMPAIGN_011_PER_FOLD_DEFERRED_004.md` — explains why per-fold is deferred and what a future sprint would need.

## 21. Recommended next branch

Two reasonable options depending on intent:

| intent | recommended next branch |
|---|---|
| Add per-fold CAMPAIGN_011 comparison support | `infra-backtrader-secondary-lane-005-fold-plan-support` |
| Harden the CAMPAIGN_002 BT adapter's in-loop EOD pattern (dormant bug documented in Phase 5 §6) | `infra-backtrader-secondary-lane-005-eod-cleanup` |

If neither is a priority, the BT-lane sprint sequence can pause here —
the load-bearing infrastructure for CAMPAIGN_002 (sprint 003) and
CAMPAIGN_011 (this sprint) is complete and PASS.

`strategy_evidence: false`. CAMPAIGN_011 remains REJECT / null
diagnostic anchor by design. Paper / demo / live remain blocked.
