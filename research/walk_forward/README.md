# research/walk_forward — walk-forward research harness

A reusable, independent fold-generation library for walk-forward
strategy research. Produces fold plans (train, validation, test
date windows), validates them, and renders summaries. Strategy
execution stays in `src/forex_bot/backtesting/`.

> `strategy_evidence: false`. The harness is diagnostic
> infrastructure. It does not approve a strategy. CAMPAIGN_002
> remains REJECT. `configs/approved_strategies.yaml` stays empty.
> Paper / demo / live remain blocked.

## Module layout

| module | role |
|---|---|
| `models.py` | Pydantic models — `Fold`, `WalkForwardPlan`, `FoldMetrics`, `AggregateMetrics`, `WalkForwardResults` |
| `splits.py` | `rolling_window_plan` and `expanding_window_plan` generators |
| `validate.py` | `validate_plan` — minimum fold count, forward-only ordering, rolling-mode no-leakage, all-boundaries-in-universe |
| `reporting.py` | `render_plan_md` and `render_results_md` |

No file under `research/walk_forward/` imports from `forex_bot`. A
grep-enforced test rail in
`tests/research/test_walk_forward_models.py` guards independence.

## Protocol

See [`docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md`](../../docs/research/WALK_FORWARD_RESEARCH_PROTOCOL.md)
for the rules the harness enforces (split conventions, no-leakage
rules, parameter-freeze modes, acceptable metrics, rejection
criteria, required artifacts).

## Dry-run script

`scripts/run_walk_forward_dry_run.py` prints a fold plan
(JSON + markdown) for a given campaign name and universe. It does
**not** execute a strategy; it only generates and validates the
plan.

```bash
python scripts/run_walk_forward_dry_run.py \
    --campaign-name CAMPAIGN_002_DRY_RUN \
    --universe-start 2020-01-01 --universe-end 2026-05-20 \
    --style rolling \
    --train-days 730 --validation-days 90 --test-days 365 \
    --step-days 365 \
    --output /tmp/walk_forward_dry_run/
```

The script writes a small `plan.json` and `plan.md` to the chosen
`--output` directory. Outputs are not auto-committed; the user
chooses what to commit.

## Safety

- No network calls, no broker calls, no QuantConnect / LEAN calls.
- No file reads at import time.
- No writes to `configs/approved_strategies.yaml`.
- No CAMPAIGN_002 rule changes.
- No bespoke-engine edits.
- All emitted documents carry `strategy_evidence: false`.
