# Forex Corpus Viability & Market Selection 001 — Summary

**Branch:** `research-forex-corpus-viability-and-market-selection-001`
**Type:** project-level strategic review. Docs-only. No strategy, no
campaign, no execution, no broker calls. **Freeze intact.**
**Date:** 2026-05-29.

This sprint answered a strategic question, not a tactical one: *are we
searching the right market, data source, instruments, and timeframe at
all?* It produced a clear decision and a conservative next direction
without creating a strategy, a campaign, or any trading activity.

---

## 1. Branch

`research-forex-corpus-viability-and-market-selection-001` (from clean
`origin/main`).

## 2. Commit hashes by phase

| Phase | Hash | Deliverable |
|-------|------|-------------|
| 0 | `74387c2` | `FOREX_CORPUS_VIABILITY_001_PLAN.md` (truth audit + plan) |
| 1 | `dbe7922` | `FOREX_RESEARCH_EVIDENCE_INVENTORY.md` |
| 2 | `af3b843` | `FOREX_STRUCTURAL_COST_CONSTRAINTS.md` |
| 3 | `10b6a77` | `OANDA_SEVEN_MAJOR_CORPUS_VIABILITY_DECISION.md` |
| 4 | `1a3bca2` | `ALTERNATIVE_MARKET_AND_DATA_SOURCE_COMPARISON.md` |
| 5 | `2c5e013` | `FUTURE_RESEARCH_OPTIONS_AFTER_FOREX_CORPUS_REVIEW.md` |
| 6 | `195cefd` | `NEXT_MARKET_SELECTION_DECISION.md` |
| 7 | `4fdedd6` | `NEXT_PROMPT_AFTER_FOREX_CORPUS_VIABILITY_REVIEW.md` |
| 8 | _this commit_ | this summary + validation |

## 3. Files changed

Nine documents, all additions under `docs/research/` (docs-only; no
code, config, registry, or executor change):

1. `FOREX_CORPUS_VIABILITY_001_PLAN.md`
2. `FOREX_RESEARCH_EVIDENCE_INVENTORY.md`
3. `FOREX_STRUCTURAL_COST_CONSTRAINTS.md`
4. `OANDA_SEVEN_MAJOR_CORPUS_VIABILITY_DECISION.md`
5. `ALTERNATIVE_MARKET_AND_DATA_SOURCE_COMPARISON.md`
6. `FUTURE_RESEARCH_OPTIONS_AFTER_FOREX_CORPUS_REVIEW.md`
7. `NEXT_MARKET_SELECTION_DECISION.md`
8. `NEXT_PROMPT_AFTER_FOREX_CORPUS_VIABILITY_REVIEW.md`
9. `FOREX_CORPUS_VIABILITY_AND_MARKET_SELECTION_001_SUMMARY.md` (this)

`git diff --name-only origin/main...HEAD -- '*.py'` is **empty** — this
sprint changed zero code.

## 4. Evidence inventory summary (Phase 1)

Twelve categories mapped to a failure-mode taxonomy:

- **Trend / breakout / mean-reversion / confluence / LTF execution:**
  all REJECT — **cost-defeated** (with **no-effect** second). C027 (the
  one idea to reach a scaffold) failed its train gate; C026 showed a
  cost *gradient* with no edge floor across M3–M30.
- **Non-time bars:** C029 cost-defeated (net −0.019R); H16/H03
  no-effect (reversion ≈0.50) → directional non-time-bar search
  **retired**.
- **Microstructure:** direction ≈0.49; genuine edges **data-blocked**
  (no true tick/L2; "volume" is a tick-count proxy).
- **Volatility / regime:** C1 high-vol is **genuine and C1-specific**
  yet **cost-defeated** on all 3 pairs; vol predictable but not
  monetizable here.
- **Macro / event / carry:** **data-blocked** (no breadth, no real rate
  leg, ~6.4y, no real financing rates) + no-effect for direction.
- **Null models, cost/financing evidence, parity/infrastructure:** all
  **working** — load-bearing gates and sound infra, not failed ideas.
  **The project is no longer code/infra blocked.**

Cross-cutting: dominant failure mode is **cost-defeated**; the single
genuine effect (C1) is real but smaller than the cost of trading it; the
universal reopen condition is **new data or a new external thesis, never
a re-tune**.

## 5. Structural cost findings (Phase 2)

The corpus is **structurally hard to trade**. Core finding: a
**two-sided cost squeeze**. Fast strategies die on the **spread wall**
(gross edges 1–3 pips vs same-order round-trip cost); slow strategies
die on the **financing wall** (C031: financing ≈4× spread). Compounding:
slippage is *worst where signals are strongest* (wide-spread high-vol
bars), rollover is cost-toxic, the 7 USD-legged majors are the most
crowded/efficient instruments and a structural USD bet, the ~6.4y sample
underpowers slow signals, and there is no true tick/order-book data.
Failures are **predominantly structural (market + cost)**, not
idea-quality — though C1 proves edges *can* exist; they are just
sub-cost here.

## 6. Current corpus viability decision (Phase 3)

**`CONTINUE_ONLY_WITH_NEW_EXTERNAL_THESIS`.** Broad undirected mining
and all re-tunes are closed; the corpus stays available as a
control/baseline and for a *single* front-gate screen behind a genuine,
**cost-aware** new thesis. Critical caveat: a thesis that does not change
the cost math will hit the same squeeze — **the higher-EV reopen is new
data or a lower-cost venue.** Broad search reopens only with ≈10–15y
history, non-USD crosses, true tick/L2, a lower-cost venue, or a genuine
new external thesis.

## 7. Alternative markets / data sources compared (Phase 4)

FX majors (current, baseline) · non-USD FX crosses · FX futures · index
futures/CFDs · metals · crypto · equities/ETFs · rates/macro (FRED) ·
higher-quality tick/L2 · multi-broker FX. Reading:

- **Cheapest new data:** non-USD crosses (same pipeline) — fixes
  crowding/breadth, **not** cost.
- **Best free-data new lane:** crypto (deep free history, larger gross
  edges; regime/venue + 24/7 cost).
- **Best structural fix to the cost squeeze:** FX/index **futures**
  (different cost profile, deep history; roll infra).
- **Best edge diversity:** index futures / metals / crypto.
- **Best free complement (already wired):** rates/macro via FRED.
- **Highest ceiling, hardest:** true tick/L2 (unlocks microstructure;
  paid, complex, overfit-prone).

## 8. Ranked future options (Phase 5)

By composite (5 = favorable): Opt 1 harden infra/docs (4.0); tie at 3.8 —
Opt 3 non-USD crosses, Opt 6 multi-market front-gate lab, Opt 8 reframe
as research lab; Opt 4 index/metal/crypto and Opt 2
corpus-only-with-thesis (3.7); Opt 7 cost/exec sim (3.5); Opt 5
tick/futures data (3.0). Judgment beyond arithmetic: cheap options score
high because they cost little but yield no edge alone; the sensible
synthesis is a **sequenced pairing** of a force-multiplier enabler
(Opt 6) + the cheapest new data that exercises it (Opt 3), with cost
modeling (Opt 7) and the lab reframing (Opt 8) folded in, deferring the
expensive lanes (4 then 5).

## 9. Recommended next direction (Phase 6)

**Build a multi-market front-gate discovery lab (Opt 6), seeded with
non-USD FX crosses (Opt 3) as its first ingested dataset.** It is an
**infrastructure + data** direction: attacks the real bottleneck (make
new search spaces cheap and uniform to evaluate), is the lowest
repeat-risk force-multiplier, builds on proven infra, uses the cheapest
genuinely-new free/local data, and commits no money, venue, or strategy.
It does **not** continue current-corpus strategy search (exhausted,
structurally cost-defeated) and does **not** create a campaign. The next
coding-agent sprint generalizes the edge-discovery lab to be
instrument-agnostic and ingests parity-checked non-USD crosses with
instrument-specific cost models + data-quality diagnostics — **no
strategy screen, no campaign, no approval.**

## 10. Was any campaign created?

**No.** No CAMPAIGN_032, no campaign of any number.

## 11. Was any strategy approved?

**No.** `configs/approved_strategies.yaml` remains `approved: []`
(confirmed empty; `forex_bot.approval` fails closed).

## 12. Do paper/demo/live remain blocked?

**Yes.** All loops refuse (empty registry; freeze guard intact). The
freeze gate confirms `paper-loop refuses ['trend_following'] — frozen`
and `demo-loop refuses ['trend_following'] — frozen`. No
executor/broker/loop change.

## 13. Validation commands run

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2389 passed, 3 skipped** (skips = absent local data) — exit 0 |
| `python scripts/check_research_freeze.py` | **ALL CHECKS PASSED** — exit 0 (registry empty; loops refuse) |
| `python scripts/validate_research_archive.py` | **ALL CHECKS PASSED** — exit 0 (23 campaigns, 747 evidence-index links resolve, no approval) |
| `python scripts/scan_artifacts_for_secrets.py` | **PASSED** — exit 0 (no credential-shaped strings) |
| `ruff check src scripts tests` | **exit 1** — see note below |
| `git status --short` | clean after the Phase 8 commit (docs-only) |

**Ruff note (honest):** `ruff check` reports 4 errors, **all
pre-existing** in `scripts/run_edge_discovery_vol_managed_tsmom.py` (the
CAMPAIGN_031 screen script, authored on `origin/main` at commit
`f0c8337`). This docs-only sprint added **zero** Python
(`git diff --name-only origin/main...HEAD -- '*.py'` is empty), so the
ruff failure is a pre-existing repo condition, not a regression from this
review. The 4 are auto-fixable (`ruff check --fix`); fixing them is
out of scope for a docs-only viability review and is flagged for a
separate cleanup task.

## 14. Recommended next prompt location

`docs/research/NEXT_PROMPT_AFTER_FOREX_CORPUS_VIABILITY_REVIEW.md`
(branch `research-multi-market-front-gate-and-nonusd-crosses-001`).

## 15. Files to review first

1. `OANDA_SEVEN_MAJOR_CORPUS_VIABILITY_DECISION.md` — the corpus verdict.
2. `NEXT_MARKET_SELECTION_DECISION.md` — the recommended next direction.
3. `FOREX_STRUCTURAL_COST_CONSTRAINTS.md` — *why* (the two-sided squeeze).
4. `FOREX_RESEARCH_EVIDENCE_INVENTORY.md` — the full evidence map.
5. `ALTERNATIVE_MARKET_AND_DATA_SOURCE_COMPARISON.md` +
   `FUTURE_RESEARCH_OPTIONS_AFTER_FOREX_CORPUS_REVIEW.md` — the options.
6. `NEXT_PROMPT_AFTER_FOREX_CORPUS_VIABILITY_REVIEW.md` — the next sprint.

---

## Bottom line

The seven-major OANDA FX corpus is **structurally cost-defeated** for the
strategy families explored; broad search on it is **exhausted**. Keep it
as a control/baseline and run new strategy work **only** behind a
genuine, cost-aware external thesis. The next *edge* more likely lives in
a **different cost structure or instrument universe** — so the
conservative next step is to build a **multi-market front gate** and seed
it with the cheapest new data (**non-USD FX crosses**), without creating
a strategy, a campaign, or any trading activity. **Freeze intact; nothing
approved; paper/demo/live blocked.**
