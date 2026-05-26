#!/usr/bin/env python3
"""Classify campaign evidence integrity after the dedupe fix."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.contamination_audit.classify import (
    classify_campaigns,
    render_classification_markdown,
    render_integrity_doc,
)

INVENTORY_PATH = ROOT / "research" / "contamination_audit" / "campaign_data_source_inventory.json"
OUT_DIR = ROOT / "research" / "contamination_audit"
JSON_OUT = OUT_DIR / "campaign_integrity_classification.json"
MD_OUT = OUT_DIR / "campaign_integrity_classification.md"
DOC_OUT = ROOT / "docs" / "research" / "CAMPAIGN_EVIDENCE_INTEGRITY_AFTER_DEDUP_FIX.md"


def main() -> int:
    if not INVENTORY_PATH.exists():
        print(f"missing inventory: {INVENTORY_PATH}", file=sys.stderr)
        return 1
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    data = classify_campaigns(inventory)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    JSON_OUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_classification_markdown(data) + "\n", encoding="utf-8")
    DOC_OUT.write_text(render_integrity_doc(data) + "\n", encoding="utf-8")

    print(f"classified {len(data['classifications'])} campaigns")
    for status, count in sorted(data["status_counts"].items()):
        print(f"  {status}: {count}")
    print(f"wrote {JSON_OUT.relative_to(ROOT)}")
    print(f"wrote {MD_OUT.relative_to(ROOT)}")
    print(f"wrote {DOC_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
