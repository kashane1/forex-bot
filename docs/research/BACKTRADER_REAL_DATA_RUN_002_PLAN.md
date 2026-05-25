# Backtrader Secondary Lane 002 — Real Data Run — Plan

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-002-real-data-run`
**Sprint kind:** infrastructure / parity (NOT a strategy campaign)
**`strategy_evidence: false`**

This sprint reuses the Backtrader secondary lane built by
`infra-backtrader-secondary-lane-001` (frozen) and attempts the real
end-to-end CAMPAIGN_002 H4 comparison that Phase 6 of that branch
documented as BLOCKED. It does **not** rebuild the lane.

## 0. Hard non-goals (binding)

1. No strategy approval. `configs/approved_strategies.yaml` stays
   `approved: []`.
2. No strategy-rule tuning. CAMPAIGN_002's frozen rules and parameters
   are read-only.
3. No verdict change. CAMPAIGN_002 stays REJECT regardless of any
   comparison outcome. CAMPAIGN_010, CAMPAIGN_011, CAMPAIGN_012,
   CAMPAIGN_013 remain rejected/null/research-only. CAMPAIGN_014
   remains scaffold-only.
4. No bespoke-engine edit. If the Backtrader lane disagrees with
   bespoke, the disagreement is recorded — the bespoke engine is **not**
   "made to match".
5. No new OANDA API call unless an explicit read-only rehydration
   check is required, and only after preferring existing local
   artefacts. No credential read or print.
6. No live / demo / paper trading. The freeze gate remains green.
7. No LEAN / QuantConnect.
8. No commit of `.env`, SQLite files, bulk CSVs, or large raw
   Backtrader outputs.

## 1. Current data availability (verified at branch creation)

| artefact | path | state | notes |
|---|---|---|---|
| seven-pair H4 candle CSVs | `research/lean_parity/exports/campaign_002_h4/*.csv` | **absent** | gitignored bulk (~0.95 MB each); the previous sprint's Phase 6 already recorded this as the blocking gap |
| seven-pair provenance JSONs | `research/lean_parity/exports/campaign_002_h4/*_H4_lean.provenance.json` | **committed** | all seven present (sha256 + count + window per pair) |
| rehydrated H4 source SQLite | `data/oanda_h4_research.sqlite3` | **absent** | gitignored under `/data/`; `scripts/rehydrate_oanda_h4_store.py --verify` confirms `BLOCKER: no H4 store` |
| `data/campaign_002.sqlite3` | `data/campaign_002.sqlite3` | **absent** | gitignored symlink — not present here |
| operational bot DB | `data/bot.sqlite3` | present (167 KB) | not candle data |
| OANDA env vars (`OANDA_TOKEN`, …) | environment | **none set** (`env | grep -c -i OANDA` → 0) | rehydration cannot run without credentials |
| `.env` file | `.env` | **not present** | only `.env.example` is committed |
| bespoke no-RiskEngine reference | `research/lean_parity/campaign_002_h4_bespoke_reference.json` | **committed** | full-window run, 1,647 trades, per-pair metrics |

### Per-pair provenance summary (from the committed sidecars)

```
AUD_USD  candles= 9931  request_hash=f80ebeddf05ab414
EUR_USD  candles= 9931  request_hash=aadc096b771961e6
GBP_USD  candles= 9931  request_hash=f8e36995228587e4
NZD_USD  candles= 9935  request_hash=84c1e5b0e9ad2b07
USD_CAD  candles= 9931  request_hash=279da4f7950b782b
USD_CHF  candles= 9931  request_hash=ee37f52e9aee64b2
USD_JPY  candles= 9932  request_hash=68c0df540212891c
```

Total expected: 69,522 H4 bars across 7 instruments over 2020-01-01 →
2026-05-19. The committed `campaign_002_data_request_hash` allows the
adapter to confirm any regenerated CSV is bit-equivalent to the
candles CAMPAIGN_002 originally consumed.

## 2. Intended data source

The CSVs are regenerable from the local rehydrated SQLite store via
`scripts/export_lean_parity_data.py`. The SQLite store itself is
regenerable from OANDA practice via `scripts/rehydrate_oanda_h4_store.py`
**only with credentials** (which this worktree does not have).

The lane consumes the existing committed Lean parity export format
(documented in `research/lean_parity/lean_h4_export_format.md`) — no
new data format, no new schema, no new source.

## 3. Why no broker / API calls are needed for the work itself

Once the CSVs are restored locally:

1. `scripts/run_backtrader_parity.py --campaign CAMPAIGN_002 --output …`
   reads the CSVs + provenance and runs the BT lane.
2. `scripts/compare_backtrader_parity.py …` reads the BT summary +
   committed bespoke reference JSON and classifies divergence.

Neither step opens a socket, neither needs credentials, neither talks
to a broker. The only OANDA-touching step is rehydration of the source
SQLite — which is a *separate* operational pre-step, owned by the
rehydration script, and not part of this sprint's authored code path.

## 4. Safety invariants (carry over from sprint 001)

- `configs/approved_strategies.yaml` is byte-identical to `main`.
- `scripts/check_research_freeze.py` exits 0.
- `scripts/validate_research_archive.py` exits 0.
- `scripts/scan_artifacts_for_secrets.py` exits 0.
- No `.env`, no `data/*.sqlite3`, no `research/lean_parity/exports/**/*.csv`,
  no `research/backtrader_lane/results/**` raw outputs are committed.
- No edit under `src/forex_bot/backtesting/`.
- No edit to `research/lean_parity/lean_parity_config.json` or the
  bespoke reference JSON.
- The runner's OANDA env-var sanitiser remains active.

## 5. Expected commands (when data becomes available)

Phase 2 — real run:

```bash
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --output research/backtrader_lane/results/campaign_002_real_data/
```

Phase 3 — comparison:

```bash
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --backtrader-results research/backtrader_lane/results/campaign_002_real_data/ \
    --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
    --output research/backtrader_lane/results/campaign_002_real_data/comparison/
```

The compact summary outputs may then be reviewed; the bulky JSONL
trade list lives under the gitignored
`research/backtrader_lane/results/` and is not committed.

## 6. Blocked criteria

This sprint declares Phase 1 BLOCKED if **all** of the following hold:

1. No CSV is present at
   `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv`
   for any of the seven pairs.
2. No rehydrated SQLite is present at
   `data/oanda_h4_research.sqlite3` (the only source the existing
   `scripts/export_lean_parity_data.py` knows how to read).
3. No OANDA practice credential is present in env or in `.env` that
   would allow `scripts/rehydrate_oanda_h4_store.py` to run.
4. No alternative locally-committed real CAMPAIGN_002 H4 candle
   bundle exists in the repo.

At the moment of branch creation **all four** of these hold. Phase 1
will exercise them once more in case the operator restored data
between branch creation and Phase 1 run.

## 7. Baseline validations passed (2026-05-24)

```text
python -m pytest tests/unit/backtrader_lane -q   → 75 passed
ruff check src tests scripts research/backtrader_lane → All checks passed
python scripts/check_research_freeze.py          → ALL CHECKS PASSED
python scripts/validate_research_archive.py      → ALL CHECKS PASSED
python scripts/scan_artifacts_for_secrets.py     → PASSED
configs/approved_strategies.yaml                 → approved: []
no .env present; no OANDA env var set; no SQLite store for the H4 research candles
```

## 8. Plan summary

- **Phase 1:** Re-verify data availability; if anything has appeared
  since branch creation, regenerate/validate the seven CSVs and
  proceed to Phase 2. If not, declare BLOCKED with the exact restore
  recipe.
- **Phase 2:** Real CAMPAIGN_002 Backtrader run (if Phase 1 unblocked).
- **Phase 3:** Comparison vs bespoke + divergence classification.
- **Phase 4:** Fidelity-debugging pass **only** if material
  divergence; fix Backtrader-lane bugs only, never the bespoke engine.
- **Phase 5:** CAMPAIGN_011 decision — only if CAMPAIGN_002 reached
  PASS or TOLERABLE_DRIFT, or divergence is clearly classified.
- **Phase 6:** Final summary, evidence-index/manifest updates, full
  validation suite.

`strategy_evidence: false`. The lane cannot, must not, and will not
approve a strategy.
