# CAMPAIGN_011 — Independent Verifier Status

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-walk-forward-001`
`strategy_evidence: false`

Phase 8 capability assessment of the free / local parity
verifier (`research/parity_verifier/`) against CAMPAIGN_011 /
`random_entry_anchor 0.1.0-c011`. **This document does not
claim independent corroboration unless the verifier actually
runs.** Capability assessment is honest about what the verifier
*can* run today and what it *cannot* without a separately
authorized extension.

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. **CAMPAIGN_011 verdict = REJECT (null-model
> anchor).** `configs/approved_strategies.yaml` remains
> `approved: []`. A verifier that has not run is not
> corroboration; it is a known gap. **For a null model, item 5
> of the six-evidence ladder is structurally not binding.**

## 1. Headline status — **VERIFIER DID NOT RUN; NOT REQUIRED FOR THE REJECT VERDICT**

| dimension | value |
|---|---|
| verifier package | [`research/parity_verifier/`](../../research/parity_verifier) |
| verifier scope today | **CAMPAIGN_002 `trend_following 0.1.0` only** (EMA + Donchian + ATR-trailing rule set, hard-coded) |
| can verifier run `random_entry_anchor` today? | **no** — the entry / exit rules in `research/parity_verifier/rules.py` implement only the CAMPAIGN_002 logic; there is no `random_entry_anchor` rule path |
| was the verifier run for CAMPAIGN_011? | **no** |
| was independent corroboration achieved? | **no** |
| does CAMPAIGN_011 pass item 5 of the six-evidence ladder? | **no — and it does not need to** (item 5 is a paper-promotion gate; null model cannot be paper-promoted) |
| does this change the verdict? | **no** — CAMPAIGN_011 is REJECT (expected); item 5 is structurally not binding |
| is verifier extension recommended now? | **conditional** — uniquely valuable as a follow-up because random's deterministic-seed property allows **exact-equivalence** corroboration (not WARN-band), but not blocking for any current work |

## 2. Why item 5 is not binding for CAMPAIGN_011

Per
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8 + the protocol's null-model classification:

| item | description | required for | this candidate |
|---|---|---|---|
| 1. Pre-commit doc | declaring frozen rules + gates | any verdict | ✓ ([`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)) |
| 2. Backtest report | per-fold metrics | REJECT or PASS | ✓ ([`CAMPAIGN_011_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_011_WALK_FORWARD_EXECUTION.md)) |
| 3. Walk-forward result | `overall_verdict ∈ {PASS, REJECT}` | REJECT or PASS | ✓ ([`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)) — REJECT |
| 4. Financing reconciliation | ESTIMATED + conservative stress | PASS-promotion | ✓ ([`CAMPAIGN_011_FINANCING_OVERLAY.md`](CAMPAIGN_011_FINANCING_OVERLAY.md)) |
| 5. Independent corroboration | free / local verifier WARN-band agreement OR custom-engine reproduction | **PASS-promotion** | **✗ — not satisfied; not required (null model cannot be paper-promoted)** |
| 6. Human approval record | reviewed `ApprovalEntry` | **PASS-promotion** | **✗ — structurally impossible (null model by design)** |

For a **REJECT**, items 1, 2, and 3 are sufficient. Items 4, 5,
6 are pre-requisites for *approval*, not for *rejection*. Since
CAMPAIGN_011 cannot be promoted (null model by design), the
missing items 5 and 6 do not change the verdict.

**Explicit statement: the verifier is not needed to reject the
null model.** The REJECT verdict stands on items 1-3 alone (and
is reinforced by item 4's financing overlay, which strictly
worsens the result).

## 3. Why verifier extension is uniquely valuable for CAMPAIGN_011 (as a follow-up)

Unlike all prior candidates, the random-entry anchor has **zero
parameter-driven behavior** outside the fixed master seed:

- `master_seed = 20260523` is fixed in the pre-commit before
  any code; it must not change.
- `entry_probability_per_bar = 0.05` is fixed before any code;
  changing it would constitute a new candidate.
- Every other parameter is fixed identically.

Therefore, for any `(master_seed, instrument, bar_timestamp_iso)`
triple, the strategy's decision is **exactly determined** by
the SHA-256 of the seed input. An independent re-implementation
of `_derive_random_pair(master_seed, instrument, ts)` in the
verifier — using only `hashlib.sha256` (standard library, same
across processes / platforms / language runtimes) — will
produce **bit-identical** `bar_random` and `gate_random` values.

This means a future verifier corroboration for CAMPAIGN_011
could be:

- **Exact**, not WARN-band.
- **Reproducible** across machines, processes, and any future
  Python / numpy / pandas version.
- **A clean template** for adding any future family — random's
  deterministic nature surfaces verifier-integration bugs
  (data alignment, fill-timing precision, sizing arithmetic)
  more clearly than a strategy whose own behavior has
  rule-induced variance.

This is in contrast to CAMPAIGN_002's verifier coverage, which
ended at WARN-band (3 OK / 4 WARN / 0 FAIL pairs; fractional-pip
drift on USD_CAD / USD_CHF expectancy R; see
[`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)).

## 4. What a verifier extension for CAMPAIGN_011 would require

The recommended `infra-free-local-parity-verifier-random-entry-001`
follow-up sprint would need to:

1. **Rule re-implementation.** Add
   `evaluate_entry_random_entry_anchor()` in
   `research/parity_verifier/rules.py` mirroring R1–R8 from
   [`RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md`](RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md),
   re-derived from the spec — never copied from
   `src/forex_bot/strategies/random_entry_anchor.py`. The
   `_derive_random_pair` equivalent must use only
   `hashlib.sha256` over the same UTF-8 string form
   `f"{master_seed}|{instrument}|{bar_timestamp_iso}"`.
2. **Event-loop adapter.** Add a `run_pair_random_entry_anchor()`
   to `event_loop.py` driving the bar-by-bar loop through the
   new `evaluate_entry` + the inherited exit precedence
   (ATR-stop + time-stop at 6 bars; no trailing).
3. **Bespoke reference loader.** Add a CAMPAIGN_011 reference
   loader (`data_loader.load_bespoke_reference_campaign_011(...)`)
   reading the committed
   `backtests/CAMPAIGN_011_random_entry_anchor/folds/...`
   summaries.
4. **Exact-equivalence comparison rules.** Set the verifier's
   tolerance ladder to **exact-equivalence** for this
   candidate (not WARN-band) — the trade count, entry
   timestamps, entry directions, and signal IDs must match
   bit-for-bit; fractional-pip drift on stop prices / fill
   prices remains acceptable per the existing infrastructure.
5. **Tests.** Mirror the existing
   `tests/research/test_parity_verifier_*.py` cases for the
   new path; preserve the grep-enforced
   no-`forex_bot`-import rail.
6. **Run, then write a `CAMPAIGN_011_INDEPENDENT_VERIFIER_RESULT.md`.**

That sprint is **optional and not required** for CAMPAIGN_011's
evidence-sprint REJECT verdict.

## 5. Why it is acceptable that the verifier did not run now

- **CAMPAIGN_011 is REJECTED.** The verdict does not depend on
  item 5.
- **CAMPAIGN_011 cannot be paper-promoted (null model).** Item
  5 is a paper-promotion gate.
- **Even an unexpected PASS would not promote the candidate.**
  Per
  [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
  §12, an unexpected PASS would trigger the investigation
  playbook (treat as pipeline bug; never promote). In that
  scenario, the verifier extension *would* be triggered as
  part of the investigation, but **as a debugging tool, not
  as a corroboration gate**.

## 6. What if the verdict had been an unexpected PASS?

If `WalkForwardResults.overall_verdict == "PASS"` had been
recorded (it was not), the documented response per
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§12 would have been:

1. **DO NOT** add `random_entry_anchor` to
   `configs/approved_strategies.yaml`.
2. **DO NOT** treat the result as evidence of an edge.
3. **DO** trigger the investigation playbook:
   - Confirm `seed_input` does not include any bar-`t` data
     (re-grep `_derive_random_pair`'s signature + source).
   - Confirm fold-boundary leakage rules pass.
   - Confirm structural audits pass.
   - Confirm the entry-probability rate matches expected
     ~5 % per bar.
   - Confirm the long-short distribution matches 50 / 50.
4. **DO** escalate to a separate investigation sprint:
   `infra-pipeline-validation-investigation-001`.
5. **DO** commit the verdict as `INVESTIGATE_PIPELINE` pending
   investigation.

**None of those steps were triggered.** The verdict was REJECT,
which is the expected and desired null-model outcome.

## 7. Comparison to CAMPAIGN_010's verifier status

| dimension | CAMPAIGN_010 | CAMPAIGN_011 |
|---|---|---|
| candidate type | research candidate (could become paper if it had passed) | **null model (cannot become paper ever)** |
| verifier extension needed for verdict? | no (REJECT is sufficient with items 1–3) | no (REJECT is sufficient and approval is structurally impossible) |
| verifier extension recommended as follow-up? | no — candidate is rejected; work in a dead path is wasted | **yes — uniquely useful as a reusable exact-equivalence template + as a future-debugging tool** |
| if extension is done, expected tolerance | WARN-band (rule-induced variance) | **exact** (deterministic seed) |
| sprint name for the extension | n/a | `infra-free-local-parity-verifier-random-entry-001` |

## 8. Recommendation

- **Do not extend the verifier inside this evidence sprint.**
  Out of scope; the sprint's charter is to produce the
  walk-forward + financing + risk artifacts (all committed).
- **Do not block downstream work** on the verifier extension.
  CAMPAIGN_011 REJECTED cleanly; future C3 / C2 / C4 discovery
  + scaffold + evidence sprints can proceed independently.
- **Do consider extending the verifier in a follow-up sprint
  named `infra-free-local-parity-verifier-random-entry-001`**
  if and only if:
  - the project's bandwidth allows
    diagnostic-infrastructure investment, OR
  - a future strategy unexpectedly passes its gates and the
    investigation playbook fires (the verifier extension
    becomes a debugging asset), OR
  - the verifier needs to be extended for a future *real*
    candidate (CAMPAIGN_011's deterministic-seed pattern
    provides the cleanest template for adding any new
    family).
- **Keep the verifier package's scope clearly documented.**
  The CAMPAIGN_002-only scope is honest; future candidates
  should each get their own verifier-extension sprint when
  (and only when) they survive walk-forward + financing under
  the evidence pipeline.

## 9. Safety state

- `configs/approved_strategies.yaml`: **`approved: []`** (untouched).
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **CAMPAIGN_011** verdict = REJECT (null model anchor).
- **No verifier code change** in this sprint. The verifier
  package is read in the docs only; not modified.
- **No new external dependency.**
- **No broker call, no `.env` read, no credential printed.**
- **No QuantConnect / LEAN.**

## 10. Cross-links

- [`research/parity_verifier/README.md`](../../research/parity_verifier/README.md)
- [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
  (the original CAMPAIGN_002 verifier design)
- [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
  (the CAMPAIGN_002 corroboration result)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_READINESS.md)
  (the prior scaffold sprint's same-posture readiness doc;
  this Phase 8 status doc upgrades "scaffold readiness" to
  "evidence-sprint completion: did not run; not required")
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md)
  (CAMPAIGN_010's verifier capability gap analysis)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 (six-evidence ladder)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
