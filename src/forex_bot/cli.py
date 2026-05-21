"""Typer CLI.

Every command requires --config. Commands that need broker credentials
raise immediately if env vars are missing. The `doctor` command does not
require broker credentials and is the entry point for new installations.
"""

from __future__ import annotations

import subprocess
from decimal import Decimal
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from forex_bot import __version__
from forex_bot.backtesting.engine import BacktestEngine
from forex_bot.backtesting.fills import FillModel
from forex_bot.broker.oanda import OandaBroker
from forex_bot.clock import utcnow
from forex_bot.config import ConfigError, Settings, load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    BrokerOrderRepo,
    CandleRepo,
    InstrumentRepo,
    OrderPlanRepo,
    RiskDecisionRepo,
    SignalRepo,
    SpreadSnapshotRepo,
    SystemEventRepo,
    TransactionRepo,
)
from forex_bot.domain.candles import CandleFrame, CandleRequest
from forex_bot.execution.reconciliation import Reconciler
from forex_bot.logging_config import configure_logging, get_logger
from forex_bot.loops import build_strategies, run_paper_loop, run_practice_loop
from forex_bot.reporting.render import render_html, render_markdown
from forex_bot.reporting.weekly import build_weekly_report

app = typer.Typer(
    help="OANDA forex research and execution bot (demo-first).",
    invoke_without_command=True,
    no_args_is_help=True,
)
console = Console()
logger = get_logger(__name__)


def _load(config_path: Path) -> Settings:
    try:
        settings = load_settings(config_path)
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=2)
    configure_logging(level="INFO", log_path=settings.app.log_path)
    return settings


def _build_broker(settings: Settings) -> OandaBroker:
    account_id, token = settings.broker_credentials()
    return OandaBroker(
        environment=settings.broker.environment,
        account_id=account_id,
        access_token=token,
        timeout_seconds=settings.broker.request_timeout_seconds,
        max_retries=settings.broker.max_retries,
    )


def _git_short_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    return result.stdout.strip() or None


# ---------------------------------------------------------------------------


@app.callback()
def main_callback(version: bool = typer.Option(False, "--version")) -> None:
    if version:
        console.print(f"forex-bot {__version__}")
        raise typer.Exit()


@app.command()
def doctor(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False, readable=True),
) -> None:
    """Validate config + env. Never touches the broker if credentials missing."""
    try:
        settings = load_settings(config)
    except ConfigError as exc:
        console.print(f"[red]Config invalid:[/red] {exc}")
        raise typer.Exit(code=2)
    configure_logging(level="INFO", log_path=settings.app.log_path)
    table = Table(title="forex-bot doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Detail")

    table.add_row("Config file", "[green]ok[/green]", str(config))
    table.add_row("Mode", "[green]ok[/green]", settings.app.mode)
    table.add_row("Broker env", "[green]ok[/green]", settings.broker.environment)
    table.add_row("Trading enabled", "yes" if settings.app.trading_enabled else "no", "")
    table.add_row("Order submission allowed", "yes" if settings.app.allow_order_submission else "no", "")
    table.add_row("Live trading allowed", "yes" if settings.app.allow_live_trading else "no", "")
    table.add_row("Config hash", "[green]ok[/green]", settings.config_hash[:16])
    kill_path = Path(settings.app.kill_switch_path)
    table.add_row(
        "Kill switch file",
        "[red]ACTIVE[/red]" if kill_path.exists() else "[green]inactive[/green]",
        str(kill_path),
    )

    try:
        account_id, _ = settings.broker_credentials()
        table.add_row("Broker credentials", "[green]present[/green]", f"account={account_id[:6]}…")
    except ConfigError as exc:
        table.add_row("Broker credentials", "[yellow]missing[/yellow]", str(exc))

    console.print(table)


@app.command("sync-instruments")
def sync_instruments(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
) -> None:
    settings = _load(config)
    broker = _build_broker(settings)
    db = Database(settings.app.database_path)
    repo = InstrumentRepo(db)
    instruments = broker.list_instruments()
    for inst in instruments:
        repo.upsert(inst, raw=inst.model_dump())
    console.print(f"[green]synced[/green] {len(instruments)} instruments")


@app.command("fetch-candles")
def fetch_candles(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    instrument: str = typer.Option(..., "--instrument", "-i"),
    granularity: str = typer.Option("H4", "--granularity", "-g"),
    count: int = typer.Option(500, "--count", "-n"),
) -> None:
    settings = _load(config)
    broker = _build_broker(settings)
    db = Database(settings.app.database_path)
    repo = CandleRepo(db)
    request = CandleRequest(
        instrument=instrument,
        granularity=granularity,  # type: ignore[arg-type]
        price=settings.market.candle_price_components,  # type: ignore[arg-type]
        count=count,
        daily_alignment=settings.market.daily_alignment,
        alignment_timezone=settings.market.alignment_timezone,
        weekly_alignment=settings.market.weekly_alignment,
    )
    candles = broker.get_candles(request)
    n = repo.upsert_many(
        candles,
        source="oanda",
        price_components=settings.market.candle_price_components,
        request_hash=str(hash((instrument, granularity, count))),
    )
    console.print(f"[green]stored[/green] {n} candles for {instrument} {granularity}")


@app.command()
def backtest(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    instrument: str | None = typer.Option(None, "--instrument", "-i"),
    granularity: str = typer.Option("H4", "--granularity", "-g"),
) -> None:
    settings = _load(config)
    db = Database(settings.app.database_path)
    instr_repo = InstrumentRepo(db)
    candles = CandleRepo(db)
    targets = [instrument] if instrument else settings.market.instruments
    fill_model = FillModel(
        fixed_slippage_pips=Decimal(str(settings.backtest.fixed_slippage_pips)),
        spread_slippage_multiplier=Decimal(str(settings.backtest.spread_slippage_multiplier)),
    )
    table = Table(title="Backtest results")
    for col in (
        "instrument",
        "trades",
        "return%",
        "max_dd%",
        "pf",
        "expectancy_r",
        "win%",
    ):
        table.add_column(col)

    for inst_name in targets:
        instrument_meta = instr_repo.get(inst_name)
        if instrument_meta is None:
            console.print(f"[yellow]skip[/yellow] {inst_name}: no instrument metadata; run sync-instruments")
            continue
        rows = candles.list(inst_name, granularity, completed_only=True)  # type: ignore[arg-type]
        if not rows:
            console.print(f"[yellow]skip[/yellow] {inst_name}: no candles; run fetch-candles")
            continue
        frame = CandleFrame.from_candles(inst_name, granularity, rows)  # type: ignore[arg-type]
        strategies = build_strategies(settings)
        for strategy, cfg in strategies:
            engine = BacktestEngine(
                instrument=instrument_meta,
                strategy=strategy,
                strategy_config=cfg,
                fill_model=fill_model,
                starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
                account_currency=settings.market.account_currency,
                risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
                max_bars_in_trade=int(cfg.get("max_bars_in_trade", 80)),
                commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),
            )
            result = engine.run(frame)
            m = result.metrics
            table.add_row(
                inst_name,
                str(m.trade_count),
                f"{m.total_return_pct:.2f}",
                f"{m.max_drawdown_pct:.2f}",
                f"{m.profit_factor:.2f}" if m.profit_factor != float("inf") else "inf",
                f"{m.expectancy_r:.3f}",
                f"{m.win_rate*100:.1f}",
            )
    console.print(table)


@app.command("paper-loop")
def paper_loop(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    once: bool = typer.Option(True, "--once/--forever", help="Run a single iteration and exit"),
) -> None:
    settings = _load(config)
    if settings.app.mode != "paper":
        console.print(f"[red]paper-loop requires mode=paper, got {settings.app.mode}[/red]")
        raise typer.Exit(2)
    broker = _build_broker(settings)
    db = Database(settings.app.database_path)
    outcome = run_paper_loop(
        settings=settings,
        broker=broker,
        instruments_repo=InstrumentRepo(db),
        candles=CandleRepo(db),
        signals=SignalRepo(db),
        decisions=RiskDecisionRepo(db),
        plans=OrderPlanRepo(db),
        snapshots=AccountSnapshotRepo(db),
        spreads=SpreadSnapshotRepo(db),
        events=SystemEventRepo(db),
    )
    console.print(
        f"[green]paper-loop done[/green] signals={len(outcome.signals)} "
        f"decisions={len(outcome.decisions)} plans={len(outcome.plans)}"
    )
    if not once:
        console.print("[yellow]--forever not implemented in v0; use launchd or cron[/yellow]")


@app.command("demo-loop")
def demo_loop(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    once: bool = typer.Option(True, "--once/--forever"),
) -> None:
    settings = _load(config)
    if settings.app.mode not in {"practice", "live"}:
        console.print(f"[red]demo-loop requires mode=practice or live, got {settings.app.mode}[/red]")
        raise typer.Exit(2)
    if not settings.app.trading_enabled or not settings.app.allow_order_submission:
        console.print("[red]demo-loop requires trading_enabled and allow_order_submission[/red]")
        raise typer.Exit(2)
    broker = _build_broker(settings)
    db = Database(settings.app.database_path)
    outcome = run_practice_loop(
        settings=settings,
        broker=broker,
        instruments_repo=InstrumentRepo(db),
        candles=CandleRepo(db),
        signals=SignalRepo(db),
        decisions=RiskDecisionRepo(db),
        plans=OrderPlanRepo(db),
        snapshots=AccountSnapshotRepo(db),
        spreads=SpreadSnapshotRepo(db),
        events=SystemEventRepo(db),
        orders=BrokerOrderRepo(db),
        transactions=TransactionRepo(db),
    )
    console.print(
        f"[green]demo-loop done[/green] signals={len(outcome.signals)} "
        f"plans={len(outcome.plans)} executions={len(outcome.executions)}"
    )
    if not once:
        console.print("[yellow]--forever not implemented in v0; use launchd or cron[/yellow]")


@app.command()
def reconcile(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
) -> None:
    settings = _load(config)
    broker = _build_broker(settings)
    db = Database(settings.app.database_path)
    reconciler = Reconciler(
        broker=broker,
        transactions=TransactionRepo(db),
        snapshots=AccountSnapshotRepo(db),
        events=SystemEventRepo(db),
    )
    report = reconciler.run()
    color = "green" if report.clean else "red"
    console.print(
        f"[{color}]reconcile clean={report.clean}[/{color}] "
        f"new_txs={report.fetched_transactions} last_tx={report.last_transaction_id}"
    )
    for diff in report.differences:
        console.print(f"  diff: {diff}")


report_app = typer.Typer(help="Reporting commands")
app.add_typer(report_app, name="report")


@report_app.command("weekly")
def report_weekly(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    out_dir: Path = typer.Option(Path("./reports"), "--out", "-o"),
) -> None:
    settings = _load(config)
    db = Database(settings.app.database_path)
    report = build_weekly_report(
        db,
        now=utcnow(),
        config_hash=settings.config_hash,
        code_commit_hash=_git_short_sha(),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"weekly-{report.window_end.strftime('%Y%m%d')}.md"
    html_path = out_dir / f"weekly-{report.window_end.strftime('%Y%m%d')}.html"
    md_path.write_text(render_markdown(report), encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")
    console.print(f"[green]wrote[/green] {md_path}")
    console.print(f"[green]wrote[/green] {html_path}")


if __name__ == "__main__":  # pragma: no cover
    app()
