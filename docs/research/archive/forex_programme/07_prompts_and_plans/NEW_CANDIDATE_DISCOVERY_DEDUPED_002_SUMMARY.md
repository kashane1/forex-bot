# New Candidate Discovery (Deduped) — Sprint Summary 002

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_002  
**Branch:** `research-new-candidate-strategy-discovery-deduped-002`  
**Base branch:** `research-weekly-cross-sectional-momentum-001`  
**Date:** 2026-05-26

---

## 1. Branch

`research-new-candidate-strategy-discovery-deduped-002`

Created from `research-weekly-cross-sectional-momentum-001` at `96a531e`
(CAMPAIGN_016 sprint close-out).

---

## 2. Commits by phase

| phase | commit | message |
|---:|---|---|
| 0 | `cfaf74e` | docs(research): open new candidate discovery sprint plan (deduped 002) |
| 1 | `bc9ccc5` | docs(research): post-dedup evidence map 002 after CAMPAIGN_016 REJECT |
| 2 | `bbac962` | docs(research): deduped candidate universe 002 and ranking post-C016 |
| 3 | `21895f7` | docs(research): select weekly volatility contraction breakout for CAMPAIGN_017 |
| 4 | `3f9d441` | docs(research): CAMPAIGN_017 precommit draft for weekly vol contraction breakout |
| 5 | *(this commit)* | docs(research): close out new candidate discovery sprint (deduped 002) |

---

## 3. CAMPAIGN_016 conclusion

| field | value |
|---|---|
| strategy | `weekly_cross_sectional_momentum_low_turnover 0.1.0-c016` |
| verdict | **REJECT** |
| base exp_r | **−0.0633** |
| 2× exp_r | **−0.0719** |
| trades | **137** |
| fold pass | **3 / 8** |
| pairs positive | **4 / 7** |
| anti-overfit | **WITHIN_NULL** |
| gap vs deduped null | **−0.0604 R** |
| Backtrader | **BLOCKED** (non-decision-blocking; boundary parity only) |

Cross-sectional weekly momentum is **retired**. Do not retune CAMPAIGN_016.

---

## 4. Candidate universe considered

Six candidates in [`DEDUPED_CANDIDATE_UNIVERSE_002.md`](DEDUPED_CANDIDATE_UNIVERSE_002.md):

1. `weekly_volatility_contraction_breakout` — **selected**
2. `multi_day_range_expansion_after_compression`
3. `portfolio_volatility_regime_filter_then_simple_signal`
4. `daily_close_reversal_after_extreme_range`
5. `pair_specific_research_lab` (lab only)
6. `carry_trend_hybrid` (financing-blocked)

---

## 5. Selected CAMPAIGN_017 candidate

| field | value |
|---|---|
| campaign | **CAMPAIGN_017** |
| strategy | `weekly_volatility_contraction_breakout 0.1.0-c017` |
| approval | **NOT APPROVED** |

---

## 6. Why selected

1. **Post-016 structural pivot** — avoids cross-sectional ranking that failed at −0.0633 R.
2. **Weekly cadence, single-pair** — lower turnover than H4 event systems; independent per-pair compression cycles.
3. **Distance from CAMPAIGN_004** — 12-week range compression + confirmed breakout, not H4 ATR P40 + 20-bar Donchian churn.
4. **No financing blocker** — pure spot breakout hypothesis.
5. **Dedup-safe data path** — H4 only, synthetic weekly aggregation.
6. **Backtrader feasible** — single-pair state machine simpler than CAMPAIGN_016 portfolio rebalance.
7. **Ranked A** in universe scoring — no higher-scoring candidate without blockers.

---

## 7. Why it is not a retune

| prior | why C017 differs |
|---|---|
| CAMPAIGN_004 | Weekly TR percentile (12 weeks) vs H4 ATR P40 (60 bars); event cadence once per compression cycle vs every H4 bar |
| CAMPAIGN_015 | With-breakout follow-through vs failed-break fade |
| CAMPAIGN_016 | Single-pair compression state vs cross-sectional rank long-top/short-bottom |
| CAMPAIGN_013 | No cross-pair ranking |

Frozen choices locked in precommit: opposite-range stop (not 2.5× ATR), 42 H4 bar max hold (not 10 bars), 0.25× ATR breakout buffer.

---

## 8. Key risks

| risk | severity |
|---|---|
| Thematic adjacency to rejected 004 breakout family | medium |
| WITHIN_NULL outcome (like 015, 016) | high |
| Sparse compression weeks → trade count below 120 gate | medium |
| Breakout whipsaw at range expansion | medium |
| Fold instability across vol regimes | medium |
| 2× cost stress collapses marginal breakouts | medium-high |
| Weekly boundary parity across bespoke / Backtrader | medium |

---

## 9. Infra blockers

| blocker | status |
|---|---|
| `CandleRepo.list` dedupe | **none** — active |
| Native D1/W1 data | **avoided** — synthetic weekly from H4 |
| Financing model | **none required** |
| Weekly aggregation module | **to build** in implementation sprint |
| Backtrader adapter | **to build** — feasibility spike required in Phase 0 |

No OANDA/broker API calls in this sprint.

---

## 10. Strategy code implemented?

**No.** This was a docs-only discovery sprint. No strategy modules, configs,
runners, or tests were added.

---

## 11. Any strategy approved?

**No.** [`configs/approved_strategies.yaml`](../../configs/approved_strategies.yaml)
remains `approved: []`.

---

## 12. Paper / demo / live blocked?

**Yes.** Verified by `check_research_freeze.py` loops_refuse gate:

- `paper-loop` refuses (no approved strategy)
- `demo-loop` refuses (no approved strategy)
- No `live-loop` command exists

---

## 13. Phase 5 validation

| command | result |
|---|---|
| `pytest tests/ -q` | **1532 passed** |
| `ruff check src tests scripts research` | **1 pre-existing I001** (import sort in CAMPAIGN_016 BT test; not introduced by this sprint) |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** |

### Staging hygiene

| check | status |
|---|---|
| `.env` staged | **no** |
| credentials staged | **no** |
| SQLite DB staged | **no** |
| bulky backtest artifacts staged | **no** (local untracked only) |
| `approved_strategies.yaml` modified | **no** — remains `approved: []` |

---

## 14. Files to review first

1. [`NEW_CANDIDATE_DISCOVERY_DEDUPED_002_PLAN.md`](NEW_CANDIDATE_DISCOVERY_DEDUPED_002_PLAN.md) — Phase 0 truth audit
2. [`POST_DEDUP_EVIDENCE_MAP_002.md`](POST_DEDUP_EVIDENCE_MAP_002.md) — updated evidence map
3. [`DEDUPED_CANDIDATE_UNIVERSE_002.md`](DEDUPED_CANDIDATE_UNIVERSE_002.md) — six candidates ranked
4. [`NEXT_CANDIDATE_SELECTION_DEDUPED_002.md`](NEXT_CANDIDATE_SELECTION_DEDUPED_002.md) — formal CAMPAIGN_017 selection
5. [`CAMPAIGN_017_PRECOMMIT_DRAFT.md`](CAMPAIGN_017_PRECOMMIT_DRAFT.md) — frozen hypothesis for implementation sprint
6. [`CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md`](CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md) — prior campaign REJECT evidence

---

## 15. Recommended next step

Implementation sprint on `research-weekly-volatility-contraction-breakout-001` (or equivalent):

1. Harden `CAMPAIGN_017_PRECOMMIT_DRAFT.md` → binding precommit
2. Implement weekly volatility features + strategy module
3. Run walk-forward on deduped H4 with base / 2× cost lanes
4. Null / anti-overfit diagnostics vs deduped CAMPAIGN_011
5. Backtrader fold-window parity spot check

**No approval path in that sprint unless explicit human policy change.**
