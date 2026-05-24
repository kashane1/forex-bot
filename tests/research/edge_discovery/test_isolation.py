"""Import-isolation rails for the edge-discovery lab.

The lab is research-only. It must not import from:

  * ``forex_bot.broker``   — would let it reach OANDA
  * ``forex_bot.loops``    — that is paper/demo/live wiring
  * ``forex_bot.approval`` — only approval logic should touch that

The financing module (``forex_bot.financing``) is allowed — it is pure
data + a small function, no I/O, and the lab needs the conservative
bp/day table for cost-stress overlays.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
LAB_ROOT = REPO_ROOT / "research" / "edge_discovery"

_BANNED_IMPORTS = (
    re.compile(r"\bfrom\s+forex_bot\.broker\b"),
    re.compile(r"\bimport\s+forex_bot\.broker\b"),
    re.compile(r"\bfrom\s+forex_bot\.loops\b"),
    re.compile(r"\bimport\s+forex_bot\.loops\b"),
    re.compile(r"\bfrom\s+forex_bot\.approval\b"),
    re.compile(r"\bimport\s+forex_bot\.approval\b"),
    re.compile(r"\bfrom\s+forex_bot\.execution\b"),
    re.compile(r"\bimport\s+forex_bot\.execution\b"),
)


def test_lab_has_no_forbidden_imports() -> None:
    offenders: list[str] = []
    for path in LAB_ROOT.rglob("*.py"):
        body = path.read_text(encoding="utf-8")
        for pattern in _BANNED_IMPORTS:
            if pattern.search(body):
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {pattern.pattern}")
    assert offenders == [], (
        "edge-discovery lab files must not import broker/loops/approval/execution: "
        + ", ".join(offenders)
    )


def test_lab_only_imports_financing_from_forex_bot() -> None:
    """Defensive: if the lab ever pulls in another forex_bot module,
    require an explicit waiver here. Today: only ``forex_bot.financing``
    is allowed."""
    allowed = {"forex_bot.financing"}
    unique_modules: set[str] = set()
    pattern = re.compile(r"\bfrom\s+(forex_bot[\w.]*)\b")
    for path in LAB_ROOT.rglob("*.py"):
        body = path.read_text(encoding="utf-8")
        for m in pattern.findall(body):
            unique_modules.add(m)
    extras = unique_modules - allowed
    assert extras == set(), (
        f"edge-discovery lab imports unexpected forex_bot modules: {sorted(extras)} "
        f"(allowed: {sorted(allowed)})"
    )
