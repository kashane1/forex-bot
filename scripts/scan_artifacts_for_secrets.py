#!/usr/bin/env python3
"""Scan committed / staged artifacts for leaked OANDA credentials.

A regression guard for credentialed sprints. It runs two scans:

  * **value scan** — when OANDA credential env vars are present, checks
    that none of those *exact values* appears in **any** tracked or
    staged file. Precise (zero false positives) — the check the
    pattern-based archive validator structurally cannot do.
  * **pattern scan** — looks for strings shaped like an OANDA v20 access
    token or account id, scoped to the committed-artifact directories
    (docs/ backtests/ research/ configs/ scripts/). `tests/` is
    deliberately excluded: test fixtures legitimately carry fake
    OANDA-shaped account ids — the value scan still covers `tests/` for
    a real leak.

The script **never prints a secret value** — a finding names the file
and which credential leaked, never the value itself.

Exit codes:
  0  clean — no credential value or credential-shaped string found
  1  a potential leak was found

Usage:
    # value scan needs the credentials in the environment:
    set -a && source .env && set +a
    python scripts/scan_artifacts_for_secrets.py

See docs/research/OANDA_PRACTICE_READONLY_001_PLAN.md.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# OANDA v20 personal access token: a 64-hex block, a hyphen, then a
# shorter hex block. A bare SHA-256 (64 hex, no hyphen+hex suffix) does
# not match — so committed data hashes are not false positives.
OANDA_TOKEN_RE = re.compile(r"\b[0-9a-f]{64}-[0-9a-f]{12,}\b")
# OANDA account id shape: three short digit groups around a 7-9 digit
# block, hyphen-separated (shape NNN-NNN-NNNNNNNN-NNN).
OANDA_ACCOUNT_RE = re.compile(r"\b\d{3}-\d{3}-\d{7,9}-\d{3}\b")

# Tracked file extensions worth scanning as text.
_TEXT_SUFFIXES = {
    ".md", ".json", ".yaml", ".yml", ".py", ".txt", ".toml",
    ".cfg", ".ini", ".sh", ".csv", ".jsonl", ".example",
}
_CREDENTIAL_ENV_VARS = (
    "OANDA_ACCESS_TOKEN_PRACTICE",
    "OANDA_ACCOUNT_ID_PRACTICE",
    "OANDA_ACCESS_TOKEN_LIVE",
    "OANDA_ACCOUNT_ID_LIVE",
)
# Pattern scan scope — the committed-artifact dirs. tests/ is excluded:
# its fixtures legitimately carry fake OANDA-shaped account ids.
_PATTERN_DIRS = ("docs", "backtests", "research", "configs", "scripts")


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str  # what leaked — never the value itself


def collect_secret_values(env: dict[str, str]) -> dict[str, str]:
    """Real (non-placeholder) credential values keyed by a safe label.
    The values themselves are used only for substring comparison and are
    never emitted."""
    values: dict[str, str] = {}
    for name in _CREDENTIAL_ENV_VARS:
        raw = (env.get(name) or "").strip()
        if raw and not raw.startswith("replace_me"):
            values[name] = raw
            if "ACCOUNT_ID" in name:
                values[f"{name} (no dashes)"] = raw.replace("-", "")
    return values


def scan_text(
    text: str, *, values: dict[str, str], check_patterns: bool = True
) -> list[str]:
    """Return the list of leak kinds found in one text blob."""
    kinds: list[str] = []
    for label, value in values.items():
        if value and value in text:
            kinds.append(f"contains the value of {label}")
    if check_patterns:
        if OANDA_TOKEN_RE.search(text):
            kinds.append("contains an OANDA-access-token-shaped string")
        if OANDA_ACCOUNT_RE.search(text):
            kinds.append("contains an OANDA-account-id-shaped string")
    return kinds


def _tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [ROOT / line for line in out.stdout.splitlines() if line]


def _staged_files() -> list[Path]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [ROOT / line for line in out.stdout.splitlines() if line]


def _under(path: Path, dirs: tuple[str, ...]) -> bool:
    """True if `path`'s first component (relative to ROOT) is in `dirs`."""
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in dirs


def scan_files(
    paths: list[Path], *, values: dict[str, str], check_patterns: bool = True
) -> tuple[list[Finding], int]:
    """Scan the given files; return findings and the count actually read."""
    findings: list[Finding] = []
    scanned = 0
    for path in paths:
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        try:
            rel = str(path.relative_to(ROOT))
        except ValueError:
            rel = str(path)
        for kind in scan_text(text, values=values, check_patterns=check_patterns):
            findings.append(Finding(rel, kind))
    return findings, scanned


def main() -> int:
    values = collect_secret_values(dict(os.environ))
    print("=== artifact secret scan ===\n")
    if values:
        labels = sorted({lbl.split(" (")[0] for lbl in values})
        print(f"value scan: active for {len(labels)} credential(s): {labels}")
    else:
        print(
            "value scan: SKIPPED — no real OANDA credentials in the "
            "environment. Source .env and re-run for the precise value "
            "scan. The pattern scan still runs."
        )

    tracked = _tracked_files()
    staged = _staged_files()

    # Value scan — every tracked + staged file (precise, no false positives).
    value_targets = sorted(set(tracked) | set(staged))
    value_findings, value_scanned = scan_files(
        value_targets, values=values, check_patterns=False
    )

    # Pattern scan — committed-artifact dirs only (tests/ fixtures excluded).
    pattern_targets = sorted(
        {p for p in tracked if _under(p, _PATTERN_DIRS)}
        | {p for p in staged if _under(p, _PATTERN_DIRS)}
    )
    pattern_findings, pattern_scanned = scan_files(
        pattern_targets, values={}, check_patterns=True
    )

    print(
        f"value scan: {value_scanned} file(s) · "
        f"pattern scan: {pattern_scanned} file(s) "
        f"under {list(_PATTERN_DIRS)}\n"
    )

    findings = value_findings + pattern_findings
    if findings:
        print(f"POTENTIAL LEAK — {len(findings)} finding(s):")
        for f in findings:
            print(f"  [LEAK] {f.path}: {f.kind}")
        print("\nartifact secret scan: FAILED")
        return 1
    print("no credential value or credential-shaped string found")
    print("artifact secret scan: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
