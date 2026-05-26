#!/usr/bin/env python3
"""Compare accepted trades for one CAMPAIGN_015 fold×pair cell.

Diagnostic-only. Does NOT approve any strategy.
`strategy_evidence: false`.

Usage:
    python scripts/diff_campaign_015_cell_trades.py \\
        --fold 1 --pair AUD_USD
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DEFAULT_BESPOKE_DIR = ROOT / "research/campaign_015/diagnostics/walk_forward_rehydrate"
DEFAULT_BT_DIR = (
    ROOT
    / "research/campaign_015/diagnostics/backtrader_fold_window_riskengine_fill_parity"
)
DEFAULT_OUTPUT = ROOT / "research/campaign_015/diagnostics/cell_parity_drilldown"

PRICE_TOLERANCE = 1e-4


class TradeClassification(StrEnum):
    MATCHED = "MATCHED"
    BT_ONLY = "BT_ONLY"
    BESPOKE_ONLY = "BESPOKE_ONLY"
    SAME_TIME_DIFFERENT_SIDE = "SAME_TIME_DIFFERENT_SIDE"
    SAME_SIGNAL_DIFFERENT_FILL = "SAME_SIGNAL_DIFFERENT_FILL"
    SAME_ENTRY_DIFFERENT_EXIT = "SAME_ENTRY_DIFFERENT_EXIT"


@dataclass(frozen=True)
class NormalizedTrade:
    source: str
    fold_index: int
    instrument: str
    entry_time: datetime
    exit_time: datetime
    side: str
    entry_price: float
    stop_price: float | None
    exit_price: float | None
    exit_reason: str
    r_multiple: float | None
    pnl: float | None
    units: int | None = None


@dataclass
class ClassifiedTrade:
    classification: TradeClassification
    bt: NormalizedTrade | None = None
    bespoke: NormalizedTrade | None = None
    notes: list[str] = field(default_factory=list)


@dataclass
class CellTradeDiff:
    fold_index: int
    pair: str
    bt_count: int
    bespoke_count: int
    delta: int
    classified: list[ClassifiedTrade]
    first_bt_only: NormalizedTrade | None
    first_bespoke_only: NormalizedTrade | None
    first_same_entry_divergent_exit: ClassifiedTrade | None
    strategy_evidence: bool = False


def _parse_ts(raw: str) -> datetime:
    ts = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        return ts.replace(tzinfo=UTC)
    return ts.astimezone(UTC)


def _float_or_none(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    return float(raw)


def load_bt_cell_trades(
    bt_dir: Path,
    *,
    fold_index: int,
    pair: str,
) -> list[NormalizedTrade]:
    path = bt_dir / "backtrader_trades.jsonl"
    if not path.is_file():
        raise FileNotFoundError(f"missing BT trades: {path}")
    out: list[NormalizedTrade] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if int(row.get("fold_index", -1)) != fold_index:
            continue
        if row.get("instrument") != pair:
            continue
        out.append(
            NormalizedTrade(
                source="bt",
                fold_index=fold_index,
                instrument=pair,
                entry_time=_parse_ts(row["entry_time"]),
                exit_time=_parse_ts(row["exit_time"]),
                side=str(row["side"]),
                entry_price=float(row["entry_price"]),
                stop_price=None,
                exit_price=float(row["exit_price"]),
                exit_reason=str(row.get("exit_reason", "")),
                r_multiple=_float_or_none(row.get("r_multiple")),
                pnl=_float_or_none(row.get("pnl_account")),
                units=int(row["units"]) if row.get("units") is not None else None,
            )
        )
    out.sort(key=lambda t: t.entry_time)
    return out


def load_bespoke_cell_trades(
    bespoke_dir: Path,
    *,
    fold_index: int,
    pair: str,
    cost: str = "base",
) -> list[NormalizedTrade]:
    fold_dir = bespoke_dir / "folds" / cost / f"fold_{fold_index:02d}"
    csv_path = fold_dir / f"fold_{fold_index:02d}_{pair}_trades.csv"
    if not csv_path.is_file():
        raise FileNotFoundError(f"missing bespoke trades: {csv_path}")
    out: list[NormalizedTrade] = []
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out.append(
                NormalizedTrade(
                    source="bespoke",
                    fold_index=fold_index,
                    instrument=pair,
                    entry_time=_parse_ts(row["entry_time"]),
                    exit_time=_parse_ts(row["exit_time"]),
                    side=str(row["side"]),
                    entry_price=float(row["entry_price"]),
                    stop_price=_float_or_none(row.get("stop_price")),
                    exit_price=_float_or_none(row.get("exit_price")),
                    exit_reason=str(row.get("exit_reason", "")),
                    r_multiple=_float_or_none(row.get("r_multiple")),
                    pnl=_float_or_none(row.get("pnl")),
                    units=int(row["units"]) if row.get("units") else None,
                )
            )
    out.sort(key=lambda t: t.entry_time)
    return out


def _entry_key(trade: NormalizedTrade) -> tuple[str, str]:
    return (trade.entry_time.isoformat(), trade.side)


def _same_entry_time(a: NormalizedTrade, b: NormalizedTrade) -> bool:
    return a.entry_time == b.entry_time


def _prices_close(a: float, b: float, *, tol: float = PRICE_TOLERANCE) -> bool:
    return abs(a - b) <= tol


def classify_cell_trades(
    bt_trades: list[NormalizedTrade],
    bespoke_trades: list[NormalizedTrade],
) -> list[ClassifiedTrade]:
    """Pair trades by entry timestamp and side; classify leftovers."""
    bt_by_key: dict[tuple[str, str], NormalizedTrade] = {}
    bt_by_time: dict[str, list[NormalizedTrade]] = {}
    for t in bt_trades:
        bt_by_key[_entry_key(t)] = t
        bt_by_time.setdefault(t.entry_time.isoformat(), []).append(t)

    bespoke_by_key: dict[tuple[str, str], NormalizedTrade] = {}
    bespoke_by_time: dict[str, list[NormalizedTrade]] = {}
    for t in bespoke_trades:
        bespoke_by_key[_entry_key(t)] = t
        bespoke_by_time.setdefault(t.entry_time.isoformat(), []).append(t)

    matched_bt: set[tuple[str, str]] = set()
    matched_bespoke: set[tuple[str, str]] = set()
    classified: list[ClassifiedTrade] = []

    for key, bt in bt_by_key.items():
        if key in bespoke_by_key:
            b = bespoke_by_key[key]
            matched_bt.add(key)
            matched_bespoke.add(key)
            same_exit = (
                bt.exit_time == b.exit_time
                and bt.exit_reason == b.exit_reason
                and _prices_close(bt.exit_price or 0, b.exit_price or 0)
            )
            if same_exit and _prices_close(bt.entry_price, b.entry_price):
                classified.append(
                    ClassifiedTrade(
                        classification=TradeClassification.MATCHED,
                        bt=bt,
                        bespoke=b,
                    )
                )
            elif not _prices_close(bt.entry_price, b.entry_price):
                classified.append(
                    ClassifiedTrade(
                        classification=TradeClassification.SAME_SIGNAL_DIFFERENT_FILL,
                        bt=bt,
                        bespoke=b,
                        notes=[
                            f"entry_price bt={bt.entry_price} bespoke={b.entry_price}",
                        ],
                    )
                )
            else:
                classified.append(
                    ClassifiedTrade(
                        classification=TradeClassification.SAME_ENTRY_DIFFERENT_EXIT,
                        bt=bt,
                        bespoke=b,
                        notes=[
                            f"exit bt={bt.exit_time.isoformat()}/{bt.exit_reason} "
                            f"bespoke={b.exit_time.isoformat()}/{b.exit_reason}",
                        ],
                    )
                )

    for ts_iso, bt_list in bt_by_time.items():
        if ts_iso not in bespoke_by_time:
            continue
        b_list = bespoke_by_time[ts_iso]
        for bt in bt_list:
            bk = _entry_key(bt)
            if bk in matched_bt:
                continue
            for b in b_list:
                if _entry_key(b) in matched_bespoke:
                    continue
                if _same_entry_time(bt, b) and bt.side != b.side:
                    classified.append(
                        ClassifiedTrade(
                            classification=TradeClassification.SAME_TIME_DIFFERENT_SIDE,
                            bt=bt,
                            bespoke=b,
                            notes=[f"side bt={bt.side} bespoke={b.side}"],
                        )
                    )
                    matched_bt.add(bk)
                    matched_bespoke.add(_entry_key(b))

    for key, bt in bt_by_key.items():
        if key not in matched_bt:
            classified.append(
                ClassifiedTrade(
                    classification=TradeClassification.BT_ONLY,
                    bt=bt,
                )
            )

    for key, b in bespoke_by_key.items():
        if key not in matched_bespoke:
            classified.append(
                ClassifiedTrade(
                    classification=TradeClassification.BESPOKE_ONLY,
                    bespoke=b,
                )
            )

    classified.sort(
        key=lambda c: (
            c.bt.entry_time if c.bt else c.bespoke.entry_time if c.bespoke else datetime.min.replace(tzinfo=UTC)
        )
    )
    return classified


def summarize_cell_diff(
    *,
    fold_index: int,
    pair: str,
    classified: list[ClassifiedTrade],
    bt_count: int,
    bespoke_count: int,
) -> CellTradeDiff:
    first_bt_only = next(
        (c.bt for c in classified if c.classification == TradeClassification.BT_ONLY),
        None,
    )
    first_bespoke_only = next(
        (
            c.bespoke
            for c in classified
            if c.classification == TradeClassification.BESPOKE_ONLY
        ),
        None,
    )
    first_exit_div = next(
        (
            c
            for c in classified
            if c.classification == TradeClassification.SAME_ENTRY_DIFFERENT_EXIT
        ),
        None,
    )
    return CellTradeDiff(
        fold_index=fold_index,
        pair=pair,
        bt_count=bt_count,
        bespoke_count=bespoke_count,
        delta=bt_count - bespoke_count,
        classified=classified,
        first_bt_only=first_bt_only,
        first_bespoke_only=first_bespoke_only,
        first_same_entry_divergent_exit=first_exit_div,
    )


def _classified_to_jsonable(c: ClassifiedTrade) -> dict[str, Any]:
    return {
        "classification": c.classification.value,
        "bt": asdict(c.bt) if c.bt else None,
        "bespoke": asdict(c.bespoke) if c.bespoke else None,
        "notes": c.notes,
    }


def _serialize_trade(t: NormalizedTrade | None) -> dict[str, Any] | None:
    if t is None:
        return None
    d = asdict(t)
    d["entry_time"] = t.entry_time.isoformat()
    d["exit_time"] = t.exit_time.isoformat()
    return d


def write_cell_diff_outputs(
    diff: CellTradeDiff,
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"fold_{diff.fold_index:02d}_{diff.pair}"
    json_path = output_dir / f"{stem}_trade_diff.json"
    md_path = output_dir / f"{stem}_trade_diff.md"

    counts: dict[str, int] = {}
    for c in diff.classified:
        counts[c.classification.value] = counts.get(c.classification.value, 0) + 1

    payload = {
        "strategy_evidence": False,
        "campaign": "CAMPAIGN_015",
        "fold_index": diff.fold_index,
        "pair": diff.pair,
        "bt_count": diff.bt_count,
        "bespoke_count": diff.bespoke_count,
        "delta": diff.delta,
        "classification_counts": counts,
        "first_bt_only": _serialize_trade(diff.first_bt_only),
        "first_bespoke_only": _serialize_trade(diff.first_bespoke_only),
        "first_same_entry_divergent_exit": (
            _classified_to_jsonable(diff.first_same_entry_divergent_exit)
            if diff.first_same_entry_divergent_exit
            else None
        ),
        "trades": [_classified_to_jsonable(c) for c in diff.classified],
    }
    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")

    lines = [
        f"# Cell trade diff — fold {diff.fold_index} / {diff.pair}",
        "",
        "> Diagnostic-only. `strategy_evidence: false`.",
        "",
        f"- Bespoke accepted: **{diff.bespoke_count}**",
        f"- BT accepted: **{diff.bt_count}**",
        f"- Delta: **+{diff.delta}**",
        "",
        "## Classification counts",
        "",
        "| classification | count |",
        "|---|---:|",
    ]
    for label, count in sorted(counts.items()):
        lines.append(f"| `{label}` | {count} |")

    lines.extend(["", "## First BT-only accepted trade", ""])
    if diff.first_bt_only:
        t = diff.first_bt_only
        lines.extend(
            [
                f"- **Entry:** `{t.entry_time.isoformat()}`",
                f"- **Side:** `{t.side}`",
                f"- **Entry price:** {t.entry_price}",
                f"- **Exit:** `{t.exit_time.isoformat()}` / `{t.exit_reason}`",
                f"- **R:** {t.r_multiple}",
            ]
        )
    else:
        lines.append("_None._")

    lines.extend(["", "## First bespoke-only accepted trade", ""])
    if diff.first_bespoke_only:
        t = diff.first_bespoke_only
        lines.extend(
            [
                f"- **Entry:** `{t.entry_time.isoformat()}`",
                f"- **Side:** `{t.side}`",
                f"- **Entry price:** {t.entry_price}",
            ]
        )
    else:
        lines.append("_None._")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def run_cell_diff(
    *,
    fold_index: int,
    pair: str,
    bespoke_dir: Path,
    backtrader_dir: Path,
    output_dir: Path,
    cost: str = "base",
) -> CellTradeDiff:
    bt_trades = load_bt_cell_trades(backtrader_dir, fold_index=fold_index, pair=pair)
    bespoke_trades = load_bespoke_cell_trades(
        bespoke_dir, fold_index=fold_index, pair=pair, cost=cost
    )
    classified = classify_cell_trades(bt_trades, bespoke_trades)
    diff = summarize_cell_diff(
        fold_index=fold_index,
        pair=pair,
        classified=classified,
        bt_count=len(bt_trades),
        bespoke_count=len(bespoke_trades),
    )
    write_cell_diff_outputs(diff, output_dir)
    return diff


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fold", type=int, required=True)
    parser.add_argument("--pair", required=True)
    parser.add_argument("--bespoke-dir", type=Path, default=DEFAULT_BESPOKE_DIR)
    parser.add_argument("--backtrader-dir", type=Path, default=DEFAULT_BT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cost", default="base")
    args = parser.parse_args(argv)

    diff = run_cell_diff(
        fold_index=args.fold,
        pair=args.pair,
        bespoke_dir=args.bespoke_dir,
        backtrader_dir=args.backtrader_dir,
        output_dir=args.output,
        cost=args.cost,
    )
    print(
        f"fold={diff.fold_index} pair={diff.pair} "
        f"bt={diff.bt_count} bespoke={diff.bespoke_count} delta=+{diff.delta}"
    )
    if diff.first_bt_only:
        print(f"first_bt_only={diff.first_bt_only.entry_time.isoformat()} {diff.first_bt_only.side}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
