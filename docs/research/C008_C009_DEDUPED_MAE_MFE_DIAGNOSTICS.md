# C008/C009 Deduped MAE/MFE Diagnostics

**Date:** 2026-05-27  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Artifact:** [`research/deduped_c008_c009_rerun/deduped_mae_mfe.json`](../../research/deduped_c008_c009_rerun/deduped_mae_mfe.json)

> **Forensic only** — `strategy_evidence: false`. Descriptive only — no stop retuning.

---

## MAE/MFE status

| item | status |
|---|---|
| computed | **yes** |
| method | H4 deduped candles between entry and exit; R normalized by entry–stop distance |
| campaigns | C008 (354 trades), C009 (403 trades) base cost train+val |

---

## C008 (deduped vs prior diagnostic)

| metric | deduped replay | prior (`stop_distance_adverse_excursion.json`) |
|---|---:|---:|
| stop % reached ≥1R before stop | **60.17%** | 58.86% |
| stop % never 1R favorable | **39.83%** | 41.14% |
| stop median MFE (R) | 1.114 | 1.098 |
| time median MFE (R) | **3.293** | 3.326 |
| median stop distance (pips) | 45.33 | 45.5 |

**Persists: yes** — mixed bad-entry (~40%) vs favorable-then-stopped (~60%) population.

---

## C009 (deduped vs prior diagnostic)

| metric | deduped replay | prior |
|---|---:|---:|
| stop % reached ≥1R before stop | **53.30%** | 53.30% |
| target median MFE (R) | **1.827** | 1.827 |
| time median MFE (R) | 1.653 | 1.653 |
| median stop distance (pips) | 45.25 | 45.25 |

**C009 MAE/MFE identical to prior diagnostic** — strong confirmation that deduped replay reproduces exit path geometry.

**Winner capping persists: yes** — target MFE ~1.83R vs C008 time MFE ~3.29R.

---

## Classification

| finding | persists |
|---|---|
| stop/time split | yes |
| C009 midline caps tail vs C008 time | yes |
| delayed reversion (high time MFE) | yes |
| bad-entry fraction (~40–47% stops never 1R favorable) | yes |

---

## Rules observed

No alternate stop distances tested. No optimization. Descriptive only.
