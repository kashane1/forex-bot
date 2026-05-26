# Non-Strategy Workstream Options After Broad-Search Pause

**Date:** 2026-05-26  
**Branch:** `research-broad-strategy-pause-and-roadmap-001`  
**Context:** Broad seven-pair pattern strategy search is **paused**. No strategy approved.

---

## Comparison matrix

| # | workstream | OANDA creds | fully local | complexity | risk | priority |
|---:|---|:---:|:---:|:---:|---|:---:|
| 1 | Observed transaction-cost model | read-only later | **yes** (phase 1) | medium | low | **P0** |
| 2 | Observed financing / rollover capture | read-only | partial | medium–high | low–med | P1 |
| 3 | Spread-regime & session-cost diagnostics | no | **yes** | low–medium | low | **P0** |
| 4 | Data expansion / longer history | optional fetch | mostly | medium | med | P2 |
| 5 | Broker fill/slippage replay | read-only | partial | high | med | P3 |
| 6 | Backtrader parity hardening | no | **yes** | medium | low | P2 |
| 7 | Portfolio/risk simulator improvements | no | **yes** | medium | low | P3 |
| 8 | Stop all research temporarily | n/a | n/a | none | none | defer |

---

## 1. Observed transaction-cost model

**Goal.** Replace or calibrate modeled spread/slippage assumptions with distributions derived from stored bid/ask candles and (later) observed practice fills.

**Why it matters.** C015–C017 fail near or below null; 2× cost stress worsens all candidates. Strategies may be losing to **structural cost drag** rather than missing a directional signal — but that cannot be quantified with the current flat cost overlay alone.

**What it would unblock.** Honest net expectancy for future campaigns; retirement of optimistic cost assumptions; gating rules (“do not trade when spread/ATR > X”).

**OANDA read-only credentials.** Not required for phase 1 (bid/ask H4 in SQLite). Helpful later to reconcile against practice transaction history.

**Fully local.** Yes for H4 spread/ATR analytics on existing deduped candles.

**Implementation complexity.** Medium — new diagnostics module, JSON summaries, tests on fixtures.

**Risk.** Low (descriptive). Danger is using diagnostics to **reverse-engineer** a strategy on the same sample — must stay non-strategy.

**Recommended priority.** **P0** — combine with item 3 in one sprint.

---

## 2. Observed financing / rollover capture

**Goal.** Capture historical swap/financing from practice account or vendor tables and accrue in backtest PnL.

**Why it matters.** Financing is an unconditional blocker for live promotion per `FUTURE_RESEARCH_BACKLOG.md` item 1. Carry-sensitive holds cannot be judged without it.

**What it would unblock.** Net-of-financing campaign verdicts; carry research (item 6 in backlog) only after model exists.

**OANDA read-only credentials.** **Yes** — practice account financing API or exported statements.

**Fully local.** Partial — ingestion may need API; accrual engine runs locally.

**Implementation complexity.** Medium–high — data source, accrual in engine, reconciliation tests.

**Risk.** Low for modeling; medium if financing tables are incomplete or mis-timestamped.

**Recommended priority.** **P1** — after spread diagnostics; before new strategy campaigns.

---

## 3. Spread-regime and session-cost diagnostics

**Goal.** Characterize spread (and spread/ATR) by pair, fold, UTC session, weekday, and volatility regime; flag cost-hostile windows.

**Why it matters.** Same rationale as item 1; fastest path to actionable **gating hypotheses** without running a new campaign.

**What it would unblock.** Pre-registered cost filters for future strategies; explanation of 2× cost failure mode; session/weekday avoid lists.

**OANDA read-only credentials.** **No** — uses existing bid/ask H4.

**Fully local.** **Yes.**

**Implementation complexity.** Low–medium — scripts + compact MD/JSON outputs.

**Risk.** Low if descriptive only.

**Recommended priority.** **P0** — selected as joint sprint with item 1.

---

## 4. Data expansion / longer history

**Goal.** Extend candle history or add pairs/asset classes with validated ingestion and dedupe.

**Why it matters.** C016 weekly sample is thin (137 trades), but C015 (375) still fails WITHIN_NULL — volume alone did not explain the rejection cluster.

**What it would unblock.** Higher *n* for weekly families **if** a new hypothesis is pre-registered after pause lifts.

**OANDA read-only credentials.** Optional for historical download.

**Fully local.** Mostly after download.

**Implementation complexity.** Medium — ingestion, dedupe probes, storage.

**Risk.** Medium — more data increases search space; must not pair with ad-hoc strategy mining.

**Recommended priority.** **P2** — defer until cost diagnostics complete and re-entry gates met.

---

## 5. Broker fill/slippage replay model

**Goal.** Replay orders against tick or sub-H4 data to estimate realistic fills vs mid/spread assumptions.

**Why it matters.** H4 bar-level fills may optimistic; explains divergence between backtest and practice.

**What it would unblock.** Fill realism for promotion decisions.

**OANDA read-only credentials.** Read-only for tick/sub-bar data if not already stored.

**Fully local.** Partial — depends on tick data availability.

**Implementation complexity.** **High.**

**Risk.** Medium — easy to overfit fill model to historical tape.

**Recommended priority.** **P3** — after spread diagnostics and observed cost distributions.

---

## 6. Backtrader parity hardening

**Goal.** Close BLOCKED/DEFERRED Backtrader paths for C016/C017 weekly boundaries and per-fold support.

**Why it matters.** Independent engine agreement reduces “engine artifact” doubt on REJECT verdicts.

**What it would unblock.** Decision-blocking parity for future campaigns; does **not** create edge.

**OANDA read-only credentials.** **No.**

**Fully local.** **Yes.**

**Implementation complexity.** Medium — fold-plan runner extension (~150–250 LOC per prior defer memo).

**Risk.** Low — verification only.

**Recommended priority.** **P2** — useful but not urgent while strategy search is paused.

---

## 7. Portfolio/risk simulator improvements

**Goal.** Improve cross-pair portfolio risk engine, correlation caps, and diagnostic overlays used in walk-forward.

**Why it matters.** Better risk realism for future campaigns; does not fix absent directional edge.

**What it would unblock.** Cleaner portfolio-level gates when strategy research resumes.

**OANDA read-only credentials.** **No.**

**Fully local.** **Yes.**

**Implementation complexity.** Medium.

**Risk.** Low.

**Recommended priority.** **P3** — after cost and financing infrastructure.

---

## 8. Stop all research temporarily

**Goal.** Halt all research sprints until external priorities change.

**Why it matters.** Minimizes compute and overfitting risk when no falsifiable strategy hypothesis exists.

**What it would unblock.** Nothing — preserves status quo freeze.

**OANDA read-only credentials.** n/a

**Fully local.** n/a

**Implementation complexity.** None.

**Risk.** None — but **institutional memory stalls** and cost questions remain unanswered.

**Recommended priority.** **Defer** — cost diagnostics are low-risk and clarify whether any future pattern search is economically plausible on this universe.

---

## Synthesis

The highest-leverage next step is **observed cost + spread-regime diagnostics (items 1 + 3)** on local deduped bid/ask H4 data — no broker order APIs, no new campaign, aligns with 2× cost failure and WITHIN_NULL cluster. Financing capture (item 2) is the logical follow-on. Strategy campaigns remain **paused** until re-entry gates in [`BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md`](BROAD_STRATEGY_SEARCH_PAUSE_MEMO.md) are satisfied.
