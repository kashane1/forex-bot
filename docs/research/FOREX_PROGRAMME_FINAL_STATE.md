# Forex Programme — Final State Index

**Status:** COMPLETE · ARCHIVED
**Date:** 2026-05-31
**Branch at closeout:** `main` @ `e33ccc15`

> **No approved trading strategy exists.** Paper, demo, and live execution remain blocked.

---

## One-paragraph summary

The forex-bot strategy-search programme systematically tested trend-following, multi-timeframe confluence, H4/M15/M1 entry signals, non-time-bar execution, overshoot/exhaustion and thin-participation factors, currency-strength, relative-value, and carry factors across USD majors, non-USD crosses, and CME FX futures — using a mature platform with pre-committed gates, matched nulls, cost-realism checks, and replication discipline. Every lane terminated in rejection, cost-defeat, or failed replication. The programme produced zero approved strategies and concluded that **market efficiency and sub-cost effect sizes**, not infrastructure, are the binding constraint.

---

## Final verdict

**No approved strategy.** `configs/approved_strategies.yaml` contains `approved: []`. All 23 campaigns in `EVIDENCE_MANIFEST.json` have `strategy_approved: false`.

---

## What was tested

| Lane | Examples |
|------|----------|
| Traditional strategies | Trend-following, ADX-filter, volatility breakout, pullback, mean-reversion (C001–C021) |
| Multi-timeframe confluence | H4/H1/M15/M5 scaffolds (C020, C021, C025) |
| Lower timeframes | M1 factor discovery, M3–M30 ladder (C026) |
| Non-time bars | Range bars, volatility bars (C029) |
| Front-gate screens | H16 overshoot-exhaustion, H03 thin-move, C031 vol-managed TSMOM |
| Factor validation | C1 MTF fade, S2 currency-strength, S4 triangular RV, carry |
| Cross-universe | Non-USD crosses, C1 replication (S1) |
| FX futures | Venue viability, futures carry diagnostic |

---

## Most important negative results

1. **C1 failed replication** — genuine on USD majors, artifact on crosses (`C1_CROSS_REPLICATION_VERDICT.md`)
2. **S2 rejected** — currency strength persists but does not predict forward returns
3. **S4 real but untradeable** — genuine no-arb reversion ~10× inside cost band
4. **Carry non-predictive** — mechanical accrual survives; spot-predictive leg null; futures carry t=0.09
5. **Cost-defeat dominant** — C026, C029, C031: gross-positive effects erased by spread + financing
6. **No front-gate success** — every cheap falsification screen rejected

---

## What looked real but was untradeable

| Finding | Why untradeable |
|---------|-----------------|
| C1 MTF confluence fade | Gross effect real; net-of-cost negative; failed cross replication |
| S4 triangular relative-value | Genuine no-arb reversion; effect size sub-cost |
| C029 range-bar breakout | Gross +0.084R; net −0.019R after M1-resolved costs |
| C031 vol-managed TSMOM | Pre-cost Sharpe +0.32; net −0.07; financing ≈4× spread |
| Carry premium | Exists as accrual; zero predictive content on price |

---

## What infrastructure remains useful

- Research framework (`research/`, campaign runners, backtesting engine)
- Factor-validation lab (`research/edge_discovery/`) with matched nulls, cost feasibility
- Front-gate process and edge-discovery protocol
- Campaign process with pre-commit gates and walk-forward discipline
- Cost-analysis framework and execution-realism policy
- Data ingestion (OANDA, FRED rates, FX futures Yahoo/FRED)
- Provenance tracking and freeze/archive validation tooling
- Non-time-bar builders, M1 materialization, parity verifiers

Infrastructure is **not** the bottleneck for future programmes.

---

## Why the programme is archived

The FX-futures carry diagnostic was the pre-committed last experiment. It removed the financing wall and still found carry statistically zero (`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`). This converted the root cause from "cost-defeated (maybe fixable)" to "idea-quality / market-efficiency is the binding limit." Per `FINAL_PROGRAMME_DIRECTION_DECISION.md`, this triggered Option E: archive the strategy search.

---

## Where to read more

| Document | Content |
|----------|---------|
| [`FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md`](FOREX_ARCHIVE_AND_CLEANUP_PROPOSAL.md) | Authoritative cleanup proposal |
| [`FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md`](FINAL_FOREX_PROGRAMME_EVIDENCE_INVENTORY.md) | Terminal evidence ledger by lane |
| [`FINAL_RESEARCH_DECISION_MEMO.md`](FINAL_RESEARCH_DECISION_MEMO.md) | Early programme NO-GO memo (C001–C009) |
| [`PROGRAMME_LESSONS_LEARNED.md`](PROGRAMME_LESSONS_LEARNED.md) | Cross-programme lessons |
| [`CROSS_FACTOR_PROGRAMME_SYNTHESIS_SUMMARY.md`](CROSS_FACTOR_PROGRAMME_SYNTHESIS_SUMMARY.md) | Factor programme synthesis |
| [`FX_FUTURES_CARRY_VERDICT.md`](FX_FUTURES_CARRY_VERDICT.md) | Terminal futures carry test |
| [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) | Campaign evidence index |
| [`EVIDENCE_MANIFEST.json`](EVIDENCE_MANIFEST.json) | Machine-readable campaign manifest |
| [`STRATEGY_STATUS.md`](STRATEGY_STATUS.md) | Human-readable strategy registry |

---

## Next programme

Cryptocurrency research (BTC/USD, ETH/USD only) is designed but **not yet started**. See [`CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`](CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md).

Do not reopen forex strategy discovery unless overwhelming new evidence appears.
