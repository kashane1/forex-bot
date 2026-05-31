# Forex Strategy-Search Programme — Final Summary

**Sprint:** `research-forex-strategy-search-archive-001` · Phase 5
**Type:** Executive summary of the entire programme. Documentation only.
**Date:** 2026-05-31
**Status:** **`ARCHIVED_STRATEGY_SEARCH`**
**Freeze:** intact. Paper/demo/live remain blocked.

---

## One paragraph

The forex-bot strategy-search programme tested 31 numbered campaigns, a five-slot
factor shortlist (C1, S1–S5), multiple front-gate screens, cross-universe expansion,
non-time-bar alternatives, and a final FX-futures carry diagnostic — and approved
**zero strategies**. The dominant early failure mode was **cost** (real gross effects
smaller than retail spread + financing). The decisive final experiment removed the
financing wall on CME futures and found **carry is genuinely non-predictive**
(`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`), converting the binding limit from "maybe
cost-fixable" to **idea quality / market efficiency**. The programme is formally
archived with a complete evidence record, durable lessons, strict reopen criteria,
and a preserved research platform.

---

## 1. Programme timeline (compressed)

| Era | Focus | Outcome |
|-----|-------|---------|
| C001–C014 | Trend, breakout, mean-reversion, session, event families | All rejected; C011 null baseline established |
| C015–C017 + dedup | Breakout cluster + integrity remediation | NO_RELIABLE_ARCHETYPE; dedup infrastructure |
| C018–C023 | Exit hypotheses + pullback/microstructure family | Exit tweaks fail; entry signal null; family RETIRED |
| C025–C027 | Edge-discovery front gate → M5 ladder → z-score survivor | All rejected; C027 was last spot hope |
| C028–C031 | RV screen, range bars, vol-managed TSMOM | Selection noise; cost-defeated; financing-defeated |
| Cross expansion | 8 non-USD crosses + S1–S5 factor shortlist | Breadth added; S4 genuine but sub-cost; C1 fails replication |
| Non-time-bar lane | Range/vol bars + H16/H03 front gates | Infrastructure kept; directional search retired |
| Carry path | FRED rate ingest + spot carry validation | Accrual real; predictive leg null |
| Programme direction | Futures pivot chosen over immediate archive | Decision-forcing venue test |
| Futures carry diagnostic | CME EOD + frozen carry factor | **CARRY_DOES_NOT_SURVIVE_IN_FUTURES → archive** |
| **This sprint** | Formal archive closeout | Programme archived |

---

## 2. Final scorecard

| Metric | Value |
|--------|------:|
| Numbered campaigns run | 31 |
| Strategies approved | **0** |
| Factor slots tested (C1 + S1–S5 + carry) | 8 |
| Genuine non-rejected factors | 1 (S4 — economically insignificant) |
| Front-gate screens run | 6+ |
| Front-gate survivors reaching scaffold | 1 (C027 → rejected) |
| Venue studies | 3 (spot, crosses, futures) |
| TEST lockbox openings | 0 |
| Paper/demo/live enablements | 0 |

---

## 3. Terminal verdicts by family

| Family | Verdict |
|--------|---------|
| Directional / trend / breakout (C001–C017, C025–C026) | rejected / cost-defeated |
| Mean-reversion / z-score (C008/C009, C027) | cost-defeated / rejected |
| MTF confluence / pullback (C020–C023) | rejected (RETIRED) |
| Cross-sectional momentum (C016, S3) | rejected |
| Currency strength (S2) | rejected |
| Relative value / cointegration (C028, S4) | rejected / real but weak |
| Non-time-bar directional (C029, H16, H03) | cost-defeated / rejected (RETIRED) |
| Vol-managed TSMOM (C031) | cost-defeated + WITHIN_NULL |
| MTF confluence factor (C1) | real but weak / failed replication |
| Carry (spot + futures) | real but weak / **non-predictive in futures** |
| Macro / context conditioning | rejected |
| Microstructure (USD_JPY thread) | rejected |

---

## 4. Root cause (final)

**Phase 1 (spot era):** Cost is the proximate killer. Multiple plausible gross
effects exist but are smaller than round-trip spread (+ financing for slow signals).

**Phase 2 (cross era):** Breadth is not the binding constraint. USD-collinearity
broken; genuine RV found; still sub-cost.

**Phase 3 (futures era):** Cost is not the *only* killer. Carry — tested in the
venue that removes nightly financing — is statistically zero on price returns.
The accrual premium was the rate differential itself, not a predictable tradable
residual.

**Final binding limit:** Idea quality / market efficiency on liquid FX at testable
cost structures and available data classes.

---

## 5. Preserved platform assets

The archive preserves — does not delete — these reusable components:

| Asset | Location / pointer |
|-------|-------------------|
| Edge-discovery lab + null/MC/cost gates | `research/edge_discovery/` |
| Walk-forward harness | Campaign runner infrastructure |
| Backtrader parity lane | Secondary verification |
| OANDA Postgres candle store | Local research DB |
| Cross registry + cost model | Non-USD cross expansion |
| Carry/rate data | FRED OECD 3M + `research/carry/` |
| Non-time-bar builders | Range/vol bar infrastructure |
| FX futures layer | `research/fx_futures/` |
| Research freeze gates | `check_research_freeze.py`, `validate_research_archive.py` |
| Approval registry | `configs/approved_strategies.yaml` (empty, enforced) |
| Evidence manifest | `EVIDENCE_MANIFEST.json`, `EVIDENCE_INDEX.md` |

---

## 6. Archive package (this sprint)

| Document | Role |
|----------|------|
| `FOREX_STRATEGY_SEARCH_ARCHIVE_PLAN.md` | Sprint plan + audit scope |
| `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md` | Complete classified ledger |
| `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md` | Durable lessons + failure taxonomy |
| `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` | Formal archive + reopen criteria |
| `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md` | Non-active future directions |
| `FOREX_STRATEGY_SEARCH_FINAL_SUMMARY.md` | This executive summary |
| `FOREX_STRATEGY_SEARCH_ARCHIVE_001_SUMMARY.md` | Sprint closeout + validation |

---

## 7. Key prior documents (historical chain)

1. `FX_FUTURES_CARRY_VERDICT.md` — terminal trigger
2. `FX_FUTURES_CARRY_PROGRAMME_IMPLICATION.md` — archive rationale
3. `FINAL_PROGRAMME_DIRECTION_DECISION.md` — futures pivot decision
4. `CARRY_FACTOR_VERDICT.md` — spot carry verdict
5. `CROSS_RELATIVE_VALUE_FACTOR_VERDICT.md` — S4 verdict
6. `C1_FACTOR_VERDICT.md` + `C1_CROSS_REPLICATION_001_SUMMARY.md` — C1 verdicts
7. `STRATEGY_STATUS.md` — human-readable strategy registry
8. `DO_NOT_REPEAT_LIST.md` — closed lanes

---

## 8. Compliance ledger

| Question | Answer |
|----------|--------|
| Campaign created? | **No** (no CAMPAIGN_032) |
| Strategy approved? | **No** (`approved: []`) |
| Factor discovery/validation? | **No** |
| Trading logic built? | **No** |
| Paper/demo/live enabled? | **No** — blocked |
| Closed lanes reopened? | **No** |
| Freeze intact? | **Yes** |

---

## 9. Recommended reading order

1. **This document** — programme overview.
2. `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` — why archived + reopen gates.
3. `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md` — complete ledger.
4. `FX_FUTURES_CARRY_VERDICT.md` — decisive final experiment.
5. `FOREX_STRATEGY_SEARCH_FINAL_LESSONS.md` — what to carry forward.
6. `FOREX_RESEARCH_FUTURE_OPPORTUNITIES.md` — if/when to restart elsewhere.

---

## 10. Closing statement

The forex strategy-search programme ends with **integrity**: every major hypothesis
was tested to a verdict, no strategy was approved without evidence, and the final
experiment (futures carry) was pre-registered and decision-forcing. The platform
remains a reusable research asset. Further FX edge work requires a genuinely new
input — not another pass over this corpus.

**Programme status: ARCHIVED.**
