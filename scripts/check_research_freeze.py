#!/usr/bin/env python3
"""CI-style research-freeze gate.

One command that fails (exit non-zero) if the research-only freeze has
been weakened. Run it before merging any research-infrastructure change.

Checks:
  1. the approved-strategy registry is empty;
  2. the research archive is internally consistent (manifest, reports,
     evidence index, non-approval verdicts);
  3. no committed artifact under docs/ backtests/ configs/ research/
     contains anything credential-shaped;
  4. paper-loop and demo-loop refuse every configured strategy.

Read-only / pure checks only — no broker, no network, no order. The
check logic is reused from `forex_bot.research_archive` and
`forex_bot.approval` so it cannot drift from the production gates.

See docs/runbooks.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.approval import StrategyNotApprovedError, assert_loop_strategies_approved
from forex_bot.config import ConfigError, load_settings
from forex_bot.research_archive import CheckResult, validate_archive

CONFIGS = ROOT / "configs"
# (config file, loop mode) pairs whose loops must refuse during the freeze.
_LOOP_CONFIGS: list[tuple[str, str]] = [("paper.yaml", "paper"), ("practice.yaml", "demo")]


def check_loops_refuse() -> CheckResult:
    """paper-loop and demo-loop must refuse every strategy their configs
    enable. A loop that does *not* refuse means the freeze is broken."""
    messages: list[str] = []
    ok = True
    for cfg_name, loop_mode in _LOOP_CONFIGS:
        path = CONFIGS / cfg_name
        if not path.exists():
            messages.append(f"{cfg_name}: config missing")
            ok = False
            continue
        try:
            settings = load_settings(path)
        except ConfigError as exc:
            messages.append(f"{cfg_name}: will not load — {exc}")
            ok = False
            continue
        try:
            assert_loop_strategies_approved(loop_mode, settings.strategy.enabled)
        except StrategyNotApprovedError:
            messages.append(
                f"{loop_mode}-loop refuses {settings.strategy.enabled} — frozen"
            )
        else:
            messages.append(
                f"{loop_mode}-loop did NOT refuse {settings.strategy.enabled} "
                "— FREEZE BROKEN"
            )
            ok = False
    return CheckResult("loops_refuse", ok, messages)


def run_freeze_checks() -> list[CheckResult]:
    """Every research-freeze check: the archive validation (which already
    covers registry-empty and the credential scan) plus loop refusal."""
    checks = list(validate_archive().checks)
    checks.append(check_loops_refuse())
    return checks


def main() -> int:
    print("=== research freeze gate ===\n")
    checks = run_freeze_checks()
    all_ok = True
    for check in checks:
        mark = "PASS" if check.ok else "FAIL"
        if not check.ok:
            all_ok = False
        print(f"[{mark}] {check.name}")
        for message in check.messages:
            print(f"       {message}")
    print()
    if all_ok:
        print("research freeze gate: ALL CHECKS PASSED")
        return 0
    failed = [c.name for c in checks if not c.ok]
    print(f"research freeze gate: FAILED ({', '.join(failed)})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
