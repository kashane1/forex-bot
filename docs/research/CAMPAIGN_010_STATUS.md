# CAMPAIGN_010 — Status

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-001`
`strategy_evidence: false`

Status of the **CAMPAIGN_010 research candidate** at the close
of the scaffold sprint.

> ## Candidate scaffold only. No verdict. No approval.
>
> - No backtest verdict yet (only a fixture / config-load smoke
>   may be recorded in [`CAMPAIGN_010_SMOKE_RESULT.md`](CAMPAIGN_010_SMOKE_RESULT.md);
>   a smoke result is **not** a verdict).
> - No paper / demo / live; the candidate is deliberately absent
>   from [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml).
> - **No strategy approval.** Approval requires a separate,
>   reviewed, human action per
>   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).
> - **CAMPAIGN_002 remains REJECT and is unrelated** to this
>   candidate; the candidate uses **no** CAMPAIGN_002 strategy
>   parameter (verified by the no-lookahead structural test in
>   [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py)).

## 1. What this sprint produced

| component | status |
|---|---|
| Sprint plan | committed: [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md) |
| Implementation spec | committed: [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md) |
| Strategy module | committed: [`src/forex_bot/strategies/session_breakout.py`](../../src/forex_bot/strategies/session_breakout.py) |
| StrategyConfig sub-model | committed: [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`SessionBreakoutStrategyConfig`, `StrategyConfig.session_breakout`) |
| Strategy re-export | committed: [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py) |
| Unit tests | committed: [`tests/unit/test_session_breakout.py`](../../tests/unit/test_session_breakout.py) — 33 cases pass |
| Research config | committed: [`configs/campaign_010_session_breakout.yaml`](../../configs/campaign_010_session_breakout.yaml) |
| Pre-commit checklist | committed: [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md) |
| Smoke result | pending (Phase 5) |
| Walk-forward readiness | pending (Phase 6) |
| Financing + risk readiness | pending (Phase 6) |
| Sprint summary | pending (Phase 7) |

## 2. What is **not** produced (by design, out of scope)

| artifact | why deferred |
|---|---|
| Walk-forward `plan.json` / `plan.md` | future evidence sprint; this sprint only proves *readiness*. |
| Per-fold backtest results | future evidence sprint. |
| Financing overlay `financing_run.json` / `.md` | future evidence sprint; ESTIMATED-only is the v1 plan. |
| Campaign report (`backtests/CAMPAIGN_010_SESSION_BREAKOUT_REPORT.md`) | future evidence sprint. |
| Independent corroboration | future verifier-extension or deterministic-replay sprint. |
| Approval record in `configs/approved_strategies.yaml` | **never** automatically; requires a reviewed human action per [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md). |

## 3. Headline result

**Candidate scaffold complete. No backtest evidence produced.
No verdict possible from this sprint.**

The candidate:

- has a `Strategy`-protocol-conforming implementation;
- has a `StrategyConfig` sub-model with strict validation;
- has 33 unit + structural-audit tests pinning rules R1–R11,
  no-lookahead, no broker imports, no CAMPAIGN_002 parameter
  inheritance, no approval-shaped fields on emitted `Signal`s,
  and the `approved_strategies.yaml` registry stays empty;
- has a research-only candidate YAML config that loads via
  `forex_bot.config.load_settings(...)` and would drive the
  bespoke `BacktestEngine` *if and when* a future evidence
  sprint authorises a backtest run;
- has explicit documentation of its DST limitation (the
  fixed-UTC session windows yield one eligible London bar per
  pair per trading day under both NY-standard and NY-DST H4
  alignments) and the rationale for the frozen parameter set.

## 4. Headline non-result

- **No expectancy claim.** None has been produced.
- **No pair-level result.** No pair has been backtested.
- **No walk-forward result.** No fold has been run.
- **No financing overlay number.** None has been computed.
- **No verdict.** CAMPAIGN_010 has *neither* PASS *nor* REJECT
  status — it is **scaffold only**.

## 5. Safety state (unchanged from Phase 0)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 verdict | **REJECT** (untouched) |
| `session_breakout` in approved registry | **no** |
| `session_breakout` in any active loop | **no** |
| paper-loop / demo-loop refuse | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| broker / OANDA call this sprint | none |
| `.env` read this sprint | none |
| credential printed this sprint | none |
| engine-PnL change | none |
| `src/forex_bot/financing.py` change | none |
| `MODELED` financing reachable | no (four refusal layers) |
| live-promotion financing blocker | stands |
| pytest baseline preserved | **735 passes** (702 prior + 33 new) |

## 6. Recommended next sprints

- `research-asian-london-session-breakout-walk-forward-001` —
  generate + commit the walk-forward plan; run per-fold
  backtests; emit `WalkForwardResults`; record gate verdicts.
- `research-financing-multi-year-fixture-expansion-001` — extend
  the per-pair `TableRateSource` fixtures from 2 weeks to full
  2020–2026 universe (optional; current plan uses
  `default_stress_rate_source()` per design §10.1 Option 1).
- `infra-ruff-up042-stress-enum-001` — clean up the 11
  pre-existing UP042 errors (carried forward; documented in
  Phase 0 of this sprint).

## 7. Cross-links

- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md`](ASIAN_LONDON_SESSION_BREAKOUT_001_PLAN.md)
- [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md)
- [`PREFERRED_CANDIDATE_EVALUATION_DESIGN.md`](PREFERRED_CANDIDATE_EVALUATION_DESIGN.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
