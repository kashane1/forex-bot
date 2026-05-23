# CAMPAIGN_011 — Status

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Status of the **CAMPAIGN_011 research candidate**
(`random_entry_anchor 0.1.0-c011`) at the close of the
scaffold sprint.

> ## Candidate scaffold only. Null model / diagnostic anchor. NO APPROVAL POSSIBLE.
>
> - **CAMPAIGN_011 is a null model by design.** It cannot be
>   added to
>   [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
>   under any circumstance. The protocol's §4 whitelist
>   explicitly lists "Baseline / null model" as "Allowed only
>   as a diagnostic comparison anchor for the preferred
>   candidate; cannot itself be the 'preferred candidate' for
>   paper promotion."
> - **No backtest verdict yet** (only a config-load smoke + the
>   unit test suite have run in this scaffold sprint; neither
>   is evidence).
> - **No evidence campaign run.** The walk-forward + financing
>   + risk pipeline is the future evidence sprint's task.
> - **Paper / demo / live blocked.** Even an unexpected PASS in
>   the future evidence sprint **does not promote** — it
>   triggers the investigation playbook, never paper.
> - **CAMPAIGN_002 remains REJECT and is unrelated** to this
>   candidate; only the candle store is reused as data input.
> - **CAMPAIGN_010 remains REJECT and is unrelated.** The
>   exit logic + walk-forward fold structure + gate vector are
>   deliberately inherited so the comparison isolates the entry
>   signal; no CAMPAIGN_010 frozen parameter is "tuned" or
>   tweaked.

## 1. What this sprint produced

| component | status |
|---|---|
| Sprint plan | committed: [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md) |
| Implementation spec | committed: [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md) |
| Strategy module | committed: [`src/forex_bot/strategies/random_entry_anchor.py`](../../src/forex_bot/strategies/random_entry_anchor.py) (~190 LOC) |
| StrategyConfig sub-model | committed: [`src/forex_bot/config.py`](../../src/forex_bot/config.py) (`RandomEntryAnchorStrategyConfig`, `StrategyConfig.random_entry_anchor`) |
| Strategy re-export | committed: [`src/forex_bot/strategies/__init__.py`](../../src/forex_bot/strategies/__init__.py) |
| Unit tests | committed: [`tests/unit/test_random_entry_anchor.py`](../../tests/unit/test_random_entry_anchor.py) — **36 cases pass** |
| Research config | committed: [`configs/campaign_011_random_entry_anchor.yaml`](../../configs/campaign_011_random_entry_anchor.yaml) |
| Pre-commit checklist | committed: [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md) |
| Scaffold readiness | committed (this phase): [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md) |
| Smoke result | pending (Phase 5) |
| Walk-forward readiness | pending (Phase 6) |
| Financing + risk readiness | pending (Phase 6) |
| Independent verifier readiness | pending (Phase 6) |
| Sprint summary | pending (Phase 7) |

## 2. What is **not** produced (by design, out of scope for this sprint)

| artifact | why deferred |
|---|---|
| Walk-forward `plan.json` / `plan.md` (committed evidence) | future evidence sprint; this sprint only proves *readiness* and runs a `/tmp` dry-run smoke. |
| Per-fold backtest results | future evidence sprint. |
| Financing overlay `financing_run.json` / `.md` | future evidence sprint. |
| Risk diagnostics `diagnostics.json` / `.md` | future evidence sprint. |
| Campaign report | future evidence sprint. |
| `scripts/run_campaign_011.py` | future evidence sprint's runner (clones `scripts/run_campaign_010.py`). |
| Independent verifier extension | optional follow-up (`infra-free-local-parity-verifier-random-entry-001`); not blocking. |
| Approval record in `configs/approved_strategies.yaml` | **structurally impossible** — null model by design. |

## 3. Headline result

**Candidate scaffold complete. No backtest evidence produced.
No verdict possible from this sprint. CAMPAIGN_011 cannot ever
be approved (null model).**

The candidate:

- has a `Strategy`-protocol-conforming implementation;
- has a `StrategyConfig` sub-model with strict validation;
- has 36 unit + structural-audit tests pinning rules R1–R8,
  determinism, distribution, no-lookahead (seed input contains
  no bar-`t` data), no `random` / `numpy.random` / built-in
  `hash()`, no broker imports, no CAMPAIGN_002 / CAMPAIGN_010
  parameter contamination, no approval-shaped fields, and the
  approved registry stays empty;
- has a research-only candidate YAML config that loads via
  `forex_bot.config.load_settings(...)` and would drive the
  bespoke `BacktestEngine` *if and when* a future evidence
  sprint authorises a backtest run;
- has explicit documentation of the null-model invariant — the
  strategy is structurally ineligible for paper / demo / live
  promotion.

## 4. Headline non-result

- **No expectancy claim.** None has been produced.
- **No pair-level result.** No pair has been backtested.
- **No walk-forward result.** No fold has been run.
- **No financing overlay number.** None has been computed.
- **No verdict.** CAMPAIGN_011 has *neither* PASS *nor* REJECT
  status — it is **scaffold only**.

## 5. Safety state (unchanged from Phase 0)

| dimension | status |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 verdict | **REJECT** (untouched) |
| CAMPAIGN_010 verdict | **REJECT** (untouched) |
| `random_entry_anchor` in approved registry | **no, and structurally cannot be (null model)** |
| `random_entry_anchor` in any active loop | **no** |
| `random_entry_anchor` in `configs/paper.yaml` | **no** (verified by Phase 3 unit test) |
| `random_entry_anchor` in `configs/practice.yaml` | **no** (verified by Phase 3 unit test) |
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
| pytest baseline | **771 passes** (735 prior + 36 new) |

## 6. Recommended next sprints

- **`research-random-entry-diagnostic-anchor-walk-forward-001`** —
  the future evidence sprint per
  [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md);
  full walk-forward + financing overlay + risk diagnostics +
  verifier-status; expected verdict REJECT; UNEXPECTED-PASS
  playbook documented and binding.
- (Optional) **`infra-free-local-parity-verifier-random-entry-001`** —
  extend the free / local verifier with a `random_entry_anchor`
  rule path; produces deterministic exact-equivalence
  corroboration; useful follow-up but not blocking for the
  evidence sprint.
- (Eventual) **`research-new-candidate-strategy-discovery-003`** —
  after CAMPAIGN_011 evidence completes, the next *real*
  candidate selection sprint (recommended ordering: C3 →
  C2 → C4 per
  [`CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md`](CANDIDATE_STRATEGY_FAMILY_REASSESSMENT_002.md)).
- (Eventual) **`infra-ruff-up042-stress-enum-001`** —
  small cleanup sprint for the 11 pre-existing UP042 findings
  in untouched files (carried forward; documented in Phase 0).

## 7. Cross-links

- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_001_PLAN.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md)
- [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_READINESS.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`NEXT_PREFERRED_CANDIDATE_002.md`](NEXT_PREFERRED_CANDIDATE_002.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`CAMPAIGN_010_REJECTION_CLOSEOUT.md`](CAMPAIGN_010_REJECTION_CLOSEOUT.md)
- [`REJECTED_FAMILY_OVERFIT_GUARDRAILS.md`](REJECTED_FAMILY_OVERFIT_GUARDRAILS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
