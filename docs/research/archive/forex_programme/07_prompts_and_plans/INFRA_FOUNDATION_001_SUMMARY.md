# Infrastructure Foundation Sprint 001 — Summary

**Date:** 2026-05-22 · **Branch:** `infra-research-foundation-001`
**Base commit:** `8c76dec` (the research-freeze HEAD)
**Outcome:** the repo is a stronger, auditable research / backtesting
platform. **No strategy was run, approved, or traded.**

This is the close-out of the sprint planned in
`docs/research/INFRA_FOUNDATION_001_PLAN.md`. All six phases completed;
none was blocked.

## What changed, by phase

| phase | commit | deliverable |
|---|---|---|
| 0 | `d1760f0` | Baseline safety audit; `INFRA_FOUNDATION_001_PLAN.md`. |
| 1 | `e5bd816` | H4→D1 aggregation (`backtesting/d1_aggregation.py`), `scripts/aggregate_h4_to_d1.py`, a `D1AGG` granularity, 10 tests, `D1_AGGREGATION_DESIGN.md`, a real-data sample. |
| 2 | `adfabbc` | Financing-model interface (`FinancingTreatment`, `FinancingModel` + 3 implementations), `financing_metadata`, the approval gate `financing_treatment_blocks_approval`, 11 tests, `FINANCING_MODEL_DESIGN.md`. |
| 3 | `af28783` | `LEAN_PARITY_DESIGN.md` and the `research/lean_parity/` skeleton (README + CAMPAIGN_002 spec). Design only — Lean was not run. |
| 4 | `41afd5f` | `EVIDENCE_MANIFEST.json` (9 campaigns), `forex_bot.research_archive` + `scripts/validate_research_archive.py` (10 checks), 13 tests, `EVIDENCE_INDEX.md` updated. |
| 5 | `c3cef2f` | Schema-validated approval registry (`forex_bot.approval`, `ApprovalEntry`), `STRATEGY_APPROVAL_PROCESS.md`, 31 approval/guard tests. |
| 6 | (this commit) | README + runbooks updated; this summary. |

### Capability deltas

- **D1 research is now possible.** Native OANDA D1 stays invalid;
  `D1AGG` candles aggregated from H4 give a valid, rollover-safe daily
  research path. (The engine still lacks next-bar-open fills — noted.)
- **Financing has an explicit, gate-able treatment.** Every report /
  campaign / approval can now state `modeled` / `estimated` /
  `unmodeled`. The default is the conservative `estimated` overlay.
- **The research archive is auditable.**
  `scripts/validate_research_archive.py` checks the registry, manifest,
  reports, links, and credentials in one command.
- **Strategy approval is now a validated, documented schema.** A
  malformed registry fails closed; entries carry evidence, expiry,
  mode, and a risk ceiling.
- **An independent-engine parity path is designed** (Lean), ready for a
  future human to execute.

## What did NOT change

- **No strategy campaign was run**; no new strategy result was produced.
- **No strategy is approved.** `configs/approved_strategies.yaml` is
  still `approved: []`.
- **No paper / demo / live trading**, no orders, no live credentials.
- **Prior campaign evidence is immutable.** CAMPAIGN_001–009 reports and
  artifacts were not modified — only linked to from new docs.
- **The backtest engine's PnL is unchanged.** Financing is still not in
  engine PnL; `D1AGG` is an opt-in granularity; existing campaigns
  remain bit-for-bit reproducible.
- The repo remains **research-only**.

## Safety state (every Phase 0 invariant still holds)

- `configs/approved_strategies.yaml` is empty.
- `paper-loop`, `demo-loop`, and the live path refuse every strategy
  (verified: CLI exit 2; 31 guard/approval tests).
- Backtesting and research tooling remain fully available — only the
  order-capable loops are gated.
- No credentials are staged or committed; `.env*` stay gitignored;
  the archive validator scans 1856 committed artifact files clean.
- Prior campaign reports / artifacts untouched.

## Validation results (Phase 6, final)

```
pytest                              224 passed
ruff check src tests scripts        All checks passed
validate_research_archive.py        ALL CHECKS PASSED (10/10)
bot paper-loop  --config paper      refused, exit 2
bot demo-loop   --config practice   refused, exit 2
approved_strategies.yaml            approved: []  (empty)
```

## Remaining blockers

1. **Financing is not modeled in-engine** — only a conservative
   `estimated` stress overlay. A hard, unconditional blocker for any
   live promotion. See `FINANCING_MODEL_DESIGN.md`.
2. **D1 backtesting is only partial.** `D1AGG` aggregation removes the
   rollover contamination, but the engine still fills at the signal
   bar's close — proper daily research wants next-bar-open fills.
3. **No live dry-run** of any candidate has ever been done.
4. **No demonstrated edge.** Five strategy families, nine campaigns, no
   approved strategy — the deeper "blocker" is the absence of a result
   worth promoting.

## Recommended next human decision points

None is authorized by this sprint. In rough priority:

1. **Decide whether to continue strategy research at all.** The honest
   base rate (nine campaigns, no edge) is reasonable grounds to stop —
   see `FINAL_RESEARCH_DECISION_MEMO.md`.
2. **If continuing: invest in infrastructure before strategies.**
   Model financing properly (capture `DAILY_FINANCING` forward, then
   build `FutureOandaObservedFinancingModel`); add next-bar-open fills
   so D1 research is fully sound. Zero overfitting risk, highest value.
3. **Execute the Lean parity check** on CAMPAIGN_002 to independently
   validate the bespoke engine — see `LEAN_PARITY_DESIGN.md`.
4. **Only with a genuinely new, human-approved thesis**, authorize a
   fresh campaign under a new pre-commit. Not a tweak of a rejected one.

Any future strategy reaches a loop only via a deliberate human approval
entry in `configs/approved_strategies.yaml`, following
`STRATEGY_APPROVAL_PROCESS.md`. Until then, the repo stays frozen.
