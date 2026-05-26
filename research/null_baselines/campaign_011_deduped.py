"""CAMPAIGN_011 deduped null-baseline rollup loader.

The committed canonical artifact lives at
``research/null_baselines/campaign_011_deduped_null_baseline.json``.
It supersedes pre-fix metrics from
``backtests/CAMPAIGN_011_random_entry_anchor/`` (LIKELY_CONTAMINATED).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_CAMPAIGN_011_DEDUPED_JSON = (
    REPO_ROOT / "research" / "null_baselines" / "campaign_011_deduped_null_baseline.json"
)
CANONICAL_CAMPAIGN_011_DEDUPED_MD = (
    REPO_ROOT / "research" / "null_baselines" / "campaign_011_deduped_null_baseline.md"
)

REQUIRED_TOP_LEVEL_KEYS = frozenset(
    {
        "schema_version",
        "campaign_id",
        "strategy_name",
        "strategy_version",
        "null_model",
        "canonical",
        "master_seed",
        "data_dedupe_policy",
        "data_source",
        "config_hash",
        "aggregate",
        "per_fold",
        "per_pair",
        "supersedes",
        "excluded_local_only",
    }
)


def load_campaign_011_deduped_null_baseline(
    path: Path | None = None,
) -> dict[str, Any]:
    """Load and minimally validate the canonical deduped null rollup."""
    target = path or CANONICAL_CAMPAIGN_011_DEDUPED_JSON
    if not target.is_file():
        raise FileNotFoundError(
            f"canonical CAMPAIGN_011 deduped null baseline missing: {target}. "
            "Run scripts/promote_campaign_011_deduped_null_baseline.py first."
        )
    payload = json.loads(target.read_text(encoding="utf-8"))
    missing = REQUIRED_TOP_LEVEL_KEYS - set(payload)
    if missing:
        raise ValueError(
            f"null baseline schema missing keys {sorted(missing)} in {target}"
        )
    if payload.get("schema_version") != 1:
        raise ValueError(
            f"unsupported schema_version {payload.get('schema_version')!r} in {target}"
        )
    if not payload.get("canonical"):
        raise ValueError(f"null baseline at {target} is not marked canonical")
    return payload
