# `research-regime-switcher-atr-percentile-walk-forward-001` — Sprint Summary

**Date:** 2026-05-23 · **Branch:** `research-regime-switcher-atr-percentile-walk-forward-001`
(worktree branch `claude/affectionate-fermi-d950fc`) · `strategy_evidence: false`

End-of-sprint summary for the CAMPAIGN_012 evidence sprint. Ran the
full walk-forward + financing overlay + risk diagnostics + verifier
assessment for `regime_switcher_atr_percentile 0.1.0-c012`.

> **Verdict: `REJECT`.** 5 of 8 inherited aggregate gates fail; metrics
> markedly worse than CAMPAIGN_011 null baseline. `configs/approved_strategies.yaml`
> remains `approved: []`. CAMPAIGN_002 / CAMPAIGN_010 / CAMPAIGN_011
> remain REJECT and untouched. Paper / demo / live remain blocked.

## 1. What changed

| dimension | value |
|---|---|
| commits this sprint | 10 (Phase 0 through Phase 9) |
| files added | 11 new docs + 2 new scripts + 1 strategy module file (already from scaffold) |
| files edited | 4 (EVIDENCE_INDEX + EVIDENCE_MANIFEST + STRATEGY_STATUS + test) |
| Python LOC added | ~750 (1 runner + 1 financing overlay + 1 risk diagnostics) |
| committed artifact files | 119 (56 fold summary.json + 56 fold trades.csv + 3 walk-forward JSON/MD + 3 financing JSON/MD + 2 risk JSON/MD) |
| markdown LOC added | ~2,750 (11 phase / status / summary docs) |
| pytest count | **818 → 818** (preserved; runner-test convention follows CAMPAIGN_010 / 011) |
| ruff findings | **3 pre-existing** in `research/lean_parity/algorithms/` (unchanged baseline) |
| walk-forward runtime | ~2,022 seconds (~33.7 min) for 8 folds × 7 pairs = 56 backtests |

### 1.1 Commits by phase

| phase | commit | scope |
|---|---|---|
| Phase 0 | `357fc05` | repo truth audit + evidence-sprint plan |
| Phase 1 | `00a25d7` | data availability + provenance |
| Phase 2 | `641ae7b` | authoritative walk-forward plan |
| Phase 3 | `216b486` | per-fold runner |
| Phase 4 | `1fc2084` | execute per-fold backtests |
| Phase 5 | `95a46bd` | walk-forward verdict + null-baseline comparison |
| Phase 6 | `ce4677f` | financing overlay |
| Phase 7 | `479c4a4` | portfolio-risk diagnostics |
| Phase 8 | `c26616d` | independent verifier status |
| Phase 9 | (this commit) | finalize: EVIDENCE_INDEX + EVIDENCE_MANIFEST + STRATEGY_STATUS + SUMMARY + test update |

## 2. Implementation status

- **Scripts added:**
  - `scripts/run_campaign_012.py` (frozen-parameter assertion before any backtest; mirrors `run_campaign_011.py`)
  - `scripts/build_campaign_012_financing_overlay.py` (mirrors `build_campaign_011_*`)
  - `scripts/build_campaign_012_risk_diagnostics.py` (mirrors `build_campaign_011_*`)
- **No source code change** in `src/forex_bot/strategies/regime_switcher_atr_percentile.py`, `src/forex_bot/backtesting/d1_aggregation.py`, `src/forex_bot/config.py`, RiskEngine, BacktestEngine, loops, or financing — all execution used the scaffold-sprint commit (`07bd9f3`) verbatim.
- **No frozen-parameter change** at any point. The runner's `_assert_frozen()` re-verified all 12 parameters against `CAMPAIGN_012_PRECOMMIT_CHECKLIST.md` §4 before each fold; 0 mismatches across all 56 backtests.

## 3. Walk-forward status

- **Plan:** 8 folds, rolling, frozen, 540/180/180/180 days, 2020-01-01 → 2026-05-20 — inherited verbatim from CAMPAIGN_010 / 011.
- **Execution:** all 56 backtests completed without exception; runner did not abort; no implementation bug fixes required.
- **Aggregate:** 3,726 trades; expectancy −0.0521 R; PF 0.034; return −43.52 % over 4 years; 1 / 7 pairs positive; 0 / 8 folds pass.
- **Verdict:** **REJECT** (5 of 8 aggregate gates fail).

## 4. Null-baseline comparison status (binding)

| metric | CAMPAIGN_011 | CAMPAIGN_012 | difference | in indistinguishability band? | meaningful improvement? |
|---|---:|---:|---:|:---:|:---:|
| aggregate expectancy R | −0.0024 | **−0.0521** | −0.0497 | NO | NO — WORSE |
| aggregate profit factor | 0.91 | **0.034** | −0.876 | NO | NO — WORSE |
| aggregate return % (4 y) | −0.53 % | **−43.52 %** | −42.99 pp | NO | NO — WORSE |
| pairs_positive | 3 / 7 | **1 / 7** | −2 pairs | boundary (worse direction) | NO — WORSE |
| fold pass rate | 0 / 8 | **0 / 8** | 0 | YES (same as null) | NO |

CAMPAIGN_012 is **worse than null** on every binding axis. Classification: **REJECT** (NOT `REJECT_INDISTINGUISHABLE_FROM_NULL`).

## 5. Financing overlay status

- **Source:** `conservative_stress` (`FinancingTreatment.estimated`); **MODELED refused at 4 layers (intact).**
- **3,404 rollover events** over 3,726 trades; missing-rate events: 0.
- `cashflow_home_total = −$65.07`; `cashflow_home_stress_total = −$65.07` (the conservative-stress source is the worst-case projection by construction).
- **No pair flips** under stress (USD_JPY's +$41.71 absorbs −$16.01 financing to +$25.70; all other pairs were already negative pre-financing).
- **Gate `conservative_stress_run_does_not_flip_verdict` PASSES** — verdict was already REJECT pre-financing; financing makes it more REJECT, not less.
- **Live-promotion financing blocker stands** independently of CAMPAIGN_012's verdict.

## 6. Portfolio-risk diagnostics status

- **8 / 8 pipeline sanity checks PASS.**
- Concurrency structurally bounded: max 1 per-instrument position (engine + R2 + config).
- Per-pair ratio max/min: **1.60** (uniform; close to CAMPAIGN_011's 1.65, opposite of CAMPAIGN_010's 12.0).
- Session distribution: diffuse across 4 UTC buckets; no concentration > 50 %.
- Time-stop exit: **79.3 %** (matches CAMPAIGN_011's ~75 %).
- RiskEngine rejection rate: **42.7 %** (SPREAD_TOO_WIDE 2,013; SESSION_BLOCKED 758) — same filters binding as CAMPAIGN_010 / 011.
- Diagnostic shape **most resembles CAMPAIGN_011 (null model)**, not CAMPAIGN_010 (concentrated session strategy).
- Diagnostics are **diagnostic only**; do not flip the verdict.

## 7. Verifier status

- **Did not run.** Verifier is capability-locked to CAMPAIGN_002 / `trend_following`.
- **Not required for REJECT** (item 5 of the six-evidence ladder is a paper-promotion gate).
- The recommended follow-up sprint `infra-free-local-parity-verifier-regime-switcher-001` is **deferred indefinitely** (no paper-promotion candidate to corroborate).

## 8. Safety state at sprint close

| dimension | value |
|---|---|
| `configs/approved_strategies.yaml` | `approved: []` (verified) |
| CAMPAIGN_002 | REJECT (untouched) |
| CAMPAIGN_010 | REJECT (untouched) |
| CAMPAIGN_011 | REJECT (null-model anchor; untouched) |
| **CAMPAIGN_012** | **REJECT (this sprint)** |
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
| historical campaign verdict change | **none** (CAMPAIGN_002 / 010 / 011 untouched) |
| parameter "tweak" or "rescue" | **none** (frozen parameters intact across all 10 phases) |
| `D1AGG` aggregator edit | **none** (read-only use) |
| `src/forex_bot/financing.py` edit | **none** |
| RiskEngine / engine / loops edit | **none** |
| new external dependency | **none** |
| pytest baseline | 818 (preserved) |
| ruff baseline | 3 pre-existing in `research/lean_parity/` (unchanged) |

## 9. Remaining blockers

| blocker | affects | next step |
|---|---|---|
| **MODELED financing refused at 4 layers** | live promotion of any future candidate | `research-financing-modeled-capture-credentialed-001` (separately authorized credentialed pilot) |
| **Independent verifier capability-locked to CAMPAIGN_002** | item 5 of six-evidence ladder for any non-`trend_following` candidate | `infra-free-local-parity-verifier-<FAMILY>-NNN` per family that reaches `RESEARCH_PASS_UNAPPROVED`; **not needed for CAMPAIGN_012's REJECT** |
| **C2 / C4 deferred from discovery-003** | next-candidate menu after CAMPAIGN_012's REJECT | C2 (carry-overlay) needs MODELED financing; C4 (vol-expansion straddle) needs engine paired-entry support; new family discovery may be more productive |
| **3 pre-existing ruff findings** in `research/lean_parity/algorithms/` | code-quality only; no runtime impact | `infra-ruff-lean-parity-archive-cleanup-001` (low-priority cleanup) |

**None of these block any next step** — CAMPAIGN_012 is rejected; what comes next is a discovery sprint to pick a different candidate family.

## 10. Recommended next branch

### Two reasonable options (mutually exclusive)

#### **Option A:** **`research-new-candidate-strategy-discovery-004`** (discovery sprint)

Re-open the discovery loop now that CAMPAIGN_012 has rejected the
regime-switcher hypothesis. Scope:

- Re-score the deferred C2 / C4 candidates against the now-7
  rejected baseline (5 prior + CAMPAIGN_011 null + CAMPAIGN_012 real).
- Consider new families not on the prior C2-C5 shortlist (e.g.
  cross-instrument momentum, calendar effects, options-strangle
  proxy).
- Codify CAMPAIGN_012 as an additional rejected-family reference
  (the regime-switcher cohort is now also off the menu under the
  same parameters).

#### **Option B:** **`infra-engine-paired-entry-support-001`** OR **`research-financing-modeled-capture-credentialed-001`** (infrastructure unblock)

Unblock either C4 (engine paired-entry) or C2 (MODELED financing)
before re-opening discovery, so the next discovery has a richer
candidate menu.

**Recommended:** **Option A** — discovery-004. The infrastructure
sprints are heavier lifts; a fresh discovery with the now-7 rejected
baseline may identify a family that does not depend on the C2 / C4
unblocks.

## 11. Exact files to review first

In review order:

1. **[`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_SUMMARY.md)** — this one-page sprint summary.
2. **[`CAMPAIGN_012_EVIDENCE_SUMMARY.md`](CAMPAIGN_012_EVIDENCE_SUMMARY.md)** — headline numbers; null-baseline interpretation; comparison to prior REJECT campaigns.
3. **[`CAMPAIGN_012_WALK_FORWARD_RESULT.md`](CAMPAIGN_012_WALK_FORWARD_RESULT.md)** — formal verdict with the binding gate vector + null-baseline comparison table + regime-switcher interpretation.
4. **[`CAMPAIGN_012_STATUS.md`](CAMPAIGN_012_STATUS.md)** — REJECTED status; per-strategy detail; CAMPAIGN_002/010/011 relationship.
5. **[`CAMPAIGN_012_WALK_FORWARD_EXECUTION.md`](CAMPAIGN_012_WALK_FORWARD_EXECUTION.md)** — per-fold execution table + per-pair aggregate.
6. **[`CAMPAIGN_012_FINANCING_OVERLAY.md`](CAMPAIGN_012_FINANCING_OVERLAY.md)** — ESTIMATED + conservative stress; no pair flip; MODELED refused.
7. **[`CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md`](CAMPAIGN_012_PORTFOLIO_RISK_DIAGNOSTICS.md)** — 8 / 8 sanity checks; uniform-noise distribution shape.
8. **[`CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md`](CAMPAIGN_012_INDEPENDENT_VERIFIER_STATUS.md)** — verifier did not run; not required for REJECT.
9. **[`CAMPAIGN_012_DATA_PROVENANCE.md`](CAMPAIGN_012_DATA_PROVENANCE.md)** — hashes match CAMPAIGN_010 / 011 verbatim.
10. **[`CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md`](CAMPAIGN_011_NULL_BASELINE_INTERPRETATION.md)** (reference) — the binding null-baseline definition.
11. **`backtests/CAMPAIGN_012_regime_switcher_atr_percentile/walk_forward/results.md`** — auto-generated harness output.
12. **`scripts/run_campaign_012.py`** — the per-fold runner; mirrors `run_campaign_011.py`.

## 12. Cross-links

- [`REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md`](REGIME_SWITCHER_ATR_PERCENTILE_WALK_FORWARD_001_PLAN.md) (Phase 0)
- [`CAMPAIGN_012_PRECOMMIT_CHECKLIST.md`](CAMPAIGN_012_PRECOMMIT_CHECKLIST.md) (binding pre-commit)
- [`REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md`](REGIME_SWITCHER_ATR_PERCENTILE_IMPLEMENTATION_SPEC.md)
- [`REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md`](REGIME_SWITCHER_ATR_PERCENTILE_001_SUMMARY.md) (scaffold-sprint summary)
- [`STRATEGY_APPROVAL_PROCESS.md`](STRATEGY_APPROVAL_PROCESS.md)
- [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md)
- [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md)
- [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json)
- [`WALK_FORWARD_RESEARCH_PROTOCOL.md`](WALK_FORWARD_RESEARCH_PROTOCOL.md)
- [`FINANCING_MODEL_STATUS.md`](FINANCING_MODEL_STATUS.md)
- [`CAMPAIGN_010_WALK_FORWARD_RESULT.md`](CAMPAIGN_010_WALK_FORWARD_RESULT.md) (sibling)
- [`CAMPAIGN_011_WALK_FORWARD_RESULT.md`](CAMPAIGN_011_WALK_FORWARD_RESULT.md) (sibling — the null baseline)
