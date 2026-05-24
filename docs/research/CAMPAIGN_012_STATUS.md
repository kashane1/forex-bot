# CAMPAIGN_012 Status — `regime_switcher_atr_percentile 0.1.0-c012`

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-001`
`strategy_evidence: false`

| dimension | value |
|---|---|
| candidate | `regime_switcher_atr_percentile 0.1.0-c012` |
| family | volatility-regime switching (C3) |
| campaign id | CAMPAIGN_012 |
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

CAMPAIGN_012 is **scaffolded only**. The `research-regime-switcher-atr-percentile-001`
sprint added the strategy module
(`src/forex_bot/strategies/regime_switcher_atr_percentile.py`), the
config schema (`RegimeSwitcherAtrPercentileStrategyConfig`), 47 unit
tests, the candidate YAML
(`configs/campaign_012_regime_switcher_atr_percentile.yaml`), and the
CAMPAIGN_012 readiness docs. **No backtest, walk-forward, financing
overlay, risk-diagnostics, or verifier evidence has been produced.**

A passing unit-test suite or non-evidence smoke is **not** strategy
evidence. The candidate cannot be paper-promoted, demo-deployed, or
live-traded under any circumstance until **all** of the following are
complete:

1. The future `research-regime-switcher-atr-percentile-walk-forward-001`
   evidence sprint runs the full 8-fold walk-forward, financing overlay
   (ESTIMATED + conservative stress; MODELED refused), and portfolio-risk
   diagnostics on the 7-pair OANDA practice H4 universe (2020-01-01 →
   2026-05-20) and writes a verdict doc.
2. The verdict passes all per-fold + aggregate gates inherited verbatim
   from CAMPAIGN_010 / CAMPAIGN_011 (see
   [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
   §10).
3. The verdict beats the CAMPAIGN_011 null-baseline floor by the
   meaningful-improvement margins codified in
   [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
   §3 — not just any positive number, but ≥ +0.0524 R aggregate
   expectancy / ≥ +0.19 profit factor / ≥ +5.5 pp pairs-positive /
   ≥ +1 pair / 100 % fold pass rate. An "indistinguishable from null"
   result (within ± 0.005 R / ± 0.10 PF / ± 2 pp / ± 1 pair of
   CAMPAIGN_011) is REJECTED regardless of which gates technically pass.
4. The verifier-extension sprint
   `infra-free-local-parity-verifier-regime-switcher-001` runs and
   corroborates the per-pair-per-fold trade counts within the existing
   WARN-band tolerances (item 5 of the six-evidence ladder; required
   for paper promotion).
5. A deliberate human approval action edits
   `configs/approved_strategies.yaml` per
   [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
   (item 6 of the six-evidence ladder).

Steps 4 and 5 are out of scope for any research sprint. Steps 1–3 are
reserved for the future evidence sprint.

## CAMPAIGN_002 / 010 / 011 relationship

| campaign | status | relation to CAMPAIGN_012 |
|---|---|---|
| CAMPAIGN_002 | REJECT (negative expectancy) | structurally unrelated; different entry family (no Donchian / no EMA) |
| CAMPAIGN_010 | REJECT (session breakout) | inherited gate vector + data + financing infrastructure; NO parameter reuse (different entry signal) |
| CAMPAIGN_011 | REJECT (null-model anchor) | inherited gate vector + data + financing infrastructure; CAMPAIGN_011 is the **null baseline** that CAMPAIGN_012 must beat by a meaningful margin (≥ +0.0524 R aggregate expectancy, ≥ +0.19 PF, ≥ +5.5 pp pairs-positive, ≥ +1 pair, 100 % fold pass rate). **CAMPAIGN_011 is only the null baseline and not a trading candidate** — it is structurally impossible to approve. |

All three remain REJECT. Their verdicts are unchanged by this sprint.

## Why this is a real candidate (not a null model)

Unlike CAMPAIGN_011's `random_entry_anchor`, the C3 regime switcher has:

- A **directional hypothesis** (close-vs-close trend continuation under
  HIGH-VOL regime; suppress trades under LOW-VOL regime).
- A **deterministic feature-driven entry** — every signal is fully
  determined by the observable price feature, with no PRNG and no
  `master_seed`.
- A **regime-conditional structure** never tested by CAMPAIGN_002 / 010 /
  011 — distinctness ≥ 5/6 vs every prior campaign (see
  [`NEXT_PREFERRED_REAL_CANDIDATE_003.md`](NEXT_PREFERRED_REAL_CANDIDATE_003.md)).
- The same exit / cost / financing / risk envelope as CAMPAIGN_010 / 011
  so the *comparison* is on the regime-gate hypothesis alone, not on a
  shifted goalpost.

This makes CAMPAIGN_012 the first real-edge candidate after the C5 null
model — but **selection is still not approval**. The evidence is what
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
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 untouched) |
| parameter "tweak" or "rescue" | **none** (frozen parameters unchanged) |
| pytest baseline | 771 → 818 (+47 new scaffold tests) |
| ruff baseline | 3 pre-existing in `research/lean_parity/algorithms/` (unchanged) |

## Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_PLAN.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md)
- [`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
