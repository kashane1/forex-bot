# CAMPAIGN_013 Status — `cross_pair_currency_strength_rotation 0.1.0-c013`

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-001`
`strategy_evidence: false`

| dimension | value |
|---|---|
| candidate | `cross_pair_currency_strength_rotation 0.1.0-c013` |
| family | cross-pair currency-strength rotation (C6) |
| campaign id | CAMPAIGN_013 |
| status | **candidate scaffold only** |
| backtest verdict | **none yet — no evidence campaign has run** |
| walk-forward verdict | **none yet** |
| financing overlay verdict | **none yet** |
| portfolio-risk diagnostics verdict | **none yet** |
| independent verifier status | **not run** (verifier capability-locked to CAMPAIGN_002) |
| strategy approval | **NO — cannot be approved by any research sprint** |
| paper / demo / live | **blocked** |
| in `configs/approved_strategies.yaml` | **no** (registry remains `approved: []`) |
| enabled in `configs/paper.yaml` | **no** |
| enabled in `configs/practice.yaml` | **no** |

## What this means

CAMPAIGN_013 is **scaffolded only**. The
`research-cross-pair-currency-strength-rotation-001` sprint added the
strategy module
(`src/forex_bot/strategies/cross_pair_currency_strength_rotation.py`),
the config schema (`CrossPairCurrencyStrengthRotationStrategyConfig`),
57 unit tests, the candidate YAML
(`configs/campaign_013_cross_pair_currency_strength_rotation.yaml`),
and the CAMPAIGN_013 readiness docs. **No backtest, walk-forward,
financing overlay, risk-diagnostics, or verifier evidence has been
produced.**

A passing unit-test suite or non-evidence smoke is **not** strategy
evidence. The candidate cannot be paper-promoted, demo-deployed, or
live-traded under any circumstance until **all** of the following are
complete:

1. The future `research-cross-pair-currency-strength-rotation-walk-forward-001`
   evidence sprint runs the full 8-fold walk-forward, financing
   overlay (ESTIMATED + conservative stress; MODELED refused), and
   portfolio-risk diagnostics on the 7-pair OANDA practice H4
   universe (2020-01-01 → 2026-05-20) and writes a verdict doc.
2. The verdict passes all per-fold + aggregate gates inherited
   verbatim from CAMPAIGN_010 / 011 / 012 (see
   [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
   §11).
3. The verdict beats the CAMPAIGN_011 null-baseline floor by the
   meaningful-improvement margins codified in
   [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
   — ≥ +0.0524 R aggregate expectancy, ≥ +0.19 PF, ≥ +5.5 pp
   pairs-positive, ≥ +1 pair, 100 % fold pass rate. An
   "indistinguishable from null" result (within ± 0.005 R / ± 0.10
   PF / ± 2 pp / ± 1 pair of CAMPAIGN_011) is REJECTED regardless of
   which gates technically pass.
4. The verifier-extension sprint
   `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001`
   runs and corroborates the per-pair-per-fold trade counts within
   the existing WARN-band tolerances.
5. A deliberate human approval action edits
   `configs/approved_strategies.yaml` per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md).

Steps 4 and 5 are out of scope for any research sprint. Steps 1–3
are reserved for the future evidence sprint.

## CAMPAIGN_002 / 010 / 011 / 012 relationship

| campaign | status | relation to CAMPAIGN_013 |
|---|---|---|
| CAMPAIGN_002 | REJECT (negative expectancy) | structurally unrelated; different entry family (no EMA / Donchian) |
| CAMPAIGN_010 | REJECT (session breakout) | inherited gate vector + data + financing infrastructure; NO mechanism reuse (different signal family) |
| CAMPAIGN_011 | REJECT (null-model anchor) | inherited gate vector + data + financing infrastructure; CAMPAIGN_011 is the **null baseline** that CAMPAIGN_013 must beat by a meaningful margin. **CAMPAIGN_011 is only the null baseline and not a trading candidate** — it is structurally impossible to approve. |
| CAMPAIGN_012 | REJECT (regime switcher) | inherited gate vector + data + financing infrastructure; CAMPAIGN_012 is the most recent rejected real-edge candidate. CAMPAIGN_013 is a structurally distinct mechanism (cross-pair rank, not single-pair vol percentile). |

All four remain REJECT. Their verdicts are unchanged by this sprint.

## Why this is a real candidate (not a null model, not a retune)

Unlike CAMPAIGN_011's `random_entry_anchor`, the C6 cross-pair
rotation has:

- A **directional hypothesis** (cross-pair relative-strength rank
  predicts the stronger-vs-weakest pair direction).
- A **deterministic feature-driven entry** — every signal is fully
  determined by observable price features, with no PRNG.
- A **cross-pair structure** never tested by CAMPAIGN_002 / 010 /
  011 / 012 — all four were per-pair single-instrument signals.
  Distinctness 6/6 vs each rejected family.
- The same exit / cost / financing / risk envelope as CAMPAIGN_010 /
  011 / 012 so the *comparison* is on the cross-pair-rank hypothesis
  alone.

This makes CAMPAIGN_013 the second non-trivial real-edge candidate
(after the C3 regime switcher, which was rejected as CAMPAIGN_012) —
but **selection is still not approval**. The evidence is what
matters.

## Safety state (verified)

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | **no** (4 refusal layers) |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 / 012 untouched) |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| pytest baseline | 818 → 875 (+57 new scaffold tests) |
| ruff baseline | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |

## Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_PLAN.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
