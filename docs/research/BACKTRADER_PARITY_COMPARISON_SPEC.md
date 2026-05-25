# Backtrader Lane — Parity Comparison Spec

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Phase:** 5 of `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
**`strategy_evidence: false`**

The comparison harness reads a Backtrader-lane `backtrader_summary.json`
(produced by the Phase 3 runner) and a campaign's bespoke reference
JSON, and emits a per-pair + overall divergence classification. It
**does not modify** any input artefact and **cannot approve** a
strategy.

## 1. Entry points

| surface | path |
|---|---|
| Python API | `research/backtrader_lane/compare.py` → `compare(...)`, `classify_pair(...)`, `render_markdown(...)`, `to_json_dict(...)` |
| CLI | `scripts/compare_backtrader_parity.py` |

### CLI

```bash
python scripts/compare_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --backtrader-results research/backtrader_lane/results/campaign_002/ \
    --bespoke-reference research/lean_parity/campaign_002_h4_bespoke_reference.json \
    --output research/backtrader_lane/results/campaign_002/comparison/ \
    [--trade-count-tolerance-pct 5.0] \
    [--expectancy-r-tolerance 0.03] \
    [--return-pct-tolerance 0.5] \
    [--win-rate-tolerance 0.05]
```

`--backtrader-results` may be a directory (containing
`backtrader_summary.json`) **or** the path to `backtrader_summary.json`
directly.

Exit codes:

- `0` — comparison succeeded (regardless of the classification — a
  divergence is a result, not a runner error)
- `2` — missing input file

## 2. Inputs

| input | shape (relevant keys) |
|---|---|
| `backtrader_summary.json` | `campaign_id`, `strategy_id`, `strategy_version`, `total_trades`, `pairs[]` (each with `instrument`, `trades`, optional `expectancy_r`, optional `return_pct`, `win_rate`), `blocked_instruments[]` |
| bespoke reference (e.g. CAMPAIGN_002) | `total_trades`, `pairs[]` (each with `instrument`, `trades`, `expectancy_r`, `return_pct`, `profit_factor`, `win_rate`, `max_drawdown_pct`) |

Per-pair fields not carried on the Backtrader summary (notably
expectancy R) are derived only when computable from trade-list data;
if absent, the harness compares whatever metrics are available and
flags missing dimensions in the pair notes. The Phase 4 CAMPAIGN_002
adapter does not currently compute per-pair expectancy R in the
runner's summary — this is the documented gap; a future iteration of
the runner may add it from `backtrader_trades.jsonl`.

## 3. Outputs

`<output>/comparison_summary.json` (machine-readable) and
`<output>/comparison_summary.md` (human-readable):

```jsonc
{
  "campaign_id": "CAMPAIGN_002",
  "strategy_id": "trend_following",
  "strategy_version": "0.1.0-baseline-frozen",
  "bespoke_reference_path": "…/campaign_002_h4_bespoke_reference.json",
  "backtrader_summary_path": "…/backtrader_summary.json",
  "bt_total_trades": 1647,
  "bespoke_total_trades": 1647,
  "overall_classification": "PASS",
  "blocked_instruments": [],
  "notes": [],
  "generated_at": "2026-05-24T…+00:00",
  "pairs": [
    {
      "instrument": "EUR_USD",
      "bt_trades": 233,
      "bespoke_trades": 233,
      "trades_delta_pct": 0.0,
      "bt_expectancy_r": null,
      "bespoke_expectancy_r": -0.196,
      "expectancy_r_delta": null,
      "bt_return_pct": null,
      "bespoke_return_pct": -10.83,
      "return_pct_delta": null,
      "bt_win_rate": null,
      "bespoke_win_rate": null,
      "win_rate_delta": null,
      "classification": "PASS",
      "notes": ["all tight tolerance bands hold"]
    }
  ],
  "strategy_evidence": false
}
```

The Markdown output adds a per-pair note section and the standard
"strategy_evidence: false" disclaimer.

## 4. Divergence labels

Reproduced from `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md` §7:

| label | semantics |
|---|---|
| `PASS` | every compared metric within tight tolerance |
| `TOLERABLE_DRIFT` | trade-count within wider band, metrics within wider band |
| `DATA_MISMATCH` | data sha / count drift (raised by the data adapter; the harness sees this indirectly via a runner failure) |
| `TIMESTAMP_ALIGNMENT_MISMATCH` | candles align to different session boundaries (similarly indirect) |
| `INDICATOR_MISMATCH` | indicator differs at warm-up |
| `SIGNAL_RULE_MISMATCH` | trade-count drift > wider band (>10%) |
| `FILL_MODEL_MISMATCH` | signal agrees, fill price / slippage differs |
| `STOP_OR_EXIT_ORDERING_MISMATCH` | same-bar SL/TP order priority differs |
| `SIZING_OR_PNL_MISMATCH` | trade-count agrees but R / PnL drifts > wider band |
| `UNSUPPORTED_BY_BACKTRADER` | rule cannot be expressed faithfully (e.g. NY-17 D1AGG) |
| `BLOCKED` | one side missing pair data |
| `UNKNOWN` | classification could not be determined |

The current `classify_pair(...)` decision ladder maps observed metric
deltas to these labels:

1. Either side missing → `BLOCKED`.
2. Tight bands all hold → `PASS`.
3. Trade-count within tight band but metric drift inside wider band → `TOLERABLE_DRIFT`.
4. Trade-count outside wider band → `SIGNAL_RULE_MISMATCH`.
5. Trade-count agrees but expectancy R / return % outside wider band → `SIZING_OR_PNL_MISMATCH`.
6. Otherwise → `UNKNOWN`.

`FILL_MODEL_MISMATCH`, `STOP_OR_EXIT_ORDERING_MISMATCH`,
`INDICATOR_MISMATCH`, `TIMESTAMP_ALIGNMENT_MISMATCH`,
`DATA_MISMATCH`, and `UNSUPPORTED_BY_BACKTRADER` are vocabulary the
human operator may assign by reading the per-pair notes — the harness
cannot, by trade counts and aggregate metrics alone, reliably
distinguish between them. Phase 6+ may extend the classifier to consume
the trade-by-trade JSONL and emit these finer labels; for now the
operator decides from context.

## 5. Tolerances

| dimension | tight (default) | wider |
|---|---|---|
| trade count Δ % | ±5% | ±10% |
| expectancy R | ±0.03 | ±0.06 |
| return % | ±0.5 pp | ±1.0 pp |
| win rate | ±0.05 | — |

The tight band mirrors the Lean mapping spec §8 expected tolerances.
The wider band is the "TOLERABLE_DRIFT" envelope.

CLI flags override the tight band per-run.

## 6. Tests (Phase 5)

`tests/unit/backtrader_lane/test_compare.py` — 16 tests covering:

- `classify_pair` on each documented branch (PASS, TOLERABLE_DRIFT,
  SIGNAL_RULE_MISMATCH, SIZING_OR_PNL_MISMATCH, BLOCKED), plus the
  "metrics None on both sides" case
- `compare` round-trip on tiny synthetic JSONs for PASS,
  SIGNAL_RULE_MISMATCH, and BLOCKED-when-pair-only-in-one-side
- `compare` raises `FileNotFoundError` on missing inputs
- `render_markdown` and `to_json_dict` include `strategy_evidence: false`
- `Tolerances` defaults
- `compare` does not mutate its input files
- the harness module imports nothing from `forex_bot`, broker, LEAN,
  or QuantConnect
- the CLI script end-to-end (writes JSON + Markdown, returns 0 on PASS)

Validation:

```bash
python -m pytest tests/unit/backtrader_lane/test_compare.py -v
# → 16 passed
```

Full backtrader_lane suite after Phase 5:

```bash
python -m pytest tests/unit/backtrader_lane -q
# → 75 passed (7 smoke + 15 adapter + 17 runner + 20 campaign-002 + 16 compare)
```

## 7. Safety

- The harness is **read-only**. It does not write to any bespoke
  reference JSON, the Lean parity config, or any campaign report.
- It cannot approve a strategy — there is no "approve" flag, no
  registry edit, no order submission.
- It cannot modify a verdict — every committed campaign report and
  every per-fold artefact is read elsewhere by the freeze gate; the
  harness does not touch them.
- The output `comparison_summary.json`'s `strategy_evidence: false`
  is asserted by tests.

`strategy_evidence: false`. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.
