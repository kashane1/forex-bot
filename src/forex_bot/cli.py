"""Typer CLI.

Every command requires --config. Commands that need broker credentials
raise immediately if env vars are missing. The `doctor` command does not
require broker credentials and is the entry point for new installations.
"""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from forex_bot import __version__
from forex_bot.approval import StrategyNotApprovedError, assert_loop_strategies_approved
from forex_bot.backtesting.audit import audit_instrument, render_audit_markdown
from forex_bot.backtesting.engine import BacktestEngine, compute_data_request_hash
from forex_bot.backtesting.exporters import write_all
from forex_bot.backtesting.fills import FillModel
from forex_bot.broker.oanda import OandaBroker
from forex_bot.clock import utcnow
from forex_bot.config import ConfigError, Settings, load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import (
    AccountSnapshotRepo,
    BrokerOrderRepo,
    CandleRepo,
    DataSourceRecord,
    DataSourceRepo,
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
from forex_bot.guards import assert_practice_data_environment
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


def _parse_date(value: str | None) -> datetime | None:
    if value is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            dt = datetime.strptime(value, fmt)
        except ValueError:
            continue
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    raise typer.BadParameter(f"could not parse date '{value}'")


def _parse_instruments(s: str | None, default: list[str]) -> list[str]:
    if not s:
        return default
    return [x.strip().upper() for x in s.split(",") if x.strip()]


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
    from_date: str | None = typer.Option(None, "--from", help="ISO date for start of fetch window"),
    to_date: str | None = typer.Option(None, "--to", help="ISO date for end of fetch window"),
    page_size: int = typer.Option(2500, "--page-size", help="Candles per OANDA call (max 5000)"),
    keep_incomplete: bool = typer.Option(
        False,
        "--keep-incomplete/--drop-incomplete",
        help="Default drops incomplete candles per the data spec.",
    ),
    campaign: str | None = typer.Option(
        None, "--campaign", help="Tag rows in data_sources with this campaign label."
    ),
) -> None:
    """Fetch OANDA candles. With --from/--to, paginates forward until the
    window is covered. Without dates, fetches the latest --count candles.

    Drops incomplete candles by default, captures raw-bytes + normalized
    hashes per fetch into the data_sources table, and refuses to run
    unless the practice-data environment guard passes.
    """
    import hashlib

    settings = _load(config)
    guard = assert_practice_data_environment(settings)
    console.print(
        f"[green]env guard ok[/green] account={guard.account_id_redacted} "
        f"env={guard.declared_environment}"
    )

    broker = _build_broker(settings)
    db = Database(settings.app.database_path)
    repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    events = SystemEventRepo(db)
    price = settings.market.candle_price_components
    source_label = f"oanda-{settings.broker.environment}"

    from_dt = _parse_date(from_date)
    to_dt = _parse_date(to_date)

    raw_hasher = hashlib.sha256()
    norm_hasher = hashlib.sha256()
    pages = 0
    written_total = 0
    dropped_total = 0
    first_ts: str | None = None
    last_ts: str | None = None

    def _record_batch(candles_list, raw_bytes: bytes) -> int:
        """Drop incompletes (unless --keep-incomplete), accumulate hashes,
        upsert, return the count actually written."""
        nonlocal dropped_total, first_ts, last_ts
        kept = candles_list if keep_incomplete else [c for c in candles_list if c.complete]
        dropped_total += len(candles_list) - len(kept)
        if not kept:
            return 0
        raw_hasher.update(raw_bytes)
        for c in kept:
            iso = c.time.isoformat()
            # Normalized hash: deterministic over (ts, bid/ask OHLC strings).
            parts = (
                c.instrument,
                granularity,
                iso,
                str(c.bid_o), str(c.bid_h), str(c.bid_l), str(c.bid_c),
                str(c.ask_o), str(c.ask_h), str(c.ask_l), str(c.ask_c),
                str(c.volume),
            )
            norm_hasher.update("|".join(parts).encode("utf-8"))
        if first_ts is None or kept[0].time.isoformat() < first_ts:
            first_ts = kept[0].time.isoformat()
        last_ts_str = kept[-1].time.isoformat()
        if last_ts is None or last_ts_str > last_ts:
            last_ts = last_ts_str
        n = repo.upsert_many(
            kept,
            source=source_label,
            price_components=price,
            request_hash=hashlib.sha1(raw_bytes).hexdigest()[:16],
        )
        return n

    request_params: dict[str, Any] = {}

    if from_dt is None and to_dt is None:
        # Latest --count candles, single call.
        request = CandleRequest(
            instrument=instrument,
            granularity=granularity,  # type: ignore[arg-type]
            price=price,  # type: ignore[arg-type]
            count=count,
            daily_alignment=settings.market.daily_alignment,
            alignment_timezone=settings.market.alignment_timezone,
            weekly_alignment=settings.market.weekly_alignment,
        )
        try:
            candles, raw = broker.get_candles_with_raw(request)
        except Exception as exc:
            console.print(f"[red]fetch failed: {exc}[/red]")
            raise typer.Exit(1)
        request_params = request.model_dump(mode="json")
        n = _record_batch(candles, raw)
        pages = 1
        written_total = n
    else:
        if from_dt is None:
            raise typer.BadParameter("--from is required when --to is used")
        if to_dt is None:
            to_dt = utcnow()
        cursor = from_dt
        while cursor < to_dt:
            # OANDA forbids count + from + to together. Use count + from for
            # pagination; we check against to_dt ourselves.
            request = CandleRequest(
                instrument=instrument,
                granularity=granularity,  # type: ignore[arg-type]
                price=price,  # type: ignore[arg-type]
                count=page_size,
                from_time=cursor,
                to_time=None,
                daily_alignment=settings.market.daily_alignment,
                alignment_timezone=settings.market.alignment_timezone,
                weekly_alignment=settings.market.weekly_alignment,
                include_first=True,
            )
            try:
                candles, raw = broker.get_candles_with_raw(request)
            except Exception as exc:
                console.print(f"[red]fetch failed at {cursor}: {exc}[/red]")
                raise typer.Exit(1)
            if not candles:
                break
            # Clip to the requested window: drop candles whose time > to_dt.
            in_window = [c for c in candles if c.time <= to_dt]
            n = _record_batch(in_window, raw)
            pages += 1
            written_total += n
            last_in_window = in_window[-1].time if in_window else cursor
            last_received = candles[-1].time
            console.print(
                f"  page {pages} → {last_received.isoformat()} (+{n}, dropped={dropped_total})"
            )
            if last_received <= cursor:
                break  # OANDA didn't advance
            cursor = last_received + timedelta(seconds=1)
            if last_in_window >= to_dt:
                break  # we've covered the window
        request_params = {
            "instrument": instrument,
            "granularity": granularity,
            "price": price,
            "from": from_dt.isoformat(),
            "to": to_dt.isoformat(),
            "page_size": page_size,
        }

    # Record provenance in data_sources.
    record = DataSourceRecord(
        instrument=instrument,
        granularity=granularity,
        source=source_label,
        host=f"https://api-fx{settings.broker.environment}.oanda.com",
        from_time=from_dt.isoformat() if from_dt else None,
        to_time=to_dt.isoformat() if to_dt else None,
        price_components=price,
        page_count=pages,
        candles_written=written_total,
        candles_dropped_incomplete=dropped_total,
        first_ts=first_ts,
        last_ts=last_ts,
        raw_sha256=raw_hasher.hexdigest() if pages else None,
        normalized_sha256=norm_hasher.hexdigest() if written_total else None,
        request_params_json=json.dumps(request_params, default=str, sort_keys=True),
        broker_account_id_redacted=guard.account_id_redacted,
        campaign=campaign,
    )
    ds_id = ds_repo.insert(record)
    events.record(
        "data_source",
        "info",
        f"fetched {instrument} {granularity}: {written_total} candles, "
        f"{pages} pages, dropped_incomplete={dropped_total}",
        {
            "data_source_id": ds_id,
            "instrument": instrument,
            "granularity": granularity,
            "raw_sha256_prefix": record.raw_sha256[:16] if record.raw_sha256 else None,
            "normalized_sha256_prefix": record.normalized_sha256[:16] if record.normalized_sha256 else None,
        },
    )
    console.print(
        f"[green]stored[/green] {written_total} candles for {instrument} {granularity} "
        f"(pages={pages}, dropped={dropped_total}, raw_sha256={record.raw_sha256[:12] if record.raw_sha256 else 'n/a'}…)"
    )


@app.command()
def backtest(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    strategy: str | None = typer.Option(
        None, "--strategy", help="Run only this strategy (defaults to all enabled in config)"
    ),
    instrument: str | None = typer.Option(None, "--instrument", "-i"),
    instruments: str | None = typer.Option(
        None, "--instruments", help="Comma-separated list, overrides --instrument and config"
    ),
    granularity: str = typer.Option("H4", "--granularity", "-g"),
    from_date: str | None = typer.Option(None, "--from", help="ISO date inclusive"),
    to_date: str | None = typer.Option(None, "--to", help="ISO date inclusive"),
    spread_multiplier: float | None = typer.Option(
        None, "--spread-multiplier", help="Override backtest.spread_slippage_multiplier"
    ),
    slippage_pips: float | None = typer.Option(
        None, "--slippage-pips", help="Override backtest.fixed_slippage_pips"
    ),
    export_dir: Path | None = typer.Option(
        None, "--export-dir", help="Write trades.csv, equity.csv, metrics.json, metrics.md per run"
    ),
    label: str | None = typer.Option(
        None, "--label", help="Prefix label for exported files (default: instrument_strategy)"
    ),
) -> None:
    """Run one or more backtests and (optionally) export artifacts."""
    settings = _load(config)
    db = Database(settings.app.database_path)
    instr_repo = InstrumentRepo(db)
    candles = CandleRepo(db)

    targets = _parse_instruments(instruments, [instrument] if instrument else settings.market.instruments)

    fixed_slip = (
        Decimal(str(slippage_pips))
        if slippage_pips is not None
        else Decimal(str(settings.backtest.fixed_slippage_pips))
    )
    spread_mult = (
        Decimal(str(spread_multiplier))
        if spread_multiplier is not None
        else Decimal(str(settings.backtest.spread_slippage_multiplier))
    )
    fill_model = FillModel(
        fixed_slippage_pips=fixed_slip,
        spread_slippage_multiplier=spread_mult,
    )

    from_dt = _parse_date(from_date)
    to_dt = _parse_date(to_date)

    strategies_all = build_strategies(settings)
    if strategy:
        strategies_all = [(s, c) for s, c in strategies_all if s.name == strategy]
        if not strategies_all:
            console.print(f"[red]no strategy named '{strategy}' is enabled in config[/red]")
            raise typer.Exit(2)

    table = Table(title="Backtest results")
    for col in ("instrument", "strategy", "trades", "return%", "max_dd%", "pf", "exp_R", "win%", "config_hash", "data_hash"):
        table.add_column(col)

    summary_rows: list[dict] = []
    for inst_name in targets:
        instrument_meta = instr_repo.get(inst_name)
        if instrument_meta is None:
            console.print(f"[yellow]skip[/yellow] {inst_name}: no instrument metadata; run sync-instruments")
            continue
        rows = candles.list(
            inst_name,
            granularity,  # type: ignore[arg-type]
            completed_only=True,
            from_time=from_dt,
            to_time=to_dt,
        )
        if not rows:
            console.print(f"[yellow]skip[/yellow] {inst_name}: no candles in window")
            continue
        frame = CandleFrame.from_candles(inst_name, granularity, rows)  # type: ignore[arg-type]

        for strat, cfg in strategies_all:
            data_hash = compute_data_request_hash(
                instrument=inst_name,
                granularity=granularity,
                from_time=from_dt.isoformat() if from_dt else None,
                to_time=to_dt.isoformat() if to_dt else None,
                source="oanda-or-cached",
                candle_count=len(rows),
            )
            engine = BacktestEngine(
                instrument=instrument_meta,
                strategy=strat,
                strategy_config=cfg,
                fill_model=fill_model,
                starting_equity=Decimal(str(settings.backtest.starting_equity_usd)),
                account_currency=settings.market.account_currency,
                risk_per_trade_pct=Decimal(str(settings.risk.risk_per_trade_pct)),
                max_bars_in_trade=int(cfg.get("max_bars_in_trade", 80)),
                commission_per_unit=Decimal(str(settings.backtest.commission_per_unit)),
                trailing_stop_atr_multiple=cfg.get("trailing_stop_atr_multiple"),
                atr_lookback=int(cfg.get("atr_lookback", 14)),
            )
            result = engine.run(frame, data_request_hash=data_hash)
            m = result.metrics
            table.add_row(
                inst_name,
                strat.name,
                str(m.trade_count),
                f"{m.total_return_pct:.2f}",
                f"{m.max_drawdown_pct:.2f}",
                f"{m.profit_factor:.2f}" if m.profit_factor != float("inf") else "inf",
                f"{m.expectancy_r:.3f}",
                f"{m.win_rate*100:.1f}",
                result.config_hash[:10],
                data_hash[:10],
            )

            if export_dir:
                prefix = label or f"{inst_name}_{granularity}_{strat.name}"
                paths = write_all(result, export_dir, prefix)
                console.print(f"  wrote → {paths['summary_json']}")
                summary_rows.append(
                    {
                        "instrument": inst_name,
                        "strategy": strat.name,
                        "config_hash": result.config_hash,
                        "data_request_hash": data_hash,
                        "trades": m.trade_count,
                        "return_pct": m.total_return_pct,
                        "max_dd_pct": m.max_drawdown_pct,
                        "profit_factor": (
                            None if m.profit_factor == float("inf") else m.profit_factor
                        ),
                        "expectancy_r": m.expectancy_r,
                        "win_rate": m.win_rate,
                        "summary_path": str(paths["summary_json"]),
                    }
                )

    console.print(table)
    if export_dir and summary_rows:
        index_path = export_dir / (label or "index") / "_index.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
        console.print(f"[green]wrote index[/green] {index_path}")


@app.command("audit-data")
def audit_data(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    instruments: str | None = typer.Option(None, "--instruments"),
    instrument: str | None = typer.Option(None, "--instrument", "-i"),
    granularity: str = typer.Option("H4", "--granularity", "-g"),
    from_date: str | None = typer.Option(None, "--from"),
    to_date: str | None = typer.Option(None, "--to"),
    out: Path | None = typer.Option(None, "--out", help="Write audit Markdown to this path"),
) -> None:
    """Audit stored candles for completeness, gaps, duplicates, abnormal spreads."""
    settings = _load(config)
    db = Database(settings.app.database_path)
    instr_repo = InstrumentRepo(db)
    candles = CandleRepo(db)
    targets = _parse_instruments(
        instruments, [instrument] if instrument else settings.market.instruments
    )
    from_dt = _parse_date(from_date)
    to_dt = _parse_date(to_date)

    sections: list[str] = []
    table = Table(title="Data audit")
    for col in (
        "instrument",
        "g",
        "count",
        "complete",
        "bid/ask",
        "gaps",
        "dups",
        "abn_spr",
        "first",
        "last",
        "clean",
    ):
        table.add_column(col)

    for inst_name in targets:
        instrument_meta = instr_repo.get(inst_name)
        if instrument_meta is None:
            console.print(f"[yellow]skip[/yellow] {inst_name}: no instrument metadata")
            continue
        report = audit_instrument(
            candles,
            inst_name,
            granularity,  # type: ignore[arg-type]
            requested_from=from_dt,
            requested_to=to_dt,
            pip_size=instrument_meta.pip_size,
        )
        table.add_row(
            inst_name,
            granularity,
            str(report.candle_count),
            f"{report.completed_count}/{report.candle_count}",
            f"{report.bid_available_count}/{report.ask_available_count}",
            str(len(report.missing_intervals)),
            str(len(report.duplicate_timestamps)),
            str(len(report.abnormal_spreads)),
            report.first_ts.strftime("%Y-%m-%d") if report.first_ts else "-",
            report.last_ts.strftime("%Y-%m-%d") if report.last_ts else "-",
            "[green]Y[/green]" if report.is_clean else "[red]N[/red]",
        )
        sections.append(render_audit_markdown(report))

    console.print(table)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(["# Data audit", ""] + sections), encoding="utf-8")
        console.print(f"[green]wrote[/green] {out}")


@app.command("paper-loop")
def paper_loop(
    config: Path = typer.Option(..., "--config", "-c", exists=True, dir_okay=False),
    once: bool = typer.Option(True, "--once/--forever", help="Run a single iteration and exit"),
) -> None:
    settings = _load(config)
    if settings.app.mode != "paper":
        console.print(f"[red]paper-loop requires mode=paper, got {settings.app.mode}[/red]")
        raise typer.Exit(2)
    try:
        assert_loop_strategies_approved("paper", settings.strategy.enabled)
    except StrategyNotApprovedError as exc:
        console.print(f"[red]{exc}[/red]")
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
    try:
        assert_loop_strategies_approved("demo", settings.strategy.enabled)
    except StrategyNotApprovedError as exc:
        console.print(f"[red]{exc}[/red]")
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
