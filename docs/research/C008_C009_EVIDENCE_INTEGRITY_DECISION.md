# C008/C009 Evidence Integrity Decision

**Date:** 2026-05-27  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`

> **Forensic decision memo only** — `strategy_evidence: false`. **No approval.**

---

## Decision summary

| question | decision |
|---|---|
| Are old C008/C009 contaminated artifacts superseded for descriptive claims? | **Partially superseded** — headline metrics and exit anatomy **confirmed** on deduped replay; original `LIKELY_CONTAMINATED` label superseded by **`DEDUPED_FORENSIC_REPLAY_CONFIRMED`** for descriptive use |
| Is deduped replay valid? | **Yes** — frozen configs, dedupe preflight, oanda-practice source, 106k duplicates documented |
| C008 verdict | **REJECT / research-only** — unchanged |
| C009 verdict | **REJECT / research-only** — unchanged |
| Test lockbox | **Remains unopened** |
| Exit hypothesis pre-registration allowed now? | **Conditionally yes** — see below |
| Promotion / paper / demo / live | **Still blocked** |

---

## Rationale

1. **Duplicate candle storage** was real (50% redundant rows per pair/window) but duplicate bars were **identical copies** — dedupe did not change trade counts (216/138 C008, 252/151 C009 base).
2. **Train-fail / validation-positive shape** reproduced exactly on deduped inputs with frozen rules.
3. **Exit pathology** (stop/time split, C009 target capping, MAE/MFE populations) **confirmed** on deduped replay outputs.
4. **C009 train exp** showed MATERIAL_CHANGE vs original report (−0.062 → −0.025) but **gate outcome unchanged** (train still negative). Do not treat as strategy improvement.
5. Original reports remain historical record; **deduped forensic JSON** is now canonical for cross-sprint descriptive references.

---

## Evidence integrity labels (updated)

| campaign | prior label | new label | verdict |
|---|---|---|---|
| C008 | LIKELY_CONTAMINATED | **DEDUPED_FORENSIC_REPLAY_CONFIRMED** | REJECT |
| C009 | LIKELY_CONTAMINATED | **DEDUPED_FORENSIC_REPLAY_CONFIRMED** | REJECT |

Descriptive claims from stop/exit diagnostics sprint: **CONFIRMED** — not superseded.

---

## What remains blocked

| blocker | status |
|---|---|
| Train expectancy gate | FAIL both campaigns |
| Test lockbox 2025–2026 | closed |
| Financing on multi-day holds | unmodeled |
| Strategy approval | none |
| CAMPAIGN_018 | not created |
| Broad strategy search | paused |
| Paper/demo/live | refused |

---

## Future mean-reversion / exit research

**Exit hypothesis pre-registration may proceed** subject to [`FUTURE_EXIT_RESEARCH_GATE.md`](FUTURE_EXIT_RESEARCH_GATE.md) and [`FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`](FUTURE_MEAN_REVERSION_RESEARCH_GATE.md):

- Requires **new campaign ID** — not C008/C009 retune
- Entries frozen before exit tests
- Financing modeled if hold time crosses rollover
- Beat-null required
- Test lockbox discipline preserved

**Not authorized:** reviving C008/C009 as promotion candidates, tuning from validation winners, opening test window based on deduped validation metrics.

---

## Explicit no-approval statement

Deduped replay confirms the **diagnostic shape** of a rejected mean-reversion clue. It does **not** approve C008, C009, or any exit variant. No strategy is approved. `configs/approved_strategies.yaml` remains `approved: []`.
