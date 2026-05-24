# CAMPAIGN_013 Independent-Verifier Readiness

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

Phase 6 readiness doc for the independent verifier coverage of
CAMPAIGN_013. Records the current capability gap, when the gap must
be closed, and the suggested future sprint that closes it. **No
verifier code is run or modified this sprint.**

> No verifier extension built. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 / 012 remain REJECT and untouched.

## 1. Current verifier capability lock

The free / local parity verifier (`research/parity_verifier/`) is
**capability-locked to CAMPAIGN_002 / `trend_following 0.1.0`**. It
cannot validate `cross_pair_currency_strength_rotation` today
because:

- The verifier's signal-replication logic is family-specific (EMA +
  Donchian, the CAMPAIGN_002 shape).
- The verifier has no cross-pair orchestration layer.
- The verifier has no per-pair log-return helper.
- The verifier has no 8-currency strength mapping or rank-gap rule.

Prior campaigns documented this state:

- CAMPAIGN_010 / 011 / 012 verifier status: capability-locked;
  REJECT verdicts do not require verifier corroboration.

## 2. Verifier is **not required** for a clean REJECT

Per the [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
six-evidence ladder: item 5 (independent verifier) is a
**paper-promotion gate**. A REJECT verdict does not require any
independent corroboration — the gates already rejected the candidate.

If CAMPAIGN_013's evidence verdict is REJECT (any reason — per-fold
gate failure, aggregate gate failure, financing flip,
"indistinguishable from null", or BLOCKED), the verifier extension
can be indefinitely deferred without violating the freeze.

## 3. Verifier IS REQUIRED before any paper-promotion consideration

If CAMPAIGN_013's evidence verdict reaches **`RESEARCH_PASS_UNAPPROVED`**:

- All per-fold + aggregate + financing + null-baseline gates pass.
- The classification is `RESEARCH_PASS_UNAPPROVED` — never
  `APPROVED` by any research sprint.
- **Before** any human approval action can consider the candidate,
  the verifier-extension sprint
  **`infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`**
  must run and corroborate the per-pair-per-fold trade counts within
  the existing WARN-band tolerances.

Without verifier corroboration, item 5 of the six-evidence ladder is
**unmet** and the candidate cannot enter
`configs/approved_strategies.yaml`.

## 4. Suggested future sprint

| field | value |
|---|---|
| **branch name** | **`infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`** |
| trigger | only required if CAMPAIGN_013 evidence verdict is `RESEARCH_PASS_UNAPPROVED` |
| reference | sibling pattern: `infra-free-local-parity-verifier-001` (CAMPAIGN_002 verifier; existing) |
| approval allowed by this sprint? | **NO** — verifier extension is item 5; approval is item 6 (separate human action) |

### 4.1 Verifier scope (if/when extension is required)

The verifier extension must:

- Re-implement the cross-pair strength computation from spec text in
  [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
  §3 + §4 R4–R5 — not copied from the strategy module.
- Re-implement the rank-gap rule independently using only standard
  library + `numpy` — no `forex_bot` imports.
- Re-implement the multi-pair orchestration: load all 7 pairs;
  align to a common index; compute strength + ranks per bar;
  determine per-pair signals.
- Compare per-pair-per-fold trade counts within WARN-band
  tolerances. Cross-pair rotation's *rank-gap* gate is discrete
  (integer ranks), so trade-count exact equivalence is achievable
  in principle subject to floating-point determinism of the log-
  return computation.

### 4.2 Why a cross-pair rotator is *especially well-suited* to verifier corroboration

Unlike `trend_following` whose EMA crossovers can produce slightly
different timestamps under different numerical-precision paths, the
cross-pair rotator's:

- Per-pair n-bar log returns are discrete values at discrete bars.
- 8-currency strengths are weighted sums.
- Ranks are integers (with documented alphabetic tiebreak).
- Rank-gap rule is a binary comparison.

This makes the *count* of signal-firing bars amenable to exact
(not just WARN-band) corroboration. The verifier extension can
therefore set tighter tolerances than the existing CAMPAIGN_002
verifier.

## 5. Why verifier is NOT blocking the current verdict

CAMPAIGN_013 has no verdict yet (this is a scaffold sprint). When
the future evidence sprint runs:

- **REJECT is REJECT** — no corroboration can change a clean
  inherited-gate failure.
- **`RESEARCH_PASS_UNAPPROVED` requires verifier extension** —
  documented in §3.
- **BLOCKED requires no verifier** — the runner couldn't complete.

## 6. What the verifier was NOT used for (binding)

- The verifier did **not** validate `cross_pair_currency_strength_rotation`
  (capability lock; would require the extension sprint).
- The verifier did **not** validate `random_entry_anchor`
  (CAMPAIGN_011 — capability lock).
- The verifier did **not** validate `session_breakout` (CAMPAIGN_010
  — capability lock).
- The verifier did **not** validate `regime_switcher_atr_percentile`
  (CAMPAIGN_012 — capability lock).
- The verifier did **not** validate `cross_pair_currency_strength_rotation`
  via the existing `trend_following`-only adapter (would be a logical
  category error).
- No QuantConnect / LEAN-based comparison ran (LEAN is retired).
- No broker-call-based comparison ran (forbidden).

## 7. Explicit no-approval statement

The absence of a verifier run does **not** affect CAMPAIGN_013's
future verdict in either direction. If REJECT: verifier was not
needed. If `RESEARCH_PASS_UNAPPROVED`: verifier extension is then
required before paper-promotion consideration. The verifier
extension sprint is **not authorized to begin** under any verdict
other than `RESEARCH_PASS_UNAPPROVED`.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked.

## 8. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_013_WALK_FORWARD_READINESS.md`](CAMPAIGN_013_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_013_FINANCING_RISK_READINESS.md`](CAMPAIGN_013_FINANCING_RISK_READINESS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md), [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md), [`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md) (sibling references — identical capability lock)
