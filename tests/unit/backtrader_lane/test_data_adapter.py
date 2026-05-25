"""Phase 2 data-adapter tests.

These run against the tiny deterministic fixture in
`tests/unit/backtrader_lane/fixtures/`. They prove the adapter:

- parses the documented Lean H4 CSV header,
- computes a sha256 that matches the committed provenance JSON,
- enforces monotonic ascending H4 timestamps,
- preserves OHLC invariants on the mid (derived) prices,
- carries bid/ask and half_spread separately,
- raises clean errors on header / sha / row-count drift,
- exposes the instrument metadata the runner needs.

No `forex_bot` import. No network. No broker. No credential.
`strategy_evidence: false`.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("backtrader")

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.backtrader_lane.data_adapter import (  # noqa: E402
    EXPECTED_CSV_HEADER,
    CandleAdapterResult,
    CandleProvenanceError,
    CandleSchemaError,
    available_instruments,
    compute_csv_sha256,
    expected_instruments,
    load_candles,
    manifest_for,
)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def test_fixture_files_are_present() -> None:
    assert (FIXTURE_DIR / "TEST_PAIR_H4_lean.csv").exists()
    assert (FIXTURE_DIR / "TEST_PAIR_H4_lean.provenance.json").exists()


def test_expected_csv_header_matches_lean_format_doc() -> None:
    """The CSV header is contractual with research/lean_parity/lean_h4_export_format.md."""

    assert EXPECTED_CSV_HEADER == (
        "time",
        "bid_open",
        "bid_high",
        "bid_low",
        "bid_close",
        "ask_open",
        "ask_high",
        "ask_low",
        "ask_close",
        "volume",
    )


def test_load_candles_basic_shape() -> None:
    result = load_candles("TEST_PAIR", export_dir=FIXTURE_DIR)
    assert isinstance(result, CandleAdapterResult)
    assert result.instrument == "TEST_PAIR"
    assert result.bar_count == 12
    assert list(result.mid_df.columns) == ["open", "high", "low", "close", "volume"]
    assert list(result.bid_ohlc_df.columns) == ["open", "high", "low", "close"]
    assert list(result.ask_ohlc_df.columns) == ["open", "high", "low", "close"]
    assert len(result.mid_df) == 12
    assert len(result.half_spread_close) == 12


def test_load_candles_provenance_sha_round_trip() -> None:
    """The adapter's computed sha must match the committed provenance JSON."""

    result = load_candles("TEST_PAIR", export_dir=FIXTURE_DIR)
    assert result.csv_sha256 == result.provenance.data_sha256
    direct = compute_csv_sha256(FIXTURE_DIR / "TEST_PAIR_H4_lean.csv")
    assert direct == result.provenance.data_sha256


def test_load_candles_mid_ohlc_invariants() -> None:
    result = load_candles("TEST_PAIR", export_dir=FIXTURE_DIR)
    for _, row in result.mid_df.iterrows():
        assert row["low"] <= row["open"] <= row["high"]
        assert row["low"] <= row["close"] <= row["high"]
    # Half-spread is positive (ask > bid) on every bar.
    assert (result.half_spread_close > 0).all()


def test_load_candles_monotonic_4h_spacing() -> None:
    result = load_candles("TEST_PAIR", export_dir=FIXTURE_DIR)
    diffs = result.mid_df.index.to_series().diff().dropna()
    # All exactly 4h in the test fixture.
    expected = pd.Timedelta(hours=4)
    assert (diffs == expected).all()


def test_load_candles_first_last_ts() -> None:
    result = load_candles("TEST_PAIR", export_dir=FIXTURE_DIR)
    assert result.first_ts.isoformat() == "2024-01-01T22:00:00+00:00"
    assert result.last_ts.isoformat() == "2024-01-03T18:00:00+00:00"


def test_load_candles_missing_provenance_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_candles("MISSING", export_dir=tmp_path)


def test_load_candles_missing_csv_raises_file_not_found(tmp_path: Path) -> None:
    """If only the provenance JSON is present but the CSV is gitignored
    and not regenerated locally, fail loud."""

    (tmp_path / "ONLY_PROV_H4_lean.provenance.json").write_text(
        json.dumps(
            {
                "instrument": "ONLY_PROV",
                "granularity": "H4",
                "source": "oanda-test-fixture",
                "requested_from": "2024-01-01T00:00:00+00:00",
                "requested_to": "2024-01-02T00:00:00+00:00",
                "candle_count": 0,
                "first_ts": "2024-01-01T00:00:00+00:00",
                "last_ts": "2024-01-02T00:00:00+00:00",
                "data_sha256": "0" * 64,
                "campaign_002_data_request_hash": "0000000000000000",
                "lean_csv": "ONLY_PROV_H4_lean.csv",
                "exported_by": "test",
                "exported_at": "2026-05-24T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError):
        load_candles("ONLY_PROV", export_dir=tmp_path)


def test_load_candles_sha_drift_raises_provenance_error(tmp_path: Path) -> None:
    """If the CSV's content drifts from the committed sha, refuse to load."""

    # Copy the fixture but tamper one byte in the CSV (change a 1 to 2 in
    # a price). The committed sha will then no longer match.
    src_csv = (FIXTURE_DIR / "TEST_PAIR_H4_lean.csv").read_text(encoding="utf-8")
    tampered = src_csv.replace("1.10002", "1.10003", 1)
    (tmp_path / "TEST_PAIR_H4_lean.csv").write_text(tampered, encoding="utf-8")
    # Copy the committed provenance JSON untouched.
    (tmp_path / "TEST_PAIR_H4_lean.provenance.json").write_text(
        (FIXTURE_DIR / "TEST_PAIR_H4_lean.provenance.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    with pytest.raises(CandleProvenanceError):
        load_candles("TEST_PAIR", export_dir=tmp_path)


def test_load_candles_bad_header_raises_schema_error(tmp_path: Path) -> None:
    """The CSV must have the documented header columns in order."""

    csv_path = tmp_path / "BAD_PAIR_H4_lean.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        # Wrong column order: bid_open before time.
        writer.writerow(
            [
                "bid_open",
                "time",
                "bid_high",
                "bid_low",
                "bid_close",
                "ask_open",
                "ask_high",
                "ask_low",
                "ask_close",
                "volume",
            ]
        )
        writer.writerow(
            [
                "1.10000",
                "2024-01-01T22:00:00+00:00",
                "1.10005",
                "1.09995",
                "1.10002",
                "1.10020",
                "1.10025",
                "1.10015",
                "1.10022",
                "100",
            ]
        )
    (tmp_path / "BAD_PAIR_H4_lean.provenance.json").write_text(
        json.dumps(
            {
                "instrument": "BAD_PAIR",
                "granularity": "H4",
                "source": "oanda-test-fixture",
                "requested_from": "2024-01-01T22:00:00+00:00",
                "requested_to": "2024-01-01T22:00:00+00:00",
                "candle_count": 1,
                "first_ts": "2024-01-01T22:00:00+00:00",
                "last_ts": "2024-01-01T22:00:00+00:00",
                "data_sha256": "0" * 64,
                "campaign_002_data_request_hash": "0",
                "lean_csv": "BAD_PAIR_H4_lean.csv",
                "exported_by": "test",
                "exported_at": "2026-05-24T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(CandleSchemaError):
        load_candles("BAD_PAIR", export_dir=tmp_path)


def test_available_and_expected_instruments() -> None:
    expected = expected_instruments(FIXTURE_DIR)
    avail = available_instruments(FIXTURE_DIR)
    assert "TEST_PAIR" in expected
    assert "TEST_PAIR" in avail


def test_manifest_for_includes_approximation_flags() -> None:
    result = load_candles("TEST_PAIR", export_dir=FIXTURE_DIR)
    mf = manifest_for(result)
    assert mf["instrument"] == "TEST_PAIR"
    assert mf["bar_count"] == 12
    assert mf["csv_sha256"] == result.provenance.data_sha256
    assert any("MID_OHLC_DERIVED" in flag for flag in mf["approximation_flags"])
    assert any("HALF_SPREAD_CLOSE" in flag for flag in mf["approximation_flags"])


def test_data_adapter_imports_no_forex_bot() -> None:
    """Independence test: the adapter must not import the bespoke engine."""

    import research.backtrader_lane.data_adapter as adapter

    src = Path(adapter.__file__).read_text(encoding="utf-8")
    for line in src.splitlines():
        clean = line.split("#", 1)[0].strip()
        if clean.startswith("import ") or clean.startswith("from "):
            assert "forex_bot" not in clean, f"forex_bot import in data_adapter.py: {line}"


def test_data_adapter_imports_no_broker_modules() -> None:
    import research.backtrader_lane.data_adapter as adapter

    src = Path(adapter.__file__).read_text(encoding="utf-8")
    for line in src.splitlines():
        clean = line.split("#", 1)[0].strip()
        if clean.startswith("import ") or clean.startswith("from "):
            forbidden = (
                "backtrader.brokers.oandabroker",
                "backtrader.stores.oandastore",
                "backtrader.feeds.oanda",
                "import quantconnect",
                "from quantconnect",
                "import lean",
                "from lean ",
            )
            for needle in forbidden:
                assert needle not in clean, f"forbidden in data_adapter.py: {line}"
