# Walk-Forward Research Harness Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `research-walk-forward-harness-001`
**Base commit:** `8730566` (HEAD of `research-close-free-local-verifier-and-next-direction-001`)

Infrastructure sprint. Builds a reusable walk-forward harness that
future strategy candidates must pass before they can be considered
for paper / demo / live promotion. Per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§5.2, this is the **recommended next branch** because it is
strictly enabling: low overfitting risk, no new external
dependency, re-validates existing REJECTs, and raises the bar for
any future candidate.

> No strategy is approved. CAMPAIGN_002 remains REJECT. Paper /
> demo / live remain blocked. No QuantConnect / LEAN. No OANDA API
> calls. No new strategy campaign.

## 1. Purpose

Provide a single, well-tested **walk-forward fold-generation
library** + minimal **summary schema** + **dry-run CLI** that
future strategy campaigns can call. The library does not run any
backtest by itself — it produces fold specifications (train,
validation, test date windows), validates them (no overlap, no
leakage, minimum count), and renders summaries.

Strategy execution stays in the existing
`src/forex_bot/backtesting/` engine. The harness sits on top.

## 2. Non-goals

- **Not a strategy.** This sprint does not write strategy code, run
  a backtest, or produce trade outputs.
- **Not a CAMPAIGN_002 revival.** CAMPAIGN_002 is used as a
  rejected-historical-example *only*, for retrospective
  metadata-only framing.
- **Not a parameter optimizer.** The harness emits folds; choosing
  parameters per fold is the strategy's job, not the harness's.
- **Not a leakage scanner for in-fold code.** The harness ensures
  *fold-level* leakage rules (no train → test overlap, etc.); it
  cannot prevent a strategy from peeking at future data inside a
  fold. That's the strategy's responsibility.
- **Not a paper / demo / live enabler.** Approval requires the full
  evidence package per
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8.

## 3. Safety invariants

1. `configs/approved_strategies.yaml` stays `approved: []`.
2. CAMPAIGN_002 remains REJECT. No re-run, no parameter tweak.
3. Paper / demo loops keep refusing; no `live-loop` command exists.
4. No QC / LEAN command. Retirement stands.
5. No OANDA API call. No `.env` read. No credential value printed.
6. No `*.sqlite3`, candle CSV, or bulky output gets staged.
7. The bespoke engine under `src/forex_bot/` is **not modified**.
8. The free / local verifier under `research/parity_verifier/` is
   not modified by this sprint (it is closed evidence).
9. No new external dependency is added.
10. Validators must pass on every commit.

## 4. Scope

| in scope | out of scope |
|---|---|
| Fold-definition models (train/validation/test date ranges; rolling vs expanding) | Strategy code, indicator code, signal generation |
| Split-generation algorithms (rolling, expanding) | Backtest execution |
| No-overlap and no-leakage validation at fold boundaries | Per-fold parameter optimization |
| Minimum-fold-count rule (at least 3 folds for any walk-forward result) | Per-fold report rendering of backtest results |
| Summary schema (JSON + markdown) of a fold plan | Producing actual fold-result PnL |
| Dry-run CLI entry point that prints the fold plan | Running a fold against any campaign |
| Tests on tiny date-only fixtures | New strategy or campaign |

## 5. Layout

| component | path |
|---|---|
| Harness package | `research/walk_forward/` |
| `__init__.py` | public re-exports |
| `models.py` | Pydantic models for fold spec, plan, summary |
| `splits.py` | rolling-window and expanding-window split generation |
| `validate.py` | no-overlap / no-leakage / minimum-fold-count checks |
| `reporting.py` | JSON + markdown summary rendering |
| `cli.py` or `scripts/run_walk_forward_dry_run.py` | dry-run entry point |
| `README.md` | usage + safety notes |
| Tests | `tests/research/test_walk_forward_*.py` |

Independence from `forex_bot` (mirrors the free / local verifier's
convention): the harness imports nothing from `src/forex_bot/`; a
grep-enforced test rail will guard it.

## 6. Implementation phases

| phase | scope |
|---|---|
| Phase 0 | baseline + plan (this doc) |
| Phase 1 | walk-forward research protocol doc |
| Phase 2 | harness skeleton (models, splits, validate, report, dry-run script) |
| Phase 3 | tests + fixtures |
| Phase 4 | CAMPAIGN_002 retrospective dry-run (metadata-only) |
| Phase 5 | STATUS doc + EVIDENCE_INDEX / MANIFEST updates |
| Phase 6 | final validation + sprint summary |

## 7. Expected outputs

| output | path | committed? |
|---|---|---|
| Plan (this doc) | `docs/research/WALK_FORWARD_HARNESS_001_PLAN.md` | yes |
| Protocol | `docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md` | yes |
| Harness package | `research/walk_forward/*.py`, `README.md` | yes |
| Tests | `tests/research/test_walk_forward_*.py` | yes |
| Dry-run script | `scripts/run_walk_forward_dry_run.py` | yes |
| CAMPAIGN_002 retrospective | `docs/research/CAMPAIGN_002_WALK_FORWARD_RETROSPECTIVE.md` | yes |
| STATUS doc | `docs/research/WALK_FORWARD_HARNESS_STATUS.md` | yes |
| Sprint summary | `docs/research/RESEARCH_WALK_FORWARD_HARNESS_001_SUMMARY.md` | yes |
| Updated EVIDENCE_INDEX / MANIFEST | `docs/research/EVIDENCE_INDEX.md`, `docs/research/EVIDENCE_MANIFEST.json` | yes |
| Dry-run outputs (if produced) | `/tmp/walk_forward_dry_run/` (outside repo) | no |

No `data/`, candle CSVs, or verifier-result paths touched.

## 8. Validation commands

Per phase (where applicable):
- `python -m pytest -q` — must remain at 481+ passes plus any new
  harness tests.
- `ruff check src tests scripts research/parity_verifier research/walk_forward`.
- `python scripts/validate_research_archive.py`.
- `python scripts/check_research_freeze.py`.
- `python scripts/scan_artifacts_for_secrets.py`.

At sprint bookends (Phase 0 and Phase 6):
- `python -m forex_bot.cli paper-loop -c configs/paper.yaml` — must
  refuse.
- `python -m forex_bot.cli demo-loop -c configs/practice.yaml` —
  must refuse.
- `python -m forex_bot.cli --help` — must continue to list no
  `live-loop`.

## 9. Explicit statement on approval

Nothing this sprint produces can or does approve a strategy. The
harness is **fold-generation infrastructure**. A future campaign
that uses it would still need its own pre-commit, backtest report,
walk-forward result, financing reconciliation, independent
corroboration, and human approval per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8.

The Phase 4 CAMPAIGN_002 retrospective is **metadata-only** — it
describes how the harness *would* frame an already-rejected
campaign; it does not run anything new and does not change
CAMPAIGN_002's REJECT verdict.

## 10. Cross-links

- Verifier closeout:
  [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
- Next research direction:
  [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- Research freeze:
  [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- Strategy approval process:
  [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
