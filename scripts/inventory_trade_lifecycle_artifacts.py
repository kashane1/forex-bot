#!/usr/bin/env python3
"""Inventory trade-level artifacts across recent campaigns for lifecycle diagnostics.

Read-only. Walks the committed `backtests/CAMPAIGN_0xx_*` trees, finds per-pair
`*_trades.csv` files, and reports — per campaign — what trade-level data exists
and, crucially, what is **missing**. It never fabricates a field: when a column
(MFE/MAE, signal features, session/regime) is absent, it is reported absent.

It also records campaigns whose trade CSVs are *gitignored / absent* (only
aggregate `*_summary.json` committed) so the gap is explicit rather than silent.

Outputs (compact — no per-trade dumps):
  research/trade_lifecycle_diagnostics/artifact_inventory.json
  docs/research/TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md

Usage:
    python scripts/inventory_trade_lifecycle_artifacts.py

This is infrastructure/diagnostics tooling. It changes no strategy verdict,
approves nothing, and touches no broker/live path.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKTESTS = REPO_ROOT / "backtests"
OUT_JSON = REPO_ROOT / "research" / "trade_lifecycle_diagnostics" / "artifact_inventory.json"
OUT_MD = REPO_ROOT / "docs" / "research" / "TRADE_LIFECYCLE_ARTIFACT_INVENTORY.md"

# Campaign backtest directories of interest (recent entry-research cluster).
CAMPAIGN_DIRS = {
    "CAMPAIGN_019": "CAMPAIGN_019_mean_reversion_thesis_invalidation",
    "CAMPAIGN_020": "CAMPAIGN_020_mtf_confluence_pullback",
    "CAMPAIGN_021": "CAMPAIGN_021_ltf_mtf_confluence",
    "CAMPAIGN_022": "CAMPAIGN_022_h4_h1_pullback_resolution",
    "CAMPAIGN_023": "CAMPAIGN_023_h4_h1_pullback_resolution_adx22",
}

# Lifecycle field -> candidate column names (first match wins). Honest mapping:
# a field is "present" only if one of these columns exists in the CSV header.
LIFECYCLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "entry_time": ("entry_time",),
    "exit_time": ("exit_time",),
    "entry_price": ("entry_price",),
    "exit_price": ("exit_price",),
    "initial_stop_price": ("stop_price", "initial_stop_price"),
    "result_r": ("r_multiple", "result_r"),
    "exit_reason": ("exit_reason",),
    "bars_held": ("bars_held",),
    "spread_pips": ("spread_paid_pips", "spread_pips"),
    "side": ("side",),
    # Path / excursion fields — generally ABSENT (the whole point of this sprint).
    "mfe_r": ("mfe_r", "max_favorable_excursion_r"),
    "mae_r": ("mae_r", "max_adverse_excursion_r"),
    "partial_mfe_proxy": ("protective_stop_arm_mfe_r",),
    # Signal features — generally ABSENT.
    "h4_adx_at_entry": ("h4_adx_at_entry", "h4_adx", "adx_at_entry"),
    "h1_pullback_depth_atr": ("h1_pullback_depth_atr", "pullback_depth_atr"),
    "m15_reclaim_distance_atr": ("m15_reclaim_distance_atr", "reclaim_distance_atr"),
    "session_bucket": ("session_bucket", "session"),
    "volatility_regime": ("volatility_regime", "vol_regime"),
}

SPLITS = ("train", "validation", "full", "test")


@dataclass
class TradeFileReport:
    path: str
    file_type: str
    row_count: int
    columns: list[str]
    split: str | None
    instrument: str | None
    field_presence: dict[str, bool]


@dataclass
class CampaignReport:
    campaign_id: str
    dir: str
    dir_present: bool
    trade_csv_count: int
    trade_csvs_gitignored: bool
    splits_covered: list[str] = field(default_factory=list)
    pairs_covered: list[str] = field(default_factory=list)
    summary_json_count: int = 0
    files: list[TradeFileReport] = field(default_factory=list)
    note: str = ""
    # Roll-up of lifecycle field availability across this campaign's trade CSVs.
    field_availability: dict[str, bool] = field(default_factory=dict)
    per_bar_reconstruction_possible: bool = False


def _split_of(path: Path) -> str | None:
    parts = {p.lower() for p in path.parts}
    for s in SPLITS:
        if s in parts:
            return s
    return None


def _instrument_of(name: str) -> str | None:
    # filenames look like c022_USD_JPY_train_base_trades.csv
    import re

    m = re.search(r"_([A-Z]{3}_[A-Z]{3})_", name)
    return m.group(1) if m else None


def _csv_header_and_count(path: Path) -> tuple[list[str], int]:
    with path.open(newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            return [], 0
        count = sum(1 for _ in reader)
    return header, count


def _field_presence(columns: list[str]) -> dict[str, bool]:
    cols = set(columns)
    return {
        field_name: any(c in cols for c in candidates)
        for field_name, candidates in LIFECYCLE_COLUMNS.items()
    }


def _trade_csvs_gitignored(campaign_dir: str) -> bool:
    """True if this campaign's *_trades.csv pattern is in .gitignore."""
    gitignore = REPO_ROOT / ".gitignore"
    if not gitignore.exists():
        return False
    needle = f"{campaign_dir}/**/*_trades.csv"
    return needle in gitignore.read_text()


def inventory_campaign(campaign_id: str, dir_name: str) -> CampaignReport:
    cdir = BACKTESTS / dir_name
    gitignored = _trade_csvs_gitignored(dir_name)
    report = CampaignReport(
        campaign_id=campaign_id,
        dir=f"backtests/{dir_name}",
        dir_present=cdir.is_dir(),
        trade_csv_count=0,
        trade_csvs_gitignored=gitignored,
    )
    if not cdir.is_dir():
        report.note = "campaign backtest directory absent (campaign not executed or not committed)."
        return report

    trade_csvs = sorted(cdir.rglob("*_trades.csv"))
    summary_jsons = list(cdir.rglob("*_summary.json"))
    report.summary_json_count = len(summary_jsons)
    report.trade_csv_count = len(trade_csvs)

    splits: set[str] = set()
    pairs: set[str] = set()
    field_any: Counter[str] = Counter()

    for csv_path in trade_csvs:
        header, count = _csv_header_and_count(csv_path)
        presence = _field_presence(header)
        split = _split_of(csv_path)
        instrument = _instrument_of(csv_path.name)
        if split:
            splits.add(split)
        if instrument:
            pairs.add(instrument)
        for k, v in presence.items():
            if v:
                field_any[k] += 1
        report.files.append(
            TradeFileReport(
                path=str(csv_path.relative_to(REPO_ROOT)),
                file_type="csv",
                row_count=count,
                columns=header,
                split=split,
                instrument=instrument,
                field_presence=presence,
            )
        )

    report.splits_covered = sorted(splits)
    report.pairs_covered = sorted(pairs)
    # A field is "available" for the campaign if every trade CSV carries it.
    n = len(trade_csvs)
    report.field_availability = {
        k: (field_any.get(k, 0) == n and n > 0) for k in LIFECYCLE_COLUMNS
    }
    fa = report.field_availability
    report.per_bar_reconstruction_possible = all(
        fa.get(k, False)
        for k in ("entry_time", "exit_time", "entry_price", "initial_stop_price", "side")
    )

    if n == 0:
        if gitignored:
            report.note = (
                "trade CSVs are gitignored (bulky) and absent from this checkout; "
                "only aggregate *_summary.json are committed. Per-trade lifecycle "
                "data NOT available in-repo — would need a local re-export."
            )
        else:
            report.note = (
                "no *_trades.csv present (campaign scaffold-only / not executed)."
            )
    else:
        report.note = f"{n} per-pair trade CSV(s) committed and readable."
    return report


def main() -> int:
    campaigns = [
        inventory_campaign(cid, dname) for cid, dname in sorted(CAMPAIGN_DIRS.items())
    ]
    payload = {
        "strategy_evidence": False,
        "not_approved": True,
        "purpose": "trade-lifecycle artifact inventory (read-only diagnostics)",
        "lifecycle_columns_checked": {k: list(v) for k, v in LIFECYCLE_COLUMNS.items()},
        "campaigns": [asdict(c) for c in campaigns],
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n")
    OUT_MD.write_text(_render_md(campaigns))
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_MD.relative_to(REPO_ROOT)}")
    for c in campaigns:
        print(
            f"  {c.campaign_id}: {c.trade_csv_count} trade csv(s), "
            f"pairs={len(c.pairs_covered)}, splits={c.splits_covered or '-'} "
            f"recon={'yes' if c.per_bar_reconstruction_possible else 'no'}"
        )
    return 0


def _yn(v: bool) -> str:
    return "yes" if v else "no"


def _render_md(campaigns: list[CampaignReport]) -> str:
    lines: list[str] = []
    lines.append("# Trade Lifecycle Artifact Inventory")
    lines.append("")
    lines.append("**Generated by** `scripts/inventory_trade_lifecycle_artifacts.py` "
                 "(read-only). Diagnostics only — no verdict, no approval.")
    lines.append("")
    lines.append("Missing fields are reported as missing, never fabricated. "
                 "`per_bar_reconstruction_possible` means the trade CSV carries "
                 "instrument/side/entry+exit time/entry price/initial stop — enough "
                 "to *join* local candles for MFE/MAE (candle availability is a "
                 "separate question handled in Phase 4).")
    lines.append("")

    # Per-campaign coverage table.
    lines.append("## Per-campaign summary")
    lines.append("")
    lines.append("| campaign | dir present | trade CSVs | gitignored | pairs | splits | summaries | recon possible |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for c in campaigns:
        lines.append(
            f"| {c.campaign_id} | {_yn(c.dir_present)} | {c.trade_csv_count} | "
            f"{_yn(c.trade_csvs_gitignored)} | {len(c.pairs_covered)} | "
            f"{', '.join(c.splits_covered) or '-'} | {c.summary_json_count} | "
            f"{_yn(c.per_bar_reconstruction_possible)} |"
        )
    lines.append("")

    # Lifecycle field availability matrix.
    field_keys = list(LIFECYCLE_COLUMNS.keys())
    lines.append("## Lifecycle field availability (per campaign)")
    lines.append("")
    lines.append("`yes` = column present in *every* committed trade CSV for that campaign.")
    lines.append("")
    header = "| field | " + " | ".join(c.campaign_id.replace("CAMPAIGN_", "C") for c in campaigns) + " |"
    sep = "|---|" + "|".join(["---"] * len(campaigns)) + "|"
    lines.append(header)
    lines.append(sep)
    for fk in field_keys:
        row = [fk]
        for c in campaigns:
            row.append(_yn(c.field_availability.get(fk, False)) if c.trade_csv_count else "-")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # Per-campaign notes.
    lines.append("## Notes")
    lines.append("")
    for c in campaigns:
        lines.append(f"- **{c.campaign_id}** (`{c.dir}`): {c.note}")
        if c.files:
            total_rows = sum(f.row_count for f in c.files)
            lines.append(f"  - {len(c.files)} trade CSV(s), {total_rows} total trade rows.")
            lines.append(f"  - columns: `{', '.join(c.files[0].columns)}`")
    lines.append("")
    lines.append("## What is structurally missing everywhere")
    lines.append("")
    lines.append("- **Full per-trade MFE/MAE** — no campaign records max favorable / "
                 "adverse excursion. C022 carries only `protective_stop_arm_mfe_r`, a "
                 "*conditional* proxy populated only when a protective stop armed.")
    lines.append("- **Signal features at entry** — H4 ADX, H1 pullback depth, M15 "
                 "reclaim distance are not exported by any campaign's trade writer.")
    lines.append("- **Session / volatility regime tags** — not recorded; would need "
                 "derivation from entry_time + candle context.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
