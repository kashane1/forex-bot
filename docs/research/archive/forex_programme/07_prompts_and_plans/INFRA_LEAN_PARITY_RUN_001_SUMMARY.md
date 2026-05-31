# Infrastructure Lean-Parity Run Sprint 001 — Summary & Handoff

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-run-001`
**Base commit:** `4ce37bb` (HEAD of `infra-lean-parity-001`)

This sprint implemented the **faithful Lean parity algorithm** for the
already-REJECTED CAMPAIGN_002 H4 `trend_following` baseline and built
the full comparison harness. The local Lean backtest itself could not
be run — `lean init` requires a QuantConnect account, which the sprint
rules forbid. It is **not** a strategy campaign; **CAMPAIGN_002 remains
REJECT**; the research freeze is intact.

## What changed

**New script**
- `scripts/compare_lean_campaign_002_parity.py` — compares a Lean parity
  result against the bespoke reference within documented tolerances.

**Improved script**
- `scripts/run_custom_campaign_002_h4_parity.py` — added `--no-risk-engine`
  and `--json` so the parity-isolation reference is reproducible.

**New Lean artifact**
- `research/lean_parity/algorithms/campaign_002_h4_baseline/` — the
  faithful Lean Python algorithm (`main.py`), project `config.json`,
  and `README.md`.

**New reference**
- `research/lean_parity/campaign_002_h4_bespoke_reference.json` — the
  no-RiskEngine bespoke reference (1,647 trades).

**New docs** — the sprint plan, the bespoke→Lean mapping spec, the Lean
algorithm implementation notes, the comparison method, and this summary.

**Updated docs** — `LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`,
`CAMPAIGN_002_H4_PARITY_STATUS.md`, `EVIDENCE_INDEX.md`.

**Tests** — 17 new tests; the full suite is **388 passed**.

## What did NOT change

- `configs/approved_strategies.yaml` remains empty (`approved: []`).
- No strategy approved; no campaign, hypothesis, verdict, or
  recommendation; no parameter tuned.
- `paper-loop`, `demo-loop`, and the live path still refuse.
- The bespoke strategy and engine were **not** changed for parity.
- Prior campaign artifacts (CAMPAIGN_001–009) untouched.
- No order submitted; no live credentials; no QuantConnect cloud, no
  account created, no paid service.
- Financing remains estimated / stress-only — standing live blocker.
- CAMPAIGN_002 remains **REJECT**.

## Lean algorithm status

A faithful Lean algorithm is **authored** —
`research/lean_parity/algorithms/campaign_002_h4_baseline/main.py` — a
direct port of the strategy + engine mechanics per the mapping spec
(EMA 50/200 regime, Donchian-20 prior-bar breakout, ATR stop / trailing
stop, exit precedence, 240-bar time stop, `signal_bar_close` fills,
0.25%-risk sizing), using Lean's own EMA / ATR indicators.

It is **not yet validated** — authored offline, never executed against
Lean. `LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md` records every
approximation and the Lean-mechanics differences a first run will
surface.

## Lean run status

**Blocked — not executed; no result fabricated.** `lean init` (the
standard step to scaffold a Lean workspace) requires QuantConnect
account credentials and aborts without them. The sprint rules forbid
using QuantConnect cloud or requiring such credentials, so this sprint
did not authenticate; without a workspace `lean backtest` cannot run.
Full detail and the exact next steps:
`docs/research/LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`.

## Parity comparison status

**Not run** — there is no Lean result to compare. The comparison harness
`scripts/compare_lean_campaign_002_parity.py` is written and tested
(11 fixture tests) and will run the moment a Lean `parity_summary.json`
exists. The bespoke side of the comparison is fully prepared: the
no-RiskEngine reference (1,647 trades) and the exact with-RiskEngine
reproduction (1,032 trades).

## Validation results

- `pytest` — **388 passed**.
- `ruff check src tests scripts` — clean.
- `scripts/validate_research_archive.py` — all checks pass.
- `scripts/check_research_freeze.py` — all checks pass.
- `scripts/scan_artifacts_for_secrets.py` — PASSED.
- `bot paper-loop` / `bot demo-loop` — both refuse (exit 2).
- `configs/approved_strategies.yaml` — `approved: []`.
- No `*.sqlite3` store, no `.env`, no bulky Lean output / candle CSV
  staged.

## Safety state

The research freeze is **intact**. The approved-strategy registry is
empty; every order-capable loop refuses; no credential leaked; the
bespoke engine and prior evidence are unchanged; every new parity
artifact is `strategy_evidence: false`. No QuantConnect account was
created and no cloud service was used. The Lean CLI remains in an
isolated venv.

## Local files created but NOT committed

- `data/oanda_h4_research.sqlite3` — the seven-pair H4 store (unchanged
  this sprint). Gitignored.
- `research/lean_parity/exports/campaign_002_h4/*.csv` — the seven Lean
  candle CSVs (gitignored, regenerable).
- `/tmp/lean-venv/` — the isolated Lean CLI venv. Outside the repo.

## Remaining blockers

1. **The Lean backtest is unrun** — `lean init` requires a QuantConnect
   account. Completing the parity run is a deliberate human decision to
   create a (free) QuantConnect account, outside this sprint's
   no-cloud-credential rule.
2. **The Lean algorithm is not yet validated** — even once a workspace
   exists, the first run is expected to need a debugging iteration
   (custom-data path, resolution, slice semantics).
3. **Financing is estimated / stress-only** — standing live blocker,
   unchanged.

## Recommended next human decision points

1. Decide whether to create a free QuantConnect account so `lean init`
   can scaffold a workspace, then run the committed algorithm and feed
   the result to `scripts/compare_lean_campaign_002_parity.py`. This is
   the one remaining step to close independent-engine parity.
2. If the Lean run diverges, treat it per `LEAN_PARITY_COMPARISON_METHOD.md`:
   localize a Lean-side parity bug (fix it) or a real bespoke-engine
   discrepancy (document it) — never tune it away.
3. The research freeze stands. The bespoke engine is internally
   reproducible (exact CAMPAIGN_002 reproduction), but not yet
   corroborated by an independent engine — and even a full parity PASS
   would approve nothing.

## Files to review first

1. `docs/research/INFRA_LEAN_PARITY_RUN_001_PLAN.md` — the sprint plan.
2. This summary.
3. `docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md` — the bespoke→Lean
   mapping.
4. `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py` —
   the Lean algorithm, with `LEAN_ALGORITHM_IMPLEMENTATION_NOTES.md`.
5. `docs/research/LEAN_PARITY_CAMPAIGN_002_BLOCKED.md` — the run blocker.
