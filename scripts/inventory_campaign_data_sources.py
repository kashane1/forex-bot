#!/usr/bin/env python3
"""Inventory campaign artifacts and their data-source provenance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.contamination_audit.inventory import (
    build_inventory,
    render_inventory_markdown,
)

OUT_DIR = ROOT / "research" / "contamination_audit"
JSON_OUT = OUT_DIR / "campaign_data_source_inventory.json"
MD_OUT = OUT_DIR / "campaign_data_source_inventory.md"
DOC_OUT = ROOT / "docs" / "research" / "CAMPAIGN_DATA_SOURCE_INVENTORY.md"


def main() -> int:
    inventory = build_inventory(ROOT)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md = render_inventory_markdown(inventory)

    JSON_OUT.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(md + "\n", encoding="utf-8")

    doc_lines = [
        "# Campaign Data Source Inventory",
        "",
        "**Sprint:** CAMPAIGN_CONTAMINATION_AUDIT_001",
        f"**Generated:** {inventory['generated_at']}",
        "",
        "Machine-readable inventory: "
        "`research/contamination_audit/campaign_data_source_inventory.json`",
        "",
        md.split("## Status counts", 1)[-1] if "## Status counts" in md else md,
    ]
    DOC_OUT.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")

    print(f"inventory: {inventory['artifact_count']} artifacts, "
          f"{inventory['campaign_count']} campaigns")
    print(f"wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"wrote {MD_OUT.relative_to(ROOT)}")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
