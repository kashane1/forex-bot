"""Study 3 — pair-level baseline (artifact-backed, no fresh broker data).

Pulls CAMPAIGN_005's random-entry expectancy by pair and the per-pair
untouched-test results from CAMPAIGN_002 / 003 / 004 and the
train+validation results from CAMPAIGN_007 / 008 / 009. Output: per
pair, did any prior campaign cleanly beat the random-entry baseline?

The point is *not* to re-litigate any campaign verdict — the prior
verdicts stand. It is to answer:

  > Is there a pair on this universe where some prior strategy ever
  > showed *materially* less-bad behavior than the random-entry null,
  > so a future edge-discovery candidate has a defensible reason to
  > start there?

All numbers in this study are copied from the committed campaign
reports under `backtests/`. No re-computation, no new candle fetch.
The file paths and copied values are recorded so a reviewer can spot-
check every cell.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = REPO_ROOT / "research" / "edge_discovery" / "studies" / "outputs"

# --- Source cells (verbatim from committed reports) --------------------------

# CAMPAIGN_005 random-entry expectancy R, matched-frequency 20 seeds,
# fixed 30-bar hold, bid/ask fills + base costs.
# Source: backtests/CAMPAIGN_005_BENCHMARKS_REPORT.md, "Benchmark 3"
RANDOM_R_BY_PAIR = {
    "EUR_USD": -0.183,
    "GBP_USD": -0.107,
    "USD_JPY": -0.122,
    "AUD_USD": -0.147,
    "USD_CAD": -0.008,
    "USD_CHF": -0.004,
}

# CAMPAIGN_002 untouched-test (H4) expectancy R by pair.
# Source: backtests/CAMPAIGN_002_REAL_OANDA_REPORT.md
C002_H4_TEST_R = {
    "EUR_USD": +0.257,
    "GBP_USD": -0.028,
    "USD_JPY": -0.002,
    "AUD_USD": -0.037,
    "USD_CAD": -0.159,
    "USD_CHF": -0.459,
}

# CAMPAIGN_003 untouched-test expectancy R by pair.
# Source: backtests/CAMPAIGN_003_CONTROLLED_ADX_REPORT.md, "Metrics by pair — untouched test"
C003_TEST_R = {
    "EUR_USD": +0.257,
    "GBP_USD": -0.028,
    "USD_JPY": -0.002,
    "AUD_USD": -0.037,
    "USD_CAD": -0.159,
    "USD_CHF": -0.459,
}

# CAMPAIGN_004 untouched-test expectancy R by pair.
# Source: backtests/CAMPAIGN_004_VOLATILITY_BREAKOUT_REPORT.md, "Metrics by pair — untouched test"
C004_TEST_R = {
    "EUR_USD": -0.322,
    "GBP_USD": -0.148,
    "USD_JPY": -0.000,
    "AUD_USD": -0.104,
    "USD_CAD": -0.100,
    "USD_CHF": -0.307,
}

# CAMPAIGN_007 validation (test lockbox NOT opened) expectancy R by pair.
# Source: backtests/CAMPAIGN_007_H4_PULLBACK_REPORT.md, "Metrics by pair — validation"
C007_VAL_R = {
    "EUR_USD": -0.193,
    "GBP_USD": -0.242,
    "USD_JPY": +0.000,
    "AUD_USD": -0.355,
    "USD_CAD": -0.141,
    "USD_CHF": -0.063,
}

# CAMPAIGN_008 validation expectancy R by pair.
# Source: backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md, "Metrics by pair — validation"
C008_VAL_R = {
    "EUR_USD": +0.310,
    "GBP_USD": +0.117,
    "USD_JPY": +0.001,
    "AUD_USD": +0.088,
    "USD_CAD": +0.105,
    "USD_CHF": +0.409,
}

# CAMPAIGN_009 validation expectancy R by pair.
# Source: backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md, "Metrics by pair — validation"
C009_VAL_R = {
    "EUR_USD": -0.023,
    "GBP_USD": +0.391,
    "USD_JPY": -0.000,
    "AUD_USD": +0.248,
    "USD_CAD": +0.014,
    "USD_CHF": +0.391,
}

CAMPAIGN_R: dict[str, dict[str, float]] = {
    "CAMPAIGN_002_H4_test": C002_H4_TEST_R,
    "CAMPAIGN_003_test": C003_TEST_R,
    "CAMPAIGN_004_test": C004_TEST_R,
    "CAMPAIGN_007_val": C007_VAL_R,
    "CAMPAIGN_008_val": C008_VAL_R,
    "CAMPAIGN_009_val": C009_VAL_R,
}
# Validation campaigns whose test lockbox was never opened — listed so
# the per-cell label can warn the reviewer.
VALIDATION_ONLY_CAMPAIGNS = frozenset({"CAMPAIGN_007_val", "CAMPAIGN_008_val", "CAMPAIGN_009_val"})

# Materially-above-null threshold (R units). Anything below this is
# treated as "within noise of the random-entry baseline."
MATERIAL_GAP_R = 0.05


@dataclass(frozen=True)
class PairCell:
    pair: str
    random_r: float
    campaign_r_by_campaign: dict[str, float]
    gap_r_by_campaign: dict[str, float]
    best_gap_r: float
    best_campaign: str
    n_materially_above_null: int
    n_test_window_above_null: int
    n_validation_only_above_null: int


def _build_cells() -> list[PairCell]:
    cells: list[PairCell] = []
    for pair, rand in RANDOM_R_BY_PAIR.items():
        camp_r = {c: scores[pair] for c, scores in CAMPAIGN_R.items()}
        gaps = {c: round(v - rand, 4) for c, v in camp_r.items()}
        best_c, best_g = max(gaps.items(), key=lambda kv: kv[1])
        materially = sum(1 for g in gaps.values() if g >= MATERIAL_GAP_R)
        test_above = sum(
            1 for c, g in gaps.items()
            if g >= MATERIAL_GAP_R and c not in VALIDATION_ONLY_CAMPAIGNS
        )
        val_only_above = sum(
            1 for c, g in gaps.items()
            if g >= MATERIAL_GAP_R and c in VALIDATION_ONLY_CAMPAIGNS
        )
        cells.append(
            PairCell(
                pair=pair,
                random_r=rand,
                campaign_r_by_campaign=camp_r,
                gap_r_by_campaign=gaps,
                best_gap_r=best_g,
                best_campaign=best_c,
                n_materially_above_null=materially,
                n_test_window_above_null=test_above,
                n_validation_only_above_null=val_only_above,
            )
        )
    return cells


def _markdown(cells: list[PairCell]) -> str:
    lines: list[str] = []
    lines.append("# Edge-discovery study — pair_level_baseline")
    lines.append("")
    lines.append("> Exploratory lab output. Not a strategy verdict; does not approve,")
    lines.append("> promote, or change any campaign status. See")
    lines.append("> `docs/research/EDGE_DISCOVERY_LAB_001_PLAN.md`.")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append(
        "Per pair: did any prior campaign cleanly beat the artifact-backed "
        "random-entry baseline (CAMPAIGN_005, by-pair) by at least "
        f"`{MATERIAL_GAP_R:+.2f}` R? If so, was it on the **test window** "
        "(test lockbox opened — CAMPAIGN_002 / 003 / 004) or only on the "
        "**validation window** (test lockbox never opened — CAMPAIGN_007 / "
        "008 / 009)?"
    )
    lines.append("")
    lines.append("## Per-pair table (expectancy R)")
    lines.append("")
    camps = list(CAMPAIGN_R.keys())
    lines.append("| pair | random R | " + " | ".join(camps) + " | best gap | best campaign | n above null (test) | n above null (val-only) |")
    lines.append("|---" * (1 + 1 + len(camps) + 4) + "|")
    for c in cells:
        row = [c.pair, f"{c.random_r:+.3f}"]
        for camp in camps:
            row.append(f"{c.campaign_r_by_campaign[camp]:+.3f}")
        row.append(f"{c.best_gap_r:+.3f}")
        row.append(c.best_campaign)
        row.append(str(c.n_test_window_above_null))
        row.append(str(c.n_validation_only_above_null))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines.append("## Reading")
    lines.append("")
    lines.append(
        "- `random R` = CAMPAIGN_005 random-entry expectancy for that "
        "pair (mean of 20 seeds × matched-frequency entries). The "
        "univ-wide mean is **−0.095 R**."
    )
    lines.append(
        f"- A cell is `>= random R + {MATERIAL_GAP_R:+.2f}` only when "
        "the strategy's expectancy is *materially* better than random "
        "entry; smaller gaps are within the random null's noise band."
    )
    lines.append(
        "- A pair with `n above null (test) >= 1` shows at least one "
        "*test-window* result above the null — that is the strongest "
        "form of evidence in the archive. A pair with only `n above null "
        "(val-only) >= 1` was above null only on a validation window "
        "whose test lockbox never opened — that is the high-overfit-risk "
        "pattern flagged in the meta-analysis (Lesson 4)."
    )
    lines.append(
        "- The lab does not interpret these cells as future expectations. "
        "They are descriptive history; a new edge-discovery candidate "
        "should still run its own per-pair forward-return study against "
        "its own random null."
    )
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    lines.append(
        "- Numbers are verbatim from committed CAMPAIGN_002, 003, 004, "
        "005, 007, 008, 009 reports under `backtests/`. The source row "
        "for each cell is named in the source-cells block at the top of "
        "`research/edge_discovery/studies/study_pair_baseline.py`."
    )
    lines.append("")
    return "\n".join(lines)


def run() -> Path:
    cells = _build_cells()
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    md_path = OUTPUTS / "study_pair_baseline.md"
    json_path = OUTPUTS / "study_pair_baseline.json"
    md_path.write_text(_markdown(cells) + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "label": "pair_level_baseline",
                "material_gap_R": MATERIAL_GAP_R,
                "random_R_by_pair": RANDOM_R_BY_PAIR,
                "campaign_R": CAMPAIGN_R,
                "validation_only_campaigns": sorted(VALIDATION_ONLY_CAMPAIGNS),
                "per_pair_cells": [asdict(c) for c in cells],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return md_path


if __name__ == "__main__":
    p = run()
    print(f"wrote {p}")
