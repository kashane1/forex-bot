#!/usr/bin/env python3
"""Execute approved forex documentation archive moves.

Reads classifications from ``docs/research/forex_documentation_inventory.json``
and moves ARCHIVE items into ``docs/research/archive/forex_programme/``.
Leaves redirect stub markdown files at original paths so evidence-index links
and test docstring references keep resolving.

Dry-run by default; pass ``--execute`` to perform moves.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = REPO_ROOT / "docs" / "research" / "forex_documentation_inventory.json"
ARCHIVE_ROOT = REPO_ROOT / "docs" / "research" / "archive" / "forex_programme"

SCAFFOLD_DIRS = (
    "00_final_synthesis",
    "01_evidence_indexes",
    "02_campaigns/planning",
    "02_campaigns/final_interpretations",
    "02_campaigns/reports",
    "03_factor_validation/c1",
    "03_factor_validation/carry",
    "04_front_gates",
    "05_replication",
    "06_infrastructure/backtrader",
    "07_prompts_and_plans",
    "08_superseded_working_notes/direction",
    "08_superseded_working_notes/diagnostics",
)

CAMPAIGN_SUBDIR = "02_campaigns/planning"

M1_DIAGNOSTIC_FILES = (
    "docs/research/eur_usd_m1_response_matrix_summary.csv",
    "docs/research/eur_usd_m1_response_matrix_meta.json",
    "docs/research/eur_usd_m1_response_matrix_nulls.csv",
)


def _is_redirect_stub(path: Path) -> bool:
    if not path.is_file():
        return False
    return path.read_text(encoding="utf-8", errors="ignore")[:20].startswith("# Moved")


def _resolve_destination(base: str, filename: str) -> Path:
    """Map inventory destination to on-disk path with campaign planning subdir."""
    rel = base.removeprefix("docs/research/archive/forex_programme/").rstrip("/")
    if rel == "02_campaigns":
        rel = CAMPAIGN_SUBDIR
    return ARCHIVE_ROOT / rel / filename


def _stub_content(old_rel: str, new_rel: str) -> str:
    return (
        f"# Moved to archive\n\n"
        f"This document was archived on 2026-05-31 as part of the approved "
        f"forex programme cleanup (`FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`).\n\n"
        f"**Current location:** [`{new_rel}`]({new_rel})\n\n"
        f"This stub preserves evidence-index links and docstring references. "
        f"Read the archived file for full content.\n"
    )

def load_manifest_protected_paths() -> frozenset[str]:
    """Paths that must never be moved — campaign reports and manifest diagnostics."""
    manifest = json.loads(
        (REPO_ROOT / "docs" / "research" / "EVIDENCE_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    protected: set[str] = set()
    for entry in manifest.get("campaigns", []):
        for key in ("report_path", "doc", "superseded_report_path"):
            val = entry.get(key)
            if val:
                protected.add(str(val))
    for entry in manifest.get("diagnostics", []):
        val = entry.get("path")
        if val:
            protected.add(str(val))
    return frozenset(protected)


MANIFEST_PROTECTED = load_manifest_protected_paths()


def load_archive_items() -> list[dict]:
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return [
        item
        for item in data["items"]
        if item["classification"] == "ARCHIVE"
        and item["path"].startswith("docs/research/")
        and not item["path"].startswith("docs/research/archive/")
    ]


def load_needs_review_items() -> list[dict]:
    data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    return [item for item in data["items"] if item["classification"] == "NEEDS_REVIEW"]


def triage_needs_review_path(path: str) -> tuple[str, str | None]:
    """Return (KEEP|ARCHIVE, archive_subdir_relative_to_forex_programme)."""
    p = Path(path)
    name = p.name

    if any(
        part in p.parts
        for part in ("c1_validation", "c1_highvol_frontgate", "carry_rates")
    ):
        return "KEEP", None
    if path.startswith("research/"):
        return "KEEP", None

    if path in MANIFEST_PROTECTED:
        return "KEEP", None

    if path in M1_DIAGNOSTIC_FILES:
        return "KEEP", None

    if not path.startswith("docs/research/") or path.startswith("docs/research/archive/"):
        return "KEEP", None

    if name.endswith("_VERDICT.md") or "FINAL_INTERPRETATION" in name:
        return "KEEP", None

    if name.startswith("C1_"):
        return "ARCHIVE", "03_factor_validation/c1"
    if name.startswith("CARRY_"):
        return "ARCHIVE", "03_factor_validation/carry"
    if name.startswith("FX_FUTURES_CARRY_"):
        return "ARCHIVE", "00_final_synthesis"

    if name.startswith(("BACKTRADER_", "LEAN_PARITY", "INFRA_BACKTRADER")):
        return "ARCHIVE", "06_infrastructure/backtrader"

    if name.startswith("CAMPAIGN_") or name.startswith("CROSS_PAIR_CURRENCY"):
        return "ARCHIVE", CAMPAIGN_SUBDIR

    if name.startswith(
        ("NEXT_", "NEW_FACTOR", "CROSS_UNIVERSE_FACTOR", "CROSS_UNIVERSE_")
    ):
        return "ARCHIVE", "08_superseded_working_notes/direction"

    if path.startswith("docs/research/") and p.suffix == ".md":
        return "ARCHIVE", "08_superseded_working_notes/direction"

    return "KEEP", None


def create_scaffold() -> None:
    for subdir in SCAFFOLD_DIRS:
        (ARCHIVE_ROOT / subdir).mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / "docs" / "research" / "active" / "crypto_programme").mkdir(
        parents=True, exist_ok=True
    )


def _move_with_stub(
    src: Path,
    dest: Path,
    *,
    dry_run: bool,
    stats: Counter[str],
) -> None:
    old_rel = src.relative_to(REPO_ROOT).as_posix()
    new_rel = dest.relative_to(REPO_ROOT).as_posix()

    if dry_run:
        stats["would_move"] += 1
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        stats["already_at_dest"] += 1
    else:
        shutil.move(str(src), str(dest))
        stats["moved"] += 1

    stub_path = REPO_ROOT / old_rel
    if _is_redirect_stub(stub_path):
        return

    stub_path.write_text(_stub_content(old_rel, new_rel), encoding="utf-8")
    stats["stub_created"] += 1


def execute_moves(*, dry_run: bool = True) -> Counter[str]:
    items = load_archive_items()
    stats: Counter[str] = Counter()

    for item in items:
        src = REPO_ROOT / item["path"]
        if not src.is_file():
            stats["missing_source"] += 1
            continue
        if item["path"] in MANIFEST_PROTECTED:
            stats["manifest_protected"] += 1
            continue

        dest_base = item.get("proposed_archive_destination")
        if not dest_base:
            stats["no_destination"] += 1
            continue

        dest = _resolve_destination(dest_base, src.name)
        _move_with_stub(src, dest, dry_run=dry_run, stats=stats)

    return stats


def execute_needs_review_triage(*, dry_run: bool = True) -> Counter[str]:
    stats: Counter[str] = Counter()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    by_path = {item["path"]: item for item in inventory["items"]}

    for item in load_needs_review_items():
        path = item["path"]
        src = REPO_ROOT / path
        if not src.is_file():
            stats["missing"] += 1
            continue
        if src.read_text(encoding="utf-8", errors="ignore")[:20].startswith("# Moved"):
            stats["already_stub"] += 1
            continue

        action, subdir = triage_needs_review_path(path)
        if action == "KEEP":
            stats["keep"] += 1
            if not dry_run:
                by_path[path]["classification"] = "KEEP"
                by_path[path]["reasoning"] = (
                    "Executive triage 2026-05-31: keep — evidence artifact or "
                    "referenced diagnostic in canonical location"
                )
            continue

        if src.suffix != ".md":
            stats["keep_non_md"] += 1
            if not dry_run:
                by_path[path]["classification"] = "KEEP"
            continue

        dest = ARCHIVE_ROOT / subdir / src.name
        _move_with_stub(src, dest, dry_run=dry_run, stats=stats)
        if not dry_run:
            by_path[path]["classification"] = "ARCHIVE"
            by_path[path]["proposed_archive_destination"] = (
                f"docs/research/archive/forex_programme/{subdir}/"
            )
            by_path[path]["reasoning"] = (
                "Executive triage 2026-05-31: superseded intermediate doc archived"
            )

    if not dry_run:
        counts = Counter(item["classification"] for item in inventory["items"])
        inventory["counts"] = dict(counts)
        INVENTORY_PATH.write_text(
            json.dumps(inventory, indent=2) + "\n",
            encoding="utf-8",
        )
        stats["inventory_updated"] = 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform moves (default is dry-run)",
    )
    parser.add_argument(
        "--scaffold-only",
        action="store_true",
        help="Only create directory scaffold",
    )
    parser.add_argument(
        "--triage-needs-review",
        action="store_true",
        help="Executive triage of NEEDS_REVIEW inventory items",
    )
    args = parser.parse_args()

    create_scaffold()
    if args.scaffold_only:
        print(f"Created archive scaffold under {ARCHIVE_ROOT.relative_to(REPO_ROOT)}")
        return

    dry_run = not args.execute

    if args.triage_needs_review:
        stats = execute_needs_review_triage(dry_run=dry_run)
        mode = "EXECUTE" if args.execute else "DRY-RUN"
        print(f"=== needs-review triage ({mode}) ===")
        for key, count in sorted(stats.items()):
            print(f"  {key}: {count}")
        return

    stats = execute_moves(dry_run=dry_run)
    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"=== forex archive cleanup ({mode}) ===")
    for key, count in sorted(stats.items()):
        print(f"  {key}: {count}")
    print(f"  total archive items: {len(load_archive_items())}")


if __name__ == "__main__":
    main()
