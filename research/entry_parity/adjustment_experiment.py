"""Backtrader orchestration adjustment experiment (diagnostic only)."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import InstrumentRepo
from forex_bot.risk.policy import RiskEngine
from research.backtrader_exit_parity.constants import (
    CAMPAIGN_CONFIGS,
    REPO_ROOT,
    SPLITS,
    parse_split_date,
)
from research.backtrader_exit_parity.data_feed import load_split_frame
from research.backtrader_exit_parity.runner import _campaign_params
from research.backtrader_exit_parity.strategy import run_mean_reversion_exit_parity
from research.entry_parity.constants import ENTRY_PARITY_OUT_DIR
from research.entry_parity.load_trades import load_bespoke_trades


def run_adjustment_experiment(
    *,
    repo_root: Path = REPO_ROOT,
    out_dir: Path | None = None,
    mode: Literal["legacy_bt", "engine_aligned"] = "engine_aligned",
) -> dict[str, Any]:
    """Re-run BT lane with selected risk-window orchestration profile."""
    out_dir = out_dir or ENTRY_PARITY_OUT_DIR
    results: dict[str, Any] = {
        "mode": mode,
        "strategy_evidence": False,
        "parity_diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "campaigns": {},
    }

    for campaign in ("C008", "C009", "C018"):
        config_path = CAMPAIGN_CONFIGS[campaign]
        settings = load_settings(config_path)
        strategy_cfg, midline_exit, protective_r, ti_long, ti_short = _campaign_params(campaign, settings)
        fill_model = FillModel(
            fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
            spread_slippage_multiplier=Decimal(
                str(settings.backtest.spread_slippage_multiplier)
            ),
        )
        risk_engine = RiskEngine(settings, mode="backtest")
        max_bars = int(strategy_cfg.get("max_bars_in_trade", 40))
        starting_equity = float(settings.backtest.starting_equity_usd)

        db = Database(settings.app.database_path)
        try:
            instr_repo = InstrumentRepo(db)
            bt_count = 0
            bespoke_count = len(load_bespoke_trades(repo_root, campaign, "train")) + len(
                load_bespoke_trades(repo_root, campaign, "validation")
            )
            rejections: list[dict[str, Any]] = []

            for split in SPLITS:
                frm, to = parse_split_date(SPLITS[split][0]), parse_split_date(SPLITS[split][1])
                for pair in settings.market.instruments:
                    meta = instr_repo.get(pair)
                    if meta is None:
                        continue
                    frame, _ = load_split_frame(
                        repo_root, pair, from_time=frm, to_time=to
                    )
                    if frame.empty:
                        continue
                    result = run_mean_reversion_exit_parity(
                        frame,
                        instrument=meta,
                        strategy_cfg=strategy_cfg,
                        settings=settings,
                        campaign=campaign,
                        midline_exit=midline_exit,
                        protective_stop_after_r=protective_r,
                        fill_model=fill_model,
                        risk_engine=risk_engine,
                        max_bars_in_trade=max_bars,
                        starting_equity=starting_equity,
                        risk_window_mode=mode,
                        rejection_log=rejections,
                        thesis_invalidation_long_z=ti_long,
                        thesis_invalidation_short_z=ti_short,
                    )
                    bt_count += len(result.trades)

            results["campaigns"][campaign] = {
                "bespoke_trade_count": bespoke_count,
                "backtrader_trade_count": bt_count,
                "delta": bespoke_count - bt_count,
                "delta_pct": round(
                    100.0 * (bespoke_count - bt_count) / max(bespoke_count, 1), 2
                ),
                "rejection_log_count": len(rejections),
            }
        finally:
            db.close()

    return results
