# CAMPAIGN_012 Independent Verifier Status (Phase 8)

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
`strategy_evidence: false`

Phase 8 verifier-status assessment for **CAMPAIGN_012 /
`regime_switcher_atr_percentile 0.1.0-c012`**. The Phase 5 verdict
is `REJECT`. Per
[`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md) the
independent verifier (item 5 of the six-evidence ladder) is a
paper-promotion gate — **not required for a REJECT verdict.** This
doc records that the verifier did not run and that no extension is
warranted.

> No verifier code changed this sprint. No verifier run against
> CAMPAIGN_012. No strategy approved.
> `configs/approved_strategies.yaml` remains `approved: []`.

## 1. Current verifier capability

| dimension | value |
|---|---|
| location | `research/parity_verifier/` |
| capability | re-implements **CAMPAIGN_002 `trend_following 0.1.0`** mechanics independently |
| imports | does **NOT** import `forex_bot.*` (verified by source-grep tests) |
| supports `random_entry_anchor` (CAMPAIGN_011)? | **NO** (no PRNG re-implementation) |
| supports `regime_switcher_atr_percentile` (CAMPAIGN_012)? | **NO** (no D1AGG aggregator; no regime-percentile helper; no trend-filter implementation) |
| network / broker calls | **none** |
| reads | local files only |
| strategy_evidence | `false` (diagnostic only) |

The verifier is **capability-locked to CAMPAIGN_002**. It cannot
validate `regime_switcher_atr_percentile` without an extension sprint.

## 2. Did the verifier run for CAMPAIGN_012?

**NO.** The verifier was not invoked against CAMPAIGN_012's per-fold
outputs because:

1. The verifier is capability-locked to CAMPAIGN_002 and lacks the
   logic to replicate the regime-switcher signal (D1AGG aggregator +
   Wilder ATR + trailing-60 percentile + close-vs-close trend +
   ATR-fraction floor).
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

CAMPAIGN_012's verdict is REJECT. Items 1–4 are complete; item 5 is
not required; items 6 is moot.

## 4. Required future branch (deferred indefinitely)

The verifier extension was originally suggested as
**`infra-free-local-parity-verifier-regime-switcher-001`** during
the discovery-003 sprint. It would have been required if CAMPAIGN_012
had reached `RESEARCH_PASS_UNAPPROVED`. Given the REJECT verdict, the
extension is **deferred indefinitely** — there is no paper-promotion
candidate to corroborate.

Scope sketch (preserved for the historical record; **not authorized
to begin**):

- Re-implement `_compute_regime` from spec text in
  [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
  §3 (R3) — not copied from the strategy module.
- Re-implement D1AGG aggregation independently using only `hashlib`,
  `datetime`, `numpy` — no `forex_bot` imports.
- Compare per-pair-per-fold trade counts within WARN-band tolerances.
- Regime classifier is binary → exact (not just WARN-band)
  corroboration achievable in principle.

If a future *new* regime-family candidate is selected, this scope
should be revisited then.

## 5. Why verifier is NOT blocking the current verdict

- **REJECT is REJECT** — no corroboration can change a clean
  inherited-gate failure.
- **5 of 8 aggregate gates FAIL** on the bespoke-engine run; the
  verifier is not the layer that fails them.
- **Null-baseline comparison REJECT** — CAMPAIGN_012 is significantly
  worse than CAMPAIGN_011, with no plausible verifier-divergence
  story that could rescue it.
- **No human approval action is contemplated** — the candidate is
  rejected.

## 6. What the verifier was NOT used for (binding)

- The verifier did **not** validate `regime_switcher_atr_percentile`
  (capability lock; would have required the extension sprint).
- The verifier did **not** validate `random_entry_anchor`
  (CAMPAIGN_011 — capability lock).
- The verifier did **not** validate `session_breakout` (CAMPAIGN_010
  — capability lock).
- The verifier did **not** validate `regime_switcher_atr_percentile`
  via the existing `trend_following`-only adapter (would be a logical
  category error).
- No QuantConnect / LEAN-based comparison ran (LEAN is retired).
- No broker-call-based comparison ran (would require account/order
  endpoints; forbidden).

## 7. Explicit no-approval statement

The absence of a verifier run does **not** affect CAMPAIGN_012's
REJECT verdict. The candidate is rejected. The verifier extension
sprint is **not authorized** and is **deferred indefinitely**. No
human approval action is justified by this evidence.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked.

## 8. Cross-links

- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)
- [`CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_READINESS.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_010_INDEPENDENT_VERIFIER_STATUS.md) (sibling — identical capability lock)
- [`CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_011_INDEPENDENT_VERIFIER_STATUS.md) (sibling — identical capability lock)
