#!/usr/bin/env python3
"""Validate the research archive's integrity.

Read-only audit: checks that the campaign reports, the evidence
manifest, the approved-strategy registry, and the evidence index are
internally consistent and that nothing claims an approved trading
strategy. Exits non-zero if any check fails.

The check logic lives in `forex_bot.research_archive` so it can be
unit-tested; this script is a thin CLI wrapper.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.research_archive import validate_archive


def main() -> int:
    result = validate_archive()
    print("=== research archive validation ===\n")
    for check in result.checks:
        mark = "PASS" if check.ok else "FAIL"
        print(f"[{mark}] {check.name}")
        for message in check.messages:
            print(f"       {message}")
    print()
    if result.ok:
        print("research archive: ALL CHECKS PASSED")
        return 0
    failed = [c.name for c in result.checks if not c.ok]
    print(f"research archive: VALIDATION FAILED ({', '.join(failed)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
