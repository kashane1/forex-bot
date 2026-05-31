# Backtrader CAMPAIGN_011 — handoff from the no-RiskEngine reference

**Date:** 2026-05-25
**Branch (this sprint):** `infra-bespoke-campaign-011-norisk-reference-001`
**Sprint role:** documentation hand-off to the next Backtrader sprint
**`strategy_evidence: false`**

> This document tells the next Backtrader sprint exactly what is now
> in the repo, where it lives, and what to do with it. The next
> sprint will port CAMPAIGN_011 to the Backtrader secondary lane and
> compare it to the new bespoke reference. This document itself
> approves nothing, tunes nothing, and changes no verdict.
> CAMPAIGN_011 remains REJECT / null diagnostic anchor by design.

## 1. What changed in the repo as of this sprint

| change | path | committed | role |
|---|---|---|---|
| **Canonical full-window no-RiskEngine reference JSON** | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | yes | the BT-vs-bespoke comparison target |
| Informational per-fold rollup JSON | `research/lean_parity/campaign_011_h4_bespoke_reference_per_fold.json` | yes | sanity check vs the published walk-forward plan |
| Diagnostics MD | `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | yes | human-readable parity-style summary |
| Exporter script (regenerate the reference) | `scripts/export_campaign_011_norisk_reference.py` | yes | deterministic; `--full-window-only` flag for fast determinism check |
| Reference contract + schema spec | `docs/research/CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md` | yes | binding shape, tolerance bands, expected approximation flags |
| Reference runner doc | `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RUNNER.md` | yes | exact command + failure modes |
| Reference result doc | `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` | yes | the numbers + determinism check |

`configs/approved_strategies.yaml`, `src/forex_bot/strategies/random_entry_anchor.py`,
`configs/campaign_011_random_entry_anchor.yaml`, and
`src/forex_bot/backtesting/engine.py` are **unchanged** by this sprint.
The existing CAMPAIGN_011 walk-forward artefacts under
`backtests/CAMPAIGN_011_random_entry_anchor/` are unchanged.

## 2. Reference artefact summary (verbatim from the result doc)

| field | value |
|---|---|
| Full-window reference JSON sha256 | `fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78` |
| total full-window trades | **2 800** |
| pairs | 7 (canonical order: EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF, NZD_USD) |
| window | `2020-01-01` → `2026-05-20` |
| fill_timing | `signal_bar_close` |
| risk_engine_used | **`false`** |
| master_seed | `20260523` (frozen) |
| config_hash | `69ab4e6f08dca374` |

Per-pair full-window numbers are in
`CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` §4.1.

## 3. Expected future Backtrader inputs

| input | source |
|---|---|
| BT adapter | `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` (**to be created by the next sprint**) |
| Local H4 CSVs | `research/lean_parity/exports/<pair>_h4.csv` (regenerate via `scripts/export_lean_parity_data.py --db /Users/kashane/dev/forex-bot/data/campaign_002.sqlite3 ...` per sprint 003's pattern) |
| Bespoke comparison target | `research/lean_parity/campaign_011_h4_bespoke_reference.json` (this sprint) |
| Comparison runner | `scripts/compare_backtrader_parity.py` (already exists; sprint 003 used it for CAMPAIGN_002) |
| BT-lane runner driver | `scripts/run_backtrader_parity.py` (already exists) |
| Walk-forward plan | `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` — **only needed if the next sprint also implements per-fold comparison; the primary target is full-window** |

## 4. Frozen CAMPAIGN_011 rules (verbatim — for the BT adapter)

Source of truth: `src/forex_bot/strategies/random_entry_anchor.py`
(R1–R8) and `docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5.
The BT adapter must implement R1–R8 byte-for-byte.

| parameter | frozen value |
|---|---|
| `master_seed` | `20260523` |
| `entry_probability_per_bar` | `0.05` |
| `atr_lookback` | `14` |
| `atr_stop_multiple` | `2.0` |
| `trailing_stop_atr_multiple` | `None` |
| `max_bars_in_trade` | `6` (time stop) |
| `risk_per_trade_pct` | `0.25 %` |
| `starting_equity` | `500 USD` |
| `account_currency` | `USD` |
| `granularity` | `H4` |

## 5. Random-seed requirements

The BT adapter **must**:

- Derive the seed string as
  `f"{master_seed}|{instrument_name}|{bar_timestamp_iso}"` (UTF-8).
- Feed it through `hashlib.sha256(...).digest()` byte-for-byte.
- Slice `[:8]` as `bar_random` (big-endian uint64) and `[8:16]` as
  `gate_random` (big-endian uint64), matching
  `src/forex_bot/strategies/random_entry_anchor.py:84-88`.
- Convert the timestamp to UTC ISO 8601 via
  `pd.Timestamp(idx_t).tz_convert(UTC).isoformat()` (the same
  expression the bespoke strategy uses) so the seed input is
  bit-identical between BT and bespoke.

The BT adapter **must not**:

- Use `random.random()`, `numpy.random.*`, or Python's built-in
  `hash()`. These are non-deterministic across versions and would
  silently break parity.
- Sweep, perturb, or otherwise mutate `master_seed`.
- Include any bar-`t` price data (close, high, low, open, volume)
  or ATR value in the seed input.

## 6. Full-window vs per-fold mapping for the next sprint

The next sprint should compare BT-lane full-window output against
the **full-window** no-RiskEngine reference. Per-fold is optional
and informational.

| reference artefact | next-sprint use |
|---|---|
| `campaign_011_h4_bespoke_reference.json` | **primary** — direct full-window comparison; one row per pair × per metric |
| `campaign_011_h4_bespoke_reference_per_fold.json` | optional — used only if the next sprint extends `scripts/run_backtrader_parity.py` to accept a fold plan (`start, end` per fold). Not required for the first BT comparison. |

## 7. Comparison fields + tolerance bands (verbatim from the contract)

The next sprint's `compare_backtrader_parity.py` invocation should
use these tolerance bands (inherited from CAMPAIGN_002 sprint 003,
§9 of `CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md`):

| metric | tolerance | classification when exceeded |
|---|---|---|
| `trades` | exact match (Δ = 0) | `SIGNAL_RULE_MISMATCH` |
| `expectancy_r` | abs Δ ≤ `0.0050` | `SIZING_OR_PNL_MISMATCH` |
| `return_pct` | abs Δ ≤ `0.10 %` | `SIZING_OR_PNL_MISMATCH` |
| `profit_factor` | abs rel Δ ≤ `1 %` (None ↔ None) | `STOP_OR_EXIT_ORDERING_MISMATCH` |
| `win_rate` | abs Δ ≤ `0.0010` | `SIGNAL_RULE_MISMATCH` |
| `max_drawdown_pct` | abs Δ ≤ `0.10 %` | `FILL_MODEL_MISMATCH` |

## 8. Expected approximation flags (BT adapter must declare these up front)

| flag | meaning |
|---|---|
| `CAMPAIGN_011_DETERMINISTIC_SEED` | BT adapter implements the SHA-256 seed derivation byte-for-byte |
| `CAMPAIGN_011_TIME_STOP_ONLY` | strategy exit model is `time_stop_only` (no trailing stop) — the 6-bar time stop is modelled as a strategy-level rule, not via Backtrader's broker |
| `CAMPAIGN_011_NO_RISK_ENGINE_PARITY` | spread / session / loss-limit gates intentionally absent on **both sides** of the comparison (this sprint's reference is no-RiskEngine; the BT adapter must also not model them) |
| `R_FORMULA_MATCHES_BESPOKE` | same flag the CAMPAIGN_002 BT adapter carries post sprint 003: `r = pnl_home / ((entry − stop) × units)` with NO quote→home conversion of the risk denominator |

The CAMPAIGN_002 BT adapter
(`research/backtrader_lane/strategies/campaign_002_trend_following.py`)
is the template; the CAMPAIGN_011 adapter should mirror its
structure, replacing the EMA/Donchian regime logic with R1–R8.

## 9. Sprint-003 R-formula note (very important)

Sprint 003 found and fixed a divergence on USD-base pairs caused by
the BT adapter dividing R's risk denominator by `exit_price`. The
fix was applied to `research/backtrader_lane/strategies/campaign_002_trend_following.py`
post sprint-003 commit `fcf67c5`. The new CAMPAIGN_011 BT adapter
**must use the post-fix R formula from the start**:

```python
# CORRECT (matches bespoke engine.py:411-415):
if self._initial_stop_distance > 0 and self._units > 0:
    risk_distance = self._initial_stop_distance * self._units
    r_mult = pnl_account / risk_distance if risk_distance > 0 else 0.0
```

Do **not** apply a `risk_distance / exit_price` conversion for
USD-base pairs. The bespoke engine deliberately keeps the R
denominator in `(quote × units)` and does not convert to home
currency for R; the BT adapter must match.

## 10. Recommended next branch

```
infra-backtrader-secondary-lane-004-campaign-011
```

Suggested phase outline (the next sprint can tweak):

| phase | task | expected output |
|---|---|---|
| 0 | baseline + plan, branch from `df2007f` (this sprint's Phase 3 commit) | `BACKTRADER_REAL_DATA_RUN_004_PLAN.md` |
| 1 | regenerate the 7 H4 CSVs from `data/campaign_002.sqlite3` (Path B from sprint 003) | preflight doc |
| 2 | implement `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py` + tests (synthetic fixture only; CAMPAIGN_002 adapter is the template) | adapter file + 6–10 tests |
| 3 | run BT lane full-window for CAMPAIGN_011 against the new reference | run + report doc |
| 4 | classify via `scripts/compare_backtrader_parity.py` with the §7 tolerance bands; expect PASS or `SIGNAL_RULE_MISMATCH` (which would itself be a finding to investigate, never tuned away) | comparison doc |
| 5 | sprint summary | INFRA summary doc |

## 11. Required disclosure

This handoff document creates **no** new BT-lane code, **no** new
strategy, and changes **no** verdict. It is documentation for a
future sprint. CAMPAIGN_011 remains REJECT / null diagnostic anchor
by design. CAMPAIGN_002 remains REJECT.
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.
