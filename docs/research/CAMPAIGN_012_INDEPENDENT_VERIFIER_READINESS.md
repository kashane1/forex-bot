# CAMPAIGN_012 Independent-Verifier Readiness

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

Phase 6 readiness doc for the independent verifier coverage of
CAMPAIGN_012. This doc records the current capability gap, when the
gap must be closed, and the suggested future sprint that closes it.
**No verifier code is run or modified this sprint.**

> No verifier extension built. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_002 / 010 / 011 remain REJECT and untouched.

## 1. Current verifier capability lock

The free / local parity verifier
(`research/parity_verifier/`) is **capability-locked to CAMPAIGN_002 /
`trend_following 0.1.0`**. It cannot validate
`regime_switcher_atr_percentile` today because:

- The verifier's signal-replication logic is family-specific
  (EMA + Donchian, the CAMPAIGN_002 shape).
- The verifier has no D1AGG aggregator implementation.
- The verifier has no regime-feature implementation.
- The verifier has no `numpy.percentile`-based trailing-window logic.

Prior campaigns documented this state:

- CAMPAIGN_010 verifier status: "verifier did NOT run for CAMPAIGN_010;
  would only matter for a hypothetical PASS (not for this REJECT)".
- CAMPAIGN_011 verifier status: same; null-model REJECT did not require
  verifier corroboration.

## 2. Verifier is **not required** for a clean REJECT

Per the [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
six-evidence ladder: item 5 (independent verifier) is a
**paper-promotion gate**. A REJECT verdict does not require any
independent corroboration — the gates already rejected the candidate.

If CAMPAIGN_012's evidence verdict is REJECT (any reason — per-fold
gate failure, aggregate gate failure, financing flip, or
"indistinguishable from null"), the verifier extension can be
indefinitely deferred without violating the freeze.

## 3. Verifier IS REQUIRED before any paper-promotion consideration

If CAMPAIGN_012's evidence verdict reaches **`RESEARCH_PASS_UNAPPROVED`**:

- All per-fold + aggregate + financing + null-baseline gates pass.
- The classification is `RESEARCH_PASS_UNAPPROVED` — never `APPROVED`
  by any research sprint.
- **Before** any human approval action can consider the candidate, the
  verifier-extension sprint
  **`infra-free-local-parity-verifier-regime-switcher-001`** must run
  and corroborate the per-pair-per-fold trade counts within the
  existing WARN-band tolerances.

Without verifier corroboration, item 5 of the six-evidence ladder is
**unmet** and the candidate cannot enter
`configs/approved_strategies.yaml`.

## 4. Suggested future sprint

| field | value |
|---|---|
| **branch name** | **`infra-free-local-parity-verifier-regime-switcher-001`** |
| trigger | only required if CAMPAIGN_012 evidence verdict is `RESEARCH_PASS_UNAPPROVED` |
| reference | sibling pattern: `infra-free-local-parity-verifier-001` (CAMPAIGN_002 verifier; existing) |
| scope | re-implement the regime-switcher signal logic **independently** (no `forex_bot.strategies.regime_switcher_atr_percentile` import); re-implement D1AGG aggregation independently (only `hashlib` / `datetime` / `numpy`); compare per-pair per-fold trade counts within existing WARN-band tolerances |
| approval allowed by this sprint? | **NO** — verifier extension is item 5 of the ladder; approval is item 6 (separate human action) |

### 4.1 Verifier scope (if/when extension is required)

The verifier extension must:

- Re-implement `_compute_regime` from spec text in
  [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
  §3 (R3) — not copied from `src/forex_bot/strategies/regime_switcher_atr_percentile.py`.
- Re-implement the D1AGG aggregation independently using only
  `hashlib`, `datetime`, and `numpy` — no `forex_bot` imports.
- Compare per-pair per-fold trade counts within the existing WARN-band
  tolerances. The regime gate's *binary* classification (HIGH-VOL vs
  LOW-VOL) means trade-count *exact* equivalence is achievable in
  principle (subject to floating-point determinism in the percentile
  computation).
- Re-emit a deterministic Signal for each HIGH-VOL bar with a trend
  filter pass; compare side + signal_id (or canonical input string) to
  the strategy module's output.
- Report any discrepancy as a verifier WARN (≤ tolerance) or FAIL
  (> tolerance) per pair per fold.

### 4.2 Why a regime switcher is *especially well-suited* to verifier corroboration

Unlike `trend_following` whose EMA crossovers can produce slightly
different timestamps under different numerical-precision paths, the
regime-switcher's:

- Reference D1AGG ATR is a discrete value at a discrete day.
- The trailing-60 percentile is computed from a discrete-day window.
- The HIGH-VOL/LOW-VOL classification is binary.
- The trend filter is a binary comparison.

This makes the *count* of HIGH-VOL bars and the *count* of trend-pass
bars amenable to exact (not just WARN-band) corroboration. The
verifier extension can therefore set tighter tolerances than the
existing CAMPAIGN_002 verifier.

## 5. What this readiness doc does NOT do

- Does not build or modify the verifier.
- Does not run the verifier on any candidate.
- Does not produce strategy evidence.
- Does not approve any strategy.
- Does not authorize the suggested verifier-extension sprint to begin —
  that requires an explicit human action.

## 6. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_012_WALK_FORWARD_READINESS.md`](CAMPAIGN_012_WALK_FORWARD_READINESS.md)
- [`CAMPAIGN_012_FINANCING_RISK_READINESS.md`](CAMPAIGN_012_FINANCING_RISK_READINESS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) (sibling reference)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) (sibling reference)
