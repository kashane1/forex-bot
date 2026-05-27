# Signal Contract Audit — Result

**Sprint:** Audit 001 · Phase 4  
**Classification:** **WARN** (core fields present; audit metadata gaps)

## Current signal schema (`domain/signals.py`)

| Field | Present |
|-------|---------|
| `signal_id` | Yes |
| `strategy_name` / `strategy_version` | Yes |
| `instrument` / `timeframe` | Yes |
| `timestamp` | Yes (decision bar time) |
| `side`, `entry_intent` | Yes |
| `stop_model`, `stop_price`, `exit_model` | Yes |
| `take_profit_price` | Optional |
| `features`, `reason` | Yes |
| `campaign_id` / `strategy_run_id` | **No** |
| `decision_time` vs `signal_time` split | **No** (single `timestamp`) |
| `available_data_cutoff` | **No** (can nest in `features`) |
| `source_candle_timestamp` | **No** |
| `htf_feature_timestamps` | **No** (ad hoc in `features` per strategy) |
| `blocked_reason` | **No** on Signal (rejections via RiskEngine export) |

## Separation: strategy / risk / execution

| Layer | Emits | Verified |
|-------|-------|----------|
| Strategy | `Signal` only | `generate_signal` return type; no broker imports in `strategies/*` |
| Risk | `RiskDecision` / rejections | `risk/policy.py`; exported in `risk_rejections.csv` |
| Execution | Orders via `Planner` / loops | Loops refuse without approval (`test_approved_strategies.py`) |
| Backtest engine | Fills from signals + bid/ask bars | No live OANDA order APIs in backtest path |

## Tests added

- `tests/unit/test_signal_contract_audit_001.py`

## Gaps vs recommended schema

Migration should be **additive** (optional fields) to avoid breaking CAMPAIGN_001–019 artifact hashes:

1. `available_data_cutoff: datetime | None`
2. `htf_feature_times: dict[str, datetime]`
3. `campaign_id: str | None` on exported rows (already in run config hash elsewhere)

## Classification

**WARN:** Contract is usable and separated from execution, but lacks standardized cutoff/HTF provenance fields for cross-campaign meta-analysis.
