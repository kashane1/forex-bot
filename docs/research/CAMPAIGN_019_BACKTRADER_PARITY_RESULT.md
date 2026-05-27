# CAMPAIGN_019 — Backtrader Parity Result

**Date:** 2026-05-27  
**Branch:** `research-campaign-019-thesis-invalidation-execution-001`  
**Lane:** `research/backtrader_exit_parity/` · `home_currency_v1` · `engine_aligned`

---

## Command

```bash
python scripts/run_backtrader_exit_parity.py --campaign C019
```

---

## Trade-count parity (±1 tolerance)

| Split | Bespoke | Backtrader | Δ | Verdict |
|---|---|---|---|---|
| Train | 219 | 219 | 0 | **PASS** |
| Validation | 138 | 137 | −1 | **CLOSE_MATCH** (within ±1) |

**Aggregate classification:** **CLOSE_MATCH** (precommit gate: **PASS**)

---

## Exit-reason alignment

| Split | Reason | Bespoke share | BT share | Δ (pp) |
|---|---|---|---|---|
| train | stop | 60.73% | 60.73% | 0.0 |
| train | thesis_invalidation | 12.33% | 12.33% | 0.0 |
| train | time | 26.48% | 26.48% | 0.0 |
| validation | stop | 52.90% | 53.28% | 0.38 |
| validation | thesis_invalidation | 13.04% | 13.14% | 0.10 |
| validation | time | 34.06% | 33.58% | 0.48 |

No BT-only unexplained entries. Thesis invalidation exit behavior matches bespoke on train;
validation within CLOSE_MATCH tolerance.

---

## Artifacts

| File | Purpose |
|---|---|
| `research/backtrader_exit_parity/c019_parity_summary.json` | Split-level exit stats |
| `research/backtrader_exit_parity/c019_parity_trades.jsonl` | BT trade log |
| `research/backtrader_exit_parity/c019_trades.jsonl` | Alias copy for campaign review |
| `research/backtrader_exit_parity/c019_exit_reason_comparison.csv` | Per-reason comparison rows |

---

## Gate impact

Backtrader parity **passed** precommitted ±1 trade tolerance. Screening gates **failed**
independently, so test lockbox remains closed.
