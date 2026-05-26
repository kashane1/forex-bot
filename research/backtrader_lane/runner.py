"""Backtrader-lane runner contract.

A campaign-agnostic harness that:

1. Looks up a frozen campaign in the campaign registry.
2. Loads the candle data via `data_adapter.load_candles(...)`.
3. Drives `bt.Cerebro` per-pair with the campaign's adapter strategy.
4. Emits compact comparable artifacts:
    - `backtrader_summary.json` — per-pair + aggregate metrics
    - `backtrader_trades.jsonl` — one closed trade per line
    - `backtrader_metrics.json` — analyzer outputs (TradeAnalyzer, etc.)
    - `run_manifest.json` — git commit, package versions, command,
      hashes, campaign id, strategy adapter id/version, instrument list,
      date range, approximation flags
    - `run_log_summary.md` — human-readable summary

The runner does **not** approve strategies, mutate verdicts, or call
any broker / OANDA / LEAN / cloud service. It refuses to run if any
candle CSV is missing or its sha256 drifts from the committed
provenance JSON (unless `--no-strict-data` is passed; off by default).

`strategy_evidence: false`.
"""

from __future__ import annotations

import json
import os
import platform
import shlex
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from research.backtrader_lane.data_adapter import (
    DEFAULT_EXPORT_DIR,
    CandleAdapterResult,
    available_instruments,
    expected_instruments,
    load_candles,
    manifest_for,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Campaign registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BacktraderTrade:
    """One closed trade as the runner serialises it.

    Pure data — the runner never executes anything based on these
    values; they are the artefact written to disk for the comparison
    harness to read."""

    instrument: str
    side: str  # "long" | "short"
    entry_time: datetime
    entry_price: float
    exit_time: datetime
    exit_price: float
    units: int
    exit_reason: str
    bars_held: int
    pnl_quote: float
    pnl_account: float
    r_multiple: float | None
    return_pct: float | None
    fold_index: int | None = None


@dataclass(frozen=True)
class PairRunResult:
    """One pair's BT run output."""

    instrument: str
    candle_count: int
    trades: list[BacktraderTrade]
    final_cash: float
    starting_cash: float
    analyzer_outputs: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CampaignAdapter:
    """A frozen-rule campaign port.

    `runner_fn(candles, starting_equity_usd, **kwargs)` must run one
    Cerebro on one instrument and return a `PairRunResult`. The runner
    enforces no other contract on the adapter — it can use whatever
    Backtrader strategy / sizer / commissioner combination it needs.
    """

    campaign_id: str           # "CAMPAIGN_002", "CAMPAIGN_011", …
    strategy_id: str           # e.g. "trend_following 0.1.0-baseline-frozen"
    strategy_version: str
    description: str
    runner_fn: Callable[..., PairRunResult]
    default_instruments: tuple[str, ...]
    default_starting_equity_usd: float
    risk_per_trade_pct: float
    approximation_flags: tuple[str, ...]
    notes: str = ""


_CAMPAIGN_REGISTRY: dict[str, CampaignAdapter] = {}


def register_campaign(adapter: CampaignAdapter) -> None:
    """Register a campaign adapter.

    Re-registering an existing campaign id is a programmer error and
    raises immediately."""

    if adapter.campaign_id in _CAMPAIGN_REGISTRY:
        raise ValueError(f"campaign already registered: {adapter.campaign_id}")
    _CAMPAIGN_REGISTRY[adapter.campaign_id] = adapter


def list_campaigns() -> list[str]:
    return sorted(_CAMPAIGN_REGISTRY.keys())


def get_campaign(campaign_id: str) -> CampaignAdapter:
    if campaign_id not in _CAMPAIGN_REGISTRY:
        raise KeyError(
            f"unknown campaign {campaign_id!r}; registered: {list_campaigns()}"
        )
    return _CAMPAIGN_REGISTRY[campaign_id]


def clear_registry_for_testing() -> None:
    """Clear the registry. Only used by tests that need a clean slate."""

    _CAMPAIGN_REGISTRY.clear()


# ---------------------------------------------------------------------------
# Built-in smoke adapter
# ---------------------------------------------------------------------------

# The smoke adapter is the only campaign id the runner can execute end-to-end
# without a real campaign-port adapter. It is **not** a frozen campaign and
# its output is **not** evidence — it exists only so the Phase 3 runner
# harness has a deterministic round-trip target for tests.


def _smoke_runner(
    candles: CandleAdapterResult,
    starting_equity_usd: float,
    *,
    entry_bar: int = 3,
    exit_bar: int = 8,
    size: int = 1000,
) -> PairRunResult:
    """Run a one-shot deterministic Cerebro on a single pair's candles.

    Buys ``size`` units at ``entry_bar`` and sells at ``exit_bar``. The
    rising-price fixture guarantees this produces exactly one positive
    closed trade — the same property the Phase 1 smoke test exercised
    on synthetic SmokeBars, now exercised on the data-adapter output.
    """

    import backtrader as bt

    df = candles.mid_df.copy()
    # Backtrader's PandasData wants tz-naive datetime index.
    df.index = df.index.tz_convert("UTC").tz_localize(None)

    recorded: list[BacktraderTrade] = []
    captured_entry: dict[str, Any] = {}

    instrument = candles.instrument

    class _SmokeStrategy(bt.Strategy):  # pragma: no cover - bt callbacks
        params = (("entry_bar", entry_bar), ("exit_bar", exit_bar), ("size", size))

        def __init__(self) -> None:
            self._opened = False
            self._closed = False
            self._entry_idx: int | None = None

        def next(self) -> None:
            i = len(self)
            if not self._opened and i == self.p.entry_bar:
                self.buy(size=self.p.size)
                self._opened = True
                self._entry_idx = i
                captured_entry["entry_time"] = bt.num2date(self.data.datetime[0])
                captured_entry["entry_price"] = float(self.data.close[0])
            elif self._opened and not self._closed and i == self.p.exit_bar:
                self.sell(size=self.p.size)
                self._closed = True
                exit_time = bt.num2date(self.data.datetime[0])
                exit_price = float(self.data.close[0])
                entry_price = captured_entry["entry_price"]
                pnl_quote = (exit_price - entry_price) * self.p.size
                bars_held = i - (self._entry_idx or i)
                recorded.append(
                    BacktraderTrade(
                        instrument=instrument,
                        side="long",
                        entry_time=captured_entry["entry_time"].replace(tzinfo=UTC),
                        entry_price=entry_price,
                        exit_time=exit_time.replace(tzinfo=UTC),
                        exit_price=exit_price,
                        units=self.p.size,
                        exit_reason="smoke_oneshot",
                        bars_held=bars_held,
                        pnl_quote=pnl_quote,
                        pnl_account=pnl_quote,
                        r_multiple=None,
                        return_pct=None,
                    )
                )

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(starting_equity_usd)
    feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(feed)
    cerebro.addstrategy(_SmokeStrategy)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")
    results = cerebro.run()
    strat = results[0]
    ta = strat.analyzers.trade_analyzer.get_analysis()
    closed = (
        ta.total.closed
        if hasattr(ta, "total") and hasattr(ta.total, "closed")
        else len(recorded)
    )
    return PairRunResult(
        instrument=instrument,
        candle_count=candles.bar_count,
        trades=recorded,
        final_cash=float(cerebro.broker.getcash()),
        starting_cash=float(starting_equity_usd),
        analyzer_outputs={"closed_trades": int(closed)},
    )


SMOKE_CAMPAIGN = CampaignAdapter(
    campaign_id="SMOKE_FIXTURE",
    strategy_id="smoke_oneshot",
    strategy_version="0.0.0-smoke",
    description=(
        "Built-in deterministic one-shot strategy used to test the runner "
        "harness on the tiny fixture. NOT a frozen campaign. NOT evidence."
    ),
    runner_fn=_smoke_runner,
    default_instruments=("TEST_PAIR",),
    default_starting_equity_usd=10_000.0,
    risk_per_trade_pct=0.0,
    approximation_flags=(
        "SMOKE_FIXTURE_ONLY: deterministic one-shot adapter; not a real campaign",
    ),
    notes="strategy_evidence: false",
)


def _ensure_smoke_registered() -> None:
    """Register the smoke adapter once. Idempotent on import."""

    if "SMOKE_FIXTURE" not in _CAMPAIGN_REGISTRY:
        register_campaign(SMOKE_CAMPAIGN)


_ensure_smoke_registered()


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------


def _git_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
        )
        return out.decode("ascii").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _git_dirty() -> bool | None:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            stderr=subprocess.DEVNULL,
        )
        return bool(out.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    try:
        import backtrader as bt

        versions["backtrader"] = str(bt.__version__)
    except ImportError:
        versions["backtrader"] = "not-installed"
    try:
        import pandas as pd

        versions["pandas"] = str(pd.__version__)
    except ImportError:
        versions["pandas"] = "not-installed"
    return versions


def build_manifest(
    *,
    campaign: CampaignAdapter,
    command: str,
    instruments_run: list[str],
    instruments_blocked: list[str],
    data_manifests: list[dict[str, Any]],
    starting_equity_usd: float,
    strict_data: bool,
) -> dict[str, Any]:
    """Assemble the run manifest."""

    return {
        "_meta": {
            "description": (
                "Backtrader secondary-lane run manifest. Verification only — "
                "strategy_evidence: false. CAMPAIGN_002, CAMPAIGN_010, "
                "CAMPAIGN_011, CAMPAIGN_012, CAMPAIGN_013 remain rejected/null/"
                "research-only. CAMPAIGN_014 remains scaffold-only. Paper/"
                "demo/live remain blocked."
            ),
            "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        },
        "command": command,
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "packages": _package_versions(),
        "campaign": {
            "campaign_id": campaign.campaign_id,
            "strategy_id": campaign.strategy_id,
            "strategy_version": campaign.strategy_version,
            "description": campaign.description,
            "approximation_flags": list(campaign.approximation_flags),
            "notes": campaign.notes,
        },
        "instruments": {
            "requested": sorted(set(instruments_run + instruments_blocked)),
            "run": sorted(instruments_run),
            "blocked": sorted(instruments_blocked),
        },
        "data": {
            "strict_mode": strict_data,
            "per_instrument": data_manifests,
        },
        "execution": {
            "starting_equity_usd": starting_equity_usd,
            "risk_per_trade_pct": campaign.risk_per_trade_pct,
        },
        "strategy_evidence": False,
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def _trade_to_jsonl(t: BacktraderTrade) -> str:
    payload: dict[str, Any] = {
        "instrument": t.instrument,
        "side": t.side,
        "entry_time": t.entry_time.isoformat(),
        "entry_price": t.entry_price,
        "exit_time": t.exit_time.isoformat(),
        "exit_price": t.exit_price,
        "units": t.units,
        "exit_reason": t.exit_reason,
        "bars_held": t.bars_held,
        "pnl_quote": t.pnl_quote,
        "pnl_account": t.pnl_account,
        "r_multiple": t.r_multiple,
        "return_pct": t.return_pct,
    }
    if t.fold_index is not None:
        payload["fold_index"] = t.fold_index
    return json.dumps(payload, sort_keys=True)


def write_trades_jsonl(path: Path, trades: list[BacktraderTrade]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for t in trades:
            fh.write(_trade_to_jsonl(t))
            fh.write("\n")


def _build_summary(
    *,
    campaign: CampaignAdapter,
    pair_results: list[PairRunResult],
    instruments_blocked: list[str],
    starting_equity_usd: float,
) -> dict[str, Any]:
    per_pair: list[dict[str, Any]] = []
    total_trades = 0
    total_pnl_account = 0.0
    for pr in pair_results:
        pnl_total = sum(t.pnl_account for t in pr.trades)
        wins = sum(1 for t in pr.trades if t.pnl_account > 0)
        losses = sum(1 for t in pr.trades if t.pnl_account < 0)
        win_rate = (wins / len(pr.trades)) if pr.trades else None
        per_pair.append(
            {
                "instrument": pr.instrument,
                "candle_count": pr.candle_count,
                "trades": len(pr.trades),
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "pnl_account_total": pnl_total,
                "final_cash": pr.final_cash,
                "starting_cash": pr.starting_cash,
                "analyzer": pr.analyzer_outputs,
            }
        )
        total_trades += len(pr.trades)
        total_pnl_account += pnl_total
    return {
        "campaign_id": campaign.campaign_id,
        "strategy_id": campaign.strategy_id,
        "strategy_version": campaign.strategy_version,
        "starting_equity_usd": starting_equity_usd,
        "total_trades": total_trades,
        "total_pnl_account": total_pnl_account,
        "pairs": per_pair,
        "blocked_instruments": instruments_blocked,
        "strategy_evidence": False,
    }


def _render_log_summary_md(
    *, summary: dict[str, Any], manifest: dict[str, Any]
) -> str:
    lines: list[str] = []
    lines.append(f"# Backtrader Lane — Run Log — `{summary['campaign_id']}`")
    lines.append("")
    lines.append(
        "> `strategy_evidence: false`. Verification infrastructure only. "
        "Does not approve any strategy. Paper / demo / live remain blocked."
    )
    lines.append("")
    lines.append(f"- generated_at: `{manifest['_meta']['generated_at']}`")
    lines.append(f"- git_commit: `{manifest['git_commit']}`")
    lines.append(f"- git_dirty: `{manifest['git_dirty']}`")
    lines.append(f"- backtrader: `{manifest['packages']['backtrader']}`")
    lines.append(
        f"- python: `{manifest['packages']['python']}` "
        f"on `{manifest['packages']['platform']}`"
    )
    lines.append(f"- strategy: `{summary['strategy_id']}` `{summary['strategy_version']}`")
    lines.append(
        f"- instruments run: {len(manifest['instruments']['run'])} · "
        f"blocked: {len(manifest['instruments']['blocked'])}"
    )
    lines.append(f"- total trades: **{summary['total_trades']}**")
    lines.append(f"- total PnL (account ccy): **{summary['total_pnl_account']:.4f}**")
    lines.append("")
    lines.append("| instrument | candles | trades | wins | losses | win rate | PnL acct |")
    lines.append("|---|---|---|---|---|---|---|")
    for pair in summary["pairs"]:
        wr = (
            f"{pair['win_rate']:.4f}"
            if pair["win_rate"] is not None
            else "—"
        )
        lines.append(
            f"| {pair['instrument']} | {pair['candle_count']} | {pair['trades']} | "
            f"{pair['wins']} | {pair['losses']} | {wr} | "
            f"{pair['pnl_account_total']:.4f} |"
        )
    if summary["blocked_instruments"]:
        lines.append("")
        lines.append("### Blocked instruments")
        for name in summary["blocked_instruments"]:
            lines.append(f"- `{name}` — CSV / provenance missing or sha drift")
    lines.append("")
    lines.append("### Approximation flags")
    for flag in manifest["campaign"]["approximation_flags"]:
        lines.append(f"- {flag}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Runner entry point
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunOptions:
    campaign_id: str
    output_dir: Path
    instruments: list[str] | None = None
    data_export_dir: Path = DEFAULT_EXPORT_DIR
    starting_equity_usd: float | None = None
    dry_run: bool = False
    strict_data: bool = True
    # ``full`` — iterate the entire CSV (legacy behaviour).
    # ``fold_windows`` — run each walk-forward test window independently.
    run_mode: str = "full"
    fold_plan_path: Path | None = None
    warmup_days: int = 90
    # When True, only count trades whose entry falls inside the fold
    # test window. When False (default for CAMPAIGN_015 fold mode),
    # mirror the bespoke engine which counts trades in the 90-day
    # warmup margin before ``test_start``.
    strict_test_window: bool = False
    entry_bar_stop_policy: str = "backtrader_default"
    risk_engine_parity: bool = False


def _resolve_instruments(
    campaign: CampaignAdapter, options: RunOptions
) -> list[str]:
    if options.instruments:
        return list(options.instruments)
    return list(campaign.default_instruments)


def preflight(options: RunOptions) -> dict[str, Any]:
    """Inspect data availability without running Cerebro.

    Returns a dict the runner / dry-run reports to the caller.
    """

    campaign = get_campaign(options.campaign_id)
    instruments = _resolve_instruments(campaign, options)
    if options.run_mode == "fold_windows":
        if options.fold_plan_path is None:
            raise ValueError("fold_windows mode requires fold_plan_path")
        from research.backtrader_lane.fold_windows import (
            fold_specs_from_plan,
            load_fold_plan,
            preflight_fold_windows,
        )

        plan = load_fold_plan(options.fold_plan_path)
        specs = fold_specs_from_plan(plan, warmup_days=options.warmup_days)

        def _load(name: str) -> CandleAdapterResult:
            return load_candles(
                name,
                export_dir=options.data_export_dir,
                strict=options.strict_data,
            )

        pf = preflight_fold_windows(
            instruments=instruments,
            fold_specs=specs,
            load_fn=_load,
        )
        pf["campaign_id"] = campaign.campaign_id
        pf["fold_plan_path"] = str(options.fold_plan_path)
        pf["dry_run"] = options.dry_run
        return pf

    expected = expected_instruments(options.data_export_dir)
    available = available_instruments(options.data_export_dir)
    blocked: list[str] = []
    runnable: list[str] = []
    for name in instruments:
        if name in available:
            runnable.append(name)
        else:
            blocked.append(name)
    return {
        "campaign_id": campaign.campaign_id,
        "run_mode": options.run_mode,
        "instruments_requested": instruments,
        "instruments_runnable": runnable,
        "instruments_blocked": blocked,
        "expected_in_export_dir": expected,
        "available_in_export_dir": available,
        "export_dir": str(options.data_export_dir),
        "dry_run": options.dry_run,
    }


def _write_run_artifacts(
    *,
    options: RunOptions,
    campaign: CampaignAdapter,
    manifest: dict[str, Any],
    summary: dict[str, Any],
    pair_results: list[PairRunResult],
) -> None:
    options.output_dir.mkdir(parents=True, exist_ok=True)
    (options.output_dir / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (options.output_dir / "backtrader_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    all_trades: list[BacktraderTrade] = []
    for pr in pair_results:
        all_trades.extend(pr.trades)
    write_trades_jsonl(options.output_dir / "backtrader_trades.jsonl", all_trades)
    metrics: dict[str, Any] = {
        "per_pair": [
            {
                "instrument": pr.instrument,
                "analyzer": pr.analyzer_outputs,
                "final_cash": pr.final_cash,
                "starting_cash": pr.starting_cash,
            }
            for pr in pair_results
        ],
    }
    (options.output_dir / "backtrader_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    log_md = _render_log_summary_md(summary=summary, manifest=manifest)
    (options.output_dir / "run_log_summary.md").write_text(log_md, encoding="utf-8")

    forbidden_env_keys = (
        "OANDA_TOKEN",
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "OANDA_ACCOUNT",
    )
    manifest_text = (options.output_dir / "run_manifest.json").read_text(encoding="utf-8")
    for key in forbidden_env_keys:
        if key in manifest_text:
            raise RuntimeError(
                f"manifest accidentally references {key}; refusing to keep it."
            )
        value = os.environ.get(key)
        if value and value in manifest_text:
            raise RuntimeError(
                "manifest contains a value that matches an OANDA env var; refusing to keep it."
            )


def run_fold_windows(options: RunOptions) -> dict[str, Any]:
    """Run the campaign once per walk-forward fold test window.

    Each fold × instrument is an independent run with equity reset to
    ``starting_equity_usd``. Candle data is sliced to
    ``[test_start - warmup_days, test_end]`` inclusive, matching the
    bespoke ``run_campaign_015.py`` loader.
    """

    if options.fold_plan_path is None:
        raise ValueError("fold_windows mode requires fold_plan_path")

    from research.backtrader_lane.fold_windows import (
        entry_in_test_window,
        fold_specs_from_plan,
        load_fold_plan,
        slice_candles,
    )

    campaign = get_campaign(options.campaign_id)
    starting_equity_usd = (
        options.starting_equity_usd
        if options.starting_equity_usd is not None
        else campaign.default_starting_equity_usd
    )
    instruments = _resolve_instruments(campaign, options)
    plan = load_fold_plan(options.fold_plan_path)
    fold_specs = fold_specs_from_plan(plan, warmup_days=options.warmup_days)

    options.output_dir.mkdir(parents=True, exist_ok=True)
    data_manifests: list[dict[str, Any]] = []
    instruments_blocked: set[str] = set()
    all_pair_results: list[PairRunResult] = []
    fold_summaries: list[dict[str, Any]] = []
    per_fold_pair_trades: dict[str, dict[str, int]] = {}

    loaded: dict[str, CandleAdapterResult] = {}
    for name in instruments:
        try:
            loaded[name] = load_candles(
                name,
                export_dir=options.data_export_dir,
                strict=options.strict_data,
            )
            data_manifests.append(manifest_for(loaded[name]))
        except FileNotFoundError:
            instruments_blocked.add(name)

    runner_kwargs_base: dict[str, Any] = {
        "strict_test_window": options.strict_test_window,
        "entry_bar_stop_policy": options.entry_bar_stop_policy,
        "risk_engine_parity": options.risk_engine_parity,
    }

    for spec in fold_specs:
        fold_dir = options.output_dir / "folds" / f"fold_{spec.fold_index:02d}"
        fold_pair_results: list[PairRunResult] = []
        fold_trades: list[BacktraderTrade] = []
        fold_blocked: list[str] = []

        for name in instruments:
            if name in instruments_blocked:
                fold_blocked.append(name)
                continue
            try:
                sliced = slice_candles(
                    loaded[name],
                    from_time=spec.candle_load_start,
                    to_time=spec.candle_load_end,
                )
            except ValueError:
                fold_blocked.append(name)
                continue
            if options.dry_run:
                continue
            pair_result = campaign.runner_fn(
                sliced,
                starting_equity_usd,
                fold_window=spec,
                **runner_kwargs_base,
            )
            counted = [
                t
                for t in pair_result.trades
                if entry_in_test_window(
                    t.entry_time,
                    test_start=spec.test_start,
                    test_end=spec.test_end,
                    strict=options.strict_test_window,
                )
            ]
            tagged = [
                BacktraderTrade(
                    instrument=t.instrument,
                    side=t.side,
                    entry_time=t.entry_time,
                    entry_price=t.entry_price,
                    exit_time=t.exit_time,
                    exit_price=t.exit_price,
                    units=t.units,
                    exit_reason=t.exit_reason,
                    bars_held=t.bars_held,
                    pnl_quote=t.pnl_quote,
                    pnl_account=t.pnl_account,
                    r_multiple=t.r_multiple,
                    return_pct=t.return_pct,
                    fold_index=spec.fold_index,
                )
                for t in counted
            ]
            fold_trades.extend(tagged)
            fold_pair_results.append(
                PairRunResult(
                    instrument=pair_result.instrument,
                    candle_count=pair_result.candle_count,
                    trades=tagged,
                    final_cash=pair_result.final_cash,
                    starting_cash=pair_result.starting_cash,
                    analyzer_outputs={
                        **pair_result.analyzer_outputs,
                        "closed_trades": len(tagged),
                    },
                )
            )
            per_fold_pair_trades.setdefault(f"fold_{spec.fold_index:02d}", {})[name] = len(
                tagged
            )

        all_pair_results.extend(fold_pair_results)

        fold_total = sum(len(pr.trades) for pr in fold_pair_results)
        fold_summary = {
            "fold_index": spec.fold_index,
            "test_start": str(spec.test_start),
            "test_end": str(spec.test_end),
            "total_trades": fold_total,
            "blocked_instruments": sorted(fold_blocked),
            "pairs": [
                {
                    "instrument": pr.instrument,
                    "trades": len(pr.trades),
                    "candle_count": pr.candle_count,
                }
                for pr in fold_pair_results
            ],
        }
        fold_summaries.append(fold_summary)

        if not options.dry_run:
            fold_dir.mkdir(parents=True, exist_ok=True)
            write_trades_jsonl(fold_dir / "backtrader_trades.jsonl", fold_trades)
            (fold_dir / "fold_summary.json").write_text(
                json.dumps(fold_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

    instruments_run = sorted({pr.instrument for pr in all_pair_results})
    command = "python " + " ".join(shlex.quote(arg) for arg in sys.argv[1:])
    manifest = build_manifest(
        campaign=campaign,
        command=command,
        instruments_run=instruments_run,
        instruments_blocked=sorted(instruments_blocked),
        data_manifests=data_manifests,
        starting_equity_usd=starting_equity_usd,
        strict_data=options.strict_data,
    )
    manifest["run_mode"] = "fold_windows"
    manifest["fold_plan_path"] = str(options.fold_plan_path)
    manifest["warmup_days"] = options.warmup_days
    manifest["strict_test_window"] = options.strict_test_window
    manifest["entry_bar_stop_policy"] = options.entry_bar_stop_policy
    manifest["risk_engine_parity"] = options.risk_engine_parity
    manifest["fold_count"] = len(fold_specs)
    manifest["approximation_flags"] = list(campaign.approximation_flags) + [
        (
            "FOLD_WINDOW_BESPOKE_MIRROR: each fold × pair is an independent "
            "run with equity reset; candle slice matches "
            "run_campaign_015.py _fold_dates_to_dts (90-day warmup margin)."
        ),
        (
            "STRICT_TEST_WINDOW="
            f"{options.strict_test_window}: when false, trades with "
            "entry_time before test_start inside the warmup margin are "
            "counted (mirrors bespoke engine behaviour)."
        ),
    ]

    # Aggregate per-instrument across folds.
    agg_by_pair: dict[str, dict[str, Any]] = {}
    for pr in all_pair_results:
        bucket = agg_by_pair.setdefault(
            pr.instrument,
            {
                "instrument": pr.instrument,
                "candle_count": 0,
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "pnl_account_total": 0.0,
            },
        )
        bucket["candle_count"] += pr.candle_count
        bucket["trades"] += len(pr.trades)
        bucket["wins"] += sum(1 for t in pr.trades if t.pnl_account > 0)
        bucket["losses"] += sum(1 for t in pr.trades if t.pnl_account < 0)
        bucket["pnl_account_total"] += sum(t.pnl_account for t in pr.trades)

    pair_rows: list[dict[str, Any]] = []
    for name in sorted(agg_by_pair):
        b = agg_by_pair[name]
        n = b["trades"]
        pair_rows.append(
            {
                **b,
                "win_rate": (b["wins"] / n) if n else None,
                "final_cash": None,
                "starting_cash": starting_equity_usd,
                "analyzer": {"closed_trades": n},
            }
        )

    total_trades = sum(b["trades"] for b in agg_by_pair.values())
    total_pnl = sum(b["pnl_account_total"] for b in agg_by_pair.values())
    aggregate_rejections: dict[str, int] = {}
    for pr in all_pair_results:
        rc = pr.analyzer_outputs.get("rejection_counts", {})
        for code, count in rc.items():
            aggregate_rejections[code] = aggregate_rejections.get(code, 0) + int(count)
    summary = {
        "campaign_id": campaign.campaign_id,
        "strategy_id": campaign.strategy_id,
        "strategy_version": campaign.strategy_version,
        "starting_equity_usd": starting_equity_usd,
        "total_trades": total_trades,
        "total_pnl_account": total_pnl,
        "pairs": pair_rows,
        "blocked_instruments": sorted(instruments_blocked),
        "strategy_evidence": False,
        "dry_run": options.dry_run,
        "run_mode": "fold_windows",
        "fold_count": len(fold_specs),
        "strict_test_window": options.strict_test_window,
        "entry_bar_stop_policy": options.entry_bar_stop_policy,
        "risk_engine_parity": options.risk_engine_parity,
        "rejection_counts": aggregate_rejections if options.risk_engine_parity else {},
        "fold_summaries": fold_summaries,
        "per_fold_pair_trades": per_fold_pair_trades,
    }

    _write_run_artifacts(
        options=options,
        campaign=campaign,
        manifest=manifest,
        summary=summary,
        pair_results=all_pair_results,
    )
    return summary


def run(options: RunOptions) -> dict[str, Any]:
    """Execute the configured campaign in the Backtrader lane.

    Writes ``run_manifest.json``, ``backtrader_summary.json``,
    ``backtrader_trades.jsonl``, ``backtrader_metrics.json``, and
    ``run_log_summary.md`` to ``options.output_dir``. Returns the
    summary dict.
    """

    if options.run_mode == "fold_windows":
        return run_fold_windows(options)

    campaign = get_campaign(options.campaign_id)
    starting_equity_usd = (
        options.starting_equity_usd
        if options.starting_equity_usd is not None
        else campaign.default_starting_equity_usd
    )
    instruments = _resolve_instruments(campaign, options)
    options.output_dir.mkdir(parents=True, exist_ok=True)

    data_manifests: list[dict[str, Any]] = []
    pair_results: list[PairRunResult] = []
    instruments_blocked: list[str] = []

    for name in instruments:
        try:
            candles = load_candles(
                name,
                export_dir=options.data_export_dir,
                strict=options.strict_data,
            )
        except FileNotFoundError:
            instruments_blocked.append(name)
            continue
        data_manifests.append(manifest_for(candles))
        if options.dry_run:
            continue
        pair_results.append(
            campaign.runner_fn(candles, starting_equity_usd)
        )

    instruments_run = [pr.instrument for pr in pair_results]

    command = "python " + " ".join(shlex.quote(arg) for arg in sys.argv[1:])
    manifest = build_manifest(
        campaign=campaign,
        command=command,
        instruments_run=instruments_run,
        instruments_blocked=instruments_blocked,
        data_manifests=data_manifests,
        starting_equity_usd=starting_equity_usd,
        strict_data=options.strict_data,
    )
    summary = _build_summary(
        campaign=campaign,
        pair_results=pair_results,
        instruments_blocked=instruments_blocked,
        starting_equity_usd=starting_equity_usd,
    )
    summary["dry_run"] = options.dry_run
    summary["run_mode"] = "full"
    manifest["run_mode"] = "full"

    _write_run_artifacts(
        options=options,
        campaign=campaign,
        manifest=manifest,
        summary=summary,
        pair_results=pair_results,
    )

    return summary
