# INFRA — Backtrader Secondary Lane 001 — Plan

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Sprint kind:** infrastructure / parity (NOT a strategy campaign)
**`strategy_evidence: false`**

A secondary, **local-only** backtesting/verification lane built on top
of [Backtrader](https://www.backtrader.com/) (the original `backtrader`
Python package), running alongside — never replacing — the bespoke
backtest engine in `src/forex_bot/backtesting/`. The lane ingests the
same exported H4 research candles already used by the bespoke engine,
runs the frozen campaign rules where feasible, emits compact comparable
trade/metrics artifacts, and classifies divergence from the bespoke
engine.

## 0. Hard non-goals (binding)

This sprint **must not**:

1. Approve any strategy. `configs/approved_strategies.yaml` stays
   `approved: []`. No strategy name is added under any circumstance.
2. Mutate any existing campaign verdict. CAMPAIGN_002, CAMPAIGN_010,
   CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain REJECT / null /
   research-only exactly as currently documented. CAMPAIGN_014 remains
   scaffold-only unless evidence already exists in the repo.
3. Tune any strategy parameter, rule, or threshold. Frozen rules are
   ported as-is; mismatches are documented, not "fixed" via tuning.
4. Touch the bespoke engine in `src/forex_bot/backtesting/`. If the
   Backtrader lane disagrees with bespoke, **the disagreement is
   recorded** — neither side is "made to match" the other.
5. Create, submit, modify, or close any broker order. The lane is a
   read-only comparison utility.
6. Use any OANDA API, OANDA endpoint, or OANDA credentials. No network
   calls, no `httpx`/`requests` to broker endpoints, no environment
   credentials read or printed.
7. Use Backtrader's old OANDA / live-broker integration paths. Imports
   from `backtrader.stores.oandastore`, `backtrader.brokers.oandabroker`,
   `backtrader.feeds.oanda` and any live-broker module are forbidden.
   Only the local `Cerebro` + `feeds.GenericCSVData` / `feeds.PandasData`
   surface is used.
8. Use QuantConnect / LEAN. The LEAN path is RETIRED for this project
   (`docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`); no LEAN
   imports, no `lean` CLI invocations, no QuantConnect cloud.
9. Use any cloud backtest service of any kind.
10. Change paper/demo/live gates or any safety guard. The freeze
    checker (`scripts/check_research_freeze.py`) must remain green.
11. Replace the bespoke engine. The bespoke engine remains the
    canonical runtime for all campaigns and the canonical source of
    every committed verdict; the Backtrader lane is a *secondary*
    verifier, like `research/parity_verifier/` is.

## 1. Motivation

The repo already has an internal independent-engine verifier under
`research/parity_verifier/` (free / local, no broker, no QuantConnect),
which was the replacement direction once LEAN was retired
(`docs/research/QUANTCONNECT_LEAN_RETIREMENT_DECISION.md`). That
verifier is **capability-locked to CAMPAIGN_002** and is itself
implemented in this repo (i.e. authored by the same team that authored
the bespoke engine).

A third, **fully external**, mature, widely-used event-driven
backtesting engine — one we did not write — adds a second independent
axis of disagreement: not just "two implementations of the same spec"
but "two implementations + a third-party event loop". If Backtrader
reproduces a bespoke metric within tolerance, that is stronger
evidence that the bespoke engine's mechanics are not silently doing
something idiosyncratic. If it diverges, the divergence is itself a
classified, named artifact (see §6 below) — never a silent change to a
verdict.

This is the same shape as `infra-free-local-parity-verifier-*` and
`infra-lean-parity-*` were intended to be, before LEAN was retired:
verification infrastructure that **cannot approve a strategy** and is
recorded in `docs/research/EVIDENCE_INDEX.md` under "Diagnostic & parity
artifacts (NOT strategy evidence)".

## 2. Why Backtrader (first target)

| factor | rationale |
|---|---|
| local-only | `pip install backtrader` → `Cerebro` runs entirely offline; no broker, no cloud, no auth |
| event-driven | matches the bespoke engine's bar-by-bar model; needed for honest H4 trade-by-trade comparison |
| mature & widely used | well-documented, MIT-licensed, used in many published parity studies |
| Python 3.12 | the repo's Python; expected to work but verified in Phase 1 |
| pluggable feeds | `GenericCSVData` and `PandasData` accept the H4 candles already exported by `scripts/export_lean_parity_data.py` |
| pluggable analyzers | `TradeAnalyzer`, `SharpeRatio`, `DrawDown`, `Returns` cover the comparison metrics we need |
| commission/slippage configurable | `CommInfoBase` + `set_slippage_perc` / `set_slippage_fixed` are crude but adequate for the H4 cost model |

Limitations are explicit and documented up-front (§4 below).

## 3. Why not other tools (yet)

- **`backtrader-next`** — a community fork. Considered as a fallback if
  the canonical `backtrader` package will not install or import cleanly
  under Python 3.12. Phase 1 decides this.
- **NautilusTrader** — high-performance Rust-backed engine; intended for
  high-frequency / multi-asset / live-broker integration. Heavier
  dependency footprint than needed for an H4 parity check. Considered
  only as a fallback in the Phase 1 decision memo if both Backtrader and
  `backtrader-next` fail.
- **vectorbt, zipline-reloaded** — out of scope; vectorbt is
  vectorized/lookahead-prone and zipline is daily-bar oriented.

## 4. Known Backtrader limitations vs the bespoke engine

These are documented as **expected approximations**, not bugs. Any
parity comparison must flag them in advance.

1. **Bid/ask spread.** Backtrader's stock fill model is single-price
   (close/open) + commission/slippage. The bespoke engine's H4 fills
   use a bid/ask-aware rule (long enters at ask, short at bid, plus
   spread-multiplier slippage). The Backtrader lane will approximate
   this via:
   - feed the Backtrader engine the **mid** OHLC,
   - apply slippage = `fixed_slippage_pips + (spread/2) *
     spread_slippage_multiplier` per side via `set_slippage_fixed`,
   - or, if a more faithful per-bar slippage is needed, an adjusted
     per-bar mid-with-half-spread tweak (Phase 2 decides).
   The choice and its expected effect on parity error are documented.
2. **`signal_bar_close` vs `next_bar_open`.** Backtrader's default is
   `next_bar_open` (a `cheat_on_close=True` switch exists to flip).
   CAMPAIGN_002 and the campaigns the lane will target ran in
   `signal_bar_close`. The lane uses `cheat_on_close=True` to match.
   See `docs/research/FILL_TIMING_MODEL.md`.
3. **Gap-through fills.** The bespoke engine has an opt-in
   `gap_through` policy (`docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`).
   The lane defaults to bespoke's default (`none`) — never `gap_through`
   — to keep comparison narrowly scoped. Same-bar SL+TP collisions are
   tracked separately as `ambiguous_exit_count` on the bespoke side;
   Backtrader's order-priority handling is its own and may produce a
   different number — this is a *FILL_MODEL_MISMATCH* candidate, not a
   bug.
4. **Position sizing.** Bespoke uses risk-fraction sizing via
   `RiskEngine`. Backtrader has its own `Sizer` infrastructure; we
   subclass `bt.Sizer` to compute risk-fraction sizing identically.
   Differences in rounding to whole units / lot sizes may produce
   sub-bps drift — recorded.
5. **Financing / swap.** Neither engine models financing in PnL.
   `ESTIMATED + conservative stress` financing overlay is bespoke-only
   and **out of scope** for the Backtrader lane; the lane reports
   "financing: NOT MODELED — comparison runs pre-financing only".
6. **Indicator definitions.** Backtrader's `ATR` / `EMA` use Wilder's
   smoothing and standard EMA respectively, matching the bespoke
   definitions (`forex_bot.backtesting.indicators`). Donchian: bespoke
   uses prior-bars-only; Backtrader's `Highest`/`Lowest` over a window
   includes the current bar — the lane uses an explicit
   `bt.indicators.Highest(self.data.high(-1), period=N)` form to
   replicate prior-bars-only. This is documented per adapter.
7. **Time-stop / max-bars-in-trade.** Backtrader does not have a
   first-class "close after N bars" — the lane implements it inside
   `next()` by tracking bar count since entry. This is exact, just
   non-default.
8. **RiskEngine gates.** Bespoke runs the production `RiskEngine`
   (`forex_bot.risk`) gates (spread, session, sizing, exposure, margin)
   even in backtest. The Backtrader lane does **not** replicate these
   gates by default — it's a strategy + mechanics parity, not a
   RiskEngine parity. (For CAMPAIGN_002 we have a `risk_engine=None`
   bespoke reference (`research/lean_parity/campaign_002_h4_bespoke_reference.json`,
   1,647 trades) that is the apples-to-apples comparison target for
   strategy+mechanics-only ports.)
9. **Multi-pair portfolio.** Backtrader supports multi-data
   `Cerebro.adddata`; each campaign decides whether to run pairs
   independently (matches bespoke's per-pair model) or together (would
   share equity in the BT broker — drifts from bespoke).
   **Default: per-pair independent runs**, matching the bespoke
   convention and the published campaign-002 / -011 reports.

## 5. Data source

**Single source of truth for candles in this sprint:**
`research/lean_parity/exports/campaign_002_h4/*.csv` (gitignored bulk
data), regenerable via:

```bash
python scripts/export_lean_parity_data.py \
    --config configs/campaign_002_real_oanda.yaml \
    --output research/lean_parity/exports/campaign_002_h4/
```

These are the same real-OANDA-practice H4 candles CAMPAIGN_002 used
(provenance JSONs are committed; `data_sha256` and
`campaign_002_data_request_hash` are checked into provenance files).
The Backtrader lane refuses to run if:

- a requested instrument's CSV is missing locally,
- a requested instrument's CSV `sha256` does not match the committed
  provenance JSON, **or**
- any instrument's CSV contains incomplete candles.

No OANDA endpoint is contacted. No new data is fetched.

For campaigns that did not use the seven-pair H4 store (e.g. D1 cases),
the lane reports BLOCKED with a clear "data not available for
Backtrader lane" message.

## 6. Campaigns this sprint touches

This sprint **does not change any campaign verdict**. It only adds a
secondary lane that:

1. **Reads** existing bespoke reference artifacts.
2. **Runs** a Backtrader port of frozen campaign rules.
3. **Compares** Backtrader output to bespoke output.
4. **Classifies** divergence under one of the labels in §7.

### Candidate first campaign (Phase 4 decides; not chosen yet)

| campaign | why it might be first | why it might not |
|---|---|---|
| CAMPAIGN_002 (trend_following baseline) | best-documented; has explicit Lean parity spec (`docs/research/CAMPAIGN_002_LEAN_MAPPING_SPEC.md`); two bespoke references (with and without RiskEngine); the seven-pair CSV export is ready; the existing `research/parity_verifier/` was built for this exact target — easy to cross-check | most complex strategy of the candidate set (EMA + Donchian + ATR-stop + trailing); higher chance of FILL/INDICATOR/SIGNAL mismatch sub-types to chase |
| CAMPAIGN_011 (random_entry_anchor — null model) | deterministic by seed; minimal strategy logic (coin flip + ATR stop + max-bars); makes data-loop / fill-model / sizing isolatable from indicator / rule complexity; lowest implementation cost | requires reproducing the bespoke seed-derived per-bar entry coin flip *exactly* across two engines — that's a `numpy.random.default_rng(seed)` per-pair contract; if bit-exact reproduction fails, this becomes a SIGNAL_RULE_MISMATCH chase that obscures the engine baseline |

Both are viable. The Phase 4 file
(`docs/research/BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md`) will state the
choice and justify it. The default lean is **CAMPAIGN_002 (no-RiskEngine
reference, 1,647 trades)**, because it has the existing Lean mapping
spec and bespoke reference JSON; the random-entry anchor's per-bar
coin-flip reproducibility is a separate, downstream check.

### Possible second campaign (Phase 7 decides)

If first campaign succeeds, the second exercises a different failure
mode:

- CAMPAIGN_011 if first was CAMPAIGN_002 (test deterministic null);
- CAMPAIGN_010 if multi-session entry behaviour is the question;
- CAMPAIGN_012 if D1AGG aggregation can be represented in Backtrader
  (probably not — Backtrader's resampling is timeframe-coupled and the
  bespoke `aggregate_h4_to_d1.py` uses NY-17 alignment that BT does not
  natively express).

CAMPAIGN_006 (D1) is explicitly out — it is REJECT-NO-VALID-RESULT in
the bespoke engine for D1-specific infrastructure reasons and would not
be a meaningful comparison.

CAMPAIGN_013 (cross-pair currency strength) requires synchronised
multi-pair signals; Backtrader can express it but it adds an extra
adapter complexity that is probably not worth tackling in this sprint.

## 7. Divergence classification (binding labels)

Every comparison run emits exactly one of these labels:

| label | meaning |
|---|---|
| `PASS` | every compared metric within tolerance |
| `TOLERABLE_DRIFT` | within a wider tolerance band; expected from rounding / sizing whole-units |
| `DATA_MISMATCH` | one engine saw different candles (sha256 / count mismatch) |
| `TIMESTAMP_ALIGNMENT_MISMATCH` | candles align to different session boundaries |
| `INDICATOR_MISMATCH` | indicator output differs at warm-up / smoothing |
| `SIGNAL_RULE_MISMATCH` | identical inputs, different signal — rule port bug or rule ambiguity |
| `FILL_MODEL_MISMATCH` | signal agrees, fill price / slippage / order priority differs |
| `STOP_OR_EXIT_ORDERING_MISMATCH` | same-bar SL+TP order priority differs |
| `SIZING_OR_PNL_MISMATCH` | trade count + entry/exit agrees, R / PnL differs |
| `UNSUPPORTED_BY_BACKTRADER` | rule cannot be expressed faithfully in Backtrader (e.g. NY-17 D1AGG) |
| `UNKNOWN` | catch-all when classification cannot be determined |

The comparison harness (Phase 5) emits one label per campaign plus a
per-pair table with finer-grained labels.

## 8. Safety invariants

Enforced for every commit on this branch:

1. `configs/approved_strategies.yaml` is byte-identical to `main`.
2. `scripts/check_research_freeze.py` exits 0.
3. `scripts/validate_research_archive.py` exits 0.
4. `scripts/scan_artifacts_for_secrets.py` exits 0.
5. No `.env`, no `data/*.sqlite3`, no `research/lean_parity/exports/**/*.csv`,
   no `research/backtrader_lane/results/**` raw outputs are committed.
6. No file under `src/forex_bot/backtesting/` is touched.
7. No new approved-strategy entry exists anywhere.
8. No call to `OANDARestClient` / `httpx` against broker endpoints
   exists in any Backtrader-lane file (greppable: `oanda-practice`,
   `api-fxpractice`, `httpx`).
9. `backtrader.brokers.oandabroker`, `backtrader.feeds.oanda` and
   `backtrader.stores.oandastore` are not imported anywhere.
10. `lean`, `quantconnect`, `QuantConnect` are not imported anywhere in
    new files.

## 9. Validation commands

Per-phase and final:

```bash
python -m pytest -x -q
ruff check src tests scripts
ruff check research          # informational; pre-existing LEAN-retired files surface RUF100
python scripts/validate_research_archive.py
python scripts/check_research_freeze.py
python scripts/scan_artifacts_for_secrets.py
```

Backtrader-lane-specific (added in Phase 3):

```bash
python -m pytest -x -q tests/unit/backtrader_lane
python scripts/run_backtrader_parity.py --campaign <id> --dry-run
```

## 10. Expected output files

```
docs/research/
  INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md           # this doc (Phase 0)
  INFRA_BACKTRADER_SECONDARY_LANE_001_SUMMARY.md        # Phase 8
  BACKTRADER_INSTALL_AND_SMOKE_RESULT.md                # Phase 1
  BACKTRADER_TOOL_BLOCKED_DECISION.md                   # Phase 1 only if blocked
  BACKTRADER_DATA_ADAPTER_SPEC.md                       # Phase 2
  BACKTRADER_RUNNER_CONTRACT.md                         # Phase 3
  BACKTRADER_FIRST_CAMPAIGN_ADAPTER.md                  # Phase 4
  BACKTRADER_PARITY_<CAMPAIGN>_COMPARISON.md            # Phase 5/6 per campaign
  BACKTRADER_PARITY_FIRST_RESULT.md                     # Phase 6
  BACKTRADER_PARITY_SECOND_RESULT.md                    # Phase 7 (if not blocked)
  BACKTRADER_SECOND_CAMPAIGN_BLOCKED.md                 # Phase 7 (if blocked)

research/backtrader_lane/                               # NEW
  __init__.py
  README.md
  data_adapter.py
  runner.py
  strategies/
    __init__.py
    campaign_002_trend_following.py    # (or other first campaign)
  tests fixtures (small) checked in under tests/

scripts/
  run_backtrader_parity.py             # NEW
  compare_backtrader_parity.py         # NEW

tests/unit/backtrader_lane/            # NEW
  test_data_adapter.py
  test_runner.py
  test_strategies.py
  test_compare.py
  fixtures/                            # tiny deterministic CSVs

research/backtrader_lane/results/      # gitignored
```

## 11. Fallback plan if Backtrader install/import fails

Phase 1 will:

1. Attempt `pip install backtrader` (and any compatibility extras) into
   the repo's existing virtualenv style.
2. Run a one-line `python -c "import backtrader"` smoke import.
3. If either step fails, write
   `docs/research/BACKTRADER_TOOL_BLOCKED_DECISION.md` containing:
   - the exact pip output,
   - the exact Python traceback,
   - a comparison memo of `backtrader-next` vs NautilusTrader (and a
     light note on vectorbt for completeness),
   - a recommended next infra branch,
   - **explicit refusal to silently switch tools** — the user / next
     sprint chooses the fallback.
4. Phases 2 through 7 are then either reduced to "blocked, see decision
   memo" or replaced by adapter equivalents in the chosen fallback —
   not in this sprint.

The remaining safety invariants still hold either way: no approval, no
verdict change, no broker.

## 12. Why this sprint exists at all

The repo is in a research freeze. A frozen research platform's value
*is* the strength of its evidence. Adding an independent third-party
engine to the comparison set strengthens (or weakens, honestly!) the
existing evidence by giving each REJECT verdict a second
implementation's vote on the underlying mechanics. It does not change
any verdict; it raises (or lowers) confidence in the verdicts already
recorded. That is the only thing this sprint does.

**Current status, unchanged:** no strategy approved. Paper / demo /
live blocked. Research freeze intact. Bespoke engine canonical.
