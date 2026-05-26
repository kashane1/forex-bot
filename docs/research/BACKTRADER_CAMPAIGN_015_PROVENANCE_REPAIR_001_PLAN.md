# Backtrader CAMPAIGN_015 — Provenance Repair Infra Sprint 001 — Plan

**Branch:** `infra-backtrader-campaign-015-provenance-repair-001`
**Sprint kind:** infrastructure — **NOT** strategy, tuning, or promotion.
**Date:** 2026-05-26

> Loading this plan does **not** approve any strategy. No paper / demo
> / live loop is enabled by this work. No broker call, no `.env`, no
> live OANDA, no QuantConnect. `configs/approved_strategies.yaml`
> remains `approved: []` and must remain `approved: []` at every phase
> commit.

---

## 1 · What this sprint is and is not

The prior CAMPAIGN_015 post-run diagnostics sprint
([`CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_SUMMARY.md`](CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_SUMMARY.md))
ran the bespoke walk-forward cleanly but found the Backtrader
secondary verification lane **BLOCKED** with divergence classification
`DATA_MISMATCH`: all 7 CSVs in
`research/lean_parity/exports/campaign_002_h4/` have row/raw sha drift
versus their committed `*.provenance.json` sidecars.

This sprint:

- **does** repair the local CSV / provenance lock-step (Phase 2),
- **does** run the Backtrader lane against CAMPAIGN_015 and compare
  to the bespoke rehydrate output (Phases 3 / 4),
- **does** classify divergence with the binding pre-commit label
  set (Phase 4),
- **does NOT** change CAMPAIGN_015 strategy parameters, frozen
  config, or any gate,
- **does NOT** add anything to `configs/approved_strategies.yaml`,
- **does NOT** enable paper / demo / live,
- **does NOT** modify the bespoke engine to force parity,
- **does NOT** call live OANDA or any other broker / cloud backtest.

If BT still diverges after the provenance repair, the divergence gets
documented honestly. The bespoke remains canonical.

---

## 2 · Observed root cause (Phase 0 audit)

- The provenance JSONs in `research/lean_parity/exports/campaign_002_h4/`
  carry `exported_at: 2026-05-22T20:38:19+00:00`. The matching CSV
  files in the main repo (gitignored, mtime `2026-05-25 17:07`) were
  re-exported on 25 May without re-committing the sidecars.
- Per the row-sha256 algorithm in
  `research.backtrader_lane.data_adapter.compute_csv_sha256`, all 7
  instrument CSVs row-hash to values that do NOT match the committed
  `data_sha256` (see Phase 1 diagnostic for the full table).
- The `research.backtrader_lane.data_adapter.load_candles` function
  correctly refuses to continue with `strict=True` (the default), so
  the CAMPAIGN_015 Backtrader runner fails at preflight.

The fix is **not** to disable strict provenance checking. It is to
re-export the 7 H4 CSVs together with fresh, matching provenance
sidecars from the same canonical SQLite store the bespoke lane uses,
and pin those into the repo (as small JSON sidecars; the CSVs remain
gitignored per repo convention).

Canonical source-of-truth DB for the CAMPAIGN_015 universe:
`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (133 MB,
gitignored; symlinked into the worktree as `data/campaign_002.sqlite3`).

---

## 3 · Phases

| phase | output | purpose |
|---|---|---|
| 0 | this plan | truth audit + sprint scaffold |
| 1 | `scripts/diagnose_backtrader_csv_provenance.py` + tests + `research/campaign_015/diagnostics/backtrader_provenance_mismatch.{json,md}` + [`BACKTRADER_CAMPAIGN_015_PROVENANCE_MISMATCH.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_MISMATCH.md) | document the exact mismatch on every instrument |
| 2 | re-exported CSVs + matching `*.provenance.json` (the small JSON sidecars committed; CSVs remain gitignored); `EXPORT_MANIFEST.json` if applicable; verification doc | restore lock-step |
| 3 | [`BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md`](BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md) | confirm the BT runner now loads all 7 CSVs |
| 4 | [`BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md) updated with real numbers + `research/campaign_015/diagnostics/backtrader_lane/` outputs | classify divergence with the binding label set |
| 5 | [`BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RESULT.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RESULT.md) | final BT_* label + next-step decision |
| 6 | [`BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_SUMMARY.md`](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_SUMMARY.md) | sprint summary + final validation |

A phase that lacks its inputs emits a clearly-labeled `BLOCKED`
diagnostic and does not invent results.

---

## 4 · Phase-4 binding divergence-label set (verbatim, from the pre-commit)

- `PASS`
- `TOLERABLE_DRIFT`
- `DATA_MISMATCH`
- `TIMESTAMP_MISMATCH`
- `SIGNAL_RULE_MISMATCH`
- `FILL_TIMING_MISMATCH`
- `STOP_OR_TIME_EXIT_MISMATCH`
- `SIZING_OR_PNL_MISMATCH`
- `BLOCKED`

## 5 · Phase-5 final BT_* labels (binding)

- `BT_VERIFICATION_PASS` — BT broadly reproduces CAMPAIGN_015 bespoke
  (trade count, per-pair distribution, expectancy R within tolerance);
- `BT_TOLERABLE_DRIFT` — small drift but consistent in direction and
  magnitude with known approximation flags (no rule mismatch);
- `BT_DIVERGENCE_NEEDS_DEBUG` — BT runs but the result diverges in a
  way that cannot be attributed to a known approximation; further infra
  work is required to triage;
- `BT_STILL_BLOCKED` — provenance repair failed or BT still cannot run.

---

## 6 · Phase-0 truth-audit results

- Branch: `infra-backtrader-campaign-015-provenance-repair-001` — new, clean. ✓
- `configs/approved_strategies.yaml` — `approved: []`. ✓
- Paper-loop / demo-loop refuse — confirmed by
  `python scripts/check_research_freeze.py` ⇒ `research freeze gate: ALL CHECKS PASSED`. ✓
- `python scripts/validate_research_archive.py` ⇒ `research archive: ALL CHECKS PASSED`. ✓
- `python scripts/scan_artifacts_for_secrets.py` ⇒ `artifact secret scan: PASSED`. ✓
- `pytest tests/ -q` ⇒ `1452 passed`. ✓
- `ruff check src tests scripts research` ⇒ 3 pre-existing findings
  in `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (commit `e382af4`); unrelated to this sprint and out of scope.
- CAMPAIGN_015 prior sprint artifacts present:
  - `research/campaign_015/diagnostics/walk_forward_rehydrate/` ✓
  - `research/campaign_015/diagnostics/gate_failure_autopsy.{json,md}` ✓
  - `research/campaign_015/diagnostics/concentration.{json,md}` ✓
  - `research/campaign_015/diagnostics/null_and_anti_overfit.{json,md}` ✓
  - `research/campaign_015/diagnostics/backtrader_comparison.json` (the prior BLOCKED record) ✓
- Local canonical data:
  - `data/campaign_002.sqlite3` — symlinked to main repo (133 MB), gitignored. ✓
  - EUR_USD H4 candles in 2020-01-01..2026-05-20 window: **19,864 candle rows** in the DB (the prior provenance recorded 9,931 unique bars; the DB has roughly two rows per bar in the current schema, consistent with bid/ask carry — the export script reconciles to bar count when it writes).
- Backtrader adapter present:
  `research/backtrader_lane/strategies/campaign_015_failed_breakout_reversal.py`. ✓
- Backtrader CSV preflight: confirmed still failing with
  `CandleProvenanceError: sha256 drift for EUR_USD: csv=16ed0bc40d05…, provenance=866d75446030…`.

---

## 7 · Validation commands

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

Run at Phase 0 (baseline) and Phase 6 (final).

---

## 8 · This sprint cannot approve the strategy

Even a clean `BT_VERIFICATION_PASS` outcome leaves CAMPAIGN_015 at
`REJECT` (the strategy still fails its trade-count and fold-pass-rate
gates) and leaves `configs/approved_strategies.yaml` at `approved: []`.
This sprint's verdict ceiling is `INFRA_UNBLOCKED`. Approval requires
a fresh pre-committed campaign on a clean candidate and a human
registry edit — neither is in scope here.
