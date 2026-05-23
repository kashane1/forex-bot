# Infrastructure Free / Local Parity Verifier Sprint 002 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-002-full-data-run`
**Base commit:** `6ec5e7e` (HEAD of `infra-free-local-parity-verifier-001`)

The follow-on sprint to the first verifier sprint. The first sprint
implemented the package, fixture-level indicator / rule / event-loop /
comparison tests (85 verifier-side fixture tests pass), and the script
entry point, but ended with the full-data run BLOCKED locally because
the H4 export CSVs are gitignored bulk data and were not present. This
sprint's goal is to unblock the data and run the first full-data
verifier + comparison.

> `strategy_evidence: false`. This sprint cannot approve a strategy.
> CAMPAIGN_002 remains REJECT. Paper / demo / live remain blocked.
> `configs/approved_strategies.yaml` stays empty.

## 1. Purpose

- Make the seven-pair H4 candle CSV exports locally available so the
  free / local verifier can run end-to-end.
- Run the verifier against the seven pairs over the full
  2020-01-01 → 2026-05-20 window.
- Compare the verifier's trade list against the **no-RiskEngine**
  bespoke reference (`campaign_002_h4_bespoke_reference.json`,
  1,647 trades).
- Classify any divergence under the inherited LEAN-era taxonomy.
- Fix verifier-side bugs surfaced by divergence; never change the
  bespoke engine or CAMPAIGN_002 rules in service of better numbers.

## 2. Non-goals

- Not a strategy approval. CAMPAIGN_002 stays REJECT regardless of
  outcome.
- Not a CAMPAIGN_002 re-run — the bespoke engine is not invoked.
- Not a tuning loop.
- Not a paper / demo / live trigger.
- Not a broker connection. The only OANDA touch permitted is a
  historical-candle re-fetch (practice-mode, read-only) to rebuild
  the local SQLite store if needed, exactly as the existing
  `scripts/rehydrate_oanda_h4_store.py` already does.
- Not a QuantConnect / LEAN reopening. Retirement stands.

## 3. Safety invariants

Hold across every phase, every commit:

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No campaign re-run, no new campaign
   registered.
3. Paper / demo loops keep refusing; no `live-loop` command exists.
4. No QC credential is requested, read, written, or echoed.
5. No broker credential is **printed**. OANDA practice credentials may
   be used **only** by the existing rehydrate script for historical
   read-only candle retrieval; no order placement, no live mode.
6. No `.env`, `*.sqlite3`, candle CSV, or bulky verifier output gets
   staged or committed.
7. No new external dependency added unless explicitly approved.
8. The bespoke engine under `src/forex_bot/` is **not modified** to
   match the verifier.
9. The frozen CAMPAIGN_002 rules in
   `research/lean_parity/lean_parity_config.json` and the mapping
   spec are read-only inputs.
10. Validators must pass on every commit: pytest, ruff, archive
    validator, freeze checker, secret scanner.
11. No reopening of the QuantConnect / LEAN path.

## 4. Artifact inventory — local state at sprint start

Captured 2026-05-22, this branch HEAD.

| artifact | committed? | locally present? |
|---|---|---|
| `data/oanda_h4_research.sqlite3` | no (gitignored) | **NO** — only `data/.gitkeep` |
| 7 × `research/lean_parity/exports/campaign_002_h4/*_H4_lean.csv` | no (gitignored) | **NO** — only the 7 `*.provenance.json` files |
| 7 × `*.provenance.json` for the CSVs | yes | yes |
| `research/lean_parity/campaign_002_h4_bespoke_reference.json` (no-RiskEngine, 1,647 trades) | yes | yes |
| `research/lean_parity/lean_parity_config.json` (authoritative params) | yes | yes |
| `research/lean_parity/campaign_002_h4_spec.md` | yes | yes |
| `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` | yes | yes |
| `docs/research/LEAN_PARITY_COMPARISON_METHOD.md` | yes | yes |

OANDA practice credentials:
- `.env` file in repo root: **absent** (only `.env.example`).
- `OANDA_*` environment variables set in this shell: **none**.

`scripts/rehydrate_oanda_h4_store.py --verify` (read-only, no
credentials needed) confirms the SQLite store is absent:

```text
BLOCKER: no H4 store at data/oanda_h4_research.sqlite3. Run a
rehydration fetch first (requires OANDA practice credentials).
```

## 5. Whether data regeneration is needed — and whether it is possible

**Needed:** yes — both the SQLite store and the seven CSVs are
absent. Without the CSVs, the verifier cannot run on real candles.

**Possible on this branch:** no. The repo's approved regeneration
path is `scripts/rehydrate_oanda_h4_store.py`, which **requires OANDA
practice credentials** (account id + token). The script's docstring
explicitly states the practice-data environment guard must pass and
"missing credentials … abort the fetch". No `.env` is present, no
practice credentials are in the environment, and no other approved
network-fetch workflow exists for these candles. Per the sprint
rules:

> If credentials or source data are missing, stop this phase and
> document the blocker. Do not fabricate data.

This sprint will therefore **document the blocker honestly** at Phase
1 and proceed only with the safe phases that do not require the bulk
data — re-confirming the safety state, updating the status doc to
reflect that the data unblock has not happened, and writing the
sprint summary. Phases 2, 3, and 4 cannot meaningfully execute
without the CSVs; they will be marked BLOCKED and the corresponding
docs will record exactly what was missing.

This is the same physical blocker the first verifier sprint
documented; the difference is that this sprint is the one that
explicitly attempts the unblock and records the practical state of
the local environment.

## 6. Expected planned commands (if creds were available)

For the record — these are **not run** this sprint because the
prerequisite credentials are absent:

```bash
# (NOT RUN) Rehydrate the H4 SQLite store from OANDA practice:
python scripts/rehydrate_oanda_h4_store.py --config configs/paper.yaml

# (NOT RUN) Export seven Lean-parity CSVs per pair:
for inst in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF NZD_USD; do
  python scripts/export_lean_parity_data.py \
    --db data/oanda_h4_research.sqlite3 \
    --instrument "$inst" --from 2020-01-01 --to 2026-05-20
done

# (NOT RUN) Run the verifier across the seven pairs:
python scripts/run_free_local_parity_verifier.py \
  --output research/parity_verifier/results/campaign_002_h4_full_data/
```

If a future invocation re-runs this plan in an environment with
practice credentials present, the commands above execute Phases 1
through 3 as designed. The verifier already supports this end-to-end
(implemented in Sprint 001).

## 7. Expected outputs

| output | path | committed? |
|---|---|---|
| Sprint plan (this doc) | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_002_PLAN.md` | yes |
| Data unblock status | `docs/research/FREE_LOCAL_PARITY_VERIFIER_DATA_UNBLOCK_STATUS.md` | yes — records BLOCKER state |
| Full-data run status | `docs/research/FREE_LOCAL_PARITY_VERIFIER_FULL_DATA_RUN.md` | yes — records BLOCKED at Phase 2 |
| Comparison doc (updated) | `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` | yes — re-confirms BLOCKED for full-data, fixture-level still PASS |
| Headline status (updated) | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md` | yes |
| Evidence index / manifest | updated | yes |
| Sprint summary | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_002_SUMMARY.md` | yes |
| Verifier run outputs | `research/parity_verifier/results/campaign_002_h4_full_data/` | n/a — not produced |
| SQLite store | `data/oanda_h4_research.sqlite3` | n/a — not produced |
| H4 export CSVs | `research/lean_parity/exports/campaign_002_h4/*.csv` | n/a — not produced |

## 8. Explicit statement on approval

This sprint cannot and does not approve a strategy. It does not edit
`configs/approved_strategies.yaml`, the bespoke engine, the
CAMPAIGN_002 rules, the campaign reports, or `EVIDENCE_MANIFEST.json`
campaign verdicts. Its outputs are diagnostic only — every committed
verifier artifact carries `strategy_evidence: false` and the
comparison-report model rejects construction with the rail flipped.

## 9. Cross-links

- Retirement: [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md)
- Original design: [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
- Sprint 001 (implementation): [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md)
- Headline status: [`FREE_LOCAL_PARITY_VERIFIER_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_STATUS.md)
- Mapping spec: [`CAMPAIGN_002_LEAN_MAPPING_SPEC.md`](CAMPAIGN_002_LEAN_MAPPING_SPEC.md)
- Authoritative parameters: `research/lean_parity/lean_parity_config.json`
- Tolerances + divergence taxonomy: [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md)
- Bespoke no-RiskEngine reference: `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647 trades)
- Existing rehydrate script: [`scripts/rehydrate_oanda_h4_store.py`](../../scripts/rehydrate_oanda_h4_store.py)
- Existing export script: [`scripts/export_lean_parity_data.py`](../../scripts/export_lean_parity_data.py)
- Verifier script: [`scripts/run_free_local_parity_verifier.py`](../../scripts/run_free_local_parity_verifier.py)
