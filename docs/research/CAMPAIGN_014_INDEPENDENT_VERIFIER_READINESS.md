# CAMPAIGN_014 Independent-Verifier Readiness

**Date:** 2026-05-24 · **Branch:** `research-calendar-event-window-anomaly-001`
`strategy_evidence: false`

Phase 7 independent-verifier readiness summary for **CAMPAIGN_014 /
`calendar_event_window_anomaly 0.1.0-c014`**. **Scaffold sprint
only — no verifier evidence run.**

> No strategy approved. **A passing readiness doc is NOT approval
> and is NOT evidence.** Verifier extension is item 5 of the six-
> evidence ladder; it is NOT required for a REJECT verdict.

## 1. Current verifier capability lock

| dimension | value |
|---|---|
| verifier | `research/parity_verifier/` (free / local; no broker) |
| capability lock | **CAMPAIGN_002 / `trend_following`** only |
| binding lock doc | [`INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_004_SUMMARY.md) (or latest infra-free-local-parity-verifier-NNN summary) |
| verifier extension history | CAMPAIGN_010 / 011 / 012 / 013 evidence sprints all deferred verifier extension because each candidate REJECTED; extending an indefinitely-deferred verifier for a REJECT candidate produces zero research value |

## 2. Verifier extension status for CAMPAIGN_014

**NOT REQUIRED for REJECT verdict** (matches CAMPAIGN_010 / 011 /
012 / 013 precedent).

**Required ONLY if CAMPAIGN_014 reaches `RESEARCH_PASS_UNAPPROVED`**
(item 5 of the six-evidence ladder).

## 3. Suggested future verifier-extension branch

### **`infra-free-local-parity-verifier-calendar-event-window-anomaly-001`**

| field | value |
|---|---|
| trigger condition | CAMPAIGN_014 reaches `RESEARCH_PASS_UNAPPROVED` in the evidence sprint |
| scope | per-family verifier extension — re-implement event-fixture loader + R3 event-window proximity + R5 counter-direction signal + R6 ATR fail-closed + R7 ATR stop in the independent verifier; verify per-fold trade-by-trade parity with the bespoke engine within a documented tolerance |
| safety | LOW risk — verifier is isolated from broker / execution / loops paths; it reads candle data + event fixture and computes signals independently; no order-emitting code |
| effort | medium (~5–7 days; smaller than CAMPAIGN_013's would have been because there's no cross-pair runner contract to re-implement) |
| binding requirement | the verifier must re-implement the event-fixture loader's binding deny-list (no actual/forecast/surprise/revision/commentary) so any future fixture revision is caught at both the engine-side and verifier-side loader |

## 4. Why verifier is NOT required for a REJECT verdict

A REJECT verdict means the strategy did not produce a positive
edge under pre-committed gates. Independent corroboration of a
REJECT is unnecessary because:

1. The bespoke engine + verifier would BOTH reject the strategy.
2. The verifier extension's research value is to **corroborate a
   PASS** — confirming an independent implementation produces the
   same edge — not to corroborate a REJECT.
3. Spending verifier-extension effort on a REJECT candidate burns
   sprint capacity that could be used for the next discovery sprint
   or for the next real candidate.

## 5. Six-evidence ladder status for CAMPAIGN_014

| item | name | status (after this scaffold sprint) | status (expected after future evidence sprint) |
|---|---|---|---|
| 1 | data provenance | **NOT STARTED** (evidence-sprint Phase 1) | **COMPLETE** (matches CAMPAIGN_010 / 011 / 012 / 013 provenance verbatim) |
| 2 | walk-forward verdict | **NOT STARTED** (evidence-sprint Phase 5) | **COMPLETE** (REJECT or RESEARCH_PASS_UNAPPROVED or BLOCKED) |
| 3 | financing overlay | **NOT STARTED** (evidence-sprint Phase 6) | **COMPLETE** (ESTIMATED + conservative stress; MODELED refused) |
| 4 | risk diagnostics | **NOT STARTED** (evidence-sprint Phase 7) | **COMPLETE** (standard + CAMPAIGN_014-specific event-class diagnostics) |
| 5 | independent verifier | **NOT REQUIRED for REJECT** | **DEFERRED** if REJECT; **REQUIRED via `infra-free-local-parity-verifier-calendar-event-window-anomaly-001`** if RESEARCH_PASS_UNAPPROVED |
| 6 | deliberate human approval | **MOOT** for scaffold; **MOOT** for REJECT; **REQUIRED but never automatic** for RESEARCH_PASS_UNAPPROVED |

## 6. No verifier evidence run

| dimension | value |
|---|---|
| verifier extension implemented for CAMPAIGN_014 | **NO** |
| verifier evidence run for CAMPAIGN_014 | **NOT RUN** |
| verifier scaffolding for CAMPAIGN_014 | **NOT STARTED** |

## 7. Explicit no-approval statement

**Even after a hypothetical verifier-extension corroboration of a
`RESEARCH_PASS_UNAPPROVED` verdict, the strategy STILL cannot be
approved automatically.** Item 6 of the six-evidence ladder
(deliberate human approval) is permanent — only a human edit to
`configs/approved_strategies.yaml` per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) can
promote the strategy.

## 8. Safety state (unchanged)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| CAMPAIGN_002 / 010 / 011 / 012 / 013 | all REJECT (untouched) |
| CAMPAIGN_014 | scaffold-only |
| approved strategies | **none** |
| paper-loop / demo-loop | refuse |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |

## 9. Cross-links

- [`CAMPAIGN_014_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_014_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CAMPAIGN_014_WALK_FORWARD_READINESS.md`](CAMPAIGN_014_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_014_FINANCING_RISK_READINESS.md`](CAMPAIGN_014_FINANCING_RISK_READINESS.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md) (sibling — deferred-indefinitely precedent)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_005.md) (future evidence sprint prompt)
