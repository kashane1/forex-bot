#!/usr/bin/env python3
"""Dry-run a walk-forward fold plan.

Generates a fold plan from CLI args, validates it under the
protocol rules, and writes plan.json + plan.md to the chosen
output directory. Does NOT execute a strategy; does NOT touch any
campaign or backtest engine.

The script is intentionally self-contained:
- no imports from forex_bot;
- no network / broker / OANDA calls;
- no writes to configs/approved_strategies.yaml.

See docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md and
research/walk_forward/README.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# isort: off
from research.walk_forward.models import ParameterMode, SplitStyle
from research.walk_forward.reporting import render_plan_md
from research.walk_forward.splits import (
    expanding_window_plan,
    rolling_window_plan,
)
from research.walk_forward.validate import PlanValidationError, validate_plan
# isort: on


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run a walk-forward fold plan. Generates + validates the "
            "plan; does not execute a strategy."
        )
    )
    parser.add_argument("--campaign-name", required=True)
    parser.add_argument(
        "--universe-start",
        type=date.fromisoformat,
        required=True,
        help="YYYY-MM-DD",
    )
    parser.add_argument(
        "--universe-end",
        type=date.fromisoformat,
        required=True,
        help="YYYY-MM-DD",
    )
    parser.add_argument(
        "--style",
        choices=[s.value for s in SplitStyle],
        default=SplitStyle.ROLLING.value,
    )
    parser.add_argument(
        "--parameter-mode",
        choices=[m.value for m in ParameterMode],
        default=ParameterMode.FROZEN.value,
        help=(
            "Strategy parameter selection mode. Only `frozen` is valid "
            "under the current research freeze."
        ),
    )
    parser.add_argument(
        "--train-days",
        type=int,
        required=True,
        help=(
            "rolling: train window length per fold; "
            "expanding: initial train window length"
        ),
    )
    parser.add_argument("--validation-days", type=int, required=True)
    parser.add_argument("--test-days", type=int, required=True)
    parser.add_argument(
        "--step-days",
        type=int,
        required=True,
        help=(
            "rolling: train start step between folds; "
            "expanding: train window growth between folds"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory to write plan.json and plan.md into.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    out_dir: Path = args.output
    out_dir.mkdir(parents=True, exist_ok=True)

    style = SplitStyle(args.style)
    parameter_mode = ParameterMode(args.parameter_mode)
    if parameter_mode is not ParameterMode.FROZEN:
        print(
            f"WARNING: parameter_mode={parameter_mode.value!r} is not the "
            f"default; only `frozen` is authorized under the current "
            f"research freeze.",
            file=sys.stderr,
        )

    if style is SplitStyle.ROLLING:
        plan = rolling_window_plan(
            campaign_name=args.campaign_name,
            universe_start=args.universe_start,
            universe_end=args.universe_end,
            train_window_days=args.train_days,
            validation_window_days=args.validation_days,
            test_window_days=args.test_days,
            step_days=args.step_days,
            parameter_mode=parameter_mode,
        )
    else:
        plan = expanding_window_plan(
            campaign_name=args.campaign_name,
            universe_start=args.universe_start,
            universe_end=args.universe_end,
            initial_train_window_days=args.train_days,
            validation_window_days=args.validation_days,
            test_window_days=args.test_days,
            step_days=args.step_days,
            parameter_mode=parameter_mode,
        )

    try:
        validate_plan(plan)
    except PlanValidationError as exc:
        print(f"PLAN INVALID: {exc}", file=sys.stderr)
        return 2

    json_path = out_dir / "plan.json"
    md_path = out_dir / "plan.md"
    json_path.write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, default=str),
        encoding="utf-8",
    )
    md_path.write_text(render_plan_md(plan), encoding="utf-8")

    print(f"Wrote: {json_path}")
    print(f"       {md_path}")
    print(f"Fold count: {len(plan.folds)}")
    print(f"Style: {plan.split_style.value} · parameter_mode: {plan.parameter_mode.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
