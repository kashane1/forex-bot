# CAMPAIGN_015 — Post-Run Diagnostics 001 — Sprint Summary

> **SUPERSEDED / STALE DUE TO DUPLICATE-CANDLE CONTAMINATION** — see
> [`CAMPAIGN_015_DEDUPED_RERUN_001_SUMMARY.md`](CAMPAIGN_015_DEDUPED_RERUN_001_SUMMARY.md).

**Branch:** `research-campaign-015-post-run-diagnostics-001`
**Date:** 2026-05-25 / 2026-05-26
**Sprint type:** post-run diagnostic — **NOT** strategy, tuning, or
promotion work.
**Strategy under inspection:** `failed_breakout_reversal 0.1.0-c015`
**Config hash:** `17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`
**Runner verdict (unchanged):** **REJECT**
**Approval status (unchanged):** **NOT_APPROVED**
**Approved-strategy registry (unchanged):** `approved: []`
**Final post-run interpretation label:** **`SPARSE_BUT_PROMISING`**
(with USD_CHF pair-concentration caveats and Phase-4 BT-lane BLOCKED caveat).
**Final recommendation:** **`COLLECT_MORE_DATA_FIRST`** with
`RUN_BACKTRADER_OR_NULL_FIRST` as a hard precondition for any
further CAMPAIGN_015-derived research.

---

## 1 · Commits by phase

| phase | sha | what landed |
|---|---|---|
| 0 | `3f737c4` | Truth audit + sprint plan + rehydrate walk-forward run |
| 1 | `44eafbd` | Gate-failure autopsy script + 10 tests + doc |
| 2 | `5891ced` | Concentration / fragility script + 13 tests + doc |
| 3 | `719e814` | Matched-null + anti-overfit wiring + 6 tests + doc |
| 4 | `73d4277` | BT-vs-bespoke = DATA_MISMATCH (BLOCKED) + doc |
| 5 | `432125c` | Interpretation memo |
| 6 | `99dac8b` | No-follow-up-candidate decision doc |
| 7 | (this commit) | Final validation + this summary |

---

## 2 · Files changed

### Plans, decisions, interpretation (`docs/research/`)
- [`CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md`](CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md)
- [`CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md`](CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md)
- [`CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md`](CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md)
- [`CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md`](CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md)
- [`BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md)
- [`CAMPAIGN_015_POST_RUN_INTERPRETATION.md`](CAMPAIGN_015_POST_RUN_INTERPRETATION.md)
- [`CAMPAIGN_015_NO_FOLLOWUP_DECISION.md`](CAMPAIGN_015_NO_FOLLOWUP_DECISION.md)
- `CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_SUMMARY.md` (this file)

### Diagnostic scripts (`scripts/`)
- [`diagnose_campaign_015_gate_failures.py`](../../scripts/diagnose_campaign_015_gate_failures.py)
- [`diagnose_campaign_015_concentration.py`](../../scripts/diagnose_campaign_015_concentration.py)
- [`run_campaign_015_anti_overfit_diagnostics.py`](../../scripts/run_campaign_015_anti_overfit_diagnostics.py)

### Tests (`tests/unit/`)
- [`test_diagnose_campaign_015_gate_failures.py`](../../tests/unit/test_diagnose_campaign_015_gate_failures.py) — 10 tests
- [`test_diagnose_campaign_015_concentration.py`](../../tests/unit/test_diagnose_campaign_015_concentration.py) — 13 tests
- [`test_run_campaign_015_anti_overfit_diagnostics.py`](../../tests/unit/test_run_campaign_015_anti_overfit_diagnostics.py) — 6 tests

### Machine-readable diagnostic artifacts (`research/campaign_015/diagnostics/`)
- `walk_forward_rehydrate/` — full per-fold + per-pair + per-trade rehydrate run (`gate_result.json`, `fold_detail.json`, `results.json`, `results.md`, `plan.json`, `preflight.json`, and 112 per-pair-per-fold trade CSVs + 112 per-pair-per-fold summary JSONs).
- `gate_failure_autopsy.json` / `gate_failure_autopsy.md`
- `concentration.json` / `concentration.md`
- `null_and_anti_overfit.json` / `null_and_anti_overfit.md`
- `backtrader_comparison.json`

### Files NOT modified (verified)
- `configs/approved_strategies.yaml` — still `approved: []`.
- `backtests/CAMPAIGN_015_failed_breakout_reversal/` — prior BLOCKED
  artifacts left untouched.
- `backtests/CAMPAIGN_011_random_entry_anchor/` — null artifacts
  consumed read-only.
- All prior `docs/research/CAMPAIGN_015_*` and `BACKTRADER_CAMPAIGN_015_COMPARISON.md`
  docs — left untouched. The post-run docs in this sprint are
  *additions*, not revisions.
- All prior strategy modules, walk-forward runner, anti-overfit
  classifier — untouched.

---

## 3 · Commands run

Validation (Phase 0 and Phase 7):

```bash
pytest tests/ -q
ruff check src tests scripts research
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
git status --short
```

Rehydrate walk-forward (Phase 0):

```bash
python scripts/run_campaign_015.py \
  --config configs/campaign_015_failed_breakout_reversal.yaml \
  --out    research/campaign_015/diagnostics/walk_forward_rehydrate
```

Diagnostic scripts (Phases 1 / 2 / 3):

```bash
python scripts/diagnose_campaign_015_gate_failures.py \
  --gate-result research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/gate_result.json \
  --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
  --out-json    research/campaign_015/diagnostics/gate_failure_autopsy.json \
  --out-md      research/campaign_015/diagnostics/gate_failure_autopsy.md

python scripts/diagnose_campaign_015_concentration.py \
  --fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
  --out-json    research/campaign_015/diagnostics/concentration.json \
  --out-md      research/campaign_015/diagnostics/concentration.md

python scripts/run_campaign_015_anti_overfit_diagnostics.py \
  --campaign-fold-detail research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/fold_detail.json \
  --null-fold-detail     backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/fold_detail.json \
  --out-json             research/campaign_015/diagnostics/null_and_anti_overfit.json \
  --out-md               research/campaign_015/diagnostics/null_and_anti_overfit.md
```

BT secondary lane attempt (Phase 4):

```bash
python scripts/run_backtrader_parity.py \
  --campaign CAMPAIGN_015 \
  --output   research/campaign_015/diagnostics/backtrader_lane/
# → fails on row-sha256 drift for all 7 CAMPAIGN_002 H4 CSVs.
```

---

## 4 · Gate-failure autopsy summary

(See [`CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md`](CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md).)

| dimension | base cost | 2x cost |
|---|---|---|
| Failed aggregate gates | `fold_pass_rate_ge_5_of_8`, `trade_count_min_200` | same |
| Passing aggregate gates | `fold_count_ge_8`, `expectancy_r_min`, `profit_factor_min`, `trade_count_max_800`, `pairs_positive_ge_4_of_7`, `single_pair_dominance_le_70pct` | same |
| Folds passing per-fold gates | 0 / 8 | 0 / 8 |
| Folds failing `trade_count_ge_30` | **8 / 8** | **8 / 8** |
| Folds failing `expectancy_r_ge_0` | 1 / 8 (fold 0) | 1 / 8 |
| Folds failing `pairs_positive_ge_3` | 2 / 8 (folds 0, 7) | varies |
| Folds failing `single_pair_dominance_le_60pct` | 1 / 8 (fold 1) | 1 / 8 |
| Counterfactual (NON-GATING) folds passing if trade-count gate dropped | **5 / 8** | 4 / 8 |
| Pair-fold cells with 0 trades | 9 / 56 (16%) | 9 / 56 |
| Pair-fold cells with ≤ 1 trade | 17 / 56 (30%) | 17 / 56 |

---

## 5 · Exact failed gates

**Aggregate (base & 2x cost):**
1. `fold_pass_rate_ge_5_of_8` — 0 folds pass, threshold 5.
2. `trade_count_min_200` — 164 trades, threshold 200.

**Per-fold (base):** every fold fails on at least
`trade_count_ge_30` (max in-fold trades = 28). Folds 0, 7 additionally
fail `pairs_positive_ge_3`. Fold 0 additionally fails
`expectancy_r_ge_0`. Fold 1 additionally fails
`single_pair_dominance_le_60pct` (77.4%).

---

## 6 · Trade-count / fold-pass explanation

Per-fold trade-count series at base cost:
`[18, 26, 26, 28, 24, 14, 14, 14]` — **max 28, min 14, total 164**.

No fold ever clears 30 trades. The `trade_count_ge_30` per-fold gate
is therefore the *root cause* of the 0/8 fold-pass rate (since every
fold fails it before any of the other per-fold gates can save it).
The aggregate `trade_count_min_200` (164 < 200) is the *secondary*
failure; the strategy fires at roughly the rate of 6 trades per pair
per year across the 7-pair / 4-test-year universe.

---

## 7 · Pair / fold concentration findings

(See [`CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md`](CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md).)

- **Top fold (fold 3, 2023-06-14..2023-12-10) = 31.8% of total R**;
  LOO-fold expectancy never drops below +0.189. **Not a single-fold
  artifact.**
- **Top pair USD_CHF = 54.5% of total R**; LOO-pair drops aggregate
  expectancy from +0.230 to +0.125 R/trade. **Real net-R concentration
  in USD_CHF.**
- **Top pair-fold cell `fold_06 / USD_CHF` = 24.9% of total R.**

---

## 8 · Top-trade / top-pair / top-fold concentration findings

| concentration measure | base | 2xcost |
|---|---|---|
| top-1 trade share of total R | 16.5% | 18.4% |
| top-3 trades share of total R | **48.0%** | **54.7%** |
| top-5 trades share of total R | **77.1%** | **87.9%** |
| top-1 pair (net-R) share | USD_CHF 54.5% | USD_CHF (similar) |
| top-1 fold share | fold 3 = 31.8% | fold 3 (similar) |
| top-1 pair-fold cell share | fold_06_USD_CHF = 24.9% | (similar) |
| median trade R | **-0.254** | (similar) |

The aggregate edge is concentrated in ~5 outlier trades over 164. The
distribution is right-skewed: median trade loses; upside lives in the
upper tail.

**Headline-PF anomaly:** the runner reports PF = **107.55** (base) /
**39.69** (2xcost). This is computed at the pair-rollup return_pct
level; with only one negative-return pair (NZD_USD), the denominator
is tiny, which inflates the headline PF. The **honest trade-level PF**
(gross_positive_r / abs(gross_negative_r)) is **1.48 base / 1.40
2xcost** — a modest win/loss ratio, not an extraordinary edge.

---

## 9 · LOO stability result

- **LOO by fold:** aggregate expectancy R ranges from **+0.189**
  (drop fold 3, best fold) to **+0.284** (drop fold 0, worst fold).
  **Never negative.** Not a single-fold artifact.
- **LOO by pair:** aggregate expectancy R ranges from **+0.125**
  (drop USD_CHF) to **+0.272** (drop EUR_USD). **USD_CHF roughly
  halves the edge** when removed.
- LOO-pair fold-pass count is **0 / 8 regardless of which pair is
  dropped** — the per-fold trade-count gate binds throughout.

---

## 10 · Null comparison result

(See [`CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md`](CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md).)

Matched null = CAMPAIGN_011 `random_entry_anchor` on the same 7-pair
/ H4 / 8-fold universe with identical fold windows.

| metric | value |
|---|---|
| C015 mean per-fold expectancy R | +0.223 |
| C011 null mean per-fold expectancy R | -0.003 |
| Mean per-fold gap R | **+0.225** |
| Per-fold t-stat (n=8) | **+3.190** |
| Null per-fold std R | 0.048 |
| LOO-min mean gap R | +0.184 |
| Folds with positive gap | 7 / 8 |

The campaign cleanly beats the matched random-entry null on every
per-fold expectancy except fold 0. **Conditional on the trades that
fired**, the edge is real.

---

## 11 · Anti-overfit label

**`ROBUST_ABOVE_NULL`** — the strongest favorable diagnostic label in
the pre-commit's classifier (§11). All 7 anti-overfit gates pass:

- `loo_min_mean_gap_r ≥ +0.05` (actual +0.184) ✓
- `per_fold_t_stat ≥ +2.0` (actual +3.19) ✓
- `median_per_fold_expectancy_r ≥ 0.0` (actual +0.259) ✓
- `trade_level_cumulative_r > 0` (actual +37.73) ✓
- `pair_concentration (gross-positive-R share) ≤ 70%` (actual 30.2%) ✓
- `fold_concentration ≤ 60%` (actual 22.3%) ✓
- `cost_dominance ≤ 50%` (actual 0%) ✓

> Reconciliation note: the classifier's pair concentration metric
> (30.2%, gross-positive-R lens) differs from Phase 2's net-R lens
> (54.5%). Both are honest. The classifier's is the binding
> pre-committed lens for the label; the net-R view is the lens that
> matters for forward fragility and must be held alongside.

---

## 12 · Backtrader comparison status

**`DATA_MISMATCH` → `BLOCKED`**
(See [`BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md).)

The Backtrader secondary lane refused to load any of the 7
CAMPAIGN_002 H4 CSVs because the runner's row-sha256 (and the raw
file sha256) does **not** match the committed `data_sha256` in the
matching `*.provenance.json`. This is a real data-handling regression
in `research/lean_parity/exports/campaign_002_h4/`, not a strategy
issue, and is out of scope for a post-run diagnostic sprint.

The bespoke lane therefore stands alone in this sprint. Any further
CAMPAIGN_015-derived work must require a clean BT lane as a
precondition.

---

## 13 · Final interpretation label

**`SPARSE_BUT_PROMISING`** with USD_CHF concentration caveats and a
BT-lane BLOCKED caveat. The campaign:

- *clears the matched random-entry null* with statistical significance
  (Phase 3);
- *is not a single-fold or single-trade artifact* once you grant the
  whole window (LOO-fold preserves the edge);
- *is sparse in a way that prevents gate-passing* (every fold fails
  `trade_count_ge_30`);
- *is meaningfully USD_CHF-dependent on the net-R view*;
- *has not been corroborated by the BT secondary lane*.

This is not `AGGREGATE_ARTIFACT`. It is not `NULL_DOMINATED`. It is a
positive per-trade edge on a sample that is too thin and too
USD_CHF-leveraged to flip a verdict.

---

## 14 · Is CAMPAIGN_015 better than previous campaigns?

**Yes, dramatically — and it is the first campaign with positive
aggregate expectancy on the same universe:**

| campaign | strategy | aggregate exp R (base) |
|---|---|---|
| CAMPAIGN_010 | `session_breakout` | -0.041 |
| CAMPAIGN_011 | `random_entry_anchor` (null baseline) | -0.002 |
| CAMPAIGN_012 | `regime_switcher_atr_percentile` | -0.052 |
| CAMPAIGN_013 | `cross_pair_currency_strength_rotation` | -0.056 |
| CAMPAIGN_014 | `calendar_event_window_anomaly` | -0.148 |
| **CAMPAIGN_015** | **`failed_breakout_reversal`** | **+0.230** |

Every prior post-CAMPAIGN_002 campaign on the canonical 7-pair / H4 /
8-fold universe came in *below the random-entry null*. CAMPAIGN_015
clears the null by +0.225 R/trade and clears it on 7 of 8 folds.

---

## 15 · Is CAMPAIGN_015 approved?

**No.** `configs/approved_strategies.yaml` is and remains
`approved: []`. The runner verdict is REJECT. No diagnostic in this
sprint can flip either.

---

## 16 · Are paper / demo / live remain blocked?

**Yes.** All order-capable loops refuse to start. Confirmed by
`python scripts/check_research_freeze.py` which reports paper-loop
and demo-loop both refusing `['trend_following']` and the
research-freeze gate `ALL CHECKS PASSED`.

---

## 17 · Recommended next step

**Sequence:**

1. **Infra sprint A — fix Lean-parity CSV provenance lock-step**, so
   the BT secondary lane can run. Re-export the 7 CAMPAIGN_002 H4
   CSVs and commit matching provenance JSONs together. Verify with
   `python -c "from research.backtrader_lane.data_adapter import load_candles; [load_candles(p) for p in ('EUR_USD','GBP_USD','USD_JPY','AUD_USD','USD_CAD','USD_CHF','NZD_USD')]"`.
   Then run `python scripts/run_backtrader_parity.py --campaign CAMPAIGN_015 --output …`
   against the rehydrate bespoke output. If BT corroborates: proceed.
   If BT disagrees: the corroboration is the new story.

2. **Infra sprint B — extend the H4 universe.** Add as many years of
   OANDA-practice H4 history as the data store supports. Re-run the
   **same** frozen CAMPAIGN_015 config (`config_hash` must match
   `17ddfd7e…`) on the extended universe. No parameter changes.

3. **Decision sprint.** Only if Sprints A + B both succeed and the
   extended-universe expectancy R remains positive *and* the
   per-pair distribution is less USD_CHF-concentrated, write a real
   docs-only follow-up candidate design.

Until then, no new strategy candidate; no approval; no paper /
demo / live changes.

---

## 18 · Files to review first (recommended reading order)

1. [`CAMPAIGN_015_POST_RUN_INTERPRETATION.md`](CAMPAIGN_015_POST_RUN_INTERPRETATION.md) — the human-readable answer.
2. [`CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md`](CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md) — exact failing gates + counterfactual.
3. [`CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md`](CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md) — pair / trade / fold concentration + LOO.
4. [`CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md`](CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md) — null gap, t-stat, classifier label.
5. [`BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md) — BT BLOCKED reason.
6. [`CAMPAIGN_015_NO_FOLLOWUP_DECISION.md`](CAMPAIGN_015_NO_FOLLOWUP_DECISION.md) — why no new candidate yet.
7. [`CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md`](CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_PLAN.md) — sprint plan / scope / hard rules.

---

## 19 · Safety statement (final, verified)

- `configs/approved_strategies.yaml` is `approved: []`. ✓
- Paper / demo / live loops refuse to start. ✓
- Runner verdict for CAMPAIGN_015 is REJECT (NOT_APPROVED). ✓
- No CAMPAIGN_015 parameter has been tuned. ✓
- No pre-committed gate has been relaxed. ✓
- No broker call; no `.env`; no live OANDA. ✓
- No prior campaign evidence was modified. ✓
- The local sqlite DB and lean_parity CSVs are gitignored symlinks
  from the main repo root; never committed. ✓
- Even the strongest diagnostic label (`ROBUST_ABOVE_NULL`) does not
  approve this strategy. ✓
- `pytest tests/ -q` — `1452 passed`.
- `python scripts/check_research_freeze.py` — `research freeze gate: ALL CHECKS PASSED`.
- `python scripts/validate_research_archive.py` — `research archive: ALL CHECKS PASSED`.
- `python scripts/scan_artifacts_for_secrets.py` — `artifact secret scan: PASSED`.
- `ruff check src tests scripts research` — 3 pre-existing findings
  in `research/lean_parity/algorithms/campaign_002_h4_baseline/main.py`
  (commit `e382af4`, unrelated); no new findings from this sprint.
