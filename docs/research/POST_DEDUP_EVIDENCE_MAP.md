# Post-Dedup Evidence Map

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_001  
**Branch:** `research-new-candidate-strategy-discovery-deduped-001`  
**Date:** 2026-05-26

This document maps which research evidence is safe to use after the
duplicate-candle cleanup, which evidence is contaminated or archival only,
and what constraints future strategy candidates must satisfy.

> **No strategy is approved.** `configs/approved_strategies.yaml` remains
> `approved: []`. Paper, demo, and live trading remain blocked.

---

## 1. Infrastructure state (dedup-safe)

| component | status | notes |
|---|---|---|
| `CandleRepo.list` dedupe | **DEDUP-SAFE** | `dedupe_candles()` with `keep_last` policy; commit `30b4654` |
| `src/forex_bot/data/candle_dedupe.py` | **DEDUP-SAFE** | Canonical dedupe module |
| Research freeze gate | **PASS** | `scripts/check_research_freeze.py` |
| Archive validation | **PASS** | `scripts/validate_research_archive.py` |
| Approved strategies registry | **EMPTY** | `configs/approved_strategies.yaml` → `approved: []` |
| Paper / demo / live loops | **BLOCKED** | Refuse to start without approved strategy |

All **new** campaign implementations must load candles exclusively through
`CandleRepo.list` (or equivalent deduped export path). Bespoke SQLite reads
that bypass dedupe are forbidden.

---

## 2. Canonical null baseline (dedup-safe)

| field | value |
|---|---|
| path | `research/null_baselines/campaign_011_deduped_null_baseline.json` |
| strategy | `random_entry_anchor 0.1.0-c011` |
| aggregate trades | 1,180 |
| aggregate expectancy R | **−0.0029154071495408797** |
| per-fold expectancy mean / std | **−0.0027 / 0.0479** |
| aggregate return % | −0.68 |
| profit factor | 0.89 |
| verdict | REJECT (null model by design) |
| input dir | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/` |

**Superseded (archival only):** pre-fix null centre −0.0024 R, 1,177 trades.
See `docs/research/CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md`.

Future campaigns must compare against the deduped null centre and report
gap on aggregate expectancy R, fold stability, and anti-overfit gates.

---

## 3. Dedup-safe campaign evidence

| campaign | strategy | verdict | integrity | key metrics |
|---|---|---|---|---|
| **CAMPAIGN_011** | `random_entry_anchor` (null) | REJECT | **DEDUP-SAFE** | exp_r −0.0029, 1,180 trades |
| **CAMPAIGN_015** | `failed_breakout_reversal` | REJECT | **DEDUP-SAFE** (deduped rerun) | base exp_r −0.0101, 375 trades, 2/8 fold pass, WITHIN_NULL |

### CAMPAIGN_015 deduped detail

| lane | exp_r | trades | notes |
|---|---:|---:|---|
| base | −0.0101 | 375 | anti-overfit: **WITHIN_NULL** |
| 2× cost | −0.0283 | — | worsens under stress |
| Backtrader | TOLERABLE_DRIFT | BT 288 vs bespoke 375 | diagnostic only |

Prior contaminated `ROBUST_ABOVE_NULL` label is **SUPERSEDED BY DEDUP RERUN**.
See `docs/research/CAMPAIGN_015_DEDUPED_NULL_AND_ANTI_OVERFIT.md`.

---

## 4. Contaminated / archival evidence

### LIKELY_CONTAMINATED (pre-fix SQLite, verdict unchanged)

These campaigns ran on duplicate UTC H4 bars before `CandleRepo.list` dedupe.
Verdicts remain **REJECT**; headline metrics must **not** be used as positive
evidence or for null-band comparisons without deduped rerun.

| campaign | strategy family | verdict | integrity | notes |
|---|---|---|---|---|
| CAMPAIGN_002 | trend_following baseline | REJECT | LIKELY_CONTAMINATED | H4/H1 real OANDA |
| CAMPAIGN_003 | trend_following + ADX gate | REJECT | LIKELY_CONTAMINATED | ADX variant |
| CAMPAIGN_004 | volatility_breakout | REJECT | LIKELY_CONTAMINATED | ATR compression |
| CAMPAIGN_005 | benchmarks (random/always) | descriptive | LIKELY_CONTAMINATED | pre-dedup random mean |
| CAMPAIGN_007 | pullback_continuation | REJECT | LIKELY_CONTAMINATED | test lockbox never opened |
| CAMPAIGN_008 | range mean_reversion | REJECT | LIKELY_CONTAMINATED | validation-only metrics |
| CAMPAIGN_009 | mean_reversion midline exit | REJECT | LIKELY_CONTAMINATED | validation-only metrics |
| CAMPAIGN_010 | session_breakout | REJECT | LIKELY_CONTAMINATED | Asian/London session |
| CAMPAIGN_012 | regime_switcher_atr_percentile | REJECT | LIKELY_CONTAMINATED | null gap −0.0492 R (refreshed) |
| CAMPAIGN_013 | cross_pair_currency_strength_rotation | REJECT | LIKELY_CONTAMINATED | null gap −0.0535 R (refreshed) |
| CAMPAIGN_014 | calendar_event_window_anomaly | REJECT | LIKELY_CONTAMINATED | null gap −0.1448 R (refreshed) |

### Post-dedup null reference refresh (docs-only, not rerun)

CAMPAIGN_012–014 null-relative conclusions were refreshed against the deduped
null centre. Conclusions **unchanged** — all far below null. Full walk-forward
reruns remain optional (Priority 2 in `POST_DEDUP_RERUN_BACKLOG.md`).

### Blocked (infrastructure, not verdict)

| campaign | issue |
|---|---|
| CAMPAIGN_006 | D1 candles untestable by current engine — **blocked**, not rejected |

### Archived / no rerun unless specific reason

CAMPAIGN_002–010 are archived. Do not rerun unless a specific integrity or
methodology question requires it.

---

## 5. Retired strategy families

The following families are **retired** for new implementation. Future
candidates must be structurally distinct — not retunes, parameter sweeps, or
variant filters on these families.

| family | campaigns | retirement reason |
|---|---|---|
| **Trend-following (EMA/Donchian)** | 002, 003, 006 | Negative expectancy across universe; ADX gate did not help |
| **ADX trend variants** | 003 | Subset of trend-following; rejected |
| **Volatility breakout (ATR compression)** | 004 | Negative across all pairs; cost-sensitive |
| **Pullback continuation** | 007 | Failed validation gates; never reached test |
| **Mean-reversion (c008/c009)** | 008, 009 | Rejected; validation metrics contaminated — do not revive unless structurally new |
| **Session breakout** | 010 | Rejected on walk-forward; session-filter fragility |
| **ATR regime switcher** | 012 | Rejected; turnover amplification; null gap −0.05 R |
| **Currency-strength rotation** | 013 | Rejected; cross-pair ranking did not beat null |
| **Calendar-event anomaly** | 014 | Rejected; event-window fragility; NFP dominated |
| **Failed-breakout reversal** | 015 | **Deduped REJECT**; WITHIN_NULL; do not revive or retune |
| **Carry-aware approaches** | — | **Blocked** unless financing modeling is sufficient for the hypothesis |

### Pattern lessons (from failed campaigns, not positive evidence)

- H4 event/reversal/breakout systems showed high turnover and cost sensitivity.
- Turnover amplification (012, 013) worsened already-poor edges.
- Session and calendar filters introduced sparse-trade and concentration risks.
- Single-pair or single-fold dominance appeared in multiple rejections.
- Pre-fix contaminated metrics inflated some CAMPAIGN_015 signals — deduped rerun
  collapsed edge to WITHIN_NULL.

---

## 6. Open families (candidate space)

No strategy family is **approved**. The open space for new candidates is
defined negatively: anything structurally distinct from §5 that:

1. Uses deduped `CandleRepo.list` data path exclusively.
2. Compares against deduped CAMPAIGN_011 null baseline.
3. Does not retune or extend rejected families.
4. Has falsifiable pre-committed gates before implementation.
5. Is Backtrader-verifiable or at least adapter-feasible.
6. Does not require carry/financing unless financing overlay is modeled.
7. Targets lower turnover than H4 event systems where possible.

Promising structural directions (not yet tested):

- **Cross-sectional / relative** signals (rank pairs, trade extremes).
- **Weekly / multi-day** cadence (lower turnover than H4 bar triggers).
- **Volatility regime gating** applied *before* a distinct signal (not 012-style switcher).
- **Portfolio-level filters** (volatility regime, exposure caps) wrapping a simple signal.

---

## 7. Constraints for future candidates

### Data

- Universe: seven major pairs (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD,
  USD_CHF, NZD_USD) unless precommit expands with justification.
- Timeframe: H4 and/or D1 aggregates from existing OANDA practice SQLite.
- All loads through deduped `CandleRepo.list`.

### Null comparison

- Centre: aggregate exp_r **−0.0029154071495408797** (deduped CAMPAIGN_011).
- Band: ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair (binding protocol unchanged).
- Anti-overfit: LOO fold stability, pair concentration, cost dominance, 2× cost stress.

### Gates (minimum)

- Minimum trade count appropriate to signal cadence (precommit honestly).
- Fold pass rate adapted to turnover (weekly systems need lower per-fold counts
  but sufficient aggregate sample).
- No strategy approval even if screen passes.
- Backtrader adapter feasibility check before full walk-forward.

### Forbidden

- Adding to `approved_strategies.yaml`.
- Paper / demo / live enablement.
- Broker / OANDA API calls during research sprint.
- Parameter optimization beyond tiny precommitted set.
- Using contaminated metrics as positive evidence.
- Reviving CAMPAIGN_015 or any retired family.

---

## 8. Evidence index pointers

| topic | doc |
|---|---|
| Dedupe fix impact | `CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md` |
| Null supersession | `CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md` |
| CAMPAIGN_012–014 null refresh | `CAMPAIGN_012/013/014_POST_DEDUP_NULL_REFERENCE.md` |
| CAMPAIGN_015 deduped interpretation | `CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md` |
| Rerun backlog | `POST_DEDUP_RERUN_BACKLOG.md` |
| Strategy status | `STRATEGY_STATUS.md` |
| Failed campaign lessons | `FAILED_CAMPAIGN_META_ANALYSIS_001.md` |

---

## 9. Summary

| category | count | action |
|---|---:|---|
| Dedup-safe evidence | 2 campaigns (011 null, 015 deduped reject) | Use for null comparison and lessons |
| LIKELY_CONTAMINATED | 002–014 (except 011 deduped, 015 deduped) | Verdict only; no positive metrics |
| Retired families | 11+ families | Do not retune or revive |
| Approved strategies | 0 | Remains empty |
| Next step | 1 fresh candidate | See `DEDUPED_CANDIDATE_UNIVERSE.md` |
