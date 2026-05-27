"""Risk/filter attribution for bespoke-only entry gaps."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from research.entry_parity.compare_entries import compare_all_campaigns
from research.entry_parity.constants import REPO_ROOT
from research.entry_parity.load_trades import load_bespoke_rejections


def build_risk_filter_attribution(*, repo_root=REPO_ROOT) -> dict[str, Any]:
    comparison = compare_all_campaigns(repo_root=repo_root)
    rejection_totals: Counter[str] = Counter()

    for campaign in ("C008", "C009", "C018"):
        for split in ("train", "validation"):
            for row in load_bespoke_rejections(repo_root, campaign, split):
                rejection_totals[row["rejection_code"]] += 1

    root_causes = {
        "backtrader_risk_window_bug": (
            "Legacy BT lane used rolling 7-day lookback for realized_pl_week "
            "instead of bespoke calendar Monday-week window. Minor once PnL fixed."
        ),
        "backtrader_pnl_home_currency_bug": (
            "BT _pnl() omitted quote->USD conversion for USD_JPY and USD_CAD. "
            "JPY losses recorded as USD destroyed equity and triggered "
            "DRAWDOWN_LIMIT — primary cause of ~20% trade-count gap."
        ),
        "backtrader_position_still_open": (
            "Bespoke-only entry timestamp falls inside an open Backtrader "
            "trade window — exit timing cascade from prior trade."
        ),
        "backtrader_missing_signal_or_risk": (
            "No bespoke rejection log and BT flat at timestamp — likely "
            "cumulative RiskEngine drawdown/weekly-loss rejection in BT lane "
            "without a logged bespoke rejection at same timestamp."
        ),
        "bespoke_risk_rejection_logged": (
            "Bespoke logged spread/session/risk rejection; trade not taken "
            "in bespoke — should not appear as bespoke-only entry (data check)."
        ),
    }

    attribution_summary = comparison.get("aggregate_attribution", {})
    primary = "BACKTRADER_IMPLEMENTATION_GAP"
    if attribution_summary.get("backtrader_position_still_open", 0) > 30:
        primary = "EXPECTED_ORCHESTRATION_DIFFERENCE"

    return {
        "strategy_evidence": False,
        "parity_diagnostic_only": True,
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "primary_classification": primary,
        "bespoke_rejection_code_totals": dict(rejection_totals),
        "entry_gap_attribution": attribution_summary,
        "root_cause_notes": root_causes,
        "spread_filter": "Same RiskEngine path — spread/session filters apply in both lanes when signals fire.",
        "session_filter": "Rejection CSVs show SESSION_BLOCKED and SPREAD_TOO_WIDE in bespoke logs.",
        "max_position_handling": "Both lanes single-position; BT missing entries when prior BT exit delayed.",
        "same_bar_reentry": "Both lanes allow entry after same-bar exit — not primary gap driver.",
        "fill_timing": "Both signal_bar_close — ruled out.",
        "indicator_warmup": "220 bars both lanes — ruled out for matched early entries.",
        "dedupe_alignment": "Same deduped SQLite feed — ruled out.",
        "campaign_comparison": comparison.get("campaigns", {}),
    }
