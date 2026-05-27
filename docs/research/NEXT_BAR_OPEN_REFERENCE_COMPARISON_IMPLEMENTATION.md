# next_bar_open Reference Comparison — Implementation

**Script:** `scripts/compare_fill_timing_reference_campaign.py`  
**Helpers:** `research/fill_timing_comparison/metrics.py`  
**Output:** `research/fill_timing_reference_comparison/` (compact, committed)

## Requirements met

| Requirement | Implementation |
|-------------|----------------|
| Local only | Reads `data/campaign_002.sqlite3` |
| No broker / OANDA orders | No broker imports |
| No parameter tuning | Frozen C019 config validated vs C008 |
| No approval / lockbox | Manifest flags `not_approved`, `test_lockbox_opened: false` |
| Risk parity with C019 runner | `RiskEngine(settings, mode="backtest")` |
| Compact artifacts | JSON + small CSV only |
| Large trades gitignored | `local_trades/` in `.gitignore` |

## Tests

- `tests/unit/test_fill_timing_comparison_metrics.py`
- `tests/unit/test_compare_fill_timing_script.py`

## Usage

```bash
python scripts/compare_fill_timing_reference_campaign.py
```
