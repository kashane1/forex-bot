# Backtrader CAMPAIGN_015 — Provenance Repair Infra Sprint 001 — Summary

**Branch:** `infra-backtrader-campaign-015-provenance-repair-001`
**Date:** 2026-05-26
**Sprint kind:** infrastructure — NOT strategy, tuning, or promotion.
**Final sprint label:** **`BT_DIVERGENCE_NEEDS_DEBUG`**
**Approval status (unchanged):** `NOT_APPROVED`. `configs/approved_strategies.yaml`
is and remains `approved: []`. Paper / demo / live remain blocked.

---

## 1 · Commits by phase

| phase | sha | what landed |
|---|---|---|
| 0 | `4d559e6` | Truth audit + sprint plan |
| 1 | `4277d90` | CSV/provenance mismatch diagnostic script + 8 tests + report |
| 2 | `f93c511` | Re-export CSVs + provenance lock-step (tz-determinism fix + dedupe) |
| 3 | `bbe818b` | BT preflight passes for all 7 instruments |
| 4 | `02e8951` | BT vs bespoke comparison = `TIMESTAMP_MISMATCH` |
| 5 | `60eb5d9` | Interpretation + next-step decision = `BT_DIVERGENCE_NEEDS_DEBUG` |
| 6 | this commit | Final validation + this summary |

---

## 2 · Files changed (new / modified by this sprint)

### Docs (`docs/research/`)
- `BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md` — sprint plan
- `BACKTRADER_CAMPAIGN_015_PROVENANCE_MISMATCH.md` — Phase 1 mismatch report
- `BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RE_EXPORT.md` — Phase 2 re-export doc
- `BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md` — Phase 3 preflight doc
- `BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md` — Phase 4 comparison doc (clearly-labeled addition; prior `BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md` left untouched)
- `BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RESULT.md` — Phase 5 decision doc
- `BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_SUMMARY.md` (this file)

### Scripts (`scripts/`)
- `diagnose_backtrader_csv_provenance.py` — new diagnostic
- `build_lean_parity_export_manifest.py` — new manifest builder
- `build_campaign_015_bespoke_reference.py` — new reference builder
- `export_lean_parity_data.py` — **modified**: candle/provenance timestamps now normalised to UTC; CSV de-duplicated by UTC timestamp (deterministic + monotonic for BT lane)

### Tests (`tests/unit/`)
- `test_diagnose_backtrader_csv_provenance.py` — 8 tests (all pass)

### Machine-readable artifacts (`research/`)
- `research/lean_parity/exports/campaign_002_h4/*.provenance.json` — re-generated, lock-step with current CSVs
- `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.json` — new consolidated manifest
- `research/campaign_015/diagnostics/backtrader_provenance_mismatch.{json,md}` — status went from "complete drift" to "ALL BT-STRICT PREFLIGHT PASS"
- `research/campaign_015/diagnostics/backtrader_lane/` — BT run outputs + compare-harness outputs
- `research/campaign_015/diagnostics/campaign_015_bespoke_reference.json` — per-pair bespoke reference

### Files NOT modified (verified)
- `configs/approved_strategies.yaml` — `approved: []`
- `scripts/run_campaign_015.py` — bespoke runner, untouched
- `research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py` — BT adapter, untouched
- `research/anti_overfit/campaign_015.py` — classifier, untouched
- All prior CAMPAIGN_015 / BACKTRADER_CAMPAIGN_015 docs — left untouched (new docs are clearly-labeled additions)
- All prior backtests/CAMPAIGN_011_* artifacts — read-only consumed

---

## 3 · Commands run

Validation (Phase 0 and Phase 6):
```bash
pytest tests/ -q                              # 1460 passed
ruff check src tests scripts research         # 3 pre-existing findings only
python scripts/check_research_freeze.py       # ALL CHECKS PASSED
python scripts/validate_research_archive.py   # ALL CHECKS PASSED
python scripts/scan_artifacts_for_secrets.py  # PASSED
git status --short                            # clean
```

Provenance diagnostic (Phase 1 and after Phase 2):
```bash
python scripts/diagnose_backtrader_csv_provenance.py \
  --exports-dir research/lean_parity/exports/campaign_002_h4 \
  --out-json    research/campaign_015/diagnostics/backtrader_provenance_mismatch.json \
  --out-md      research/campaign_015/diagnostics/backtrader_provenance_mismatch.md
# Phase 1 status: ALL BT-STRICT PREFLIGHT FAIL (complete drift)
# After Phase 2 status: ALL BT-STRICT PREFLIGHT PASS
```

Re-export + manifest (Phase 2):
```bash
for pair in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  python scripts/export_lean_parity_data.py \
    --db data/campaign_002.sqlite3 \
    --instrument "$pair" \
    --from 2020-01-01 --to 2026-05-20 \
    --out-dir research/lean_parity/exports/campaign_002_h4
done
python scripts/build_lean_parity_export_manifest.py
```

BT preflight + run + compare (Phases 3 / 4):
```bash
python scripts/run_backtrader_parity.py --campaign CAMPAIGN_015 --output research/campaign_015/diagnostics/backtrader_lane --dry-run
python scripts/run_backtrader_parity.py --campaign CAMPAIGN_015 --output research/campaign_015/diagnostics/backtrader_lane
python scripts/build_campaign_015_bespoke_reference.py \
  --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
  --out         research/campaign_015/diagnostics/campaign_015_bespoke_reference.json
python scripts/compare_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --backtrader-results research/campaign_015/diagnostics/backtrader_lane \
  --bespoke-reference  research/campaign_015/diagnostics/campaign_015_bespoke_reference.json \
  --output             research/campaign_015/diagnostics/backtrader_lane
```

---

## 4 · Provenance mismatch root cause

Two coupled causes:

1. **Timezone-determinism bug** in `scripts/export_lean_parity_data.py`.
   The script emitted `Candle.time.isoformat()` directly; on a machine
   whose local timezone is non-UTC, this leaked offsets like
   `-08:00` (PST) into the CSV `time` column. The row-sha256
   algorithm hashes the string representation, so the offset format
   alone drifted the sha vs the prior UTC-style sidecar.
2. **Lock-step missed**: a re-export on 2026-05-25 17:50 updated the
   CSVs but the `*.provenance.json` sidecars from 2026-05-22 were not
   re-committed.

Both fixed in Phase 2.

---

## 5 · Whether re-export / provenance repair passed

**PASS.** Phase 1 diagnostic post-repair reports `ALL BT-STRICT
PREFLIGHT PASS`. All 7 instruments now:

- have matching row-sha256 vs their `*.provenance.json` `data_sha256`,
- have matching row count vs the sidecar `candle_count`,
- have matching first / last timestamps,
- iterate monotonically in UTC.

---

## 6 · Backtrader preflight status

**PASS.** `scripts/run_backtrader_parity.py --campaign CAMPAIGN_015
--dry-run` reports `instruments_runnable = 7`, `instruments_blocked = 0`.

---

## 7 · Backtrader run status

**PASS-to-completion.** 575 total trades across 7 instruments, 9,933–
9,937 candles each, -51.43 account-currency total PnL. No errors,
no broker calls, no Lean / QuantConnect.

---

## 8 · Backtrader-vs-bespoke divergence classification

**`TIMESTAMP_MISMATCH`** (primary, this sprint).

- Compare harness auto-label: `SIGNAL_RULE_MISMATCH` (faithful to its
  inputs; trade-count delta > 10% on every pair).
- This sprint's binding classification: `TIMESTAMP_MISMATCH`, because
  BT iterates the whole ~6.4-year CSV while bespoke walks-forward
  through 8 × 180-day test windows (≈ 3.95 years of test coverage).
  Until the windows are aligned, any residual SIGNAL_RULE_MISMATCH
  cannot be isolated.
- Per-pair trade-count delta: +137% (GBP_USD) to +1,280% (NZD_USD).
  Window-coverage ratio (1.6×) accounts for some of the 3.5× gap;
  the remaining ~2.2× requires a windowed re-run to attribute.

See:
[BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md).

---

## 9 · Does CAMPAIGN_015 remain unapproved?

**Yes.** Strategy verdict is unchanged (REJECT). Diagnostic label from
the prior post-run sprint (`SPARSE_BUT_PROMISING` / `ROBUST_ABOVE_NULL`)
is unchanged. `configs/approved_strategies.yaml` is `approved: []`.

---

## 10 · Do paper / demo / live remain blocked?

**Yes.** All order-capable loops refuse to start. Confirmed by
`python scripts/check_research_freeze.py` (research freeze gate:
ALL CHECKS PASSED).

---

## 11 · Recommended next step

**Window-align the BT vs bespoke comparison** in a small infra sprint
*before* doing any further CAMPAIGN_015-derived research. Two options:

1. **BT-on-fold-windows**: extend the BT runner to accept a fold-window
   list and run BT eight times (one per bespoke test window), then
   aggregate. This is the closer-to-existing-infra option.
2. **Bespoke-full-window**: add a `--full-window` mode to
   `scripts/run_campaign_015.py` that bypasses the rolling walk-forward
   and runs once across the entire 2020-2026 universe. This would
   match what BT does.

After alignment, re-run the compare harness. If the divergence
collapses to `PASS` or `TOLERABLE_DRIFT`, the BT precondition is
satisfied and the next CAMPAIGN_015 research step can proceed (which
the prior sprint recommended as `COLLECT_MORE_DATA_FIRST` — i.e., an
extended-universe re-run of the frozen CAMPAIGN_015 config).

---

## 12 · Files to review first (recommended reading order)

1. [`BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RESULT.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RESULT.md) — the human-readable result.
2. [`BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md`](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md) — what BT vs bespoke shows now.
3. [`BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RE_EXPORT.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RE_EXPORT.md) — what changed in Phase 2.
4. [`BACKTRADER_CAMPAIGN_015_PROVENANCE_MISMATCH.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_MISMATCH.md) — root cause analysis.
5. [`BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md`](BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md) — Phase 3 preflight evidence.
6. [`BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md) — sprint plan.
7. [`BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_SUMMARY.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_SUMMARY.md) — this file.

---

## 13 · Safety statement (final)

- `configs/approved_strategies.yaml` is `approved: []`. ✓
- Paper / demo / live loops refuse to start. ✓
- Runner verdict for CAMPAIGN_015 is REJECT (NOT_APPROVED). ✓
- No CAMPAIGN_015 parameter has been tuned. ✓
- No pre-committed gate has been relaxed. ✓
- No broker call; no `.env`; no live OANDA; no Lean / QuantConnect. ✓
- Bespoke engine — untouched. ✓
- BT adapter strategy — untouched. ✓
- The `config_hash` for the rehydrate
  (`17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`)
  is unchanged. ✓
- No prior campaign evidence was modified (all new docs are clearly
  labeled additions). ✓
- The local sqlite + Lean-parity CSVs remain gitignored symlinks /
  bulk files in the main repo root; only the small provenance JSONs
  + the new manifest are committed. ✓
- `pytest tests/ -q` — `1460 passed`.
- `python scripts/check_research_freeze.py` — `research freeze gate: ALL CHECKS PASSED`.
- `python scripts/validate_research_archive.py` — `research archive: ALL CHECKS PASSED`.
- `python scripts/scan_artifacts_for_secrets.py` — `artifact secret scan: PASSED`.
- `ruff check src tests scripts research` — 3 pre-existing findings
  in `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (commit `e382af4`, unrelated); no new findings from this sprint.
