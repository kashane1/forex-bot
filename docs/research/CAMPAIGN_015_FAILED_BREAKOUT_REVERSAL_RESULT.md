# CAMPAIGN_015 Walk-Forward Result — `failed_breakout_reversal 0.1.0-c015`

**Date:** 2026-05-25 · **Branch:** `research-failed-breakout-reversal-campaign-015`
**Verdict:** `BLOCKED`

> **No strategy approved. `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live loops remain blocked.
> CAMPAIGN_001-014 verdicts are untouched.**

## 1. Outcome

The CAMPAIGN_015 walk-forward run is classified **`BLOCKED`** on the
binding Phase 0 §13 BLOCKED-conditions. The bespoke engine did **not**
execute any backtest. No fold-level metrics exist; no aggregate
expectancy was computed; no per-fold trades were written.

The runner's classification is the Phase 0 §13 outcome:

> If data required for a run is absent, write a BLOCKED artifact. Do
> not fabricate results.

This document is the canonical Phase 3 artifact and is consumed by
Phase 4 (which inherits BLOCKED) and Phase 7 (which records BLOCKED
in `STRATEGY_STATUS.md` and `EVIDENCE_MANIFEST.json`).

## 2. Blocked reason (verbatim from the runner)

```
{
  "verdict": "BLOCKED",
  "blocked": true,
  "blocked_reasons": [
    "database_path does not exist: data/campaign_002.sqlite3"
  ]
}
```

(Source: `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/gate_result.json`,
generated `2026-05-25T19:47:40Z`.)

The expected real-OANDA-practice H4 candle store at
`./data/campaign_002.sqlite3` (the same physical store consumed by
CAMPAIGN_002 / 010 / 011 / 012 / 013 / 014) is **not present** in
this worktree. The Phase 0 audit (`docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_PRECOMMIT.md`
§15) recorded the same state before any code was written.

## 3. What the runner did do (the artifact skeleton)

The Phase 2 runner satisfied its binding contract under the BLOCKED
branch:

* Constructed the rolling walk-forward plan in-process (8 folds,
  540 / 180 / 180 / 180 days, ROLLING, FROZEN, `strategy_evidence =
  false`); the plan is written to
  `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/plan.json`.
* Ran the read-only local-data preflight; the preflight finding is
  recorded in `walk_forward/preflight.json`.
* Asserted the YAML frozen parameters match the Phase 0 §5 table
  via `_assert_frozen()`; no deviation.
* Wrote `walk_forward/gate_result.json` with `verdict = "BLOCKED"`
  and an itemized `blocked_reasons` list.
* Did **not** open the sealed final test window. Did **not** call
  the broker. Did **not** make a network request. Did **not** write
  any per-fold or per-pair trade summary (no engine invocation).

## 4. Posture / safety verification (binding)

| invariant | state |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (byte-stable) |
| `failed_breakout_reversal` in the registry | **No** |
| Paper-loop refuses every configured strategy | **Yes** |
| Demo-loop refuses every configured strategy | **Yes** |
| OANDA live credentials used | **No** |
| OANDA practice credentials used | **No** (no network call) |
| LEAN / QuantConnect imports | **None** |
| Backtrader OANDA / live-broker imports | **None** |
| Runner imports `forex_bot.broker` | **None** |
| Broker order submitted / modified / cancelled | **None** |
| Historical campaign artifacts mutated | **None** |
| CAMPAIGN_001-014 manifest entries changed | **No** |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `scan_artifacts_for_secrets.py` | PASS (pattern scan) |

## 5. What this verdict means for the verdict ceiling

The Phase 0 §16 verdict ceiling stands:

> The maximum possible verdict for CAMPAIGN_015 is
> `PASS_RESEARCH_SCREEN`. It is not an approval path.

A `BLOCKED` outcome is **not** a rejection of the failed-breakout-
reversal hypothesis — it is the absence of evidence in this
worktree's local data store. Re-running this campaign in a worktree
that has the canonical `data/campaign_002.sqlite3` (the OANDA
practice H4 store hashed against CAMPAIGN_002 / 010-014 lineage)
would produce per-fold metrics and a verdict in the actual gate
domain (PASS_RESEARCH_SCREEN / REJECT). That is a separate sprint;
this sprint records the BLOCKED state and stops cleanly.

## 6. What is **not** in this document

* No per-fold expectancy numbers, no aggregate R, no profit factor,
  no return %, no fold-pass-rate. The runner produced none of these.
* No null-baseline comparison (Phase 4 inherits BLOCKED).
* No Backtrader corroboration (Phase 5 / 6 inherit BLOCKED).
* No approval recommendation. No promotion to paper / demo / live.
* No tuning of frozen parameters. No retry. No fixture / data
  fabrication.

## 7. Files produced by Phase 3

| file | role |
|---|---|
| `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/plan.json` | in-process rolling plan; 8 folds rolling / frozen / strategy_evidence=false |
| `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/preflight.json` | read-only local-data preflight finding (DB path does not exist) |
| `backtests/CAMPAIGN_015_failed_breakout_reversal/walk_forward/gate_result.json` | machine-readable verdict (`BLOCKED`) consumed by Phase 4 + Phase 7 |
| `docs/research/CAMPAIGN_015_FAILED_BREAKOUT_REVERSAL_RESULT.md` | this document |

## 8. Reproduction

```
OANDA_ACCOUNT_ID_PRACTICE=test \
OANDA_ACCESS_TOKEN_PRACTICE=test \
python scripts/run_campaign_015.py \
  --config configs/campaign_015_failed_breakout_reversal.yaml \
  --out backtests/CAMPAIGN_015_failed_breakout_reversal
```

Exits 0; writes `gate_result.json` with `verdict: BLOCKED`; makes no
broker call; does not touch `configs/approved_strategies.yaml`.

## 9. Disposition

* CAMPAIGN_015 is recorded as **BLOCKED** in the evidence manifest.
* `STRATEGY_STATUS.md` records `failed_breakout_reversal 0.1.0-c015`
  as `blocked` (cannot be validly tested with current local data),
  not `rejected` and not `research-only — pass`.
* No promotion path. No registry edit. No loop config edit.
* A future sprint that obtains the canonical OANDA-practice H4 store
  may re-run the runner unchanged; the frozen parameters guarantee
  comparability across re-runs.
