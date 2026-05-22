#!/usr/bin/env python3
"""Orchestrate the safe local research-data preparation steps, in order.

A single entry point that runs the data/parity pipeline:

  1. rehydrate the local real-OANDA practice H4 store;
  2. verify the H4 store (hashes, coverage);
  3. run the six-pair D1AGG + next-bar-open diagnostic smoke;
  4. (optional) export the CAMPAIGN_002 Lean-parity data;
  5. run the research-freeze gate as a final safety check.

Every step delegates to an existing, individually-tested script, each
of which has its own guards. This orchestrator is deliberately narrow:

  * it **refuses a live environment** (`OANDA_ENVIRONMENT=live`);
  * it never prints an account id or token;
  * it never submits an order, runs a strategy campaign, or approves a
    strategy — it only invokes the read-only / data-prep scripts above.

`--dry-run` prints the ordered plan and runs nothing.

Usage:
    python scripts/prepare_local_research_data.py --dry-run
    python scripts/prepare_local_research_data.py [--with-lean-export]

See docs/research/DATA_REHYDRATION_RUNBOOK.md.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_PY = sys.executable


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]
    needs_credentials: bool
    optional: bool = False

    def display(self) -> str:
        """A human-readable command — `python` for the interpreter, and
        repo-relative paths so the printed plan is portable."""
        parts: list[str] = []
        for index, token in enumerate(self.command):
            if index == 0 and token == _PY:
                parts.append("python")
            elif token.startswith(str(ROOT)):
                parts.append(str(Path(token).relative_to(ROOT)))
            else:
                parts.append(token)
        return " ".join(parts)


def _script(name: str) -> str:
    return str(ROOT / "scripts" / name)


def build_plan(*, with_lean_export: bool) -> list[Step]:
    """The ordered, safe data-prep plan. Pure — no side effects."""
    plan = [
        Step(
            "rehydrate the local real-OANDA H4 store",
            [_PY, _script("rehydrate_oanda_h4_store.py")],
            needs_credentials=True,
        ),
        Step(
            "verify the H4 store (hashes, coverage)",
            [_PY, _script("rehydrate_oanda_h4_store.py"), "--verify"],
            needs_credentials=False,
        ),
        Step(
            "six-pair D1AGG + next-bar-open diagnostic smoke",
            [_PY, _script("smoke_d1agg_next_open.py")],
            needs_credentials=False,
        ),
    ]
    if with_lean_export:
        plan.append(
            Step(
                "export CAMPAIGN_002 Lean-parity data (EUR_USD)",
                [_PY, _script("export_lean_parity_data.py"), "--instrument", "EUR_USD"],
                needs_credentials=False,
                optional=True,
            )
        )
    plan.append(
        Step(
            "research-freeze gate (final safety check)",
            [_PY, _script("check_research_freeze.py")],
            needs_credentials=False,
        )
    )
    return plan


def live_environment_error() -> str | None:
    """A refusal message if the environment points at OANDA live, else
    None. The orchestrator only ever prepares data on a practice
    account."""
    declared = os.environ.get("OANDA_ENVIRONMENT", "").strip().lower()
    if declared and declared != "practice":
        return (
            f"OANDA_ENVIRONMENT='{declared}' — this orchestrator prepares "
            "research data on a PRACTICE account only. Refusing to run."
        )
    return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Orchestrate safe local research-data preparation."
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="print the ordered plan and run nothing",
    )
    ap.add_argument(
        "--with-lean-export", action="store_true",
        help="also export the CAMPAIGN_002 Lean-parity data",
    )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    plan = build_plan(with_lean_export=args.with_lean_export)

    live_error = live_environment_error()
    if live_error:
        print(f"BLOCKER: {live_error}", file=sys.stderr)
        return 2

    if args.dry_run:
        print("=== local research-data preparation — DRY RUN ===\n")
        print("Would run these steps in order (nothing executed):\n")
        for i, step in enumerate(plan, 1):
            tag = " [needs OANDA practice credentials]" if step.needs_credentials else ""
            opt = " [optional]" if step.optional else ""
            print(f"  {i}. {step.name}{tag}{opt}")
            print(f"     $ {step.display()}")
        print("\nNo orders, no campaigns, no approvals, no live access.")
        return 0

    print("=== local research-data preparation ===\n")
    outcomes: list[tuple[str, str]] = []
    failed = False
    for i, step in enumerate(plan, 1):
        print(f"--- step {i}/{len(plan)}: {step.name} ---")
        result = subprocess.run(step.command, cwd=ROOT, check=False)
        if result.returncode == 0:
            status = "ok"
        elif result.returncode == 2:
            status = "blocked (expected — e.g. missing data/credentials)"
        else:
            status = f"FAILED (exit {result.returncode})"
            failed = True
        outcomes.append((step.name, status))
        print(f"    → {status}\n")

    print("=== summary ===")
    for name, status in outcomes:
        print(f"  - {name}: {status}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
