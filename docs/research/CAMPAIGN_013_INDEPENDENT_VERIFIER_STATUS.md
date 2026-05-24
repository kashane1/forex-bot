# CAMPAIGN_013 Independent Verifier Status (Phase 8)

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
`strategy_evidence: false`

Phase 8 verifier-status assessment for **CAMPAIGN_013 /
`cross_pair_currency_strength_rotation 0.1.0-c013`**. The Phase 5
verdict is `REJECT`. Per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) the
independent verifier (item 5 of the six-evidence ladder) is a
paper-promotion gate — **not required for a REJECT verdict.** This
doc records that the verifier did not run and that no extension is
warranted.

> No verifier code changed this sprint. No verifier run against
> CAMPAIGN_013. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Current verifier capability

| dimension | value |
|---|---|
| location | `research/parity_verifier/` |
| capability | re-implements **CAMPAIGN_002 `trend_following 0.1.0`** mechanics independently |
| imports | does **NOT** import `forex_bot.*` (verified by source-grep tests) |
| supports `random_entry_anchor` (CAMPAIGN_011)? | **NO** (no PRNG re-implementation) |
| supports `regime_switcher_atr_percentile` (CAMPAIGN_012)? | **NO** (no D1AGG aggregator / no regime-percentile helper) |
| supports `cross_pair_currency_strength_rotation` (CAMPAIGN_013)? | **NO** (no 8-currency-strength matrix / no cross-pair alignment / no rank-gap rule) |
| network / broker calls | **none** |
| reads | local files only |
| strategy_evidence | `false` (diagnostic only) |

The verifier is **capability-locked to CAMPAIGN_002**. It cannot
validate `cross_pair_currency_strength_rotation` without an
extension sprint — and in CAMPAIGN_013's case the extension would be
*structurally larger* than for CAMPAIGN_012 because the cross-pair
runner integration contract (load-7-pairs / align-common-index /
inject-`cross_pair_closes`) must also be re-implemented
independently.

## 2. Did the verifier run for CAMPAIGN_013?

**NO.** The verifier was not invoked against CAMPAIGN_013's per-fold
outputs because:

1. The verifier is capability-locked to CAMPAIGN_002 and lacks the
   logic to replicate the cross-pair signal:
   - 8-currency strength matrix computation
   - USD-base `+log_return` / USD-quote `−log_return` /
     USD = `−mean(non-USD)` signing
   - Strength ranking + rank-gap threshold rule
   - 7-pair common-index alignment (cross-pair runner integration
     contract)
   - Per-pair `cross_pair_closes` injection mechanism
2. The Phase 5 verdict is **REJECT** — the verifier (item 5 of the
   six-evidence ladder) is a paper-promotion gate, not a REJECT
   gate. A REJECT verdict is not corroborated or overturned by
   verifier presence/absence.

## 3. Is the verifier required for the current verdict?

**NO.** Per the six-evidence ladder:

| item | name | required for REJECT? | required for RESEARCH_PASS_UNAPPROVED? | required for paper promotion? |
|---|---|:---:|:---:|:---:|
| 1 | data provenance | ✓ | ✓ | ✓ |
| 2 | walk-forward verdict | ✓ | ✓ | ✓ |
| 3 | financing overlay | ✓ | ✓ | ✓ |
| 4 | risk diagnostics | ✓ | ✓ | ✓ |
| **5** | **independent verifier** | **✗** | **✓** | **✓** |
| 6 | deliberate human approval | ✗ | ✗ | ✓ |

CAMPAIGN_013's verdict is REJECT. Items 1–4 are complete; item 5 is
not required; item 6 is moot.

## 4. Required future branch (deferred indefinitely)

The verifier extension was originally suggested as
**`infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`**
during the Phase 0 plan of this sprint. It would have been required
if CAMPAIGN_013 had reached `RESEARCH_PASS_UNAPPROVED`. Given the
REJECT verdict, the extension is **deferred indefinitely** — there
is no paper-promotion candidate to corroborate.

Scope sketch (preserved for the historical record; **not authorized
to begin**):

- Re-implement the 8-currency strength matrix from spec text in
  [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
  — not copied from the strategy module.
- Re-implement cross-pair common-index alignment using only
  `pandas` / `numpy` — no `forex_bot` imports; no
  `research.cross_pair_runner` reuse.
- Re-implement the rank-gap rule `|rank(quote) − rank(base)| ≥ 4`
  inclusively (boundary semantics binding).
- Replicate the per-pair `cross_pair_closes` injection contract
  (load-all-pairs / intersect / validate finite + positive endpoints
  / fail-closed on missing/misaligned/non-finite).
- Compare per-pair-per-fold trade counts within WARN-band
  tolerances. The verifier would need to coordinate trades across 7
  parallel per-pair runs — substantially more complex than
  CAMPAIGN_010 / 012's per-pair-independent verification.
- Strength matrix → rank → rank-gap pipeline is *deterministic* (no
  randomness), so exact (not just WARN-band) corroboration is
  achievable in principle.
- Compute budget: this extension is **noticeably larger** than the
  CAMPAIGN_012 extension would have been — primarily because of the
  cross-pair alignment contract.

If a future *new* cross-pair-family candidate is selected, this scope
should be revisited then.

## 5. Why verifier is NOT blocking the current verdict

- **REJECT is REJECT** — no corroboration can change a clean
  inherited-gate failure.
- **5 of 8 aggregate gates FAIL** on the bespoke-engine run; the
  verifier is not the layer that fails them.
- **Null-baseline comparison REJECT** — CAMPAIGN_013 is
  catastrophically worse than CAMPAIGN_011 (−113.36 % vs −0.53 %
  aggregate return) and worse than CAMPAIGN_012 by 2.6 ×, with no
  plausible verifier-divergence story that could rescue it.
- **Cross-pair contract was satisfied** — the runner's contract
  diagnostics (common_index 1,825-1,848 H4 bars on every fold)
  confirm the cross-pair data alignment was correct; a verifier
  re-implementation would not find a contract violation to overturn.
- **No human approval action is contemplated** — the candidate is
  rejected.

## 6. What the verifier was NOT used for (binding)

- The verifier did **not** validate
  `cross_pair_currency_strength_rotation` (capability lock; would
  have required the extension sprint).
- The verifier did **not** validate `random_entry_anchor`
  (CAMPAIGN_011 — capability lock).
- The verifier did **not** validate `session_breakout` (CAMPAIGN_010
  — capability lock).
- The verifier did **not** validate
  `regime_switcher_atr_percentile` (CAMPAIGN_012 — capability lock).
- The verifier did **not** validate
  `cross_pair_currency_strength_rotation` via the existing
  `trend_following`-only adapter (would be a logical category
  error).
- No QuantConnect / LEAN-based comparison ran (LEAN is retired).
- No broker-call-based comparison ran (would require account/order
  endpoints; forbidden).

## 7. Verifier vs cross-pair runner contract — separation of concerns

The cross-pair runner integration contract (Phase 3 / Phase 4
requirement) is a **bespoke-engine** concern: the
`scripts/run_campaign_013.py` runner must load 7 pairs, intersect
their indices, and inject `cross_pair_closes` into the strategy's
config. This was **verified within the bespoke implementation**
(`cross_pair_diagnostics` in `fold_detail.json` shows
`contract_satisfied = true` on all 8 folds; see Phase 7 §7.1).

A future independent-verifier extension would re-implement this
contract *independently* — i.e. without importing
`research.cross_pair_runner` or `scripts.run_campaign_013` — to
corroborate that the bespoke implementation made no algorithmic
error in the cross-pair alignment step. This independent
re-implementation is distinct from the contract's *satisfaction*
(which is purely a bespoke-engine fact).

For CAMPAIGN_013 (REJECT), the independent re-implementation is
not required.

## 8. Explicit no-approval statement

The absence of a verifier run does **not** affect CAMPAIGN_013's
REJECT verdict. The candidate is rejected. The verifier extension
sprint
(`infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`)
is **not authorized** and is **deferred indefinitely**. No human
approval action is justified by this evidence.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked.

## 9. Cross-links

- [`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_READINESS.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) (sibling — identical capability lock)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) (sibling — identical capability lock)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md) (sibling — identical capability lock)
