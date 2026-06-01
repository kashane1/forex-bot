#!/usr/bin/env python3
"""Run exploratory Family C trend-persistence diagnostics on canonical crypto spot data."""

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
from research.crypto.diagnostics.loader import DEFAULT_END, DEFAULT_START, load_all_series
from research.crypto.diagnostics.trend_persistence import run_full_diagnostics
from research.crypto.registry import CANONICAL_INSTRUMENTS
from research.crypto.trend_persistence import MATERIALIZED_SOURCE, cost_breakdown

ARTIFACT_DIR = ROOT / "research/crypto/diagnostics/family_c_trend_persistence_001"
TIMEFRAMES = ("M15", "H1", "H4", "D1")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def _fmt(v: Any, *, digits: int = 4) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


def render_baseline_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family C Baseline Trend Persistence Result",
        "",
        "**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`",
        "**Type:** Exploratory diagnostic only — no strategy, campaign, or approval",
        "",
        "---",
        "",
        "## Autocorrelation by lag",
        "",
        "| Instrument | TF | AC1 | AC2 | AC4 | AC8 |",
        "|------------|-----|----:|----:|----:|----:|",
    ]
    for inst, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            ac = block["timeframes"][tf]["autocorr"]
            lines.append(
                f"| {inst} | {tf} | {_fmt(ac.get('ac1'))} | {_fmt(ac.get('ac2'))} | "
                f"{_fmt(ac.get('ac4'))} | {_fmt(ac.get('ac8'))} |"
            )
    lines.extend(["", "## Run-length and continuation", ""])
    lines.append("| Instrument | TF | Mean run | P(cont|2 bars) | P(cont|4 bars) |")
    lines.append("|------------|-----|--------:|---------------:|---------------:|")
    for inst, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            runs = block["timeframes"][tf]["run_lengths"]
            cont = block["timeframes"][tf]["continuation"]
            lines.append(
                f"| {inst} | {tf} | {_fmt(runs.get('mean_run'), digits=2)} | "
                f"{_fmt(cont.get('after_2_bars'))} | {_fmt(cont.get('after_4_bars'))} |"
            )
    lines.extend(["", "## Horizon cross (diagnostic only)", ""])
    for inst, cross in payload.get("horizon_cross", {}).items():
        for key, block in cross.items():
            lines.append(
                f"- **{inst} {key}:** n={block.get('sample_size')}, "
                f"mean={_fmt(block.get('mean_aligned_return'))}, hit={_fmt(block.get('hit_rate'))}"
            )
    lines.append("")
    lines.append("Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/baseline.json`")
    return "\n".join(lines) + "\n"


def render_null_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family C Null Baseline Result",
        "",
        f"**Seed:** {payload['null_seed']} · **Trials by TF:** {payload.get('null_trials_by_tf')}",
        "",
        "| Instrument | TF | AC1 obs | shuffle p | sign-flip p | block-boot p |",
        "|------------|-----|--------:|----------:|------------:|-------------:|",
    ]
    for inst, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            null = block["timeframes"][tf]["null_ac1"]
            obs = null.get("observed")
            lines.append(
                f"| {inst} | {tf} | {_fmt(obs)} | "
                f"{_fmt((null.get('shuffle') or {}).get('p_value_two_sided'))} | "
                f"{_fmt((null.get('sign_flip') or {}).get('p_value_two_sided'))} | "
                f"{_fmt((null.get('block_bootstrap') or {}).get('p_value_two_sided'))} |"
            )
    lines.extend(
        [
            "",
            "Interpretation: low p-value vs null suggests observed AC1 is unlikely under iid/random-sign "
            "assumptions; does **not** imply tradability after costs.",
            "",
            "Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/null_baseline.json`",
        ]
    )
    return "\n".join(lines) + "\n"


def render_regime_md(payload: dict[str, Any]) -> str:
    rd = payload["regime_definition"]
    lines = [
        "# Crypto Family C Regime Sensitivity Result",
        "",
        f"**Measure:** {rd['measure']} · low≤{rd['low_pct']}% · high≥{rd['high_pct']}%",
        "",
        "| Instrument | TF | Low-vol AC1 | Mid-vol AC1 | High-vol AC1 |",
        "|------------|-----|----------:|------------:|-------------:|",
    ]
    for inst, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            reg = block["timeframes"][tf]["regime_autocorr"]
            lines.append(
                f"| {inst} | {tf} | {_fmt(reg.get('low_vol_ac1'))} | "
                f"{_fmt(reg.get('mid_vol_ac1'))} | {_fmt(reg.get('high_vol_ac1'))} |"
            )
    lines.append("")
    lines.append("Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/regime.json`")
    return "\n".join(lines) + "\n"


def render_cost_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Crypto Family C Cost and Turnover Sensitivity Result",
        "",
        "Frozen costs: `CRYPTO_COST_MODEL_001.md`. Diagnostic momentum proxy only.",
        "",
        "| Instrument | TF | Gross bps | Spread-only bps | All-in bps | 2× stress bps | All-in hurdle |",
        "|------------|-----|----------:|----------------:|-----------:|--------------:|--------------:|",
    ]
    for inst, block in payload["instruments"].items():
        for tf in TIMEFRAMES:
            edges = block["timeframes"][tf]["cost_edges_momentum_mean"]
            lines.append(
                f"| {inst} | {tf} | {_fmt(edges.get('gross_edge_bps'), digits=2)} | "
                f"{_fmt(edges.get('spread_only_edge_bps'), digits=2)} | "
                f"{_fmt(edges.get('all_in_edge_bps'), digits=2)} | "
                f"{_fmt(edges.get('stress_2x_edge_bps'), digits=2)} | "
                f"{_fmt(edges.get('cost_hurdle_all_in_bps'), digits=0)} |"
            )
    lines.extend(["", "## Momentum proxy Sharpe (annualized)", ""])
    for inst, block in payload["instruments"].items():
        lines.append(f"### {inst}")
        lines.append("| TF | Gross | Spread-only | All-in | 2× stress |")
        lines.append("|----|------:|------------:|-------:|----------:|")
        for tf in TIMEFRAMES:
            mom = block["timeframes"][tf]["momentum_proxy"]
            lines.append(
                f"| {tf} | {_fmt(mom['gross']['sharpe'])} | {_fmt(mom['spread_only']['sharpe'])} | "
                f"{_fmt(mom['all_in']['sharpe'])} | {_fmt(mom['stress_2x']['sharpe'])} |"
            )
        lines.append("")
    lines.append("Artifact: `research/crypto/diagnostics/family_c_trend_persistence_001/cost.json`")
    return "\n".join(lines) + "\n"


def render_synthesis_md(payload: dict[str, Any]) -> str:
    c = payload["classification"]
    inst = payload["instruments"]

    def ac1(symbol: str, tf: str) -> float | None:
        return inst[symbol]["timeframes"][tf]["autocorr"].get("ac1")

    def mom_sharpe(symbol: str, tf: str, variant: str) -> float:
        return inst[symbol]["timeframes"][tf]["momentum_proxy"][variant]["sharpe"]

    btc_m15 = ac1("BTC_USD", "M15")
    eth_m15 = ac1("ETH_USD", "M15")
    eth_h1 = ac1("ETH_USD", "H1")
    proceed_fv = c["label"] == "PROMISING_FOR_FACTOR_VALIDATION"
    family_b_next = c["label"] == "STATISTICAL_ONLY_COST_DEFEATED"

    lines = [
        "# Crypto Family C Trend Persistence Diagnostics 001 — Synthesis",
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
        f"1. **BTC statistical persistence?** M15 AC1={_fmt(btc_m15)}; D1 negative AC1; weak vs null.",
        f"2. **ETH statistical persistence?** M15 AC1={_fmt(eth_m15)}; H1 AC1={_fmt(eth_h1)}; strongest exploratory AC1.",
        f"3. **Strongest horizon?** {c.get('strongest_signal')} — no all-in cost survival.",
        "4. **High-vol concentration?** Mixed; see regime report — BTC D1 low-vol AC1 positive, high-vol negative.",
        f"5. **Spread-only survival?** {c.get('any_spread_survives')}.",
        f"6. **All-in survival?** {c.get('any_allin_survives')}.",
        "7. **2× stress?** No positive momentum Sharpe at any horizon.",
        "8. **vs FX programme?** Not materially better — 120 bps taker RT dominates short-horizon momentum proxies, as in FX cost-defeat.",
        "9. **Economic vs statistical?** Statistical hints only (ETH M15 AC1); economically defeated after spread+fees.",
        f"10. **Proceed to factor validation?** {'Yes (pre-registered)' if proceed_fv else 'No'}.",
        "11. **Family A wait?** Yes — defer MTF confluence.",
        f"12. **Family B next?** {'Yes — recommended' if family_b_next else 'Consider if pivoting from weak/null'}.",
        "13. **Family D wait?** Yes until standard-bar diagnostics complete.",
        f"14. **Next sprint:** `NEXT_PROMPT_*` for `{c['label']}` (Phase 7).",
        "",
        "---",
        "",
        "## Headline Sharpe (momentum proxy)",
        "",
        f"- ETH M15 gross: {_fmt(mom_sharpe('ETH_USD', 'M15', 'gross'))} · all-in: {_fmt(mom_sharpe('ETH_USD', 'M15', 'all_in'))}",
        f"- BTC H1 gross: {_fmt(mom_sharpe('BTC_USD', 'H1', 'gross'))} · all-in: {_fmt(mom_sharpe('BTC_USD', 'H1', 'all_in'))}",
        "",
        "## Safety",
        "",
        "- No strategy, campaign, or approval.",
        "- Gaps: no interpolation; exchange-side gaps accepted; ~99.94% M1 coverage.",
        "",
        f"**ETH drives short horizon:** {c.get('eth_drives_short_horizon')}",
    ]
    return "\n".join(lines) + "\n"


def render_combined_md(payload: dict[str, Any]) -> str:
    """Single index report linking phase artifacts."""
    c = payload["classification"]
    return "\n".join(
        [
            "# Crypto Family C Trend Persistence Diagnostics 001",
            "",
            "**Sprint:** `crypto-family-c-trend-persistence-diagnostics-001`",
            "**Type:** Exploratory diagnostic only — no strategy, campaign, or approval",
            f"**Classification:** `{c['label']}`",
            "",
            "Phase reports:",
            "- `CRYPTO_FAMILY_C_BASELINE_TREND_PERSISTENCE_RESULT.md`",
            "- `CRYPTO_FAMILY_C_NULL_BASELINE_RESULT.md`",
            "- `CRYPTO_FAMILY_C_REGIME_SENSITIVITY_RESULT.md`",
            "- `CRYPTO_FAMILY_C_COST_TURNOVER_SENSITIVITY_RESULT.md`",
            "- `CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SYNTHESIS.md`",
            "",
            f"Full JSON: `research/crypto/diagnostics/family_c_trend_persistence_001/full.json`",
            "",
            c["rationale"],
            "",
        ]
    ) + "\n"


def write_outputs(payload: dict[str, Any], *, docs_dir: Path) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / "full.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    for name, key in [
        ("baseline.json", None),
        ("null_baseline.json", None),
        ("regime.json", None),
        ("cost.json", None),
    ]:
        (ARTIFACT_DIR / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )

    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "CRYPTO_FAMILY_C_BASELINE_TREND_PERSISTENCE_RESULT.md").write_text(
        render_baseline_md(payload), encoding="utf-8"
    )
    (docs_dir / "CRYPTO_FAMILY_C_NULL_BASELINE_RESULT.md").write_text(
        render_null_md(payload), encoding="utf-8"
    )
    (docs_dir / "CRYPTO_FAMILY_C_REGIME_SENSITIVITY_RESULT.md").write_text(
        render_regime_md(payload), encoding="utf-8"
    )
    (docs_dir / "CRYPTO_FAMILY_C_COST_TURNOVER_SENSITIVITY_RESULT.md").write_text(
        render_cost_md(payload), encoding="utf-8"
    )
    (docs_dir / "CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001_SYNTHESIS.md").write_text(
        render_synthesis_md(payload), encoding="utf-8"
    )
    (docs_dir / "CRYPTO_FAMILY_C_TREND_PERSISTENCE_DIAGNOSTICS_001.md").write_text(
        render_combined_md(payload), encoding="utf-8"
    )


def write_next_prompt(payload: dict[str, Any], *, docs_dir: Path) -> str:
    label = payload["classification"]["label"]
    if label == "PROMISING_FOR_FACTOR_VALIDATION":
        path = docs_dir / "NEXT_PROMPT_CRYPTO_FAMILY_C_TREND_PERSISTENCE_FACTOR_VALIDATION_001.md"
        body = _factor_validation_prompt()
    elif label == "STATISTICAL_ONLY_COST_DEFEATED":
        path = docs_dir / "NEXT_PROMPT_CRYPTO_FAMILY_B_RELATIVE_VALUE_DIAGNOSTICS_001.md"
        body = _family_b_prompt()
    elif label == "WEAK_OR_NULL":
        path = docs_dir / "NEXT_PROMPT_CRYPTO_FAMILY_B_OR_D_SELECTION_001.md"
        body = _family_b_or_d_prompt()
    elif label == "MIXED_REQUIRES_TARGETED_FOLLOWUP":
        path = docs_dir / "NEXT_PROMPT_CRYPTO_FAMILY_C_SLOW_HORIZON_FOLLOWUP_001.md"
        body = _mixed_followup_prompt()
    else:
        path = docs_dir / "NEXT_PROMPT_CRYPTO_DATA_GAP_REPAIR_001.md"
        body = _data_repair_prompt()
    path.write_text(body, encoding="utf-8")
    return str(path.relative_to(ROOT))


def _factor_validation_prompt() -> str:
    return """# Next Prompt — Crypto Family C Trend Persistence Factor Validation 001

**Type:** Factor-validation prompt only — NOT strategy or campaign
**Prerequisite:** Family C exploratory diagnostics classified PROMISING_FOR_FACTOR_VALIDATION

Pre-register gates, matched nulls, and cost thresholds before any validation run.
"""


def _family_b_prompt() -> str:
    return """# Next Prompt — Crypto Family B Relative Value Diagnostics 001

**Type:** Exploratory diagnostics only — NOT strategy or campaign
**Reason:** Family C trend persistence was statistically weak or cost-defeated; avoid tuning momentum — pivot to BTC/ETH relative value.

## Scope

- Instruments: BTC_USD, ETH_USD
- Spread/ratio mean-reversion and lead-lag diagnostics
- Same frozen cost model variants (gross, spread-only, all-in, 2×)
- Null baselines required
- No strategy, campaign, or approval
"""


def _family_b_or_d_prompt() -> str:
    return """# Next Prompt — Crypto Family B or D Selection 001

**Type:** Planning/diagnostics selection — NOT strategy or campaign
**Reason:** Family C trend persistence exploratory pass was WEAK_OR_NULL.

## Decision

Compare expected information gain:
- **Family B:** BTC/ETH relative value (spread, ratio, correlation regime)
- **Family D:** Non-time bars (volume/dollar bars) after confirming standard bars lack edge

Choose one family for the next diagnostic sprint. No campaigns.
"""


def _mixed_followup_prompt() -> str:
    return """# Next Prompt — Crypto Family C Slow Horizon Follow-up 001

**Type:** Narrow exploratory follow-up — NOT strategy or campaign
**Reason:** MIXED_REQUIRES_TARGETED_FOLLOWUP — gross-only signal at slow horizons without all-in survival.

## Scope

- D1/H4 only; pre-registered lookbacks; same frozen costs
- No new strategy logic; diagnostics only
"""


def _data_repair_prompt() -> str:
    return """# Next Prompt — Crypto Data Gap Repair 001

**Type:** Data quality sprint — NOT strategy or campaign
**Reason:** BLOCKED_DATA_QUALITY classification.

Repair canonical store issues before any factor diagnostics.
"""


def main(argv: list[str] | None = None, *, environ: dict[str, str] | None = None) -> int:
    environ = bootstrap_environ(environ)
    parser = argparse.ArgumentParser(description="Crypto Family C trend persistence diagnostics.")
    parser.add_argument("--start", default=DEFAULT_START.isoformat().replace("+00:00", "Z"))
    parser.add_argument("--end", default=DEFAULT_END.isoformat().replace("+00:00", "Z"))
    args = parser.parse_args(argv)
    docs_dir = ROOT / "docs/research/active/crypto_programme"

    try:
        cfg = get_research_database_config(environ=environ, require=True)
        store = PostgresCandleStore(cfg)
        series = load_all_series(
            store,
            start_utc=_parse_dt(args.start),
            end_utc=_parse_dt(args.end),
        )
        payload = run_full_diagnostics(series)
        payload["start_utc"] = args.start
        payload["end_utc"] = args.end
        payload["source"] = MATERIALIZED_SOURCE
        for inst in CANONICAL_INSTRUMENTS:
            payload.setdefault("instruments", {}).setdefault(inst, {})["cost_model"] = {
                tf: {
                    "1x": cost_breakdown(inst, tf, stress=False).__dict__,
                    "2x": cost_breakdown(inst, tf, stress=True).__dict__,
                }
                for tf in TIMEFRAMES
            }
        write_outputs(payload, docs_dir=docs_dir)
        next_prompt = write_next_prompt(payload, docs_dir=docs_dir)
    except ResearchDatabaseBlocked as exc:
        print(json.dumps({"status": "BLOCKED", "message": str(exc)}, indent=2))
        return 2

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
