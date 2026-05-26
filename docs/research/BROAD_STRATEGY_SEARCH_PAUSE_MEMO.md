# Broad Strategy Search Pause Memo

**Date:** 2026-05-26  
**Branch:** `research-broad-strategy-pause-and-roadmap-001`  
**Authority:** Post-dedup failure meta-analysis (`research-post-dedup-failure-meta-analysis-001`)

> **No strategy approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper / demo / live remain blocked. CAMPAIGN_018 will **not** be created.

---

## 1. Why broad strategy search is paused

Three consecutive **dedup-safe** broad pattern families on the standard seven-pair OANDA practice H4 universe — failed breakout reversal (CAMPAIGN_015), weekly cross-sectional momentum (CAMPAIGN_016), and weekly volatility contraction breakout (CAMPAIGN_017) — all **REJECT** with anti-overfit classification **WITHIN_NULL** versus the canonical deduped null baseline (CAMPAIGN_011).

Post-dedup meta-analysis found:

- **No campaign beats null on aggregate expectancy** (all three sit below −0.0029 R).
- **All worsen under 2× cost stress** — cost drag is real but not the primary story; directional edge is absent at portfolio level.
- **No reliable archetype** across pair, fold, side, or exit dimensions (classification: `NO_RELIABLE_ARCHETYPE`).
- Exploratory cells (USD_JPY micro-positive, fold winners, short-side less-bad) are **economically null** or **non-replicating across families**.

Continuing broad pattern churn without a new falsifiable hypothesis repeats a known failure mode and increases overfitting risk. The project therefore **pauses** broad seven-pair pattern strategy campaigns until explicit re-entry gates are met.

---

## 2. Summary table — CAMPAIGN_015–017 vs deduped null

Canonical null: **CAMPAIGN_011** deduped `random_entry_anchor` — aggregate exp_r **−0.002915**, **1,180** trades, 0/8 fold pass.  
Source: `research/null_baselines/campaign_011_deduped_null_baseline.json`.

| campaign | strategy family | verdict | base exp_r | gap vs null | trades | fold pass | PF (base) | anti-overfit | 2× cost |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| CAMPAIGN_011 | random_entry_anchor (null) | REJECT (null anchor) | −0.0029 | 0 | 1,180 | 0/8 | 0.894 | n/a | n/a |
| CAMPAIGN_015 | failed_breakout_reversal | REJECT | −0.0101 | −0.0072 | 375 | 2/8 | 2.848 | WITHIN_NULL | worsens |
| CAMPAIGN_016 | weekly_cross_sectional_momentum | REJECT | −0.0633 | −0.0604 | 137 | 3/8 | 0.982 | WITHIN_NULL | worsens |
| CAMPAIGN_017 | weekly_volatility_contraction_breakout | REJECT | −0.0227 | −0.0198 | 230 | 3/8 | 0.770 | WITHIN_NULL | worsens |

Dedup-safe artifact paths:

- CAMPAIGN_015: `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/`
- CAMPAIGN_016: `backtests/CAMPAIGN_016_weekly_cross_sectional_momentum/`
- CAMPAIGN_017: `backtests/CAMPAIGN_017_weekly_volatility_contraction_breakout/`

See also [`POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md`](POST_DEDUP_CAMPAIGN_METRIC_MATRIX.md) and [`POST_DEDUP_ARCHETYPE_ANALYSIS.md`](POST_DEDUP_ARCHETYPE_ANALYSIS.md).

---

## 3. Why CAMPAIGN_018 is not justified now

CAMPAIGN_018 would be another **broad pattern-family discovery** campaign without a pre-registered hypothesis that falsifies the C015–C017 failure cluster. Meta-analysis already rejected:

- pair-specific lab (USD_JPY ≈ null noise),
- regime-specific lab (fold winners do not align across families),
- immediate data expansion (C015 has adequate *n* and still fails WITHIN_NULL),
- financing sprint as the *immediate* next step (aggregate edge absent before cost refinement).

Scaffolding CAMPAIGN_018 now would violate the pause rationale and the research-freeze discipline. **CAMPAIGN_018 is not created.**

---

## 4. Why pair-specific lab is not justified

- **USD_JPY** is positive in 3/3 campaigns but exp_r ≈ **0.001–0.004 R** — indistinguishable from the null centre (−0.0029 R) and null fold std band (~0.048 R).
- **NZD_USD / EUR_USD** “leaders” in CAMPAIGN_016 are **sparse-trade concentration artifacts** (e.g. NZD_USD ~2.24 R on tiny *n*), not stable cross-family signal.
- **USD_CAD** is consistently negative across campaigns — useful as an **exclusion note**, not as a long-bias lab target.
- No pair shows beat-null magnitude **≥ 0.05 R** at aggregate level with stable replication across C015–C017.

Automated classifier `PAIR_SPECIFIC_SIGNAL_WORTH_LAB` is **overridden by human review** in [`POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md`](POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md).

---

## 5. Why side-specific lab is not justified

- Aggregate long exp_r across candidates: **−0.063 R**; short: **+0.020 R** — shorts are *less bad* but portfolio-level anti-overfit remains **WITHIN_NULL**.
- Exit mix is dominated by **stops (~50%)** and **time exits (~48%)** — failure mode is stop-outs and low hit rate, not a clean side asymmetry tradable at seven-pair scale.
- Side slicing on exploratory cells would be **post-hoc** on already-rejected campaigns.

---

## 6. Why retuning is forbidden

- CAMPAIGN_015, CAMPAIGN_016, and CAMPAIGN_017 were run under **pre-committed gates** on deduped inputs. Retuning parameters, gates, or cost bands after seeing fold/pair cells is **explicit overfitting** on rejected evidence.
- None cleared **ROBUST_ABOVE_NULL**; all are **WITHIN_NULL**. Parameter sweeps cannot convert WITHIN_NULL into approval without a new pre-registered hypothesis and campaign ID.
- `configs/approved_strategies.yaml` must remain empty; no paper/demo/live enablement is authorized.

**Forbidden during pause:** threshold tweaks, fold gating changes, pair subsets chosen from post-hoc winners, indicator variant searches branded as “refinements” of C015–C017.

---

## 7. What evidence would reopen strategy discovery

Future broad or family-specific strategy research may resume only when **all** re-entry gates below are satisfied. Meeting one gate alone is insufficient.

### 7.1 Structural / infrastructure gates (at least one required)

| gate | description |
|---|---|
| New external data source | Materially different inputs (e.g. alternative vendor, tick-derived features) with documented provenance — not relabeling existing SQLite H4 |
| New market structure thesis | Written falsifiable claim about *why* edge should exist (microstructure, flow, calendar mechanism) — not another indicator stack on the same bars |
| Observed-cost / financing model completed | Transaction cost and rollover/financing captured from observed practice data and reconciled to backtest PnL — closes optimism gap |
| Extended historical coverage | Longer or denser history that changes trade-count sufficiency for weekly families *with* pre-registered hypothesis |
| Materially different execution timeframe | Validated engine support (e.g. D1 blocker lifted) with pre-commit before run |
| Independent external thesis | Institutional or academic source cited; hypothesis registered before any in-sample peek |

### 7.2 Pre-registration gates (all required)

1. **New falsifiable hypothesis** in a pre-commit doc — **not** a retune of C015/C016/C017.
2. Expected beat-null magnitude **≥ 0.05 R** above deduped null centre on aggregate, with pre-declared minimum trade count and fold pass criteria.
3. **DEDUPED_INPUT** paths only; contaminated pre-fix metrics excluded from claims.
4. Backtrader verification path defined (not BLOCKED/DEFERRED) **or** explicitly scoped as diagnostic-only with decision-blocking flag documented.
5. Human review recorded in a research decision memo — still **no** `approved_strategies.yaml` edit without a separate promotion sprint.

### 7.3 Anti-pattern gate (explicit)

- **Clear pre-registered reason** why the proposal is **not** another indicator variant on the same H4 seven-pair walk-forward template without new structural edge.

---

## 8. What work IS allowed during pause

| allowed | examples |
|---|---|
| Infrastructure | Observed transaction-cost model, spread/session diagnostics, financing capture, data expansion plumbing |
| Evidence hygiene | Dedupe audits, null baseline maintenance, archive validation |
| Parity / verification | Backtrader lane for **existing** families — diagnostic only, not strategy evidence |
| Documentation | Pause memos, backlog updates, non-strategy sprint prompts |

| not allowed | examples |
|---|---|
| New broad campaigns | CAMPAIGN_018, CAMPAIGN_019 pattern discovery without gates |
| Retuning | C015/C016/C017 parameters, gates, pair subsets from post-hoc cells |
| Promotion | paper/demo/live, `approved_strategies.yaml` entries |
| Broker calls | OANDA order placement or live account trading |

---

## 9. Related documents

| document | role |
|---|---|
| [`POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md`](POST_DEDUP_FAILURE_META_ANALYSIS_001_SUMMARY.md) | Meta-analysis close-out |
| [`POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md`](POST_DEDUP_NEXT_RESEARCH_LANE_DECISION.md) | Lane selection + re-entry criteria source |
| [`BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_PLAN.md`](BROAD_STRATEGY_PAUSE_AND_ROADMAP_001_PLAN.md) | This sprint plan |
| [`NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md`](NEXT_NON_STRATEGY_WORKSTREAM_DECISION.md) | Selected non-strategy sprint (Phase 4) |
