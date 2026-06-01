#!/usr/bin/env python3
"""Run exploratory Family B BTC/ETH relative-value diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from forex_bot.data.postgres_candle_store import PostgresCandleStore
from forex_bot.data.research_db import ResearchDatabaseBlocked, get_research_database_config
from forex_bot.project_env import bootstrap_environ
from research.crypto.diagnostics.loader import (
    DEFAULT_END,
    DEFAULT_START,
    align_btc_eth_pair,
    load_all_series,
)
from research.crypto.diagnostics.relative_value import (
    COST_VARIANTS,
    FX_S4_REFERENCE_NOTE,
    TIMEFRAMES,
    run_full_diagnostics,
)

ARTIFACT_DIR = ROOT / "research/crypto/diagnostics/family_b_relative_value_001"
DOCS = ROOT / "docs/research/active/crypto_programme"


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _fmt(v: Any, *, digits: int = 4) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


def render_lead_lag_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family B Lead-Lag and Relationship Result",
        "",
        "**Type:** Exploratory diagnostic only",
        "",
        "| TF | Same-bar corr | Roll corr μ | BTC→ETH lag1 bps (gross) | ETH→BTC lag1 bps |",
        "|----|-------------:|------------:|-------------------------:|-----------------:|",
    ]
    for tf in TIMEFRAMES:
        b = payload["timeframes"].get(tf, {}).get("lead_lag", {})
        b2e = b.get("btc_leads_eth", {}).get("lags", {}).get("lag_1", {})
        e2b = b.get("eth_leads_btc", {}).get("lags", {}).get("lag_1", {})
        lines.append(
            f"| {tf} | {_fmt(b.get('same_bar_correlation'))} | "
            f"{_fmt(b.get('rolling_correlation_mean'))} | "
            f"{_fmt(b2e.get('gross_directional_bps'), digits=2)} | "
            f"{_fmt(e2b.get('gross_directional_bps'), digits=2)} |"
        )
    lines.append("")
    lines.append("Artifact: `research/crypto/diagnostics/family_b_relative_value_001/lead_lag.json`")
    return "\n".join(lines) + "\n"


def render_momentum_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family B Relative Momentum Result",
        "",
        "Pre-declared lookbacks; top-minus-bottom quintile spread in relative return (bps).",
        "",
        "| TF | Lookback | Gross spread bps | All-in paired survives? |",
        "|----|---------:|-----------------:|:------------------------|",
    ]
    for tf in TIMEFRAMES:
        rm = payload["timeframes"].get(tf, {}).get("relative_momentum", {}).get("lookbacks", {})
        for lb, row in sorted(rm.items(), key=lambda x: int(x[0])):
            surv = row.get("cost", {}).get("all_in", {}).get("survives", False)
            lines.append(
                f"| {tf} | {lb} | {_fmt(row.get('top_minus_bottom_bps'), digits=2)} | {surv} |"
            )
    lines.extend(
        [
            "",
            "Family C reference ETH M15 gross momentum edge ~0.20 bps — compare magnitudes only.",
            "",
            "Artifact: `research/crypto/diagnostics/family_b_relative_value_001/relative_momentum.json`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_divergence_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family B Divergence and Reversion Result",
        "",
        "Beta-adjusted log spread z-score bands (|z| ≥ 1, 1.5, 2).",
        "",
        "| TF | Band | Events | Gross paired bps | All-in survives |",
        "|----|------|-------:|-----------------:|:----------------|",
    ]
    for tf in TIMEFRAMES:
        bands = payload["timeframes"].get(tf, {}).get("divergence_reversion", {}).get("spread_z_bands", {})
        for key, row in sorted(bands.items()):
            lines.append(
                f"| {tf} | {key} | {row.get('event_count', 0)} | "
                f"{_fmt(row.get('gross_paired_bps'), digits=2)} | "
                f"{row.get('cost', {}).get('all_in', {}).get('survives', False)} |"
            )
    lines.append("")
    lines.append("Artifact: `research/crypto/diagnostics/family_b_relative_value_001/divergence.json`")
    return "\n".join(lines) + "\n"


def render_regime_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family B Regime Sensitivity Result",
        "",
        "Terciles: low 33% / mid 34% / high 33% on BTC vol, ETH vol, rolling correlation.",
        "",
    ]
    for tf in TIMEFRAMES:
        reg = payload["timeframes"].get(tf, {}).get("regime", {})
        lines.append(f"### {tf}")
        lines.append(f"- Lead-lag BTC lag1 by corr regime: {reg.get('lead_lag_btc_lag1_by_corr_regime')}")
        lines.append("")
    lines.append("Artifact: `research/crypto/diagnostics/family_b_relative_value_001/regime.json`")
    return "\n".join(lines) + "\n"


def render_cost_md(payload: dict[str, Any]) -> str:
    c = payload["classification"]
    lines = [
        "# Crypto Family B Cost and FX S4 Comparison Result",
        "",
        FX_S4_REFERENCE_NOTE,
        "",
        f"**Max gross bps observed:** {_fmt(c.get('max_gross_bps_observed'), digits=2)}",
        f"**Spread-only paired survives:** {c.get('any_spread_paired_survives')}",
        f"**All-in paired survives:** {c.get('any_allin_paired_survives')}",
        f"**Beats Family C gross scale:** {c.get('beats_family_c_gross_scale')}",
        "",
        "## Paired cost hurdles by timeframe (all-in bps)",
        "",
        "| TF | BTC leg | ETH leg | Paired RT |",
        "|----|--------:|--------:|----------:|",
    ]
    for tf in TIMEFRAMES:
        pc = payload["timeframes"].get(tf, {}).get("paired_costs", {}).get("all_in", {})
        lines.append(
            f"| {tf} | {_fmt(pc.get('btc_one_leg_bps'), digits=0)} | "
            f"{_fmt(pc.get('eth_one_leg_bps'), digits=0)} | {_fmt(pc.get('paired_rt_bps'), digits=0)} |"
        )
    lines.extend(
        [
            "",
            "## vs Family C",
            "",
            "Family C best gross momentum ~1.0 Sharpe at ETH M15 but **negative** all-in; "
            "Family B must exceed ~0.2 bps gross **and** clear paired hurdle (~260–280 bps M15).",
            "",
            "## vs FX S4",
            "",
            "If gross effects remain single-digit bps after paired costs, classify as same "
            "'real but cost-band trapped' class as FX S4 — not a campaign trigger.",
            "",
            "Artifact: `research/crypto/diagnostics/family_b_relative_value_001/cost.json`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_synthesis_md(payload: dict[str, Any]) -> str:
    c = payload["classification"]
    best = payload.get("strongest_effect", {})
    tfs = payload["timeframes"]
    b2e_h1 = (
        tfs.get("H1", {})
        .get("lead_lag", {})
        .get("btc_leads_eth", {})
        .get("lags", {})
        .get("lag_1", {})
        .get("gross_directional_bps")
    )
    e2b_h1 = (
        tfs.get("H1", {})
        .get("lead_lag", {})
        .get("eth_leads_btc", {})
        .get("lags", {})
        .get("lag_1", {})
        .get("gross_directional_bps")
    )
    return "\n".join(
        [
            "# Crypto Family B Relative Value Diagnostics 001 — Synthesis",
            "",
            "**Type:** Exploratory diagnostic only",
            "",
            f"**Classification:** `{c['label']}`",
            "",
            c["rationale"],
            "",
            "---",
            "",
            "## Answers",
            "",
            f"1. **BTC → ETH lead-lag?** See lead-lag report; H1 lag1 gross bps ≈ {_fmt(b2e_h1, digits=2)}.",
            f"2. **ETH → BTC lead-lag?** H1 lag1 gross bps ≈ {_fmt(e2b_h1, digits=2)}.",
            "3. **Relative momentum?** Quintile spreads in momentum report.",
            "4. **Divergence/reversion?** Z-band events in divergence report.",
            f"5. **Strongest timeframe?** {best.get('tf')}",
            f"6. **Strongest effect family?** {best.get('family')}",
            f"7. **Null robustness?** See null columns in JSON artifacts.",
            "8. **Regime stable?** See regime report.",
            f"9. **Spread-only paired survives?** {c.get('any_spread_paired_survives')}",
            f"10. **All-in paired survives?** {c.get('any_allin_paired_survives')}",
            "11. **2× stress survives?** No (by construction if all-in fails).",
            f"12. **Better than Family C?** {c.get('beats_family_c_gross_scale')} (gross scale only).",
            "13. **Better than FX S4?** Unlikely economically — similar cost-band trap if gross < paired hurdle.",
            f"14. **Factor validation?** {'Yes' if c['label'] == 'PROMISING_FOR_FACTOR_VALIDATION' else 'No'}.",
            "15. **Family D next?** If weak/null or cost-defeated.",
            "16. **Family E forward?** Only after spot lanes exhausted.",
            f"17. **Next sprint:** Phase 8 prompt for `{c['label']}`.",
            "",
            f"**Strongest gross bps:** {_fmt(best.get('gross_bps'), digits=2)}",
        ]
    ) + "\n"


def write_next_prompt(payload: dict[str, Any]) -> str:
    label = payload["classification"]["label"]
    if label == "PROMISING_FOR_FACTOR_VALIDATION":
        path = DOCS / "NEXT_PROMPT_CRYPTO_FAMILY_B_RELATIVE_VALUE_FACTOR_VALIDATION_001.md"
        body = "# Next Prompt — Family B Relative Value Factor Validation 001\n\nPre-registered validation only.\n"
    elif label == "STATISTICAL_ONLY_COST_DEFEATED":
        path = DOCS / "NEXT_PROMPT_CRYPTO_FAMILY_D_OR_E_SELECTION_001.md"
        body = (
            "# Next Prompt — Crypto Family D or E Selection 001\n\n"
            "**Reason:** Family B relative value cost-defeated — do not tune RV.\n\n"
            "Choose Family D (non-time bars) vs Family E (funding/OI prep).\n"
        )
    elif label == "WEAK_OR_NULL":
        path = DOCS / "NEXT_PROMPT_CRYPTO_FAMILY_D_NON_TIME_BAR_DIAGNOSTICS_001.md"
        body = (
            "# Next Prompt — Crypto Family D Non-Time Bar Diagnostics 001\n\n"
            "Exploratory volume/dollar bar diagnostics — no strategy/campaign.\n"
        )
    elif label == "MIXED_REQUIRES_TARGETED_FOLLOWUP":
        path = DOCS / "NEXT_PROMPT_CRYPTO_FAMILY_B_RV_SLOW_HORIZON_FOLLOWUP_001.md"
        body = "# Next Prompt — Family B RV Slow Horizon Follow-up 001\n\nD1/H4 only; diagnostics only.\n"
    else:
        path = DOCS / "NEXT_PROMPT_CRYPTO_DATA_GAP_REPAIR_001.md"
        body = "# Next Prompt — Crypto Data Gap Repair 001\n"
    path.write_text(body, encoding="utf-8")
    return str(path.relative_to(ROOT))


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=DEFAULT_START.isoformat().replace("+00:00", "Z"))
    parser.add_argument("--end", default=DEFAULT_END.isoformat().replace("+00:00", "Z"))
    args = parser.parse_args(argv)

    try:
        cfg = get_research_database_config(environ=environ, require=True)
        store = PostgresCandleStore(cfg)
        series = load_all_series(
            store,
            start_utc=_parse_dt(args.start),
            end_utc=_parse_dt(args.end),
        )
        aligned_by_tf = {
            tf: align_btc_eth_pair(series["BTC_USD"][tf], series["ETH_USD"][tf])
            for tf in TIMEFRAMES
        }
        payload = run_full_diagnostics(aligned_by_tf)
        payload["start_utc"] = args.start
        payload["end_utc"] = args.end
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, indent=2))
        return 2

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    full_path = ARTIFACT_DIR / "full.json"
    full_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    for name in ("lead_lag", "relative_momentum", "divergence", "regime", "cost"):
        (ARTIFACT_DIR / f"{name}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "CRYPTO_FAMILY_B_LEAD_LAG_RELATIONSHIP_RESULT.md").write_text(
        render_lead_lag_md(payload), encoding="utf-8"
    )
    (DOCS / "CRYPTO_FAMILY_B_RELATIVE_MOMENTUM_RESULT.md").write_text(
        render_momentum_md(payload), encoding="utf-8"
    )
    (DOCS / "CRYPTO_FAMILY_B_DIVERGENCE_REVERSION_RESULT.md").write_text(
        render_divergence_md(payload), encoding="utf-8"
    )
    (DOCS / "CRYPTO_FAMILY_B_REGIME_SENSITIVITY_RESULT.md").write_text(
        render_regime_md(payload), encoding="utf-8"
    )
    (DOCS / "CRYPTO_FAMILY_B_COST_AND_FX_S4_COMPARISON_RESULT.md").write_text(
        render_cost_md(payload), encoding="utf-8"
    )
    (DOCS / "CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001_SYNTHESIS.md").write_text(
        render_synthesis_md(payload), encoding="utf-8"
    )
    next_prompt = write_next_prompt(payload)

    print(
        json.dumps(
            {
                "status": "PASS",
                "classification": payload["classification"]["label"],
                "artifacts": str(ARTIFACT_DIR.relative_to(ROOT)),
                "next_prompt": next_prompt,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
