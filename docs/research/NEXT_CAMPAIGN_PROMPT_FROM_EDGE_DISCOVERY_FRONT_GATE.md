# NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE

**Status:** a *draft prompt* for a future strategy-campaign scaffold/precommit,
justified by the Phase 1–6 edge-discovery evidence of
`research-edge-discovery-front-gate-idea-selection-001`. **It is NOT executed in
this sprint.** Running it is a separate, explicit, human-issued action. This
document creates no campaign, approves nothing, opens no test lockbox, and keeps
paper/demo/live blocked and `configs/approved_strategies.yaml` = `approved: []`.

> Justifying evidence:
> [ranking & decision](EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md),
> [filter ablation](EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md),
> [matched-null](EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md),
> [signal probes](EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md),
> [opportunity map](EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md). Binding gates:
> [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md),
> [`FUTURE_CAMPAIGN_REENTRY_GATES.md`](FUTURE_CAMPAIGN_REENTRY_GATES.md),
> [`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md).

---

## The idea that earned this prompt

**H4 low-volatility, quiet-session, strong-extension, short-biased z-score mean
reversion on the seven majors.** Concretely, as screened:

- **Signal:** 20-bar rolling mean/σ of the H4 mid close; trigger when `|z| ≥
  2.5` (strong extension). Entry side = **toward the mean** (the ablation showed
  the edge is on the **short** side — selling rich extensions; long-side hurts).
- **Regime filter:** trailing-window ATR percentile ≤ 0.33 (**low-vol** regime).
- **Session filter:** entry UTC session ∈ {asia, london} (**quiet** sessions).
- **Pairs:** all 7 majors (pair-robust 6/7; *not* USD_JPY-only — USD_JPY's value
  is cost, not signal).
- **Hold / exit (screened proxy):** ~12 H4 bars (≈ 2 days). The campaign must
  specify a precommitted exit (e.g. mean-touch target + ATR stop + time stop) and
  test it against the fixed-horizon proxy.
- **Timeframe:** H4 (cost-feasible; spread/ATR ≈ 0.04–0.10).

## Why it earned a campaign (front-gate evidence)

1. **Cost feasibility — PASS.** H4 spread/ATR far below the 0.25 hostile gate;
   the edge-adding subset survives a conservative financing-inclusive cost
   overlay (+0.000626 post-cost vs +0.000754 optimistic).
2. **Forward-return information — PASS.** Signed forward log-return rises
   monotonically with horizon (pre-cost +0.000009 → +0.000341, h1→h24).
3. **Matched null — PASS.** `BEATS_MATCHED_NULL` on **all six** modes
   (timestamp-random, side-shuffled, pair-matched, session-matched,
   holding-period-matched, full), percentile 100, effect 3.7–6.0.
4. **Filter ablation — PASS.** low-vol / strong-extension / quiet-session each
   `FILTER_ADDS_EDGE` (not sample-only); long-side hurts → short bias;
   cost-adv-pair sample-only.
5. **Robustness — PARTIAL PASS.** Pair-robust (6/7 positive); multi-year
   positive (4/7). **Not** a single-year (2023) artifact after filtering.

## Pre-registered kill-conditions (MUST be tested; any failure → REJECT)

The front gate could not resolve these cheaply; the campaign exists to
adjudicate them on a clean train/validation/test split:

- **Recency / non-stationarity.** Subset post-cost was **negative in 2021, 2024,
  and 2026-partial**. If the validation window (and especially the most recent
  fold) is not positive post-cost, **REJECT** — do not average a decayed edge.
- **Filter forking-path.** The three filters were retained *after* seeing the
  ablation. The campaign must **precommit** the exact `|z|≥2.5 & ATR-pct≤0.33 &
  session∈{asia,london} & short-bias` rule **before** any train run and not
  re-tune it; a held-out test confirms it.
- **Conditioning narrowness.** Precommit it explicitly as a low-vol
  quiet-session short-reversion strategy; do **not** generalize to all
  regimes/sessions/sides mid-campaign.
- **Selection-noise context.** The raw-variant matrix flagged
  `LIKELY_SELECTION_NOISE` (USD_JPY single-pair). The campaign must demonstrate
  `ROBUST_MATRIX_SIGNAL` (not selection noise) on its own train matrix.

---

## ===== BEGIN FUTURE-CAMPAIGN PROMPT (do not run until explicitly instructed) =====

> Paste-ready prompt for a future campaign **scaffold + precommit** sprint. It is
> a *scaffold/precommit* prompt — it still does not approve, does not enable
> paper/demo/live, and does not open the test lockbox until its own later phases
> and a human approval say so.

**Branch:** `research-campaign-0NN-lowvol-quietsession-zscore-reversion-scaffold-001`
(assign `0NN` = the next unused campaign number; **grep first** that it is unused
— C024 is abandoned, C025/C026 are used, so C027 is expected free, but
re-verify per the project rule before assigning).

**Context:** the edge-discovery front gate
(`research-edge-discovery-front-gate-idea-selection-001`) screened 12 idea
families and found exactly one campaign-eligible idea (this one). All evidence is
in the `EDGE_DISCOVERY_*` docs. C011 is the null benchmark; C025/C026 stay
rejected; the lower-TF Donchian family stays closed.

**Goal:** scaffold and **precommit** (not run to approval) a campaign for the H4
low-vol quiet-session strong-extension short-biased z-score reversion strategy,
with full train/validation/test discipline and Backtrader parity required before
any promotion review.

**Hard rules (unchanged from the freeze):**
- Do not approve any strategy; do not edit `configs/approved_strategies.yaml`
  (stays `approved: []`).
- Do not enable paper/demo/live; do not modify executor/broker/OANDA behavior;
  no OANDA order/trade/position/transaction/live calls; no live creds.
- Local existing data only (H4 store `data/campaign_002.sqlite3`); no new fetch.
- Do not commit `.env`/credentials/DB dumps/raw candles/bulky artifacts.
- Do not open the test lockbox until the precommitted train+validation gates pass
  and the precommit checklist is filed; test is single-use and human-gated.

**Phases:**
0. Truth audit; create branch; restate the edge-discovery evidence and the four
   pre-registered kill-conditions; confirm freeze/approved=[]/loops-refuse.
1. **Precommit** the exact rule set **before any run**: signal `|z|≥2.5` on a
   20-bar H4 mean; entry short when z≥+2.5 (sell extension) and the regime/session
   filters hold; **regime** ATR-percentile ≤ 0.33 (trailing window, no lookahead);
   **session** ∈ {asia, london} (UTC buckets); **pairs** all 7 majors; **exit**
   precommitted (mean-touch target + ATR-multiple stop + time stop ≈ 12 H4 bars);
   risk/sizing precommitted. Write `CAMPAIGN_0NN_PRECOMMIT_CHECKLIST.md` filling
   in the pre-campaign edge-discovery checklist with the Phase 1–6 lab artifacts.
2. **Train** fold(s) only: build the signal/trade/filter-stage/funnel ledgers
   (per `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md` and the edge-discovery
   compatibility checklist), compute the train matrix, and run the lab gates
   (cost-feasibility, matched-null, filter-ablation, matrix-sanity) on the
   *campaign's own* ledgers. REJECT if any lab gate fails (e.g.
   `LIKELY_SELECTION_NOISE`, matched-null not beaten, filters sample-only).
3. **Validation** fold(s): confirm the precommitted rule holds out-of-sample
   **without re-tuning**; the **most recent validation fold must be positive
   post-cost** (recency kill-condition). REJECT otherwise.
4. **Backtrader parity:** reproduce the engine result in Backtrader to parity
   tolerance **before** any promotion consideration (per the BACKTRADER_* parity
   contract). No promotion without parity.
5. **Test lockbox (human-gated, single-use):** only if Phases 2–4 pass and a human
   authorizes opening it. Pre-register the pass/fail metric. One shot.
6. **Promotion review:** only if the test passes, present a promotion-review
   candidate to a human. Approval is a separate, manual `approved_strategies.yaml`
   edit by a human — never automatic.

**Data requirements:** H4 OHLC (bid/ask) for the 7 majors, 2020-01→2026-05, from
`data/campaign_002.sqlite3` (worktree-aware resolution; `PYTHONPATH=$PWD/src`).
No M1/M5/M15/M30 needed (the idea is H4). No carry/event data needed.

**Artifact requirements:** emit edge-discovery-compatible ledgers (signal, trade,
filter-stage, signal-funnel; pair/side/session/timeframe/hold/spread/cost/
split-window metadata; candidate registry; matrix table; null-benchmark
compatibility fields; reproducibility + seed metadata) so the lab can re-screen
the campaign's own output. See `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md` and
`EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md`.

**Validation commands:** `pytest tests/ -q`; `ruff check src tests scripts
research`; `check_research_freeze.py`; `validate_research_archive.py`;
`scan_artifacts_for_secrets.py`.

**Expected outcome bar:** REJECT unless the precommitted rule shows post-cost edge
above the campaign's own matched null on **both** train and validation (recent
fold positive), survives Backtrader parity, and is not selection-noise — only
then may the human-gated test lockbox be considered.

## ===== END FUTURE-CAMPAIGN PROMPT =====

**Reminder:** nothing above is executed in this sprint. This file is the
deliverable; acting on it requires an explicit future instruction.
