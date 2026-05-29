# NEXT_SPRINT_PROMPT_AFTER_CAMPAIGN_027_SCAFFOLD

**Status:** a *draft prompt* for the future CAMPAIGN_027 train/validation
execution sprint. **It is NOT executed now.** Running it is a separate, explicit,
human-issued action. This document creates no evidence, approves nothing, opens
no test lockbox, and keeps paper/demo/live blocked and
`configs/approved_strategies.yaml` = `approved: []`.

> Binding inputs (do not re-derive):
> [precommit scope](CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md),
> [reconciliation](CAMPAIGN_027_EDGE_DISCOVERY_TO_PRECOMMIT_RECONCILIATION.md),
> [artifact contract](CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md),
> [parity design](CAMPAIGN_027_BACKTRADER_PARITY_DESIGN.md),
> [reentry gates](FUTURE_CAMPAIGN_REENTRY_GATES.md),
> [artifact requirements](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md),
> [compatibility checklist](EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md).

---

## ===== BEGIN FUTURE TRAIN/VALIDATION PROMPT (do not run until explicitly instructed) =====

**Branch:** `research-campaign-027-h4-filtered-zscore-reversion-train-validation-001`
(start from latest `origin/main` after the scaffold sprint is merged).

**Context:** CAMPAIGN_027 (`h4_filtered_zscore_reversion 0.1.0-c027`) is a
precommitted scaffold — the single idea that survived the edge-discovery front
gate. The exact rule is **frozen** in
`CAMPAIGN_027_PRECOMMIT_H4_FILTERED_ZSCORE_REVERSION_SCOPE.md`. This sprint runs
train + validation evidence on the campaign's **own** ledgers and decides
REJECT vs PROCEED-TO-PARITY. It does **not** approve, does **not** open the test
lockbox, does **not** enable paper/demo/live.

**Hard rules (unchanged from the freeze):**
- **No tuning.** The Phase-2 frozen rule is run as-is. No parameter matrix, no
  re-selection of filters/side/thresholds/exits after seeing results. If the
  frozen rule fails, the verdict is REJECT — not a re-tune.
- **One frozen candidate** only (single-candidate registry is fine).
- **Train then validation only.** Selection (if any sub-fold logic exists) is on
  **train only**; validation is confirmation, never parameter selection (G7).
- **No test lockbox** (2025-01-01 → 2026-05-20) unless **all** train/validation
  gates **and** Backtrader parity pass in a *later* sprint and a human authorizes
  a single-use open (G8).
- Do not edit `configs/approved_strategies.yaml` (stays `approved: []`); no
  paper/demo/live; no executor/broker/OANDA mutation; no live creds; local H4
  store only; no new fetch; no `.env`/credentials/DB/raw-candle/bulky commits.

**Required evidence (on the campaign's own artifacts):**
1. Emit the full edge-discovery-compatible ledgers per
   `CAMPAIGN_027_EDGE_DISCOVERY_ARTIFACT_CONTRACT.md` (signal, trade,
   signal-funnel, candidate registry; metadata items 4–12; both
   optimistic and **conservative** cost; C011 null reference; reproducibility +
   seed manifest).
2. **Conservative financing-inclusive cost** is the binding metric for every
   gate (1.5-pip spread + 2×0.2-pip slip + financing over the 12-bar hold).
3. **Matched-null comparison** on the campaign's own ledgers — must beat the
   *structure-matched* null (side-shuffled, session-matched, full) by a
   meaningful margin (G1/G2).
4. **Filter-ablation confirmation** — each retained filter (low-vol,
   strong-extension, quiet-session) must re-derive `FILTER_ADDS_EDGE` on the
   campaign's own data, not merely reduce sample (G4).
5. **Pair-robustness** — no single-pair dominance / no sign-flip on pair-holdout
   (G5); **matrix-sanity** `ROBUST_MATRIX_SIGNAL`, not `LIKELY_SELECTION_NOISE`
   (G6).
6. **Year robustness incl. the 2024/2026 recency gate** — the most recent
   validation fold must be **positive post-conservative-cost**; a decayed edge
   averaged over the window is not acceptable.
7. **2× cost stress** must not fail materially.

**Pre-registered kill conditions (any one → REJECT or BLOCK; may not be weakened):**
1. Train expectancy ≤ 0 after conservative cost.
2. Validation expectancy ≤ 0 after conservative cost.
3. Edge not robust across pairs / single-pair dominated.
4. Edge negative or collapsing in recent years, especially **2024/2026**.
5. Matched-null comparison no longer beats random by a meaningful margin.
6. Filter ablation shows filters only reduce sample.
7. 2× cost stress fails materially.
8. Backtrader parity cannot be achieved before any promotion-review step.
9. Required artifact ledgers missing or incompatible with the edge-discovery lab.

**Outcome bar:** PROCEED-TO-PARITY only if the frozen rule shows post-conservative
-cost edge above the campaign's own matched null on **both** train and validation
(recent fold positive), is pair-robust and not selection-noise, and survives 2×
cost stress. Otherwise **REJECT** (record the killing diagnostic + flag in
`FUTURE_RESEARCH_BACKLOG.md`; the family closes unless a new external thesis
arrives). Parity (separate sprint) and the human-gated single-use test lockbox
are downstream of a PROCEED verdict; **approval remains a separate manual human
edit** to `configs/approved_strategies.yaml` and is never automatic.

**Validation commands:** `pytest tests/ -q`; `ruff check src tests scripts
research`; `check_research_freeze.py`; `validate_research_archive.py`;
`scan_artifacts_for_secrets.py`.

## ===== END FUTURE TRAIN/VALIDATION PROMPT =====

**Reminder:** nothing above is executed in this sprint. This file is the
deliverable; acting on it requires an explicit future instruction.
