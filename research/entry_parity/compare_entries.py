"""Timestamp-level entry comparison bespoke vs Backtrader."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime
from typing import Any

from research.entry_parity.constants import REPO_ROOT
from research.entry_parity.load_trades import (
    _parse_ts,
    entry_key,
    load_campaign_entries,
)


def _weekday(ts: datetime) -> str:
    return ts.strftime("%A")


def _session(hour: int) -> str:
    if hour < 7:
        return "Asia/late"
    if hour < 12:
        return "London"
    if hour < 17:
        return "London/NY overlap"
    return "NY"


def _position_open_at(
    trades: list[dict[str, Any]], instrument: str, ts: datetime
) -> bool:
    for t in trades:
        if t["instrument"] != instrument:
            continue
        entry = _parse_ts(t["entry_time"])
        exit_ = _parse_ts(t["exit_time"])
        if entry <= ts <= exit_:
            return True
    return False


def compare_campaign_entries(
    campaign: str,
    *,
    repo_root=REPO_ROOT,
) -> dict[str, Any]:
    data = load_campaign_entries(repo_root, campaign)
    bespoke = data["bespoke"]
    backtrader = data["backtrader"]
    rejections = data["rejections"]

    b_keys = {entry_key(r): r for r in bespoke}
    bt_keys = {entry_key(r): r for r in backtrader}
    common = set(b_keys) & set(bt_keys)
    bespoke_only = set(b_keys) - set(bt_keys)
    bt_only = set(bt_keys) - set(b_keys)

    rej_by_ts: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rejections:
        rej_by_ts[(r["instrument"], r["timestamp"])].append(r)

    attribution: Counter[str] = Counter()
    bespoke_only_details: list[dict[str, Any]] = []

    for key in sorted(bespoke_only):
        row = b_keys[key]
        inst, ts_iso, side = key
        ts = _parse_ts(ts_iso)
        hour = ts.hour
        detail: dict[str, Any] = {
            "campaign": campaign,
            "instrument": inst,
            "entry_time": ts_iso,
            "side": side,
            "split": row.get("split", ""),
            "weekday": _weekday(ts),
            "hour_utc": hour,
            "session": _session(hour),
        }
        if _position_open_at(backtrader, inst, ts):
            detail["attribution"] = "backtrader_position_still_open"
            attribution["backtrader_position_still_open"] += 1
        else:
            detail["attribution"] = "risk_engine_or_orchestration_divergence"
            attribution["risk_engine_or_orchestration_divergence"] += 1
        bespoke_only_details.append(detail)

    for key in sorted(bt_only):
        row = bt_keys[key]
        inst, ts_iso, side = key
        ts = _parse_ts(ts_iso)
        if _position_open_at(bespoke, inst, ts):
            attribution["bespoke_position_still_open"] += 1
        else:
            attribution["backtrader_extra_entry"] += 1

    by_pair: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    by_split: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for key in common:
        inst = key[0]
        split = b_keys[key].get("split", "unknown")
        by_pair[inst]["common"] += 1
        by_split[split]["common"] += 1
    for key in bespoke_only:
        inst = key[0]
        split = b_keys[key].get("split", "unknown")
        by_pair[inst]["bespoke_only"] += 1
        by_split[split]["bespoke_only"] += 1
    for key in bt_only:
        inst = key[0]
        split = bt_keys[key].get("split", "unknown")
        by_pair[inst]["backtrader_only"] += 1
        by_split[split]["backtrader_only"] += 1

    warmup_cutoff = 220
    first_bars_bespoke_only = sum(
        1
        for d in bespoke_only_details
        if d.get("attribution") == "backtrader_missing_signal_or_risk"
    )

    return {
        "campaign": campaign,
        "bespoke_entry_count": len(b_keys),
        "backtrader_entry_count": len(bt_keys),
        "common_entries": len(common),
        "bespoke_only_entries": len(bespoke_only),
        "backtrader_only_entries": len(bt_only),
        "common_pct_of_bespoke": round(100.0 * len(common) / max(len(b_keys), 1), 2),
        "common_pct_of_backtrader": round(100.0 * len(common) / max(len(bt_keys), 1), 2),
        "attribution_counts": dict(attribution),
        "by_pair": {k: dict(v) for k, v in sorted(by_pair.items())},
        "by_split": {k: dict(v) for k, v in sorted(by_split.items())},
        "bespoke_only_details": bespoke_only_details,
        "warmup_bars_required": warmup_cutoff,
        "first_bars_note": (
            "Warmup-sensitive gaps not isolated bar-by-bar in this pass; "
            f"{first_bars_bespoke_only} bespoke-only entries lack rejection logs "
            "and BT position overlap."
        ),
    }


def compare_all_campaigns(*, repo_root=REPO_ROOT) -> dict[str, Any]:
    campaigns = {}
    aggregate = Counter()
    for campaign in ("C008", "C009", "C018"):
        result = compare_campaign_entries(campaign, repo_root=repo_root)
        campaigns[campaign] = result
        for k, v in result.get("attribution_counts", {}).items():
            aggregate[k] += v
        aggregate[f"{campaign}_bespoke_only"] += result["bespoke_only_entries"]
        aggregate[f"{campaign}_common"] += result["common_entries"]
    return {
        "campaigns": campaigns,
        "aggregate_attribution": dict(aggregate),
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "strategy_evidence": False,
        "parity_diagnostic_only": True,
    }
