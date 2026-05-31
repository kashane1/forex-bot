# CAMPAIGN_011 no-RiskEngine bespoke reference — Sprint 001 Plan

**Date:** 2026-05-25
**Branch:** `infra-bespoke-campaign-011-norisk-reference-001`
**Sprint role:** infrastructure / reference-artifact generation
**`strategy_evidence: false`**

> This sprint **does not approve a strategy**, does not change
> CAMPAIGN_011 rules, does not change CAMPAIGN_011's verdict, and
> does not enable paper / demo / live trading.
> `configs/approved_strategies.yaml` remains `approved: []`.
> CAMPAIGN_011 remains **REJECT / null diagnostic anchor by design**.

## 1. Purpose

Produce a canonical **no-RiskEngine** bespoke-engine reference for
`random_entry_anchor 0.1.0-c011` (CAMPAIGN_011), suitable for the
future Backtrader CAMPAIGN_011 comparison sprint.

The Backtrader CAMPAIGN_011 port was deferred in sprint 003 (see
[`BACKTRADER_CAMPAIGN_011_BLOCKED_003.md`](BACKTRADER_CAMPAIGN_011_BLOCKED_003.md))
on two structural grounds:

1. **No published no-RiskEngine bespoke reference for CAMPAIGN_011.**
   The committed per-fold artefacts under
   `backtests/CAMPAIGN_011_random_entry_anchor/` were generated with
   `RiskEngine(mode='backtest')` wired in, so a direct BT-lane (no
   spread / session / loss-limit gates) vs bespoke (with gates)
   comparison would classify as `SIGNAL_RULE_MISMATCH` from
   gate-driven rejections rather than any real divergence.
2. **Per-fold vs full-window shape mismatch.** The BT-lane runner is
   full-window-per-pair; CAMPAIGN_011's bespoke evidence is per-fold
   per-pair (8 folds × 7 pairs).

This sprint addresses prerequisite (1). Prerequisite (2) is a
BT-lane feature decision (not a bespoke-side operation) and remains
out of scope here.

## 2. Non-goals (binding)

- Do **not** approve any strategy. `configs/approved_strategies.yaml`
  remains `approved: []`.
- Do **not** change CAMPAIGN_011 rules, frozen parameters, or
  `master_seed`. The seed is fixed at `20260523` per
  `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5 / §6.
- Do **not** change CAMPAIGN_011's REJECT / null-diagnostic verdict.
- Do **not** modify the bespoke engine itself unless a tiny helper /
  CLI shape requires it.
- Do **not** modify the Backtrader lane except for docs referencing
  the new reference artefact.
- Do **not** make any OANDA API call.
- Do **not** run paper / demo / live.
- Do **not** use QuantConnect / LEAN.
- Do **not** commit `.env`, SQLite, bulk CSVs, raw trade dumps, or
  secrets.
- Do **not** re-fetch the data; only reuse `data/campaign_002.sqlite3`
  (the CAMPAIGN_002 / CAMPAIGN_011 shared OANDA-practice H4 store).

## 3. Inventory of existing CAMPAIGN_011 artefacts

| artefact | committed | shape | RiskEngine | role |
|---|---|---|---|---|
| `configs/campaign_011_random_entry_anchor.yaml` | yes | YAML | n/a | frozen config |
| `src/forex_bot/strategies/random_entry_anchor.py` | yes | Python | n/a | strategy module |
| `scripts/run_campaign_011.py` | yes | Python | **wired** | per-fold walk-forward runner |
| `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/plan.json` | yes | JSON (8 folds) | n/a | rolling plan |
| `backtests/CAMPAIGN_011_random_entry_anchor/walk_forward/results.json` | yes | JSON | **wired** | per-fold metrics + REJECT |
| `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_PAIR_summary.json` | yes (56 files) | JSON | **wired** | per-fold per-pair summary |
| `backtests/CAMPAIGN_011_random_entry_anchor/folds/fold_NN/fold_NN_PAIR_trades.csv` | yes (56 files, small) | CSV | **wired** | per-fold per-pair trades |
| `docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` | yes | MD | n/a | frozen parameter source |
| `docs/research/RANDOM_ENTRY_DIAGNOSTIC_ANCHOR_IMPLEMENTATION_SPEC.md` | yes | MD | n/a | R1–R8 spec |
| `docs/research/CAMPAIGN_011_WALK_FORWARD_RESULT.md` | yes | MD | **wired** | walk-forward report |

**No no-RiskEngine bespoke reference exists.** This sprint creates it.

## 4. Frozen rule / parameter source

The reference must run **exactly** the frozen CAMPAIGN_011 rules, no
tuning. Source of truth, verbatim:

* Strategy module: `src/forex_bot/strategies/random_entry_anchor.py`
  (R1–R8 enforced).
* Frozen parameters: `docs/research/CAMPAIGN_011_PRECOMMIT_CHECKLIST.md`
  §5:

  | parameter | value |
  |---|---|
  | `version` | `0.1.0-c011` |
  | `timeframe` | `H4` |
  | `master_seed` | `20260523` |
  | `entry_probability_per_bar` | `0.05` |
  | `atr_lookback` | `14` |
  | `atr_stop_multiple` | `2.0` |
  | `trailing_stop_atr_multiple` | `null` |
  | `max_bars_in_trade` | `6` |
  | `min_atr_pips` | `{}` |
  | `risk.risk_per_trade_pct` | `0.25` |

* Universe: 7 pairs (`EUR_USD`, `GBP_USD`, `USD_JPY`, `AUD_USD`,
  `USD_CAD`, `USD_CHF`, `NZD_USD`).
* Granularity: `H4`.
* Window: `2020-01-01` → `2026-05-20` (full split — same window the
  CAMPAIGN_002 no-RiskEngine reference uses).

Any deviation from the values above is a *new* candidate per
`CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §5 and is forbidden here.

## 5. Data source (decided)

Local-only: `data/campaign_002.sqlite3` (the same store the
existing CAMPAIGN_011 with-RiskEngine artefacts use; see
`configs/campaign_011_random_entry_anchor.yaml:44`).

In the worktree, this file lives at
`/Users/kashane/dev/forex-bot/data/campaign_002.sqlite3` (115 MB,
**not** inside the worktree's isolated `data/`). The sprint-003
finding that this file is reachable from the worktree applies here
too. Sprint 003 already proved the data is sufficient for a
full-window CAMPAIGN_002 run (1 647 trades, all 7 pairs).

If for any reason the DB is unreachable from this worktree, the
sprint stops cleanly and writes a blocked doc. **No OANDA fetch.**

## 6. No-RiskEngine interpretation

"No-RiskEngine" means the bespoke `BacktestEngine` is instantiated
with `risk_engine=None`. Per
`src/forex_bot/backtesting/engine.py:10-13` and the
sprint-001 / sprint-003 use of
`scripts/run_custom_campaign_002_h4_parity.py --no-risk-engine`,
this disables:

* spread filter (config: `spread_filter.*`),
* session filter (config: `session_filter.*`),
* daily / weekly / total drawdown gates (config: `risk.max_*`),
* margin gates (config: `margin.*`).

It **does not** disable:

* the strategy's own R1–R8 logic (seed, gate, ATR-stop, time stop),
* position-uniqueness (R2 — strategy refuses re-entry while a
  position is open),
* the `max_bars_in_trade = 6` time stop (strategy-level rule),
* fill timing (`signal_bar_close`),
* commission / slippage modelling (`backtest.*`).

This is the parity-isolation contract used for the CAMPAIGN_002
no-RiskEngine reference; CAMPAIGN_011 inherits it verbatim.

## 7. Expected outputs

| artefact | path | committed | purpose |
|---|---|---|---|
| machine-readable summary | `research/lean_parity/campaign_011_h4_bespoke_reference.json` | yes (small) | future BT comparison target |
| run report | `docs/research/CAMPAIGN_011_NORISK_REFERENCE_RESULT.md` | yes | Phase 3 result doc |
| compact diagnostics | `backtests/diagnostics/custom_campaign_011_h4_parity_norisk.md` | yes (small) | parity-style summary table |
| raw trade dumps | `backtests/diagnostics/campaign_011_norisk/` | **gitignored** | optional, large; only if produced |

Reference-JSON schema mirrors `campaign_002_h4_bespoke_reference.json`:

```json
{
  "parity_target": "CAMPAIGN_011 H4 random_entry_anchor null-model baseline",
  "risk_engine_used": false,
  "fill_timing": "signal_bar_close",
  "window": ["2020-01-01", "2026-05-20"],
  "master_seed": 20260523,
  "config_hash": "<sha256>",
  "strategy_evidence": false,
  "total_trades": <int>,
  "pairs": [
    {
      "instrument": "...",
      "candle_count": <int>,
      "trades": <int>,
      "expectancy_r": <float>,
      "return_pct": <float>,
      "profit_factor": <float|null>,
      "win_rate": <float>,
      "max_drawdown_pct": <float>
    },
    ...
  ]
}
```

Phase 1 defines the schema in detail (`CAMPAIGN_011_NORISK_REFERENCE_CONTRACT.md`).

## 8. Safety invariants (enforced before merge)

- `configs/approved_strategies.yaml` byte-identical to main:
  `approved: []`.
- `src/forex_bot/strategies/random_entry_anchor.py` byte-identical
  to main (R1–R8 untouched).
- `configs/campaign_011_random_entry_anchor.yaml` byte-identical to
  main (frozen parameters untouched).
- No OANDA API call in any phase.
- No `.env` / `*.sqlite3` / bulk CSV staged.
- Determinism: rerun produces an identical reference-JSON content
  hash.
- `strategy_evidence: false` in every emitted artefact.
- Reference JSON's `risk_engine_used: false` and a prominent
  "CAMPAIGN_011 remains REJECT / null diagnostic anchor by design"
  banner in every emitted MD.

## 9. Validation commands (every phase)

```bash
python -m pytest -q
ruff check src tests scripts research/backtrader_lane
python scripts/check_research_freeze.py
python scripts/validate_research_archive.py
python scripts/scan_artifacts_for_secrets.py
```

Determinism check (Phase 3):

```bash
python scripts/export_campaign_011_norisk_reference.py --out /tmp/r1.json
python scripts/export_campaign_011_norisk_reference.py --out /tmp/r2.json
sha256sum /tmp/r1.json /tmp/r2.json
```

Both hashes must match.

## 10. Why this cannot approve CAMPAIGN_011

Producing the reference is a **mechanical reproduction** of the
already-frozen CAMPAIGN_011 rules under the `risk_engine=None`
toggle. It introduces no new hypothesis, sweeps no parameter, runs
no comparison against any future candidate, and never writes to
`configs/approved_strategies.yaml`.

CAMPAIGN_011 is a *null model by construction* (random-seed coin
flip per H4 bar). Even an unexpected PASS on any future evaluation
sprint would, per `CAMPAIGN_011_PRECOMMIT_CHECKLIST.md` §12,
trigger pipeline investigation — never promotion. The pre-commit
explicitly says CAMPAIGN_011 cannot be added to
`configs/approved_strategies.yaml` under any circumstance.

`strategy_evidence: false`. Paper / demo / live remain blocked.
