"""Read-only loaders for verifier inputs.

The verifier consumes:

- the authoritative CAMPAIGN_002 parameter set
  (``research/lean_parity/lean_parity_config.json``);
- the bespoke no-RiskEngine reference
  (``research/lean_parity/campaign_002_h4_bespoke_reference.json``);
- the exported H4 candle CSVs in ``research/lean_parity/exports/campaign_002_h4/``.

All three live inside the repo; the CSVs are gitignored bulk data and
may be absent — :func:`load_candle_csv` raises a clear ``FileNotFoundError``
so callers can mark a phase BLOCKED rather than guess.

No bespoke-engine imports. No network calls.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from research.parity_verifier.models import Bar, CandleSeries, VerifierConfig

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = _REPO_ROOT / "research" / "lean_parity" / "lean_parity_config.json"
DEFAULT_BESPOKE_REFERENCE_PATH = (
    _REPO_ROOT / "research" / "lean_parity" / "campaign_002_h4_bespoke_reference.json"
)
DEFAULT_EXPORT_DIR = _REPO_ROOT / "research" / "lean_parity" / "exports" / "campaign_002_h4"


def load_verifier_config(path: Path = DEFAULT_CONFIG_PATH) -> VerifierConfig:
    """Load the CAMPAIGN_002 parameters from the authoritative JSON."""

    raw = json.loads(path.read_text(encoding="utf-8"))
    strategy = raw["strategy"]
    cost = raw["cost_model"]
    sizing = raw["sizing"]
    market = raw["market"]
    return VerifierConfig(
        ema_fast=strategy["ema_fast"],
        ema_slow=strategy["ema_slow"],
        donchian_lookback=strategy["donchian_lookback"],
        atr_lookback=strategy["atr_lookback"],
        atr_stop_multiple=strategy["atr_stop_multiple"],
        trailing_stop_atr_multiple=strategy["trailing_stop_atr_multiple"],
        max_bars_in_trade=strategy["max_bars_in_trade"],
        risk_per_trade_pct=sizing["risk_per_trade_pct"],
        starting_equity_usd=sizing["starting_equity_usd"],
        fixed_slippage_pips=cost["fixed_slippage_pips"],
        spread_slippage_multiplier=cost["spread_slippage_multiplier"],
        min_atr_pips=strategy.get("min_atr_pips") or {},
        account_currency=market["account_currency"],
    )


def config_hash(config: VerifierConfig) -> str:
    """Stable SHA-256 of the verifier's frozen parameter set. Used as
    a sanity marker in the verifier output."""

    payload = json.dumps(config.model_dump(mode="json"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_bespoke_reference(path: Path = DEFAULT_BESPOKE_REFERENCE_PATH) -> dict:
    """Return the bespoke reference JSON as a plain dict. The shape is
    pinned by ``research/lean_parity/campaign_002_h4_bespoke_reference.json``
    and exercised in tests."""

    return json.loads(path.read_text(encoding="utf-8"))


def _parse_csv_time(raw: str) -> datetime:
    """The export CSVs write ISO-8601 timestamps with an explicit ``+00:00``
    offset. Parse strictly to catch silent locale or format drift."""

    raw = raw.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def load_candle_csv(
    instrument: str,
    export_dir: Path = DEFAULT_EXPORT_DIR,
) -> CandleSeries:
    """Read one ``<INST>_H4_lean.csv`` from the export bundle.

    Raises :class:`FileNotFoundError` if the CSV is not present. The
    CSVs are gitignored bulk data; absence is an expected branch state,
    not a verifier bug.
    """

    csv_path = export_dir / f"{instrument}_H4_lean.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV not found at {csv_path}. The Lean parity export CSVs "
            f"are gitignored regenerable bulk data — see "
            f"research/lean_parity/exports/campaign_002_h4/EXPORT_MANIFEST.md."
        )
    bars: list[Bar] = []
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            bid_open = float(row["bid_open"])
            bid_high = float(row["bid_high"])
            bid_low = float(row["bid_low"])
            bid_close = float(row["bid_close"])
            ask_open = float(row["ask_open"])
            ask_high = float(row["ask_high"])
            ask_low = float(row["ask_low"])
            ask_close = float(row["ask_close"])
            bars.append(
                Bar(
                    time=_parse_csv_time(row["time"]),
                    open=(bid_open + ask_open) / 2.0,
                    high=(bid_high + ask_high) / 2.0,
                    low=(bid_low + ask_low) / 2.0,
                    close=(bid_close + ask_close) / 2.0,
                    bid_open=bid_open,
                    bid_high=bid_high,
                    bid_low=bid_low,
                    bid_close=bid_close,
                    ask_open=ask_open,
                    ask_high=ask_high,
                    ask_low=ask_low,
                    ask_close=ask_close,
                    volume=int(row.get("volume", 0) or 0),
                )
            )
    return CandleSeries(instrument=instrument, bars=bars)


def csv_present(instrument: str, export_dir: Path = DEFAULT_EXPORT_DIR) -> bool:
    """Cheap availability check for a single CSV. Used by the script
    entry point so a missing file can be reported cleanly."""

    return (export_dir / f"{instrument}_H4_lean.csv").exists()
