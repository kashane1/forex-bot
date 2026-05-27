"""Strategy-approval registry — schema, validation, and the loop guard.

A strategy family may run in a paper / demo / live loop ONLY if the
approved-strategy registry (`configs/approved_strategies.yaml`) holds a
valid, active approval entry for it and that loop mode. Backtesting is
research and is never gated by this module — only signal-emitting /
order-capable loops are.

The registry ships EMPTY after the Research Marathon 001 NO-GO freeze:
no strategy is approved, so every loop refuses. Adding an entry is a
deliberate, reviewed human action — see
`docs/research/STRATEGY_APPROVAL_PROCESS.md`.

This module owns the entry schema, loads and validates the registry,
and evaluates which strategies are approved for a given loop mode. A
malformed registry fails closed: every loop refuses.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator

from forex_bot.config import ConfigError

_REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVED_STRATEGIES_PATH = _REPO_ROOT / "configs" / "approved_strategies.yaml"

# Strategy families that may legitimately appear in an approval entry. A
# typo'd or unknown strategy id is rejected rather than silently ignored.
_KNOWN_STRATEGIES = frozenset({
    "trend_following",
    "volatility_breakout",
    "pullback_continuation",
    "mean_reversion",
})
# Repo-wide hard ceiling on per-trade risk (percent of equity).
_MAX_RISK_CEILING_PCT = 0.5
_LOOP_MODES = ("paper", "demo", "live")


class StrategyNotApprovedError(ConfigError):
    """Raised when a loop is asked to run a strategy that is not approved
    for that loop mode."""


class ApprovalError(StrategyNotApprovedError):
    """Raised when the approved-strategy registry itself is malformed or
    holds an invalid entry. A subclass of StrategyNotApprovedError so a
    bad registry fails closed — every loop refuses."""


class ApprovalEntry(BaseModel):
    """One human-authored strategy approval.

    Every field is mandatory (except `notes`). An entry only ever
    *permits* a strategy in *one* loop mode; a strategy that needs both
    paper and demo gets two entries.
    """

    model_config = ConfigDict(extra="forbid")

    strategy_id: str
    version: str
    allowed_mode: str  # one of paper / demo / live
    approved_by: str
    approval_date: date
    expiry_date: date
    evidence_report: str  # repo-relative path to the campaign report
    max_risk_per_trade_pct: float
    notes: str = ""

    @model_validator(mode="after")
    def _validate(self) -> ApprovalEntry:
        if self.strategy_id not in _KNOWN_STRATEGIES:
            raise ValueError(
                f"strategy_id {self.strategy_id!r} is not a known strategy "
                f"{sorted(_KNOWN_STRATEGIES)}"
            )
        if not self.version.strip():
            raise ValueError("version is required")
        if self.allowed_mode not in _LOOP_MODES:
            raise ValueError(f"allowed_mode must be one of {_LOOP_MODES}")
        if not self.approved_by.strip():
            raise ValueError("approved_by (the approving human) is required")
        if self.expiry_date <= self.approval_date:
            raise ValueError("expiry_date must be after approval_date")
        if not self.evidence_report.strip():
            raise ValueError("evidence_report path is required")
        if not (0.0 < self.max_risk_per_trade_pct <= _MAX_RISK_CEILING_PCT):
            raise ValueError(
                f"max_risk_per_trade_pct must be in (0, {_MAX_RISK_CEILING_PCT}]"
            )
        return self

    def is_active(self, on_date: date) -> bool:
        """True if `on_date` falls within the approval window."""
        return self.approval_date <= on_date <= self.expiry_date


def load_approval_registry(
    registry_path: Path | None = None,
    *,
    repo_root: Path = _REPO_ROOT,
    require_evidence: bool = True,
) -> list[ApprovalEntry]:
    """Parse and validate the approved-strategy registry.

    Returns the list of approval entries (possibly empty). Raises
    `ApprovalError` if the file is not valid YAML, is not a mapping,
    `approved` is not a list, an entry is not a mapping, an entry fails
    the schema, or (when `require_evidence`) an entry's evidence report
    does not exist.
    """
    path = registry_path or APPROVED_STRATEGIES_PATH
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ApprovalError(f"registry {path} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ApprovalError(f"registry {path} must be a YAML mapping")
    raw = data.get("approved")
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ApprovalError(f"registry {path}: 'approved' must be a list")

    entries: list[ApprovalEntry] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ApprovalError(
                f"registry {path}: approved[{index}] must be a mapping with "
                f"the approval-entry schema, got {type(item).__name__} "
                "(a bare strategy name is not a valid approval entry)"
            )
        try:
            entry = ApprovalEntry.model_validate(item)
        except ValidationError as exc:
            raise ApprovalError(
                f"registry {path}: approved[{index}] is invalid: {exc}"
            ) from exc
        if require_evidence and not (repo_root / entry.evidence_report).is_file():
            raise ApprovalError(
                f"registry {path}: approved[{index}] ({entry.strategy_id}) "
                f"evidence_report does not exist: {entry.evidence_report}"
            )
        entries.append(entry)
    return entries


def active_entries(
    entries: list[ApprovalEntry], on_date: date
) -> list[ApprovalEntry]:
    """The subset of `entries` whose approval window contains `on_date`."""
    return [e for e in entries if e.is_active(on_date)]


def approved_strategy_ids(
    loop_mode: str,
    *,
    registry_path: Path | None = None,
    on_date: date | None = None,
    live_gates_ok: bool = False,
    repo_root: Path = _REPO_ROOT,
) -> set[str]:
    """Strategy ids approved to run in `loop_mode` as of `on_date`.

    Empty by default (the freeze): an empty registry approves nothing.
    An entry counts only if it is schema-valid, has existing evidence,
    is active (not expired), and its `allowed_mode` equals `loop_mode`.
    A `live` entry additionally requires `live_gates_ok` — confirmation
    that the existing config-layer live gates have passed.
    """
    today = on_date or date.today()
    ids: set[str] = set()
    for entry in active_entries(
        load_approval_registry(registry_path, repo_root=repo_root), today
    ):
        if entry.allowed_mode != loop_mode:
            continue
        if entry.allowed_mode == "live" and not live_gates_ok:
            continue
        ids.add(entry.strategy_id)
    return ids


def assert_loop_strategies_approved(
    loop_mode: str,
    enabled_strategies: list[str],
    *,
    registry_path: Path | None = None,
    on_date: date | None = None,
    live_gates_ok: bool = False,
) -> None:
    """Refuse a paper / demo / live loop unless *every* enabled strategy
    is approved for that loop mode.

    Backtesting is never gated — only signal-emitting / order-capable
    loops are. A malformed registry raises `ApprovalError` (a
    `StrategyNotApprovedError`), so the loop fails closed.
    """
    approved = approved_strategy_ids(
        loop_mode,
        registry_path=registry_path,
        on_date=on_date,
        live_gates_ok=live_gates_ok,
    )
    unapproved = sorted(s for s in enabled_strategies if s not in approved)
    if unapproved:
        raise StrategyNotApprovedError(
            f"{loop_mode}-loop refused: strategy/strategies {unapproved} are "
            f"not approved for {loop_mode} trading in the approved-strategy "
            f"registry ('{APPROVED_STRATEGIES_PATH.name}'). As of the "
            f"research freeze (Research Marathon 001 = NO-GO) the registry is "
            f"empty and NO strategy is approved. Approving a strategy is a "
            f"deliberate, reviewed human action — see "
            f"docs/research/STRATEGY_APPROVAL_PROCESS.md."
        )


def execution_realism_promotion_blockers(meta: object | None) -> list[str]:
    """Fill-timing policy blockers for promotion review (not registry approval).

    Empty list means execution-realism metadata does not block promotion
    readiness evaluation; other gates (verdict, registry, loops) still apply.
    """
    from forex_bot.research.execution_realism import (
        ExecutionRealismMetadata,
        promotion_readiness_errors,
    )

    return promotion_readiness_errors(meta)
