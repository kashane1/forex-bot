"""Orchestrate C008/C009/C018 exit-parity replays."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import backtrader as bt

from forex_bot.backtesting.fills import FillModel
from forex_bot.config import load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import InstrumentRepo
from forex_bot.risk.policy import RiskEngine
from research.backtrader_exit_parity.constants import (
    CAMPAIGN_CONFIGS,
    FILL_TIMING,
    GAP_FILL_POLICY,
    PARITY_OUT_DIR,
    REPO_ROOT,
    SPLITS,
    parse_split_date,
)
from research.backtrader_exit_parity.data_feed import load_split_frame
from research.backtrader_exit_parity.exit_logic import exit_reason_stats
from research.backtrader_exit_parity.pnl import DEFAULT_ACCOUNT_CURRENCY
from research.backtrader_exit_parity.strategy import (
    run_mean_reversion_exit_parity,
)

PNL_CONVERSION_MODE = "home_currency_v1"
RISK_WINDOW_MODE = "engine_aligned"


def _campaign_params(campaign: str, settings: Any) -> tuple[dict[str, Any], bool, float | None]:
    if campaign == "C018":
        cfg = settings.strategy.mean_reversion_protective_stop.model_dump()
        ps = cfg.get("protective_stop") or {}
        threshold = float(ps.get("favorable_excursion_r_threshold", 1.0))
        return cfg, False, threshold
    cfg = settings.strategy.mean_reversion.model_dump()
    midline = bool(cfg.get("midline_exit", campaign == "C009"))
    return cfg, midline, None


def run_campaign_parity(
    campaign: str,
    *,
    repo_root: Path = REPO_ROOT,
    out_dir: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Run train + validation exit parity for one campaign."""
    config_path = CAMPAIGN_CONFIGS[campaign]
    settings = load_settings(config_path)
    strategy_cfg, midline_exit, protective_r = _campaign_params(campaign, settings)
    fill_model = FillModel(
        fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
        spread_slippage_multiplier=Decimal(
            str(settings.backtest.spread_slippage_multiplier)
        ),
    )
    risk_engine = RiskEngine(settings, mode="backtest")
    max_bars = int(strategy_cfg.get("max_bars_in_trade", 40))
    starting_equity = float(settings.backtest.starting_equity_usd)

    db = Database(settings.app.database_path if db_path is None else db_path)
    try:
        instr_repo = InstrumentRepo(db)
        all_trades: list[dict[str, Any]] = []
        by_split: dict[str, list[dict[str, Any]]] = {"train": [], "validation": []}

        for split, (frm_s, to_s) in SPLITS.items():
            frm, to = parse_split_date(frm_s), parse_split_date(to_s)
            for pair in settings.market.instruments:
                meta = instr_repo.get(pair)
                if meta is None:
                    continue
                frame, dedupe_meta = load_split_frame(
                    repo_root,
                    pair,
                    from_time=frm,
                    to_time=to,
                    db_path=db_path or Path(settings.app.database_path),
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
                    risk_window_mode=RISK_WINDOW_MODE,
                )
                for t in result.trades:
                    rec = {
                        "instrument": t.instrument,
                        "side": t.side,
                        "units": t.units,
                        "entry_time": t.entry_time.isoformat(),
                        "exit_time": t.exit_time.isoformat(),
                        "entry_price": t.entry_price,
                        "exit_price": t.exit_price,
                        "exit_reason": t.exit_reason,
                        "bars_held": t.bars_held,
                        "r_multiple": t.r_multiple,
                        "split": split,
                        "protective_stop_armed": t.protective_stop_armed,
                        "protective_stop_exit": t.protective_stop_exit,
                    }
                    all_trades.append(rec)
                    by_split[split].append(rec)

        summary: dict[str, Any] = {
            "campaign": campaign,
            "strategy_evidence": False,
            "parity_diagnostic_only": True,
            "generated_at_utc": datetime.now(tz=UTC).isoformat(),
            "engine": "backtrader_exit_parity",
            "backtrader_version": bt.__version__,
            "pnl_conversion_mode": PNL_CONVERSION_MODE,
            "account_currency": DEFAULT_ACCOUNT_CURRENCY,
            "risk_window_mode": RISK_WINDOW_MODE,
            "data_source": str(db_path or settings.app.database_path),
            "deduped_candles": True,
            "fill_timing": FILL_TIMING,
            "gap_fill_policy": GAP_FILL_POLICY,
            "midline_exit": midline_exit,
            "protective_stop_after_r": protective_r,
            "aggregate": exit_reason_stats(all_trades),
            "by_split": {
                split: exit_reason_stats(trades) for split, trades in by_split.items()
            },
            "protective_arm_rate_pct": round(
                100.0
                * sum(1 for t in all_trades if t.get("protective_stop_armed"))
                / max(len(all_trades), 1),
                2,
            )
            if campaign == "C018"
            else None,
            "protective_exit_rate_pct": round(
                100.0
                * sum(1 for t in all_trades if t.get("protective_stop_exit"))
                / max(len(all_trades), 1),
                2,
            )
            if campaign == "C018"
            else None,
        }
        out = out_dir or PARITY_OUT_DIR
        out.mkdir(parents=True, exist_ok=True)
        summary_path = out / f"{campaign.lower()}_parity_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
        trades_path = out / f"{campaign.lower()}_parity_trades.jsonl"
        with trades_path.open("w", encoding="utf-8") as fh:
            for rec in all_trades:
                fh.write(json.dumps(rec, default=str) + "\n")
        return summary
    finally:
        db.close()


def run_all_campaigns(
    *,
    repo_root: Path = REPO_ROOT,
    out_dir: Path | None = None,
) -> dict[str, dict[str, Any]]:
    results = {}
    for campaign in ("C008", "C009", "C018"):
        results[campaign] = run_campaign_parity(campaign, repo_root=repo_root, out_dir=out_dir)
    write_parity_run_manifest(results, out_dir or PARITY_OUT_DIR)
    return results


def write_parity_run_manifest(
    results: dict[str, dict[str, Any]],
    out_dir: Path,
) -> Path:
    """Write run metadata for refreshed parity artifacts."""
    first = next(iter(results.values()), {})
    manifest: dict[str, Any] = {
        "strategy_evidence": False,
        "parity_diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "backtrader_version": first.get("backtrader_version", bt.__version__),
        "pnl_conversion_mode": PNL_CONVERSION_MODE,
        "account_currency": DEFAULT_ACCOUNT_CURRENCY,
        "risk_window_mode": RISK_WINDOW_MODE,
        "data_source": first.get("data_source", "data/campaign_002.sqlite3"),
        "deduped_candles": True,
        "fill_timing": FILL_TIMING,
        "gap_fill_policy": GAP_FILL_POLICY,
        "campaigns": {
            campaign: {
                "total_trades": data.get("aggregate", {}).get("total_trades", 0),
                "campaign_version": data.get("campaign"),
            }
            for campaign, data in results.items()
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "parity_run_manifest.json"
    path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    return path
