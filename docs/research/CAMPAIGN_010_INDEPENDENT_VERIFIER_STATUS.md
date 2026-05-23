# CAMPAIGN_010 — Independent Verifier Status

**Date:** 2026-05-23 · **Branch:** `research-asian-london-session-breakout-walk-forward-001`
`strategy_evidence: false`

Phase 7 capability assessment of the free / local parity verifier
(`research/parity_verifier/`) against the CAMPAIGN_010 research
candidate (`session_breakout 0.1.0-c010`). **This document does
not claim independent corroboration unless the verifier actually
runs.** Capability assessment is honest about what the verifier
*can* run today and what it *cannot* without a separately
authorized extension.

> No strategy approved. CAMPAIGN_002 remains REJECT.
> `configs/approved_strategies.yaml` remains `approved: []`.
> A verifier that has not run is not corroboration; it is a known
> gap.

## 1. Headline status — **VERIFIER DID NOT RUN; CAMPAIGN_010 NOT INDEPENDENTLY CORROBORATED**

| dimension | value |
|---|---|
| verifier package | [`research/parity_verifier/`](../../research/parity_verifier) |
| verifier scope today | **CAMPAIGN_002 `trend_following 0.1.0` only** (EMA + Donchian + ATR-trailing rule set, hard-coded) |
| can verifier run `session_breakout` today? | **no** — the entry / exit rules in `research/parity_verifier/rules.py` implement only the CAMPAIGN_002 logic; there is no `session_breakout` rule path |
| was the verifier run for CAMPAIGN_010? | **no** |
| was independent corroboration achieved? | **no** |
| does CAMPAIGN_010 pass item 5 of the six-evidence ladder? | **no** |
| does this change the verdict? | **no** — the Phase 4 verdict is REJECT; corroborating a REJECT does not lift it. The missing corroboration only matters for a hypothetical PASS, which this candidate does not earn. |
| is verifier extension recommended now? | **no** — the candidate has been REJECTED; extending the verifier for it would be work invested in a dead path. |

## 2. What the verifier package contains today

Inspected at this sprint's tip commit:

| file | role | session_breakout support |
|---|---|:---:|
| `models.py` | Pydantic models (Bar, CandleSeries, VerifierConfig, Signal, Trade, …) | generic; usable |
| `instruments.py` | static instrument metadata for the 7-pair universe | usable as-is |
| `data_loader.py` | read-only loaders (parameter JSON, candle CSVs) | usable for the loader side |
| `indicators.py` | independent EMA, ATR, Donchian | ATR is reusable; the Asian-range computation has no helper here |
| `rules.py` | independent rule evaluation: `evaluate_entry` (EMA + Donchian + ADX-free trend), initial stop, trailing-stop ratchet, bid/ask-aware fill, 0.25 %-risk sizing, PnL | **CAMPAIGN_002 rules only** — no Asian-range gate, no session-window gate, no London-breakout direction logic |
| `event_loop.py` | bar-by-bar deterministic loop for one pair, hard-wired to the `evaluate_entry` shape from CAMPAIGN_002 | requires a parallel path for `session_breakout` |
| `compare.py` | tolerance-ladder comparison against a bespoke reference | reusable structurally; needs a `session_breakout` bespoke reference |
| `reporting.py` | markdown rendering for verifier / comparison output | reusable |

The package's README is explicit on scope:

> A minimal independent re-implementation of the CAMPAIGN_002 H4
> `trend_following 0.1.0` strategy + engine mechanics.

The verifier was deliberately built for CAMPAIGN_002 only; extending
it to a new candidate is a new sprint, never a "let me just hack
it in" move.

## 3. What an independent corroboration of CAMPAIGN_010 would require

A separately-authorized sprint (recommended name:
`infra-free-local-parity-verifier-session-breakout-005`) would need to:

1. **Rule re-implementation.** Add `evaluate_entry_session_breakout()`
   in `research/parity_verifier/rules.py` mirroring the candidate's
   R1–R11 from
   [`ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md`](ASIAN_LONDON_SESSION_BREAKOUT_IMPLEMENTATION_SPEC.md),
   re-derived from the spec — never copied from
   `src/forex_bot/strategies/session_breakout.py`.
2. **Event-loop adapter.** Add a `run_pair_session_breakout()` to
   `event_loop.py` so the bar-by-bar loop drives the new
   `evaluate_entry` and the exit precedence (no trailing stop in v1
   for this candidate; time-stop at 6 bars; ATR hard stop only).
3. **Bespoke reference export.** Add a CAMPAIGN_010 reference loader
   (`data_loader.load_bespoke_reference_campaign_010(...)`) reading
   the committed `backtests/CAMPAIGN_010_session_breakout/folds/...`
   summaries.
4. **Comparison rules.** Decide the trade-count / metric / per-pair
   tolerance ladder for CAMPAIGN_010 in
   `compare.py` (CAMPAIGN_002's tolerances were tuned to its
   trailing-stop ratchet behavior; CAMPAIGN_010 has no trailing
   stop, so the tolerances would be different).
5. **Tests.** Mirror the existing
   `tests/research/test_parity_verifier_*.py` cases for the new
   path; preserve the grep-enforced no-`forex_bot`-import rail.
6. **Run, then write `CAMPAIGN_010_INDEPENDENT_VERIFIER_RESULT.md`.**
   The verifier's output, not this status doc, is what would
   constitute independent corroboration.

That sprint is **out of scope for the current REJECT verdict**.
The candidate is being retired; investing further verifier code
in a dead path violates the freeze's "no scope creep" rule.

## 4. Why this is acceptable for a REJECT (and not for a PASS)

Per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 the six-evidence ladder:

| item | description | required for | this sprint |
|---|---|---|---|
| 1. Pre-commit doc | declaring frozen rules + gates | any verdict | ✓ ([`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)) |
| 2. Backtest report | single-window or per-fold metrics | REJECT or PASS | ✓ ([`CAMPAIGN_010_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_010_WALK_FORWARD_EXECUTION.md)) |
| 3. Walk-forward result | `overall_verdict ∈ {PASS, REJECT}` | REJECT or PASS | ✓ ([`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)) |
| 4. Financing reconciliation | ESTIMATED + conservative stress | PASS-promotion | ✓ ([`CAMPAIGN_010_FINANCING_OVERLAY.md`](CAMPAIGN_010_FINANCING_OVERLAY.md)) |
| 5. **Independent corroboration** | **free / local verifier WARN-band agreement OR custom-engine reproduction** | **PASS-promotion** | **✗ — not satisfied here** |
| 6. Human approval record | reviewed `ApprovalEntry` | PASS-promotion | ✗ (would only be applicable for PASS) |

For a **REJECT**, items 1, 2, and 3 are sufficient. Items 4, 5, 6
are pre-requisites for *approval*, not for *rejection*. Since
CAMPAIGN_010 is REJECTED, the missing items 5 and (vacuous) 6 do
not change the verdict.

For a hypothetical PASS, the missing item 5 would be a blocking
gap — and a future PASS candidate from any family would need an
extended verifier before its approval review.

## 5. Recommendation

- **Do not extend the verifier for CAMPAIGN_010.** The candidate
  is being retired (Phase 8 will update STRATEGY_STATUS to
  `rejected`).
- **Keep the verifier package's scope clearly documented.** The
  CAMPAIGN_002-only scope is honest; future candidates should
  reuse the same pattern (separate verifier sprint per family).
- **Treat verifier extension as a precondition** for *any* future
  candidate that survives walk-forward + financing. The
  next-branch recommendation (Phase 8) will reflect this.

## 6. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **No verifier code change.** The verifier package is read but not
  modified.
- **No new external dependency.**
- **No broker call, no `.env` read, no credential printed.**
- **No QuantConnect / LEAN.**

## 7. Cross-links

- [`research/parity_verifier/README.md`](../../research/parity_verifier/README.md)
- [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
  (the original CAMPAIGN_002 verifier design)
- [`INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md`](INFRA_FREE_LOCAL_PARITY_VERIFIER_001_PLAN.md)
- [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_010_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_010_PRECOMMIT_CHECKLIST.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
