# Backtrader CAMPAIGN_011 — Phase 3 full-window run (pre-fix)

**Date:** 2026-05-25
**Branch:** `infra-backtrader-secondary-lane-004-campaign-011`
**Phase:** 3 of `BACKTRADER_CAMPAIGN_011_004_PLAN.md`
**`strategy_evidence: false`**

> Captures the **initial** (pre-fix) full-window Backtrader-lane
> CAMPAIGN_011 run output, exactly as produced. Any divergence found
> here is preserved for the Phase 4 comparison; any Backtrader-lane
> fix lands in Phase 5. CAMPAIGN_011 remains REJECT / null diagnostic
> anchor by design.

## 1. Exact command

```bash
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_011 \
    --output research/backtrader_lane/results/campaign_011_full_window_004
```

(The CSV export directory defaults to
`research/lean_parity/exports/campaign_002_h4/` — the same gitignored
CSVs sprint 003 already validated.)

## 2. Data source

| field | value |
|---|---|
| CSV directory | `research/lean_parity/exports/campaign_002_h4/` (gitignored bulk data; sha256-verified against the committed `*.provenance.json` sidecars on every load) |
| Provenance source | Sprint 003 regenerated the 7 CSVs from `data/campaign_002.sqlite3` (no OANDA call); their sha256 matches the committed provenance bit-for-bit (`BACKTRADER_REAL_DATA_PREFLIGHT_003.md`) |
| OANDA / network access | **none** |
| Credentials touched | **none** |

## 3. Backtrader version + environment

| field | value |
|---|---|
| Backtrader | `1.9.78.123` |
| Python | `3.12.3` |
| Platform | `macOS-26.3.1-arm64-arm-64bit` |
| Git commit at run | `07497392230ac03921efd27efa85fbacee5876e3` (Phase 2 — `0749739`) |
| Git dirty at run | `False` |

## 4. Reference artifact path

`research/lean_parity/campaign_011_h4_bespoke_reference.json` (sha256
`fba55057499756a4f588909645d1b10a4d98c881240efdd5b8d69b90670d1b78`,
2 800 total trades).

## 5. Deterministic seed behaviour

`master_seed = 20260523` (verified at adapter load by
`_assert_frozen(...)`). Random source is SHA-256 only —
`_derive_random_pair` produces bit-identical `(bar_random, gate_random)`
pairs on identical inputs (31 unit tests in Phase 1 cover this).

Two consecutive runs produced **bit-identical** artefacts:

```
$ shasum -a 256 /tmp/c011_bt_summary_run1.json /tmp/c011_bt_run2/backtrader_summary.json
59b719075b014d0098548e7fd519a6ea57faf09daa34acd3a1c7ad5ddbef7ad5  run1/backtrader_summary.json
59b719075b014d0098548e7fd519a6ea57faf09daa34acd3a1c7ad5ddbef7ad5  run2/backtrader_summary.json

$ shasum -a 256 /tmp/c011_bt_trades_run1.jsonl /tmp/c011_bt_run2/backtrader_trades.jsonl
a28cf11c2f588ccfd38ecdd4719b2f24393ca8697df482c59e22599936f0e6a9  run1/backtrader_trades.jsonl
a28cf11c2f588ccfd38ecdd4719b2f24393ca8697df482c59e22599936f0e6a9  run2/backtrader_trades.jsonl
```

Determinism on the BT side: **PASS**.

## 6. Full-window dates

| field | value |
|---|---|
| Window | `2020-01-01` → `2026-05-20` (inclusive UTC) |
| Granularity | `H4` |
| Pairs | 7 (canonical order) |

## 7. Run status

**Completed without warnings or errors.** No instruments blocked. No
strict-data sha drift. ~12 s wall-clock on this hardware.

## 8. Total trade count

| field | value |
|---|---|
| BT total trades | **2 808** |
| Bespoke total trades (reference) | **2 800** |
| Δ | **+8 trades (≈ +0.29 %)** |

The Δ is **non-zero**; Phase 4 will classify it. Initial inspection
(see §9) traces the cause to a warmup-window off-by-N between the BT
adapter and the bespoke engine; the fix lands in Phase 5.

## 9. Per-pair trade counts

| instrument | BT trades | bespoke trades | Δ | BT pnl_account | BT win_rate |
|---|---|---|---|---|---|
| EUR_USD | 395 | 394 | +1 | -23.87 | 0.4734 |
| GBP_USD | 401 | 400 | +1 | -5.24 | 0.4738 |
| USD_JPY | 419 | 418 | +1 | +28.57 | 0.4940 |
| AUD_USD | 385 | 385 | **0** | -30.39 | 0.4753 |
| USD_CAD | 396 | 394 | +2 | -11.18 | 0.4697 |
| USD_CHF | 411 | 409 | +2 | +22.70 | 0.5061 |
| NZD_USD | 401 | 400 | +1 | -13.09 | 0.4763 |
| **total** | **2 808** | **2 800** | **+8** | **-32.51** | — |

### 9.1 Initial-trade timestamp comparison (EUR_USD)

| run | first trade entry | side | units |
|---|---|---|---|
| BT (pre-fix) | `2020-01-08T22:00:00+00:00` | short | 289 |
| Bespoke reference | `2020-01-10T10:00:00+00:00` | long | 352 |
| BT (pre-fix) — second trade | `2020-01-10T10:00:00+00:00` | long | 343 |

The BT side fires an **extra** signal at `2020-01-08T22:00:00+00:00`
that the bespoke engine skips. From the second trade onward both
sides share the same entry timestamps (units differ slightly because
of NAV compounding — BT had one extra trade closing first).

`2020-01-08T22:00:00+00:00` is bar index **31** (0-indexed) in the
EUR_USD CSV, counting the H4 candle that opens at 22:00 UTC on
2020-01-01 as bar 0 and respecting weekend gaps. The bespoke engine
runs `for i in range(warmup, len(df))` with
`warmup = max(strategy.warmup_bars_required(), 5)` and the strategy
declares `warmup_bars_required() = 32` (see
`src/forex_bot/strategies/random_entry_anchor.py:99-101`), so the
bespoke engine **skips bars 0-31 entirely** and first calls the
strategy on bar index 32. The BT adapter currently honours only
the strategy-internal R1 check (`len(df) >= atr_lookback + 2 = 16`),
so it processes bars 16-31 — bars where the SHA-256 gate fires are
extra entries the bespoke side never sees. This is the load-bearing
cause of the +8 trade delta.

## 10. Warnings / errors

None. pytest's `filterwarnings = ["error", ...]` did not escalate
anything during the run.

## 11. Approximation flags carried by the adapter

(See `research/backtrader_lane/strategies/campaign_011_random_entry_anchor.py`
`CAMPAIGN_011_APPROXIMATION_FLAGS`.)

- `CAMPAIGN_011_DETERMINISTIC_SEED`
- `CAMPAIGN_011_TIME_STOP_ONLY`
- `CAMPAIGN_011_NO_RISK_ENGINE_PARITY`
- `ATR_PRIOR_BAR`
- `MID_CLOSE_FOR_STOP_PLACEMENT`
- `BACKTRADER_BROKER_BYPASSED`
- `MANUAL_SIZING_RISK_FRACTION`
- `NO_FINANCING`
- `R_FORMULA_MATCHES_BESPOKE`

## 12. Local generated files NOT committed

| file | location | committed | reason |
|---|---|---|---|
| `backtrader_summary.json` | `research/backtrader_lane/results/campaign_011_full_window_004/` | **no** | `research/backtrader_lane/results/` is gitignored |
| `backtrader_trades.jsonl` (2 808 lines) | same | **no** | gitignored bulk |
| `backtrader_metrics.json` | same | **no** | gitignored |
| `run_manifest.json` | same | **no** | gitignored |
| `run_log_summary.md` | same | **no** | gitignored |
| `/tmp/c011_bt_summary_run1.json` (determinism scratch) | `/tmp/` | **no** | scratch |
| `/tmp/c011_bt_run2/` (determinism scratch) | `/tmp/` | **no** | scratch |
| `backtests/diagnostics/campaign_011_norisk/full_window_trades.jsonl` (bespoke trade dump used for diff) | repo | **no** | gitignored by sprint 001 of `infra-bespoke-campaign-011-norisk-reference-*` |

The Phase 4 comparison doc commits only a small summary JSON + MD
under `backtests/diagnostics/` policy.

## 13. Required disclosure

CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.
The +8 trade delta is a Backtrader-lane fidelity bug (warmup
mismatch), NOT a bespoke-engine bug, NOT evidence of a strategy
edge, and changes nothing about CAMPAIGN_011's verdict. The fix
lands in Phase 5; the initial run is preserved as the load-bearing
finding.

`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. `strategy_evidence: false`.
