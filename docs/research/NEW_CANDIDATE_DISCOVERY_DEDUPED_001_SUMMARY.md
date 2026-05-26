# New Candidate Discovery (Deduped) — Sprint Summary

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_001  
**Branch:** `research-new-candidate-strategy-discovery-deduped-001`  
**Base branch:** `research-post-dedup-null-reference-refresh-001`  
**Date:** 2026-05-26

---

## 1. Branch

`research-new-candidate-strategy-discovery-deduped-001`

Created from `research-post-dedup-null-reference-refresh-001` at `8e43749`.

---

## 2. Commits by phase

| phase | commit | message |
|---:|---|---|
| 0 | `7cce870` | docs(research): open new candidate discovery sprint plan (deduped 001) |
| 1 | `4532bf5` | docs(research): post-dedup evidence map for candidate discovery |
| 2 | `92facdc` | docs(research): deduped candidate universe and ranking |
| 3 | `6af5bcb` | docs(research): select weekly cross-sectional momentum for CAMPAIGN_016 |
| 4 | `d24070d` | docs(research): CAMPAIGN_016 precommit draft for weekly momentum |
| 5 | *(this commit)* | docs(research): close out new candidate discovery sprint (deduped 001) |

---

## 3. Evidence map summary

### Dedup-safe

| artifact | status |
|---|---|
| `CandleRepo.list` + `dedupe_candles()` | **DEDUP-SAFE** |
| CAMPAIGN_011 deduped null baseline | **DEDUP-SAFE** — exp_r −0.0029, 1,180 trades |
| CAMPAIGN_015 deduped rerun | **DEDUP-SAFE REJECT** — exp_r −0.0101, WITHIN_NULL |

### Contaminated / archival

- CAMPAIGN_002–010, 012–014 walk-forward metrics: **LIKELY_CONTAMINATED**
- Verdicts unchanged REJECT; do not use as positive evidence
- CAMPAIGN_012–014 null gaps refreshed (docs-only): −0.049 / −0.054 / −0.145 R vs null

### Retired families

Trend-following, ADX, volatility breakout, pullback, mean-reversion (c008/c009),
session breakout, ATR regime switcher, currency-strength rotation, calendar-event
anomaly, failed-breakout reversal, carry-aware (financing-blocked).

See [`POST_DEDUP_EVIDENCE_MAP.md`](POST_DEDUP_EVIDENCE_MAP.md).

---

## 4. Candidate universe considered

Six candidates evaluated in [`DEDUPED_CANDIDATE_UNIVERSE.md`](DEDUPED_CANDIDATE_UNIVERSE.md):

1. `weekly_cross_sectional_momentum_low_turnover`
2. `weekly_volatility_contraction_breakout`
3. `multi_day_carry_trend_hybrid` (financing-blocked)
4. `portfolio_volatility_regime_filter_then_signal`
5. `session_range_reversal_cost_gated`
6. `pair_specific_research_lab` (lab only)

---

## 5. Ranking table

| rank | candidate | score | notes |
|---:|---|:---:|---|
| **1** | weekly_cross_sectional_momentum_low_turnover | **A** | Selected |
| 2 | weekly_volatility_contraction_breakout | B+ | 004-family adjacency |
| 3 | portfolio_volatility_regime_filter_then_signal | B | 012 regime baggage |
| 4 | multi_day_carry_trend_hybrid | C | **Financing blocked** |
| 5 | session_range_reversal_cost_gated | D | 010/015 adjacency |
| — | pair_specific_research_lab | Lab | Not a campaign |

---

## 6. Selected candidate

**`weekly_cross_sectional_momentum_low_turnover`**

---

## 7. Proposed campaign id

**CAMPAIGN_016** — strategy version `weekly_cross_sectional_momentum_low_turnover 0.1.0-c016`

---

## 8. Why selected

- Structurally distinct from all rejected CAMPAIGN_002–015 families
- Weekly cross-sectional rank (not single-pair trend, breakout, reversal, or event)
- Low turnover addresses cost-sensitivity lesson from failed H4 systems
- No financing blocker (unlike carry hybrid)
- Compatible with existing deduped H4 SQLite
- Falsifiable with tiny precommitted parameter set
- No contaminated positive evidence anchoring expectations
- Backtrader verification feasible (015 deduped TOLERABLE_DRIFT precedent)

See [`NEXT_CANDIDATE_SELECTION_DEDUPED_001.md`](NEXT_CANDIDATE_SELECTION_DEDUPED_001.md).

---

## 9. Key risks

| risk | severity |
|---|---|
| Weekly FX momentum WITHIN_NULL (like deduped 015) | high |
| Thematic overlap with rejected CAMPAIGN_013 rotation | medium |
| Low per-fold trade count under USD cap + cost filter | medium |
| Weekly boundary parity between bespoke and Backtrader | medium |
| Single-pair concentration (GBP_USD / USD_JPY) | medium |
| 2× cost stress collapse | medium |

---

## 10. Infra blockers

| blocker | status |
|---|---|
| Deduped data path | **Ready** |
| Weekly bar aggregator | **Not built** — implementation sprint work |
| Backtrader weekly signal adapter | **Not built** — feasibility spike required |
| Financing model for carry | **N/A** — not needed for this candidate |
| D1 engine (CAMPAIGN_006 blocker) | **Avoided** — H4-only |

No blocker prevents opening the implementation sprint; weekly aggregation and
Backtrader adapter are the first engineering tasks.

---

## 11. Strategy code implemented?

**No.** Docs-only sprint. No strategy module, config, or walk-forward run.

---

## 12. Any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`.

---

## 13. Paper / demo / live blocked?

**Yes.** All loops refuse to start without approved strategy.

---

## 14. Phase 0 / 5 validation

| command | result |
|---|---|
| `pytest tests/ -q` | **1509 passed** |
| `ruff check src tests scripts research` | **PASS** |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |

### Staging hygiene (verified)

| check | status |
|---|---|
| `.env` staged | **NO** |
| credentials staged | **NO** |
| SQLite DB staged | **NO** |
| bulky backtest artifacts staged | **NO** |
| `approved_strategies.yaml` unchanged | **YES — `approved: []`** |

Untracked local artifacts (CAMPAIGN_011/015 deduped backtests, diagnostics)
remain uncommitted per sprint rules.

---

## 15. Files to review first

1. [`NEW_CANDIDATE_DISCOVERY_DEDUPED_001_PLAN.md`](NEW_CANDIDATE_DISCOVERY_DEDUPED_001_PLAN.md) — sprint plan and truth audit
2. [`POST_DEDUP_EVIDENCE_MAP.md`](POST_DEDUP_EVIDENCE_MAP.md) — dedup-safe vs contaminated evidence
3. [`DEDUPED_CANDIDATE_UNIVERSE.md`](DEDUPED_CANDIDATE_UNIVERSE.md) — full candidate analysis and ranking
4. [`NEXT_CANDIDATE_SELECTION_DEDUPED_001.md`](NEXT_CANDIDATE_SELECTION_DEDUPED_001.md) — formal selection
5. [`CAMPAIGN_016_PRECOMMIT_DRAFT.md`](CAMPAIGN_016_PRECOMMIT_DRAFT.md) — implementation sprint starting point
6. [`research/null_baselines/campaign_011_deduped_null_baseline.json`](../../research/null_baselines/campaign_011_deduped_null_baseline.json) — null centre

---

## 16. Recommended next step

Open **CAMPAIGN_016 implementation sprint**: harden precommit draft, implement
weekly cross-sectional momentum on deduped data, run Backtrader feasibility
spike, then full walk-forward with null comparison. Default expected outcome:
**REJECT** — do not retune on failure.
