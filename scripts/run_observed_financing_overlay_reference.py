#!/usr/bin/env python3
"""Emit observed-financing overlay reference artifacts (no broker, no strategy)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import importlib.util

from forex_bot.research.financing_overlay import (
    OBSERVED_PRACTICE_FIXTURE_PATH,
    FinancingOverlayMode,
    overlay_ledger,
)
from forex_bot.research.financing_reconciliation import (
    compare_to_synthetic_overlay,
    load_observed_fixture,
)

_apply_spec = importlib.util.spec_from_file_location(
    "apply_financing_overlay",
    ROOT / "scripts" / "apply_financing_overlay_to_trade_ledgers.py",
)
assert _apply_spec and _apply_spec.loader
_apply = importlib.util.module_from_spec(_apply_spec)
_apply_spec.loader.exec_module(_apply)
build_ledgers = _apply.build_ledgers

OUT = ROOT / "research/observed_financing_capture_readonly"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    observed = load_observed_fixture(OBSERVED_PRACTICE_FIXTURE_PATH)
    validation = {
        "strategy_evidence": False,
        "not_approved": True,
        "fixture_path": str(OBSERVED_PRACTICE_FIXTURE_PATH.relative_to(ROOT)),
        "valid": observed is not None,
        "entry_count": len(observed.entries) if observed else 0,
        "sufficient_for_overlay": bool(observed and observed.entries),
    }
    (OUT / "observed_fixture_validation.json").write_text(
        json.dumps(validation, indent=2) + "\n", encoding="utf-8",
    )
    recon = compare_to_synthetic_overlay(observed)
    (OUT / "observed_vs_synthetic_delta.json").write_text(
        json.dumps(recon, indent=2) + "\n", encoding="utf-8",
    )

    manifest = {
        "strategy_evidence": False,
        "not_approved": True,
        "campaign_020_created": False,
        "observed_overlay_ran": False,
        "git_commit": subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip(),
        "generated_at_utc": datetime.now(UTC).isoformat(),
    }

    if not validation["sufficient_for_overlay"]:
        (OUT / "insufficiency_report.json").write_text(
            json.dumps(
                {
                    "reason": "OBSERVED_FIXTURE_EMPTY_OR_SPARSE",
                    "entry_count": validation["entry_count"],
                    "recommendation": "run read-only capture when practice credentials available",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        manifest["observed_overlay_ran"] = False
        (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print("Observed overlay skipped — insufficient fixture entries")
        return

    ledgers = build_ledgers()
    summaries = {}
    for ledger in ledgers:
        summaries[ledger.ledger_label] = overlay_ledger(
            ledger, FinancingOverlayMode.OBSERVED_PRACTICE_FIXTURE
        ).__dict__
    manifest["observed_overlay_ran"] = True
    (OUT / "observed_overlay_summary_by_campaign.json").write_text(
        json.dumps(summaries, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Observed overlay complete")


if __name__ == "__main__":
    main()
