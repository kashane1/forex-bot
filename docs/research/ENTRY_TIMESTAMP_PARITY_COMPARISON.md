# Entry Timestamp Parity Comparison

**Branch:** `infra-entry-orchestration-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence:** [`research/entry_parity/entry_timestamp_comparison.json`](../../research/entry_parity/entry_timestamp_comparison.json)

---

## Headline

**Every Backtrader entry was a subset of bespoke entries** on prior (broken-PnL) artifacts:

| Campaign | Bespoke | BT (broken) | Common | BT-only | Bespoke-only |
|---|---:|---:|---:|---:|---:|
| C008 | 354 | 279 | **279 (100% of BT)** | 0 | 75 |
| C009 | 403 | 332 | **332 (100% of BT)** | 0 | 71 |
| C018 | 378 | 314 | **314 (100% of BT)** | 0 | 64 |

Common trades have **identical entry and exit timestamps** — no signal drift on matched trades.

---

## Per-pair gap (C008, broken-PnL lane)

| Pair | Bespoke | BT | Delta |
|---|---:|---:|---:|
| USD_JPY | 62 | 3 | **59** |
| USD_CAD | 59 | 44 | 15 |
| GBP_USD | 65 | 64 | 1 |
| Others | — | — | 0 |

USD_JPY alone explains ~79% of the C008 bespoke-only gap.

---

## Bespoke-only attribution (broken lane)

| Cause | Count (all campaigns) |
|---|---:|
| RiskEngine / orchestration divergence | ~207 |
| BT position still open | 3 |

No Backtrader-only entries — bespoke never missed a BT entry.

---

## After PnL fix (adjustment experiment)

See [`BACKTRADER_ENTRY_PARITY_ADJUSTMENT_EXPERIMENT.md`](BACKTRADER_ENTRY_PARITY_ADJUSTMENT_EXPERIMENT.md). Delta collapses to **±1 trade per campaign**.
