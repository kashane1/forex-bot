# Post-Dedup Evidence Map 002

**Sprint:** NEW_CANDIDATE_DISCOVERY_DEDUPED_002  
**Branch:** `research-new-candidate-strategy-discovery-deduped-002`  
**Date:** 2026-05-26

This document updates the post-dedup evidence map after CAMPAIGN_016
**REJECT**. It maps dedup-safe evidence, retired families, open hypothesis
space, and constraints for CAMPAIGN_017.

> **No strategy is approved.** `configs/approved_strategies.yaml` remains
> `approved: []`. Paper, demo, and live trading remain blocked.

Supersedes narrative scope of `POST_DEDUP_EVIDENCE_MAP.md` (001) for
campaigns 011, 015, and 016; 001 doc remains archival for the first
post-dedup discovery sprint.

---

## 1. Infrastructure state (dedup-safe)

| component | status | notes |
|---|---|---|
| `CandleRepo.list` dedupe | **DEDUP-SAFE** | `dedupe_candles()` with `keep_last` policy; commit `30b4654` |
| `src/forex_bot/data/candle_dedupe.py` | **DEDUP-SAFE** | Canonical dedupe module |
| Research freeze gate | **PASS** | `scripts/check_research_freeze.py` |
| Archive validation | **PASS** | `scripts/validate_research_archive.py` (16 campaigns) |
| Approved strategies registry | **EMPTY** | `configs/approved_strategies.yaml` → `approved: []` |
| Paper / demo / live loops | **BLOCKED** | Refuse to start without approved strategy |

All **new** campaign implementations must load candles exclusively through
`CandleRepo.list` (or equivalent deduped export path).

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

Future campaigns must compare against this deduped null centre.

---

## 3. Dedup-safe campaign evidence

| campaign | strategy | verdict | integrity | key metrics |
|---|---|---|---|---|
| **CAMPAIGN_011** | `random_entry_anchor` (null) | REJECT | **DEDUP-SAFE** | exp_r −0.0029, 1,180 trades |
| **CAMPAIGN_015** | `failed_breakout_reversal` | REJECT | **DEDUP-SAFE** | base exp_r −0.0101, 375 trades, 2/8 fold pass, WITHIN_NULL |
| **CAMPAIGN_016** | `weekly_cross_sectional_momentum_low_turnover` | REJECT | **DEDUP-SAFE** | base exp_r −0.0633, 137 trades, 3/8 fold pass, WITHIN_NULL |

### CAMPAIGN_015 deduped detail

| lane | exp_r | trades | notes |
|---|---:|---:|---|
| base | −0.0101 | 375 | anti-overfit: **WITHIN_NULL** |
| 2× cost | −0.0283 | — | worsens under stress |
| Backtrader | TOLERABLE_DRIFT | BT 288 vs bespoke 375 | diagnostic only |

Do **not** revive or retune.

### CAMPAIGN_016 deduped detail

| lane | exp_r | trades | notes |
|---|---:|---:|---|
| base | **−0.0633** | **137** | anti-overfit: **WITHIN_NULL** |
| 2× cost | **−0.0719** | 137 | worsens under stress |
| gap vs deduped null | **−0.0604 R** | — | below null centre |
| fold pass | **3 / 8** | — | failed `fold_pass_rate_ge_5_of_8` |
| pairs positive | **4 / 7** | — | passed gate but insufficient edge |
| Backtrader | **BLOCKED** | boundary parity only | non-decision-blocking |
| verdict | **REJECT** | — | do not retune |

See `docs/research/CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md`,
`docs/research/CAMPAIGN_016_NULL_AND_ANTI_OVERFIT.md`.

---

## 4. Contaminated / archival evidence

### LIKELY_CONTAMINATED (pre-fix SQLite, verdict unchanged)

| campaign | strategy family | verdict | integrity |
|---|---|---|---|
| CAMPAIGN_002 | trend_following baseline | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_003 | trend_following + ADX gate | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_004 | volatility_breakout (H4 ATR compression) | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_005 | benchmarks | descriptive | LIKELY_CONTAMINATED |
| CAMPAIGN_007 | pullback_continuation | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_008 | range mean_reversion | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_009 | mean_reversion midline exit | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_010 | session_breakout | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_012 | regime_switcher_atr_percentile | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_013 | cross_pair_currency_strength_rotation | REJECT | LIKELY_CONTAMINATED |
| CAMPAIGN_014 | calendar_event_window_anomaly | REJECT | LIKELY_CONTAMINATED |

### Post-dedup null reference refresh (docs-only)

CAMPAIGN_012–014 null-relative conclusions refreshed against deduped null;
all far below null. Conclusions unchanged REJECT.

### Blocked (infrastructure)

| campaign | issue |
|---|---|
| CAMPAIGN_006 | D1 candles untestable by current engine |

---

## 5. Retired strategy families

The following families are **retired** for new implementation. Future
candidates must be structurally distinct — not retunes, parameter sweeps, or
variant filters on these families.

| family | campaigns | retirement reason |
|---|---|---|
| **Trend-following (EMA/Donchian)** | 002, 003, 006 | Negative expectancy; ADX gate did not help |
| **ADX trend variants** | 003 | Subset of trend-following; rejected |
| **Volatility breakout (H4 ATR compression)** | 004 | Negative across universe; H4 churn; cost-sensitive |
| **Pullback continuation** | 007 | Failed validation gates |
| **Mean-reversion (c008/c009)** | 008, 009 | Rejected |
| **Session breakout** | 010 | Rejected on walk-forward |
| **ATR regime switcher** | 012 | Rejected; turnover amplification |
| **Currency-strength rotation** | 013 | Rejected; cross-pair ranking did not beat null |
| **Calendar-event anomaly** | 014 | Rejected; event-window fragility |
| **Failed-breakout reversal** | 015 | **Deduped REJECT**; WITHIN_NULL; do not revive |
| **Weekly cross-sectional momentum** | 016 | **Deduped REJECT**; WITHIN_NULL; gap −0.0604 R; do not retune |
| **Carry-aware approaches** | — | **Blocked** unless financing modeling is sufficient |

### Pattern lessons (from failed campaigns, not positive evidence)

- H4 event/reversal/breakout systems showed high turnover and cost sensitivity.
- Cross-sectional ranking at weekly cadence (016) still failed gates and landed WITHIN_NULL.
- Turnover amplification (012, 013) worsened already-poor edges.
- Session and calendar filters introduced sparse-trade and concentration risks.
- Fold instability (016: folds 2–4 positive, 5–7 deeply negative) is a recurring rejection mode.
- Pre-fix contaminated metrics must not anchor expectations.

---

## 6. Why cross-sectional momentum is now lower priority

CAMPAIGN_016 was the first dedup-safe test of weekly cross-sectional
relative momentum. Results:

1. **Negative aggregate edge:** exp_r −0.0633 vs null −0.0029 — materially worse than null, not a marginal miss.
2. **WITHIN_NULL classifier** but failed primary gates (exp_r, PF, fold pass rate).
3. **Low sample:** 137 trades vs precommitted minimum 300 — weekly cadence did not produce enough trades for stable inference.
4. **Fold instability:** severe sign flips across folds; LOO and median-fold gates failed.
5. **No Backtrader parity** — secondary lane BLOCKED (non-decision-blocking given REJECT).

The cross-sectional *relative* hypothesis at weekly frequency is **retired**
unless a structurally different mechanism is precommitted (not parameter
tuning of 016 lookbacks, blend weights, or rank selection).

Remaining cross-sectional ideas (013-style daily rotation, 016-style weekly
momentum) are deprioritized. CAMPAIGN_017 should **not** rank pairs or trade
long-top / short-bottom.

---

## 7. Remaining open hypothesis space

No strategy family is **approved**. Open space is defined negatively:

1. Uses deduped `CandleRepo.list` data path exclusively.
2. Compares against deduped CAMPAIGN_011 null baseline.
3. Does not retune or extend rejected families (§5).
4. Has falsifiable pre-committed gates before implementation.
5. Is Backtrader-verifiable or adapter-feasible.
6. Does not require carry/financing unless financing overlay is modeled.
7. Targets lower turnover than H4 event systems.
8. **Does not use cross-sectional pair ranking** (016 lesson).
9. **Does not fade failed breakouts** (015 lesson).
10. **Does not use H4-bar compression breakout churn** (004 lesson) — weekly/multi-day cadence preferred.

Promising structural directions (not yet tested on deduped data):

- **Weekly volatility contraction → expansion breakout** (single-pair, not cross-sectional).
- **Multi-day range expansion after compression** (hold measured in days, not H4 bars).
- **Portfolio vol regime filter** gating a simple signal (not 012-style per-pair switcher).
- **Daily close reversal after extreme range** (distinct from session breakout 010 and failed-break 015).
- **Pair-specific lab** (hypothesis generation only, not a campaign).

---

## 8. Constraints for CAMPAIGN_017

### Data

- Universe: seven major pairs (EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD,
  USD_CHF, NZD_USD).
- Timeframe: H4 only; synthetic weekly/multi-day aggregation from deduped H4.
- No native D1/W1 data dependency (CAMPAIGN_006 blocker avoided).
- All loads through deduped `CandleRepo.list`.

### Null comparison

- Centre: aggregate exp_r **−0.0029154071495408797** (deduped CAMPAIGN_011).
- Band: ±0.005 R / ±0.10 PF / ±2 pp / ±1 pair.
- Anti-overfit: LOO fold stability, pair concentration, cost dominance, 2× cost stress.

### Gates (minimum)

- Trade count gate appropriate to low-turnover cadence (precommit: e.g. 120–500).
- Fold pass rate adapted to turnover.
- No strategy approval even if screen passes.
- Backtrader fold-window plan before full verdict.

### Forbidden for CAMPAIGN_017

- Retuning CAMPAIGN_016 (lookbacks, blend, rank rules, stops).
- Reviving CAMPAIGN_015 or any retired family.
- Cross-sectional momentum or strength rotation ranking.
- H4 ATR compression breakout as in CAMPAIGN_004 (same bar trigger cadence).
- Adding to `approved_strategies.yaml`.
- Paper / demo / live enablement.
- Broker / OANDA API calls.
- Using contaminated 002–014 metrics as positive evidence.

---

## 9. Evidence index pointers

| topic | doc |
|---|---|
| Dedupe fix impact | `CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md` |
| Null supersession | `CAMPAIGN_011_NULL_BASELINE_SUPERSESSION.md` |
| CAMPAIGN_015 deduped | `CAMPAIGN_015_DEDUPED_RERUN_INTERPRETATION.md` |
| CAMPAIGN_016 result | `CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_RESULT.md` |
| CAMPAIGN_016 interpretation | `CAMPAIGN_016_WEEKLY_CROSS_SECTIONAL_MOMENTUM_INTERPRETATION.md` |
| Prior evidence map (001) | `POST_DEDUP_EVIDENCE_MAP.md` |
| Rerun backlog | `POST_DEDUP_RERUN_BACKLOG.md` |
| Strategy status | `STRATEGY_STATUS.md` |

---

## 10. Summary

| category | count | action |
|---|---:|---|
| Dedup-safe evidence | 3 campaigns (011 null, 015 reject, 016 reject) | Use for null comparison and lessons |
| LIKELY_CONTAMINATED | 002–014 (except deduped 011/015) | Verdict only; no positive metrics |
| Retired families | 12+ families | Do not retune or revive |
| Approved strategies | 0 | Remains empty |
| Next step | CAMPAIGN_017 | See `DEDUPED_CANDIDATE_UNIVERSE_002.md` |
