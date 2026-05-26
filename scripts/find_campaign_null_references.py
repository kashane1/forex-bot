#!/usr/bin/env python3
"""Scan the repo for CAMPAIGN_011 null-baseline and CAMPAIGN_012–014 references."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCAN_ROOTS = [
    ROOT / "docs" / "research",
    ROOT / "research",
    ROOT / "backtests",
    ROOT / "docs" / "research" / "EVIDENCE_INDEX.md",
    ROOT / "docs" / "research" / "EVIDENCE_MANIFEST.json",
]

OUT_JSON = ROOT / "research" / "contamination_audit" / "post_dedup_null_reference_inventory.json"
OUT_MD = ROOT / "research" / "contamination_audit" / "post_dedup_null_reference_inventory.md"
OUT_DOC = ROOT / "docs" / "research" / "POST_DEDUP_NULL_REFERENCE_INVENTORY.md"

CANONICAL_NULL_JSON = "research/null_baselines/campaign_011_deduped_null_baseline.json"
SUPERSEDED_NULL_JSON = "backtests/CAMPAIGN_011_random_entry_anchor"

PATTERN_SPECS: list[tuple[str, str, re.Pattern[str]]] = [
    (
        "campaign_011",
        "CAMPAIGN_011 mention",
        re.compile(r"CAMPAIGN_011", re.IGNORECASE),
    ),
    (
        "random_entry_anchor",
        "random_entry_anchor strategy name",
        re.compile(r"random_entry_anchor", re.IGNORECASE),
    ),
    (
        "old_null_expectancy",
        "superseded null expectancy (−0.0024)",
        re.compile(r"-0\.0024|−0\.0024"),
    ),
    (
        "old_null_trades",
        "superseded null trade count (1,177)",
        re.compile(r"\b1,?177\b"),
    ),
    (
        "old_null_return",
        "superseded null return (−0.53 %)",
        re.compile(r"-0\.53\s*%|−0\.53\s*%"),
    ),
    (
        "old_null_pf",
        "superseded null profit factor (0.91)",
        re.compile(r"\b0\.91\b"),
    ),
    (
        "old_null_json_path",
        "pre-fix CAMPAIGN_011 artifact path",
        re.compile(
            r"backtests/CAMPAIGN_011_random_entry_anchor(?!_deduped)",
            re.IGNORECASE,
        ),
    ),
    (
        "canonical_null_json",
        "canonical deduped null JSON path",
        re.compile(r"campaign_011_deduped_null_baseline\.json", re.IGNORECASE),
    ),
    (
        "above_null_claim",
        "above-null or beats-null language",
        re.compile(
            r"(above null|beats null|better than null|meaningful improvement over null|beat margin\?\s*\*\*YES)",
            re.IGNORECASE,
        ),
    ),
    (
        "campaign_012",
        "CAMPAIGN_012 mention",
        re.compile(r"CAMPAIGN_012", re.IGNORECASE),
    ),
    (
        "campaign_013",
        "CAMPAIGN_013 mention",
        re.compile(r"CAMPAIGN_013", re.IGNORECASE),
    ),
    (
        "campaign_014",
        "CAMPAIGN_014 mention",
        re.compile(r"CAMPAIGN_014", re.IGNORECASE),
    ),
    (
        "superseded_null_reference",
        "explicit superseded-null annotation",
        re.compile(r"SUPERSEDED_NULL_REFERENCE|superseded null|null comparison uses contaminated", re.IGNORECASE),
    ),
]

SKIP_SUFFIXES = {".pyc", ".pyo", ".sqlite", ".db", ".csv", ".jsonl", ".png", ".jpg", ".gif", ".webp"}
SKIP_DIR_NAMES = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}


@dataclass
class Match:
    line_number: int
    line_text: str
    pattern_id: str
    pattern_label: str


@dataclass
class FileInventory:
    path: str
    matches: list[Match] = field(default_factory=list)

    @property
    def pattern_ids(self) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for m in self.matches:
            if m.pattern_id not in seen:
                seen.add(m.pattern_id)
                ordered.append(m.pattern_id)
        return ordered


def iter_scan_paths() -> list[Path]:
    paths: list[Path] = []
    for root in SCAN_ROOTS:
        if root.is_file():
            paths.append(root)
            continue
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            paths.append(path)
    return paths


def scan_file(path: Path, *, root: Path | None = None) -> FileInventory:
    base = root or ROOT
    try:
        rel = path.relative_to(base).as_posix()
    except ValueError:
        rel = path.as_posix()
    inventory = FileInventory(path=rel)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return inventory
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern_id, pattern_label, pattern in PATTERN_SPECS:
            if pattern.search(line):
                inventory.matches.append(
                    Match(
                        line_number=line_number,
                        line_text=line.rstrip()[:240],
                        pattern_id=pattern_id,
                        pattern_label=pattern_label,
                    )
                )
    return inventory


def build_inventory(files: list[FileInventory]) -> dict:
    matched_files = [f for f in files if f.matches]
    pattern_counts: dict[str, int] = {}
    for f in matched_files:
        for pid in f.pattern_ids:
            pattern_counts[pid] = pattern_counts.get(pid, 0) + 1

    campaign_hits = {
        "CAMPAIGN_012": sum(1 for f in matched_files if "campaign_012" in f.pattern_ids),
        "CAMPAIGN_013": sum(1 for f in matched_files if "campaign_013" in f.pattern_ids),
        "CAMPAIGN_014": sum(1 for f in matched_files if "campaign_014" in f.pattern_ids),
    }
    old_null_hits = sum(
        1
        for f in matched_files
        if any(
            pid in f.pattern_ids
            for pid in (
                "old_null_expectancy",
                "old_null_trades",
                "old_null_return",
                "old_null_json_path",
            )
        )
    )
    canonical_hits = sum(1 for f in matched_files if "canonical_null_json" in f.pattern_ids)

    return {
        "schema_version": 1,
        "sprint": "POST_DEDUP_NULL_REFERENCE_REFRESH_001",
        "canonical_null_json": CANONICAL_NULL_JSON,
        "superseded_null_artifact": SUPERSEDED_NULL_JSON,
        "scan_roots": [
            (p.relative_to(ROOT).as_posix() if p.is_dir() else p.name)
            if p.exists() and (p.is_file() or p.is_relative_to(ROOT))
            else p.as_posix()
            for p in SCAN_ROOTS
        ],
        "files_scanned": len(files),
        "files_with_matches": len(matched_files),
        "pattern_counts": dict(sorted(pattern_counts.items())),
        "campaign_file_hits": campaign_hits,
        "files_with_old_null_metrics": old_null_hits,
        "files_with_canonical_null_json": canonical_hits,
        "files": [
            {
                "path": f.path,
                "pattern_ids": f.pattern_ids,
                "match_count": len(f.matches),
            }
            for f in matched_files
        ],
    }


def scan_all() -> tuple[dict, list[FileInventory]]:
    files = [scan_file(path) for path in iter_scan_paths()]
    matched_files = [f for f in files if f.matches]
    return build_inventory(files), matched_files


def render_markdown(
    data: dict,
    *,
    title: str,
    matched_files: list[FileInventory],
) -> str:
    by_path = {f.path: f for f in matched_files}
    lines = [
        f"# {title}",
        "",
        f"**Sprint:** {data['sprint']}  ",
        f"**Files scanned:** {data['files_scanned']}  ",
        f"**Files with matches:** {data['files_with_matches']}  ",
        "",
        "## Summary",
        "",
        f"- Canonical null JSON: `{data['canonical_null_json']}`",
        f"- Superseded artifact: `{data['superseded_null_artifact']}`",
        f"- Files with old null metrics: **{data['files_with_old_null_metrics']}**",
        f"- Files referencing canonical null JSON: **{data['files_with_canonical_null_json']}**",
        "",
        "### Campaign file hits",
        "",
        "| campaign | files with mention |",
        "|---|---:|",
    ]
    for campaign, count in data["campaign_file_hits"].items():
        lines.append(f"| {campaign} | {count} |")
    lines.extend(
        [
            "",
            "### Pattern counts",
            "",
            "| pattern | files |",
            "|---|---:|",
        ]
    )
    for pattern_id, count in data["pattern_counts"].items():
        lines.append(f"| `{pattern_id}` | {count} |")
    lines.extend(["", "## Per-file matches (sample)", ""])
    for file_entry in data["files"]:
        lines.append(f"### `{file_entry['path']}`")
        lines.append("")
        lines.append(f"Patterns: {', '.join(f'`{p}`' for p in file_entry['pattern_ids'])}")
        lines.append(f"Match count: {file_entry['match_count']}")
        lines.append("")
        full = by_path.get(file_entry["path"])
        if full is None:
            continue
        for match in full.matches[:5]:
            lines.append(
                f"- L{match.line_number} `{match.pattern_id}`: {match.line_text}"
            )
        if len(full.matches) > 5:
            lines.append(f"- … {len(full.matches) - 5} more matches")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    data, matched_files = scan_all()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        render_markdown(
            data,
            title="Post-Dedup Null Reference Inventory (machine)",
            matched_files=matched_files,
        ),
        encoding="utf-8",
    )
    OUT_DOC.write_text(
        render_markdown(
            data,
            title="Post-Dedup Null Reference Inventory",
            matched_files=matched_files,
        ),
        encoding="utf-8",
    )
    print(f"scanned {data['files_scanned']} files")
    print(f"matched {data['files_with_matches']} files")
    print(f"wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUT_MD.relative_to(ROOT)}")
    print(f"wrote {OUT_DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
