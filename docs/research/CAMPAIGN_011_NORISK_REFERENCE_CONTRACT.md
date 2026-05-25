# CAMPAIGN_011 no-RiskEngine reference — schema contract

**Date:** 2026-05-25
**Branch:** `infra-bespoke-campaign-011-norisk-reference-001`
**Phase:** 1 of `CAMPAIGN_011_NORISK_REFERENCE_001_PLAN.md`
**`strategy_evidence: false`**

> Defines *exactly* what the reference artefact must contain, with
> deterministic-seed and full-window-vs-per-fold semantics pinned,
> before Phase 2 generates it. Approves nothing. CAMPAIGN_011 remains
> REJECT / null diagnostic anchor by design.

## 1. Goal of the contract

A future Backtrader CAMPAIGN_011 comparison sprint must be able to
read **one canonical bespoke reference** and compare its full-window
trades-and-metrics against a BT-lane runner that already operates
full-window per pair (the same harness sprint 003 used for
CAMPAIGN_002). The contract below fixes the artefact's shape, fields,
and determinism rules so the future sprint never has to ask "which
window?" or "which seed?" or "which RiskEngine setting?"

## 2. Decision: full-window primary, per-fold secondary

| dimension | choice | rationale |
|---|---|---|
| Primary reference | **full-window single run** `2020-01-01` → `2026-05-20` | the BT-lane runner is full-window-per-pair; this is the comparison the next sprint will perform |
| Secondary reference | **per-fold rollup** (8 folds, frozen plan) | preserves evidence context with the published walk-forward plan; useful for sanity-check that per-fold trade counts reconcile to the full-window total |
| Plan source | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` (committed) | the rolling plan is frozen pre-commit; this sprint must **not** create a new plan |
| Comparison target the next sprint will use | the **full-window** JSON only | per-fold rollup is informational, not the BT comparison target |

The Backtrader CAMPAIGN_011 comparison sprint should compare
BT-lane full-window output against the full-window
no-RiskEngine bespoke reference (`pairs[]` shape mirrors
CAMPAIGN_002). The per-fold artefact is provided as an
informational sanity-check, not a separate comparison target.

## 3. Deterministic seed rules (binding)

The CAMPAIGN_011 strategy seed is `master_seed = 20260523`, frozen
in `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5 / §6.

The reference must:

- Pass `master_seed=20260523` into the strategy module unchanged.
- Never call `random.random()`, `numpy.random.*`, or Python's
  built-in `hash()`. The seed input is fed only to SHA-256.
- Produce a bit-identical reference JSON on repeat runs given the
  same source SQLite file and the same Python interpreter / repo
  state.
- Sort pairs in the canonical order
  `EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD`
  (matches `CAMPAIGN_002` reference order).
- Sort per-fold rollup by `fold_index` ascending.
- Sort trades (in any optional trade-dump) by `(instrument,
  signal_timestamp, signal_id)`.

These rules guarantee the Phase 3 determinism check (sha256 of two
runs are equal) passes.

## 4. Full-window mechanics

| field | value | source |
|---|---|---|
| window start (inclusive UTC) | `2020-01-01T00:00:00Z` | matches CAMPAIGN_002 reference window |
| window end (inclusive UTC) | `2026-05-20T23:59:59Z` | matches CAMPAIGN_002 reference window |
| granularity | `H4` | per `configs/campaign_011_random_entry_anchor.yaml` |
| pairs | 7 (canonical order) | per `configs/campaign_011_random_entry_anchor.yaml` |
| data source | local SQLite at `data/campaign_002.sqlite3` | per `configs/campaign_011_random_entry_anchor.yaml` |
| data source label | `oanda-practice` | enforced by `DataSourceRepo.latest_for(...)` |
| fill timing | `signal_bar_close` | CAMPAIGN_002 reference precedent and the strategy's `time_stop_only` exit model |
| RiskEngine | `None` | this is the no-RiskEngine reference |
| starting equity | `500.0 USD` | per `configs/campaign_011_random_entry_anchor.yaml:88` |
| risk per trade | `0.25 %` | per `configs/campaign_011_random_entry_anchor.yaml:88` |
| commission | `0.0` per unit | per `configs/campaign_011_random_entry_anchor.yaml:140` |
| slippage | `0.2` pip fixed + `0.5×` spread multiplier | per `configs/campaign_011_random_entry_anchor.yaml:137-138` |
| time stop | `max_bars_in_trade = 6` (strategy-level, **always on**) | per the spec — this is NOT a RiskEngine gate |

The R-formula must match `src/forex_bot/backtesting/engine.py:411-415`
verbatim — same fix sprint 003 applied to the BT lane:

```
risk_distance = abs(entry - stop) * units      # quote ccy * units
r_mult = pnl_home / risk_distance              # NO quote→home conversion
```

The bespoke engine already implements this formula; the BT-lane
adapter aligned to it. The reference will therefore carry the
correct R values out of the box.

## 5. Per-fold rollup mechanics

| field | value | source |
|---|---|---|
| folds | 8 (rolling, frozen) | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` |
| fold windows | inclusive day range → UTC datetimes | matches `scripts/run_campaign_011.py:_fold_dates_to_dts` |
| RiskEngine | `None` (this is the diff from the committed walk-forward run) | sprint contract |
| all other settings | same as §4 | reuse |

The per-fold rollup is computed by running the same full-window
strategy under the no-RiskEngine path against each fold's
**test-window** only and aggregating. Train / validation windows
are not run (they are not part of CAMPAIGN_011's published
evidence).

> Per-fold trade counts are **not** required to sum exactly to the
> full-window total — strategy state (e.g. an open position
> straddling a fold boundary, R2 re-entry blocking on bar at start
> of a fold) makes a small Δ legitimate. The full-window number is
> the canonical one.

## 6. Output paths

| artefact | path | committed | size budget |
|---|---|---|---|
| Full-window reference JSON | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | yes | ≤ 4 KB |
| Per-fold rollup JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | yes | ≤ 12 KB |
| Run report (Phase 3) | `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` | yes | ≤ 30 KB |
| Compact parity-style diagnostics | `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | yes | ≤ 8 KB |
| Optional raw trade dumps (full-window) | `backtests/diagnostics/campaign_011_norisk/full_window_trades.jsonl` | **gitignored** | unbounded |
| Optional raw trade dumps (per-fold) | `backtests/diagnostics/campaign_011_norisk/folds/...` | **gitignored** | unbounded |

`backtests/diagnostics/campaign_011_norisk/` must be added to
`.gitignore` before Phase 3.

## 7. Full-window reference JSON schema

```json
{
  "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline",
  "risk_engine_used": false,
  "fill_timing": "signal_bar_close",
  "window": ["2020-01-01", "2026-05-20"],
  "master_seed": 20260523,
  "config_hash": "<sha256 string>",
  "data_request_hashes": {
    "EUR_USD": "<short hash>",
    "...": "..."
  },
  "strategy_evidence": false,
  "approval_path": "none (null model by design)",
  "total_trades": 0,
  "pairs": [
    {
      "instrument": "EUR_USD",
      "candle_count": 0,
      "trades": 0,
      "expectancy_r": 0.0,
      "return_pct": 0.0,
      "profit_factor": null,
      "win_rate": 0.0,
      "max_drawdown_pct": 0.0
    }
  ]
}
```

Field types and ranges:

| field | type | constraint |
|---|---|---|
| `parity_target` | string | constant — the title above |
| `risk_engine_used` | bool | **must be `false`** |
| `fill_timing` | string | `"signal_bar_close"` |
| `window` | array of two ISO date strings | `["2020-01-01", "2026-05-20"]` |
| `master_seed` | int | `20260523` |
| `config_hash` | string | sha256 hex of the source YAML config |
| `data_request_hashes` | object | per-pair short hashes (12 hex), key = instrument |
| `strategy_evidence` | bool | **must be `false`** |
| `approval_path` | string | `"none (null model by design)"` |
| `total_trades` | int | ≥ 0 |
| `pairs` | array of 7 pair objects | canonical order |
| `pairs[].instrument` | string | one of the 7 canonical pairs |
| `pairs[].candle_count` | int | ≥ 1 |
| `pairs[].trades` | int | ≥ 0 |
| `pairs[].expectancy_r` | float | finite |
| `pairs[].return_pct` | float | finite |
| `pairs[].profit_factor` | float or null | null only when there are no losing trades and ≥ 1 winning trade |
| `pairs[].win_rate` | float | ∈ [0, 1] |
| `pairs[].max_drawdown_pct` | float | ≤ 0 |

`pairs[].expectancy_r`, `return_pct`, `profit_factor`,
`max_drawdown_pct` are rounded to 4 decimal places before write to
match the CAMPAIGN_002 reference convention.

## 8. Per-fold rollup JSON schema

```json
{
  "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline (per-fold)",
  "risk_engine_used": false,
  "fill_timing": "signal_bar_close",
  "master_seed": 20260523,
  "config_hash": "<sha256>",
  "strategy_evidence": false,
  "approval_path": "none (null model by design)",
  "plan_source": "backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json",
  "folds": [
    {
      "fold_index": 0,
      "test_start": "2021-12-21",
      "test_end": "2022-06-18",
      "total_trades": 0,
      "expectancy_r": 0.0,
      "return_pct": 0.0,
      "profit_factor": null,
      "pairs": [
        {
          "instrument": "EUR_USD",
          "trades": 0,
          "expectancy_r": 0.0,
          "return_pct": 0.0,
          "profit_factor": null,
          "win_rate": 0.0
        }
      ]
    }
  ]
}
```

## 9. Comparison fields the future BT sprint should check

Full-window reference: every pair × every metric, with per-metric
tolerance bands inherited from CAMPAIGN_002 sprint 003 verbatim:

| metric | tolerance | classification when exceeded |
|---|---|---|
| `trades` | exact match (Δ = 0) | `SIGNAL_RULE_MISMATCH` |
| `expectancy_r` | abs Δ ≤ `0.0050` | `SIZING_OR_PNL_MISMATCH` |
| `return_pct` | abs Δ ≤ `0.10 %` | `SIZING_OR_PNL_MISMATCH` |
| `profit_factor` | abs rel Δ ≤ `1 %` (None ↔ None) | `STOP_OR_EXIT_ORDERING_MISMATCH` |
| `win_rate` | abs Δ ≤ `0.0010` | `SIGNAL_RULE_MISMATCH` |
| `max_drawdown_pct` | abs Δ ≤ `0.10 %` | `FILL_MODEL_MISMATCH` |

Per-fold rollup is for sanity only — no tolerance bands required.

## 10. Known expected approximation flags (for the future BT adapter)

When the Backtrader CAMPAIGN_011 adapter is later built, these
known approximations must be declared up front and they apply to
the eventual BT-vs-bespoke comparison, not to the reference itself:

* `CAMPAIGN_011_DETERMINISTIC_SEED` — BT adapter must implement the
  SHA-256 seed derivation in
  `_derive_random_pair(master_seed, instrument_name, bar_timestamp_iso)`
  byte-for-byte.
* `CAMPAIGN_011_TIME_STOP_ONLY` — strategy exit model is
  `time_stop_only` (no trailing stop). The 6-bar time stop is
  modelled as a strategy-level rule, not via Backtrader's broker.
* `CAMPAIGN_011_NO_RISK_ENGINE_PARITY` — spread / session /
  loss-limit gates are intentionally absent on **both sides** of
  the comparison because the reference is no-RiskEngine.
* `R_FORMULA_MATCHES_BESPOKE` — same flag the sprint-003 BT-lane
  adapter carries; the reference is computed with the bespoke
  formula at `src/forex_bot/backtesting/engine.py:411-415`.

These flags are documented here only as a hand-off note for the
next sprint. **The reference produced by this sprint carries
none of them** — it is the bespoke engine output, by definition.

## 11. Limitations

- The reference is a single-window full-run plus an informational
  per-fold rollup. It does **not** include train / validation
  windows; CAMPAIGN_011's published evidence uses only test
  windows, and there is no benefit to running train / validation
  in the reference.
- The no-RiskEngine path silences the spread / session / loss-limit
  gates. The reference therefore reports **more** trades than the
  committed walk-forward `results.json` (which had RiskEngine
  wired). This is the intended diff and is the whole point of a
  no-RiskEngine reference.
- The reference does **not** include financing / swap costs; the
  CAMPAIGN_011 financing overlay
  (`CAMPAIGN_011_FINANCING_OVERLAY.md`) was a separate diagnostic
  pass on the walk-forward trades and remains independent.
- The reference **cannot** be used as evidence of a strategy edge
  (CAMPAIGN_011 is a null model by construction; an "improvement"
  caused by removing the RiskEngine is not edge — it is the
  absence of operational safety gates).
- The reference is not signed for paper / demo / live trading.
  CAMPAIGN_011 cannot be added to
  `configs/approved_strategies.yaml` under any circumstance.

`strategy_evidence: false`. CAMPAIGN_011 remains REJECT / null
diagnostic anchor by design. Paper / demo / live remain blocked.
