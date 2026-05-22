# Infrastructure Lean-Parity Run Sprint 001 — Plan

**Date:** 2026-05-22 · **Branch:** `infra-lean-parity-run-001`
**Base commit:** `4ce37bb` (HEAD of `infra-lean-parity-001`)

## Purpose

The `infra-lean-parity-001` sprint made the repo parity-ready: the
seven-pair H4 store and Lean export bundle are complete, the Lean CLI is
installed, and the bespoke engine's CAMPAIGN_002 H4 baseline is
reproduced exactly. The one open item was the **Lean side** — no
faithful Lean algorithm existed.

This sprint **implements the faithful Lean parity algorithm** for the
already-REJECTED CAMPAIGN_002 H4 `trend_following` baseline and, if Lean
is locally runnable, executes an **offline local parity dry run** against
the exported seven-pair H4 data.

It is **verification of the measurement instrument** — the bespoke
backtest engine — not of a trading edge. **CAMPAIGN_002 remains REJECT**
regardless of any parity outcome.

## Non-goals

This sprint will **not**:

- run a new strategy campaign, hypothesis, or research decision;
- produce a strategy verdict or trading recommendation;
- approve any strategy, or edit `configs/approved_strategies.yaml`
  except to verify it stays empty (`approved: []`);
- tune any strategy parameter or change any CAMPAIGN_002 rule;
- change the bespoke strategy or engine to make parity "pass";
- paper / demo / live trade, or make any of those easier to run;
- submit, create, close, or modify any order;
- use live credentials, or any QuantConnect **cloud** service or paid
  tier;
- hide or tune away a divergence.

## Safety invariants (must hold at every commit)

1. `configs/approved_strategies.yaml` stays empty (`approved: []`).
2. `paper-loop`, `demo-loop`, and the live path refuse every strategy.
3. Backtesting / diagnostics stay available; loops stay gated.
4. No credential value is printed, logged, or committed; `.env` stays
   gitignored.
5. No `data/*.sqlite3` store and no bulky Lean output / candle CSV is
   committed.
6. No synthetic data is presented as real.
7. Prior campaign artifacts (CAMPAIGN_001–009) are immutable.
8. `pytest` and `ruff check src tests scripts` stay green.
9. Every new parity artifact is `strategy_evidence: false`.
10. The Lean CLI runs in an isolated venv that cannot disturb the
    forex-bot environment.

## Expected phases

| phase | deliverable |
|---|---|
| 0 | Baseline verification & this plan |
| 1 | Formal CAMPAIGN_002 → Lean mapping spec |
| 2 | Faithful local Lean parity algorithm |
| 3 | Pre-run comparison harness + fixtures |
| 4 | Local Lean dry-run attempt (or documented blocker) |
| 5 | Diagnose & fix parity *implementation* bugs (only if Lean runs and diverges) |
| 6 | Parity status finalization |
| 7 | Safety & final validation, summary |

Each phase commits separately. A blocked phase is documented and the
next independent phase proceeds. Phase 4 is gated on Lean being locally
runnable *and* the algorithm having enough fidelity to avoid misleading
output; Phase 5 runs only if Lean runs and diverges for implementation
reasons.

## Exact parity target

- **Strategy:** `trend_following 0.1.0-baseline-frozen`.
- **Timeframe:** H4 (17:00-NY aligned).
- **Universe:** the seven CAMPAIGN_002 instruments — EUR_USD, GBP_USD,
  USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD.
- **Window:** 2020-01-01 → 2026-05-20.
- **Fill timing:** `signal_bar_close` (CAMPAIGN_002 predates the
  next-bar-open model).
- **Cost model:** bid/ask-aware fills, 0.2 pip slippage, 0.5× spread
  (base regime); financing excluded (unmodeled in both engines).

## Exact source of truth

- **Strategy logic:** `src/forex_bot/strategies/trend_following.py`.
- **Engine behavior:** `src/forex_bot/backtesting/` (engine, fills).
- **Authoritative parameters:** `research/lean_parity/lean_parity_config.json`.
- **Bespoke reference numbers:** the custom-engine reproduction
  `backtests/diagnostics/custom_campaign_002_h4_parity.md` (which itself
  exactly reproduced `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`).
- **Data:** `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv`
  (gitignored; provenance JSONs committed).

## Tolerance philosophy

Parity is not bit-equality — Lean and the bespoke engine differ in fill
mechanics, indicator seeding, and bar handling. A parity run **passes**
when the independent engine *corroborates* the bespoke one within
documented tolerances (≥95% same entry bar, trade count ±5%, expectancy
±0.03 R, both engines REJECT). A **material** divergence outside
tolerance is a finding to **localize and fix on the Lean side** (if it
is a parity-implementation bug) or to **document as a real bespoke-engine
discrepancy** — never tuned away, never hidden. A FAIL is informative,
not a defeat.

## Validation commands

```bash
python3 -m pytest -q
ruff check src tests scripts
python3 scripts/validate_research_archive.py
python3 scripts/check_research_freeze.py
set -a && source .env && set +a && python3 scripts/scan_artifacts_for_secrets.py
bot paper-loop --config configs/paper.yaml --once   # exit 2
bot demo-loop  --config configs/practice.yaml --once # exit 2
grep -nE '^[^#]' configs/approved_strategies.yaml    # => approved: []
git status --short | grep -E '\.sqlite3|\.env|results/.*\.(csv|json)' || echo clean
```

## Why this cannot approve a strategy

CAMPAIGN_002 closed **REJECT** in Research Marathon 001. Parity checks
whether the *engine that produced that verdict* measured correctly — it
says nothing about the strategy. A parity PASS would mean only "the
bespoke engine and an independent engine agree on the numbers"; the
numbers themselves are a rejected strategy's. `configs/approved_strategies.yaml`
stays empty; every order-capable loop still refuses. Nothing in this
sprint, and nothing in any parity result, approves a strategy or lifts
the research freeze.

## Phase 0 verification result

Performed 2026-05-22 on branch `infra-lean-parity-run-001`:

- Branch base `4ce37bb`; working tree clean. [verified]
- `configs/approved_strategies.yaml`: `approved: []`. [verified]
- `paper-loop` / `demo-loop` refuse (CLI exit 2). [verified]
- `validate_research_archive.py`, `check_research_freeze.py`,
  `scan_artifacts_for_secrets.py` — all pass. [verified]
- Local artifacts present: `data/oanda_h4_research.sqlite3` (seven pairs,
  NZD_USD = 9,935 H4 candles), seven Lean-export provenance JSONs, the
  custom-engine parity reproduction report. [verified]
- Lean available: `lean 1.0.225` in the isolated venv `/tmp/lean-venv`;
  Docker 29.1.3 present; no cloud login required. [verified]
- Targeted approval/guard pytest (60) pass; `ruff check` clean.
  [verified]

Phase 0 safety verification: **all invariants hold.**
