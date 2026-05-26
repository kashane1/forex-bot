"""Scan campaign artifacts and record data-source provenance."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

CAMPAIGN_ID_RE = re.compile(r"CAMPAIGN_(\d{3})", re.IGNORECASE)
SQLITE_RE = re.compile(r"(?:data/)?(?:campaign(?:_\d{3})?|oanda_h4_research)\.sqlite3", re.I)
CSV_EXPORT_RE = re.compile(r"(?:lean_parity/exports|\.csv|backtrader.*csv)", re.I)
CANDLEREPO_RE = re.compile(r"CandleRepo|database_path|candle_repo", re.I)
BACKTRADER_RE = re.compile(r"backtrader|Backtrader|BT lane", re.I)
DEDUPED_RE = re.compile(r"deduped|keep_last|DEDUPED_INPUT|duplicate.*drop", re.I)
DUPLICATE_COUNT_RE = re.compile(
    r"duplicate[s]?[_ ]?(?:rows )?(?:detected|dropped)|duplicates_dropped",
    re.I,
)
DATE_RE = re.compile(r"\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})")
VERDICT_RE = re.compile(
    r"(?:verdict|Overall verdict)[:\s]*\*?\*?(REJECT|PASS|DIAGNOSTIC|BLOCKED|"
    r"SYNTHETIC_NOT_EVIDENCE|REJECT_NO_VALID_RESULT|NO-GO)",
    re.I,
)

SCAN_ROOTS = (
    "docs/research",
    "backtests",
    "research",
    "configs",
)

SKIP_SUFFIXES = {".sqlite3", ".db", ".env"}
SKIP_PARTS = {"node_modules", ".git", "__pycache__"}

STRATEGY_BY_CAMPAIGN: dict[str, str] = {
    "CAMPAIGN_001": "trend_following (synthetic)",
    "CAMPAIGN_002": "trend_following 0.1.0",
    "CAMPAIGN_003": "trend_following + ADX-14",
    "CAMPAIGN_004": "volatility_breakout 0.1.0-c004",
    "CAMPAIGN_005": "benchmarks (none)",
    "CAMPAIGN_006": "daily trend (blocked)",
    "CAMPAIGN_007": "pullback_continuation",
    "CAMPAIGN_008": "mean_reversion 0.1.0-c008",
    "CAMPAIGN_009": "mean_reversion 0.2.0-c009",
    "CAMPAIGN_010": "session_breakout 0.1.0-c010",
    "CAMPAIGN_011": "random_entry_anchor 0.1.0-c011",
    "CAMPAIGN_012": "regime_switcher_atr_percentile 0.1.0-c012",
    "CAMPAIGN_013": "cross_pair_currency_strength_rotation 0.1.0-c013",
    "CAMPAIGN_014": "calendar_event_window_anomaly 0.1.0-c014",
    "CAMPAIGN_015": "failed_breakout_reversal 0.1.0-c015",
}

CONTAMINATION_STATUSES = frozenset({
    "DEDUP_SAFE",
    "CONTAMINATED_SUPERSEDED",
    "LIKELY_CONTAMINATED",
    "CSV_EXPORT_SAFE",
    "BACKTRADER_ONLY_DIAGNOSTIC",
    "BLOCKED_NO_RUN",
    "NULL_BASELINE_REQUIRES_RERUN",
    "UNKNOWN_REQUIRES_RERUN",
})


@dataclass
class ArtifactRecord:
    campaign_id: str | None
    strategy_name: str | None
    artifact_path: str
    data_source_path: str | None = None
    sqlite_path: str | None = None
    csv_export_path: str | None = None
    generated_date: str | None = None
    uses_candle_repo_list: bool = False
    uses_backtrader_csv: bool = False
    uses_deduped_post_fix_path: bool = False
    duplicate_counts_reported: bool = False
    documented_verdict: str | None = None
    recommended_contamination_status: str = "UNKNOWN_REQUIRES_RERUN"
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_campaign_id(raw: str) -> str:
    m = CAMPAIGN_ID_RE.search(raw)
    if not m:
        return raw.upper()
    return f"CAMPAIGN_{m.group(1)}"


def _campaign_from_path(path: Path) -> str | None:
    parts = "/".join(path.parts)
    m = CAMPAIGN_ID_RE.search(parts)
    if m:
        return f"CAMPAIGN_{m.group(1)}"
    if path.name.startswith("campaign_") and path.suffix == ".yaml":
        num = path.stem.split("_")[1]
        if num.isdigit():
            return f"CAMPAIGN_{int(num):03d}"
    return None


EVIDENCE_PATH_PREFIXES = (
    "docs/research/",
    "configs/campaign_",
    "backtests/CAMPAIGN_",
    "backtests/campaign_",
    "backtests/diagnostics/",
    "research/campaign_",
    "research/backtrader_lane/",
    "research/walk_forward/",
    "research/lean_parity/",
)


def _is_evidence_path(rel: str) -> bool:
    if rel in {
        "docs/research/EVIDENCE_INDEX.md",
        "docs/research/EVIDENCE_MANIFEST.json",
    }:
        return True
    if "/runs/" in rel or "/runs.pre_pnl_fix/" in rel:
        return False
    return any(rel.startswith(p) for p in EVIDENCE_PATH_PREFIXES)


def _should_scan(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    name = path.name.lower()
    if name.endswith("_trades.csv") or name.endswith(".jsonl"):
        return False
    rel_parts = path.parts
    if "folds" in rel_parts:
        # Per-fold cell artifacts are trade dumps; keep walk_forward rollups only.
        return False
    if path.suffix.lower() in {".csv"}:
        return False
    if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".txt", ".py", ".log"}:
        return False
    if path.suffix.lower() == ".json" and path.stat().st_size > 200_000:
        return False
    return path.is_file()


def _read_text(path: Path, limit: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _extract_sqlite(text: str, path: Path) -> str | None:
    m = SQLITE_RE.search(text)
    if m:
        return m.group(0)
    if "campaign_002.sqlite3" in str(path):
        return "data/campaign_002.sqlite3"
    return None


def _extract_verdict(text: str) -> str | None:
    m = VERDICT_RE.search(text)
    return m.group(1).upper() if m else None


def _extract_date(text: str) -> str | None:
    m = DATE_RE.search(text)
    return m.group(1) if m else None


def _infer_status(record: ArtifactRecord) -> str:
    path = record.artifact_path.lower()
    cid = record.campaign_id or ""

    if "backtrader" in path and (
        "comparison" in path or "parity" in path or "lane" in path
    ):
        if record.uses_backtrader_csv or "csv" in path:
            return "CSV_EXPORT_SAFE" if "diagnostic" not in path else "BACKTRADER_ONLY_DIAGNOSTIC"
        return "BACKTRADER_ONLY_DIAGNOSTIC"

    if cid == "CAMPAIGN_001" or "synthetic" in (record.notes or []):
        return "DEDUP_SAFE"

    if cid == "CAMPAIGN_006":
        return "BLOCKED_NO_RUN"

    if "deduped" in path or record.uses_deduped_post_fix_path:
        return "DEDUP_SAFE"

    if cid == "CAMPAIGN_015" and "failed_breakout_reversal/" in path and "deduped" not in path:
        return "CONTAMINATED_SUPERSEDED"

    if cid == "CAMPAIGN_011" and record.uses_candle_repo_list and not record.uses_deduped_post_fix_path:
        if "deduped" not in path:
            return "NULL_BASELINE_REQUIRES_RERUN"

    if record.uses_backtrader_csv and not record.uses_candle_repo_list:
        return "CSV_EXPORT_SAFE"

    if record.uses_candle_repo_list and record.sqlite_path and "campaign_002" in record.sqlite_path:
        if "deduped" not in path:
            return "LIKELY_CONTAMINATED"

    if record.documented_verdict == "BLOCKED":
        return "BLOCKED_NO_RUN"

    return "UNKNOWN_REQUIRES_RERUN"


def _analyze_file(repo_root: Path, path: Path) -> ArtifactRecord | None:
    rel = path.relative_to(repo_root).as_posix()
    campaign_id = _campaign_from_path(path)
    text = _read_text(path)

    if not campaign_id and not CAMPAIGN_ID_RE.search(text):
        if path.name in {"EVIDENCE_INDEX.md", "EVIDENCE_MANIFEST.json"}:
            campaign_id = None
        elif not any(k in rel for k in ("campaign", "CAMPAIGN", "backtrader")):
            return None

    sqlite_path = _extract_sqlite(text, path)
    uses_candle = bool(CANDLEREPO_RE.search(text)) or bool(sqlite_path)
    uses_bt_csv = bool(CSV_EXPORT_RE.search(text)) or (
        "backtrader" in rel.lower() and path.suffix.lower() == ".csv"
    )
    uses_deduped = bool(DEDUPED_RE.search(text)) or "deduped" in rel.lower()
    dup_counts = bool(DUPLICATE_COUNT_RE.search(text))

    if path.suffix == ".yaml" and "database_path" in text:
        try:
            data = yaml.safe_load(text)
            db = (data or {}).get("app", {}).get("database_path")
            if db:
                sqlite_path = str(db).lstrip("./")
                uses_candle = True
        except yaml.YAMLError:
            pass

    strategy = STRATEGY_BY_CAMPAIGN.get(campaign_id or "", None)
    notes: list[str] = []
    if "synthetic" in text.lower():
        notes.append("synthetic")

    record = ArtifactRecord(
        campaign_id=campaign_id,
        strategy_name=strategy,
        artifact_path=rel,
        data_source_path=sqlite_path or ("synthetic" if "synthetic" in notes else None),
        sqlite_path=sqlite_path,
        csv_export_path=rel if uses_bt_csv and path.suffix.lower() == ".csv" else None,
        generated_date=_extract_date(text),
        uses_candle_repo_list=uses_candle,
        uses_backtrader_csv=uses_bt_csv,
        uses_deduped_post_fix_path=uses_deduped,
        duplicate_counts_reported=dup_counts,
        documented_verdict=_extract_verdict(text),
        notes=notes,
    )
    record.recommended_contamination_status = _infer_status(record)
    return record


def _manifest_campaign_entries(repo_root: Path) -> list[ArtifactRecord]:
    manifest_path = repo_root / "docs/research/EVIDENCE_MANIFEST.json"
    if not manifest_path.exists():
        return []
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    records: list[ArtifactRecord] = []
    for camp in data.get("campaigns", []):
        cid = camp.get("campaign_id")
        report = camp.get("report_path")
        folder = camp.get("artifact_folder")
        sqlite_path = "data/campaign_002.sqlite3"
        if cid == "CAMPAIGN_001":
            sqlite_path = "data/campaign.sqlite3"
        uses_deduped = cid == "CAMPAIGN_015" and folder and "deduped" in folder
        rec = ArtifactRecord(
            campaign_id=cid,
            strategy_name=STRATEGY_BY_CAMPAIGN.get(cid or "", camp.get("strategy_family")),
            artifact_path=f"docs/research/EVIDENCE_MANIFEST.json#{cid}",
            data_source_path=camp.get("data_source"),
            sqlite_path=sqlite_path if camp.get("data_source") == "oanda-practice" else None,
            generated_date=data.get("generated"),
            uses_candle_repo_list=camp.get("data_source") in {"oanda-practice", "synthetic"},
            uses_backtrader_csv=False,
            uses_deduped_post_fix_path=uses_deduped,
            duplicate_counts_reported=bool(
                (camp.get("key_metrics") or {}).get("duplicate_rows_dropped")
            ),
            documented_verdict=camp.get("verdict"),
            notes=["manifest_entry"],
        )
        rec.recommended_contamination_status = _infer_status(rec)
        records.append(rec)
        if report:
            p = repo_root / report
            if p.exists():
                sub = _analyze_file(repo_root, p)
                if sub:
                    sub.campaign_id = cid
                    sub.strategy_name = rec.strategy_name
                    sub.documented_verdict = camp.get("verdict")
                    records.append(sub)
        if folder:
            folder_path = repo_root / folder
            wf = folder_path / "walk_forward" / "results.json"
            if wf.exists():
                sub = _analyze_file(repo_root, wf)
                if sub:
                    sub.campaign_id = cid
                    sub.documented_verdict = camp.get("verdict")
                    records.append(sub)
    return records


def build_inventory(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    records: list[ArtifactRecord] = []
    seen: set[str] = set()

    for scan_root in SCAN_ROOTS:
        base = root / scan_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not _should_scan(path):
                continue
            rel = path.relative_to(root).as_posix()
            if not _is_evidence_path(rel):
                continue
            rec = _analyze_file(root, path)
            if rec is None:
                continue
            if rec.artifact_path in seen:
                continue
            seen.add(rec.artifact_path)
            records.append(rec)

    for rec in _manifest_campaign_entries(root):
        if rec.artifact_path not in seen:
            seen.add(rec.artifact_path)
            records.append(rec)

    records.sort(key=lambda r: (r.campaign_id or "ZZZ", r.artifact_path))

    by_campaign: dict[str, list[dict[str, Any]]] = {}
    for rec in records:
        key = rec.campaign_id or "NON_CAMPAIGN"
        by_campaign.setdefault(key, []).append(rec.to_dict())

    status_counts: dict[str, int] = {}
    for rec in records:
        status_counts[rec.recommended_contamination_status] = (
            status_counts.get(rec.recommended_contamination_status, 0) + 1
        )

    return {
        "generated_at": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "branch": "research-campaign-contamination-audit-001",
        "artifact_count": len(records),
        "status_counts": status_counts,
        "campaign_count": len([k for k in by_campaign if k.startswith("CAMPAIGN")]),
        "artifacts": [r.to_dict() for r in records],
        "by_campaign": by_campaign,
    }


def render_inventory_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# Campaign Data Source Inventory",
        "",
        f"**Generated:** {inventory['generated_at']}",
        f"**Artifacts scanned:** {inventory['artifact_count']}",
        "",
        "## Status counts",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status, count in sorted(inventory["status_counts"].items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## By campaign", ""])
    for cid in sorted(inventory["by_campaign"], key=lambda x: (x != "NON_CAMPAIGN", x)):
        arts = inventory["by_campaign"][cid]
        lines.append(f"### {cid} ({len(arts)} artifacts)")
        lines.append("")
        for art in arts[:25]:
            lines.append(
                f"- `{art['artifact_path']}` — **{art['recommended_contamination_status']}**"
                f" — verdict={art.get('documented_verdict') or 'n/a'}"
            )
        if len(arts) > 25:
            lines.append(f"- … and {len(arts) - 25} more")
        lines.append("")
    return "\n".join(lines)
