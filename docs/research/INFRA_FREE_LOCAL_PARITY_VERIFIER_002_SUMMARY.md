# Infrastructure Free / Local Parity Verifier Sprint 002 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-002-full-data-run`
**Base commit:** `6ec5e7e` (HEAD of `infra-free-local-parity-verifier-001`)

The follow-on sprint that attempted to unblock the data and run the
first full-data verifier + comparison. **The data unblock was not
possible under the sprint rules** — no local SQLite store, no OANDA
practice credentials configured, no `.env` present. The verifier was
exercised end-to-end against the absent CSVs and produced a clean
BLOCKED state (7 × BLOCKED, exit code 2, no crash, no fabricated
data). The comparison harness was re-run programmatically against
the real bespoke no-RiskEngine reference (1,647 trades) and produced
a structurally identical seven-row BLOCKED report.

**No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
demo / live remain blocked. No orders were submitted. No
QuantConnect / LEAN command was run. No QC credentials were
requested, read, or written. No broker credentials were printed.**

## 1. Branch name

`infra-free-local-parity-verifier-002-full-data-run`.

## 2. Commit hashes by phase

| phase | commit |
|---|---|
| Phase 0 — baseline & sprint plan | `dc1b6f0` |
| Phase 1 — data unblock BLOCKED | `a47854f` |
| Phase 2 — first full-data run BLOCKED | `43548b1` |
| Phase 3 — comparison vs bespoke BLOCKED | `3b4a2ef` |
| Phase 4 — verifier-side debug pass | (skipped — conditional on material divergence; no full-data run → no divergence to debug) |
| Phase 5 — status & evidence updates | `1499d15` |
| Phase 6 — final validation & summary | (this commit) |

## 3. Files changed by phase

| phase | files |
|---|---|
| Phase 0 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md` (new); `docs/research/EVIDENCE_INDEX.md` |
| Phase 1 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md` (new) |
| Phase 2 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md` (new) |
| Phase 3 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` (Sprint-002 re-run record appended) |
| Phase 5 | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md`, `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` |
| Phase 6 | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md` (new) |

No code under `src/`, `tests/`, `scripts/`, or `research/parity_verifier/`
was modified. No campaign config, campaign report, or
`configs/approved_strategies.yaml` was touched.

## 4. Validation commands run

- `python -m pytest -q` → **473 passed** (same as Sprint 001 baseline
  + 85 verifier-side fixture tests).
- `ruff check src tests scripts research/parity_verifier` → **clean**.
- `python scripts/validate_research_archive.py` → **ALL CHECKS PASSED**
  (6 diagnostic artifacts; 78 evidence-index links resolve; no
  credential-shaped strings in 1,920 committed artifact files).
- `python scripts/check_research_freeze.py` → **ALL CHECKS PASSED**
  (paper-loop + demo-loop both refuse `['trend_following']` — frozen).
- `python scripts/scan_artifacts_for_secrets.py` → **PASSED**.
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` →
  **refused** with the empty-registry message.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` →
  **refused** with the empty-registry message.
- `python -m forex_bot.cli --help` → no `live-loop` command exists.

## 5. QuantConnect / LEAN status

**Retired throughout.** No QC account was created, accessed, or
requested. No `lean login` / `lean init` / `lean backtest` was
attempted. The retirement decision record from the prior sprint
remains the source of truth.

## 6. QC credentials

**None requested, read, or created.** No QC value of any kind was
prompted-for, sourced, echoed, or written this sprint.

## 7. OANDA practice historical fetch

**Not used.** No call was made to any OANDA endpoint. The only
OANDA-touching invocation was `scripts/rehydrate_oanda_h4_store.py --verify`
(the read-only mode that confirms store absence without needing
credentials), which printed:

```text
BLOCKER: no H4 store at data/oanda_h4_research.sqlite3. Run a
rehydration fetch first (requires OANDA practice credentials).
```

The fetch was deliberately **not attempted** because no credentials
were configured (no `.env`, no `OANDA_*` env vars), and the sprint
rules forbid fabricating data.

## 8. Broker credentials

**None printed, none committed.** The env-presence check redacted
all values before any print (`env | grep -iE OANDA | sed 's/=.*/=<REDACTED>/'`),
and that command produced empty output anyway — no `OANDA_*`
variables are set in this shell.

## 9. Orders

**None submitted.** This sprint touched no broker, no exchange, no
order placement, no `paper-loop` / `demo-loop` execution path. The
only loop invocations were the documented refusal checks at Phase 0
and Phase 6 (both refused as expected).

## 10. Strategy approval

**None.** `configs/approved_strategies.yaml` remains `approved: []`.
The verifier's `VerifierResult` and `ComparisonReport` models still
hard-pin `strategy_evidence: false`.

## 11. CAMPAIGN_002

**Remains REJECT.** Confirmed by the archive validator at every
commit this sprint.

## 12. Paper / demo / live

**All remain blocked.** Direct CLI invocations at this phase
re-confirmed it; the freeze checker re-confirmed it at every commit.

## 13. Data unblock status

**BLOCKED.** Detail in
[`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md):

- `data/oanda_h4_research.sqlite3` absent (only `data/.gitkeep`).
- All seven H4 export CSVs absent (only their `*.provenance.json`
  siblings are present).
- `.env` absent (only `.env.example`).
- No `OANDA_*` env vars in shell.
- Rehydrate-script `--verify` confirms store absence.
- No fetch attempted (per the sprint rules).

Two alternative future-invocation unblock paths are documented:
either transfer a pre-existing SQLite store from another machine,
**or** provide OANDA practice credentials in `.env` and let the
existing rehydrate + export chain do its job.

## 14. Full-data verifier run status

**BLOCKED.** Detail in
[`FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md):

- Invoked `scripts/run_free_local_parity_verifier.py --output /tmp/parity_verifier_002_run/`.
- Verifier reported 7 × BLOCKED with the precise missing CSV path
  for each pair.
- Wrote a valid `parity_summary.json` (`VerifierResult` shape;
  `total_trades: 0`, `pairs: []`, `strategy_evidence: false`,
  `risk_engine_used: false`).
- Wrote an empty `trades.csv` (header row only).
- Wrote a markdown summary listing the blocked pairs.
- Exited with code **2** (documented "every pair blocked" signal).
- No crash, no stack trace, no fabricated data.

## 15. Total verifier trades

**0.** No pair ran.

## 16. By-pair verifier trades

| instrument | trades |
|---|---|
| EUR_USD | 0 |
| GBP_USD | 0 |
| USD_JPY | 0 |
| AUD_USD | 0 |
| USD_CAD | 0 |
| USD_CHF | 0 |
| NZD_USD | 0 |
| **total** | **0** |

## 17. Bespoke reference used

`research/lean_parity/campaign_002_h4_bespoke_reference.json` — the
**no-RiskEngine** bespoke reference. Top-level keys confirm scope:

- `parity_target`: `"CAMPAIGN_002 H4 trend_following baseline"`
- `risk_engine_used`: `false`
- `fill_timing`: `"signal_bar_close"`
- `window`: `["2020-01-01", "2026-05-20"]`
- `config_hash`: `d536a9b06818197f9915de6224e0b8ae58e77abe2c6f3c19426338646fb077bf`
- `strategy_evidence`: `false`
- `total_trades`: `1647`
- 7 pairs (full CAMPAIGN_002 universe).

The 1,032-trade with-RiskEngine reference is **not** used. Mixing
references is forbidden by the mapping spec §0 and was not done.

## 18. Comparison result

**BLOCKED.** Detail in the
[`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
"Sprint-002 re-run record" section:

- Overall status: **BLOCKED**.
- Overall classification: **`unknown`**.
- Bespoke total trades: 1,647.
- Verifier total trades: — (not produced).
- All seven pair rows: BLOCKED with full bespoke-side values
  preserved.
- No divergence hidden, relabelled, or tuned away.

## 19. Divergence classification

**`unknown`** for all seven pairs and overall. The verifier never
produced numbers to diverge from, so the divergence cannot be
classified into a specific bucket (it is not `data_mismatch`
because the data side has not even been attempted; not
`indicator_mismatch` because no indicator series ran; etc.). The
comparison correctly avoids labelling the absence of output as
PASS, WARN, or FAIL.

## 20. Verifier bugs fixed

**None.** The script handled the absent-data state cleanly:
deterministic BLOCKED messages, valid `VerifierResult` shape, exit
code 2, no crash, no fabricated data. The Sprint 001 fixture-test
suite (85 cases) continues to pass unchanged on this branch.

## 21. Bespoke-engine bugs found

**None.** The bespoke engine was not exercised. A real-candle
cross-check was not possible because the CSVs are absent. A bespoke-
side bug, if it exists, will only surface in a future full-data run
once the unblock is performed.

## 22. Local files created but not committed

All outside the repo, under `/tmp/parity_verifier_002_run/`:

- `parity_summary.json` — shape-valid `VerifierResult`, zeros.
- `trades.csv` — header row only, zero data rows.
- `parity_summary.md` — markdown summary listing blocked pairs.
- `comparison.md` — markdown comparison report (BLOCKED rows).
- `run.log` — captured stdout/stderr from the script invocation.

`git status` is clean. No `.env`, no SQLite, no candle CSV, no
verifier output was staged this sprint.

## 23. Large / data outputs intentionally gitignored

The .gitignore rules from Sprint 001 are unchanged:

- `data/*.sqlite3` — gitignored before this sprint; no SQLite store
  exists locally anyway.
- `research/lean_parity/exports/campaign_002_h4/**/*.csv` —
  gitignored; none exists locally.
- `research/parity_verifier/results/**/trades.csv` — gitignored.

This sprint added no new `.gitignore` rules.

## 24. Remaining blockers

1. **Local H4 candle CSVs absent** → the full seven-pair full-window
   verifier run cannot execute. Unblock requires either transferring
   an existing `data/oanda_h4_research.sqlite3` from another machine
   **or** configuring OANDA practice credentials in `.env` so the
   existing rehydrate + export chain can rebuild the store.
2. **Verifier-side debugging pass (Phase 4 of this sprint)** could
   not begin — it is conditional on a material divergence from a
   full-data run, and no full-data run was produced.
3. **Bespoke-engine cross-check** still pending — no real-candle
   comparison happened, so no statement can be made about whether
   the bespoke engine and the verifier agree on real OANDA H4
   candles.

## 25. Recommended next decision

Two options for the user to choose between, both safe:

- **Option A — provide credentials.** Configure OANDA practice
  credentials in `.env` (account id + token, practice-mode), then a
  follow-on sprint (`infra-free-local-parity-verifier-003-with-data`
  is one suggested name) re-runs Phase 1's `rehydrate_oanda_h4_store.py`
  → seven `export_lean_parity_data.py` invocations →
  `run_free_local_parity_verifier.py` → comparison. The verifier
  code is ready; the gating decision is purely the credential.
- **Option B — transfer a pre-existing store.** If a
  `data/oanda_h4_research.sqlite3` already exists on another
  machine the user controls, copying it into `data/` lets the
  follow-on sprint skip the OANDA fetch entirely and go straight to
  the export + verifier + comparison.

Either option resolves blocker 1 and unlocks blockers 2 and 3
automatically. Neither option modifies any strategy, the bespoke
engine, the approved-strategy registry, or the campaign verdicts.

## 26. Exact files to review first

1. [`FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md)
   — why the data unblock did not happen and how a future invocation
   can resolve it.
2. [`FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md`](FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md)
   — verbatim BLOCKED behavior from the script invocation and the
   per-pair / totals tables.
3. [`FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md`](FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md)
   "Sprint-002 re-run record" section — the comparison harness run
   against the real bespoke no-RiskEngine reference, plus the
   reference-scope confirmation.
4. [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
   — the headline status with the Sprint-002 re-confirmation
   banner.
5. [`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md)
   — the sprint plan, including the artifact-inventory table that
   recorded the BLOCKER up front.
6. This summary
   ([`INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md)).
