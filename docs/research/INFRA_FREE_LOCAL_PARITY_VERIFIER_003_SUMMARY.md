# Infrastructure Free / Local Parity Verifier Sprint 003 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-003-with-data`
**Base commit:** `387e51a` (HEAD of `infra-free-local-parity-verifier-002-full-data-run`)

The guarded OANDA-practice historical rehydrate + export + verifier
sprint. **Status: BLOCKED, identical to Sprint 002** — no OANDA
practice credentials were configured locally (no `.env`, no
`OANDA_*` env vars in shell), and no pre-existing
`data/oanda_h4_research.sqlite3` was present. Per the sprint rules,
no fetch was attempted; the rehydrate script ran only in `--verify`
mode (no API call). The verifier was re-invoked end-to-end against
the absent CSVs and produced a clean BLOCKED state (7 × BLOCKED,
exit 2). The comparison harness was re-run against the **1,647-trade
no-RiskEngine** bespoke reference and produced a structurally
identical seven-row BLOCKED report.

**No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
demo / live remain blocked. No orders were submitted. No
QuantConnect / LEAN command was run. No QC credentials were
requested, read, or written. No broker credentials were printed.
No OANDA endpoint other than `--verify` (no API call) was contacted.**

## 1. Branch name

`infra-free-local-parity-verifier-003-with-data`.

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 — baseline & sprint plan | `526e032` |
| Phase 1 — rehydrate BLOCKED | `54aaf97` |
| Phase 2 — export BLOCKED | `87da284` |
| Phase 3 — full-data verifier BLOCKED | `3cdbcfa` |
| Phase 4 — comparison vs 1,647-trade bespoke BLOCKED | `2b3f365` |
| Phase 5 — verifier-side debug pass | (skipped — conditional on material divergence; full-data run was BLOCKED, no divergence to debug) |
| Phase 6 — status & evidence updates | `2c74f1c` |
| Phase 7 — final validation & summary | (this commit) |

## 3. Files changed by phase

| phase | files |
|---|---|
| Phase 0 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md` (new); `docs/research/EVIDENCE_INDEX.md` |
| Phase 1 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md` (new) |
| Phase 2 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md` (new) |
| Phase 3 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md` (new) |
| Phase 4 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` (Sprint-003 re-run record appended) |
| Phase 6 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` |
| Phase 7 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md` (new); `docs/research/EVIDENCE_INDEX.md` |

No code under `src/`, `tests/`, `scripts/`, or
`research/parity_verifier/` was modified. No campaign config,
campaign report, or `configs/approved_strategies.yaml` was touched.

## 4. Validation commands run

- `python -m pytest -q` → **473 passed**.
- `ruff check src tests scripts research/parity_verifier` → **clean**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (6 diagnostic artifacts; 83 evidence-index links resolve; no
  credential-shaped strings in 1,925 committed artifact files).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**.
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  **refused** (empty-registry message).
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  **refused**.
- `python -m forex_bot.cli --help` → no `live-loop` command exists.
- `python scripts/rehydrate_oanda_h4_store.py --verify` → reported
  store absent (no API call).

## 5. QuantConnect / LEAN status

**Retired throughout.** No QC account access, no `lean *` command
attempted, no QC credential of any kind touched.

## 6. QC credentials

**None requested, read, or created.**

## 7. OANDA practice historical fetch

**Not used.** No OANDA endpoint was contacted. The only OANDA-touching
invocation was `scripts/rehydrate_oanda_h4_store.py --verify` (the
read-only verification mode that **makes no API call**), which
reported `BLOCKER: no H4 store at data/oanda_h4_research.sqlite3.`
The fetch was deliberately not attempted because no credentials were
configured (per the sprint rules).

## 8. Broker credentials printed / committed

**None printed, none committed.** The env-presence check used a
Python one-liner that prints `SET` or `unset` per variable name; the
value never enters the output stream. All six probed `OANDA_*`
variables printed `unset`.

## 9. Orders

**None submitted.** This sprint touched no broker, no exchange, no
order placement, no `paper-loop` / `demo-loop` execution path. The
rehydrate and export scripts contain no order endpoints by design.

## 10. Strategy approval

**None.** `configs/approved_strategies.yaml` remains `approved: []`.

## 11. CAMPAIGN_002

**Remains REJECT.** Confirmed at every commit by the archive
validator.

## 12. Paper / demo / live

**All remain blocked.** Both `paper-loop` and `demo-loop` refused at
the final validation; no `live-loop` command exists.

## 13. Rehydrate status

**BLOCKED.** No `.env`, no `OANDA_*` env vars, no SQLite store. The
rehydrate script ran only in `--verify` mode (no API call). No
fetch attempted. Detail:
[`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md).

## 14. Export status

**BLOCKED.** No source SQLite store, so the export script could not
run (it refuses by design when the database is absent). Detail:
[`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md).

## 15. Full-data verifier run status

**BLOCKED.** Verifier reported 7 × BLOCKED, exited 2, wrote a valid
zero-trade `parity_summary.json`, an empty `trades.csv`, and a
markdown summary listing the blocked pairs. No crash, no fabricated
data. Detail:
[`FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md).

## 16. Total verifier trades

**0.**

## 17. By-pair verifier trades

EUR_USD 0, GBP_USD 0, USD_JPY 0, AUD_USD 0, USD_CAD 0, USD_CHF 0,
NZD_USD 0 — **total 0**.

## 18. Bespoke reference used

`research/lean_parity/campaign_002_h4_bespoke_reference.json` — the
**no-RiskEngine** bespoke reference. Scope re-asserted in code
before comparison:

```python
assert bespoke['total_trades'] == 1647
assert bespoke['risk_engine_used'] is False
```

Top-level keys confirmed:

- `parity_target`: `"CAMPAIGN_002 H4 trend_following baseline"`
- `risk_engine_used`: `false`
- `fill_timing`: `"signal_bar_close"`
- `window`: `["2020-01-01", "2026-05-20"]`
- `config_hash`: `d536a9b06818197f9915de6224e0b8ae58e77abe2c6f3c19426338646fb077bf`
- `strategy_evidence`: `false`
- `total_trades`: `1647`
- 7 pairs (full CAMPAIGN_002 universe).

The 1,032-trade with-RiskEngine reference is **not** used.

## 19. Comparison result

**BLOCKED.** Overall status BLOCKED, overall classification
`unknown`. Bespoke total trades 1,647; verifier total trades not
produced. All seven pair rows BLOCKED with the full bespoke-side
values preserved.

## 20. Divergence classification

**`unknown`** for all seven pairs and overall. Not `data_mismatch`
because the data side was not attempted on this branch; not
`indicator_mismatch` because no indicator series ran; etc. The
comparison correctly avoids labelling absence-of-output as PASS,
WARN, or FAIL.

## 21. Verifier bugs fixed

**None.** The verifier behaved correctly throughout. All 85
verifier-side fixture tests continue to pass on this branch.

## 22. Bespoke-engine bugs found

**None.** The bespoke engine was not exercised — no real-candle
cross-check happened.

## 23. Local files created but not committed

All under `/tmp/parity_verifier_003_run/` (outside the repo, not
staged):

- `parity_summary.json` — shape-valid `VerifierResult`, zeros.
- `trades.csv` — header row only.
- `parity_summary.md` — markdown summary listing blocked pairs.
- `comparison.md` — markdown comparison report (BLOCKED rows).
- `run.log` — captured stdout/stderr.

No `.env`, no SQLite store, no candle CSV, no verifier output was
staged. `git status` is clean.

## 24. Large / data outputs intentionally gitignored

Unchanged from prior sprints:

- `data/*.sqlite3` — gitignored; none exists locally.
- `research/lean_parity/exports/campaign_002_h4/**/*.csv` —
  gitignored; none exists locally.
- `research/parity_verifier/results/**/trades.csv` — gitignored
  (added in Sprint 001).

This sprint added no new `.gitignore` rules.

## 25. Remaining blockers

1. **No OANDA practice credentials configured** → rehydrate +
   export + full-data verifier all BLOCKED.
2. **No pre-existing `data/oanda_h4_research.sqlite3`** to transfer
   into the repo as an alternative.
3. **Verifier-side debugging pass (Phase 5)** could not begin —
   conditional on a material full-data divergence, none produced.
4. **Bespoke-engine cross-check** still pending — no real-candle
   comparison happened.

## 26. Recommended next decision

Two options for the user to choose between, both safe:

- **Option A — provide OANDA practice credentials.** Place a `.env`
  in the repo root with the practice account id + token (the
  rehydrate script's docstring documents the exact variable names
  and refuses ambiguous / live environments). Then a follow-on
  sprint (suggested name
  `infra-free-local-parity-verifier-004-with-creds`) re-runs the
  rehydrate → export → verifier → comparison chain. The rehydrate
  script is historical-only (`GET .../candles`); no orders are
  placed.
- **Option B — transfer a pre-existing SQLite store.** Copy
  `data/oanda_h4_research.sqlite3` from another machine into the
  repo's `data/` directory. The export and verifier steps then
  proceed without any OANDA touch.

Either option unblocks all four pending blockers. Neither option
modifies any strategy, the bespoke engine, the approved-strategy
registry, or the campaign verdicts.

## 27. Exact files to review first

1. [`FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_REHYDRATE_STATUS.md)
   — why the rehydrate did not happen, exact commands, unblock
   options.
2. [`FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_003_EXPORT_STATUS.md)
   — why the export did not happen.
3. [`FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_003_FULL_DATA_RUN.md)
   — verbatim BLOCKED behavior + totals tables.
4. [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
   "Sprint-003 re-run record" section — harness re-run with the
   reference-scope assertion against the 1,647-trade no-RiskEngine
   reference.
5. [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
   — headline status with the Sprint-003 re-confirmation banner.
6. [`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_PLAN.md)
   — sprint plan with the credential-presence and historical-only
   confirmations.
7. This summary
   ([`INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_003_SUMMARY.md)).
