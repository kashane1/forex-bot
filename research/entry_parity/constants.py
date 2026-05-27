"""Constants for entry orchestration parity diagnostics."""

from __future__ import annotations

from research.backtrader_exit_parity.constants import (
    REPO_ROOT,
)

ENTRY_PARITY_OUT_DIR = REPO_ROOT / "research" / "entry_parity"
BT_TRADES_DIR = REPO_ROOT / "research" / "backtrader_exit_parity"

BESPOKE_REJECTION_GLOBS: dict[str, str] = {
    "C008": "backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/baseline/{split}/*_risk_rejections.csv",
    "C009": "backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/{split}/base/*_risk_rejections.csv",
    "C018": "backtests/CAMPAIGN_018_mean_reversion_protective_stop/{split}/base/*_risk_rejections.csv",
}

CAMPAIGN_BT_TRADE_FILES: dict[str, str] = {
    "C008": "c008_parity_trades.jsonl",
    "C009": "c009_parity_trades.jsonl",
    "C018": "c018_parity_trades.jsonl",
}
