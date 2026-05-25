# Backtrader — Install + Smoke Test Result

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-001`
**Phase:** 1 of `INFRA_BACKTRADER_SECONDARY_LANE_001_PLAN.md`
**`strategy_evidence: false`** — infrastructure smoke test, not a campaign.

## Verdict

**PASS.** The canonical [Backtrader](https://www.backtrader.com/)
Python package installs cleanly, imports cleanly under
`warnings.simplefilter('error')` (the repo's pytest default), and runs
both a no-op and a one-shot deterministic strategy against a tiny
pandas-built H4 fixture without raising. No broker module is imported.
No network call is made. No credential is read.

The secondary verification lane proceeds to Phase 2 (data adapter).

## Environment

| field | value |
|---|---|
| repo | `forex-bot` (research-frozen) |
| branch | `infra-backtrader-secondary-lane-001` |
| Python | `3.12.3` (`/Library/Frameworks/Python.framework/Versions/3.12/bin/python3`) |
| platform | macOS Darwin 25.3.0 |
| install command | `pip install backtrader` |
| package | `backtrader` |
| installed version | **`1.9.78.123`** (from PyPI, MIT licence) |
| module path | `/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/backtrader/__init__.py` |
| optional-extras entry | `pyproject.toml` → `[project.optional-dependencies]` → `backtrader-lane = ["backtrader>=1.9.78,<2.0"]` |

The pin floor is the version we successfully tested; the cap stays
below the (currently non-existent) `2.0` major to avoid breaking
changes if the package ever ships one.

## Install command (verbatim)

```bash
pip install backtrader
```

Output excerpt:

```
Collecting backtrader
  Using cached backtrader-1.9.78.123-py2.py3-none-any.whl.metadata (6.8 kB)
Using cached backtrader-1.9.78.123-py2.py3-none-any.whl (419 kB)
Installing collected packages: backtrader
Successfully installed backtrader-1.9.78.123
```

No build step (pure-Python wheel). No native compilation. No additional
transitive dependency conflicts surfaced.

Project-level integration:

```bash
pip install -e .[backtrader-lane]      # installs the optional extra
pip install -e .[dev,research,backtrader-lane]   # if running tests too
```

## Import status

```bash
python -c "import backtrader; print(backtrader.__version__)"
# → 1.9.78.123
```

Under the repo's pytest filter (`filterwarnings = ["error", ...]`),
the import raises **no** warning:

```python
import warnings
warnings.simplefilter("error")
import backtrader as bt  # no DeprecationWarning, no SyntaxWarning
```

## Smoke-test commands

```bash
python -m pytest tests/unit/backtrader_lane/test_smoke.py -v
```

The smoke module is `research/backtrader_lane/smoke.py`; the test file
is `tests/unit/backtrader_lane/test_smoke.py`. Tests:

| test | what it proves |
|---|---|
| `test_backtrader_imports_under_filterwarnings_error` | `import backtrader` triggers no warning that the repo's pytest config would escalate |
| `test_deterministic_h4_bars_are_pure` | the smoke fixture is bit-reproducible (pure function, no clock, no RNG) |
| `test_bars_to_pandas_has_expected_columns` | the pandas → Backtrader feed shape is OHLCV |
| `test_noop_cerebro_runs_without_warnings_or_errors` | Cerebro instantiates a strategy, loads a PandasData feed, runs `next()` over 50 bars, returns one strategy result |
| `test_oneshot_cerebro_emits_exactly_one_closed_trade` | a deterministic one-shot strategy (enter bar 5, exit bar 10) produces exactly one closed trade on a rising-price sequence and a positive net PnL |
| `test_smoke_module_has_no_forbidden_imports` | the smoke module imports no `backtrader.brokers.oandabroker` / `.stores.oandastore` / `.feeds.oanda` / QuantConnect / LEAN |
| `test_backtrader_lane_package_has_no_forbidden_imports` | greppable safety net across the whole `research/backtrader_lane/` tree |

Result:

```
============================== 7 passed in 0.11s ===============================
```

## What was deliberately *not* exercised

- No live-broker connection. `backtrader.brokers.oandabroker`,
  `backtrader.stores.oandastore`, and `backtrader.feeds.oanda` are
  **not imported anywhere** (tested twice — module-level scan and
  package-level scan).
- No QuantConnect / LEAN. No `lean` CLI invocation.
- No network call. No credential read.
- No order on a real account of any kind.

## Known compatibility notes

- Backtrader uses `collections.abc`-compatible imports in 1.9.78.x —
  no `DeprecationWarning` under Python 3.12 in our smoke runs.
- `backtrader.feeds.PandasData` correctly accepts an OHLCV-named
  DataFrame indexed by `datetime`.
- `Cerebro.broker.setcash` and `cerebro.run()` work without side
  effects on the global RNG.
- The `TradeAnalyzer.get_analysis()` `.total.closed` attribute is
  available; we also wrap a small custom `_TradeRecorder` analyzer to
  capture per-trade PnL because `TradeAnalyzer` only exposes aggregate
  totals in some 1.9.78.x sub-revisions.

No compatibility blocker surfaced. No fallback to `backtrader-next` or
NautilusTrader is required. The
`BACKTRADER_TOOL_BLOCKED_DECISION.md` fallback memo was therefore
**not** created.

## Statement of safety

This phase touched only:

- `pyproject.toml` — added the optional `backtrader-lane` extra,
- `research/backtrader_lane/__init__.py` — package marker,
- `research/backtrader_lane/smoke.py` — pure smoke helpers,
- `research/backtrader_lane/strategies/__init__.py` — empty marker,
- `tests/unit/backtrader_lane/__init__.py` — empty marker,
- `tests/unit/backtrader_lane/test_smoke.py` — smoke tests,
- `docs/research/BACKTRADER_INSTALL_AND_SMOKE_RESULT.md` — this doc.

`configs/approved_strategies.yaml` is **untouched** and remains
`approved: []`. No file under `src/forex_bot/backtesting/` is touched.
`scripts/check_research_freeze.py`, `scripts/validate_research_archive.py`,
and `scripts/scan_artifacts_for_secrets.py` all PASS after this phase.

Backtrader is treated strictly as a **local backtesting/verifier tool**.
It is not, and must not become, the canonical runtime. It cannot
approve a strategy. CAMPAIGN_002, CAMPAIGN_010, CAMPAIGN_011,
CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/research-only.
CAMPAIGN_014 remains scaffold-only. Paper / demo / live remain blocked.
