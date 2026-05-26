"""Classify campaign evidence integrity after the dedupe fix."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

DEDUPE_FIX_COMMIT = "30b4654"
DEDUPE_FIX_BRANCH = "infra-canonical-candle-dedup-and-campaign015-rerun-001"
CAMPAIGN_015_DEDUPED_ARTIFACT = (
    "backtests/CAMPAIGN_015_failed_breakout_reversal_deduped"
)
CAMPAIGN_011_DEDUPED_ARTIFACT = "backtests/CAMPAIGN_011_random_entry_anchor_deduped"

CAMPAIGN_015_CONTAMINATED_METRICS = {
    "base_exp_r": 0.23,
    "2x_exp_r": 0.1909,
    "total_trades": 164,
    "anti_overfit": "ROBUST_ABOVE_NULL",
}
CAMPAIGN_015_DEDUPED_METRICS = {
    "base_exp_r": -0.0101,
    "2x_exp_r": -0.0283,
    "total_trades": 375,
    "anti_overfit": "WITHIN_NULL",
}


@dataclass
class CampaignClassification:
    campaign_id: str
    strategy_name: str
    official_verdict_before_audit: str
    evidence_integrity_status: str
    result_remains_valid: bool
    mark_superseded: bool
    rerun_required: bool
    why: str
    artifact_paths: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dominant_status(statuses: list[str]) -> str:
    priority = [
        "CONTAMINATED_SUPERSEDED",
        "NULL_BASELINE_REQUIRES_RERUN",
        "LIKELY_CONTAMINATED",
        "UNKNOWN_REQUIRES_RERUN",
        "DEDUP_SAFE",
        "CSV_EXPORT_SAFE",
        "BACKTRADER_ONLY_DIAGNOSTIC",
        "BLOCKED_NO_RUN",
    ]
    for p in priority:
        if p in statuses:
            return p
    return statuses[0] if statuses else "UNKNOWN_REQUIRES_RERUN"


def _classify_campaign(
    campaign_id: str,
    inventory_by_campaign: dict[str, list[dict[str, Any]]],
    manifest_campaigns: dict[str, dict[str, Any]],
) -> CampaignClassification:
    arts = inventory_by_campaign.get(campaign_id, [])
    statuses = [a.get("recommended_contamination_status", "UNKNOWN_REQUIRES_RERUN") for a in arts]
    status = _dominant_status(statuses)
    manifest = manifest_campaigns.get(campaign_id, {})
    verdict = manifest.get("verdict", "UNKNOWN")
    strategy = manifest.get("strategy_family") or campaign_id
    paths = [a["artifact_path"] for a in arts[:10]]

    rules: dict[str, tuple[str, bool, bool, bool, str]] = {
        "CAMPAIGN_001": (
            "DEDUP_SAFE",
            True,
            False,
            False,
            "Synthetic harness validation on data/campaign.sqlite3; not OANDA H4 duplicate issue.",
        ),
        "CAMPAIGN_002": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Real OANDA H4 via pre-fix CandleRepo on campaign_002.sqlite3; REJECT verdict "
            "likely directionally stable but metrics unverified post-dedupe. Parity CSV lane safe.",
        ),
        "CAMPAIGN_003": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Same pre-fix SQLite bespoke path as CAMPAIGN_002; REJECT; low rerun priority.",
        ),
        "CAMPAIGN_004": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Pre-fix SQLite bespoke; strongly negative REJECT; magnitude may shift post-dedupe.",
        ),
        "CAMPAIGN_005": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Diagnostic benchmarks on pre-fix SQLite; random-entry baseline may shift.",
        ),
        "CAMPAIGN_006": (
            "BLOCKED_NO_RUN",
            False,
            False,
            False,
            "D1 infrastructure blocker; no valid bespoke H4 duplicate exposure for verdict.",
        ),
        "CAMPAIGN_007": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Pre-fix SQLite bespoke H4; REJECT on train/validation.",
        ),
        "CAMPAIGN_008": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Pre-fix SQLite; validation-positive metrics unverified post-dedupe.",
        ),
        "CAMPAIGN_009": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Pre-fix SQLite; validation-positive metrics unverified post-dedupe.",
        ),
        "CAMPAIGN_010": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            False,
            "Walk-forward on pre-fix SQLite; REJECT; metrics and gate counts may shift.",
        ),
        "CAMPAIGN_011": (
            "NULL_BASELINE_REQUIRES_RERUN",
            False,
            True,
            True,
            "Null-model anchor on pre-fix SQLite (−0.0024 R, 1177 trades). Deduped rerun "
            "artifact exists locally (−0.0029 R, 1180 trades) but must be promoted as "
            "canonical before null comparisons for CAMPAIGN_012–015 remain valid.",
        ),
        "CAMPAIGN_012": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            True,
            "Pre-fix SQLite; REJECT vs null baseline uses contaminated CAMPAIGN_011 metrics.",
        ),
        "CAMPAIGN_013": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            True,
            "Pre-fix SQLite; null comparison invalid until CAMPAIGN_011 deduped baseline canonical.",
        ),
        "CAMPAIGN_014": (
            "LIKELY_CONTAMINATED",
            False,
            False,
            True,
            "Pre-fix SQLite; null comparison invalid until CAMPAIGN_011 deduped baseline canonical.",
        ),
        "CAMPAIGN_015": (
            "DEDUP_SAFE",
            True,
            True,
            False,
            "Original bespoke SUPERSEDED BY DEDUP RERUN; canonical evidence is deduped folder "
            f"({CAMPAIGN_015_DEDUPED_ARTIFACT}). Deduped exp_r −0.0101, WITHIN_NULL, REJECT.",
        ),
    }

    if campaign_id in rules:
        integrity, valid, superseded, rerun, why = rules[campaign_id]
    else:
        integrity = status
        valid = integrity == "DEDUP_SAFE"
        superseded = integrity in {"CONTAMINATED_SUPERSEDED", "NULL_BASELINE_REQUIRES_RERUN"}
        rerun = integrity in {
            "NULL_BASELINE_REQUIRES_RERUN",
            "UNKNOWN_REQUIRES_RERUN",
            "LIKELY_CONTAMINATED",
        }
        why = f"Inferred from inventory dominant status {status}."

    notes: list[str] = []
    if any("deduped" in p for p in paths):
        notes.append("deduped_artifact_present")
    if any(s == "BACKTRADER_ONLY_DIAGNOSTIC" for s in statuses):
        notes.append("has_backtrader_diagnostic_artifacts")

    return CampaignClassification(
        campaign_id=campaign_id,
        strategy_name=strategy,
        official_verdict_before_audit=verdict,
        evidence_integrity_status=integrity,
        result_remains_valid=valid,
        mark_superseded=superseded,
        rerun_required=rerun,
        why=why,
        artifact_paths=paths,
        notes=notes,
    )


def classify_campaigns(
    inventory: dict[str, Any],
    *,
    dedupe_fix_commit: str = DEDUPE_FIX_COMMIT,
) -> dict[str, Any]:
    by_campaign = inventory.get("by_campaign", {})
    manifest_campaigns: dict[str, dict[str, Any]] = {}
    for art in inventory.get("artifacts", []):
        if art.get("notes") and "manifest_entry" in art["notes"]:
            manifest_campaigns[art["campaign_id"]] = {
                "verdict": art.get("documented_verdict"),
                "strategy_family": art.get("strategy_name"),
            }

    campaign_ids = [f"CAMPAIGN_{i:03d}" for i in range(1, 16)]
    classifications = [
        _classify_campaign(cid, by_campaign, manifest_campaigns) for cid in campaign_ids
    ]

    status_counts: dict[str, int] = {}
    for c in classifications:
        status_counts[c.evidence_integrity_status] = (
            status_counts.get(c.evidence_integrity_status, 0) + 1
        )

    return {
        "generated_at": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dedupe_fix_commit": dedupe_fix_commit,
        "dedupe_fix_branch": DEDUPE_FIX_BRANCH,
        "campaign_015_contaminated_metrics": CAMPAIGN_015_CONTAMINATED_METRICS,
        "campaign_015_deduped_metrics": CAMPAIGN_015_DEDUPED_METRICS,
        "campaign_011_deduped_artifact": CAMPAIGN_011_DEDUPED_ARTIFACT,
        "status_counts": status_counts,
        "classifications": [c.to_dict() for c in classifications],
    }


def render_classification_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Campaign Integrity Classification",
        "",
        f"**Generated:** {data['generated_at']}",
        f"**Dedupe fix commit:** `{data['dedupe_fix_commit']}`",
        "",
        "## Summary",
        "",
        "| status | campaigns |",
        "|---|---:|",
    ]
    for status, count in sorted(data["status_counts"].items()):
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Per-campaign", ""])
    for c in data["classifications"]:
        lines.extend([
            f"### {c['campaign_id']} — {c['evidence_integrity_status']}",
            "",
            f"- **Verdict (unchanged):** {c['official_verdict_before_audit']}",
            f"- **Valid for decisions:** {c['result_remains_valid']}",
            f"- **Mark superseded:** {c['mark_superseded']}",
            f"- **Rerun required:** {c['rerun_required']}",
            f"- **Why:** {c['why']}",
            "",
        ])
    return "\n".join(lines)


def render_integrity_doc(data: dict[str, Any]) -> str:
    lines = [
        "# Campaign Evidence Integrity After Dedupe Fix",
        "",
        "**Sprint:** CAMPAIGN_CONTAMINATION_AUDIT_001",
        f"**Date:** {data['generated_at'][:10]}",
        "",
        "> No strategy verdicts changed to PASS. No approvals granted.",
        "",
        "## Executive summary",
        "",
        "Duplicate UTC H4 bars in `data/campaign_002.sqlite3` contaminated "
        "pre-fix bespoke loads via `CandleRepo.list`. Canonical dedupe "
        f"(`keep_last`) landed in commit `{data['dedupe_fix_commit']}`. "
        "CAMPAIGN_015 bespoke evidence is **SUPERSEDED BY DEDUP RERUN**.",
        "",
        "CAMPAIGN_011 null baseline **requires deduped rerun promotion** before "
        "null comparisons for CAMPAIGN_012–015 can be treated as integrity-safe.",
        "",
        "## Classification table",
        "",
        "| campaign | integrity status | verdict | valid | superseded | rerun |",
        "|---|---|---|:--:|:--:|:--:|",
    ]
    for c in data["classifications"]:
        lines.append(
            f"| {c['campaign_id']} | {c['evidence_integrity_status']} | "
            f"{c['official_verdict_before_audit']} | "
            f"{'yes' if c['result_remains_valid'] else 'no'} | "
            f"{'yes' if c['mark_superseded'] else 'no'} | "
            f"{'yes' if c['rerun_required'] else 'no'} |"
        )
    lines.extend(["", "## CAMPAIGN_015 contaminated vs deduped", ""])
    lines.append("| metric | contaminated | deduped |")
    lines.append("|---|---:|---:|")
    for key in CAMPAIGN_015_CONTAMINATED_METRICS:
        lines.append(
            f"| {key} | {CAMPAIGN_015_CONTAMINATED_METRICS[key]} | "
            f"{CAMPAIGN_015_DEDUPED_METRICS.get(key, 'n/a')} |"
        )
    lines.extend(["", "## Per-campaign rationale", ""])
    for c in data["classifications"]:
        lines.append(f"### {c['campaign_id']}")
        lines.append("")
        lines.append(c["why"])
        lines.append("")
    return "\n".join(lines)
