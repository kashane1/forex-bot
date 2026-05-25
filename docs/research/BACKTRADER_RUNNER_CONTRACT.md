# Backtrader Lane — Runner Contract

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Phase:** 3 of `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
**`strategy_evidence: false`**

The runner is the single entry point that drives one registered
campaign through Backtrader and writes a fixed set of compact comparable
artefacts. It is **campaign-agnostic** — the campaign id picks a
`CampaignAdapter` from a registry, and the registered adapter owns the
strategy logic (rules, sizer, commissioner, analyzers).

## 1. Entry points

| surface | path |
|---|---|
| Python API | `research/backtrader_lane/runner.py` → `run(RunOptions)`, `preflight(RunOptions)` |
| CLI | `scripts/run_backtrader_parity.py` |

### CLI flags

```
--campaign <ID>            # required (or --list-campaigns)
--output <DIR>             # required
--instruments PAIR [PAIR…] # optional override; defaults to the campaign's set
--data-export-dir <DIR>    # default research/lean_parity/exports/campaign_002_h4/
--starting-equity-usd N    # default campaign's starting equity
--dry-run                  # preflight only; writes empty-trades artefacts
--no-strict-data           # allow sha drift vs committed provenance (off by default)
--list-campaigns           # print registered campaign ids and exit
```

Exit codes:

- `0` — success (or successful dry-run / `--list-campaigns`)
- `2` — usage error (missing required arg, unknown campaign id)

## 2. Inputs

| input | source |
|---|---|
| candle CSVs | `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv` (gitignored) |
| provenance JSONs | `research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.provenance.json` (committed) |
| campaign registry | adapters registered via `register_campaign(...)` in `research/backtrader_lane/strategies/*.py` |

The runner *never* fetches candles, *never* talks to a broker, *never*
imports `forex_bot.broker` / `lean` / `quantconnect`, *never* writes to
the source CSVs.

## 3. Outputs

Every successful run (including `--dry-run`) writes exactly the
following files into `--output`:

```
<output>/
  run_manifest.json          # generated_at, git commit, packages, campaign meta,
                             # instruments requested/run/blocked, data provenance
                             # per instrument, execution config
  backtrader_summary.json    # per-pair + aggregate metrics, strategy_evidence: false
  backtrader_trades.jsonl    # one closed BacktraderTrade per line, sorted-keys JSON
  backtrader_metrics.json    # analyzer outputs (TradeAnalyzer counts, final cash)
  run_log_summary.md         # human-readable: campaign, env, per-pair table,
                             # blocked instruments, approximation flags
```

`backtrader_summary.json` shape (top-level keys):

```jsonc
{
  "campaign_id": "SMOKE_FIXTURE",
  "strategy_id": "smoke_oneshot",
  "strategy_version": "0.0.0-smoke",
  "starting_equity_usd": 10000.0,
  "total_trades": 1,
  "total_pnl_account": 0.5,
  "pairs": [
    {
      "instrument": "TEST_PAIR",
      "candle_count": 12,
      "trades": 1,
      "wins": 1, "losses": 0, "win_rate": 1.0,
      "pnl_account_total": 0.5,
      "final_cash": 10000.5,
      "starting_cash": 10000.0,
      "analyzer": {"closed_trades": 1}
    }
  ],
  "blocked_instruments": [],
  "strategy_evidence": false,
  "dry_run": false
}
```

`backtrader_trades.jsonl` row shape:

```jsonc
{
  "instrument": "TEST_PAIR",
  "side": "long",
  "entry_time": "2024-01-02T06:00:00+00:00",
  "entry_price": 1.10032,
  "exit_time":  "2024-01-03T02:00:00+00:00",
  "exit_price":  1.10082,
  "units":  1000,
  "exit_reason": "smoke_oneshot",
  "bars_held": 5,
  "pnl_quote":   0.5,
  "pnl_account": 0.5,
  "r_multiple":  null,    // populated only when adapter computes R
  "return_pct":  null
}
```

`run_manifest.json` highlights:

- `_meta.generated_at` (ISO-8601 UTC)
- `command` (the script's argv excluding `python`)
- `git_commit` + `git_dirty`
- `packages.{python,platform,backtrader,pandas}`
- `campaign.{campaign_id,strategy_id,strategy_version,description,approximation_flags,notes}`
- `instruments.{requested,run,blocked}`
- `data.strict_mode` + `data.per_instrument[]` (each entry carries
  `csv_sha256`, `provenance_data_sha256`,
  `provenance_campaign_002_data_request_hash`, `first_ts`, `last_ts`,
  `bar_count`, and `approximation_flags` from the adapter)
- `execution.{starting_equity_usd, risk_per_trade_pct}`
- `strategy_evidence: false`

## 4. Determinism

Re-running the runner on the same fixture writes a **bit-identical**
`backtrader_trades.jsonl` and a `backtrader_summary.json` that differs
only on the explicit `dry_run` boolean. The manifest's
`_meta.generated_at` and `command` are expected to vary; everything
else is byte-stable.

## 5. Failure modes

| failure | runner behaviour |
|---|---|
| missing CSV (or provenance) for an instrument | instrument added to `blocked_instruments`; run continues; manifest records it |
| sha256 drift versus committed provenance | `CandleProvenanceError` raised (strict mode, default); runner exits non-zero |
| CSV header drift | `CandleSchemaError` raised; runner exits non-zero |
| empty CSV / non-monotonic timestamps / OHLC invariants broken | `ValueError` raised; runner exits non-zero |
| unknown campaign id | `KeyError` raised; CLI exits with code 2 |
| OANDA env-var name *or value* present in the rendered manifest text | `RuntimeError` raised; manifest is overwritten only after the check passes |
| sub-H4 inter-bar gap | `ValueError` raised |

The runner never silently drops data, never silently writes a fake
trade, and never silently treats a missing instrument as zero trades —
those are different states and each has its own artefact representation.

## 6. Known limitations / approximations

Inherited from `BACKTRADER_DATA_ADAPTER_SPEC.md`:

1. `MID_OHLC_DERIVED` — Backtrader sees mid OHLC, derived from bid+ask.
2. `BAR_OPEN_TIMESTAMP` — the index value is the bar OPEN time.
3. `HALF_SPREAD_CLOSE` — only the close-time half-spread is carried.

Added by the runner harness itself:

4. `BACKTRADER_BROKER_DEFAULT_FILLS` — Backtrader's default broker fills
   at the next bar's open price unless `cheat_on_close=True` is set;
   each campaign adapter is responsible for configuring this to match
   the campaign's documented fill timing (CAMPAIGN_002 uses
   `signal_bar_close`, so adapters that mirror CAMPAIGN_002 must enable
   `cheat_on_close`).
5. `BACKTRADER_SIZER_DEFAULT_UNIT` — the default `Sizer` uses whole
   units; campaigns sized as a risk fraction may incur sub-bps rounding
   drift versus the bespoke engine's float-precision sizing.
6. `NO_RISK_ENGINE_GATES` — the runner does **not** replicate the
   bespoke `RiskEngine` gates (spread, session, exposure, margin). This
   matches CAMPAIGN_002's `risk_engine=None` bespoke reference and the
   existing `research/parity_verifier/` design.
7. `NO_FINANCING_OVERLAY` — the runner does **not** apply financing or
   the ESTIMATED + conservative-stress overlay. Comparison harness in
   Phase 5 runs pre-financing only.

Each per-campaign adapter must declare any additional approximation
flags it introduces (e.g. `DONCHIAN_PRIOR_BARS_ONLY`,
`TIME_STOP_BAR_COUNTER`), and the runner surfaces them in
`campaign.approximation_flags` of the manifest plus the
`run_log_summary.md`.

## 7. Tests (Phase 3)

`tests/unit/backtrader_lane/test_runner.py` — 17 tests covering:

- registry registration / unknown-campaign error
- preflight (runnable + blocked) reporting
- expected artefact files exist and are non-empty
- summary carries `strategy_evidence: false` and per-pair counts
- deterministic trade JSONL on the fixture (round-trip stable)
- dry-run produces empty trades but still writes the manifest
- blocked when CSV missing — no fake trade, manifest records BLOCKED
- manifest data block carries sha256 and approximation flags
- OANDA env var name *and* value cannot leak into the manifest
- `--no-strict-data` is a documented escape hatch; strict mode is the
  default and raises on sha drift
- runner module imports no `forex_bot` / broker / LEAN / QuantConnect
- CLI entry-point smoke (`--list-campaigns`, missing args → 2, unknown
  campaign → 2)

Validation:

```bash
python -m pytest tests/unit/backtrader_lane -q
# → 39 passed (7 smoke + 15 adapter + 17 runner)
```

## 8. Safety invariants

- `configs/approved_strategies.yaml` untouched.
- `src/forex_bot/backtesting/` untouched.
- No `forex_bot` import in `research/backtrader_lane/runner.py` or
  `scripts/run_backtrader_parity.py` (greppable test enforces).
- No `backtrader.brokers.oandabroker` / `backtrader.stores.oandastore` /
  `backtrader.feeds.oanda` / `quantconnect` / `lean` import in any
  Backtrader-lane file (greppable test enforces).
- Manifest sanitiser raises if any of `OANDA_TOKEN`, `OANDA_API_TOKEN`,
  `OANDA_ACCOUNT_ID`, `OANDA_ACCOUNT` ever appear (as key name or
  matching value) in the rendered manifest.
- All raw output directories are gitignored
  (`research/backtrader_lane/results/`).

`strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.
