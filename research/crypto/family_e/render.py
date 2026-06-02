"""Render Family E result docs + classification directly from JSON results.

All numbers in the markdown docs are machine-rendered from the diagnostic result
dicts — never eye-transcribed (a hard lesson from the FX programme).
"""

from __future__ import annotations

from research.crypto.family_e.reporting import GateInputs, classify, fmt

VARIANTS = ("gross", "spread_only", "all_in", "stress_2x")


def _shuffled_p(cell: dict) -> float | None:
    ng = cell.get("nulls_gross")
    if not ng:
        return None
    return ng["shuffled"]["p_value_two_sided"]


def _matched_p(cell: dict) -> float | None:
    ng = cell.get("nulls_gross")
    if not ng:
        return None
    return ng["matched_random"]["p_value_greater"]


def collect_decile_pvalues(result: dict, prefix: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for h, cell in result["horizons"].items():
        p = _shuffled_p(cell["pooled"])
        if p is not None:
            out[f"{prefix}|h{h}|pooled_gross"] = p
    return out


def _cell_row(name: str, cell: dict) -> str:
    e = cell["edges"]
    return (
        f"| {name} | {cell['n']} | {fmt(e['gross'],digits=6)} | "
        f"{fmt(e['spread_only'],digits=6)} | {fmt(e['all_in'],digits=6)} | "
        f"{fmt(e['stress_2x'],digits=6)} | {fmt(_shuffled_p(cell))} | {fmt(_matched_p(cell))} |"
    )


def classify_decile(result: dict, holm: dict, prefix: str, *, insts: list[str]) -> dict:
    """Classify a decile diagnostic using Holm-adjusted pooled-gross p across horizons."""
    best = None
    for h, cell in result["horizons"].items():
        pooled = cell["pooled"]
        key = f"{prefix}|h{h}|pooled_gross"
        adj_p = holm.get(key, 1.0)
        clears = adj_p < 0.05 and pooled["edges"]["gross"] > 0
        btc_ok = cell[insts[0]]["edges"]["gross"] > 0
        eth_ok = cell[insts[1]]["edges"]["gross"] > 0
        gate = GateInputs(
            gross_effect_clears_null=clears,
            all_in_net_positive=pooled["edges"]["all_in"] > 0,
            stress_net_positive=pooled["edges"]["stress_2x"] > 0,
            btc_supportive=btc_ok,
            eth_supportive=eth_ok,
            pooled_supportive=pooled["edges"]["gross"] > 0,
            sufficient_observations=pooled["n"] >= 100,
        )
        label, rationale = classify(gate)
        rank = ("candidate_for_front_gate", "statistical_only_cost_defeated",
                "cost_defeated", "rejected", "blocked_data_quality").index(label)
        cand = (-rank, pooled["edges"]["all_in"])
        if best is None or cand > best[0]:
            best = (cand, h, label, rationale, adj_p)
    if best is None:
        return {"label": "blocked_data_quality", "rationale": "no horizons evaluated"}
    _, h, label, rationale, adj_p = best
    return {"label": label, "rationale": rationale, "decisive_horizon": h,
            "holm_adj_p_pooled_gross": adj_p}


def classify_cell(pooled_cell: dict, *, btc_cell: dict, eth_cell: dict, holm_p: float,
                  oi_low_power: bool = False) -> dict:
    """Classify a single pooled cohort cell against its BTC/ETH legs."""
    clears = holm_p < 0.05 and pooled_cell["edges"]["gross"] > 0
    gate = GateInputs(
        gross_effect_clears_null=clears,
        all_in_net_positive=pooled_cell["edges"]["all_in"] > 0,
        stress_net_positive=pooled_cell["edges"]["stress_2x"] > 0,
        btc_supportive=btc_cell["edges"]["gross"] > 0,
        eth_supportive=eth_cell["edges"]["gross"] > 0,
        pooled_supportive=pooled_cell["edges"]["gross"] > 0,
        sufficient_observations=pooled_cell["n"] >= 100,
        oi_depth_limited=oi_low_power,
    )
    label, rationale = classify(gate)
    return {"label": label, "rationale": rationale, "holm_adj_p": holm_p}


def collect_persistence_pvalues(result: dict, prefix: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for k, block in result["k_values"].items():
        for h, cell in block["horizons"].items():
            p = _shuffled_p(cell["pooled"]["continuation"])
            if p is not None:
                out[f"{prefix}|k{k}|h{h}|cont_pooled_gross"] = p
    return out


def render_persistence_doc(*, sprint_line: str, result: dict, classification: dict,
                           insts: list[str]) -> str:
    lines = [
        "# Crypto Family E Diagnostic 2 — Funding Trend Continuation Result",
        "", sprint_line,
        "**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.",
        "", f"**Hypothesis:** {result.get('hypothesis','')}",
        "", f"**Classification:** `{classification['label']}`",
        "", classification.get("rationale", ""), "",
        "Continuation trades in the sign of persistent funding; contrarian is the after-cost "
        "alternative. Monotonicity across k∈{3,6,9} is the design's pass signal.", "",
    ]
    for k, block in result["k_values"].items():
        lines += [f"## k = {k} settlements", "",
                  "| Horizon | Split | n | cont gross | cont all-in | cont 2× | contra gross | shuffled p |",
                  "|--------:|-------|--:|-----------:|------------:|--------:|-------------:|-----------:|"]
        for h, cell in block["horizons"].items():
            for name in (insts[0], insts[1], "pooled"):
                c = cell[name]["continuation"]
                ca = cell[name]["contrarian"]
                lines.append(
                    f"| {h} | {name} | {c['n']} | {fmt(c['edges']['gross'],digits=6)} | "
                    f"{fmt(c['edges']['all_in'],digits=6)} | {fmt(c['edges']['stress_2x'],digits=6)} | "
                    f"{fmt(ca['edges']['gross'],digits=6)} | {fmt(_shuffled_p(c))} |"
                )
        lines += [f"Skipped: {block.get('skipped')}.", ""]
    lines += ["## Why this is not a strategy", "",
              "Exploratory sign test; no portfolio construction. Competes with Diagnostic 1 — "
              "at most one of reversion/continuation can hold.", ""]
    return "\n".join(lines) + "\n"


def render_cross_doc(*, sprint_line: str, result: dict, classification: dict) -> str:
    lines = [
        "# Crypto Family E Diagnostic 6 — Cross-Asset Confirmation Result",
        "", sprint_line,
        "**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.",
        "", f"**Hypothesis:** {result.get('hypothesis','')}",
        "", f"**Classification:** `{classification['label']}`",
        "", classification.get("rationale", ""), "",
        "Agreement = both BTC & ETH funding in the same extreme decile (faded both legs, "
        "single-leg cost). Disagreement = one extreme, one neutral (relative-value, paired "
        "two-leg cost). Wrong-pairing swaps BTC/ETH returns as a control.", "",
    ]
    for h, cell in result.get("horizons", {}).items():
        lines += [f"## Horizon {h}h (n common windows = {cell['n_common_windows']})", "",
                  "| Cohort | n legs | gross | all-in | 2× stress | shuffled p |",
                  "|--------|-------:|------:|-------:|----------:|-----------:|"]
        for key, label in (("agreement_directional", "agreement (directional)"),
                           ("disagreement_relative_value", "disagreement (RV)"),
                           ("wrong_pairing_control", "wrong-pairing (control)")):
            c = cell[key]
            lines.append(
                f"| {label} | {c['n']} | {fmt(c['edges']['gross'],digits=6)} | "
                f"{fmt(c['edges']['all_in'],digits=6)} | {fmt(c['edges']['stress_2x'],digits=6)} | "
                f"{fmt(_shuffled_p(c))} |"
            )
        lines.append("")
    lines += ["## Why this is not a strategy", "",
              "Exploratory; explicitly inherits Family B's paired-cost caution.", ""]
    return "\n".join(lines) + "\n"


def render_regime_doc(*, sprint_line: str, result: dict, impact: str) -> str:
    lines = [
        "# Crypto Family E Diagnostic 7 — Regime Conditioning Result",
        "", sprint_line,
        "**Type:** Exploratory diagnostic only — highest forking-path risk.",
        "", "**Frozen regimes:** " + ", ".join(result["regimes"]) + ".",
        "", "Applied to base diagnostics 1 (funding reversion h24), 2 (continuation k6 h24), "
        "3 (basis reversion h24). Tercile 0=low, 1=mid, 2=high of the regime variable. "
        "Holm discipline applies; a tiny regime slice must not override base failure.", "",
        f"**Classification impact:** {impact}", "",
    ]
    for base, block in result["base_diagnostics"].items():
        lines += [f"## {base}", "",
                  "| Regime | Tercile | n | gross | all-in | 2× stress | shuffled p |",
                  "|--------|--------:|--:|------:|-------:|----------:|-----------:|"]
        for regime, cells in block.items():
            for t in (0, 1, 2):
                c = cells[f"tercile_{t}"]
                lines.append(
                    f"| {regime} | {t} | {c['n']} | {fmt(c['edges']['gross'],digits=6)} | "
                    f"{fmt(c['edges']['all_in'],digits=6)} | {fmt(c['edges']['stress_2x'],digits=6)} | "
                    f"{fmt(_shuffled_p(c))} |"
                )
        lines.append("")
    lines += ["## Forking-path warning", "",
              "Many regime cells × diagnostics × terciles → high multiple-comparisons risk. "
              "Any single favorable cell is treated as a forking-path artifact unless the base "
              "diagnostic also passed and the cell survives Holm.", ""]
    return "\n".join(lines) + "\n"


def render_oi_doc(*, sprint_line: str, result: dict) -> str:
    lines = [
        "# Crypto Family E Diagnostics 4 & 5 — OI Impulse / Funding-OI Interaction (LOW-POWER)",
        "", sprint_line,
        "**Type:** Exploratory, explicitly LOW-POWER. No strategy/campaign/front gate/approval.",
        "", "**Classification:** `blocked_low_power_oi`", "",
        result.get("note", ""), "",
        "## OI availability", "",
        "| Instrument | OI rows | low-power |",
        "|------------|--------:|:---------:|",
    ]
    for inst, a in result.get("availability", {}).items():
        lines.append(f"| {inst} | {a['n_oi_rows']} | {'yes' if a['low_power'] else 'no'} |")
    lines += ["",
              "With only ~180d aggregate daily OI, diagnostics 4 (OI impulse) and 5 (funding/OI "
              "interaction) cannot reach `candidate_for_front_gate`. Forward OI collection is the "
              "prerequisite for a powered test.", "",
              "## Recommendation", "",
              "Forward-collect per-instrument OI (8h or daily) before any OI-dependent diagnostic.", ""]
    return "\n".join(lines) + "\n"


def render_decile_doc(
    *, doc_title: str, sprint_line: str, result: dict, classification: dict,
    insts: list[str], extra_notes: str = "",
) -> str:
    lines = [
        f"# {doc_title}",
        "",
        sprint_line,
        "**Type:** Exploratory diagnostic only — no strategy, campaign, front gate, or approval.",
        "",
        f"**Hypothesis:** {result.get('hypothesis','')}",
        "",
        f"**Classification:** `{classification['label']}`",
        "",
        classification.get("rationale", ""),
        "",
        "Edges are mean per-entry net signed returns (fraction of notional). "
        "Funding cashflow (long pays short when funding>0) enters all-in and 2× stress.",
        "",
    ]
    for h, cell in result["horizons"].items():
        lines += [
            f"## Horizon {h}h",
            "",
            "| Split | n | gross | spread-only | all-in | 2× stress | shuffled p | matched p> |",
            "|-------|--:|------:|-----------:|-------:|----------:|-----------:|-----------:|",
            _cell_row(insts[0], cell[insts[0]]),
            _cell_row(insts[1], cell[insts[1]]),
            _cell_row("pooled", cell["pooled"]),
            "",
            f"Decile cuts (pooled inputs per-instrument): "
            f"{insts[0]} {cell[insts[0]].get('decile_cuts')}, "
            f"{insts[1]} {cell[insts[1]].get('decile_cuts')}.",
            f"Skipped windows: {result.get('skipped')}.",
            "",
        ]
    if extra_notes:
        lines += [extra_notes, ""]
    lines += [
        "## Why this is not a strategy",
        "",
        "One exploratory conditional-return statistic. No sizing, execution, walk-forward, "
        "or portfolio construction. A statistically-real effect is not a tradable edge.",
        "",
        f"## Front-gate eligibility: "
        f"{'candidate (FUTURE design only)' if classification['label']=='candidate_for_front_gate' else 'no'}",
        "",
    ]
    return "\n".join(lines) + "\n"
