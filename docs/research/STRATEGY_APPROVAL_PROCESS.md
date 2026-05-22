# Strategy Approval Process

**Date:** 2026-05-22 · **Branch:** `infra-research-foundation-001` · Phase 5

> **No strategy is approved.** `configs/approved_strategies.yaml` is
> empty; every paper / demo / live loop refuses to start. This document
> defines what a human must do to ever change that. It does **not**
> approve anything, and this sprint adds **no** approval entry.

## 1. Why no strategy is currently approved

Nine campaigns across five strategy families produced no edge that
cleared its pre-committed gates (see
`docs/research/FINAL_RESEARCH_DECISION_MEMO.md`). The research is frozen.
The approved-strategy registry is therefore empty, and the loop guard
(`forex_bot.approval`) refuses every loop.

Approval is **opt-in, deliberate, and reviewed.** It never happens by
default, by a tweak, or as a side effect.

## 2. The approval registry and entry schema

The registry is `configs/approved_strategies.yaml`:

```yaml
approved: []   # empty — nothing approved
```

To approve a strategy, a human adds one **approval entry** to the
`approved` list. Each entry is validated by `forex_bot.approval`
against this schema — a malformed entry makes every loop fail closed:

| field | meaning |
|---|---|
| `strategy_id` | strategy family — one of `trend_following`, `volatility_breakout`, `pullback_continuation`, `mean_reversion` |
| `version` | the exact strategy version approved (e.g. `0.2.0-c009`) |
| `allowed_mode` | exactly one of `paper`, `demo`, `live` — one entry permits one mode |
| `approved_by` | the human who signed off (name / identifier) |
| `approval_date` | ISO date the approval was granted |
| `expiry_date` | ISO date the approval lapses (must be after `approval_date`) |
| `evidence_report` | repo-relative path to the campaign report that earned the approval — the file must exist |
| `max_risk_per_trade_pct` | per-trade risk ceiling for this approval, in (0, 0.5] |
| `notes` | optional free text |

The registry validation rejects: bare strings, missing or unknown
fields, unknown `strategy_id`, a missing `evidence_report` file, an
`expiry_date` not after `approval_date`, and out-of-bounds risk. An
**expired** entry parses but approves nothing. A `paper` entry unlocks
**only** the paper loop; demo and live each need their own entry. A
`live` entry is honoured only when the existing config-layer live gates
have also passed.

## 3. Minimum evidence required before PAPER-TRADE-ONLY

A strategy may be considered for a `paper` approval entry **only** if
**all** of the following hold:

1. A **fresh, pre-committed campaign** — its pass/fail gates written and
   committed *before* the run.
2. The campaign **passed every screening gate** and, with the test
   lockbox opened, **every test-window gate** — on real OANDA data.
3. The result earns at most **PAPER-TRADE-ONLY** (live is never earned
   by a backtest).
4. **Cost-stress survival** — positive expectancy at the 2× cost regime.
5. **Financing-stressed** expectancy is non-negative; the financing
   treatment is at least `estimated` (see
   `docs/research/FINANCING_MODEL_DESIGN.md`).
6. **Out-of-sample breadth** — the edge holds across multiple pairs and
   the train/validation/test splits, not one lucky window.
7. The campaign report, pre-commit, and artifacts are committed and
   pass `scripts/validate_research_archive.py`.

No campaign to date (CAMPAIGN_001–009) meets bar 2 — none passed its
gates. That is why the registry is empty.

## 4. Approval procedure — human signoff steps

1. **Confirm the evidence.** A reviewer (not the campaign's author)
   independently reads the campaign report and pre-commit and confirms
   §3 is satisfied with no gate relaxed after the fact.
2. **Write the entry.** Add one `ApprovalEntry` to
   `configs/approved_strategies.yaml` with `allowed_mode: paper`, a real
   `evidence_report` path, a conservative `max_risk_per_trade_pct`, the
   reviewer in `approved_by`, and an `expiry_date` no more than ~90 days
   out (approvals must be re-earned, not permanent).
3. **Validate.** `scripts/validate_research_archive.py` and the
   `forex_bot.approval` tests must pass with the entry present.
4. **Commit** the registry change on its own, clearly-described commit,
   referencing the evidence report and the reviewer.
5. The paper loop will now accept that strategy. Demo and live remain
   refused until their own entries exist.

## 5. Required config changes

- The approval entry itself in `configs/approved_strategies.yaml`.
- The operating config (`configs/paper.yaml`) must enable exactly the
  approved `strategy_id` at the approved `version`, and set
  `risk.risk_per_trade_pct` at or below the entry's
  `max_risk_per_trade_pct`.
- No order-submission or live flags change for a `paper` approval —
  paper mode cannot submit orders by construction.

## 6. Required forward paper-trading plan

Before approval, write a plan covering:

- the paper-trading horizon (a minimum number of weeks / trades);
- the metrics tracked live vs. the backtest expectation (expectancy,
  win rate, drawdown, spread paid, rejection rate);
- the divergence thresholds that would pause or revoke the approval;
- who reviews the weekly paper report and when.

## 7. Required rollback plan

Approval must ship with a rollback path:

- **Immediate stop:** `touch KILL_SWITCH` halts all loops; removing the
  approval entry (or letting it expire) makes every loop refuse again.
- A documented trigger list — what observed behaviour forces a rollback
  (drawdown breach, divergence from backtest, reconciliation failure).
- Rollback is reverting the registry to `approved: []` and committing
  that revert. The guard then returns to the frozen state.

## 8. Required monitoring and reporting

- The weekly report (`bot report weekly`) must be reviewed for every
  week the strategy is paper-trading.
- Per-signal risk rejections continue to be exported and audited.
- Any divergence beyond the plan's thresholds pauses the approval.

## 9. Why live trading is a separate, later decision

A `paper` approval is **not** a step toward live on a timer. Live
trading additionally requires, as wholly separate decisions:

- a **modeled** (not merely estimated) financing treatment — the
  current hard live blocker;
- every existing config-layer live gate (`allow_live_trading`, the
  acknowledgement phrase, the manually approved config hash);
- a separate, explicit `live` approval entry, earned by demo-trading
  evidence, not by a paper result;
- an independent human decision to accept real capital risk.

The approval registry makes paper trading *possible to authorize
safely*. It does not make live trading any nearer.

## 10. How the guard enforces this

`forex_bot.approval` loads and validates the registry; the loop entry
points (`run_paper_loop`, `run_practice_loop`) call
`assert_loop_strategies_approved` before doing any work. Backtesting and
research are never gated — only signal-emitting / order-capable loops.
The behaviour is unit-tested by `tests/unit/test_approval.py` and
`tests/unit/test_approved_strategies.py`.
