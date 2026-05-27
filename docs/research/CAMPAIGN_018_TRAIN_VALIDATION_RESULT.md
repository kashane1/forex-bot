# CAMPAIGN_018 Train/Validation Results

**Date:** 2026-05-27  
**Branch:** `research-campaign-018-protective-stop-execution-001`  
**Campaign:** CAMPAIGN_018 · `mean_reversion_protective_stop 0.1.0-c018`

> **Research execution** — `strategy_evidence: true`, `not_approved: true`. **No approval.**

---

## Command

```bash
python scripts/run_campaign_018_protective_stop.py train-validation
```

**Elapsed:** ~319s · **Git:** `2ec55d3` runner + `adae664` implementation

---

## Data path

| item | value |
|---|---|
| Database | `./data/campaign_002.sqlite3` |
| Source | `oanda-practice` |
| Dedupe | `keep_last` (mandatory) |
| Config | `configs/campaign_018_mean_reversion_protective_stop.yaml` |

---

## Split windows

| split | window |
|---|---|
| train | 2020-01-01 → 2022-12-31 |
| validation | 2023-01-01 → 2024-12-31 |
| test | **not run** (screening failed) |

---

## Train metrics (base cost)

| metric | C018 | C008 deduped |
|---|---:|---:|
| trades | 236 | 216 |
| expectancy R | **−0.119** | −0.025 |
| profit factor | 0.92 | 1.02 |
| pairs positive | 2/6 | 5/6 |

---

## Validation metrics (base cost)

| metric | C018 | C008 deduped |
|---|---:|---:|
| trades | 142 | 138 |
| expectancy R | **+0.194** | +0.161 |
| profit factor | 1.58 | 1.29 |
| pairs positive | 6/6 | 6/6 |

---

## Gate table

| gate | result |
|---|---|
| train expectancy ≥ 0 | **FAIL** (−0.119) |
| validation expectancy > 0 | PASS (+0.194) |
| validation PF ≥ 1.05 | PASS (1.58) |
| validation pairs ≥ 2 | PASS (6/6) |
| validation trades ≥ 30 | PASS (142) |
| validation 2× stress exp ≥ 0 | PASS (+0.178) |
| beat C011 null (+0.010 margin) | PASS (> 0.0071) |
| protective mechanism active (≥10%) | PASS (53.3% armed) |
| zero target exits | PASS (0) |
| full stress_15x exp ≥ 0 | **FAIL** (−0.018 agg) |

**Screening:** **FAIL** · **Verdict:** **REJECT**

---

## 2× cost stress (validation)

Expectancy **+0.178 R**, PF **1.49**, 5/6 pairs positive.

---

## Mechanism diagnostics (all runs combined)

| metric | value |
|---|---:|
| protective stop armed | 53.3% of trades |
| protective stop exits | 37.0% |
| hard stop exits | 47.4% |
| time exits | 16.4% |
| target exits | **0** |

Exit mix shifted from C008 stop/time (~68/32) toward stop/protective/time — protective rule **active** and **avoided midline targets**.

---

## Comparison summary

| baseline | train exp R | val exp R |
|---|---:|---:|
| C008 deduped | −0.025 | +0.161 |
| C009 deduped | −0.025 | +0.186 |
| C018 | −0.119 | +0.194 |
| C011 null | — | −0.003 |

C018 **improved validation** vs C008 but **worsened train** materially. Beat-null on validation but **failed primary train gate**.

---

## Test lockbox

**NOT allowed to open** — screening gate failed (`train_expectancy_gte_zero`, `full_stress_15x_expectancy_gte_zero`).

---

## Explicit no-approval statement

CAMPAIGN_018 is **REJECT** under precommitted gates. No strategy approved. `configs/approved_strategies.yaml` remains empty. Paper/demo/live blocked.
