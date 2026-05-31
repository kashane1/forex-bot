# Infrastructure Lean-Parity Sprint 001 — Summary & Handoff

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-001`
**Base commit:** `bf4ec44` (HEAD of `oanda-practice-readonly-001`)

This sprint completed **independent-engine parity readiness** for the
CAMPAIGN_002 H4 baseline: the seven-pair data and Lean export are
complete, the Lean CLI is installed, and the custom-engine side of the
parity is reproduced exactly. It is **not** a strategy campaign — no
order was submitted, no strategy approved, no verdict produced, and the
research freeze is intact. CAMPAIGN_002 remains **REJECT**.

## What changed

**New script**
- `scripts/run_custom_campaign_002_h4_parity.py` — reproduces the
  CAMPAIGN_002 H4 baseline on the bespoke engine for parity.

**Improved scripts**
- `scripts/rehydrate_oanda_h4_store.py` — added an `--instruments`
  option (fetch / verify / report a custom universe).
- `scripts/audit_h4_data_quality.py` — added `--instruments`; the report
  header now detects the git branch at runtime (was hardcoded).

**New docs** — the sprint plan, the NZD_USD rehydration result, the
seven-pair data-quality audit, the Lean dry-run blocker, the parity
status report, and this summary.

**Updated docs / manifests** — `LEAN_PARITY_EXECUTION_GUIDE.md`,
`LEAN_PARITY_LOCAL_STATUS.md`, the Lean `EXPORT_MANIFEST.md`,
`EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`.

**New diagnostic artifact** — `backtests/diagnostics/custom_campaign_002_h4_parity.md`.

**Tests** — 7 new tests added; the full suite is **377 passed**.

## What did NOT change

- `configs/approved_strategies.yaml` remains empty (`approved: []`).
- No strategy is approved; no campaign was run; no trading verdict or
  recommendation was produced; no parameter was tuned; no new hypothesis
  was run.
- `paper-loop`, `demo-loop`, and the live path still refuse every
  strategy.
- Prior campaign artifacts (CAMPAIGN_001–009) are untouched.
- No order was submitted, created, modified, or closed.
- No live credentials were used; the live host was never contacted.
- Financing remains **estimated / stress-only** — a standing hard live
  blocker, unchanged.
- CAMPAIGN_002 remains **REJECT**.

## Seven-pair H4 data status

The local real-OANDA practice H4 store now holds the **full seven-pair
CAMPAIGN_002 universe** — the six majors plus **NZD_USD**, newly fetched
this sprint (9,935 completed H4 candles, 2020-01-01 → 2026-05-19, 0
incomplete, full bid/ask). The seven-pair data-quality audit found
**all 7 pairs acceptable** for diagnostics / parity: 0 incomplete, 0
duplicates, full bid/ask, only expected weekend / holiday gaps.

The freshly-rehydrated store's normalized candle hashes **match the
hashes recorded in the committed CAMPAIGN_002 report** — the data is
provably the same candles CAMPAIGN_002 used.

## Lean export status

The CAMPAIGN_002 H4 Lean export bundle is **complete for all seven
pairs** (69,522 candles total). Seven `*_H4_lean.provenance.json`
sidecars and the `EXPORT_MANIFEST.md` are committed; the bulky candle
CSVs stay gitignored and uncommitted.

## Custom-engine parity reproduction status

`scripts/run_custom_campaign_002_h4_parity.py` re-ran the CAMPAIGN_002
H4 baseline on the bespoke engine, the committed campaign config, and
the seven-pair store, with CAMPAIGN_002's fill timing
(`signal_bar_close`) and the RiskEngine wired in.

**Result: an exact match to the committed CAMPAIGN_002 report** — all
seven pairs identical on trade count and expectancy R (Δ +0 trades,
Δ ±0.000 R each), 1,032 total trades vs 1,032 committed. The bespoke
engine's CAMPAIGN_002 H4 baseline is fully reproducible and hash-pinned.

## Lean local run status

**Lean CLI installed; the parity backtest was NOT run.** `pip install
lean` succeeded into an isolated venv (`lean 1.0.225`); Docker is
present. No Lean parity backtest was executed and no result fabricated.
The blocker (`LEAN_PARITY_CAMPAIGN_002_BLOCKED.md`):

1. No faithful Lean algorithm — `campaign_002_h4_spec.md` is a
   spec-only skeleton; the signal / exit / sizing / custom-data logic
   is unwritten. Authoring a *verified-faithful* reimplementation is a
   deliberate, review-gated task; a rushed one yields misleading
   divergence, which this sprint forbids.
2. The `quantconnect/lean` Docker engine image is not yet pulled.

## Safety state

The research freeze is **intact**. The approved-strategy registry is
empty; every order-capable loop refuses; backtests / diagnostics remain
available; no credential leaked; prior evidence is untouched; every new
diagnostic / parity artifact is `strategy_evidence: false`. The Lean CLI
was installed in an isolated venv that cannot disturb the forex-bot
environment.

## Validation results

- `pytest` — **377 passed**.
- `ruff check src tests scripts` — clean.
- `scripts/validate_research_archive.py` — all checks pass (55
  evidence-index links resolve; diagnostic artifacts strategy_evidence
  false).
- `scripts/check_research_freeze.py` — all checks pass.
- `scripts/scan_artifacts_for_secrets.py` — PASSED.
- `bot paper-loop` / `bot demo-loop` — both refuse (exit 2).
- `configs/approved_strategies.yaml` — `approved: []`.
- No `*.sqlite3` store, no `.env`, no bulky candle CSV staged.

## Local files created but NOT committed

- `data/oanda_h4_research.sqlite3` — NZD_USD added; the store now holds
  ~69,522 H4 candles across seven pairs. Gitignored.
- `research/lean_parity/exports/campaign_002_h4/NZD_USD_H4_lean.csv`
  (and the six prior CSVs) — gitignored, regenerable.
- `/tmp/lean-venv/` — the isolated Lean CLI venv (`lean 1.0.225`).
  Outside the repo; session-local working install.

## Remaining blockers

1. **No faithful Lean algorithm + no Docker engine image** — blocks the
   actual Lean parity backtest. Authoring a verified-faithful
   CAMPAIGN_002 Lean algorithm is a deliberate, review-gated human task.
2. **Financing is estimated / stress-only** — a standing hard live
   blocker, unchanged; out of scope here.

## Recommended next human decision points

1. Decide whether to commission the **faithful Lean algorithm** —
   authored from `campaign_002_h4_spec.md` and reviewed for fidelity —
   then run the local Lean backtest and compare against the committed
   custom-engine reproduction. This is the one remaining step to close
   independent-engine parity.
2. The research freeze stands. The exact custom-engine reproduction of
   CAMPAIGN_002 corroborates the bespoke engine's internal
   reproducibility, but **not** by an independent engine yet — and even
   a full parity PASS would approve nothing. Lifting the freeze remains
   a separate, deliberate, evidence-backed human decision per
   `docs/research/STRATEGY_APPROVAL_PROCESS.md`.

## Files to review first

1. `docs/research/INFRA_LEAN_PARITY_001_PLAN.md` — the sprint plan.
2. This summary.
3. `docs/research/CAMPAIGN_002_H4_PARITY_STATUS.md` — the parity status.
4. `backtests/diagnostics/custom_campaign_002_h4_parity.md` — the exact
   custom-engine reproduction.
5. `docs/research/LEAN_PARITY_CAMPAIGN_002_BLOCKED.md` — the remaining
   Lean-side blocker.
