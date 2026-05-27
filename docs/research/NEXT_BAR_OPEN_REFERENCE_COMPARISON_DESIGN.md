# next_bar_open Reference Comparison — Design

**Sprint:** WARN remediation 001 · Phase 1  
**Reference:** CAMPAIGN_019 (`mean_reversion_thesis_invalidation 0.1.0-c019`)

## Selected reference

| Item | Value |
|------|-------|
| Campaign | CAMPAIGN_019 |
| Strategy | `mean_reversion_thesis_invalidation` |
| Version | `0.1.0-c019` |
| Entry params | Frozen C008-identical (runner validates) |
| Exit | Engine thesis_invalidation z ≤ −3 / z ≥ +3 |
| Fallback | Not required — C019 `BacktestEngine` accepts `fill_timing` |

## Why CAMPAIGN_019

- Recent, committed artifacts with `fill_timing: signal_bar_close`
- Backtrader parity documented separately (unchanged this sprint)
- Train/validation metrics pinned in `research/campaign_019/`
- No test lockbox involvement for this infrastructure comparison

## Comparison scope

| Dimension | Held constant | Varied |
|-----------|---------------|--------|
| Data | `data/campaign_002.sqlite3`, dedupe keep_last | — |
| Splits | train 2020–2022, validation 2023–2024 | — |
| Pairs | 6 majors in C019 config | — |
| Cost | base (0.2 pip fixed, 0.5× spread slip) | — |
| Risk | C019 YAML risk engine | — |
| Strategy rules | C019 frozen | — |
| Fill timing | — | `signal_bar_close` vs `next_bar_open` |

## Commands

```bash
python scripts/compare_fill_timing_reference_campaign.py
# optional gitignored trades:
python scripts/compare_fill_timing_reference_campaign.py --write-local-trades
```

## Artifacts (committed, compact)

| File | Content |
|------|---------|
| `research/fill_timing_reference_comparison/run_manifest.json` | Provenance, flags, hashes |
| `signal_bar_close_metrics.json` | Train/validation aggregates |
| `next_bar_open_metrics.json` | Train/validation aggregates |
| `fill_timing_delta.json` | Portfolio deltas |
| `exit_reason_delta.csv` | Exit share shifts |
| `pair_fold_delta.csv` | Per-pair expectancy deltas |

Large trade CSVs → `research/fill_timing_reference_comparison/local_trades/` (gitignored).

## Comparison table schema

| Column | Description |
|--------|-------------|
| split | train / validation |
| metric | trade_count, expectancy_r, profit_factor, pairs_positive |
| signal_bar_close | baseline value |
| next_bar_open | conservative value |
| delta | open − close |

## Metrics

- Train/validation trade count, expectancy R, PF, pairs positive
- Exit reason share delta (stop / time / thesis_invalidation / …)
- Per-pair expectancy R delta
- `NEXT_BAR_OPEN_UNAVAILABLE` rejection count
- Entry price delta (approximate when trade counts match)

## Known limitations

- Not a new strategy campaign; `strategy_evidence: false`
- Does not re-run full/test/stress regimes (train+validation base only)
- Entry pairing for pip delta is aggregate, not trade-ID matched
- C019 committed baseline may differ slightly from re-run due to hash/timing; manifest records both

## Infrastructure evidence only

Results inform **fill-timing policy** for future precommits. They do **not** approve CAMPAIGN_019 or any strategy.
