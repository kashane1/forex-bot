# Infrastructure Free/Local Parity Verifier Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-free-local-parity-verifier-001`
**Base commit:** `72b8d3c` (HEAD of `infra-retire-quantconnect-lean-001`)

Implementation sprint for the free / local independent parity verifier
designed in
[`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md).
QuantConnect/LEAN is retired (see
[`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md));
this sprint builds the replacement.

> `strategy_evidence: false`. This sprint verifies the *measurement
> instrument* (the bespoke backtest engine), not any strategy. **It
> cannot approve a strategy.** CAMPAIGN_002 stays REJECT regardless of
> any verifier outcome. `configs/approved_strategies.yaml` stays empty.
> Paper / demo / live stay blocked.

## 1. Purpose

Implement a working, deterministic, repo-internal independent verifier
that consumes the same H4 candles CAMPAIGN_002 used and reproduces the
trend_following 0.1.0 trade list from the strategy specification —
without importing any bespoke engine code. Compare its output to the
no-RiskEngine bespoke reference and classify any divergence under the
inherited LEAN-era taxonomy. The verifier is the first independent
implementation that can corroborate (or contradict) the bespoke engine
on CAMPAIGN_002 without QuantConnect / LEAN / cloud / broker access.

## 2. Non-goals

- **Not a new strategy.** No new entry/exit/sizing rule, no new
  parameter, no new family.
- **Not a CAMPAIGN_002 re-run** — the bespoke engine is not invoked.
- **Not strategy approval.** Even a clean PASS approves nothing.
- **Not a tuning loop.** No knob is turned to improve numbers.
- **Not a paper / demo / live trigger.** No order-capable loop is
  touched. `configs/approved_strategies.yaml` stays empty.
- **Not a broker / OANDA / cloud / API client.** No network calls.
- **Not a QuantConnect / LEAN tool.** Retirement stands.
- **Not a replacement for the bespoke RiskEngine.** The verifier
  targets the *no-RiskEngine* bespoke reference (1,647 trades), exactly
  as the LEAN algorithm did. See `CAMPAIGN_002_LEAN_MAPPING_SPEC.md` §0.

## 3. Safety invariants

These hold across every phase, every commit:

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No campaign re-run, no new campaign
   registered.
3. Paper / demo loops keep refusing; no `live-loop` command exists.
4. No broker / OANDA / QC credential is read, prompted-for, written,
   echoed, or committed.
5. No `.env`, no `*.sqlite3`, no large regenerable candle CSV, no
   bulky verifier output gets staged or committed.
6. No new external dependency is added in this sprint. The verifier
   uses only the repo's existing `pandas`, `numpy`, `pydantic`,
   `pyyaml`, `typer`, `rich`.
7. The bespoke engine source under `src/forex_bot/` is **not modified**
   by this sprint. The verifier package does not import from it.
8. The frozen CAMPAIGN_002 rules in
   `research/lean_parity/lean_parity_config.json` (and the mapping
   spec) are **read-only** inputs. No edit.
9. Validators must pass on every commit: pytest, ruff, archive
   validator, freeze checker, secret scanner.
10. No reopening of the QuantConnect / LEAN path.

## 4. Artifact discovery — local state at sprint start

| artifact | committed in repo? | locally present? | role |
|---|---|---|---|
| `data/oanda_h4_research.sqlite3` (seven-pair H4 store) | no (gitignored) | **NO** — only an empty directory + `.gitkeep` | optional input; verifier event loop can read CSVs directly |
| `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` (7 files) | no (gitignored) | **NO** — only the `*.provenance.json` files are present | primary input for the event-loop verifier |
| `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.provenance.json` (7 files) | **yes** | yes | hashes pinning the absent CSVs |
| `research/lean_parity/campaign_002_h4_bespoke_reference.json` (1,647 trades) | **yes** | yes | comparison reference |
| `research/lean_parity/campaign_002_h4_spec.md` (rules) | **yes** | yes | rule source (with the noted caveat that the spec table is stale; `lean_parity_config.json` is authoritative) |
| `research/lean_parity/lean_parity_config.json` (authoritative params) | **yes** | yes | parameter source |
| `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` (precise mechanics) | **yes** | yes | rule source — primary |
| `docs/research/LEAN_PARITY_COMPARISON_METHOD.md` (tolerances + taxonomy) | **yes** | yes | comparison spec |

**Consequence.** The seven-pair H4 candle CSVs and the SQLite store
are **absent locally**. The verifier sprint therefore cannot run a
full seven-pair verification end-to-end on this branch as the
artifacts ship. Per the plan rules, this is **not** a sprint-killer:
the verifier package + fixture tests + comparison harness are all
buildable without the bulk data, and the full data run becomes the
explicit BLOCKED status that Phase 5/8 records. If the user
regenerates the CSVs locally later (via `EXPORT_MANIFEST.md`'s
`scripts/export_lean_parity_data.py`), the verifier can be run end-to-end
without further code changes.

## 5. Implementation phases

| phase | scope | deliverables |
|---|---|---|
| Phase 0 | baseline & artifact discovery (this doc) | plan doc |
| Phase 1 | package skeleton, models, interface tests | `research/parity_verifier/` package; model tests |
| Phase 2 | indicator fixture verifier (EMA / ATR / Donchian) | independent indicators + fixture tests + fixture doc |
| Phase 3 | rule fixture verifier (entry / exit / stop / trailing / sizing) | rules module + fixture tests + fixture doc |
| Phase 4 | minimal event loop + script entry point | `event_loop.py`, `scripts/run_free_local_parity_verifier.py`, event-loop status doc |
| Phase 5 | comparison harness vs bespoke reference + comparison doc | `compare.py`, `FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` |
| Phase 6 | verifier-side debugging pass (only if material divergence) | verifier-side fixes + updated docs |
| Phase 7 | evidence docs + EVIDENCE_INDEX / MANIFEST updates | status doc + index/manifest updates |
| Phase 8 | final validation + sprint summary | summary doc |

Each phase commits separately when files change, runs the full
validation suite, and never touches the safety invariants in §3.

## 6. Validation commands

Per-phase (where applicable):
- `python -m pytest -q` (full suite) — must remain at 388+ passes plus
  any new tests this sprint adds.
- `ruff check src tests scripts` (and `research/parity_verifier`
  once it exists).
- `python scripts/validate_research_archive.py`.
- `python scripts/check_research_freeze.py`.
- `python scripts/scan_artifacts_for_secrets.py`.

Direct loop refusal checks at the bookend phases (Phase 0 and Phase 8):
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` — must
  print the empty-registry refusal.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` — must
  print the empty-registry refusal.
- `python -m forex_bot.cli --help` — must continue to list no
  `live-loop` command.

## 7. Expected outputs

| output | path | committed? |
|---|---|---|
| Verifier package code | `research/parity_verifier/` | yes |
| Verifier unit / fixture tests | `tests/research/test_parity_verifier_*.py` | yes |
| Script entry point | `scripts/run_free_local_parity_verifier.py` | yes |
| Indicator fixture doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_INDICATOR_FIXTURES.md` | yes |
| Rule fixture doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_RULE_FIXTURES.md` | yes |
| Event-loop status doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_EVENT_LOOP_STATUS.md` | yes |
| Comparison doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_COMPARISON.md` | yes |
| Final status doc | `docs/research/FREE_LOCAL_PARITY_VERIFIER_STATUS.md` | yes |
| Sprint summary | `docs/research/INFRA_FREE_LOCAL_PARITY_VERIFIER_001_SUMMARY.md` | yes |
| Per-pair `parity_summary.json` from a full run | `research/parity_verifier/results/campaign_002_h4/parity_summary.json` | only if produced and small; otherwise gitignored |
| Per-pair trade CSV from a full run | `research/parity_verifier/results/campaign_002_h4/trades.csv` | gitignored (regenerable bulk) |

`research/parity_verifier/results/` will be added to `.gitignore` for
trade CSVs and any other bulky outputs; small JSON summaries may be
committed if produced.

## 8. Explicit statement on approval

Nothing this sprint produces can or does approve a strategy. The
verifier:

- does not edit `configs/approved_strategies.yaml`;
- does not change any campaign report or `EVIDENCE_MANIFEST.json`
  campaign verdict;
- does not call any broker / cloud / API;
- does not enable `paper-loop` or `demo-loop`;
- does not modify the bespoke engine code;
- does not change CAMPAIGN_002 parameters or rules;
- writes only **diagnostic** evidence (the verifier outputs are
  `strategy_evidence: false`, same as the LEAN-era parity diagnostics
  in `EVIDENCE_MANIFEST.json`).

A clean PASS would mean only: "two engines built from the spec,
without sharing code, agree on the numbers for a rejected strategy."
A divergence is **always** a finding to localize — never tuned away,
never hidden — and the bespoke engine is **not** modified to match the
verifier without an explicit human review on a separate branch.

## 9. Cross-links

- Retirement: [`QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`](QUANTCONNECT_LEAN_RETIREMENT_DECISION.md)
- Plan: [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
- Mapping spec: [`CAMPAIGN_002_LEAN_MAPPING_SPEC.md`](CAMPAIGN_002_LEAN_MAPPING_SPEC.md)
- Authoritative parameters: `research/lean_parity/lean_parity_config.json`
- Comparison tolerances + taxonomy:
  [`LEAN_PARITY_COMPARISON_METHOD.md`](LEAN_PARITY_COMPARISON_METHOD.md)
- Bespoke reference data:
  `research/lean_parity/campaign_002_h4_bespoke_reference.json`
- Frozen approved-strategy registry (stays empty):
  `configs/approved_strategies.yaml`
