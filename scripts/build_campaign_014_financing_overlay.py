#!/usr/bin/env python3
"""CAMPAIGN_014 financing overlay (ESTIMATED + conservative stress).

Reads the per-fold trade CSVs produced by ``run_campaign_014.py``,
converts each trade to a ``research.financing.PositionInterval``, and
runs ``calculate_run`` with ``default_stress_rate_source()`` (the
debit-on-both-sides conservative stress source).

Emits:
  * backtests/CAMPAIGN_014_calendar_event_window_anomaly/financing/financing_run.json
  * backtests/CAMPAIGN_014_calendar_event_window_anomaly/financing/financing_run.md
  * backtests/CAMPAIGN_014_calendar_event_window_anomaly/financing/financing_summary.json

Strict rules:
  * No broker call, no credential read.
  * MODELED treatment is refused at the source layer.
  * Engine PnL is unchanged. The overlay is additive context.
  * No strategy approved; configs/approved_strategies.yaml untouched.
  * Even a clean financing pass produces RESEARCH_PASS_UNAPPROVED at
    best — never APPROVED. For CAMPAIGN_014 (which REJECTED in Phase 5),
    the financing overlay is diagnostic confirmation that the verdict
    is not changed by reasonable financing costs.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# isort: off
from research.financing import (
    FinancingTreatment,
    PositionInterval,
    calculate_run,
    default_stress_rate_source,
    dump_events_json,
    render_summary_md,
)
# isort: on

PAIRS = (
    "EUR_USD",
    "GBP_USD",
    "USD_JPY",
    "AUD_USD",
    "USD_CAD",
    "USD_CHF",
    "NZD_USD",
)


def _load_trades(folds_dir: Path) -> list[tuple[PositionInterval, dict[str, str]]]:
    out: list[tuple[PositionInterval, dict[str, str]]] = []
    for fold_dir in sorted(folds_dir.iterdir()):
        if not fold_dir.is_dir():
            continue
        for pair in PAIRS:
            csv_path = fold_dir / f"{fold_dir.name}_{pair}_trades.csv"
            if not csv_path.exists():
                continue
            with csv_path.open(encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for i, row in enumerate(reader):
                    pid = f"{fold_dir.name}_{pair}_{i:04d}"
                    interval = PositionInterval(
                        position_id=pid,
                        instrument=row["instrument"],
                        side=row["side"],
                        units=Decimal(row["units"]),
                        entry_price=Decimal(row["entry_price"]),
                        open_time=datetime.fromisoformat(row["entry_time"]),
                        close_time=datetime.fromisoformat(row["exit_time"]),
                        home_currency="USD",
                    )
                    out.append((interval, dict(row, fold_dir=fold_dir.name)))
    return out


def _empty_bucket() -> dict:
    return {
        "trades": 0,
        "events": 0,
        "cashflow_home_total": 0.0,
        "cashflow_home_stress_total": 0.0,
        "trade_pnl_usd": 0.0,
    }


def _aggregate(
    pairs_with_rows: list[tuple[PositionInterval, dict[str, str]]],
    summaries: list,
) -> dict:
    by_pair: dict[str, dict] = {p: _empty_bucket() for p in PAIRS}
    by_side: dict[str, dict] = {"long": _empty_bucket(), "short": _empty_bucket()}
    by_fold: dict[str, dict] = {}
    total_trade_pnl_usd = 0.0
    for s, (interval, row) in zip(summaries, pairs_with_rows, strict=True):
        pnl = float(row["pnl"])
        total_trade_pnl_usd += pnl
        by_pair[interval.instrument]["trades"] += 1
        by_pair[interval.instrument]["events"] += s.rollovers
        by_pair[interval.instrument]["cashflow_home_total"] += s.cashflow_home_total
        by_pair[interval.instrument]["cashflow_home_stress_total"] += (
            s.cashflow_home_stress_total
        )
        by_pair[interval.instrument]["trade_pnl_usd"] += pnl

        by_side[interval.side]["trades"] += 1
        by_side[interval.side]["events"] += s.rollovers
        by_side[interval.side]["cashflow_home_total"] += s.cashflow_home_total
        by_side[interval.side]["cashflow_home_stress_total"] += (
            s.cashflow_home_stress_total
        )
        by_side[interval.side]["trade_pnl_usd"] += pnl

        fold = row["fold_dir"]
        by_fold.setdefault(fold, _empty_bucket())
        by_fold[fold]["trades"] += 1
        by_fold[fold]["events"] += s.rollovers
        by_fold[fold]["cashflow_home_total"] += s.cashflow_home_total
        by_fold[fold]["cashflow_home_stress_total"] += s.cashflow_home_stress_total
        by_fold[fold]["trade_pnl_usd"] += pnl

    return {
        "total_trade_pnl_usd": total_trade_pnl_usd,
        "by_pair": by_pair,
        "by_side": by_side,
        "by_fold": dict(sorted(by_fold.items())),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign-dir", required=True)
    args = ap.parse_args()

    campaign_dir = Path(args.campaign_dir)
    folds_dir = campaign_dir / "folds"
    if not folds_dir.exists():
        raise SystemExit(f"missing {folds_dir}")
    fin_dir = campaign_dir / "financing"
    fin_dir.mkdir(parents=True, exist_ok=True)

    trades_rows = _load_trades(folds_dir)
    intervals = [iv for iv, _ in trades_rows]
    print(f"loaded {len(intervals)} trade intervals from {folds_dir}")

    source = default_stress_rate_source()
    print(
        f"rate source: name={source.name!r} treatment={source.treatment.value!r}"
    )
    if source.treatment == FinancingTreatment.MODELED:
        raise SystemExit("rate source is MODELED — must be ESTIMATED for v1")

    report = calculate_run(intervals, rate_source=source)

    (fin_dir / "financing_run.json").write_text(
        dump_events_json(report), encoding="utf-8"
    )
    (fin_dir / "financing_run.md").write_text(
        render_summary_md(report), encoding="utf-8"
    )

    extra = _aggregate(trades_rows, report.positions)
    extra_payload = {
        "campaign_id": "CAMPAIGN_014",
        "strategy_name": "calendar_event_window_anomaly",
        "strategy_version": "0.1.0-c014",
        "rate_source": source.name,
        "rate_source_treatment": source.treatment.value,
        "modeled_refused": True,
        "financing_in_engine_pnl": False,
        "financing_is_live_blocker": True,
        "missing_rate_event_count": report.missing_rate_event_count,
        "report_fields": {
            "event_count": report.event_count,
            "cashflow_home_total": report.cashflow_home_total,
            "cashflow_home_stress_total": report.cashflow_home_stress_total,
        },
        "trade_pnl": {"total_usd": extra["total_trade_pnl_usd"]},
        "by_pair": extra["by_pair"],
        "by_side": extra["by_side"],
        "by_fold": extra["by_fold"],
    }
    (fin_dir / "financing_summary.json").write_text(
        json.dumps(extra_payload, indent=2, default=str), encoding="utf-8"
    )
    print(f"wrote {fin_dir / 'financing_run.json'}")
    print(f"wrote {fin_dir / 'financing_run.md'}")
    print(f"wrote {fin_dir / 'financing_summary.json'}")
    print()
    print(
        f"event_count={report.event_count} "
        f"cashflow_home_total={report.cashflow_home_total:+.2f} "
        f"stress_total={report.cashflow_home_stress_total:+.2f}"
    )
    print(f"missing_rate_event_count={report.missing_rate_event_count}")
    print(f"trade_pnl_total_usd={extra['total_trade_pnl_usd']:+.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
