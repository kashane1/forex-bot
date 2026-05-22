#!/usr/bin/env python3
"""Diagnostic-only smoke check: the D1AGG + next_bar_open fill path.

THIS IS NOT A STRATEGY CAMPAIGN. It produces NO strategy verdict, NO
trading recommendation, NO approval, and opens NO test-window research
decision. It exercises plumbing only:

  * H4 -> D1AGG aggregation (when a real OANDA H4 candle store exists);
  * the next_bar_open fill timing running on D1AGG bars;
  * rollover-blackout safety of D1AGG timestamps (and, by extension,
    that a rollover-window session filter would not block them);
  * explicit detection of a missing bar N+1.

A deterministic fixed-bar *diagnostic probe* drives the engine. The
probe has no indicators, no parameters, and no edge logic — its
"trades" are mechanical artifacts, never strategy evidence.

Real data only. The smoke refuses synthetic candles. If no real OANDA
H4 store is available it documents that as a blocker and still runs the
mechanical D1AGG -> next_bar_open verification on the committed,
provenance-tracked EUR_USD D1AGG sample.

Usage:
    python scripts/smoke_d1agg_next_open.py [--db PATH] [--out PATH]

See docs/research/FILL_TIMING_MODEL.md and
docs/research/D1_AGGREGATION_DESIGN.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.backtesting.d1_aggregation import (
    AGG_GRANULARITY,
    aggregate_h4_to_d1,
    rollover_safe,
)
from forex_bot.backtesting.engine import BacktestEngine, BacktestResult
from forex_bot.backtesting.fills import NEXT_BAR_OPEN_UNAVAILABLE, FillModel
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo
from forex_bot.domain.candles import Candle, CandleFrame
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.signals import Signal
from forex_bot.strategies.base import StrategyContext

SIX_MAJORS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
# The rehydrated real-OANDA H4 store (scripts/rehydrate_oanda_h4_store.py).
DEFAULT_DB = ROOT / "data" / "oanda_h4_research.sqlite3"
SAMPLE_CSV = ROOT / "research" / "d1_aggregation" / "sample_EUR_USD_H4_to_D1.csv"
DEFAULT_OUT = ROOT / "backtests" / "diagnostics" / "d1agg_next_open_six_pair_smoke.md"

# Per-major pip metadata. USD_JPY is the only JPY pair (pip_location -2).
_PIP_LOCATION = {"USD_JPY": -2}
_DISPLAY_PRECISION = {"USD_JPY": 3}

_ZERO_FILL = FillModel(
    fixed_slippage_pips=Decimal("0"), spread_slippage_multiplier=Decimal("0")
)


# --------------------------------------------------------------------------
# Result containers
# --------------------------------------------------------------------------


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


@dataclass
class InstrumentSmoke:
    instrument: str
    data_source: str
    d1agg_count: int
    data_hash: str | None = None
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.checks) and all(c.ok for c in self.checks)


# --------------------------------------------------------------------------
# Diagnostic probe — NOT a strategy
# --------------------------------------------------------------------------


class DiagnosticProbe:
    """A deterministic fixed-bar probe. It is NOT a strategy: no
    indicators, no parameters, no edge logic. It emits exactly one long
    signal on a chosen bar purely to drive the engine's fill plumbing.
    Its output is a mechanical artifact and is NEVER strategy evidence."""

    name = "diagnostic_probe"
    version = "0.0.0-diagnostic"

    def __init__(self, fire_at_len: int) -> None:
        self._fire_at_len = fire_at_len

    def warmup_bars_required(self) -> int:
        return 2

    def generate_signal(self, ctx: StrategyContext) -> Signal | None:
        df = ctx.candles.df
        if len(df) != self._fire_at_len:
            return None
        ts = df.index[-1]
        close = Decimal(str(df["close"].iloc[-1]))
        return Signal(
            signal_id=f"probe-{self._fire_at_len}",
            strategy_name=self.name,
            strategy_version=self.version,
            instrument=ctx.instrument.name,
            timeframe=AGG_GRANULARITY,
            timestamp=ts.to_pydatetime(),
            side="long",
            stop_model="diagnostic",
            # A deliberately wide stop: the probe exercises ENTRY plumbing,
            # not exit logic, so it should not be stopped out.
            stop_price=close * Decimal("0.95"),
            exit_model="diagnostic",
        )


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------


def make_instrument(name: str) -> Instrument:
    return Instrument(
        name=name,
        type="CURRENCY",
        display_precision=_DISPLAY_PRECISION.get(name, 5),
        pip_location=_PIP_LOCATION.get(name, -4),
        trade_units_precision=0,
        minimum_trade_size=Decimal("1"),
        maximum_order_units=Decimal("100000000"),
        margin_rate=Decimal("0.02"),
    )


def distinct_h4_sources(db: Database, instrument: str) -> list[str]:
    rows = db.fetchall(
        "SELECT DISTINCT source FROM candles WHERE instrument=? AND granularity='H4'",
        (instrument,),
    )
    return sorted(str(r["source"]) for r in rows)


def load_d1agg_sample(csv_path: Path) -> list[Candle]:
    """Parse the committed real-OANDA-derived D1AGG sample CSV."""
    out: list[Candle] = []
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["granularity"] != AGG_GRANULARITY:
                raise ValueError(
                    f"{csv_path} has a non-D1AGG row: {row['granularity']!r}"
                )
            out.append(
                Candle(
                    instrument="EUR_USD",
                    granularity=AGG_GRANULARITY,
                    time=datetime.fromisoformat(row["time"]),
                    complete=row["complete"].strip().lower() == "true",
                    volume=int(row["volume"]),
                    bid_o=Decimal(row["bid_o"]), bid_h=Decimal(row["bid_h"]),
                    bid_l=Decimal(row["bid_l"]), bid_c=Decimal(row["bid_c"]),
                    ask_o=Decimal(row["ask_o"]), ask_h=Decimal(row["ask_h"]),
                    ask_l=Decimal(row["ask_l"]), ask_c=Decimal(row["ask_c"]),
                )
            )
    return out


def check_sample_provenance(csv_path: Path) -> Check:
    """The committed D1AGG sample must carry real-OANDA provenance — a
    source H4 count and a 64-hex source hash from aggregate_h4_to_d1."""
    meta_path = csv_path.with_suffix(".meta.json")
    if not meta_path.exists():
        return Check("data_is_real_oanda", False, f"no provenance meta beside {csv_path.name}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    h4_count = int(meta.get("source_h4_count", 0))
    src_hash = str(meta.get("source_hash", ""))
    src = str(meta.get("source", "")).lower()
    if h4_count > 0 and len(src_hash) == 64 and "aggregation" in src:
        return Check(
            "data_is_real_oanda", True,
            f"committed sample derived from {h4_count} real OANDA H4 candles, "
            f"source_hash {src_hash[:16]}… — not synthetic",
        )
    return Check(
        "data_is_real_oanda", False,
        f"sample provenance incomplete in {meta_path.name}",
    )


# --------------------------------------------------------------------------
# Mechanical checks
# --------------------------------------------------------------------------


def check_blackout(d1agg: list[Candle]) -> Check:
    """Every D1AGG timestamp must clear the NY rollover blackout. A bar
    that cleared the blackout would also clear a rollover-window session
    filter — that is the whole point of the D1AGG construction."""
    bad = [c.time.isoformat() for c in d1agg if not rollover_safe(c.time)]
    if bad:
        return Check(
            "d1agg_timestamps_clear_blackout", False,
            f"{len(bad)} D1AGG bar(s) inside the rollover blackout: {bad[:3]}",
        )
    return Check(
        "d1agg_timestamps_clear_blackout", True,
        f"all {len(d1agg)} D1AGG timestamps clear the 16:45–17:15 NY rollover "
        "blackout (so a rollover-window session filter would not block them)",
    )


def check_next_bar_open_data_available(d1agg: list[Candle]) -> Check:
    """Structural: every non-final D1AGG bar has a successor carrying an
    open bid/ask — a next_bar_open fill is available for it."""
    if len(d1agg) < 2:
        return Check("next_bar_open_data_available", False, "fewer than 2 D1AGG bars")
    missing = [
        d1agg[k + 1].time.isoformat()
        for k in range(len(d1agg) - 1)
        if d1agg[k + 1].bid_o is None or d1agg[k + 1].ask_o is None
    ]
    if missing:
        return Check(
            "next_bar_open_data_available", False,
            f"{len(missing)} successor bar(s) lack an open quote: {missing[:3]}",
        )
    return Check(
        "next_bar_open_data_available", True,
        f"all {len(d1agg) - 1} non-final D1AGG bars have a usable next-bar open quote",
    )


def _run_probe(
    instrument: Instrument, d1agg: list[Candle], fire_at_len: int
) -> BacktestResult:
    frame = CandleFrame.from_candles(instrument.name, AGG_GRANULARITY, d1agg)
    engine = BacktestEngine(
        instrument=instrument,
        strategy=DiagnosticProbe(fire_at_len),
        strategy_config={},
        fill_model=_ZERO_FILL,
        fill_timing="next_bar_open",
        starting_equity=Decimal("500"),
        account_currency="USD",
        max_bars_in_trade=10_000,
    )
    return engine.run(frame)


def check_engine_fills_at_next_open(
    instrument: Instrument, d1agg: list[Candle]
) -> Check:
    """End-to-end: the engine, on D1AGG bars with next_bar_open, fills a
    probe entry at bar N+1's open — never the signal bar's close."""
    if len(d1agg) < 10:
        return Check(
            "engine_fills_at_next_bar_open", False,
            f"need >= 10 D1AGG bars to probe, have {len(d1agg)}",
        )
    fire_len = 7  # window length 7 -> signal bar index 6 (engine warmup is 5)
    result = _run_probe(instrument, d1agg, fire_at_len=fire_len)
    if len(result.trades) != 1:
        return Check(
            "engine_fills_at_next_bar_open", False,
            f"diagnostic probe produced {len(result.trades)} trades, expected 1",
        )
    trade = result.trades[0]
    fill_bar = d1agg[fire_len]  # bar index 7 = N+1 of signal bar index 6
    expected_entry = Decimal(str(float(fill_bar.ask_o)))  # mirrors engine float round-trip
    if (
        trade.fill_timing == "next_bar_open"
        and trade.entry_price == expected_entry
        and trade.entry_time == fill_bar.time
    ):
        return Check(
            "engine_fills_at_next_bar_open", True,
            f"probe entry filled at D1AGG bar N+1 open: "
            f"{fill_bar.time.date()} ask_open={fill_bar.ask_o}",
        )
    return Check(
        "engine_fills_at_next_bar_open", False,
        f"probe entry {trade.entry_price}@{trade.entry_time} "
        f"(fill_timing={trade.fill_timing}) != bar N+1 open "
        f"{expected_entry}@{fill_bar.time}",
    )


def check_missing_bar_detected(
    instrument: Instrument, d1agg: list[Candle]
) -> Check:
    """A probe signal on the final D1AGG bar has no bar N+1 — it must be
    recorded as an explicit NEXT_BAR_OPEN_UNAVAILABLE skip, no trade."""
    if len(d1agg) < 7:
        return Check("missing_next_bar_detected", False, "fewer than 7 D1AGG bars")
    result = _run_probe(instrument, d1agg, fire_at_len=len(d1agg))
    skipped = [
        r for r in result.rejected_signals
        if NEXT_BAR_OPEN_UNAVAILABLE in r.rejection_codes
    ]
    if len(result.trades) == 0 and len(skipped) == 1:
        return Check(
            "missing_next_bar_detected", True,
            f"final-bar probe signal recorded as an explicit "
            f"{NEXT_BAR_OPEN_UNAVAILABLE} skip; no trade opened",
        )
    return Check(
        "missing_next_bar_detected", False,
        f"final-bar probe: {len(result.trades)} trade(s), {len(skipped)} skip(s) "
        "— expected 0 trades and 1 skip",
    )


def smoke_instrument(
    instrument: Instrument,
    d1agg: list[Candle],
    *,
    data_source: str,
    provenance: Check,
    data_hash: str | None = None,
) -> InstrumentSmoke:
    smoke = InstrumentSmoke(instrument.name, data_source, len(d1agg), data_hash=data_hash)
    smoke.checks.append(provenance)
    smoke.checks.append(check_blackout(d1agg))
    smoke.checks.append(check_next_bar_open_data_available(d1agg))
    smoke.checks.append(check_engine_fills_at_next_open(instrument, d1agg))
    smoke.checks.append(check_missing_bar_detected(instrument, d1agg))
    return smoke


def smoke_from_store(
    db_path: Path,
) -> tuple[list[InstrumentSmoke], list[str], dict[str, str]]:
    """Run the six-pair smoke against a real OANDA H4 store: aggregate
    each major to D1AGG and smoke it. Returns the per-instrument smokes,
    any blockers, and a six-pair coverage map. Synthetic-sourced candles
    are refused outright."""
    db = Database(db_path)
    repo = CandleRepo(db)
    smokes: list[InstrumentSmoke] = []
    blockers: list[str] = []
    coverage: dict[str, str] = {}
    for pair in SIX_MAJORS:
        h4 = repo.list(pair, "H4", completed_only=True)
        if not h4:
            blockers.append(f"{pair}: no H4 candles in the store")
            coverage[pair] = "blocked — no H4 candles in store"
            continue
        sources = distinct_h4_sources(db, pair)
        if not sources or not all(s.startswith("oanda") for s in sources):
            blockers.append(
                f"{pair}: H4 source(s) {sources} are not real OANDA — refused"
            )
            coverage[pair] = f"refused — non-OANDA source {sources}"
            continue
        agg = aggregate_h4_to_d1(list(h4), instrument=pair)
        provenance = Check(
            "data_is_real_oanda", True,
            f"H4 source(s) {sources}; {agg.aggregated_count} trading days "
            f"aggregated; source_hash {agg.source_hash[:16]}…",
        )
        smokes.append(
            smoke_instrument(
                make_instrument(pair), agg.candles,
                data_source=f"OANDA H4 → D1AGG ({len(h4)} H4 bars)",
                provenance=provenance,
                data_hash=agg.source_hash,
            )
        )
        coverage[pair] = (
            f"aggregated — {agg.aggregated_count} D1AGG bars, "
            f"source_hash {agg.source_hash[:12]}…"
        )
    return smokes, blockers, coverage


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


def render_report(
    mode: str,
    smokes: list[InstrumentSmoke],
    blockers: list[str],
    coverage: dict[str, str],
) -> str:
    all_ok = bool(smokes) and all(s.ok for s in smokes)
    lines = [
        "# D1AGG + next-bar-open — six-pair diagnostic smoke report",
        "",
        "**DIAGNOSTIC-ONLY.** This report contains **no strategy evidence**, "
        "**no trading recommendation**, and **no approval**. It is a "
        "mechanical plumbing check of the D1AGG aggregation path and the "
        "`next_bar_open` fill timing across the six major pairs. The engine "
        "here is driven by a deterministic fixed-bar *diagnostic probe* with "
        "no indicators and no edge logic; its trades are mechanical "
        "artifacts, not results. No strategy was run, no campaign was opened, "
        "no test-window research decision was made, and the research freeze "
        "is unaffected.",
        "",
        f"- Generated: `{datetime.now().isoformat(timespec='seconds')}`",
        f"- Data mode: **{mode}**",
        f"- Overall mechanical status: **{'PASS' if all_ok else 'FAIL'}**",
        "- See `docs/research/FILL_TIMING_MODEL.md`, "
        "`docs/research/D1_AGGREGATION_DESIGN.md`, and "
        "`docs/research/OANDA_H4_DATA_REHYDRATION.md`.",
        "",
        "## Instrument coverage (six majors)",
        "",
        "| pair | status |",
        "|---|---|",
    ]
    for pair in SIX_MAJORS:
        lines.append(f"| {pair} | {coverage.get(pair, 'not evaluated')} |")
    lines.append("")

    if blockers:
        lines += ["## Blockers / limitations", ""]
        lines += [f"- {b}" for b in blockers]
        lines += [
            "",
            "A blocker here is a *data-availability* limitation, not a "
            "mechanical failure. The six-pair H4→D1AGG smoke needs a real "
            "OANDA practice H4 store — rebuild it with "
            "`scripts/rehydrate_oanda_h4_store.py` (see "
            "`docs/research/OANDA_H4_DATA_REHYDRATION.md`). The store is "
            "gitignored and never committed. The mechanical "
            "D1AGG→`next_bar_open` verification below still runs on real, "
            "provenance-tracked data.",
            "",
        ]

    for smoke in smokes:
        lines += [
            f"## {smoke.instrument}",
            "",
            f"- Data source: {smoke.data_source}",
            f"- D1AGG bars: {smoke.d1agg_count}",
            f"- Data hash: `{smoke.data_hash or 'n/a'}`",
            "",
            "| check | status | detail |",
            "|---|---|---|",
        ]
        for c in smoke.checks:
            mark = "PASS" if c.ok else "FAIL"
            lines.append(f"| `{c.name}` | {mark} | {c.detail} |")
        lines.append("")

    lines += [
        "## What this does and does not establish",
        "",
        "**Does:** the D1AGG aggregation output feeds the backtest engine; "
        "`next_bar_open` fills an entry at bar N+1's open; D1AGG timestamps "
        "clear the rollover blackout; a final-bar signal is skipped "
        "explicitly. Pure mechanics.",
        "",
        "**Does not:** measure, suggest, or imply any strategy edge. The "
        "diagnostic probe is not a strategy. Nothing here is evidence for "
        "or against any strategy, and nothing here approves anything.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Diagnostic-only six-pair D1AGG + next_bar_open smoke check."
    )
    ap.add_argument(
        "--db", default=str(DEFAULT_DB),
        help="SQLite store of real OANDA H4 candles "
        "(default: data/oanda_h4_research.sqlite3)",
    )
    ap.add_argument(
        "--out", default=str(DEFAULT_OUT), help="output diagnostic report path",
    )
    return ap.parse_args()


def _display_path(path: Path) -> str:
    """Repo-relative when possible, so committed reports stay portable."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _sample_source_hash() -> str | None:
    meta_path = SAMPLE_CSV.with_suffix(".meta.json")
    if not meta_path.exists():
        return None
    return json.loads(meta_path.read_text(encoding="utf-8")).get("source_hash")


def main() -> int:
    args = parse_args()
    db_path = Path(args.db)
    db_display = _display_path(db_path)

    if db_path.exists():
        mode = f"real OANDA H4 store ({db_display})"
        smokes, blockers, coverage = smoke_from_store(db_path)
    else:
        mode = "committed D1AGG sample (no real OANDA H4 store present)"
        smokes, blockers = [], [
            f"no real OANDA H4 candle store at {db_display} — the six-pair "
            f"H4→D1AGG aggregation smoke could not run for {', '.join(SIX_MAJORS)}"
        ]
        coverage = {pair: "blocked — no H4 store" for pair in SIX_MAJORS}

    # Fallback so the mechanical verification always runs on real data.
    if not smokes:
        if not SAMPLE_CSV.exists():
            blockers.append(f"committed D1AGG sample missing: {SAMPLE_CSV}")
        else:
            smokes.append(
                smoke_instrument(
                    make_instrument("EUR_USD"),
                    load_d1agg_sample(SAMPLE_CSV),
                    data_source=(
                        f"committed real D1AGG sample "
                        f"{SAMPLE_CSV.relative_to(ROOT)}"
                    ),
                    provenance=check_sample_provenance(SAMPLE_CSV),
                    data_hash=_sample_source_hash(),
                )
            )

    report = render_report(mode, smokes, blockers, coverage)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\n[wrote diagnostic report] {out}")

    ok = bool(smokes) and all(s.ok for s in smokes)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
