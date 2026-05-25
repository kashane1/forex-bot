"""Phase 1 smoke tests: prove Backtrader can run locally with no broker access.

These tests are the only proof we need that the canonical `backtrader`
package is usable from the repo's Python 3.12 environment without touching
OANDA, LEAN, credentials, or the live broker.

If `backtrader` is not installed the entire module is skipped via the
top-level `pytest.importorskip`; the rest of the repo's test suite is
unaffected.

`strategy_evidence: false`. These tests verify infrastructure only.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("backtrader")

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.smoke import (  # noqa: E402
    bars_to_pandas,
    deterministic_h4_bars,
    run_noop_cerebro,
    run_oneshot_cerebro,
)


def test_backtrader_imports_under_filterwarnings_error() -> None:
    """The repo's pytest config sets `filterwarnings = ["error", ...]`. An
    `import backtrader` that triggered a DeprecationWarning or similar
    would already have failed the whole suite — this test makes the check
    explicit so future package updates surface a clean signal."""

    import backtrader as bt

    assert bt.__version__, "backtrader version string must be non-empty"


def test_deterministic_h4_bars_are_pure() -> None:
    a = deterministic_h4_bars(n=20)
    b = deterministic_h4_bars(n=20)
    assert len(a) == 20
    assert all(x == y for x, y in zip(a, b, strict=True))
    # Monotonically increasing timestamps spaced exactly 4h apart.
    for prev, curr in zip(a, a[1:], strict=False):
        assert (curr.timestamp - prev.timestamp).total_seconds() == 4 * 3600


def test_bars_to_pandas_has_expected_columns() -> None:
    df = bars_to_pandas(deterministic_h4_bars(n=5))
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 5
    # OHLC invariants on every row.
    for _, row in df.iterrows():
        assert row["low"] <= row["open"] <= row["high"]
        assert row["low"] <= row["close"] <= row["high"]


def test_noop_cerebro_runs_without_warnings_or_errors() -> None:
    """A no-op strategy must execute next() over every bar and Cerebro
    must return exactly one strategy instance."""

    bars = deterministic_h4_bars(n=50)
    assert run_noop_cerebro(bars) == 1


def test_oneshot_cerebro_emits_exactly_one_closed_trade() -> None:
    """The deterministic one-shot strategy buys at bar 5 and sells at bar
    10, so we must see exactly one closed trade with positive PnL on the
    monotonically-rising price sequence."""

    bars = deterministic_h4_bars(n=30, base_price=1.10000, step=0.00010)
    result = run_oneshot_cerebro(bars)
    assert result["closed_trades"] == 1
    # Rising-price linear sequence + long 1000 units between bars 5 and 10
    # → final cash strictly greater than starting cash and net PnL > 0.
    assert result["final_cash"] > 10_000.0
    assert result["net_pnl"] > 0.0


def _import_lines(path: Path) -> list[str]:
    """Return lines that are actual Python imports (not docstrings/comments).

    Strips comment text and only returns lines whose stripped form starts
    with `import` or `from`. Conservative on purpose — we want zero false
    positives from prose that names the forbidden modules.
    """

    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("import ") or line.startswith("from "):
            out.append(line)
    return out


_FORBIDDEN_IMPORT_SUBSTRINGS = (
    "backtrader.brokers.oandabroker",
    "backtrader.stores.oandastore",
    "backtrader.feeds.oanda",
    "quantconnect",
    "from lean ",
    "import lean",
)


def test_smoke_module_has_no_forbidden_imports() -> None:
    import research.backtrader_lane.smoke as smoke_mod

    for line in _import_lines(Path(smoke_mod.__file__)):
        for needle in _FORBIDDEN_IMPORT_SUBSTRINGS:
            assert needle not in line, f"forbidden import in smoke.py: {line}"


def test_backtrader_lane_package_has_no_forbidden_imports() -> None:
    """Greppable safety net across the whole backtrader_lane package."""

    pkg_root = ROOT / "research" / "backtrader_lane"
    for path in pkg_root.rglob("*.py"):
        for line in _import_lines(path):
            for needle in _FORBIDDEN_IMPORT_SUBSTRINGS:
                assert needle not in line, f"forbidden import in {path}: {line}"
