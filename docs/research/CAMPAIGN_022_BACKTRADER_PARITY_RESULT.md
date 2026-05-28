# CAMPAIGN_022 — Backtrader Parity Result

**Date:** 2026-05-28 · **Strategy:** `h4_h1_pullback_resolution_entry 0.1.0-c022`
**Status:** **NOT RUN — moot (train gate REJECT)**

## Rationale

Per the frozen gate discipline (EXECUTION_001_PLAN), Backtrader parity is required **only before
the test lockbox opens**, and only after train **and** validation gates pass. The binding train
gate failed:

- train expectancy = −0.1042R (< 0) → immediate REJECT, no validation rescue, test lockbox stays closed.

Backtrader parity is an independent-engine cross-check whose sole purpose is to protect a
*lockbox-eligible* result from a bespoke-engine artifact. Since C022 is REJECT and the lockbox will
not open under any branch, running parity would change no decision and would consume multi-hour
compute with no evidentiary value.

## What would be required if C022 had been lockbox-eligible

- A `research/backtrader_lane/` adapter mirroring the frozen C022 logic (H4 multi-factor bias,
  H1 holding-pullback, M15 reclaim, 2×ATR stop, 32-bar time stop, next_bar_open).
- Trade-count agreement, no unexplained entries, HTF-alignment consistency, reclaim-timing
  consistency, and stop/time-exit consistency within tolerance.

This adapter was intentionally **not** built, consistent with not expending compute on a rejected
campaign and with the no-modification discipline.

## Statement

Parity NOT executed because the campaign is already REJECT. No lockbox opened. No approval.
`approved_strategies.yaml` remains `approved: []`.
