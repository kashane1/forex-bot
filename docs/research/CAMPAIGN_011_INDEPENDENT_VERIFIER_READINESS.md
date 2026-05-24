# CAMPAIGN_011 — Independent Verifier Readiness

**Date:** 2026-05-23 · **Branch:** `research-random-entry-diagnostic-anchor-001`
`strategy_evidence: false`

Phase 6 independent-verifier integration-readiness assessment
for **CAMPAIGN_011** / `random_entry_anchor 0.1.0-c011`.
**Reading this document does not approve the strategy and does
not claim independent corroboration.**

> No strategy approved. CAMPAIGN_002 remains REJECT. CAMPAIGN_010
> remains REJECT. `configs/approved_strategies.yaml` remains
> `approved: []`. **CAMPAIGN_011 is a null model — cannot be
> approved by design. Item 5 (independent corroboration) and item
> 6 (human approval) of the six-evidence ladder are structurally
> not binding for this candidate.**

## 1. Headline status — **VERIFIER EXTENSION OPTIONAL, NOT BLOCKING**

| dimension | value |
|---|---|
| verifier package | [`research/parity_verifier/`](../../research/parity_verifier) |
| verifier scope today | **CAMPAIGN_002 `trend_following 0.1.0` only** (EMA + Donchian + ATR-trailing rule set, hard-coded) |
| can verifier run `random_entry_anchor` today? | **no** — the entry / exit rules in `research/parity_verifier/rules.py` implement only the CAMPAIGN_002 logic; there is no `random_entry_anchor` rule path |
| verifier extension required for CAMPAIGN_011 evidence sprint? | **no** — item 5 of the six-evidence ladder is a *paper-promotion* gate; CAMPAIGN_011 cannot be paper-promoted |
| verifier extension recommended as follow-up? | **yes** — uniquely valuable for a null model because random has zero tunable parameters; same `(seed, pair, timestamp)` → same trades → **deterministic exact-equivalence** corroboration is possible |
| recommended follow-up branch | `infra-free-local-parity-verifier-random-entry-001` |
| blocking the scaffold sprint? | **no** |
| blocking the future evidence sprint? | **no** |

## 2. Why verifier extension is uniquely valuable for C5 (random)

Unlike all prior candidates (CAMPAIGN_002, CAMPAIGN_010), the
random-entry anchor has **zero parameter-driven behavior**:

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
across processes / platforms / language runtimes) — will produce
**bit-identical** `bar_random` and `gate_random` values.

This means the verifier's CAMPAIGN_011 corroboration could be:

- **Exact**, not WARN-band.
- **Reproducible** across machines, processes, and any future
  Python / numpy / pandas version.
- **A clean template** for adding any future family — random's
  deterministic nature surfaces verifier-integration bugs
  (data alignment, fill-timing precision, sizing arithmetic)
  more clearly than a strategy whose own behavior has
  rule-induced variance.

This is in contrast to CAMPAIGN_002's verifier coverage, which
ended at WARN-band (3 OK / 4 WARN / 0 FAIL pairs;
fractional-pip drift on USD_CAD / USD_CHF expectancy R; see
[`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)).

## 3. What an independent corroboration of CAMPAIGN_011 would require

The recommended `infra-free-local-parity-verifier-random-entry-001`
sprint would need to:

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
   tolerance ladder to **exact-equivalence** for this candidate
   (not WARN-band) — the trade count, entry timestamps, entry
   directions, and signal IDs must match bit-for-bit;
   fractional-pip drift on stop prices / fill prices remains
   acceptable per the existing infrastructure.
5. **Tests.** Mirror the existing
   `tests/research/test_parity_verifier_*.py` cases for the
   new path; preserve the grep-enforced
   no-`forex_bot`-import rail.
6. **Run, then write `CAMPAIGN_011_INDEPENDENT_VERIFIER_RESULT.md`.**

That sprint is **optional and not required** for CAMPAIGN_011's
evidence-sprint REJECT verdict.

## 4. Why it is acceptable that the verifier is not extended now

Per
[`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
§13 + the six-evidence ladder in
[`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
§8:

| item | description | required for | this candidate |
|---|---|---|---|
| 1. Pre-commit doc | declaring frozen rules + gates | any verdict | ✓ ([`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)) |
| 2. Backtest report | per-fold metrics | REJECT or PASS | will be ✓ after evidence sprint |
| 3. Walk-forward result | `overall_verdict ∈ {PASS, REJECT}` | REJECT or PASS | will be ✓ after evidence sprint |
| 4. Financing reconciliation | ESTIMATED + conservative stress | PASS-promotion | will be ✓ after evidence sprint |
| 5. **Independent corroboration** | **free / local verifier WARN-band agreement OR custom-engine reproduction** | **PASS-promotion** | **✗ — not satisfied; not required (null model)** |
| 6. Human approval record | reviewed `ApprovalEntry` | PASS-promotion | **✗ — structurally impossible (null model)** |

For a **REJECT**, items 1, 2, and 3 are sufficient. Items 4, 5,
6 are pre-requisites for *approval*, not for *rejection*. Since
CAMPAIGN_011 cannot be promoted (null model), the missing items
5 and 6 do not change the verdict.

For a hypothetical PASS — which CAMPAIGN_011 is expected to NOT
produce, and if it does, the documented response is the
investigation playbook (not promotion) per
[`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
§12 — the verifier extension would be triggered as part of the
investigation, never as a promotion gate.

## 5. Comparison to CAMPAIGN_010's verifier status

| dimension | CAMPAIGN_010 | CAMPAIGN_011 |
|---|---|---|
| candidate type | research candidate (could become paper if it had passed) | **null model (cannot become paper ever)** |
| verifier extension needed for verdict? | no (REJECT is sufficient with items 1–3) | no (REJECT is sufficient and approval is structurally impossible) |
| verifier extension recommended? | no — candidate is rejected, work in a dead path is wasted | **yes — uniquely useful as a reusable exact-equivalence template** |
| if extension is done, expected tolerance | WARN-band (rule-induced variance) | **exact** (deterministic seed) |

## 6. Recommendation

- **Do not extend the verifier for CAMPAIGN_011 inside this
  scaffold sprint.** Out of scope; this sprint produces no
  evidence-sprint trade artifacts to corroborate against.
- **Do not extend the verifier inside the future
  CAMPAIGN_011 evidence sprint either.** The evidence sprint's
  charter is to produce the walk-forward + financing + risk
  artifacts; verifier work is a separate sprint.
- **Do consider extending the verifier in a follow-up sprint
  named `infra-free-local-parity-verifier-random-entry-001`**
  after CAMPAIGN_011 evidence is committed. The exact-equivalence
  property is valuable both as a pipeline-correctness check and
  as a reusable template for future candidates.
- **Keep the verifier package's scope clearly documented.** The
  CAMPAIGN_002-only scope is honest; future candidates should
  each get their own verifier-extension sprint when (and only
  when) they survive walk-forward + financing under the
  evidence pipeline.

## 7. Safety state (unchanged)

- `configs/approved_strategies.yaml`: **`approved: []`**.
- **CAMPAIGN_002 remains REJECT** (untouched).
- **CAMPAIGN_010 remains REJECT** (untouched).
- **No verifier code change** in this sprint. The verifier
  package is read in the docs only; not modified.
- **No new external dependency.**
- **No broker call, no `.env` read, no credential printed.**
- **No QuantConnect / LEAN.**

## 8. Cross-links

- [`research/parity_verifier/README.md`](../../research/parity_verifier/README.md)
- [`FREE_LOCAL_PARITY_VERIFIER_PLAN.md`](FREE_LOCAL_PARITY_VERIFIER_PLAN.md)
  (the original CAMPAIGN_002 verifier design)
- [`FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md`](FREE_LOCAL_PARITY_VERIFIER_ACCEPTED_STATUS.md)
  (the CAMPAIGN_002 corroboration result)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md)
  (CAMPAIGN_010's verifier capability gap analysis — the same
  posture this CAMPAIGN_011 doc takes, with the added insight
  that random's determinism makes extension uniquely valuable)
- [`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_011_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_STATUS.md`](CAMPAIGN_011_STATUS.md)
- [`CAMPAIGN_011_WALK_FORWARD_READINESS.md`](CAMPAIGN_011_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_011_FINANCING_RISK_READINESS.md`](CAMPAIGN_011_FINANCING_RISK_READINESS.md)
- [`NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md`](NEXT_PREFERRED_CANDIDATE_IMPLEMENTATION_DESIGN_002.md)
- [`NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md`](NEXT_CANDIDATE_EVIDENCE_BRANCH_SPEC_002.md)
- [`NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md`](NEXT_RESEARCH_DIRECTION_AFTER_CAMPAIGN_002_REJECT.md)
  §8 (six-evidence ladder)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
