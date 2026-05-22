# Lean Parity Execution Guide

**Date:** 2026-05-22 · **Branch:** `infra-execution-fidelity-001` · Phase 3
**Updated:** 2026-05-22 · `oanda-practice-readonly-001` Phase 7 — the
local real-OANDA H4 store is built and the CAMPAIGN_002 H4 export bundle
is produced (six pairs). See §2 and the export manifest.

Moves Lean parity from **design-only** to a **runnable local
preparation harness**. It builds on `docs/research/LEAN_PARITY_DESIGN.md`
(the design) and the `research/lean_parity/` skeleton.

> **Verification, not research.** Lean parity re-implements the
> CAMPAIGN_002 H4 `trend_following` baseline in an independent engine to
> check the bespoke backtest engine. CAMPAIGN_002 is already **REJECT**.
> A parity PASS corroborates the engine; a FAIL localizes an engine bug.
> Neither outcome approves a strategy. No QuantConnect cloud, no paid
> service, no live execution, no credentials.

## 1. Why CAMPAIGN_002 is the parity target

Every campaign verdict (CAMPAIGN_002–009, all REJECT) rests on one
**bespoke** engine (`src/forex_bot/backtesting/`). If that engine had a
systematic bug the verdicts could be wrong. Re-implementing one campaign
in QuantConnect Lean and comparing is how we check the instrument.

CAMPAIGN_002 H4 `trend_following` is the right first (and, for v1, only)
target:

- **Simplest strategy** — EMA(50/200) regime + Donchian(20) breakout +
  ATR(14) stop. No regime sub-models, no z-scores.
- **Already REJECT** — the stakes are low. A parity discrepancy cannot
  flip a "promote" decision, because there is no promotion.
- **Real OANDA data**, documented in
  `backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md`.
- Single-instrument (EUR_USD H4) is enough for a first run.

## 2. What can be run now

Two scripts are runnable today — no broker, no network, no paid service:

### `scripts/build_lean_parity_config.py` — runnable now

Reads the committed `configs/campaign_002_real_oanda.yaml` and writes
`research/lean_parity/lean_parity_config.json` — the **authoritative**
parameters for the parity run, extracted from the config rather than
copied by hand.

This matters: the prose table in `research/lean_parity/campaign_002_h4_spec.md`
was copied from the *frozen baseline* (`configs/paper.yaml`) and is
**wrong for CAMPAIGN_002** — it shows `atr_stop_multiple` 2.5 and
`max_bars_in_trade` 80. CAMPAIGN_002 actually used `atr_stop_multiple`
**2.0**, `max_bars_in_trade` **240**, and an empty `min_atr_pips`. The
generated JSON is the single source of truth; trust it over any prose.

```bash
python scripts/build_lean_parity_config.py
```

### `scripts/export_lean_parity_data.py` — produced (Phase 7)

Reads completed OANDA H4 bid/ask candles from the local store and writes
a Lean custom-data CSV plus a provenance sidecar (see
`research/lean_parity/lean_h4_export_format.md`). It exports **real data
only** — it refuses any candle whose source is not `oanda-*`, reads only
the local store (no OANDA call), and fabricates nothing.

The export bundle lives in `research/lean_parity/exports/campaign_002_h4/`
(`EXPORT_MANIFEST.md` plus the candle CSVs and provenance JSONs). The
candle CSVs are bulky market data and are gitignored
(`research/lean_parity/exports/**/*.csv`); the provenance JSONs and the
manifest are committed.

As of `oanda-practice-readonly-001` Phase 7 the export **has been
produced** — a full export of all six pairs in the local H4 store
(EUR_USD, GBP_USD, USD_JPY, AUD_USD, USD_CAD, USD_CHF), full window
2020-01-01 → 2026-05-19, ~9,931 candles each. NZD_USD (the 7th
CAMPAIGN_002 instrument) is not in the six-pair store and was not
exported.

Exact commands — build the store, then export all six CAMPAIGN_002 H4
pairs into the bundle:

```bash
# 1. Build the local real-OANDA H4 store (needs practice credentials):
set -a && source .env && set +a
python scripts/rehydrate_oanda_h4_store.py

# 2. Export each CAMPAIGN_002 H4 pair (read-only — local store only):
for inst in EUR_USD GBP_USD USD_JPY AUD_USD USD_CAD USD_CHF; do
  python scripts/export_lean_parity_data.py \
      --db data/oanda_h4_research.sqlite3 --instrument "$inst" \
      --from 2020-01-01 --to 2026-05-20
done
```

Outputs (in `research/lean_parity/exports/campaign_002_h4/`), per pair:
`<INST>_H4_lean.csv` (the candles, gitignored) and
`<INST>_H4_lean.provenance.json` (`data_sha256`,
`campaign_002_data_request_hash`, counts, window — committed).

## 3. What remains manual (and why)

| step | why it is manual |
|---|---|
| `pip install lean` + Docker | Installing a toolchain is a deliberate human step; this sprint does not install Lean. |
| `lean init` workspace | The Lean workspace lives outside this repo's package tree. |
| Writing the Lean algorithm | It depends on Lean's `AlgorithmImports` runtime, not installed here. Skeleton: `research/lean_parity/campaign_002_h4_spec.md`. |
| Running `lean backtest` | Local Docker backtest — a human-initiated run. |
| Comparing results | Judge the Lean output against the committed CAMPAIGN_002 artifacts using §4. |

Lean's local backtester is free (open-source `lean` CLI + Docker). No
paid QuantConnect tier and no cloud compute are needed for the local
parity backtest. This sprint deliberately does **not** install the
toolchain or run a backtest — that is the documented manual boundary.

### Exact local Lean command (when Lean is installed)

Once the export exists and a Lean algorithm has been written from the
skeleton in `research/lean_parity/campaign_002_h4_spec.md`:

```bash
# In the Lean workspace (created by `lean init`, outside this repo):
lean backtest "TrendFollowingC002Parity"
```

Inputs: the exported `EUR_USD_H4_lean.csv` consumed as Lean custom data,
preserving the 17:00-NY-aligned open timestamps. Outputs: Lean's trade
list and statistics, compared against the committed CAMPAIGN_002
artifacts using §4. Whether Lean is installed is checked by
`docs/research/LEAN_PARITY_LOCAL_STATUS.md`.

### Current status (no data blocker)

The prior data-availability blocker is **cleared**. The local real-OANDA
H4 store (`data/oanda_h4_research.sqlite3`) was built in
`oanda-practice-readonly-001` Phase 4 and the CAMPAIGN_002 H4 export
bundle was produced in Phase 7. The store and the candle CSVs remain
gitignored and are never committed; the provenance JSONs and the export
manifest are committed. What still requires a deliberate human step is
installing the Lean toolchain and running the Lean backtest — see §3 and
`docs/research/LEAN_PARITY_LOCAL_STATUS.md`.

## 4. Comparison metrics that matter

Compare the Lean run against the committed CAMPAIGN_002 artifacts.
Full mapping and a tickable list: `research/lean_parity/CAMPAIGN_002_PARITY_CHECKLIST.md`.

| quantity | tolerance | why |
|---|---|---|
| trade entry bar | same bar, ≥ 95% of trades | the core check — same signals |
| entry / exit price | within ~1 pip | fill-model differences are expected |
| trade count | within ±5% | aggregate signal agreement |
| total return | within ±0.5 pp | aggregate outcome agreement |
| expectancy (R) | within ±0.03 R | per-trade outcome agreement |
| verdict | both **REJECT** | the engines must agree on the conclusion |

**Excluded from parity** (documented divergences, not failures):
financing (unmodeled in both); the bespoke `RiskEngine`'s spread /
session / correlation / margin filters (bespoke — compare only the
bespoke engine's *accepted* trades). Rejection counts will not match,
by design.

**Fill timing:** CAMPAIGN_002 predates the fill-timing model
(`docs/research/FILL_TIMING_MODEL.md`), so parity uses
`signal_bar_close`. A `next_bar_open` parity would be a separate,
later comparison and is out of scope here.

## 5. Pass / fail

- **PASS** — ≥ 95% of entries on the same bar, all aggregates inside
  tolerance, both engines REJECT. The bespoke engine is corroborated.
- **FAIL** — systematic divergence outside tolerance. Localize it
  (indicator seeding, fill model, stop precedence, timestamp alignment),
  treat it as a bespoke-engine bug, fix, and re-run.
- A parity result **never** approves a strategy. It validates the
  measurement instrument only.

## 6. Files

| path | role |
|---|---|
| `docs/research/LEAN_PARITY_DESIGN.md` | the design and rationale |
| `docs/research/LEAN_PARITY_EXECUTION_GUIDE.md` | this guide |
| `research/lean_parity/README.md` | skeleton index + install steps |
| `research/lean_parity/campaign_002_h4_spec.md` | strategy spec + Lean algorithm skeleton |
| `research/lean_parity/lean_h4_export_format.md` | the export CSV format |
| `research/lean_parity/CAMPAIGN_002_PARITY_CHECKLIST.md` | tickable mapping + tolerance checklist |
| `research/lean_parity/lean_parity_config.json` | generated authoritative parameters |
| `research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md` | the export bundle manifest (status, mapping, assumptions, tolerances) |
| `scripts/build_lean_parity_config.py` | generates the parameter JSON |
| `scripts/export_lean_parity_data.py` | exports real H4 candles to Lean CSV |
| `scripts/rehydrate_oanda_h4_store.py` | builds the local real-OANDA H4 store the export reads |
| `docs/research/OANDA_H4_DATA_REHYDRATION.md` | how to build / verify the H4 store |
| `src/forex_bot/lean/parity_notes.md` | where to record every divergence |
