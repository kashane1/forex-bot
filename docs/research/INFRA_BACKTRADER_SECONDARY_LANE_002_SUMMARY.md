# INFRA — Backtrader Secondary Lane 002 — Real Data Run — Summary

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-002-real-data-run`
**Sprint kind:** infrastructure / parity (NOT a strategy campaign)
**`strategy_evidence: false`**

## 0. Headline

**BLOCKED — same load-bearing artefact as sprint 001's Phase 6.**

The Backtrader secondary lane built by `infra-backtrader-secondary-lane-001`
remains correct, tested, and ready to run. The single artefact that
would unblock the real CAMPAIGN_002 H4 comparison —
`data/oanda_h4_research.sqlite3` — is gitignored and absent from this
worktree, and no OANDA practice credentials are present in env / `.env`
to rehydrate it. This sprint did not fabricate data, did not weaken
the freeze, and did not change any campaign verdict.

> **No strategy approved. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
> CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
> CAMPAIGN_014 remains scaffold-only. `configs/approved_strategies.yaml`
> remains `approved: []`. Paper / demo / live remain blocked.**

## 1. Branch + commits by phase

Branch: `infra-backtrader-secondary-lane-002-real-data-run`
(branched from `infra-backtrader-secondary-lane-001` @ `f28cfbd`).

| phase | commit | description |
|---|---|---|
| 0 | `80d3073` | plan + baseline; data-availability snapshot |
| 1 | `bc035b3` | BLOCKED preflight; the load-bearing restore recipe |
| 2 | — | not run (depends on Phase 1) |
| 3 | — | not run (depends on Phase 2) |
| 4 | — | not run (no divergence to debug because no run) |
| 5 | `271dcd9` | CAMPAIGN_011 BLOCKED (cascade); carry-forward implementation prompt |
| 6 | (this) | sprint summary + evidence-index/manifest update |

## 2. Data source status

| artefact | state |
|---|---|
| `data/oanda_h4_research.sqlite3` | **absent** — verified at branch creation and at Phase 1 re-check; `python scripts/rehydrate_oanda_h4_store.py --verify` returns `BLOCKER: no H4 store at data/oanda_h4_research.sqlite3` |
| `data/campaign_002.sqlite3` | **absent** (the legacy gitignored symlink path) |
| `data/bot.sqlite3` | present (167 KB operational DB — not candle data) |
| `research/lean_parity/exports/campaign_002_h4/*.csv` | **absent** — the gitignored bulk CSVs are not regenerable without the source SQLite above |
| `research/lean_parity/exports/campaign_002_h4/*_H4_lean.provenance.json` | **committed** — all seven sidecars present (sha256 + count + window + `campaign_002_data_request_hash`) |
| `research/lean_parity/campaign_002_h4_bespoke_reference.json` | **committed** — 1,647-trade no-RiskEngine reference for CAMPAIGN_002 |
| `.env` | **not present** (only `.env.example` is committed) |
| OANDA env vars (`OANDA_TOKEN` / `OANDA_API_TOKEN` / `OANDA_ACCOUNT_ID`) | **none set** (`env \| grep -c -i OANDA` → 0) |

## 3. Exact real-data files used / generated

**None.** No CSV was produced, no SQLite was opened beyond the
operational `data/bot.sqlite3`, no provenance sidecar was modified.
The Phase 1 runner preflight wrote a small `backtrader_summary.json`
to `/tmp/bt_preflight_002/` (outside the repo) which was inspected
but **not** committed. The `research/backtrader_lane/results/`
directory is gitignored as a defence-in-depth measure.

## 4. CAMPAIGN_002 Backtrader run status

**Not run.** Phase 2 was skipped because Phase 1 was BLOCKED. The
runner preflight correctly reported every requested instrument as
blocked and did not fabricate a trade:

```text
instruments_requested: [EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD]
instruments_runnable:  []
instruments_blocked:   [EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD]
expected_in_export_dir: [AUD_USD, EUR_USD, GBP_USD, NZD_USD, USD_CAD, USD_CHF, USD_JPY]
available_in_export_dir: []
```

## 5. CAMPAIGN_002 comparison status

**Not run.** Phase 3 was skipped because Phase 2 was skipped.

## 6. CAMPAIGN_002 divergence classification

**N/A — no comparison.** No new divergence label was emitted by this
sprint. The Backtrader-lane comparison harness's `BLOCKED` label
(`research/backtrader_lane/compare.py`) is what would have been
emitted at Phase 3, identical to what sprint 001's Phase 6 already
documented.

## 7. Backtrader-lane bugs fixed

**None.** No real comparison was performed, so no new bug could be
surfaced. The 75 backtrader_lane tests (smoke + adapter + runner +
CAMPAIGN_002 adapter + comparison) continue to PASS, exactly as they
did at sprint 001's Phase 8.

## 8. Bespoke-engine bugs found

**None.** Cannot find a bug we did not compare against.

## 9. CAMPAIGN_011 status

**BLOCKED (cascade).** Phase 5's precondition ("CAMPAIGN_002 reached
PASS or TOLERABLE_DRIFT, or divergence is clearly documented") was
unmet because Phase 1 was BLOCKED. The same single artefact
(`data/oanda_h4_research.sqlite3`) unblocks both campaigns at once —
CAMPAIGN_011 reused the same local store as CAMPAIGN_010 / CAMPAIGN_002
(see `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §4).

The carry-forward implementation prompt for the CAMPAIGN_011 BT
adapter (frozen parameters, R1–R8 rules, approximation flags, test
plan) is recorded verbatim in
[`BACKTRADER_CAMPAIGN_011_BLOCKED_002.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_002.md) §4.

## 10. Known unsupported / approximated behaviour

Unchanged from sprint 001 (the lane itself is unchanged):

| flag | meaning |
|---|---|
| `MID_OHLC_DERIVED` | mid OHLC derived from bid/ask; BT feed sees mid only |
| `BAR_OPEN_TIMESTAMP` | index value is the bar OPEN time, 17:00-NY aligned |
| `HALF_SPREAD_CLOSE` | only the close-time half-spread is carried |
| `BACKTRADER_INDICATORS` | EMA + ATR via `bt.indicators`; sub-pip warmup differences possible |
| `DONCHIAN_PRIOR_BARS_ONLY` | manual deque (BT's stock `Highest`/`Lowest` would lookahead) |
| `BACKTRADER_BROKER_BYPASSED` | strategy has its own one-position state machine |
| `MANUAL_SIZING_RISK_FRACTION` | manual whole-unit floor; sub-bps drift from float vs Decimal |
| `TRAILING_STOP_RATCHET` | same 2.0×ATR multiple as initial stop |
| `NO_RISK_ENGINE` | spread / session / loss-limit gates not modelled |
| `NO_FINANCING` | financing/swap not modelled (pre-financing comparison) |

## 11. Local generated files not committed

| location | content | rule |
|---|---|---|
| `/tmp/bt_preflight_002/` | Phase 1 preflight artefacts (manifest, empty trades.jsonl, log) | outside the repo |
| `research/backtrader_lane/results/` | (empty in this worktree) | gitignored |
| `research/backtrader_lane/exports/` | (empty in this worktree) | gitignored |

## 12. Validation commands run

```bash
python -m pytest tests/unit/backtrader_lane -q          # 75 PASS  (baseline)
python -m pytest -q                                     # 1179 PASS (final — see below)
ruff check src tests scripts research/backtrader_lane   # All checks passed
python scripts/check_research_freeze.py                 # ALL CHECKS PASSED
python scripts/validate_research_archive.py             # ALL CHECKS PASSED
python scripts/scan_artifacts_for_secrets.py            # PASSED
```

The full suite is re-run at the bottom of this document.

## 13. Safety state

- `configs/approved_strategies.yaml` byte-identical to `main` and to
  the branch parent: `approved: []`.
- `src/forex_bot/` untouched (no diff vs the parent branch).
- `configs/paper.yaml`, `configs/practice.yaml` untouched.
- `backtests/` untouched.
- `research/lean_parity/lean_parity_config.json` untouched.
- `research/lean_parity/campaign_002_h4_bespoke_reference.json` untouched.
- No `.env` staged. No SQLite staged. No bulk CSV staged. No large
  raw Backtrader output staged. No OANDA API call made. No LEAN /
  QuantConnect import added. No paper / demo / live enablement.

Files touched on this branch (relative to `infra-backtrader-secondary-lane-001`):

```
docs/research/BACKTRADER_REAL_DATA_RUN_002_PLAN.md           NEW
docs/research/BACKTRADER_REAL_DATA_PREFLIGHT_002.md          NEW
docs/research/BACKTRADER_CAMPAIGN_011_BLOCKED_002.md         NEW
docs/research/INFRA_BACKTRADER_SECONDARY_LANE_002_SUMMARY.md NEW (this)
docs/research/EVIDENCE_INDEX.md                              +1 section
docs/research/EVIDENCE_MANIFEST.json                         +4 entries
```

## 14. Recommended next branch

Same target as sprint 001's recommendation, restated with the latest
preflight diagnosis:

**Branch name:** `infra-backtrader-secondary-lane-003-real-data-run`
*(or any branch that performs the data restore + run + comparison
separately from new lane code, since the lane itself needs no change)*

**Single hard prerequisite:** restore `data/oanda_h4_research.sqlite3`
in the operator's working tree by one of:

- **Path A (no broker call):** copy a previous backup of the file to
  `data/oanda_h4_research.sqlite3`.
- **Path B (read-only OANDA practice):** populate `.env` with practice
  credentials (`OANDA_PRACTICE_TOKEN`, `OANDA_PRACTICE_ACCOUNT_ID`,
  `OANDA_ENVIRONMENT=practice`) and run
  `python scripts/rehydrate_oanda_h4_store.py`.

Then, in the new branch:

1. Verify the store: `python scripts/rehydrate_oanda_h4_store.py --verify`.
2. Export the seven CAMPAIGN_002 H4 CSVs:
   ```bash
   python scripts/export_lean_parity_data.py \
       --db data/oanda_h4_research.sqlite3 \
       --out-dir research/lean_parity/exports/campaign_002_h4/
   ```
3. Real CAMPAIGN_002 run:
   ```bash
   python scripts/run_backtrader_parity.py \
       --campaign CAMPAIGN_002 \
       --output research/backtrader_lane/results/campaign_002_real_data/
   ```
4. Real CAMPAIGN_002 comparison:
   ```bash
   python scripts/compare_backtrader_parity.py \
       --campaign CAMPAIGN_002 \
       --backtrader-results research/backtrader_lane/results/campaign_002_real_data/ \
       --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
       --output research/backtrader_lane/results/campaign_002_real_data/comparison/
   ```
5. Document the classification in
   `docs/research/BACKTRADER_CAMPAIGN_002_REAL_COMPARISON.md`.
6. If `PASS` / `TOLERABLE_DRIFT`: implement CAMPAIGN_011 per
   `BACKTRADER_CAMPAIGN_011_BLOCKED_002.md` §4 and run/compare.
7. Final summary doc.

## 15. Exact files I should review first

1. [`BACKTRADER_REAL_DATA_PREFLIGHT_002.md`](BACKTRADER_REAL_DATA_PREFLIGHT_002.md) — the BLOCKED state + the load-bearing restore recipe.
2. [`BACKTRADER_REAL_DATA_RUN_002_PLAN.md`](BACKTRADER_REAL_DATA_RUN_002_PLAN.md) — the non-goals + blocked criteria.
3. [`BACKTRADER_CAMPAIGN_011_BLOCKED_002.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_002.md) — the carry-forward CAMPAIGN_011 implementation prompt for the future unblock sprint.
4. [`INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md`](INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md) — the parent sprint's status, unchanged here.

## 16. Required disclosure

**This sprint cannot approve any strategy and does not enable paper /
demo / live trading.** No campaign verdict changed. The lane was not
exercised on real data because the load-bearing data artefact is not
present locally; the existing Backtrader-lane code is unchanged and
ready to run the moment data is restored. `strategy_evidence: false`.
