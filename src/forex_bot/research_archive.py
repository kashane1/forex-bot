"""Research-archive integrity validation.

Checks that the committed research evidence — campaign reports, the
evidence manifest, the approved-strategy registry, the evidence index —
is internally consistent and that nothing claims an approved trading
strategy. Pure read-only auditing; it never writes or mutates anything.

Used by `scripts/validate_research_archive.py`. The check functions take
explicit paths / data so they are unit-testable on synthetic inputs.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "docs" / "research" / "EVIDENCE_MANIFEST.json"
REGISTRY_PATH = REPO_ROOT / "configs" / "approved_strategies.yaml"
EVIDENCE_INDEX_PATH = REPO_ROOT / "docs" / "research" / "EVIDENCE_INDEX.md"

# Verdicts a research campaign may legitimately carry. None of these is an
# approval — a campaign reaching an approval verdict would be a red flag.
ALLOWED_VERDICTS = frozenset({
    "REJECT",
    "REJECT_NO_VALID_RESULT",
    "SYNTHETIC_NOT_EVIDENCE",
    "DIAGNOSTIC",
    "NO-GO",
})

_REQUIRED_CAMPAIGN_KEYS = frozenset({
    "campaign_id", "report_path", "strategy_family", "data_source",
    "verdict", "key_metrics", "commit_hash", "artifact_folder",
    "test_window_opened", "risk_engine_used", "financing_treatment",
    "strategy_approved",
})

# OANDA credential shapes: practice account ids and personal access
# tokens. Deliberately specific — git SHAs and config hashes (continuous
# hex, no dash) must not match.
_CREDENTIAL_PATTERNS = (
    re.compile(r"\b101-\d{3}-\d{6,}-\d{3}\b"),
    re.compile(r"\b[0-9a-f]{24,}-[0-9a-f]{24,}\b"),
)
_SCAN_EXTENSIONS = frozenset({".md", ".json", ".csv", ".yaml", ".yml", ".txt"})
_SCAN_DIRS = ("docs", "backtests", "research", "configs")
_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


@dataclass
class CheckResult:
    name: str
    ok: bool
    messages: list[str] = field(default_factory=list)


@dataclass
class ArchiveValidation:
    checks: list[CheckResult]

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def load_manifest(manifest_path: Path = MANIFEST_PATH) -> dict:
    """Load the evidence manifest JSON. Raises on malformed JSON."""
    return json.loads(manifest_path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Individual checks
# --------------------------------------------------------------------------


def check_registry_empty(registry_path: Path = REGISTRY_PATH) -> CheckResult:
    """The approved-strategy registry must exist and be empty."""
    if not registry_path.exists():
        return CheckResult(
            "registry_empty", False, [f"registry file missing: {registry_path}"]
        )
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    approved = data.get("approved") or []
    if approved:
        return CheckResult(
            "registry_empty", False,
            [f"approved-strategy registry is NOT empty: {approved!r}"],
        )
    return CheckResult(
        "registry_empty", True,
        ["configs/approved_strategies.yaml is empty — no strategy approved"],
    )


def check_manifest_schema(campaigns: list[dict]) -> CheckResult:
    """Every campaign entry carries the required keys."""
    if not campaigns:
        return CheckResult("manifest_schema", False, ["manifest has no campaigns"])
    msgs: list[str] = []
    for entry in campaigns:
        cid = entry.get("campaign_id", "<unknown>")
        missing = _REQUIRED_CAMPAIGN_KEYS - set(entry)
        if missing:
            msgs.append(f"{cid}: missing keys {sorted(missing)}")
    if msgs:
        return CheckResult("manifest_schema", False, msgs)
    return CheckResult(
        "manifest_schema", True,
        [f"{len(campaigns)} campaign entries, all with the required keys"],
    )


def check_reports_exist(
    campaigns: list[dict], repo_root: Path = REPO_ROOT
) -> CheckResult:
    """Every campaign's report file exists and is non-empty."""
    msgs: list[str] = []
    for entry in campaigns:
        cid = entry.get("campaign_id", "<unknown>")
        rel = entry.get("report_path")
        if not rel:
            msgs.append(f"{cid}: no report_path")
            continue
        path = repo_root / rel
        if not path.is_file():
            msgs.append(f"{cid}: report missing: {rel}")
        elif path.stat().st_size == 0:
            msgs.append(f"{cid}: report is empty: {rel}")
    if msgs:
        return CheckResult("reports_exist", False, msgs)
    return CheckResult(
        "reports_exist", True, [f"all {len(campaigns)} campaign reports present"]
    )


def check_artifact_folders_exist(
    campaigns: list[dict], repo_root: Path = REPO_ROOT
) -> CheckResult:
    """Every campaign's artifact folder exists (when one is declared)."""
    msgs: list[str] = []
    checked = 0
    for entry in campaigns:
        cid = entry.get("campaign_id", "<unknown>")
        rel = entry.get("artifact_folder")
        if rel is None:
            continue
        checked += 1
        if not (repo_root / rel).is_dir():
            msgs.append(f"{cid}: artifact folder missing: {rel}")
    if msgs:
        return CheckResult("artifact_folders_exist", False, msgs)
    return CheckResult(
        "artifact_folders_exist", True,
        [f"all {checked} declared campaign artifact folders present"],
    )


def check_no_approved_strategy(campaigns: list[dict]) -> CheckResult:
    """No campaign entry may be marked as an approved strategy."""
    approved = [
        e.get("campaign_id", "<unknown>")
        for e in campaigns
        if e.get("strategy_approved") is not False
    ]
    if approved:
        return CheckResult(
            "no_approved_strategy", False,
            [f"campaigns flag strategy_approved != false: {approved}"],
        )
    return CheckResult(
        "no_approved_strategy", True,
        ["every campaign has strategy_approved = false"],
    )


def check_verdicts_non_approval(campaigns: list[dict]) -> CheckResult:
    """Every campaign verdict is a known non-approval verdict."""
    msgs: list[str] = []
    for entry in campaigns:
        cid = entry.get("campaign_id", "<unknown>")
        verdict = entry.get("verdict")
        if verdict not in ALLOWED_VERDICTS:
            msgs.append(f"{cid}: verdict {verdict!r} is not an allowed non-approval verdict")
    if msgs:
        return CheckResult("verdicts_non_approval", False, msgs)
    return CheckResult(
        "verdicts_non_approval", True,
        ["all campaign verdicts are non-approval (REJECT / DIAGNOSTIC / ...)"],
    )


def check_report_verdict_tokens(
    campaigns: list[dict], repo_root: Path = REPO_ROOT
) -> CheckResult:
    """Each report's text corroborates its manifest verdict.

    A soft cross-check: the report must contain the verdict's primary
    keyword (case-insensitive). Guards against the manifest and the
    report drifting apart.
    """
    msgs: list[str] = []
    for entry in campaigns:
        cid = entry.get("campaign_id", "<unknown>")
        verdict = str(entry.get("verdict", ""))
        keyword = verdict.replace("-", "_").split("_", 1)[0]
        if len(keyword) < 4:  # too short to be a meaningful token
            continue
        path = repo_root / str(entry.get("report_path", ""))
        if not path.is_file():
            continue  # already reported by check_reports_exist
        if keyword.lower() not in path.read_text(encoding="utf-8").lower():
            msgs.append(f"{cid}: report does not mention verdict keyword {keyword!r}")
    if msgs:
        return CheckResult("report_verdict_tokens", False, msgs)
    return CheckResult(
        "report_verdict_tokens", True,
        ["every report's text corroborates its manifest verdict"],
    )


def check_evidence_index_links(
    index_path: Path = EVIDENCE_INDEX_PATH, repo_root: Path = REPO_ROOT
) -> CheckResult:
    """Every repo-relative link in the evidence index resolves to a file."""
    if not index_path.is_file():
        return CheckResult(
            "evidence_index_links", False, [f"evidence index missing: {index_path}"]
        )
    broken: list[str] = []
    checked = 0
    for url in _MARKDOWN_LINK.findall(index_path.read_text(encoding="utf-8")):
        target = url.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        checked += 1
        resolved = (index_path.parent / target).resolve()
        if not resolved.exists():
            broken.append(f"broken link: {target}")
    if broken:
        return CheckResult("evidence_index_links", False, broken)
    return CheckResult(
        "evidence_index_links", True,
        [f"all {checked} repo-relative evidence-index links resolve"],
    )


def scan_files_for_credentials(files: list[Path]) -> CheckResult:
    """Scan the given files for anything shaped like an OANDA credential."""
    hits: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in _CREDENTIAL_PATTERNS:
            if pattern.search(text):
                hits.append(f"possible credential in {path}")
                break
    if hits:
        return CheckResult("no_credentials", False, hits)
    return CheckResult(
        "no_credentials", True,
        [f"no credential-shaped strings in {len(files)} committed artifact files"],
    )


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def _tracked_text_files(repo_root: Path = REPO_ROOT) -> list[Path]:
    """Git-tracked text artifacts under the scanned directories."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z", *_SCAN_DIRS],
            capture_output=True, text=True, check=False,
        ).stdout
    except FileNotFoundError:
        return []
    files: list[Path] = []
    for rel in out.split("\0"):
        if not rel:
            continue
        path = repo_root / rel
        if path.suffix.lower() in _SCAN_EXTENSIONS and path.is_file():
            files.append(path)
    return files


def validate_archive(repo_root: Path = REPO_ROOT) -> ArchiveValidation:
    """Run every research-archive integrity check on the real repo."""
    checks: list[CheckResult] = []
    checks.append(check_registry_empty(repo_root / "configs" / "approved_strategies.yaml"))

    manifest_path = repo_root / "docs" / "research" / "EVIDENCE_MANIFEST.json"
    try:
        manifest = load_manifest(manifest_path)
        campaigns = manifest.get("campaigns", [])
    except (OSError, json.JSONDecodeError) as exc:
        checks.append(CheckResult("manifest_load", False, [f"cannot load manifest: {exc}"]))
        return ArchiveValidation(checks)

    checks.append(CheckResult("manifest_load", True, [f"loaded {manifest_path.name}"]))
    checks.append(check_manifest_schema(campaigns))
    checks.append(check_reports_exist(campaigns, repo_root))
    checks.append(check_artifact_folders_exist(campaigns, repo_root))
    checks.append(check_no_approved_strategy(campaigns))
    checks.append(check_verdicts_non_approval(campaigns))
    checks.append(check_report_verdict_tokens(campaigns, repo_root))
    checks.append(
        check_evidence_index_links(
            repo_root / "docs" / "research" / "EVIDENCE_INDEX.md", repo_root
        )
    )
    checks.append(scan_files_for_credentials(_tracked_text_files(repo_root)))
    return ArchiveValidation(checks)
