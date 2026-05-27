"""Frozen constants for C008/C009/C018 exit-parity diagnostics."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SPLITS: dict[str, tuple[str, str]] = {
    "train": ("2020-01-01", "2022-12-31"),
    "validation": ("2023-01-01", "2024-12-31"),
}

CAMPAIGN_CONFIGS: dict[str, Path] = {
    "C008": REPO_ROOT / "configs" / "campaign_008_range_mean_reversion.yaml",
    "C009": REPO_ROOT / "configs" / "campaign_009_mean_reversion.yaml",
    "C018": REPO_ROOT / "configs" / "campaign_018_mean_reversion_protective_stop.yaml",
}

BESPOKE_TRADE_GLOBS: dict[str, str] = {
    "C008": "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/{split}/*_trades.csv",
    "C009": "backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/{split}/base/*_trades.csv",
    "C018": "backtests/CAMPAIGN_018_mean_reversion_protective_stop/{split}/base/*_trades.csv",
}

FILL_TIMING = "signal_bar_close"
GAP_FILL_POLICY = "none"

PARITY_OUT_DIR = REPO_ROOT / "research" / "backtrader_exit_parity"


def parse_split_date(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str).replace(tzinfo=UTC)
