# `research-cross-pair-currency-strength-rotation-walk-forward-001` — Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-cross-pair-currency-strength-rotation-walk-forward-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the CAMPAIGN_013 evidence sprint. Ran the
full walk-forward + financing overlay + portfolio-risk diagnostics +
verifier assessment for `cross_pair_currency_strength_rotation
0.1.0-c013` (the C6 cross-pair currency-strength rotation
candidate).

> **Verdict: `REJECT`.** 5 of 8 inherited aggregate gates fail;
> the worst-performing campaign to date by aggregate return, profit
> factor, and trade count. Catastrophically worse than CAMPAIGN_011
> null baseline. The cross-pair runner integration contract was
> **SATISFIED** on all 8 folds; the REJECT is on inherited gates
> alone (not BLOCKED). `configs/approved_strategies.yaml` remains
> `approved: []`. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011 /
> CAMPAIGN_012 remain REJECT and untouched. Paper / demo / live
> remain blocked.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 10 (Phase 0 through Phase 9) |
| files added | 12 new docs + 3 new scripts |
| files edited | 4 (EVIDENCE_INDEX + EVIDENCE_MANIFEST + STRATEGY_STATUS + test) |
| Python LOC added | ~1,400 (1 runner + 1 financing overlay + 1 risk diagnostics; runner is larger due to cross-pair contract) |
| committed artifact files | ~120 (56 fold summary.json + 56 fold trades.csv + 3 walk-forward JSON/MD + 3 financing JSON/MD + 2 risk JSON/MD) |
| markdown LOC added | ~3,300 (12 phase / status / summary docs) |
| pytest count | **875 → 875** (preserved; runner-test convention follows CAMPAIGN_010 / 011 / 012) |
| ruff findings | **3 pre-existing** in `research/lean_parity/algorithms/` (unchanged baseline) |
| walk-forward runtime | **~20.2 seconds** for 8 folds × 7 pairs = 56 backtests (much faster than CAMPAIGN_012's ~33 min; no D1AGG aggregation) |

### 1.1 Commits by phase

| phase | commit | scope |
|---|---|---|
| Phase 0 | `959eb3c` | repo truth audit + evidence-sprint plan |
| Phase 1 | `d88073c` | data availability + provenance |
| Phase 2 | `ac86cfa` | authoritative walk-forward plan |
| Phase 3 | `56785f3` | per-fold runner with cross-pair contract |
| Phase 4 | `df07aa6` | execute per-fold backtests |
| Phase 5 | `adb3995` | walk-forward verdict + null-baseline comparison |
| Phase 6 | `7778baa` | financing overlay (ESTIMATED + conservative stress) |
| Phase 7 | `273ee01` | portfolio-risk diagnostics |
| Phase 8 | `799fcfc` | independent verifier status |
| Phase 9 | (this commit) | finalize: EVIDENCE_INDEX + EVIDENCE_MANIFEST + STRATEGY_STATUS + SUMMARY + test update |

## 2. Implementation status

- **Scripts added:**
  - `scripts/run_campaign_013.py` — per-fold runner with **binding cross-pair runner integration contract**: loads all 7 pairs' completed H4 candles, aligns to common timestamp index, validates finite + positive endpoints, injects `cross_pair_closes` into each pair's `strategy_config`, fails closed (`BLOCKED`) if any pair missing/misaligned/non-finite/insufficient. Frozen-parameter assertion before any backtest.
  - `scripts/build_campaign_013_financing_overlay.py` (mirrors `build_campaign_012_*` with campaign-id swap).
  - `scripts/build_campaign_013_risk_diagnostics.py` (extends `build_campaign_012_*` with cross-pair-specific sections: zero-cells, long/short, simultaneous signals, firing rate, contract status).
- **No source code change** in `src/forex_bot/strategies/cross_pair_currency_strength_rotation.py`, `src/forex_bot/config.py`, RiskEngine, BacktestEngine, loops, or financing — all execution used the scaffold-sprint code verbatim.
- **No frozen-parameter change** at any point. The runner's `_assert_frozen()` re-verified all 9 parameters against `CAMPAIGN_013_PRECOMMIT_CHECKLIST.md` §4 before each fold; 0 mismatches across all 56 backtests.

## 3. Walk-forward status

- **Plan:** 8 folds, rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20 — inherited verbatim from CAMPAIGN_010 / 011 / 012.
- **Execution:** all 56 backtests completed without exception; runner did not abort; no implementation bug fixes required; **all 8 folds satisfied the cross-pair runner integration contract** (common_index 1,825-1,848 H4 bars).
- **Aggregate:** **7,940 trades**; expectancy **−0.0564 R**; PF **0.000**; return **−113.36 %** over 4 years; **1 / 7 pairs positive** (USD_JPY +0.0000); **0 / 8 folds pass**.
- **Verdict:** **REJECT** (5 of 8 aggregate gates fail) — not BLOCKED (contract satisfied) and not REJECT_INDISTINGUISHABLE_FROM_NULL (metrics diverge from null in worse direction far outside ±band).

## 4. Null-baseline comparison status (binding)

| metric | CAMPAIGN_011 | CAMPAIGN_013 | difference | in indistinguishability band? | meaningful improvement? |
|---|---:|---:|---:|:---:|:---:|
| aggregate expectancy R | −0.0024 | **−0.0564** | −0.0540 | NO | NO — WORSE |
| aggregate profit factor | 0.91 | **0.000** | −0.910 | NO | NO — WORSE |
| aggregate return % (4 y) | −0.53 % | **−113.36 %** | −112.83 pp | NO | NO — WORSE |
| pairs_positive | 3 / 7 | **1 / 7** | −2 pairs | boundary (worse direction) | NO — WORSE |
| fold pass rate | 0 / 8 | **0 / 8** | 0 | YES (same as null) | NO |

CAMPAIGN_013 is **worse than null** on every binding axis.
Classification: **REJECT** (NOT `REJECT_INDISTINGUISHABLE_FROM_NULL`).

## 5. Financing overlay status

- **Source:** `conservative_stress` (`FinancingTreatment.estimated`); **MODELED refused at 4 layers (intact).**
- **7,154 rollover events** over 7,940 trades; missing-rate events: 0.
- `cashflow_home_total = −$139.99`; `cashflow_home_stress_total = −$139.99` (the conservative-stress source is the worst-case projection by construction).
- **1 pair flips + → −** under stress (USD_JPY: pre-fin +$2.27 → post-fin −$5.89), taking `pairs_positive_count` from 1/7 to 0/7 post-financing. (1/7 was already a gate failure; 0/7 is more failure, not a verdict change.)
- **Gate `conservative_stress_run_does_not_flip_verdict` PASSES** — verdict was already REJECT pre-financing; financing makes it more REJECT, not less.
- **Live-promotion financing blocker stands** independently of CAMPAIGN_013's verdict.

## 6. Portfolio-risk diagnostics status

- **All standard diagnostics computed.** No diagnostic finding contradicts the REJECT verdict.
- **Cross-pair-specific findings (new in CAMPAIGN_013):**
  - Cross-pair runner contract: SATISFIED on all 8 folds.
  - Zero-trade pair-fold cells: 29 / 56 (51.8 %) — rank-gap rule's intended sparseness.
  - Per-fold long/short imbalance: dramatic regime swings (fold 1 100% short, fold 2 100% long); aggregate ~50/50.
  - Simultaneous-signal frequency: **~40 % of trading bars have ≥ 2 pairs entering at the same H4 timestamp** (up to 4 pairs simultaneously on some bars).
  - Per-pair firing rate: ~16-18 % of bars for trading pairs (not a true "high-conviction" rotator).
- **Architectural finding:** `MAX_OPEN_POSITIONS_EXCEEDED = 0` — the BacktestEngine is single-instrument; the runner invokes one engine per pair per fold. A portfolio-aware runner would cut trade count by ~40 % via simultaneous-signal filtering but cannot rescue per-pair negative expectancy (6 of 7 pairs are negative). The standing rule "do not relax `max_open_positions` to rescue trade count" remains intact.
- RiskEngine rejections: **5,523 total (41 % rejection rate)** — SPREAD_TOO_WIDE 3,024, DRAWDOWN_LIMIT 1,507 (concentrated USD_CHF + NZD_USD), SESSION_BLOCKED 992.
- Time-stop exit: **76.7 %** (consistent with no-edge time-stop-exit pattern).
- Diagnostics are **diagnostic only**; do not flip the verdict.

## 7. Verifier status

- **Did not run.** Verifier is capability-locked to CAMPAIGN_002 / `trend_following`.
- **Not required for REJECT** (item 5 of the six-evidence ladder is a paper-promotion gate).
- The recommended follow-up sprint `infra-free-local-parity-verifier-cross-pair-currency-strength-rotation-001` is **deferred indefinitely** (no paper-promotion candidate to corroborate; the extension would be structurally larger than CAMPAIGN_012's would have been because of the cross-pair runner integration contract re-implementation requirement).

## 8. Safety state at sprint close

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| CAMPAIGN_012 | REJECT (untouched) |
| **CAMPAIGN_013** | **REJECT (this sprint)** |
| approved strategies | **none** |
| paper-loop refuses | ✓ |
| demo-loop refuses | ✓ |
| `live-loop` command | does not exist |
| QuantConnect / LEAN | retired |
| MODELED financing reachable | no (4 refusal layers; intact) |
| live-promotion financing blocker | stands |
| broker / OANDA call this sprint | **none** |
| `.env` read / credential printed | **none** |
| account / order / trade / position / transaction endpoint queried | **none** |
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 / 012 untouched) |
| parameter "tweak" or "rescue" | **none** (frozen parameters intact across all 10 phases) |
| `max_open_positions` relaxation | **none** (rule explicitly maintained) |
| `src/forex_bot/financing.py` edit | **none** |
| RiskEngine / engine / loops edit | **none** |
| new external dependency | **none** |
| pytest baseline | 875 (preserved) |
| ruff baseline | 3 pre-existing in `research/lean_parity/` (unchanged) |

## 9. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **MODELED financing refused at 4 layers** | live promotion of any future candidate | `research-financing-modeled-capture-credentialed-001` (separately authorized credentialed pilot) |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of six-evidence ladder for any non-`trend_following` candidate | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family that reaches `RESEARCH_PASS_UNAPPROVED`; **not needed for CAMPAIGN_013's REJECT** |
| **C2 / C4 / C7 / C8 / C9 deferred** | next-candidate menu after CAMPAIGN_013's REJECT | discovery-005 sprint should reassess; CAMPAIGN_013's catastrophic loss adds important data on turnover-amplifying filters |
| **3 pre-existing ruff findings** in `research/lean_parity/algorithms/` | code-quality only; no runtime impact | `infra-ruff-lean-parity-archive-cleanup-001` (low-priority cleanup) |

**None of these block any next step** — CAMPAIGN_013 is rejected; what comes next is a discovery sprint to pick a different candidate family.

## 10. Recommended next branch

### Two reasonable options (mutually exclusive)

#### **Option A:** **`research-new-candidate-strategy-discovery-005`** (discovery sprint)

Re-open the discovery loop now that CAMPAIGN_013 has rejected the
cross-pair-rotation hypothesis. Scope:

- Codify CAMPAIGN_013 as an additional rejected-family reference
  (the cross-pair currency-strength rotation cohort is now also off
  the menu under the same parameters).
- Codify the new **turnover-amplification anti-pattern** lesson:
  CAMPAIGN_012 (regime gate, 3,726 trades, −43.52 %) and
  CAMPAIGN_013 (cross-pair rank, 7,940 trades, −113.36 %) both
  demonstrate that adding a turnover-amplifying filter to a
  negative-edge entry direction on H4 majors makes results
  materially worse, not better — the incremental complexity buys
  trade frequency without buying signal quality. New families
  should not propose turnover-amplifying filters on top of
  rejected entry directions.
- Re-score the deferred C2 / C4 / C7 / C8 / C9 candidates against
  the now-8 rejected baseline (5 prior + CAMPAIGN_011 null +
  CAMPAIGN_012 + CAMPAIGN_013).
- Consider entry directions that have not yet been tested on this
  universe (e.g. pure intra-bar imbalance, calendar-event windows,
  options-implied measures if obtainable read-only).

#### **Option B:** **`infra-engine-paired-entry-support-001`** OR **`research-financing-modeled-capture-credentialed-001`** (infrastructure unblock)

Unblock either C4 (engine paired-entry) or C2 (MODELED financing)
before re-opening discovery, so the next discovery has a richer
candidate menu.

**Recommended:** **Option A** — discovery-005. The infrastructure
sprints are heavier lifts; a fresh discovery with the now-8 rejected
baseline and the new turnover-amplification anti-pattern is likely
the most productive next step.

## 11. Exact files to review first

In review order:

1. **[`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_SUMMARY.md)** — this one-page sprint summary.
2. **[`CAMPAIGN_013_EVIDENCE_SUMMARY.md`](CAMPAIGN_013_EVIDENCE_SUMMARY.md)** — headline numbers; null-baseline interpretation; comparison to prior REJECT campaigns.
3. **[`CAMPAIGN_013_WALK_FORWARD_RESULT.md`](CAMPAIGN_013_WALK_FORWARD_RESULT.md)** — formal verdict with the binding gate vector + null-baseline comparison table + cross-pair rotator interpretation.
4. **[`CAMPAIGN_013_STATUS.md`](CAMPAIGN_013_STATUS.md)** — REJECTED status; per-strategy detail; CAMPAIGN_002 / 010 / 011 / 012 relationship.
5. **[`CAMPAIGN_013_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_013_WALK_FORWARD_EXECUTION.md)** — per-fold execution table + per-pair aggregate + cross-pair contract diagnostics.
6. **[`CAMPAIGN_013_FINANCING_OVERLAY.md`](CAMPAIGN_013_FINANCING_OVERLAY.md)** — ESTIMATED + conservative stress; USD_JPY flips + → −; MODELED refused.
7. **[`CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_013_PORTFOLIO_RISK_DIAGNOSTICS.md)** — standard + cross-pair-specific diagnostics; architectural finding on `MAX_OPEN_POSITIONS_EXCEEDED = 0`.
8. **[`CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_013_INDEPENDENT_VERIFIER_STATUS.md)** — verifier did not run; not required for REJECT.
9. **[`CAMPAIGN_013_DATA_PROVENANCE.md`](CAMPAIGN_013_DATA_PROVENANCE.md)** — hashes match CAMPAIGN_010 / 011 / 012 verbatim.
10. **[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)** (reference) — the binding null-baseline definition.
11. **`backtests/CAMPAIGN_013_cross_pair_currency_strength_rotation/walk_forward/results.md`** — auto-generated harness output.
12. **`scripts/run_campaign_013.py`** — the per-fold runner with cross-pair runner integration contract implementation.

## 12. Cross-links

- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_WALK_FORWARD_001_PLAN.md) (Phase 0)
- [`CAMPAIGN_013_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_013_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_IMPLEMENTATION_SPEC.md)
- [`CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md`](CROSS_PAIR_CURRENCY_STRENGTH_ROTATION_001_SUMMARY.md) (scaffold-sprint summary)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) (sibling)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) (sibling — the null baseline)
- [`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md) (sibling — most recent rejected real-edge candidate)
- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md) (sibling sprint summary)
